"""有序独立模型配置与 fast/complex 固定流式路由。"""

import copy
import ipaddress
import json
import math
import re
from dataclasses import dataclass, field
from urllib.parse import urlsplit

import openai

from arnold_magic_node.core.ai_protocol import (
    API_STYLE_CHAT_COMPLETIONS,
    API_STYLE_RESPONSES,
    SUPPORTED_API_STYLES,
    AiConfigurationError,
    AiRequestError,
    parse_json_output,
    validate_json_schema_subset,
)


AI_MODE_FAST = "fast"
AI_MODE_COMPLEX = "complex"
MAX_MODELS = 64
MAX_MODEL_NAME_LENGTH = 256
MAX_MODEL_ID_LENGTH = 128
MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
MAX_API_KEY_LENGTH = 8192
MAX_BODY_LIMIT = 10 * 1024 * 1024
CHAT_TOKEN_PARAMETERS = ("max_tokens", "max_completion_tokens")


def normalize_api_key(value):
    """返回去除首尾空白后的安全 API Key，空值返回 ``None``。"""

    if value is None:
        return None
    if not isinstance(value, str):
        raise AiConfigurationError("API Key 必须是字符串")
    key = value.strip()
    if not key:
        return None
    if len(key) > MAX_API_KEY_LENGTH or any(
        ord(character) < 33 or ord(character) > 126 for character in key
    ):
        raise AiConfigurationError("API Key 格式无效")
    return key


def _is_loopback_host(hostname):
    if not hostname:
        return False
    if hostname.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


def normalize_base_url(base_url):
    """校验并标准化 AI 服务根 URL。"""

    if not isinstance(base_url, str) or not base_url:
        raise AiConfigurationError("base_url 不能为空")
    if base_url != base_url.strip() or "\\" in base_url:
        raise AiConfigurationError("base_url 格式无效")
    if any(
        character.isspace() or ord(character) < 32 or ord(character) == 127
        for character in base_url
    ):
        raise AiConfigurationError("base_url 包含空白或控制字符")

    try:
        parts = urlsplit(base_url)
        port = parts.port
    except ValueError as error:
        raise AiConfigurationError("base_url 格式无效") from error
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise AiConfigurationError("base_url 必须是有效的 HTTP(S) URL")
    if parts.username is not None or parts.password is not None:
        raise AiConfigurationError("base_url 不得包含用户名或密码")
    if parts.query or parts.fragment:
        raise AiConfigurationError("base_url 不得包含 query 或 fragment")
    if port is not None and port < 1:
        raise AiConfigurationError("base_url 端口无效")
    if parts.scheme == "http" and not _is_loopback_host(parts.hostname):
        raise AiConfigurationError("远程 AI 接口必须使用 HTTPS")
    return base_url.rstrip("/"), parts


def _validate_number(value, name, minimum, maximum):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or (isinstance(value, float) and not math.isfinite(value))
        or value < minimum
        or value > maximum
    ):
        raise AiConfigurationError(
            "{} 必须在 {} 到 {} 之间".format(name, minimum, maximum)
        )


def _validate_integer(value, name, minimum, maximum):
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < minimum
        or value > maximum
    ):
        raise AiConfigurationError(
            "{} 必须是 {} 到 {} 之间的整数".format(name, minimum, maximum)
        )


def migrate_ai_settings(values):
    """校验当前 AI 设置 schema；旧版 schema 不再自动迁移。"""

    if not isinstance(values, dict):
        raise AiConfigurationError("AI 设置根节点必须是 JSON 对象")
    version = values.get("schema_version", 1)
    if type(version) is not int:
        raise AiConfigurationError("不支持的 AI 设置 schema_version")
    if version == 3:
        return copy.deepcopy(values)
    raise AiConfigurationError("不支持的 AI 设置 schema_version")


@dataclass(frozen=True)
class AiModelConfig:
    """一个模型的完整连接配置；API Key 只允许持久化与传输使用。"""

    id: str
    model: str
    base_url: str
    api_style: str
    api_key: str = field(repr=False)
    timeout_seconds: float
    max_output_tokens: int
    max_request_bytes: int
    max_response_bytes: int
    chat_token_parameter: str

    @classmethod
    def from_mapping(cls, values):
        if not isinstance(values, dict):
            raise AiConfigurationError("模型配置必须是 JSON 对象")
        fields = {
            "id",
            "model",
            "base_url",
            "api_style",
            "api_key",
            "timeout_seconds",
            "max_output_tokens",
            "max_request_bytes",
            "max_response_bytes",
            "chat_token_parameter",
        }
        unknown = [key for key in values if key not in fields]
        if unknown:
            raise AiConfigurationError(
                "模型配置包含未知字段：{}".format(
                    ", ".join(repr(key) for key in unknown[:5])
                )
            )
        missing = [key for key in fields if key not in values]
        if missing:
            raise AiConfigurationError("模型配置字段不完整")

        model_id = cls._normalize_id(values["id"])
        model = cls._normalize_model_name(values["model"])
        api_style = values["api_style"]
        if api_style not in SUPPORTED_API_STYLES:
            raise AiConfigurationError("不支持的 API 风格：{}".format(api_style))
        base_url = values["base_url"]
        if base_url:
            normalized_url, url_parts = normalize_base_url(base_url)
        else:
            normalized_url, url_parts = "", None
        api_key = normalize_api_key(values["api_key"]) or ""
        if api_key and url_parts is not None and url_parts.scheme != "https":
            raise AiConfigurationError("带 API Key 的模型接口必须使用 HTTPS")
        chat_token_parameter = values["chat_token_parameter"]
        if chat_token_parameter not in CHAT_TOKEN_PARAMETERS:
            raise AiConfigurationError("Chat token 参数不受支持")
        _validate_number(values["timeout_seconds"], "timeout_seconds", 1, 300)
        _validate_integer(
            values["max_output_tokens"], "max_output_tokens", 1, 1000000
        )
        _validate_integer(
            values["max_request_bytes"], "max_request_bytes", 1, MAX_BODY_LIMIT
        )
        _validate_integer(
            values["max_response_bytes"], "max_response_bytes", 1, MAX_BODY_LIMIT
        )

        return cls(
            id=model_id,
            model=model,
            base_url=normalized_url,
            api_style=api_style,
            api_key=api_key,
            timeout_seconds=values["timeout_seconds"],
            max_output_tokens=values["max_output_tokens"],
            max_request_bytes=values["max_request_bytes"],
            max_response_bytes=values["max_response_bytes"],
            chat_token_parameter=chat_token_parameter,
        )

    @staticmethod
    def _normalize_id(model_id):
        if (
            not isinstance(model_id, str)
            or not model_id
            or len(model_id) > MAX_MODEL_ID_LENGTH
            or not MODEL_ID_PATTERN.match(model_id)
        ):
            raise AiConfigurationError("模型配置 ID 格式无效")
        return model_id

    @staticmethod
    def _normalize_model_name(model):
        if not isinstance(model, str):
            raise AiConfigurationError("AI 模型名称必须是字符串")
        normalized = model.strip()
        if not normalized:
            return ""
        if len(normalized) > MAX_MODEL_NAME_LENGTH:
            raise AiConfigurationError("AI 模型名称过长")
        if any(
            character.isspace() or ord(character) < 32 or ord(character) == 127
            for character in normalized
        ):
            raise AiConfigurationError("AI 模型名称格式无效")
        return normalized

    def to_mapping(self):
        return {
            "id": self.id,
            "model": self.model,
            "base_url": self.base_url,
            "api_style": self.api_style,
            "api_key": self.api_key,
            "timeout_seconds": self.timeout_seconds,
            "max_output_tokens": self.max_output_tokens,
            "max_request_bytes": self.max_request_bytes,
            "max_response_bytes": self.max_response_bytes,
            "chat_token_parameter": self.chat_token_parameter,
        }


@dataclass(frozen=True)
class AiRoutingConfig:
    """schema v3：有序模型池与 fast/complex 两个固定引用。"""

    schema_version: int
    models: tuple
    fast_model_id: str
    complex_model_id: str

    @classmethod
    def from_mapping(cls, values):
        migrated = migrate_ai_settings(values)
        allowed = {
            "schema_version",
            "models",
            "fast_model_id",
            "complex_model_id",
        }
        unknown = [key for key in migrated if key not in allowed]
        if unknown:
            raise AiConfigurationError(
                "AI 设置包含未知字段：{}".format(
                    ", ".join(repr(key) for key in unknown[:5])
                )
            )
        if set(migrated) != allowed:
            raise AiConfigurationError("AI 设置字段不完整")
        if migrated["schema_version"] != 3:
            raise AiConfigurationError("不支持的 AI 设置 schema_version")
        raw_models = migrated["models"]
        if not isinstance(raw_models, list) or not raw_models:
            raise AiConfigurationError("模型列表不能为空")
        if len(raw_models) > MAX_MODELS:
            raise AiConfigurationError("模型列表最多允许 {} 项".format(MAX_MODELS))
        models = tuple(AiModelConfig.from_mapping(item) for item in raw_models)
        ids = [profile.id for profile in models]
        if len(set(ids)) != len(ids):
            raise AiConfigurationError("模型配置 ID 不能重复")
        for field_name in ("fast_model_id", "complex_model_id"):
            value = migrated[field_name]
            if not isinstance(value, str) or value not in ids:
                raise AiConfigurationError("{} 必须引用现有模型".format(field_name))
        return cls(
            schema_version=3,
            models=models,
            fast_model_id=migrated["fast_model_id"],
            complex_model_id=migrated["complex_model_id"],
        )

    def model_by_id(self, model_id):
        for profile in self.models:
            if profile.id == model_id:
                return profile
        raise AiConfigurationError("模型配置不存在")

    def model_for_mode(self, mode):
        if mode == AI_MODE_FAST:
            return self.model_by_id(self.fast_model_id)
        if mode == AI_MODE_COMPLEX:
            return self.model_by_id(self.complex_model_id)
        raise AiConfigurationError("AI 模式无效")

    def to_mapping(self):
        return {
            "schema_version": 3,
            "models": [profile.to_mapping() for profile in self.models],
            "fast_model_id": self.fast_model_id,
            "complex_model_id": self.complex_model_id,
        }


def _create_sdk_client(profile, timeout_seconds=None):
    """按模型配置创建 OpenAI SDK 客户端；本地 HTTP 接口使用占位 Key。"""

    base_url, url_parts = normalize_base_url(profile.base_url)
    timeout = profile.timeout_seconds if timeout_seconds is None else timeout_seconds
    if not profile.model:
        raise AiConfigurationError("AI 模型名称不能为空")
    api_key = profile.api_key
    if url_parts.scheme == "http":
        api_key = api_key or "sk-local"
    elif not api_key:
        raise AiConfigurationError("当前模型未配置 API Key")
    return openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        max_retries=0,
    )


def _map_sdk_error(error):
    """把 OpenAI SDK 异常映射为插件的 AiRequestError。"""

    if isinstance(error, openai.AuthenticationError):
        message = "认证失败（API Key 无效或无权限）"
    elif isinstance(error, openai.RateLimitError):
        message = "请求频率或额度受限"
    elif isinstance(error, openai.APIConnectionError):
        message = "无法连接 AI 接口"
    elif isinstance(error, openai.APITimeoutError):
        message = "AI 请求超时"
    elif isinstance(error, openai.BadRequestError):
        message = "请求参数被拒绝：{}".format(error)
    else:
        message = "AI 请求失败：{}".format(error)
    return AiRequestError(message)


class AiService(object):
    """绑定 fast 或 complex 的唯一模型，并向 tools 暴露流式输入接口。"""

    def __init__(self, config, client_factory=None, mode=AI_MODE_FAST):
        if not isinstance(config, AiRoutingConfig):
            config = AiRoutingConfig.from_mapping(config)
        self.config = config
        self.mode = AI_MODE_FAST if mode is None else mode
        self.profile = config.model_for_mode(self.mode)
        self.client_factory = client_factory or _create_sdk_client

    def _client(self):
        return self.client_factory(self.profile)

    @staticmethod
    def _serialize_input(input_data):
        if isinstance(input_data, str):
            return input_data
        try:
            return json.dumps(input_data, ensure_ascii=False, allow_nan=False)
        except (TypeError, ValueError, RecursionError) as error:
            raise AiConfigurationError("AI 输入无法序列化为 JSON") from error

    def stream(
        self,
        input_data,
        instructions=None,
        response_schema=None,
        schema_name="structured_output",
    ):
        """以 SSE 增量形式返回模型可见文本。"""

        profile = self.profile
        client = self._client()
        try:
            if profile.api_style == API_STYLE_RESPONSES:
                params = {
                    "model": profile.model,
                    "input": self._serialize_input(input_data),
                    "store": False,
                    "stream": True,
                }
                if instructions:
                    params["instructions"] = instructions
                if profile.max_output_tokens:
                    params["max_output_tokens"] = profile.max_output_tokens
                if response_schema is not None:
                    params["text"] = {
                        "format": {
                            "type": "json_schema",
                            "name": schema_name,
                            "strict": True,
                            "schema": response_schema,
                        }
                    }
                with client.responses.create(**params) as stream:
                    for event in stream:
                        if event.type == "response.output_text.delta":
                            yield event.delta
            else:
                messages = []
                if instructions:
                    messages.append({"role": "system", "content": instructions})
                messages.append(
                    {"role": "user", "content": self._serialize_input(input_data)}
                )
                params = {
                    "model": profile.model,
                    "messages": messages,
                    "stream": True,
                }
                if profile.max_output_tokens:
                    params[profile.chat_token_parameter] = profile.max_output_tokens
                if response_schema is not None:
                    params["response_format"] = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": schema_name,
                            "strict": True,
                            "schema": response_schema,
                        },
                    }
                with client.chat.completions.create(**params) as stream:
                    for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta:
                            content = chunk.choices[0].delta.content
                            if content:
                                yield content
        except openai.OpenAIError as error:
            raise _map_sdk_error(error) from error

    def ask(
        self,
        input_data,
        instructions=None,
        response_schema=None,
        schema_name="structured_output",
    ):
        return "".join(
            self.stream(
                input_data,
                instructions=instructions,
                response_schema=response_schema,
                schema_name=schema_name,
            )
        )

    def generate_json(
        self,
        input_data,
        response_schema,
        instructions=None,
        schema_name="structured_output",
    ):
        text = self.ask(
            input_data,
            instructions=instructions,
            response_schema=response_schema,
            schema_name=schema_name,
        )
        data = parse_json_output(text)
        validate_json_schema_subset(data, response_schema)
        return data


def create_ai_service(
    settings=None,
    user_root=None,
    paths=None,
    mode=AI_MODE_FAST,
    client_factory=None,
):
    """创建固定 fast/complex 模型的服务；调用端不选择具体模型。"""

    if settings is None:
        from .ai_settings import load_ai_settings

        settings = load_ai_settings(user_root=user_root, paths=paths)
    return AiService(
        AiRoutingConfig.from_mapping(settings),
        client_factory=client_factory,
        mode=mode,
    )


def test_ai_model(profile, client_factory=None):
    """只探测一个完整模型配置；发送 ``"1"`` 且绝不切换模型。"""

    if not isinstance(profile, AiModelConfig):
        profile = AiModelConfig.from_mapping(profile)
    client = (client_factory or _create_sdk_client)(
        profile,
        timeout_seconds=min(profile.timeout_seconds, 20),
    )
    try:
        if profile.api_style == API_STYLE_RESPONSES:
            client.responses.create(
                model=profile.model,
                input="1",
                max_output_tokens=32,
            )
        else:
            client.chat.completions.create(
                model=profile.model,
                messages=[{"role": "user", "content": "1"}],
                **{profile.chat_token_parameter: 32},
            )
    except openai.OpenAIError as error:
        raise _map_sdk_error(error) from error
    return True


__all__ = [
    "AI_MODE_COMPLEX",
    "AI_MODE_FAST",
    "AiModelConfig",
    "AiRoutingConfig",
    "AiService",
    "MAX_MODELS",
    "create_ai_service",
    "migrate_ai_settings",
    "normalize_base_url",
    "test_ai_model",
]
