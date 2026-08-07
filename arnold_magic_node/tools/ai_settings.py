"""独立 AI 设置文件的按需初始化与读写。"""

from pathlib import Path

from ..core.paths import DEFAULT_AI_SETTINGS_PATH
from ..core.storage import load_json, save_json
from .runtime import get_runtime_paths


AI_SETTINGS = "AI_Settings.json"


def _ai_settings_path(user_root=None, paths=None):
    if paths is None:
        paths = get_runtime_paths(user_root)
    return Path(paths.settings_path) / AI_SETTINGS


def ensure_ai_settings(user_root=None, paths=None):
    """首次实际使用 AI 时复制只读默认设置。"""

    settings_path = _ai_settings_path(user_root, paths)
    if not settings_path.exists() or settings_path.stat().st_size == 0:
        return save_json(settings_path, load_json(DEFAULT_AI_SETTINGS_PATH))
    return settings_path


def load_ai_settings(user_root=None, paths=None):
    """读取用户 AI 设置；缺失时按需创建。"""

    settings_path = ensure_ai_settings(user_root, paths)
    return load_json(settings_path)


def save_ai_settings(settings, user_root=None, paths=None):
    """保存不含密钥本体的用户 AI 设置。"""

    if not isinstance(settings, dict):
        raise TypeError("AI settings must be a dict")
    if "api_key" in settings:
        raise ValueError("API key must not be stored in AI settings")
    from .ai_client import AiClientConfig

    AiClientConfig.from_mapping(settings).validate()
    return save_json(_ai_settings_path(user_root, paths), settings)


def save_ai_settings_with_session_key(
    settings,
    previous_base_url=None,
    api_key=None,
    user_root=None,
    paths=None,
):
    """原子保存公开设置，并按 origin 更新可选的进程内密钥。"""

    from .ai_client import (
        AiClientConfig,
        AiConfigurationError,
        normalize_api_key,
    )
    from .ai_credentials import (
        api_origin,
        clear_session_api_key,
        set_session_api_key,
    )

    config = AiClientConfig.from_mapping(settings).validate()
    new_origin = api_origin(config.base_url)
    previous_origin = None
    if previous_base_url:
        try:
            previous_origin = api_origin(previous_base_url)
        except AiConfigurationError:
            # 旧版本可能写入过现行规则不再接受的 URL。它不可能
            # 对应当前凭据存储中的有效 origin，不应阻止用户修复配置。
            pass
    normalized_key = normalize_api_key(api_key)
    if normalized_key is not None and not new_origin.startswith("https://"):
        raise AiConfigurationError("本地 HTTP 接口不会接收会话 API Key")

    settings_path = save_ai_settings(
        settings,
        user_root=user_root,
        paths=paths,
    )
    if previous_origin and previous_origin != new_origin:
        clear_session_api_key(previous_base_url)
    if normalized_key is not None:
        set_session_api_key(config.base_url, normalized_key)
    return settings_path


__all__ = [
    "AI_SETTINGS",
    "ensure_ai_settings",
    "load_ai_settings",
    "save_ai_settings",
    "save_ai_settings_with_session_key",
]
