"""用户设置初始化与重置工具。"""

import os

from ..core.settings import initialize_default_settings as initialize_settings_files
from .runtime import AMS_CONFIG, get_runtime_paths


def initialize_default_settings():
    """按需创建缺失的默认用户配置与预设。"""

    paths = get_runtime_paths()
    return initialize_settings_files(paths.user_data_root)


def reset_settings():
    """删除当前主设置文件并重新生成默认配置。"""

    paths = get_runtime_paths()
    config_path = os.path.join(paths.settings_path, AMS_CONFIG)
    if os.path.exists(config_path):
        os.remove(config_path)
    return initialize_default_settings()


__all__ = ["initialize_default_settings", "reset_settings"]
