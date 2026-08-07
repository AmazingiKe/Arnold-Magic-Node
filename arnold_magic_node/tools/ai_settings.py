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


__all__ = [
    "AI_SETTINGS",
    "ensure_ai_settings",
    "load_ai_settings",
    "save_ai_settings",
]
