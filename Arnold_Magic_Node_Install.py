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

# Import Qt libraries
try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtCore import Signal, Slot
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtCore import Signal, Slot


class LicenseWindow(QtWidgets.QDialog):
    def __init__(self, parent=None, installer=None):
        super(LicenseWindow, self).__init__(parent)
        self.installer = installer
        self.setWindowTitle("Arnold Magic Node - EULA")
        self.setFixedSize(600, 800)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Title
        title_label = QtWidgets.QLabel("Arnold Magic Node | End User License Agreement")
        title_label.setStyleSheet("background-color: #333333; color: white; font-weight: bold; padding: 5px;")
        title_label.setFixedHeight(30)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # License text area
        try:
            with open(os.path.join(os.path.dirname(__file__), "Arnold_Magic_Node_License.txt"), "r",
                      encoding="utf-8") as f:
                license_text = f.read()
        except FileNotFoundError:
            license_text = "许可证文件未找到 (License file not found)"

        self.text_area = QtWidgets.QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setText(license_text)
        # self.text_area.setFixedHeight(450)
        main_layout.addWidget(self.text_area)

        # Buttons layout
        button_layout = QtWidgets.QHBoxLayout()

        # Decline button
        decline_button = QtWidgets.QPushButton("Not Accept")
        decline_button.setFixedWidth(240)
        decline_button.clicked.connect(self.reject)

        # Accept button
        accept_button = QtWidgets.QPushButton("Yes, I Accept")
        accept_button.setFixedWidth(240)
        accept_button.clicked.connect(self.accept_license)

        button_layout.addWidget(decline_button)
        button_layout.addSpacing(20)  # Add spacing between buttons
        button_layout.addWidget(accept_button)

        main_layout.addLayout(button_layout)

    def accept_license(self):
        if self.installer:
            self.installer.license_shown = True
            self.installer.INSTALL()
        self.accept()


class LicenseInstaller:
    def __init__(self):
        self.license_shown = False
        self.license_window = None

    def show_license_window(self):
        """
        显示许可证窗口
        """
        # 如果已经显示过许可证，直接执行安装
        if self.license_shown:
            self.INSTALL()
            return

        # 创建并显示Qt窗口
        self.license_window = LicenseWindow(installer=self)
        result = self.license_window.exec_()

        # 如果用户关闭窗口而不点击按钮，我们认为用户拒绝了许可
        if result != QtWidgets.QDialog.Accepted:
            self.license_window = None

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
            image=os.path.normpath(os.path.join(script_path, "icon","Logo_B.svg")),
            parent=parent,
            label=button_name
        )


# 创建全局实例
license_installer = LicenseInstaller()


def onMayaDroppedPythonFile(*args, **kwargs):
    license_installer.show_license_window()


# 启动时显示许可证窗口
license_installer.show_license_window()
