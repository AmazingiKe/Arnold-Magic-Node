"""有序独立模型配置与 fast/complex 固定流式路由。"""

import copy
import re
from dataclasses import dataclass, field

from arnold_magic_node.core.ai_protocol import parse_json_output, validate_json_schema_subset
from .ai_client import (
    DEFAULT_API_KEY_ENV,
    AiClientConfig,
    AiConfigurationError,
    OpenAICompatibleClient,
    UrllibTransport,
    normalize_api_key,
    normalize_base_url,
)


AI_MODE_FAST = "fast"
AI_MODE_COMPLEX = "complex"
SUPPORTED_AI_MODES = (AI_MODE_FAST, AI_MODE_COMPLEX)
MAX_MODELS = 64
MAX_MODEL_NAME_LENGTH = 256
MAX_MODEL_ID_LENGTH = 128
MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _legacy_profile(model_id, model, legacy):
    return {
        "id": model_id,
        "model": model,
        "base_url": legacy.base_url,
        "api_style": legacy.api_style,
        "api_key": "",
        "timeout_seconds": legacy.timeout_seconds,
        "max_output_tokens": legacy.max_output_tokens,
        "max_request_bytes": legacy.max_request_bytes,
        "max_response_bytes": legacy.max_response_bytes,
        "chat_token_parameter": legacy.chat_token_parameter,
    }


def _migrate_v1(values):
    legacy = AiClientConfig.from_mapping(values)
    model_id = "model_001"
    return {
        "schema_version": 3,
        "models": [_legacy_profile(model_id, legacy.model, legacy)],
        "fast_model_id": model_id,
        "complex_model_id": model_id,
    }


def _migrate_v2(values):
    defaults = AiClientConfig()
    queues = values.get("model_queues")
    if not isinstance(queues, dict):
        raise AiConfigurationError("旧版 model_queues 必须是 JSON 对象")

    ordered_names = []
    mode_first_names = {}
    for mode in SUPPORTED_AI_MODES:
        queue = queues.get(mode)
        models = queue.get("models") if isinstance(queue, dict) else None
        if not isinstance(models, list) or not models:
            raise AiConfigurationError("旧版快速和复杂模型队列不能为空")
        if any(not isinstance(model, str) for model in models):
            raise AiConfigurationError("旧版模型名称必须是字符串")
        mode_first_names[mode] = models[0]
        for model in models:
            if model not in ordered_names:
                ordered_names.append(model)

    legacy = AiClientConfig(
        schema_version=1,
        api_style=values.get("api_style", defaults.api_style),
        base_url=values.get("base_url", defaults.base_url),
        model=ordered_names[0],
        api_key_env=values.get("api_key_env", DEFAULT_API_KEY_ENV),
        timeout_seconds=values.get("timeout_seconds", defaults.timeout_seconds),
        max_output_tokens=values.get("max_output_tokens", defaults.max_output_tokens),
        max_request_bytes=values.get("max_request_bytes", defaults.max_request_bytes),
        max_response_bytes=values.get(
            "max_response_bytes", defaults.max_response_bytes
        ),
        chat_token_parameter=values.get(
            "chat_token_parameter", defaults.chat_token_parameter
        ),
    )
    profiles = []
    ids_by_name = {}
    for index, model in enumerate(ordered_names, 1):
        model_id = "model_{:03d}".format(index)
        ids_by_name[model] = model_id
        profiles.append(_legacy_profile(model_id, model, legacy))
    return {
        "schema_version": 3,
        "models": profiles,
        "fast_model_id": ids_by_name[mode_first_names[AI_MODE_FAST]],
        "complex_model_id": ids_by_name[mode_first_names[AI_MODE_COMPLEX]],
    }


def migrate_ai_settings(values):
    """把 v1/v2 设置迁移为 v3 映射；迁移本身不写回磁盘。"""

    if not isinstance(values, dict):
        raise AiConfigurationError("AI 设置根节点必须是 JSON 对象")
    version = values.get("schema_version", 1)
    if type(version) is not int:
        raise AiConfigurationError("不支持的 AI 设置 schema_version")
    if version == 3:
        return copy.deepcopy(values)
    if version == 2:
        return _migrate_v2(values)
    if version == 1:
        return _migrate_v1(values)
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
        normalized_url, url_parts = normalize_base_url(values["base_url"])
        api_key = normalize_api_key(values["api_key"]) or ""
        if api_key and url_parts.scheme != "https":
            raise AiConfigurationError("带 API Key 的模型接口必须使用 HTTPS")
        client_config = AiClientConfig(
            schema_version=1,
            api_style=values["api_style"],
            base_url=normalized_url,
            model=model,
            api_key_env=DEFAULT_API_KEY_ENV,
            timeout_seconds=values["timeout_seconds"],
            max_output_tokens=values["max_output_tokens"],
            max_request_bytes=values["max_request_bytes"],
            max_response_bytes=values["max_response_bytes"],
            chat_token_parameter=values["chat_token_parameter"],
        ).validate()
        return cls(
            id=model_id,
            model=client_config.model,
            base_url=normalized_url,
            api_style=client_config.api_style,
            api_key=api_key,
            timeout_seconds=client_config.timeout_seconds,
            max_output_tokens=client_config.max_output_tokens,
            max_request_bytes=client_config.max_request_bytes,
            max_response_bytes=client_config.max_response_bytes,
            chat_token_parameter=client_config.chat_token_parameter,
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
            raise AiConfigurationError("AI 模型名称不能为空")
        if len(normalized) > MAX_MODEL_NAME_LENGTH:
            raise AiConfigurationError("AI 模型名称过长")
        if any(
            character.isspace() or ord(character) < 32 or ord(character) == 127
            for character in normalized
        ):
            raise AiConfigurationError("AI 模型名称格式无效")
        return normalized

    def client_config(self, timeout_seconds=None, max_output_tokens=None):
        return AiClientConfig(
            schema_version=1,
            api_style=self.api_style,
            base_url=self.base_url,
            model=self.model,
            api_key_env=DEFAULT_API_KEY_ENV,
            timeout_seconds=(
                self.timeout_seconds if timeout_seconds is None else timeout_seconds
            ),
            max_output_tokens=(
                self.max_output_tokens
                if max_output_tokens is None
                else max_output_tokens
            ),
            max_request_bytes=self.max_request_bytes,
            max_response_bytes=self.max_response_bytes,
            chat_token_parameter=self.chat_token_parameter,
        ).validate()

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


class AiService(object):
    """绑定 fast 或 complex 的唯一模型，并向 tools 暴露流式输入接口。"""

    def __init__(
        self,
        config,
        client_factory=None,
        mode=AI_MODE_FAST,
        transport=None,
        environ=None,
    ):
        if not isinstance(config, AiRoutingConfig):
            config = AiRoutingConfig.from_mapping(config)
        self.config = config
        self.mode = AI_MODE_FAST if mode is None else mode
        self.profile = config.model_for_mode(self.mode)
        self.environ = environ
        self.transport = (
            transport or UrllibTransport() if client_factory is None else transport
        )
        self.client_factory = client_factory or self._create_client

    def _create_client(self, profile):
        return OpenAICompatibleClient(
            config=profile.client_config(),
            api_key=profile.api_key,
            transport=self.transport,
            environ=self.environ,
        )

    def stream(
        self,
        input_data,
        instructions=None,
        response_schema=None,
        schema_name="structured_output",
    ):
        client = self.client_factory(self.profile)
        for delta in client.stream_text(
            instructions,
            input_data,
            response_schema=response_schema,
            schema_name=schema_name,
        ):
            yield delta

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
    transport=None,
    environ=None,
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
        transport=transport,
        environ=environ,
    )


def test_ai_model(profile, transport=None, environ=None):
    """只探测一个完整模型配置；发送 ``"1"`` 且绝不切换模型。"""

    if not isinstance(profile, AiModelConfig):
        profile = AiModelConfig.from_mapping(profile)
    client = OpenAICompatibleClient(
        config=profile.client_config(
            timeout_seconds=min(profile.timeout_seconds, 20),
            max_output_tokens=min(profile.max_output_tokens, 32),
        ),
        api_key=profile.api_key,
        transport=transport,
        environ=environ,
    )
    for _ in client.stream_text(None, "1"):
        pass
    return True


__all__ = [
    "AI_MODE_COMPLEX",
    "AI_MODE_FAST",
    "AiModelConfig",
    "AiRoutingConfig",
    "AiService",
    "MAX_MODELS",
    "SUPPORTED_AI_MODES",
    "create_ai_service",
    "migrate_ai_settings",
    "test_ai_model",
]
