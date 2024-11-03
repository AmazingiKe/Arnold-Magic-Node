"""
    DependenciesLibs的作用是为了统一Maya版本然后导入必要运行库
"""

import os
import sys
import importlib
import subprocess
import time
import json
import re
from datetime import datetime
# noinspection PyUnresolvedReferences
import maya.cmds as cmds

PythonVersion = sys.version.split()[0]
MayaVersion = cmds.about(version=True) # Maya版本
MinorVersion = cmds.about(minorVersion=True) # 次要版本号
PreferencesPath = cmds.about(preferences=True) # 配置文件的地方
MayaInstallDir = os.environ.get('MAYA_LOCATION') # Maya安装的地方

ScriptPath = os.path.normpath(os.path.join(os.path.dirname(__file__))) # 脚本路径
DataPath =  os.path.normpath(os.path.join(ScriptPath, 'Datas')) # 数据文件夹
ExecutionLogsPath = os.path.normpath(os.path.join(DataPath, 'execution_logs')) # 执行次数记录文件夹

LibsPath =  os.path.normpath(os.path.join(ScriptPath, 'Libs', f'maya{str(MayaVersion)}')) # 库文件夹
MayapyPath = os.path.normpath(os.path.join(MayaInstallDir, 'bin', 'Mayapy.exe')) # maya maypy文件位置

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
    'Levenshtein' : 'python-Levenshtein',
    'wmi.py' : 'WMI',
    # 'pywin32_system32' : 'pywin32'
}

def ascii_load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def ascii_save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

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
        cmds.warning(self.DefContent + content)

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
                "--upgrade",  # 添加 --upgrade 选项
                "-i", "https://mirrors.aliyun.com/pypi/simple/"
            ]

            # 执行命令
            subprocess.check_call(pip_command)

    feedback.cp(language["DL"]["03"]) # "好棒！！！！环境配置没有任何问题♪（＾∀＾●）ﾉｼ "

def importLibs():
    for libName in LibsFilesDict:
        libNamePro = libName.replace(".pyd", "").replace(".py", "")
        importlib.import_module(libNamePro)

def upgrade_pip(MayapyPath):
    """
    直接升级 mayapy 的 pip 版本。

    Args:
        MayapyPath (str): mayapy.exe 的路径。
    """

    # 定义状态字典，用于记录升级状态
    state = {"upgrade_pip_state": None}

    try:
        # 提示用户正在升级 pip 库
        feedback.cp(language["upgrade_pip"]["01"])  # "正在升级 pip库..."

        # 运行 pip 升级命令
        subprocess.run([MayapyPath,
                        "-m",
                        "pip",
                        "install",
                        "--upgrade",
                        "pip",
                        "-i",
                        "https://mirrors.aliyun.com/pypi/simple/"], check=True)

        # 提示用户 pip 库升级成功
        feedback.cp(language["upgrade_pip"]["02"])  # "pip库 已成功升级!"

        # 更新状态为成功
        state['upgrade_pip_state'] = True

        # 保存升级状态到 JSON 文件
        ascii_save_data(
            os.path.normpath(os.path.join(ExecutionLogsPath, 'upgrade_pip_state.json')),
            state
        )

    except subprocess.CalledProcessError as e:
        # 如果升级失败，更新状态为失败
        state['upgrade_pip_state'] = False

        # 保存失败状态到 JSON 文件
        ascii_save_data(
            os.path.normpath(os.path.join(ExecutionLogsPath, 'upgrade_pip_state.json')),
            state
        )

        # 提示用户升级失败及原因
        feedback.cp(f'{language["upgrade_pip"]["03"]}{e}')  # 升级 pip 失败原因:

def check_and_install_pywin32(mayapy_path):

    try:
        import wmi
    except ModuleNotFoundError as e:
        feedback.cp(language["check_and_install_pywin32"]["01"]) # 检测到pywin32无法找到
        feedback.cp(language["check_and_install_pywin32"]["02"])  # 正在尝试重新安装 pywin32...

        # 卸载旧版本
        subprocess.run([mayapy_path, '-m', 'pip', 'uninstall', 'pywin32', '-y'])

        # 重新安装 pywin32
        subprocess.run([mayapy_path, '-m', 'pip', 'install', 'pywin32', "--upgrade", "-i", "https://mirrors.aliyun.com/pypi/simple/"])

        # 手动注册 pywin32
        pywin32_postinstall_path = r"{}\Lib\site-packages\pywin32_system32\pywin32_postinstall.py".format(mayapy_path[:-12])
        subprocess.run([mayapy_path, pywin32_postinstall_path, '-install'])

        feedback.cp(language["check_and_install_pywin32"]["03"]) # pywin32 安装完成，请重启 Maya

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

    # 检查升级状态文件是否存在
    if not os.path.exists(os.path.normpath(os.path.join(ExecutionLogsPath, 'upgrade_pip_state.json'))):
        # 如果文件不存在，调用 upgrade_pip 函数进行 pip 升级
        upgrade_pip(MayapyPath)


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

    check_and_install_pywin32(MayapyPath) # 检测wmi是否可以使用

    # 输出库检索的耗时信息
    feedback.cp(f'{language["MP"]["01"]}{format(elapsed_time,".4f")}{language["MP"]["02"]}')
    # "检索库时间: "
    #  " 秒"
