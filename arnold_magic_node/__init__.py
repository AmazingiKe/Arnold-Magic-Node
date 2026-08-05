"""Arnold Magic Node 的公共入口。"""


def show():
    """按需加载并显示插件界面。"""
    from .bootstrap import main

    return main()


__all__ = ["show"]
