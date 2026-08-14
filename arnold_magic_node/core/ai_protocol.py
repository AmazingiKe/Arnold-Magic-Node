"""OpenAI Responses 与 Chat Completions 的纯 JSON 协议工具。"""

import json
import math


API_STYLE_RESPONSES = "responses"
API_STYLE_CHAT_COMPLETIONS = "chat_completions"
SUPPORTED_API_STYLES = frozenset((API_STYLE_RESPONSES, API_STYLE_CHAT_COMPLETIONS))
MAX_JSON_INTEGER_DIGITS = 4300


class AiError(Exception):
    """所有 AI 接入错误的公共基类。"""


class AiProtocolError(AiError):
    """AI 响应不符合预期的 JSON 协议。"""


class AiConfigurationError(AiError):
    """AI 配置无效或缺少凭据。"""


class AiRequestError(AiError):
    """调用 AI 服务失败（网络、认证、频率限制等）。"""


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
    raise AiProtocolError("本地 schema 校验不支持 type：{}".format(expected_type))


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
            _matches_json_type(value, expected_type) for expected_type in expected_types
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
        if not isinstance(required, list) or not all(
            isinstance(item, str) for item in required
        ):
            raise AiProtocolError("schema required 必须是字符串数组")
        if not isinstance(additional, (bool, dict)):
            raise AiProtocolError("schema additionalProperties 必须是布尔值或对象")

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
    "AiConfigurationError",
    "AiError",
    "AiProtocolError",
    "AiRequestError",
    "SUPPORTED_API_STYLES",
    "load_json_strict",
    "parse_json_output",
    "validate_json_schema_subset",
]
