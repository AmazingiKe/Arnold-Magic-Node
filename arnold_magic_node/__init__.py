"""Arnold Magic Node 的公共入口。"""

import os
import sys


def _register_vendored_libs():
    """把仓库内联的第三方库目录加入搜索路径，使 ``import openai`` 可用。"""

    libs_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "libs")
    )
    if libs_path not in sys.path:
        sys.path.insert(0, libs_path)


_register_vendored_libs()


def show():
    """按需加载并显示插件界面。"""
    from .bootstrap import main

    return main()


__all__ = ["show"]
