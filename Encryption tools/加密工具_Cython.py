import os
import shutil
import subprocess
import sys
import glob
import re
from setuptools import setup
from Cython.Build import cythonize

# 对应 Maya 版本的 Python 版本
corresponding_version = {
    'maya2022': '3.7.7',
    'maya2023': '3.9.7',
    'maya2024': '3.10.8',
    'maya2025': '3.11.4'
}

# 自定义 Python 版本的路径字典
python_paths = {
    '3.7.7': r'C:\Users\19252\AppData\Local\Programs\Python\Python37\python.exe',
    '3.9.7': r'C:\Users\19252\AppData\Local\Programs\Python\Python39\python.exe',
    '3.10.8': r'C:\Users\19252\AppData\Local\Programs\Python\Python310\python.exe',
    '3.11.4': r'C:\Users\19252\AppData\Local\Programs\Python\Python311\python.exe'
}

def find_python_executable(version):
    """根据指定的 Python 版本返回 Python 可执行文件的绝对路径"""
    if version in python_paths:
        python_exec = python_paths[version]
        if os.path.exists(python_exec):
            return python_exec
        else:
            raise FileNotFoundError(f"指定路径中的 Python {version} 可执行文件未找到: {python_exec}")
    else:
        raise FileNotFoundError(f"未定义 Python {version} 的路径，请更新 python_paths。")


def copy_files_and_folders(src_folder, dest_folder, files_to_include, folders_to_include):
    """复制文件和文件夹的函数"""
    # 创建目标目录（如果不存在）
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    # 复制文件
    for file in files_to_include:
        src_file_path = os.path.join(src_folder, file)
        dest_file_path = os.path.join(dest_folder, file)
        if os.path.isfile(src_file_path):
            # 创建目标文件所在的目录（如果不存在）
            os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
            shutil.copy2(src_file_path, dest_file_path)
            print(f"复制文件: {src_file_path} -> {dest_file_path}")
        else:
            print(f"文件未找到: {src_file_path}")

    # 复制文件夹及其内容
    for folder in folders_to_include:
        src_folder_path = os.path.join(src_folder, folder)
        dest_folder_path = os.path.join(dest_folder, folder)
        if os.path.exists(src_folder_path):
            shutil.copytree(src_folder_path, dest_folder_path, dirs_exist_ok=True)
            print(f"复制文件夹: {src_folder_path} -> {dest_folder_path}")
        else:
            print(f"文件夹未找到: {src_folder_path}")

    print(f"所有文件和文件夹已复制到: {dest_folder}")


def encrypt_py_files(py_files, build_dir, python_version):
    # 动态生成 setup.py 内容
    setup_code = f"""
from setuptools import setup, Extension
from Cython.Build import cythonize

py_files = {py_files}

extensions = [Extension(name=file.replace('.py', ''), sources=[file]) for file in py_files]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={{'language_level': "3"}},
    ),
)
"""
    # 将 setup 代码写入临时 setup.py 文件
    temp_setup_path = os.path.join(build_dir, "temp_setup.py")
    with open(temp_setup_path, "w", encoding='utf-8') as f:
        f.write(setup_code)

    # 保存当前工作目录
    original_dir = os.getcwd()

    # 切换到编译目录
    os.chdir(build_dir)

    # 查找指定版本的 Python 可执行文件
    python_exec = find_python_executable(python_version)

    # 使用 subprocess 调用对应的 Python 版本来编译
    subprocess.run([python_exec, "temp_setup.py", "build_ext", "--inplace"])

    # 删除生成的 .c 文件
    c_files = glob.glob("*.c")
    for c_file in c_files:
        os.remove(c_file)
        print(f"已删除生成的 C 文件: {c_file}")

    # 重命名生成的 .pyd 文件，移除中间的后缀
    pyd_files = glob.glob("*.pyd")
    pattern = re.compile(r"(.*)(\.cp\d{2,3}-\w+)(\.pyd)")
    for pyd_file in pyd_files:
        match = pattern.match(pyd_file)
        if match:
            new_name = f"{match.group(1)}.pyd"
            os.rename(pyd_file, new_name)
            print(f"已重命名 {pyd_file} 为 {new_name}")

    # 回到原始目录
    os.chdir(original_dir)

    # 清理临时文件
    os.remove(temp_setup_path)

    # 删除 build 文件夹
    build_folder = os.path.join(build_dir, "build")
    if os.path.exists(build_folder):
        shutil.rmtree(build_folder)
        print(f"已删除 build 文件夹: {build_folder}")


def main():
    # 定义需要复制并加密的文件
    files_to_include = [
        'Arnold_Magic_Node.py',
        'Arnold_Magic_Node_Install.py',
        'Arnold_Magic_Node_lib.py',
        'Arnold_Magic_Node_Start.py',
        'InitialConfigFile.py',
        'InitialConfigFolder.py',
        # 'LicenseValidator.py',
        'DependenciesLibs.py',
        'README.md'
    ]

    # 需要加密的文件（从 files_to_include 中选择）
    files_to_encrypt = [
        'Arnold_Magic_Node.py',
        'Arnold_Magic_Node_lib.py',
        'Arnold_Magic_Node_Start.py',
        'InitialConfigFile.py',
        'InitialConfigFolder.py',
        # 'LicenseValidator.py',
        'DependenciesLibs.py'
    ]

    # 定义需要复制的文件夹
    folders_to_include = [
        'icon',
        'Datas/languages'
    ]

    src_folder = r'D:\DevHub\Maya_arnold_tool_WorkInProgress\Maya_arnold_tool'  # 替换为你的源文件夹路径
    dest_folder_base = input("请输入目标文件夹基础路径：")  # 用户输入的目标文件夹基础路径

    # 循环创建每个 Maya 对应的版本文件夹，并执行复制和加密
    for maya_version, python_version in corresponding_version.items():
        dest_folder = os.path.join(dest_folder_base, maya_version)

        # 调用复制函数
        copy_files_and_folders(src_folder, dest_folder, files_to_include, folders_to_include)

        # 切换文件路径到目标目录中的相对路径
        encrypted_files_relative = []
        for file in files_to_encrypt:
            if os.path.isfile(os.path.join(dest_folder, file)):
                encrypted_files_relative.append(file)
            else:
                print(f"需要加密的文件未找到: {file}")

        if encrypted_files_relative:
            # 调用加密函数
            encrypt_py_files(encrypted_files_relative, dest_folder, python_version)
        else:
            print("未找到需要加密的文件，跳过加密步骤。")

    # 可选：删除源代码文件和生成的 build 文件夹
    delete_option = input("请选择要删除的文件（1: 源代码文件, 2: build 文件夹, 3: 一起删除, 0: 不删除）: ")
    for maya_version in corresponding_version.keys():
        dest_folder = os.path.join(dest_folder_base, maya_version)
        if delete_option in ['1', '3']:
            for py_file in files_to_encrypt:
                py_file_path = os.path.join(dest_folder, py_file)
                if os.path.exists(py_file_path):
                    os.remove(py_file_path)
                    print(f"已删除源文件: {py_file_path}")
                else:
                    print(f"源文件未找到: {py_file_path}")
        if delete_option in ['2', '3']:
            build_folder = os.path.join(dest_folder, "build")
            if os.path.exists(build_folder):
                shutil.rmtree(build_folder)
                print(f"已删除 build 文件夹: {build_folder}")
        else:
            print("未选择删除任何文件。")


if __name__ == "__main__":
    main()
