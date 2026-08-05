# ______________________________________________________________________________>>> 导入必要库
import os  # 操作系统文件路径和操作
import importlib  # 动态加载模块
import maya.cmds as cmds  # Maya命令接口

from .core.paths import LANGUAGES_ROOT
from .core.storage import save_json
from .maya.environment import get_user_data_root

#______________________________________________________________________________>>> 检测 Maya 语言配置并创建语言文件
def detecting_language():
    """
    检测 Maya 所使用的语言，并创建对应的语言配置文件。
    如果语言配置文件不存在，则默认使用英文（en_US）。
    """
    language = {}

    # 获取语言文件目录中的所有语言选项
    language_list_dir = [path.name for path in LANGUAGES_ROOT.glob("*.json")]

    # 去掉文件后缀（.json）
    language_list_dir = [val.replace('.json', '') for val in language_list_dir]

    # 获取 Maya 当前使用的界面语言
    maya_language = cmds.about(uil=True)

    # 判断是否存在匹配的语言配置，否则默认英文
    if maya_language in language_list_dir:
        language['language_config'] = maya_language
    else:
        language['language_config'] = 'en_US'

    # 定义语言配置文件路径
    language_config_file_path = get_user_data_root() / "settings" / "language_config.json"

    # 如果语言配置文件不存在，则创建
    if not os.path.exists(language_config_file_path):
        save_json(language_config_file_path, language)

#______________________________________________________________________________>>> 主函数入口
def main():
    """
    主函数，负责初始化语言、默认配置和主界面。
    """
    # 检测语言配置
    detecting_language()

    # 加载并执行文件初始化模块
    from . import default_config
    importlib.reload(default_config)
    default_config.Main_program()

    # 加载并执行主程序模块
    from . import application
    importlib.reload(application)
    application.Main_program()
