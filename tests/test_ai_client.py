import ast
import io
import json
import socket
import ssl
import tempfile
import traceback
import unittest
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request

from arnold_magic_node.core.ai_protocol import AiError, AiProtocolError
from arnold_magic_node.tools.ai_client import (
    AiAuthenticationError,
    AiClientError,
    AiClientConfig,
    AiConfigurationError,
    AiHttpError,
    AiRateLimitError,
    AiResponseTooLargeError,
    AiTimeoutError,
    AiTlsError,
    AiTransportError,
    HttpResponse,
    OpenAICompatibleClient,
    UrllibTransport,
    create_openai_client,
)
from arnold_magic_node.tools.ai_settings import (
    ensure_ai_settings,
    load_ai_settings,
    save_ai_settings,
)


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {"summary": {"type": "string"}},
    "required": ["summary"],
    "additionalProperties": False,
}


class FakeTransport(object):
    def __init__(self, responses=None, error=None):
        self.responses = list(responses or [])
        self.error = error
        self.calls = []

    def post(self, url, headers, body, timeout, max_response_bytes):
        self.calls.append(
            {
                "url": url,
                "headers": dict(headers),
                "body": body,
                "timeout": timeout,
                "max_response_bytes": max_response_bytes,
            }
        )
        if self.error is not None:
            raise self.error
        return self.responses.pop(0)


class FakeUrlResponse(object):
    def __init__(self, body, status_code=200, headers=None):
        self._stream = io.BytesIO(body)
        self.status_code = status_code
        self.headers = headers or {}
        self.read_sizes = []
        self.closed = False

    def read(self, size=-1):
        self.read_sizes.append(size)
        return self._stream.read(size)

    def getcode(self):
        return self.status_code

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.closed = True
        self._stream.close()
        return False


class FakeOpener(object):
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def open(self, request, timeout):
        self.calls.append((request, timeout))
        if self.error is not None:
            raise self.error
        return self.response


def json_response(payload, status_code=200, headers=None):
    return HttpResponse(
        status_code=status_code,
        body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers or {},
    )


class OpenAICompatibleClientTests(unittest.TestCase):
    def test_calls_responses_with_environment_key_and_returns_json(self):
        transport = FakeTransport(
            [
                json_response(
                    {
                        "id": "resp_123",
                        "model": "test-model",
                        "status": "completed",
                        "usage": {"input_tokens": 20, "output_tokens": 8},
                        "output": [
                            {
                                "type": "message",
                                "content": [
                                    {
                                        "type": "output_text",
                                        "text": '{"summary":"node graph"}',
                                    }
                                ],
                            }
                        ],
                    },
                    headers={"x-request-id": "req_123"},
                )
            ]
        )
        client = OpenAICompatibleClient(
            config=AiClientConfig(
                base_url="https://api.openai.com/v1/",
                model="test-model",
                timeout_seconds=12,
            ),
            transport=transport,
            environ={"OPENAI_API_KEY": "secret-token"},
        )

        result = client.generate_json(
            instructions="Extract features",
            input_data={"nodes": ["file1"]},
            response_schema=RESPONSE_SCHEMA,
            schema_name="node_features",
        )

        self.assertEqual(result.data, {"summary": "node graph"})
        self.assertEqual(result.response_id, "resp_123")
        self.assertEqual(result.request_id, "req_123")
        self.assertEqual(result.usage, {"input_tokens": 20, "output_tokens": 8})
        call = transport.calls[0]
        self.assertEqual(call["url"], "https://api.openai.com/v1/responses")
        self.assertEqual(call["headers"]["Authorization"], "Bearer secret-token")
        self.assertEqual(call["timeout"], 12)
        self.assertEqual(
            json.loads(call["body"].decode("utf-8"))["model"], "test-model"
        )

    def test_calls_chat_completions_without_auth_for_local_service(self):
        transport = FakeTransport(
            [
                json_response(
                    {
                        "id": "chat_123",
                        "model": "local-model",
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "message": {"content": '{"summary":"local"}'},
                            }
                        ],
                    }
                )
            ]
        )
        client = OpenAICompatibleClient(
            config=AiClientConfig(
                base_url="http://127.0.0.1:1234/v1",
                api_style="chat_completions",
                model="local-model",
                max_output_tokens=128,
                chat_token_parameter="max_completion_tokens",
            ),
            transport=transport,
            environ={"OPENAI_API_KEY": "must-not-leak"},
        )

        result = client.generate_json(
            "Extract features", "graph", RESPONSE_SCHEMA, "node_features"
        )

        self.assertEqual(result.data, {"summary": "local"})
        call = transport.calls[0]
        self.assertEqual(call["url"], "http://127.0.0.1:1234/v1/chat/completions")
        self.assertNotIn("Authorization", call["headers"])
        request_payload = json.loads(call["body"].decode("utf-8"))
        self.assertEqual(request_payload["max_completion_tokens"], 128)
        self.assertNotIn("max_tokens", request_payload)
        self.assertEqual(request_payload["response_format"]["type"], "json_schema")

    def test_rejects_insecure_remote_url_and_embedded_credentials(self):
        for base_url in (
            "http://api.example.com/v1",
            "https://user:password@api.example.com/v1",
            "https://api.example.com/v1?debug=true",
            "https://api.example.com/v1#fragment",
            "https://api.example.com/v1\\responses",
        ):
            with self.subTest(base_url=base_url):
                with self.assertRaises(AiConfigurationError):
                    OpenAICompatibleClient(
                        config=AiClientConfig(base_url=base_url),
                        transport=FakeTransport(),
                        environ={"OPENAI_API_KEY": "secret"},
                    )

    def test_does_not_send_default_openai_key_to_third_party_origin(self):
        transport = FakeTransport()
        client = OpenAICompatibleClient(
            config=AiClientConfig(base_url="https://api.example.com/v1"),
            transport=transport,
            environ={"OPENAI_API_KEY": "openai-secret"},
        )

        with self.assertRaises(AiConfigurationError):
            client.generate_json("test", {}, RESPONSE_SCHEMA, "result")
        self.assertEqual(transport.calls, [])

    def test_custom_key_environment_can_target_compatible_https_service(self):
        transport = FakeTransport(
            [
                json_response(
                    {
                        "status": "completed",
                        "output_text": "compatible",
                    }
                )
            ]
        )
        client = OpenAICompatibleClient(
            config=AiClientConfig(
                base_url="https://ai.example.com/v1",
                model="compatible-model",
                api_key_env="COMPATIBLE_AI_KEY",
            ),
            transport=transport,
            environ={"COMPATIBLE_AI_KEY": "third-party-secret"},
        )

        result = client.generate_text("test", "graph")

        self.assertEqual(result.text, "compatible")
        self.assertEqual(
            transport.calls[0]["headers"]["Authorization"],
            "Bearer third-party-secret",
        )

    def test_explicit_session_key_can_target_compatible_https_service(self):
        transport = FakeTransport(
            [json_response({"status": "completed", "output_text": "ok"})]
        )
        client = OpenAICompatibleClient(
            config=AiClientConfig(base_url="https://ai.example.com/v1"),
            api_key="session-secret",
            transport=transport,
            environ={"OPENAI_API_KEY": "must-not-leak"},
        )

        client.generate_text("test", "graph")

        self.assertEqual(
            transport.calls[0]["headers"]["Authorization"],
            "Bearer session-secret",
        )

    def test_requires_key_for_remote_endpoint(self):
        transport = FakeTransport()
        client = OpenAICompatibleClient(
            config=AiClientConfig(base_url="https://api.example.com/v1"),
            transport=transport,
            environ={},
        )

        with self.assertRaises(AiConfigurationError):
            client.generate_json("test", {}, RESPONSE_SCHEMA, "result")
        self.assertEqual(transport.calls, [])

    def test_maps_authentication_and_rate_limit_errors_without_leaking_key(self):
        cases = [
            (
                json_response(
                    {
                        "error": {
                            "message": "invalid secret-token",
                            "code": "invalid_api_key",
                        }
                    },
                    status_code=401,
                    headers={"x-request-id": "req_auth"},
                ),
                AiAuthenticationError,
            ),
            (
                json_response(
                    {"error": {"message": "slow down", "code": "rate_limit"}},
                    status_code=429,
                    headers={"retry-after": "2"},
                ),
                AiRateLimitError,
            ),
        ]

        for response, error_type in cases:
            with self.subTest(error_type=error_type.__name__):
                client = OpenAICompatibleClient(
                    config=AiClientConfig(model="test-model"),
                    transport=FakeTransport([response]),
                    environ={"OPENAI_API_KEY": "secret-token"},
                )
                with self.assertRaises(error_type) as raised:
                    client.generate_json("test", {}, RESPONSE_SCHEMA, "result")
                self.assertNotIn("secret-token", str(raised.exception))
                self.assertEqual(raised.exception.status_code, response.status_code)
                self.assertEqual(len(client.transport.calls), 1)
                self.assertEqual(
                    raised.exception.error_code,
                    "invalid_api_key" if response.status_code == 401 else "rate_limit",
                )
                if response.status_code == 401:
                    self.assertIn("[REDACTED]", str(raised.exception))
                    self.assertEqual(raised.exception.request_id, "req_auth")
                else:
                    self.assertEqual(raised.exception.retry_after, "2")

    def test_maps_server_error_and_timeout(self):
        client = OpenAICompatibleClient(
            config=AiClientConfig(model="test-model"),
            transport=FakeTransport(
                [json_response({"error": {"message": "server failed"}}, 500)]
            ),
            environ={"OPENAI_API_KEY": "secret"},
        )
        with self.assertRaises(AiHttpError) as raised:
            client.generate_json("test", {}, RESPONSE_SCHEMA, "result")
        self.assertEqual(raised.exception.status_code, 500)

        timeout_client = OpenAICompatibleClient(
            config=AiClientConfig(model="test-model"),
            transport=FakeTransport(error=socket.timeout("timed out")),
            environ={"OPENAI_API_KEY": "secret"},
        )
        with self.assertRaises(AiTimeoutError):
            timeout_client.generate_json("test", {}, RESPONSE_SCHEMA, "result")

    def test_maps_url_transport_failures_without_exposing_details(self):
        cases = [
            (URLError(socket.timeout("timed out")), AiTimeoutError),
            (URLError(ssl.SSLError("bad certificate")), AiTlsError),
            (URLError("private host details"), AiTransportError),
            (IncompleteRead(b"private partial body"), AiTransportError),
            (OSError("private socket details"), AiTransportError),
        ]
        for transport_error, expected_error in cases:
            with self.subTest(expected_error=expected_error.__name__):
                client = OpenAICompatibleClient(
                    transport=FakeTransport(error=transport_error),
                    environ={"OPENAI_API_KEY": "secret"},
                )
                with self.assertRaises(expected_error) as raised:
                    client.generate_text("test", "graph")
                self.assertNotIn("private", str(raised.exception))
                formatted = "".join(
                    traceback.format_exception(
                        type(raised.exception),
                        raised.exception,
                        raised.exception.__traceback__,
                    )
                )
                self.assertNotIn("private", formatted)

    def test_redacts_api_key_from_all_http_error_metadata(self):
        api_key = "metadata-secret"
        response = json_response(
            {
                "error": {
                    "message": "failed " + api_key,
                    "code": "code-" + api_key,
                }
            },
            status_code=429,
            headers={
                "x-request-id": "request-" + api_key,
                "retry-after": "retry-" + api_key,
            },
        )
        client = OpenAICompatibleClient(
            api_key=api_key,
            transport=FakeTransport([response]),
            environ={},
        )

        with self.assertRaises(AiRateLimitError) as raised:
            client.generate_text("test", "graph")

        error = raised.exception
        for value in (
            str(error),
            error.request_id,
            error.error_code,
            error.retry_after,
        ):
            self.assertNotIn(api_key, value)

    def test_rejects_response_larger_than_configured_limit(self):
        response = HttpResponse(
            status_code=200,
            body=b"{" + (b"x" * 100) + b"}",
            headers={},
        )
        client = OpenAICompatibleClient(
            config=AiClientConfig(
                model="test-model",
                max_response_bytes=64,
            ),
            transport=FakeTransport([response]),
            environ={"OPENAI_API_KEY": "secret"},
        )

        with self.assertRaises(AiResponseTooLargeError):
            client.generate_json("test", {}, RESPONSE_SCHEMA, "result")

    def test_rejects_oversized_request_invalid_transport_and_compression(self):
        request_client = OpenAICompatibleClient(
            config=AiClientConfig(max_request_bytes=100),
            transport=FakeTransport(),
            environ={"OPENAI_API_KEY": "secret"},
        )
        with self.assertRaises(AiConfigurationError):
            request_client.generate_text("test", "x" * 500)

        invalid_transport_client = OpenAICompatibleClient(
            transport=FakeTransport([object()]),
            environ={"OPENAI_API_KEY": "secret"},
        )
        with self.assertRaises(AiTransportError):
            invalid_transport_client.generate_text("test", "graph")

        compressed_client = OpenAICompatibleClient(
            transport=FakeTransport(
                [
                    json_response(
                        {"status": "completed", "output_text": "ok"},
                        headers={"Content-Encoding": "gzip"},
                    )
                ]
            ),
            environ={"OPENAI_API_KEY": "secret"},
        )
        with self.assertRaises(AiTransportError):
            compressed_client.generate_text("test", "graph")

    def test_rejects_invalid_success_envelopes(self):
        bodies = [
            b"\xff",
            b"[]",
            b'{"id":"one","id":"two"}',
        ]
        for body in bodies:
            with self.subTest(body=body):
                client = OpenAICompatibleClient(
                    transport=FakeTransport([HttpResponse(200, body, {})]),
                    environ={"OPENAI_API_KEY": "secret"},
                )
                with self.assertRaises(AiProtocolError):
                    client.generate_text("test", "graph")

    def test_validates_config_and_settings_mapping(self):
        invalid_configs = [
            AiClientConfig(schema_version=2),
            AiClientConfig(api_style="automatic"),
            AiClientConfig(model=""),
            AiClientConfig(api_key_env="BAD-NAME"),
            AiClientConfig(timeout_seconds=0),
            AiClientConfig(timeout_seconds=float("nan")),
            AiClientConfig(timeout_seconds=float("inf")),
            AiClientConfig(max_output_tokens=True),
            AiClientConfig(max_request_bytes=0),
            AiClientConfig(max_response_bytes=20 * 1024 * 1024),
            AiClientConfig(chat_token_parameter="automatic"),
        ]
        for config in invalid_configs:
            with self.subTest(config=config):
                with self.assertRaises(AiConfigurationError):
                    OpenAICompatibleClient(config=config, transport=FakeTransport())

        with self.assertRaises(AiConfigurationError):
            OpenAICompatibleClient(config={})
        with self.assertRaises(AiConfigurationError):
            AiClientConfig.from_mapping([])
        with self.assertRaises(AiConfigurationError):
            AiClientConfig.from_mapping({"unknown_option": True})

        for base_url in (
            "https://api.example.com:bad/v1",
            "https://[invalid/v1",
            "https://api.example.com/space here/v1",
        ):
            with self.subTest(base_url=base_url):
                with self.assertRaises(AiConfigurationError):
                    OpenAICompatibleClient(
                        config=AiClientConfig(base_url=base_url),
                        transport=FakeTransport(),
                    )

    def test_rejects_invalid_api_key_value(self):
        for api_key in ("unsafe\r\nheader", "非ASCII密钥", object(), "x" * 9000):
            with self.subTest(api_key=api_key):
                client = OpenAICompatibleClient(
                    api_key=api_key,
                    transport=FakeTransport(),
                    environ={},
                )
                with self.assertRaises(AiConfigurationError):
                    client.generate_text("test", "graph")

    def test_validates_structured_output_locally(self):
        invalid_outputs = [
            "{}",
            '{"summary": 42}',
            '{"summary": "ok", "unexpected": true}',
        ]
        for output_text in invalid_outputs:
            with self.subTest(output_text=output_text):
                client = OpenAICompatibleClient(
                    transport=FakeTransport(
                        [
                            json_response(
                                {
                                    "status": "completed",
                                    "output_text": output_text,
                                }
                            )
                        ]
                    ),
                    environ={"OPENAI_API_KEY": "secret"},
                )
                with self.assertRaises(AiProtocolError):
                    client.generate_json("test", "graph", RESPONSE_SCHEMA, "result")


class UrllibTransportTests(unittest.TestCase):
    def test_posts_bounded_json_and_keeps_authorization_unredirected(self):
        url_response = FakeUrlResponse(
            b'{"output_text":"ok"}',
            headers={"Content-Length": "20", "X-Request-Id": "req_1"},
        )
        opener = FakeOpener(response=url_response)
        transport = UrllibTransport(opener=opener)

        response = transport.post(
            "https://api.openai.com/v1/responses",
            {
                "Authorization": "Bearer secret",
                "Content-Type": "application/json",
            },
            b"{}",
            timeout=15,
            max_response_bytes=128,
        )

        request, timeout = opener.calls[0]
        normal_headers = {key.lower(): value for key, value in request.headers.items()}
        unredirected_headers = {
            key.lower(): value for key, value in request.unredirected_hdrs.items()
        }
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.data, b"{}")
        self.assertEqual(timeout, 15)
        self.assertNotIn("authorization", normal_headers)
        self.assertEqual(unredirected_headers["authorization"], "Bearer secret")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b'{"output_text":"ok"}')
        self.assertEqual(url_response.read_sizes, [129])
        self.assertTrue(url_response.closed)

    def test_converts_http_error_and_closes_its_stream(self):
        error_stream = io.BytesIO(b'{"error":{"message":"slow down"}}')
        http_error = HTTPError(
            "https://api.openai.com/v1/responses",
            429,
            "Too Many Requests",
            {"Retry-After": "2"},
            error_stream,
        )
        transport = UrllibTransport(opener=FakeOpener(error=http_error))

        response = transport.post(
            "https://api.openai.com/v1/responses",
            {},
            b"{}",
            timeout=10,
            max_response_bytes=1024,
        )

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["Retry-After"], "2")
        self.assertTrue(error_stream.closed)

    def test_rejects_content_length_over_limit_without_reading(self):
        url_response = FakeUrlResponse(
            b"small",
            headers={"Content-Length": "1000"},
        )
        transport = UrllibTransport(opener=FakeOpener(response=url_response))

        with self.assertRaises(AiResponseTooLargeError):
            transport.post(
                "https://api.openai.com/v1/responses",
                {},
                b"{}",
                timeout=10,
                max_response_bytes=32,
            )
        self.assertEqual(url_response.read_sizes, [])

    def test_rejects_streamed_body_over_limit_without_content_length(self):
        url_response = FakeUrlResponse(b"x" * 33)
        transport = UrllibTransport(opener=FakeOpener(response=url_response))

        with self.assertRaises(AiResponseTooLargeError):
            transport.post(
                "https://api.openai.com/v1/responses",
                {},
                b"{}",
                timeout=10,
                max_response_bytes=32,
            )
        self.assertEqual(url_response.read_sizes, [33])
        self.assertTrue(url_response.closed)

    def test_uses_proxy_free_opener_for_loopback(self):
        remote_opener = FakeOpener(
            response=FakeUrlResponse(b'{"output_text":"remote"}')
        )
        loopback_opener = FakeOpener(
            response=FakeUrlResponse(b'{"output_text":"local"}')
        )
        transport = UrllibTransport(
            opener=remote_opener,
            loopback_opener=loopback_opener,
        )

        response = transport.post(
            "http://127.0.0.1:1234/v1/responses",
            {},
            b"{}",
            timeout=10,
            max_response_bytes=128,
        )

        self.assertEqual(response.body, b'{"output_text":"local"}')
        self.assertEqual(remote_opener.calls, [])
        self.assertEqual(len(loopback_opener.calls), 1)

    def test_default_redirect_handler_raises_http_error(self):
        transport = UrllibTransport()
        redirect_handler = next(
            handler
            for handler in transport.opener.handlers
            if handler.__class__.__name__ == "_RejectRedirectHandler"
        )
        with self.assertRaises(HTTPError) as raised:
            redirect_handler.redirect_request(
                Request("https://api.openai.com/v1/responses"),
                io.BytesIO(b"redirect"),
                307,
                "Temporary Redirect",
                {"Location": "https://example.com/steal"},
                "https://example.com/steal",
            )
        self.assertEqual(raised.exception.code, 307)


class AiSettingsTests(unittest.TestCase):
    @staticmethod
    def _profile(settings, model_id=None):
        wanted = model_id or settings["fast_model_id"]
        return next(item for item in settings["models"] if item["id"] == wanted)

    def test_ai_settings_are_created_lazily_with_v3_model_profiles(self):
        with tempfile.TemporaryDirectory() as directory:
            user_root = Path(directory) / "user-data"
            settings_path = ensure_ai_settings(user_root=user_root)
            settings = load_ai_settings(user_root=user_root)

            self.assertEqual(
                settings_path,
                user_root / "settings" / "AI_Settings.json",
            )
            self.assertTrue(settings_path.is_file())
            self.assertEqual(settings["schema_version"], 3)
            self.assertTrue(settings["models"])
            self.assertIn("api_key", settings["models"][0])
            self.assertEqual(settings["models"][0]["api_key"], "")
            self.assertIn(
                settings["fast_model_id"], {item["id"] for item in settings["models"]}
            )
            self.assertIn(
                settings["complex_model_id"],
                {item["id"] for item in settings["models"]},
            )

    def test_legacy_single_model_settings_migrate_only_in_memory_until_save(self):
        legacy = {
            "schema_version": 1,
            "api_style": "responses",
            "base_url": "https://api.openai.com/v1",
            "model": "legacy-model",
            "api_key_env": "OPENAI_API_KEY",
            "timeout_seconds": 60,
            "max_output_tokens": 4096,
            "max_request_bytes": 1048576,
            "max_response_bytes": 2097152,
            "chat_token_parameter": "max_tokens",
        }
        with tempfile.TemporaryDirectory() as directory:
            user_root = Path(directory) / "user-data"
            settings_path = ensure_ai_settings(user_root=user_root)
            settings_path.write_text(json.dumps(legacy), encoding="utf-8")

            migrated = load_ai_settings(user_root=user_root)

            self.assertEqual(migrated["schema_version"], 3)
            self.assertEqual(
                [item["model"] for item in migrated["models"]], ["legacy-model"]
            )
            self.assertEqual(migrated["models"][0]["api_key"], "")
            self.assertEqual(
                json.loads(settings_path.read_text(encoding="utf-8"))["schema_version"],
                1,
            )

            save_ai_settings(migrated, user_root=user_root)
            persisted = json.loads(settings_path.read_text(encoding="utf-8"))

        self.assertEqual(persisted["schema_version"], 3)
        self.assertNotIn("model", persisted)

    def test_ai_settings_persist_each_model_url_key_and_order_in_plain_json(self):
        with tempfile.TemporaryDirectory() as directory:
            user_root = Path(directory) / "user-data"
            settings = load_ai_settings(user_root=user_root)
            original_models = [item["model"] for item in settings["models"]]
            first = self._profile(settings)
            first["base_url"] = "https://first.example/v1"
            first["api_key"] = "first-plain-secret"
            second = dict(first)
            second.update(
                {
                    "id": "second-id",
                    "model": "second-model",
                    "base_url": "https://second.example/v1",
                    "api_key": "second-plain-secret",
                }
            )
            settings["models"].insert(0, second)
            settings["fast_model_id"] = "second-id"
            settings_path = save_ai_settings(settings, user_root=user_root)
            reloaded = load_ai_settings(user_root=user_root)
            persisted_text = settings_path.read_text(encoding="utf-8")

        self.assertEqual(
            [item["model"] for item in reloaded["models"]],
            ["second-model"] + original_models,
        )
        self.assertEqual(reloaded["models"][0]["base_url"], "https://second.example/v1")
        self.assertEqual(reloaded["models"][0]["api_key"], "second-plain-secret")
        self.assertIn("first-plain-secret", persisted_text)
        self.assertIn("second-plain-secret", persisted_text)

    def test_existing_ai_settings_are_preserved_and_invalid_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            user_root = Path(directory) / "user-data"
            settings = load_ai_settings(user_root=user_root)
            self._profile(settings)["model"] = "custom-model"
            settings_path = save_ai_settings(settings, user_root=user_root)

            self.assertEqual(ensure_ai_settings(user_root=user_root), settings_path)
            self.assertEqual(
                self._profile(load_ai_settings(user_root=user_root))["model"],
                "custom-model",
            )
            with self.assertRaises(TypeError):
                save_ai_settings([], user_root=user_root)
            with self.assertRaises(AiConfigurationError):
                save_ai_settings(
                    {"schema_version": 3, "api_key": "wrong-level"},
                    user_root=user_root,
                )

    def test_factory_accepts_in_memory_settings_without_touching_maya(self):
        transport = FakeTransport(
            [json_response({"status": "completed", "output_text": "ok"})]
        )
        client = create_openai_client(
            settings={
                "schema_version": 1,
                "base_url": "http://localhost:1234/v1",
                "api_style": "responses",
                "model": "local-model",
            },
            transport=transport,
            environ={},
        )

        self.assertEqual(client.generate_text("test", "graph").text, "ok")

    def test_factory_uses_fast_profile_and_its_stored_key(self):
        transport = FakeTransport(
            [json_response({"status": "completed", "output_text": "ok"})]
        )
        settings = {
            "schema_version": 3,
            "models": [
                {
                    "id": "fast-id",
                    "model": "fast-model",
                    "base_url": "https://fast.example/v1",
                    "api_style": "responses",
                    "api_key": "stored-fast-secret",
                    "timeout_seconds": 12,
                    "max_output_tokens": 128,
                    "max_request_bytes": 4096,
                    "max_response_bytes": 8192,
                    "chat_token_parameter": "max_tokens",
                }
            ],
            "fast_model_id": "fast-id",
            "complex_model_id": "fast-id",
        }

        client = create_openai_client(
            settings=settings,
            transport=transport,
            environ={},
        )
        result = client.generate_text(None, "graph")

        self.assertEqual(result.text, "ok")
        self.assertEqual(transport.calls[0]["url"], "https://fast.example/v1/responses")
        self.assertEqual(
            transport.calls[0]["headers"]["Authorization"],
            "Bearer stored-fast-secret",
        )

    def test_invalid_base_url_does_not_overwrite_existing_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            user_root = Path(directory) / "user-data"
            settings = load_ai_settings(user_root=user_root)
            self._profile(settings)["model"] = "preserved-model"
            save_ai_settings(settings, user_root=user_root)
            self._profile(settings)["base_url"] = "http://api.example.com/v1"

            with self.assertRaises(AiConfigurationError):
                save_ai_settings(settings, user_root=user_root)

            persisted = load_ai_settings(user_root=user_root)

        self.assertEqual(self._profile(persisted)["model"], "preserved-model")
        self.assertEqual(
            self._profile(persisted)["base_url"],
            "https://api.openai.com/v1",
        )

    def test_valid_settings_can_replace_an_invalid_legacy_base_url(self):
        with tempfile.TemporaryDirectory() as directory:
            user_root = Path(directory) / "user-data"
            settings_path = ensure_ai_settings(user_root=user_root)
            legacy_settings = {
                "schema_version": 1,
                "api_style": "responses",
                "base_url": "http://legacy.example/v1",
                "model": "legacy-model",
                "api_key_env": "OPENAI_API_KEY",
                "timeout_seconds": 60,
                "max_output_tokens": 4096,
                "max_request_bytes": 1048576,
                "max_response_bytes": 2097152,
                "chat_token_parameter": "max_tokens",
            }
            settings_path.write_text(json.dumps(legacy_settings), encoding="utf-8")
            updated_settings = load_ai_settings(user_root=user_root)
            self._profile(updated_settings)["base_url"] = (
                "https://compatible.example/v1"
            )

            save_ai_settings(updated_settings, user_root=user_root)

            persisted = load_ai_settings(user_root=user_root)

        self.assertEqual(
            self._profile(persisted)["base_url"],
            "https://compatible.example/v1",
        )

    def test_malformed_v3_settings_fail_with_configuration_error_on_load(self):
        with tempfile.TemporaryDirectory() as directory:
            user_root = Path(directory) / "user-data"
            settings_path = ensure_ai_settings(user_root=user_root)
            settings_path.write_text(
                json.dumps(
                    {
                        "schema_version": 3,
                        "models": [],
                        "fast_model_id": "missing",
                        "complex_model_id": "missing",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(AiConfigurationError):
                load_ai_settings(user_root=user_root)


class LightweightDependencyTests(unittest.TestCase):
    def test_ai_runtime_uses_no_third_party_http_or_openai_sdk(self):
        project_root = Path(__file__).resolve().parents[1]
        forbidden = {"httpx", "openai", "requests"}
        imported_roots = set()
        for relative_path in (
            "arnold_magic_node/core/ai_protocol.py",
            "arnold_magic_node/tools/ai_client.py",
            "arnold_magic_node/tools/ai_credentials.py",
            "arnold_magic_node/tools/ai_routing.py",
            "arnold_magic_node/tools/ai_settings.py",
        ):
            source = (project_root / relative_path).read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported_roots.update(
                        alias.name.split(".", 1)[0] for alias in node.names
                    )
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    imported_roots.add((node.module or "").split(".", 1)[0])

        self.assertTrue(forbidden.isdisjoint(imported_roots))

    def test_all_public_ai_failures_share_one_base_error(self):
        self.assertTrue(issubclass(AiClientError, AiError))
        self.assertTrue(issubclass(AiProtocolError, AiError))


if __name__ == "__main__":
    unittest.main()
