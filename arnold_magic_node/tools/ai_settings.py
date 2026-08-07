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
    from .ai_routing import AiRoutingConfig, migrate_ai_settings

    stored = load_json(settings_path)
    migrated = migrate_ai_settings(stored)
    if stored.get("schema_version", 1) == 3:
        models = migrated.get("models")
        if isinstance(models, list) and models:
            model_ids = [model.get("id") for model in models if isinstance(model, dict)]
            if model_ids:
                for field_name in ("fast_model_id", "complex_model_id"):
                    if migrated.get(field_name) not in model_ids:
                        migrated[field_name] = model_ids[0]
        return AiRoutingConfig.from_mapping(migrated).to_mapping()
    return migrated


def save_ai_settings(settings, user_root=None, paths=None):
    """校验并保存包含各模型明文 API Key 的用户 AI 设置。"""

    if not isinstance(settings, dict):
        raise TypeError("AI settings must be a dict")
    from .ai_routing import AiRoutingConfig

    normalized = AiRoutingConfig.from_mapping(settings).to_mapping()
    return save_json(_ai_settings_path(user_root, paths), normalized)


__all__ = [
    "AI_SETTINGS",
    "ensure_ai_settings",
    "load_ai_settings",
    "save_ai_settings",
]
