"""
这个文件的作用是指定的路径下检查某些文件夹是否存在，如果不存在，则自动创建它们。
它可以确保程序运行时需要的文件夹结构是完整的，无需手动创建这些文件夹
"""


import os


# 获取当前脚本文件的路径
ScriptPath = os.path.join(os.path.dirname(__file__))  # 脚本路径

# 要检查或创建的文件夹列表（位于 'Datas' 文件夹下）
datas_folder_list = ['languages', 'render_settings', 'settings', 'texture_manager']

# 要检查或创建的文件夹列表（位于脚本根目录下）
scrip_of_folder_list = ['Libs', 'Datas', 'Temp']


def detecting_folders(path, folder_list):
    """
    检查路径下是否存在指定的文件夹，如果不存在则创建它们。

    :param path: 文件夹所在的根路径
    :param folder_list: 需要检测的文件夹名称列表
    """
    for folder in folder_list:
        # 将文件夹名称和路径拼接成完整的文件夹路径
        folder_path = os.path.join(path, folder)

        # 如果该文件夹不存在，则创建它
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


def Main_program():
    """
    主程序入口，负责调用文件夹检测函数。

    1. 在 'Datas' 文件夹下检查和创建需要的子文件夹。
    2. 在脚本所在的根路径下检查和创建需要的文件夹。
    """
    # 定义 'Datas' 文件夹的路径
    datas_path = os.path.join(ScriptPath, 'Datas')

    # 检查并在 'Datas' 文件夹下创建指定的子文件夹
    detecting_folders(datas_path, datas_folder_list)

    # 检查并在脚本根目录下创建指定的文件夹
    detecting_folders(ScriptPath, scrip_of_folder_list)