"""Maya 窗口查找与清理辅助。"""

import maya.OpenMayaUI as omui

from .qt import QtWidgets, wrapInstance


def get_maya_main_window():
    """获取Maya主窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr),QtWidgets.QWidget)

def delete_window_if_existe(window_name):
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == window_name:
            widget.close()
            widget.deleteLater()
