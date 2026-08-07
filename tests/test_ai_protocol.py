import json
import unittest

from arnold_magic_node.core.ai_protocol import (
    API_STYLE_CHAT_COMPLETIONS,
    API_STYLE_RESPONSES,
    AiIncompleteResponseError,
    AiProtocolError,
    AiRefusalError,
    build_request_payload,
    parse_json_output,
    parse_response_text,
    validate_json_schema_subset,
)


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {"summary": {"type": "string"}},
    "required": ["summary"],
    "additionalProperties": False,
}


class AiRequestPayloadTests(unittest.TestCase):
    def test_builds_responses_structured_output_payload(self):
        payload = build_request_payload(
            api_style=API_STYLE_RESPONSES,
            model="test-model",
            instructions="提取节点特征",
            input_data={"material": "岩石"},
            response_schema=RESPONSE_SCHEMA,
            schema_name="node_features",
            max_output_tokens=512,
        )

        self.assertEqual(payload["model"], "test-model")
        self.assertEqual(payload["instructions"], "提取节点特征")
        self.assertEqual(json.loads(payload["input"]), {"material": "岩石"})
        self.assertFalse(payload["store"])
        self.assertEqual(payload["max_output_tokens"], 512)
        self.assertEqual(
            payload["text"]["format"],
            {
                "type": "json_schema",
                "name": "node_features",
                "strict": True,
                "schema": RESPONSE_SCHEMA,
            },
        )

    def test_builds_chat_completions_compatible_payload(self):
        payload = build_request_payload(
            api_style=API_STYLE_CHAT_COMPLETIONS,
            model="compatible-model",
            instructions="Return JSON only",
            input_data="node graph",
            response_schema=RESPONSE_SCHEMA,
            schema_name="node_features",
            max_output_tokens=256,
            chat_token_parameter="max_tokens",
        )

        self.assertEqual(
            payload["messages"],
            [
                {"role": "system", "content": "Return JSON only"},
                {"role": "user", "content": "node graph"},
            ],
        )
        self.assertEqual(payload["max_tokens"], 256)
        self.assertEqual(
            payload["response_format"],
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "node_features",
                    "strict": True,
                    "schema": RESPONSE_SCHEMA,
                },
            },
        )

    def test_builds_unstructured_payloads_and_alternate_chat_token(self):
        responses_payload = build_request_payload(
            api_style=API_STYLE_RESPONSES,
            model=" test-model ",
            instructions=None,
            input_data="plain input",
        )
        self.assertEqual(
            responses_payload,
            {"model": "test-model", "input": "plain input", "store": False},
        )

        chat_payload = build_request_payload(
            api_style=API_STYLE_CHAT_COMPLETIONS,
            model="chat-model",
            instructions="",
            input_data={"node": "file1"},
            max_output_tokens=32,
            chat_token_parameter="max_completion_tokens",
        )
        self.assertEqual(chat_payload["max_completion_tokens"], 32)
        self.assertEqual(len(chat_payload["messages"]), 1)

    def test_rejects_unsupported_api_style_before_request(self):
        with self.assertRaises(AiProtocolError):
            build_request_payload(
                api_style="automatic",
                model="test-model",
                instructions="test",
                input_data="test",
            )

    def test_rejects_non_json_serializable_input(self):
        with self.assertRaises(AiProtocolError):
            build_request_payload(
                api_style=API_STYLE_RESPONSES,
                model="test-model",
                instructions="test",
                input_data={"value": float("nan")},
            )

    def test_rejects_invalid_request_fields(self):
        invalid_arguments = [
            {"model": ""},
            {"instructions": object()},
            {"response_schema": []},
            {"response_schema": {}, "schema_name": "bad name"},
            {"max_output_tokens": True},
            {
                "api_style": API_STYLE_CHAT_COMPLETIONS,
                "max_output_tokens": 1,
                "chat_token_parameter": "automatic",
            },
        ]
        for overrides in invalid_arguments:
            arguments = {
                "api_style": API_STYLE_RESPONSES,
                "model": "test-model",
                "instructions": "test",
                "input_data": "graph",
            }
            arguments.update(overrides)
            with self.subTest(overrides=overrides):
                with self.assertRaises(AiProtocolError):
                    build_request_payload(**arguments)


class AiResponseParsingTests(unittest.TestCase):
    def test_extracts_responses_output_text(self):
        response = {
            "status": "completed",
            "output": [
                {"type": "reasoning", "summary": []},
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": '{"summary":"颜色校正链"}',
                        }
                    ],
                },
            ],
        }

        text = parse_response_text(API_STYLE_RESPONSES, response)
        self.assertEqual(parse_json_output(text), {"summary": "颜色校正链"})

    def test_extracts_top_level_and_multiple_responses_text_parts(self):
        self.assertEqual(
            parse_response_text(
                API_STYLE_RESPONSES,
                {"status": "completed", "output_text": "top-level"},
            ),
            "top-level",
        )
        self.assertEqual(
            parse_response_text(
                API_STYLE_RESPONSES,
                {
                    "status": "completed",
                    "output": [
                        {
                            "type": "message",
                            "content": [
                                {"type": "output_text", "text": "part 1"},
                                {"type": "output_text", "text": " + part 2"},
                            ],
                        }
                    ],
                },
            ),
            "part 1 + part 2",
        )

    def test_extracts_chat_completion_content(self):
        response = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": '{"summary":"normal chain"}',
                    },
                }
            ]
        }

        text = parse_response_text(API_STYLE_CHAT_COMPLETIONS, response)
        self.assertEqual(parse_json_output(text), {"summary": "normal chain"})

    def test_extracts_chat_array_content(self):
        text = parse_response_text(
            API_STYLE_CHAT_COMPLETIONS,
            {
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "content": [
                                {"type": "text", "text": "part 1"},
                                {"type": "output_text", "text": " + part 2"},
                            ]
                        },
                    }
                ]
            },
        )
        self.assertEqual(text, "part 1 + part 2")

    def test_detects_responses_refusal(self):
        response = {
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "refusal", "refusal": "cannot process"}
                    ],
                }
            ],
        }

        with self.assertRaises(AiRefusalError):
            parse_response_text(API_STYLE_RESPONSES, response)

    def test_detects_provider_errors_and_chat_refusals(self):
        for api_style in (API_STYLE_RESPONSES, API_STYLE_CHAT_COMPLETIONS):
            with self.subTest(api_style=api_style):
                with self.assertRaises(AiProtocolError):
                    parse_response_text(
                        api_style,
                        {"error": {"message": "provider failed"}},
                    )

        refusal_payloads = [
            {
                "choices": [
                    {
                        "finish_reason": "content_filter",
                        "message": {"content": ""},
                    }
                ]
            },
            {
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "refusal": "cannot process",
                            "content": "",
                        },
                    }
                ]
            },
        ]
        for payload in refusal_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(AiRefusalError):
                    parse_response_text(API_STYLE_CHAT_COMPLETIONS, payload)

    def test_rejects_non_terminal_or_conflicting_outputs(self):
        for status in (None, "failed", "cancelled", "in_progress"):
            payload = {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": "unsafe"}
                        ],
                    }
                ]
            }
            if status is not None:
                payload["status"] = status
            with self.subTest(status=status):
                with self.assertRaises(AiProtocolError):
                    parse_response_text(API_STYLE_RESPONSES, payload)

        with self.assertRaises(AiRefusalError):
            parse_response_text(
                API_STYLE_RESPONSES,
                {
                    "status": "completed",
                    "output_text": "must not win",
                    "output": [
                        {
                            "type": "message",
                            "content": [
                                {"type": "refusal", "refusal": "no"}
                            ],
                        }
                    ],
                },
            )

        for finish_reason in (None, "tool_calls", "function_call", "unknown"):
            with self.subTest(finish_reason=finish_reason):
                with self.assertRaises(AiProtocolError):
                    parse_response_text(
                        API_STYLE_CHAT_COMPLETIONS,
                        {
                            "choices": [
                                {
                                    "finish_reason": finish_reason,
                                    "message": {"content": "unsafe"},
                                }
                            ]
                        },
                    )

    def test_detects_incomplete_responses_and_chat_outputs(self):
        with self.assertRaises(AiIncompleteResponseError):
            parse_response_text(
                API_STYLE_RESPONSES,
                {
                    "status": "incomplete",
                    "incomplete_details": {"reason": "max_output_tokens"},
                    "output": [],
                },
            )

        with self.assertRaises(AiIncompleteResponseError):
            parse_response_text(
                API_STYLE_CHAT_COMPLETIONS,
                {
                    "choices": [
                        {
                            "finish_reason": "length",
                            "message": {"content": "{}"},
                        }
                    ]
                },
            )

    def test_rejects_missing_text_and_invalid_json(self):
        with self.assertRaises(AiProtocolError):
            parse_response_text(
                API_STYLE_RESPONSES,
                {"status": "completed", "output": []},
            )

        with self.assertRaises(AiProtocolError):
            parse_json_output("```json\n{}\n```")

        for invalid_json in ('{"value": NaN}', '{"value": 1, "value": 2}'):
            with self.subTest(invalid_json=invalid_json):
                with self.assertRaises(AiProtocolError):
                    parse_json_output(invalid_json)

        with self.assertRaises(AiProtocolError):
            parse_json_output('{"value": 1e9999}')
        with self.assertRaises(AiProtocolError):
            parse_json_output('{"value": ' + ("9" * 5000) + "}")


class JsonSchemaSubsetTests(unittest.TestCase):
    def test_validates_nested_structured_output(self):
        schema = {
            "type": "object",
            "properties": {
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "weight": {"type": "number"},
                        },
                        "required": ["name", "weight"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["nodes"],
            "additionalProperties": False,
        }

        value = {"nodes": [{"name": "file1", "weight": 1.0}]}

        self.assertIs(validate_json_schema_subset(value, schema), value)

    def test_rejects_missing_wrong_type_and_extra_properties(self):
        invalid_values = [
            {},
            {"summary": 1},
            {"summary": "ok", "unexpected": True},
        ]
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(AiProtocolError):
                    validate_json_schema_subset(value, RESPONSE_SCHEMA)


if __name__ == "__main__":
    unittest.main()
