"""
    DependenciesLibs的作用是为了统一Maya版本然后导入必要运行库
"""

import os
import sys
import importlib
import subprocess
import time
import json
from datetime import datetime
# noinspection PyUnresolvedReferences
import maya.cmds as cmds

PythonVersion = sys.version.split()[0]
MayaVersion = cmds.about(version=True)  # Maya版本
MinorVersion = cmds.about(minorVersion=True)   # 次要版本号
PreferencesPath = cmds.about(preferences=True)  # 配置文件的地方
MayaInstallDir = os.environ.get('MAYA_LOCATION')    # Maya安装的地方
ScriptPath = os.path.join(os.path.dirname(__file__)) # 脚本路径

LibsPath =  os.path.normpath(os.path.join(ScriptPath, 'Libs', f'maya{str(MayaVersion)}'))
MayapyPath = os.path.normpath(os.path.join(MayaInstallDir, 'bin', 'Mayapy.exe'))

LibsFilesDict = {
    #'cv2': 'opencv-python',
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
    'ahocorapy' : 'ahocorapy',
    'Levenshtein' : 'python-Levenshtein'
}

def ascii_load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# 加载语言配置文件，将其解析为Python字典并获取其中的 'language_config' 键的值
# 'language_config' 是从 'language_config.json' 文件中读取的指定语言（例如: 'en', 'zh'等）
language_config = ascii_load_data(os.path.join(ScriptPath, 'Datas', 'settings', 'language_config.json'))['language_config']

# 根据上一步加载的 'language_config'，动态加载相应语言的JSON文件
# 这个文件应该位于 'Datas/languages' 目录中，文件名与 'language_config' 的值相同（如 'en.json'）
# 从该语言文件中读取 'DLibs' 键的内容，通常用于加载与该语言相关的库或资源
language = ascii_load_data(os.path.join(ScriptPath, 'Datas', 'languages', f'{language_config}.json'))["DLibs"]


class FeedbackPrompt:
    """
    FeedbackPrompt此类是一个反馈错误的模块
    """

    def __init__(self):
        current_time = datetime.now()
        self.DefContent = language["FP"].format(current_time.strftime("%Y-%m-%d %H:%M:%S")) # "@Arnold Tool 插件提醒 {} | "

    def cp(self, content):
        print(self.DefContent + content)

feedback = FeedbackPrompt() # 导入报错模块

def create_version_folder():
    if not os.path.exists(LibsPath):
        os.makedirs(LibsPath)

    feedback.cp(language["CVF"]) # 很好配置库文件夹存在 ╭(●｀∀´●)╯ 鼓掌鼓掌

def detection_libs():
    for libName in LibsFilesDict:
        if not os.path.exists(os.path.join(LibsPath, libName)):
            libNamePro = libName.replace(".pyd", "").replace(".py", "")
            feedback.cp(f'{language["DL"]["01"]}<{libNamePro}>{language["DL"]["02"]}')
            # "发现"
            # "库不存在 ◔ ‸◔？   正在下载≖‿≖✧耐心等待"

            pip_command = [
                MayapyPath,
                "-m", "pip",
                "install", LibsFilesDict[libName],
                "--target", LibsPath,
                "-i", "https://mirrors.aliyun.com/pypi/simple/"
            ]

            # 执行命令
            subprocess.check_call(pip_command)

    feedback.cp(language["DL"]["03"]) # "好棒！！！！环境配置没有任何问题♪（＾∀＾●）ﾉｼ "

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

    sys.path = list(set(sys.path))  # 去重路径

    # 创建版本文件夹
    create_version_folder()  # 根据需要创建版本文件夹

    # 检测库
    detection_libs()  # 检测或加载库

    end_time = time.time()  # 记录结束时间
    elapsed_time = end_time - start_time  # 计算经过的时间

    # 输出库检索的耗时信息
    feedback.cp(f'{language["MP"]["01"]}{format(elapsed_time,".4f")}{language["MP"]["02"]}')
    # "检索库时间: "
    #  " 秒"