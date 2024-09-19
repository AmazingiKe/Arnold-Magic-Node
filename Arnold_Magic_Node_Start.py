# -*- coding: utf-8 -*-
import os
import sys
import importlib
# import msgpack

Script_path = os.path.join(os.path.dirname(__file__))


# # 保存数据为二进制格式
# def bin_save_data(self, file_path, data):
#     with open(file_path, 'wb') as file:  # 'wb' 表示写入二进制文件
#         packed_data = msgpack.packb(data)  # 将数据序列化为 MessagePack 格式
#         file.write(packed_data)
#
# def detecting_initial_config_files(path, filename, data):
#
#     # 使用path和filename创建绝对路径
#     abs_path = os.path.join(path, filename)
#
#     # 如果发现文件缺失会进行创建相应的文件并存入相对的数据
#     if not os.path.exists(abs_path):
#         bin_save_data(abs_path, data)

def main():
    import InitialConfigFolder
    importlib.reload(InitialConfigFolder)
    InitialConfigFolder.Main_program()

    import DependenciesLibs
    importlib.reload(DependenciesLibs)
    DependenciesLibs.Main_program()

    import InitialConfigFile
    importlib.reload(InitialConfigFile)
    InitialConfigFile.Main_program()

    # import LicenseValidator
    # importlib.reload(LicenseValidator)
    # LicenseValidator.Main_program()
    #
    # import Arnold_Magic_Node
    # importlib.reload(Arnold_Magic_Node)
    # Arnold_Magic_Node.Main_program()