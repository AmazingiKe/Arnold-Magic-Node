"""用户设置初始化与重置工具。"""

import os

from ..core.paths import DEFAULT_SETTINGS_PATH
from ..core.storage import load_json, save_json
from .runtime import AMS_CONFIG, get_runtime_paths


def ensure_user_settings(user_root=None):
    """从只读内置配置按需创建主用户设置。"""

    paths = get_runtime_paths(user_root)
    config_path = os.path.join(paths.settings_path, AMS_CONFIG)
    if not os.path.exists(config_path) or os.path.getsize(config_path) == 0:
        return save_json(config_path, load_json(DEFAULT_SETTINGS_PATH))
    return None


def reset_settings(user_root=None):
    """删除当前主设置文件并重新生成默认配置。"""

    paths = get_runtime_paths(user_root)
    config_path = os.path.join(paths.settings_path, AMS_CONFIG)
    if os.path.exists(config_path):
        os.remove(config_path)
    return ensure_user_settings(user_root)


__all__ = ["ensure_user_settings", "reset_settings"]
