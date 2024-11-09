import os
import shutil


def copy_files_and_folders(src_folder, dest_folder):
    # 定义需要复制的文件和文件夹
    files_to_include = [
        'Arnold_Magic_Node.py',
        'Arnold_Magic_Node_Install.py',
        'Arnold_Magic_Node_lib.py',
        'Arnold_Magic_Node_Start.py',
        'InitialConfigFile.py',
        'InitialConfigFolder.py',
        'LicenseValidator.py',
        'DependenciesLibs.py',
        'README.md'
    ]

    folders_to_include = {
        'icon': None,  # 整个 icon 文件夹
        'Datas/languages': None  # Datas 文件夹中的 languages 文件夹
    }

    # 创建目标目录（如果不存在）
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    # 复制文件
    for file in files_to_include:
        src_file_path = os.path.join(src_folder, file)
        dest_file_path = os.path.join(dest_folder, file)
        if os.path.isfile(src_file_path):
            shutil.copy2(src_file_path, dest_file_path)
            print(f"复制文件: {src_file_path} -> {dest_file_path}")

    # 复制文件夹及其内容
    for folder, _ in folders_to_include.items():
        src_folder_path = os.path.join(src_folder, folder)
        dest_folder_path = os.path.join(dest_folder, folder)
        if os.path.exists(src_folder_path):
            shutil.copytree(src_folder_path, dest_folder_path, dirs_exist_ok=True)
            print(f"复制文件夹: {src_folder_path} -> {dest_folder_path}")

    print(f"所有文件和文件夹已复制到: {dest_folder}")


# 示例使用
src_folder = r'D:\DevHub\Maya_arnold_tool_WorkInProgress\Maya_arnold_tool'  # 替换为你的源文件夹路径
dest_folder = input("请输入目标文件夹路径：")  # 用户输入的目标文件夹路径

# 调用复制函数
copy_files_and_folders(src_folder, dest_folder)