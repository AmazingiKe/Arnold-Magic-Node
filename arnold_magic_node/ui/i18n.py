"""Qt 翻译器装载与语言清单工具。

设置窗口迁移到 Qt tr() 后，翻译资源以 .qm 形式分发，语言切换
统一走本模块；JSON 语言资源仍被主窗口与工具层反馈使用。
"""

import os

from arnold_magic_node.core.paths import LANGUAGES_ROOT
from arnold_magic_node.core.storage import load_json
from arnold_magic_node.tools.runtime import get_runtime_paths
from ._qt_compat import QtCore, QtWidgets


DEFAULT_LANGUAGE_CODE = "en_US"

LANGUAGE_DISPLAY_NAMES = {"en_US": "English", "zh_CN": "简体中文"}

TRANSLATION_FILE_PREFIX = "arnold_magic_node_"

LANGUAGE_CONFIG_FILE = "language_config.json"

# 翻译器必须由模块级引用持有，防止被垃圾回收后翻译失效
_installed_translator = None


def current_language_code():
    """读取用户语言配置；配置文件缺失或内容非法时回退英文。"""

    config_path = os.path.join(
        get_runtime_paths().settings_path, LANGUAGE_CONFIG_FILE
    )
    try:
        return load_json(config_path)["language_config"]
    except (OSError, ValueError, KeyError):
        return DEFAULT_LANGUAGE_CODE


def available_languages():
    """返回可切换的语言码列表，英文源码语言恒在首位。"""

    codes = [DEFAULT_LANGUAGE_CODE]
    prefix = TRANSLATION_FILE_PREFIX
    suffix = ".qm"
    for filename in os.listdir(LANGUAGES_ROOT):
        if filename.startswith(prefix) and filename.endswith(suffix):
            codes.append(filename[len(prefix) : -len(suffix)])
    return codes


def language_display_name(code):
    """返回语言码的用户可读名称，未知语言码直接显示码本身。"""

    return LANGUAGE_DISPLAY_NAMES.get(code, code)


def install_language_translator(code=None):
    """装载指定语言的翻译器并安装到应用。

    英文是源码语言，不需要翻译文件；目标 .qm 不存在时保持不安装，
    让 tr() 回退显示英文原文。
    """

    global _installed_translator

    code = code or current_language_code()
    app = QtWidgets.QApplication.instance()
    if _installed_translator is not None:
        if app is not None:
            app.removeTranslator(_installed_translator)
        _installed_translator = None

    if code == DEFAULT_LANGUAGE_CODE:
        return

    translator_path = os.path.join(
        LANGUAGES_ROOT, TRANSLATION_FILE_PREFIX + code + ".qm"
    )
    if not os.path.exists(translator_path):
        return

    translator = QtCore.QTranslator()
    if translator.load(translator_path):
        _installed_translator = translator
        if app is not None:
            app.installTranslator(translator)


__all__ = [
    "DEFAULT_LANGUAGE_CODE",
    "LANGUAGE_CONFIG_FILE",
    "LANGUAGE_DISPLAY_NAMES",
    "TRANSLATION_FILE_PREFIX",
    "available_languages",
    "current_language_code",
    "install_language_translator",
    "language_display_name",
]
