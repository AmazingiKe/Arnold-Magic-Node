"""旧版 Shelf 命令的兼容入口。"""

import os
import sys


scripts_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "scripts"))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from arnold_magic_node import show


def main():
    """将旧入口委托给新的唯一包入口。"""
    return show()
