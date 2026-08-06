"""Arnold Magic Node 的应用组装入口。"""


def detecting_language():
    """初始化缺失的 Maya 用户语言配置。"""

    from .tools.runtime import initialize_language_config

    return initialize_language_config()


def main():
    """初始化用户数据并构建主窗口。

    入口只负责组装：UI 通过 ``tools`` 调用功能，旧的单体热重载
    兼容层不再参与运行。
    """

    import maya.cmds as cmds

    from .tools.settings import ensure_user_settings

    detecting_language()
    ensure_user_settings()

    from .ui import workspace
    from .ui.main_window import MainWindow

    workspace.delete_window_if_existe("ArnoldMagicNodeSettingsPanel")
    workspace.delete_window_if_existe("AOVLightGroupManager")
    if cmds.window("import_name_win", exists=True):
        cmds.deleteUI("import_name_win")

    return MainWindow()


__all__ = ["detecting_language", "main"]
