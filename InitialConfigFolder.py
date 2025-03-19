"""
这个文件的作用是指定的路径下检查某些文件夹是否存在，如果不存在，则自动创建它们。
它可以确保程序运行时需要的文件夹结构是完整的，无需手动创建这些文件夹。
"""

# ______________________________________________________________________________>>> 导入必要库
import os  # 操作系统文件路径相关模块

#______________________________________________________________________________>>> 全局变量定义

# 获取当前脚本文件的路径
script_path = os.path.normpath(os.path.join(os.path.dirname(__file__)))  # 脚本路径

# 要检查或创建的文件夹列表（位于 'Datas' 文件夹下）
datas_folder_list = [
    'languages',  # 语言文件夹
    'render_presets',  # 渲染预设
    'settings',  # 设置文件夹
    'texture_manager',  # 纹理管理
    'keys',  # 密钥文件夹
    'execution_logs',  # 执行日志
    'logs',  # 普通日志
    'aov_light_group_manager' # AOV灯光组管理器
]

# 要检查或创建的文件夹列表（位于脚本根目录下）
scrip_of_folder_list = [
    'Libs',  # 库文件夹
    'Datas',  # 数据文件夹
    'Temp'  # 临时文件夹
]

#______________________________________________________________________________>>> 文件夹检测与创建函数
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

#______________________________________________________________________________>>> 主程序入口
def Main_program():
    """
    主程序入口，负责调用文件夹检测函数。

    1. 在 'Datas' 文件夹下检查和创建需要的子文件夹。
    2. 在脚本所在的根路径下检查和创建需要的文件夹。
    """
    # 定义 'Datas' 文件夹的路径
    datas_path = os.path.join(script_path, 'Datas')

    # 检查并在 'Datas' 文件夹下创建指定的子文件夹
    detecting_folders(datas_path, datas_folder_list)

    # 检查并在脚本根目录下创建指定的文件夹
    detecting_folders(script_path, scrip_of_folder_list)
