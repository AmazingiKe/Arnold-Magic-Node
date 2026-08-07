"""OpenAI Responses 与 Chat Completions 的纯 JSON 协议工具。"""

import json
import math
import re


API_STYLE_RESPONSES = "responses"
API_STYLE_CHAT_COMPLETIONS = "chat_completions"
SUPPORTED_API_STYLES = frozenset(
    (API_STYLE_RESPONSES, API_STYLE_CHAT_COMPLETIONS)
)
SUPPORTED_CHAT_TOKEN_PARAMETERS = frozenset(
    ("max_tokens", "max_completion_tokens")
)
MAX_JSON_INTEGER_DIGITS = 4300


class AiError(Exception):
    """所有 AI 接入错误的公共基类。"""


class AiProtocolError(AiError):
    """请求或响应不符合预期的 AI JSON 协议。"""


class AiRefusalError(AiProtocolError):
    """模型明确拒绝了本次请求。"""


class AiIncompleteResponseError(AiProtocolError):
    """模型输出因长度或其他原因没有完整生成。"""


def _reject_json_constant(value):
    raise ValueError("unsupported JSON constant: {}".format(value))


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: {}".format(key))
        result[key] = value
    return result


def _parse_json_integer(value):
    digits = value.lstrip("-")
    if len(digits) > MAX_JSON_INTEGER_DIGITS:
        raise ValueError("JSON integer is too long")
    return int(value)


def _parse_json_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("JSON number is not finite")
    return result


def load_json_strict(text):
    """严格解析 JSON，拒绝 NaN、Infinity 和重复对象键。"""

    try:
        return json.loads(
            text,
            parse_constant=_reject_json_constant,
            parse_float=_parse_json_float,
            parse_int=_parse_json_integer,
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (TypeError, ValueError, RecursionError) as error:
        raise AiProtocolError("AI 响应不是有效的严格 JSON") from error


def _serialize_input(input_data):
    if isinstance(input_data, str):
        return input_data
    try:
        return json.dumps(
            input_data,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
    except (TypeError, ValueError, RecursionError) as error:
        raise AiProtocolError("AI 输入无法序列化为 JSON") from error


def _validate_common_request(api_style, model, instructions):
    if api_style not in SUPPORTED_API_STYLES:
        raise AiProtocolError("不支持的 API 风格：{}".format(api_style))
    if not isinstance(model, str) or not model.strip():
        raise AiProtocolError("AI 模型名称不能为空")
    if instructions is not None and not isinstance(instructions, str):
        raise AiProtocolError("AI instructions 必须是字符串")


def _validate_schema(response_schema, schema_name):
    if response_schema is None:
        return
    if not isinstance(response_schema, dict):
        raise AiProtocolError("response_schema 必须是 JSON 对象")
    if not isinstance(schema_name, str) or not re.match(
        r"^[A-Za-z0-9_-]{1,64}$", schema_name
    ):
        raise AiProtocolError(
            "schema_name 只能包含字母、数字、下划线和连字符"
        )


def _validate_max_output_tokens(max_output_tokens):
    if max_output_tokens is None:
        return
    if (
        isinstance(max_output_tokens, bool)
        or not isinstance(max_output_tokens, int)
        or max_output_tokens <= 0
    ):
        raise AiProtocolError("max_output_tokens 必须是正整数")


def build_request_payload(
    api_style,
    model,
    instructions,
    input_data,
    response_schema=None,
    schema_name="structured_output",
    max_output_tokens=None,
    chat_token_parameter="max_tokens",
):
    """构造 Responses 或 Chat Completions 的 REST 请求体。"""

    _validate_common_request(api_style, model, instructions)
    _validate_schema(response_schema, schema_name)
    _validate_max_output_tokens(max_output_tokens)
    input_text = _serialize_input(input_data)

    if api_style == API_STYLE_RESPONSES:
        payload = {
            "model": model.strip(),
            "input": input_text,
            "store": False,
        }
        if instructions:
            payload["instructions"] = instructions
        if max_output_tokens is not None:
            payload["max_output_tokens"] = max_output_tokens
        if response_schema is not None:
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": response_schema,
                }
            }
        return payload

    messages = []
    if instructions:
        messages.append({"role": "system", "content": instructions})
    messages.append({"role": "user", "content": input_text})
    payload = {"model": model.strip(), "messages": messages}

    if max_output_tokens is not None:
        if chat_token_parameter not in SUPPORTED_CHAT_TOKEN_PARAMETERS:
            raise AiProtocolError(
                "不支持的 Chat token 参数：{}".format(chat_token_parameter)
            )
        payload[chat_token_parameter] = max_output_tokens
    if response_schema is not None:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": response_schema,
            },
        }
    return payload


def _provider_error_message(payload):
    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, dict):
        return error.get("message") or error.get("code") or "AI 服务返回错误"
    if isinstance(error, str):
        return error
    return None


def _parse_responses_text(payload):
    provider_error = _provider_error_message(payload)
    if provider_error:
        raise AiProtocolError(str(provider_error))

    status = payload.get("status")
    if status == "incomplete":
        details = payload.get("incomplete_details") or {}
        reason = details.get("reason") if isinstance(details, dict) else None
        raise AiIncompleteResponseError(
            "Responses 输出不完整：{}".format(reason or "unknown")
        )
    if status != "completed":
        raise AiProtocolError(
            "Responses 状态不是 completed：{}".format(
                status or "missing"
            )
        )

    top_level_text = payload.get("output_text")
    output = payload.get("output")
    if output is None and isinstance(top_level_text, str) and top_level_text:
        return top_level_text
    if not isinstance(output, list):
        raise AiProtocolError("Responses 响应缺少 output 数组")

    text_parts = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content") or []
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "refusal":
                raise AiRefusalError(
                    str(part.get("refusal") or "模型拒绝了本次请求")
                )
            if part.get("type") == "output_text" and isinstance(
                part.get("text"), str
            ):
                text_parts.append(part["text"])

    if isinstance(top_level_text, str) and top_level_text:
        return top_level_text
    if not text_parts:
        raise AiProtocolError("Responses 响应中没有 output_text")
    return "".join(text_parts)


def _chat_content_text(content):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for part in content:
        if not isinstance(part, dict):
            continue
        if part.get("type") in ("text", "output_text") and isinstance(
            part.get("text"), str
        ):
            parts.append(part["text"])
    return "".join(parts)


def _parse_chat_completions_text(payload):
    provider_error = _provider_error_message(payload)
    if provider_error:
        raise AiProtocolError(str(provider_error))

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AiProtocolError("Chat Completions 响应缺少 choices")

    choice = choices[0]
    if not isinstance(choice, dict):
        raise AiProtocolError("Chat Completions choice 格式错误")
    finish_reason = choice.get("finish_reason")
    if finish_reason == "length":
        raise AiIncompleteResponseError("Chat Completions 输出达到长度上限")
    if finish_reason == "content_filter":
        raise AiRefusalError("Chat Completions 输出被内容过滤器阻止")
    if finish_reason != "stop":
        raise AiProtocolError(
            "Chat Completions 未返回最终文本：{}".format(
                finish_reason or "missing"
            )
        )

    message = choice.get("message")
    if not isinstance(message, dict):
        raise AiProtocolError("Chat Completions 响应缺少 message")
    refusal = message.get("refusal")
    if refusal:
        raise AiRefusalError(str(refusal))
    text = _chat_content_text(message.get("content"))
    if not text:
        raise AiProtocolError("Chat Completions 响应中没有文本内容")
    return text


def parse_response_text(api_style, payload):
    """从 REST 响应对象中提取模型文本。"""

    if api_style not in SUPPORTED_API_STYLES:
        raise AiProtocolError("不支持的 API 风格：{}".format(api_style))
    if not isinstance(payload, dict):
        raise AiProtocolError("AI 响应根节点必须是 JSON 对象")
    if api_style == API_STYLE_RESPONSES:
        return _parse_responses_text(payload)
    return _parse_chat_completions_text(payload)


def parse_json_output(text):
    """把模型文本严格解析成 Python JSON 数据。"""

    if not isinstance(text, str) or not text.strip():
        raise AiProtocolError("AI 响应文本为空")
    return load_json_strict(text)


def _schema_error(path, message):
    raise AiProtocolError("结构化输出不符合 schema（{}）：{}".format(path, message))


def _matches_json_type(value, expected_type):
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and (not isinstance(value, float) or math.isfinite(value))
        )
    raise AiProtocolError(
        "本地 schema 校验不支持 type：{}".format(expected_type)
    )


def _validate_schema_value(value, schema, path):
    if not isinstance(schema, dict):
        raise AiProtocolError("本地 schema 节点必须是 JSON 对象")

    expected_types = schema.get("type")
    if expected_types is not None:
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if (
            not isinstance(expected_types, list)
            or not expected_types
            or not all(isinstance(item, str) for item in expected_types)
        ):
            raise AiProtocolError("schema type 必须是字符串或非空字符串数组")
        if not any(
            _matches_json_type(value, expected_type)
            for expected_type in expected_types
        ):
            _schema_error(path, "类型不匹配")

    if "enum" in schema:
        enum_values = schema["enum"]
        if not isinstance(enum_values, list):
            raise AiProtocolError("schema enum 必须是数组")
        if value not in enum_values:
            _schema_error(path, "值不在 enum 中")
    if "const" in schema and value != schema["const"]:
        _schema_error(path, "值不符合 const")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        additional = schema.get("additionalProperties", True)
        if not isinstance(properties, dict):
            raise AiProtocolError("schema properties 必须是 JSON 对象")
        if (
            not isinstance(required, list)
            or not all(isinstance(item, str) for item in required)
        ):
            raise AiProtocolError("schema required 必须是字符串数组")
        if not isinstance(additional, (bool, dict)):
            raise AiProtocolError(
                "schema additionalProperties 必须是布尔值或对象"
            )

        for property_name in required:
            if property_name not in value:
                _schema_error(path, "缺少必填字段 {}".format(property_name))
        for property_name, property_value in value.items():
            property_path = path + "[" + repr(property_name) + "]"
            if property_name in properties:
                _validate_schema_value(
                    property_value,
                    properties[property_name],
                    property_path,
                )
            elif additional is False:
                _schema_error(property_path, "不允许额外字段")
            elif isinstance(additional, dict):
                _validate_schema_value(
                    property_value,
                    additional,
                    property_path,
                )

    if isinstance(value, list):
        items = schema.get("items")
        if items is not None:
            if not isinstance(items, dict):
                raise AiProtocolError("schema items 必须是 JSON 对象")
            for index, item in enumerate(value):
                _validate_schema_value(
                    item,
                    items,
                    "{}[{}]".format(path, index),
                )


def validate_json_schema_subset(value, schema):
    """按常用 JSON Schema 结构关键字做本地安全校验。

    该校验覆盖 ``type``、``enum``、``const``、``properties``、
    ``required``、``additionalProperties`` 与 ``items``。它是对服务端
    Structured Outputs 的本地兜底，不替代节点执行层的领域白名单。
    """

    _validate_schema_value(value, schema, "$")
    return value


__all__ = [
    "API_STYLE_CHAT_COMPLETIONS",
    "API_STYLE_RESPONSES",
    "AiError",
    "AiIncompleteResponseError",
    "AiProtocolError",
    "AiRefusalError",
    "SUPPORTED_API_STYLES",
    "build_request_payload",
    "load_json_strict",
    "parse_json_output",
    "parse_response_text",
    "validate_json_schema_subset",
]
