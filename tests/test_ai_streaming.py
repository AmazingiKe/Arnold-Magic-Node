import io
from http.client import IncompleteRead
import json
import socket
import unittest

from arnold_magic_node.core.ai_protocol import (
    API_STYLE_CHAT_COMPLETIONS,
    API_STYLE_RESPONSES,
    AiIncompleteResponseError,
    AiProtocolError,
    AiRefusalError,
    AiRetryableStreamError,
    AiStreamAccumulator,
    build_request_payload,
)
from arnold_magic_node.tools.ai_client import (
    AiClientConfig,
    AiResponseTooLargeError,
    AiTimeoutError,
    AiTransportError,
    HttpEventStream,
    OpenAICompatibleClient,
    UrllibTransport,
)


def event_data(payload):
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def sse_event(payload):
    return ("data: {}\n\n".format(event_data(payload))).encode("utf-8")


def responses_stream(text="你好", model="responses-model"):
    completed_response = {
        "id": "resp_stream_1",
        "status": "completed",
        "model": model,
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": text}],
            }
        ],
        "usage": {"input_tokens": 1, "output_tokens": 2},
    }
    return b"".join(
        [
            sse_event(
                {
                    "type": "response.created",
                    "response": {
                        "id": "resp_stream_1",
                        "status": "in_progress",
                        "model": model,
                    },
                }
            ),
            sse_event(
                {
                    "type": "response.output_text.delta",
                    "delta": text[0],
                    "output_index": 0,
                    "content_index": 0,
                }
            ),
            sse_event(
                {
                    "type": "response.output_text.delta",
                    "delta": text[1:],
                    "output_index": 0,
                    "content_index": 0,
                }
            ),
            sse_event(
                {
                    "type": "response.output_text.done",
                    "text": text,
                    "output_index": 0,
                    "content_index": 0,
                }
            ),
            sse_event(
                {
                    "type": "response.completed",
                    "response": completed_response,
                }
            ),
        ]
    )


class FakeStreamingResponse(object):
    def __init__(self, body, status_code=200, headers=None):
        self._body = io.BytesIO(body)
        self._status_code = status_code
        self.headers = headers or {"Content-Type": "text/event-stream"}
        self.closed = False
        self.readline_sizes = []

    def getcode(self):
        return self._status_code

    def readline(self, size=-1):
        self.readline_sizes.append(size)
        return self._body.readline(size)

    def read(self, size=-1):
        return self._body.read(size)

    def close(self):
        self.closed = True
        self._body.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class InterruptingStreamingResponse(FakeStreamingResponse):
    def readline(self, size=-1):
        line = super(InterruptingStreamingResponse, self).readline(size)
        if line:
            return line
        raise socket.timeout("stream stalled")


class IncompleteStreamingResponse(FakeStreamingResponse):
    def readline(self, size=-1):
        line = super(IncompleteStreamingResponse, self).readline(size)
        if line:
            return line
        raise IncompleteRead(b"provider-private-partial")


class FakeOpener(object):
    def __init__(self, response):
        self.response = response
        self.calls = []

    def open(self, request, timeout=None):
        self.calls.append((request, timeout))
        return self.response


class InvalidStreamingTransport(object):
    def open_stream(self, url, headers, body, timeout, max_response_bytes):
        return object()


class AiStreamingPayloadTests(unittest.TestCase):
    def test_builds_streaming_payloads_for_both_openai_protocols(self):
        responses_payload = build_request_payload(
            api_style=API_STYLE_RESPONSES,
            model="responses-model",
            instructions="reply",
            input_data="1",
            stream=True,
        )
        chat_payload = build_request_payload(
            api_style=API_STYLE_CHAT_COMPLETIONS,
            model="chat-model",
            instructions="reply",
            input_data="1",
            stream=True,
        )

        self.assertIs(responses_payload["stream"], True)
        self.assertIs(chat_payload["stream"], True)


class ResponsesStreamAccumulatorTests(unittest.TestCase):
    def test_accumulates_only_deltas_and_uses_completed_response_as_payload(self):
        accumulator = AiStreamAccumulator(API_STYLE_RESPONSES)
        completed_response = {
            "id": "resp_1",
            "status": "completed",
            "model": "responses-model",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "节点特征"}],
                }
            ],
            "usage": {"output_tokens": 4},
        }

        self.assertIsNone(
            accumulator.consume(
                event_data(
                    {
                        "type": "response.created",
                        "response": {"id": "resp_1", "status": "in_progress"},
                    }
                )
            )
        )
        self.assertIs(accumulator.is_terminal, False)
        self.assertEqual(
            accumulator.consume(
                event_data({"type": "response.output_text.delta", "delta": "节点"})
            ),
            "节点",
        )
        self.assertEqual(
            accumulator.consume(
                event_data({"type": "response.output_text.delta", "delta": "特征"})
            ),
            "特征",
        )
        self.assertIsNone(
            accumulator.consume(
                event_data(
                    {
                        "type": "response.output_text.done",
                        "text": "节点特征",
                    }
                )
            )
        )
        self.assertIs(accumulator.is_terminal, False)
        self.assertIsNone(
            accumulator.consume(
                event_data(
                    {
                        "type": "response.completed",
                        "response": completed_response,
                    }
                )
            )
        )
        self.assertIs(accumulator.is_terminal, True)

        text, payload = accumulator.finalize()

        self.assertEqual(text, "节点特征")
        self.assertEqual(payload, completed_response)

    def test_rejects_refusal_incomplete_error_and_missing_terminal_event(self):
        cases = [
            (
                {"type": "response.refusal.delta", "delta": "cannot"},
                AiRefusalError,
            ),
            (
                {
                    "type": "response.incomplete",
                    "response": {
                        "status": "incomplete",
                        "incomplete_details": {"reason": "max_output_tokens"},
                    },
                },
                AiIncompleteResponseError,
            ),
            (
                {
                    "type": "error",
                    "code": "server_error",
                    "message": "failed",
                },
                AiProtocolError,
            ),
        ]
        for payload, error_type in cases:
            with self.subTest(event_type=payload["type"]):
                accumulator = AiStreamAccumulator(API_STYLE_RESPONSES)
                with self.assertRaises(error_type):
                    accumulator.consume(event_data(payload))

        accumulator = AiStreamAccumulator(API_STYLE_RESPONSES)
        accumulator.consume(
            event_data({"type": "response.output_text.delta", "delta": "partial"})
        )
        with self.assertRaises(AiRetryableStreamError):
            accumulator.finalize()

    def test_marks_retryable_server_events_without_exposing_provider_text(self):
        cases = [
            {
                "type": "error",
                "code": "server_error",
                "message": "provider-private-detail",
            },
            {
                "type": "response.failed",
                "response": {
                    "status": "failed",
                    "error": {
                        "code": "server_error",
                        "message": "provider-private-detail",
                    },
                },
            },
        ]

        for payload in cases:
            accumulator = AiStreamAccumulator(API_STYLE_RESPONSES)
            with self.subTest(event_type=payload["type"]):
                with self.assertRaises(AiRetryableStreamError) as caught:
                    accumulator.consume(event_data(payload))
                self.assertNotIn("provider-private-detail", str(caught.exception))

        quota = AiStreamAccumulator(API_STYLE_RESPONSES)
        with self.assertRaises(AiProtocolError) as caught:
            quota.consume(
                event_data(
                    {
                        "type": "error",
                        "code": "insufficient_quota",
                        "message": "provider-private-detail",
                    }
                )
            )
        self.assertNotIsInstance(caught.exception, AiRetryableStreamError)
        self.assertNotIn("provider-private-detail", str(caught.exception))

    def test_rejects_data_after_completed_event(self):
        accumulator = AiStreamAccumulator(API_STYLE_RESPONSES)
        accumulator.consume(
            event_data(
                {
                    "type": "response.completed",
                    "response": {
                        "status": "completed",
                        "output_text": "a",
                    },
                }
            )
        )

        with self.assertRaises(AiProtocolError):
            accumulator.consume(
                event_data(
                    {
                        "type": "response.output_text.delta",
                        "delta": "b",
                    }
                )
            )

    def test_accepts_multiple_output_text_done_parts(self):
        accumulator = AiStreamAccumulator(API_STYLE_RESPONSES)
        for output_index, text in enumerate(("one", "two")):
            accumulator.consume(
                event_data(
                    {
                        "type": "response.output_text.delta",
                        "delta": text,
                        "output_index": output_index,
                        "content_index": 0,
                    }
                )
            )
            accumulator.consume(
                event_data(
                    {
                        "type": "response.output_text.done",
                        "text": text,
                        "output_index": output_index,
                        "content_index": 0,
                    }
                )
            )
        completed_response = {
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "one"}],
                },
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "two"}],
                },
            ],
        }
        accumulator.consume(
            event_data(
                {
                    "type": "response.completed",
                    "response": completed_response,
                }
            )
        )

        text, payload = accumulator.finalize()

        self.assertEqual(text, "onetwo")
        self.assertEqual(payload, completed_response)

    def test_validates_each_done_part_and_rejects_late_part_delta(self):
        wrong_done = AiStreamAccumulator(API_STYLE_RESPONSES)
        wrong_done.consume(
            event_data(
                {
                    "type": "response.output_text.delta",
                    "delta": "one",
                    "output_index": 0,
                    "content_index": 0,
                }
            )
        )
        with self.assertRaises(AiProtocolError):
            wrong_done.consume(
                event_data(
                    {
                        "type": "response.output_text.done",
                        "text": "wrong",
                        "output_index": 0,
                        "content_index": 0,
                    }
                )
            )

        late_delta = AiStreamAccumulator(API_STYLE_RESPONSES)
        done_event = {
            "type": "response.output_text.done",
            "text": "one",
            "output_index": 0,
            "content_index": 0,
        }
        late_delta.consume(
            event_data(
                {
                    "type": "response.output_text.delta",
                    "delta": "one",
                    "output_index": 0,
                    "content_index": 0,
                }
            )
        )
        late_delta.consume(event_data(done_event))
        with self.assertRaises(AiProtocolError):
            late_delta.consume(
                event_data(
                    {
                        "type": "response.output_text.delta",
                        "delta": "late",
                        "output_index": 0,
                        "content_index": 0,
                    }
                )
            )
        with self.assertRaises(AiProtocolError):
            late_delta.consume(
                event_data(
                    {
                        "type": "response.output_text.delta",
                        "delta": "",
                        "output_index": 0,
                        "content_index": 0,
                    }
                )
            )
        with self.assertRaises(AiProtocolError):
            late_delta.consume(event_data(done_event))

        mixed_indexing = AiStreamAccumulator(API_STYLE_RESPONSES)
        mixed_indexing.consume(
            event_data(
                {
                    "type": "response.output_text.delta",
                    "delta": "unindexed",
                }
            )
        )
        with self.assertRaises(AiProtocolError):
            mixed_indexing.consume(
                event_data(
                    {
                        "type": "response.output_text.delta",
                        "delta": "indexed",
                        "output_index": 1,
                        "content_index": 0,
                    }
                )
            )

    def test_final_refusal_is_redacted(self):
        accumulator = AiStreamAccumulator(API_STYLE_RESPONSES)
        accumulator.consume(
            event_data(
                {
                    "type": "response.output_text.delta",
                    "delta": "visible",
                }
            )
        )
        accumulator.consume(
            event_data(
                {
                    "type": "response.completed",
                    "response": {
                        "status": "completed",
                        "output": [
                            {
                                "type": "message",
                                "content": [
                                    {
                                        "type": "refusal",
                                        "refusal": "provider-private-refusal",
                                    }
                                ],
                            }
                        ],
                    },
                }
            )
        )

        with self.assertRaises(AiRefusalError) as caught:
            accumulator.finalize()
        self.assertNotIn("provider-private-refusal", str(caught.exception))


class ChatStreamAccumulatorTests(unittest.TestCase):
    def test_accumulates_chat_deltas_finish_reason_usage_and_done(self):
        accumulator = AiStreamAccumulator(API_STYLE_CHAT_COMPLETIONS)
        chunks = [
            {
                "id": "chat_1",
                "model": "chat-model",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": ""},
                        "finish_reason": None,
                    }
                ],
            },
            {
                "id": "chat_1",
                "model": "chat-model",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "hello"},
                        "finish_reason": None,
                    }
                ],
            },
            {
                "id": "chat_1",
                "model": "chat-model",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": " world"},
                        "finish_reason": "stop",
                    }
                ],
            },
            {
                "id": "chat_1",
                "model": "chat-model",
                "choices": [],
                "usage": {"prompt_tokens": 1, "completion_tokens": 2},
            },
        ]

        deltas = [accumulator.consume(event_data(chunk)) for chunk in chunks]
        self.assertEqual(deltas, [None, "hello", " world", None])
        self.assertIsNone(accumulator.consume("[DONE]"))
        self.assertIs(accumulator.is_terminal, True)

        text, payload = accumulator.finalize()

        self.assertEqual(text, "hello world")
        self.assertEqual(payload["id"], "chat_1")
        self.assertEqual(payload["model"], "chat-model")
        self.assertEqual(payload["usage"], {"prompt_tokens": 1, "completion_tokens": 2})

    def test_rejects_chat_refusal_incomplete_and_missing_done(self):
        refusal = AiStreamAccumulator(API_STYLE_CHAT_COMPLETIONS)
        with self.assertRaises(AiRefusalError):
            refusal.consume(
                event_data(
                    {
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"refusal": "cannot"},
                                "finish_reason": "content_filter",
                            }
                        ]
                    }
                )
            )

        incomplete = AiStreamAccumulator(API_STYLE_CHAT_COMPLETIONS)
        with self.assertRaises(AiIncompleteResponseError):
            incomplete.consume(
                event_data(
                    {
                        "choices": [
                            {
                                "index": 0,
                                "delta": {},
                                "finish_reason": "length",
                            }
                        ]
                    }
                )
            )

        missing_done = AiStreamAccumulator(API_STYLE_CHAT_COMPLETIONS)
        missing_done.consume(
            event_data(
                {
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": "complete-looking"},
                            "finish_reason": "stop",
                        }
                    ]
                }
            )
        )
        with self.assertRaises(AiRetryableStreamError):
            missing_done.finalize()

    def test_rejects_data_after_done_marker(self):
        accumulator = AiStreamAccumulator(API_STYLE_CHAT_COMPLETIONS)
        accumulator.consume("[DONE]")

        with self.assertRaises(AiProtocolError):
            accumulator.consume(
                event_data(
                    {
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": "late"},
                                "finish_reason": "stop",
                            }
                        ]
                    }
                )
            )


class HttpEventStreamTests(unittest.TestCase):
    def test_decodes_utf8_comments_crlf_and_multiline_data_frames(self):
        raw_response = FakeStreamingResponse(
            b": keep-alive\r\n"
            b"event: response.output_text.delta\r\n"
            b'data: {"type":\r\n'
            b'data: "response.output_text.delta","delta":"one"}\r\n'
            b"\r\n" + "data: 你好\n\n".encode("utf-8")
        )

        with HttpEventStream(raw_response, max_response_bytes=1024) as event_stream:
            frames = list(event_stream)

        self.assertEqual(
            frames,
            [
                '{"type":\n"response.output_text.delta","delta":"one"}',
                "你好",
            ],
        )
        self.assertTrue(raw_response.closed)

    def test_rejects_invalid_utf8_and_cumulative_size_over_limit(self):
        invalid_utf8 = FakeStreamingResponse(b"data: \xff\n\n")
        with self.assertRaises(AiProtocolError):
            list(HttpEventStream(invalid_utf8, max_response_bytes=64))
        self.assertTrue(invalid_utf8.closed)

        oversized = FakeStreamingResponse(b"data: " + (b"x" * 64) + b"\n\n")
        with self.assertRaises(AiResponseTooLargeError):
            list(HttpEventStream(oversized, max_response_bytes=32))
        self.assertTrue(oversized.closed)

    def test_close_is_idempotent_and_closes_the_underlying_response(self):
        raw_response = FakeStreamingResponse(b"data: one\n\ndata: two\n\n")
        event_stream = HttpEventStream(raw_response, max_response_bytes=128)
        iterator = iter(event_stream)

        self.assertEqual(next(iterator), "one")
        event_stream.close()
        event_stream.close()

        self.assertTrue(raw_response.closed)


class UrllibStreamingIntegrationTests(unittest.TestCase):
    def test_open_stream_is_context_managed_and_keeps_auth_unredirected(self):
        raw_response = FakeStreamingResponse(
            b"data: first\n\ndata: [DONE]\n\n",
            headers={
                "Content-Type": "text/event-stream; charset=utf-8",
                "X-Request-Id": "req_stream_1",
            },
        )
        opener = FakeOpener(raw_response)
        transport = UrllibTransport(opener=opener)

        with transport.open_stream(
            "https://api.openai.com/v1/responses",
            {
                "Authorization": "Bearer session-secret",
                "Accept": "text/event-stream",
                "Content-Type": "application/json",
            },
            b'{"stream":true}',
            timeout=9,
            max_response_bytes=1024,
        ) as event_stream:
            self.assertEqual(event_stream.status_code, 200)
            self.assertEqual(event_stream.headers["X-Request-Id"], "req_stream_1")
            self.assertEqual(list(event_stream), ["first", "[DONE]"])

        request, timeout = opener.calls[0]
        normal_headers = {key.lower(): value for key, value in request.headers.items()}
        unredirected_headers = {
            key.lower(): value for key, value in request.unredirected_hdrs.items()
        }
        self.assertEqual(timeout, 9)
        self.assertNotIn("authorization", normal_headers)
        self.assertEqual(unredirected_headers["authorization"], "Bearer session-secret")
        self.assertTrue(raw_response.closed)

    def test_client_stream_text_yields_deltas_and_sends_stream_true(self):
        raw_response = FakeStreamingResponse(
            responses_stream(),
            headers={
                "Content-Type": "text/event-stream",
                "X-Request-Id": "req_client_stream",
            },
        )
        opener = FakeOpener(raw_response)
        client = OpenAICompatibleClient(
            config=AiClientConfig(model="responses-model", timeout_seconds=7),
            transport=UrllibTransport(opener=opener),
            environ={"OPENAI_API_KEY": "stream-secret"},
        )

        deltas = list(client.stream_text("reply briefly", "1"))

        self.assertEqual(deltas, ["你", "好"])
        request, timeout = opener.calls[0]
        payload = json.loads(request.data.decode("utf-8"))
        headers = {key.lower(): value for key, value in request.headers.items()}
        self.assertIs(payload["stream"], True)
        self.assertEqual(timeout, 7)
        self.assertEqual(headers["accept"], "text/event-stream")
        self.assertEqual(headers["accept-encoding"], "identity")
        self.assertTrue(raw_response.closed)

    def test_client_stops_and_closes_immediately_after_terminal_event(self):
        raw_response = FakeStreamingResponse(
            responses_stream()
            + sse_event(
                {
                    "type": "response.output_text.delta",
                    "delta": "must-not-be-read",
                }
            )
        )
        client = OpenAICompatibleClient(
            config=AiClientConfig(model="responses-model"),
            transport=UrllibTransport(opener=FakeOpener(raw_response)),
            environ={"OPENAI_API_KEY": "stream-secret"},
        )

        self.assertEqual(list(client.stream_text(None, "1")), ["你", "好"])
        self.assertTrue(raw_response.closed)

    def test_client_maps_midstream_timeout_and_closes_response(self):
        raw_response = InterruptingStreamingResponse(
            sse_event(
                {
                    "type": "response.output_text.delta",
                    "delta": "partial",
                }
            )
        )
        client = OpenAICompatibleClient(
            config=AiClientConfig(model="responses-model"),
            transport=UrllibTransport(opener=FakeOpener(raw_response)),
            environ={"OPENAI_API_KEY": "stream-secret"},
        )
        stream = client.stream_text(None, "1")

        self.assertEqual(next(stream), "partial")
        with self.assertRaises(AiTimeoutError):
            next(stream)
        self.assertTrue(raw_response.closed)

    def test_client_maps_incomplete_http_stream_and_closes_response(self):
        raw_response = IncompleteStreamingResponse(b"")
        client = OpenAICompatibleClient(
            config=AiClientConfig(model="responses-model"),
            transport=UrllibTransport(opener=FakeOpener(raw_response)),
            environ={"OPENAI_API_KEY": "stream-secret"},
        )

        with self.assertRaisesRegex(AiTransportError, "AI 流式连接中断"):
            list(client.stream_text(None, "1"))
        self.assertTrue(raw_response.closed)

    def test_client_rejects_non_model_stream_contract_errors(self):
        compressed_response = FakeStreamingResponse(
            responses_stream(),
            headers={
                "Content-Type": "text/event-stream",
                "Content-Encoding": "gzip",
            },
        )
        compressed_client = OpenAICompatibleClient(
            config=AiClientConfig(model="responses-model"),
            transport=UrllibTransport(opener=FakeOpener(compressed_response)),
            environ={"OPENAI_API_KEY": "stream-secret"},
        )
        invalid_transport_client = OpenAICompatibleClient(
            config=AiClientConfig(model="responses-model"),
            transport=InvalidStreamingTransport(),
            environ={"OPENAI_API_KEY": "stream-secret"},
        )

        with self.assertRaises(AiProtocolError):
            list(compressed_client.stream_text(None, "1"))
        with self.assertRaises(AiProtocolError):
            list(invalid_transport_client.stream_text(None, "1"))
        self.assertTrue(compressed_response.closed)

    def test_client_propagates_retryable_server_event_and_clean_eof(self):
        bodies = (
            sse_event(
                {
                    "type": "response.failed",
                    "response": {
                        "status": "failed",
                        "error": {
                            "code": "server_error",
                            "message": "provider-private-detail",
                        },
                    },
                }
            ),
            b"",
        )
        for body in bodies:
            raw_response = FakeStreamingResponse(body)
            client = OpenAICompatibleClient(
                config=AiClientConfig(model="responses-model"),
                transport=UrllibTransport(opener=FakeOpener(raw_response)),
                environ={"OPENAI_API_KEY": "stream-secret"},
            )

            with self.subTest(body=body):
                with self.assertRaises(AiRetryableStreamError) as caught:
                    list(client.stream_text(None, "1"))
                self.assertNotIn("provider-private-detail", str(caught.exception))
                self.assertTrue(raw_response.closed)


if __name__ == "__main__":
    unittest.main()
