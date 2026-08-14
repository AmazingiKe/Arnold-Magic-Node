"""插件包与用户数据的纯路径工具。

本模块不导入 Maya，也不创建目录。宿主相关的用户目录解析位于
``arnold_magic_node.maya.environment``，这样核心路径和存储逻辑可以在
普通 Python 环境中测试。
"""

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PACKAGE_ROOT.parent
ICONS_ROOT = PROJECT_ROOT / "icons"
CONFIG_ROOT = PROJECT_ROOT / "config"
DEFAULT_SETTINGS_PATH = CONFIG_ROOT / "Arnold_Magic_Settings.json"
DEFAULT_AI_SETTINGS_PATH = CONFIG_ROOT / "AI_Settings.json"
RESOURCES_ROOT = PACKAGE_ROOT / "resources"
LANGUAGES_ROOT = RESOURCES_ROOT / "i18n"

VERSION_FILENAME = "VERSION"

USER_DATA_DIRNAME = "arnold_magic_node"
SETTINGS_DIRNAME = "settings"
PRESETS_DIRNAME = "presets"
RENDER_PRESETS_DIRNAME = "render"
LOGS_DIRNAME = "logs"
AOV_CACHE_FILENAME = "aov_light_group_cache.json"


def user_data_root(host_user_app_dir):
    """Return the plugin directory below Maya's user application directory."""
    return Path(host_user_app_dir).expanduser() / USER_DATA_DIRNAME


def user_settings_dir(user_root):
    """Return the user settings directory without creating it."""
    return Path(user_root) / SETTINGS_DIRNAME


def user_settings_path(user_root, filename):
    """Return a user settings file path."""
    return user_settings_dir(user_root) / filename


def user_presets_dir(user_root):
    """Return the unified presets directory without creating it."""
    return Path(user_root) / PRESETS_DIRNAME


def user_preset_dir(user_root, kind):
    """Return the render preset directory."""
    if kind != "render":
        raise ValueError("unsupported preset kind: {!r}".format(kind))
    return user_presets_dir(user_root) / RENDER_PRESETS_DIRNAME


def user_preset_path(user_root, kind, filename):
    """Return a render preset file path."""
    return user_preset_dir(user_root, kind) / filename


def user_aov_cache_path(user_root):
    """Return the single AOV cache file path at the user data root."""
    return Path(user_root) / AOV_CACHE_FILENAME


def user_logs_dir(user_root):
    """Return the unified user log directory without creating it."""
    return Path(user_root) / LOGS_DIRNAME


def user_log_path(user_root, filename):
    """Return a file path in the unified user log directory."""
    return user_logs_dir(user_root) / filename
