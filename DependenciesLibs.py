# -*- coding: utf-8 -*-
"""
    DependenciesLibs的作用是为了统一Maya版本然后导入必要运行库

"""

import os
import sys
import importlib
import subprocess
import time
from datetime import datetime
import maya.cmds as cmds

PythonVersion = sys.version.split()[0]
MayaVersion = cmds.about(version=True)  # Maya版本
MinorVersion = cmds.about(minorVersion=True)   # 次要版本号
PreferencesPath = cmds.about(preferences=True)  # 配置文件的地方
MayaInstallDir = os.environ.get('MAYA_LOCATION')    # Maya安装的地方
ScriptPath = os.path.join(os.path.dirname(__file__)) # 脚本路径

LibsPath = ScriptPath + '\\Libs\\maya' + str(MayaVersion)
MayapyPath = MayaInstallDir + '\\bin\\Mayapy.exe'

LibsFilesDict = {
    'cv2': 'opencv-python',
    'imagesize': 'imagesize',
    'keyboard': 'keyboard',
    'msgpack': 'msgpack',
    'PIL': 'Pillow',  # PIL 实际上是 Pillow 库
    'pyexr': 'pyexr',
    'Imath.py': 'Imath',  # Imath 是一个独立的包
    'OpenEXR.pyd': 'OpenEXR',  # OpenEXR 是一个单独的包
    'cryptography' : 'cryptography',
    'requests' : 'requests',
    'ntplib.py' : 'ntplib',
    'aiohttp' : 'aiohttp',
    'ahocorapy' : 'ahocorapy'
}

class FeedbackPrompt():
    """
    FeedbackPrompt此类是一个反馈错误的模块
    """

    def __init__(self):
        current_time = datetime.now()
        self.DefContent = '@Arnold Tool 插件提醒 {} | '.format(current_time.strftime("%Y-%m-%d %H:%M:%S"))

    def CP(self, Content):
        print(self.DefContent + Content)

feedback = FeedbackPrompt() # 导入报错模块

def Create_version_folder():
    if not os.path.exists(LibsPath):
        os.makedirs(LibsPath)

    feedback.CP("很好配置库文件夹存在 ╭(●｀∀´●)╯ 鼓掌鼓掌")

def DetectionLibs():
    for libName in LibsFilesDict:
        if not os.path.exists(os.path.join(LibsPath, libName)):
            libNamePro = libName.replace(".pyd", "").replace(".py", "")
            feedback.CP(f'发现<{libNamePro}>库不存在 ◔ ‸◔？   正在下载≖‿≖✧耐心等待')

            pip_command = [
                MayapyPath,
                "-m", "pip",
                "install", LibsFilesDict[libName],
                "--target", LibsPath,
                "-i", "https://mirrors.aliyun.com/pypi/simple/"
            ]

            # 执行命令
            subprocess.check_call(pip_command)

    feedback.CP("好棒！！！！环境配置没有任何问题♪（＾∀＾●）ﾉｼ ")

def importLibs():
    for libName in LibsFilesDict:
        libNamePro = libName.replace(".pyd", "").replace(".py", "")
        importlib.import_module(libNamePro)




def Main_program():
    """
    主程序函数，用于初始化并执行核心逻辑。

    - 记录程序的开始时间。
    - 配置库路径：将库的路径添加到系统路径（sys.path）中，确保自定义库能够被正确导入。
    - 创建版本文件夹：根据需要创建特定版本的文件夹。
    - 检测库：执行库的检测或安装操作。
    - 记录程序结束时间并计算总耗时。
    - 输出执行库检索的耗时信息。

    Returns:
        None
    """

    start_time = time.time()  # 记录开始时间

    # 配置库路径
    sys.path.append(LibsPath)  # 将库路径追加到系统路径
    sys.path.insert(0, LibsPath)  # 确保库路径被优先检索

    # 创建版本文件夹
    Create_version_folder()  # 根据需要创建版本文件夹

    # 检测库
    DetectionLibs()  # 检测或加载库

    end_time = time.time()  # 记录结束时间
    elapsed_time = end_time - start_time  # 计算经过的时间

    # 输出库检索的耗时信息
    feedback.CP(f"检索库时间: {elapsed_time:.4f} 秒")

