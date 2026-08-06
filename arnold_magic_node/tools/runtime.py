"""运行时配置、路径和语言工具。

本模块是界面层访问用户配置的唯一入口；JSON 与路径计算仍由
``core`` 提供，Maya 用户目录只在实际请求运行时路径时查询。
"""

import os
from dataclasses import dataclass

from ..core.paths import (
    ICONS_ROOT,
    LANGUAGES_ROOT,
    user_aov_cache_path,
    user_preset_dir,
    user_settings_dir,
)
from ..core.storage import ensure_directory, load_json, save_json
from ..maya.environment import MayaEnvironmentAdapter, get_user_data_root


SOFTWARE_STATE = "Release"
SOFTWARE_VERSION = "1.2.02"

PLUGIN_HOME_URL = (
    "https://flowus.cn/amazingike/share/"
    "93cfb135-4ab3-4536-8a5b-9b3e53042b51?code=LZVF69"
)
PLUGIN_FEEDBACK_URL = (
    "https://flowus.cn/form/"
    "7b125d97-3971-40ee-ac8b-c338e4a91909?code=LZVF69"
)
PLUGIN_UPDATE_DOWNLOAD_URL = (
    "https://flowus.cn/amazingike/share/"
    "84422156-5158-4b73-9a5f-c5cadbb6625a?code=LZVF69"
)
PLUGIN_HELP_DOCUMENT_URL = (
    "https://flowus.cn/amazingike/share/"
    "6e8b16c6-f8b1-4f04-bad7-24ff003224dc?code=LZVF69"
)

AMS_CONFIG = "Arnold_Magic_Settings.json"

SMALL_FONT_SIZE = 10
NORMAL_FONT_SIZE = 14
MEDIUM_FONT_SIZE = 16
LARGE_FONT_SIZE = 18
EXTRA_LARGE_FONT_SIZE = 24

MAYA_SHIFT_MODIFIER = 1
MAYA_ALT_MODIFIER = 8


@dataclass(frozen=True)
class RuntimePaths:
    """运行时读写位置的不可变快照。"""

    user_data_root: str
    settings_path: str
    render_preset_path: str
    aov_cache_path: str
    icon_path: str
    languages_path: str


def get_runtime_paths(user_root=None):
    """解析当前 Maya 用户目录下的插件运行时路径。"""

    if user_root is None:
        user_root = get_user_data_root()

    return RuntimePaths(
        user_data_root=os.path.normpath(str(user_root)),
        settings_path=os.path.normpath(str(user_settings_dir(user_root))),
        render_preset_path=os.path.normpath(str(user_preset_dir(user_root, "render"))),
        aov_cache_path=os.path.normpath(str(user_aov_cache_path(user_root))),
        icon_path=os.path.normpath(str(ICONS_ROOT)),
        languages_path=os.path.normpath(str(LANGUAGES_ROOT)),
    )


class DataManager(object):
    """旧 UI 所需的 JSON 读写兼容接口，委托给 ``core.storage``。"""

    def load_json(self, file_path):
        return load_json(file_path)

    def save_json(self, file_path, data):
        return save_json(file_path, data)


def load_config(paths=None):
    """读取用户 Arnold Magic Node 配置。"""

    paths = paths or get_runtime_paths()
    return load_json(os.path.join(paths.settings_path, AMS_CONFIG))


def save_config(config, paths=None):
    """保存用户 Arnold Magic Node 配置。"""

    paths = paths or get_runtime_paths()
    return save_json(os.path.join(paths.settings_path, AMS_CONFIG), config)


def load_language(paths=None):
    """按用户语言配置读取内置语言资源。"""

    paths = paths or get_runtime_paths()
    language_config = load_json(
        os.path.join(paths.settings_path, "language_config.json")
    )["language_config"]
    return load_json(os.path.join(paths.languages_path, language_config + ".json"))


def initialize_language_config(environment=None, paths=None):
    """按 Maya 当前界面语言创建缺失的语言选择文件。"""

    environment = environment or MayaEnvironmentAdapter()
    paths = paths or get_runtime_paths(environment.user_data_root())
    available_languages = [
        filename
        for filename in os.listdir(paths.languages_path)
        if filename.lower().endswith(".json")
    ]
    available_languages = {
        os.path.splitext(filename)[0] for filename in available_languages
    }
    maya_language = environment.ui_language()
    selected_language = (
        maya_language if maya_language in available_languages else "en_US"
    )
    language_config_path = os.path.join(
        paths.settings_path, "language_config.json"
    )
    if not os.path.exists(language_config_path):
        save_json(language_config_path, {"language_config": selected_language})


def is_modifier_pressed(modifier, modifiers=None, environment=None):
    """检测 Maya 当前的修饰键状态。"""

    if modifiers is None:
        modifiers = (environment or MayaEnvironmentAdapter()).modifiers()
    return bool(modifiers & modifier)


def ensure_runtime_directory(directory_path):
    """为界面菜单等按需创建一个运行时目录。"""

    return ensure_directory(directory_path)


__all__ = [
    "AMS_CONFIG",
    "DataManager",
    "EXTRA_LARGE_FONT_SIZE",
    "LARGE_FONT_SIZE",
    "MAYA_ALT_MODIFIER",
    "MAYA_SHIFT_MODIFIER",
    "MEDIUM_FONT_SIZE",
    "NORMAL_FONT_SIZE",
    "PLUGIN_FEEDBACK_URL",
    "PLUGIN_HELP_DOCUMENT_URL",
    "PLUGIN_HOME_URL",
    "PLUGIN_UPDATE_DOWNLOAD_URL",
    "RuntimePaths",
    "SMALL_FONT_SIZE",
    "SOFTWARE_STATE",
    "SOFTWARE_VERSION",
    "ensure_runtime_directory",
    "get_runtime_paths",
    "initialize_language_config",
    "is_modifier_pressed",
    "load_config",
    "load_language",
    "save_config",
]
