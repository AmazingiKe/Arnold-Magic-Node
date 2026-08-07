"""PySide 与 shiboken 兼容导入。"""
# 兼容2022往后的所有版本

try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtGui import QAction
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtWidgets import QAction
    from shiboken2 import wrapInstance
