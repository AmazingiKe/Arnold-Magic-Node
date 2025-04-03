###########################
#
#   Arnold_Magic_Node_安装器
#   Arnold_Magic_Node_Plugin Installer
#
#   2024年12月12日修改安装器
#   Modified installer on December 12, 2024
#
###########################

import os
import maya.mel
import maya.cmds as cmds


class LicenseInstaller:
    def __init__(self):
        self.license_shown = False

    def show_license_window(self):
        """
        显示许可证窗口
        """
        # 如果已经显示过许可证，直接执行安装
        if self.license_shown:
            self.INSTALL()
            return

        # 许可证文本内容
        try:
            with open(os.path.join(os.path.dirname(__file__), "Arnold_Magic_Node_License.txt"), "r",
                      encoding="utf-8") as f:
                license_text = f.read()
        except FileNotFoundError:
            license_text = "许可证文件未找到"

        # 创建许可证窗口
        if cmds.window("licenseWindow", exists=True):
            cmds.deleteUI("licenseWindow")

        window = cmds.window(
            "licenseWindow",
            title="Arnold Magic Node - EULA",
            widthHeight=(500, 565),
            sizeable=False
        )

        # 主布局
        main_layout = cmds.columnLayout(adjustableColumn=True, parent=window)

        # 标题
        cmds.text(
            label="Arnold Magic Node | End User License Agreement",
            font="boldLabelFont",
            height=30,
            backgroundColor=[0.2, 0.2, 0.2]
        )

        # 许可证文本区域
        cmds.scrollField(
            editable=False,
            wordWrap=True,
            text=license_text,
            height=500,
            width=480,
            parent=main_layout
        )

        # 按钮布局
        button_row = cmds.rowColumnLayout(
            numberOfColumns=3,  # 增加一列用于间隔
            columnWidth=[(1, 240), (2, 20), (3, 240)],
            parent=main_layout
        )

        # 拒绝按钮
        cmds.button(
            label="Not Accept",
            width=240,
            command=lambda x: cmds.deleteUI(window)
        )

        # 间隔
        cmds.separator(style='none', width=20)

        # 接受按钮
        cmds.button(
            label="Yes, I Accept",
            width=240,
            command=self.accept_license
        )

        cmds.showWindow(window)

    def accept_license(self, *args):
        """
        接受许可证
        """
        # 关闭窗口
        if cmds.window("licenseWindow", exists=True):
            cmds.deleteUI("licenseWindow")

        # 标记已显示许可证
        self.license_shown = True

        # 执行安装
        self.INSTALL()

    def INSTALL(self):
        """
        将自定义工具安装到 Maya 的工具架中
        """
        # 获取当前脚本路径
        script_path = os.path.normpath(os.path.join(os.path.dirname(__file__)))

        # 需要执行的 Python 脚本命令
        command = f'''import sys
import importlib
import os

File_Path = r"{script_path}"

if not os.path.exists(File_Path):
    cmds.confirmDialog(message="检测到你的路径是错误的", button="确定", title="报错提醒，滴滴滴")
else:
    sys.path.append(File_Path)
    import Arnold_Magic_Node_Start

    importlib.reload(Arnold_Magic_Node_Start)
    Arnold_Magic_Node_Start.main()
'''

        # 获取当前选中的工具架
        shelf = maya.mel.eval('$gShelfTopLevel=$gShelfTopLevel')
        parent = maya.cmds.tabLayout(shelf, query=True, selectTab=True)

        # 定义按钮名称
        button_name = 'Arnold_Magic_Node'

        # 将按钮添加到当前工具架中
        cmds.shelfButton(
            command=command,
            annotation=button_name,
            imageOverlayLabel=button_name,
            sourceType='Python',
            image='alignSurface.png',
            parent=parent,
            label=button_name
        )


# 创建全局实例
license_installer = LicenseInstaller()


def onMayaDroppedPythonFile(*args, **kwargs):
    license_installer.show_license_window()


# 启动时显示许可证窗口
license_installer.show_license_window()
