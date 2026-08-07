"""休眠的贴图批量导入窗口；迁移期间不恢复菜单入口。"""

import maya.cmds as cmds


class TextureBatchImporterDialog:
    def __init__(self):
        WIN_TITLE = "TextureBatchImporterDialog  Beta:1.0"

        # 判断窗口是否存在，如果存在则删除
        if cmds.window(WIN_TITLE, exists=True):
            cmds.deleteUI(WIN_TITLE)

        # 创建主窗口
        self.window = cmds.workspaceControl(WIN_TITLE, retain=False, floating=True,w=300,h=300)








        # 显示窗口
        cmds.showWindow(self.window)

        def create_widgets(self):
            pass
