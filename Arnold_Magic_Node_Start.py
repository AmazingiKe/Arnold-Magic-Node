# -*- coding: utf-8 -*-
import os
import importlib
import maya.cmds as cmds
import json

Script_path = os.path.join(os.path.dirname(__file__))

# 检测maya所用的语言并创建相应的语言配置
def detecting_language():
    language = {}

    # 获取当前脚本的目录路径
    Script_path = os.path.join(os.path.dirname(__file__)).replace('/', '\\').replace("\\", "\\\\")

    # 获取所有的语言文件
    language_list_dir = os.listdir(
        os.path.join(Script_path, "Datas", "languages")
    )
    # 删除.json
    language_list_dir = [val.replace('.json', '') for val in language_list_dir]


    maya_language = cmds.about(uil=True)

    # 如果存在maya使用的语言有的话就用，没有的话就默认英文
    if maya_language not in language_list_dir:
        language['language_config'] = maya_language
    else:
        language['language_config'] = 'zh_CN'

    # 获取语言配置的路径
    language_config_file_path = os.path.join(Script_path, "Datas", "settings", "language_config.json")

    if not os.path.exists(language_config_file_path):
        with open(language_config_file_path, 'w') as file:
            json.dump(language, file, indent=4)

def main():
    import InitialConfigFolder
    importlib.reload(InitialConfigFolder)
    InitialConfigFolder.Main_program()

    detecting_language()

    import DependenciesLibs
    importlib.reload(DependenciesLibs)
    DependenciesLibs.Main_program()

    import InitialConfigFile
    importlib.reload(InitialConfigFile)
    InitialConfigFile.Main_program()

    import LicenseValidator
    importlib.reload(LicenseValidator)
    LicenseValidator.Main_program()
