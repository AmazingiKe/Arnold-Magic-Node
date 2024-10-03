##############################################################################################
# # ++ 导入所需的库和模块

# 1. Maya 库
import maya.cmds as cmds  # 导入 Maya 的 cmds 模块，用于执行 Maya 命令和操作场景
import maya.OpenMayaUI as omui  # 导入 Maya 的 OpenMayaUI 模块，用于操作 Maya 的用户界面

# 2. 文件与系统操作
import os  # 提供与操作系统交互的功能，如文件路径操作、目录遍历等
import sys  # 提供与 Python 解释器交互的功能，如获取脚本路径、调整模块搜索路径等
import importlib  # 用于动态导入和重新加载模块，支持模块的按需加载
import pathlib  # 提供面向对象的文件系统路径操作，增强对路径的处理能力

# 3. 数据处理
import json  # 用于序列化和反序列化 JSON 数据，方便与外部数据进行交换
import ast  # 用于解析和操作 Python 代码的抽象语法树，适用于代码分析和转换
import msgpack  # 用于高效的二进制序列化和反序列化，比 JSON 更节省空间和更快
from ahocorapy.keywordtree import KeywordTree  # 用于高效的多模式匹配，适合文本搜索和过滤
import numpy as np

# 4. 字符串处理
import re  # 提供正则表达式操作，用于模式匹配、搜索和替换字符串
import difflib  # 用于比较文本差异，生成差异报告或补丁，适合版本控制和文本分析

# 5. 图像处理
import imghdr  # 用于识别图像文件的类型，如 JPEG、PNG、GIF 等
from PIL import Image  # 导入 Pillow 库，用于图像打开、编辑和保存，支持多种图像格式和高级图像处理功能
import cv2

# 6. 时间管理
import time  # 提供时间相关的函数，如时间戳获取、延时操作等
from datetime import datetime  # 提供日期和时间的对象和操作方法，支持更复杂的时间处理

# 7. 网络操作
import webbrowser  # 提供在 Web 浏览器中打开 URL 的功能，支持跨平台操作
import keyboard  # 用于监听和发送键盘事件，适合自动化任务和快捷键实现

# 8. 依赖管理
import DependenciesLibs  # 导入自定义的依赖管理模块，用于加载和初始化项目所需的其他库
DependenciesLibs.importLibs()  # 调用自定义模块中的函数，动态导入和初始化所需的依赖库

# ##############################################################################################








#   路径识别判断的库
class PathDetection(object):
    """
    PathDetection 类用于处理路径检测和内容匹配。
    这个类实现了路径获取、内容检测、数据处理和匹配功能。
    """
    
    def __init__(self):
        self.node_attr = {} # ！此变量是零时变量，用来储存路径等的属性
        self.feedback = FeedbackPrompt() # 错误提示模块

    # 获取路径
    def get_node_path(self, node_name):
        """
        获取节点的文件路径。

        该函数接收一个节点名称（`node_name`），并将节点的文件路径存储在 `self.node_attr` 字典中。
        字典的键是节点名称，值是一个字典，其中包含以下键：
            - 'path'：节点的文件路径

        参数:
            node_name (str): 节点的名称。必须是文件类型节点。

        返回:
            无返回值。函数将节点的文件路径存储在 `self.node_attr` 字典中。
        
        注意:
            - `self.node_attr` 是一个字典，存储节点的属性。
            - 使用 `os.path.normpath` 对文件路径进行规范化，以便在不同操作系统上保持一致性。
        """
        self.node_attr[node_name] = {}
        self.node_attr[node_name]['path'] = os.path.normpath(cmds.getAttr(f"{node_name}.fileTextureName"))

        return self.node_attr

    # 获取对饮节点路径下的内容并且过滤
    def detection_path_content(self, node_name, exclude_list):
        """
        检测节点路径下的文件内容，并过滤文件列表。

        该函数接收一个节点名称（`node_name`）和一个要排除的元素列表（`exclude_list`），
        并返回一个过滤后的文件列表，其中只包含图像文件且不包含要排除的元素。

        参数:
            node_name (str): 节点的名称。必须是文件类型节点。
            exclude_list (list): 要排除的元素列表。

        返回:
            list: 过滤后的文件列表，其中只包含图像文件且不包含 `exclude_list` 中的元素。

        注意:
            - 使用 `os.listdir` 获取节点路径目录下的文件列表。
            - 使用 `imghdr.what` 检查文件是否为图像类型。
            - 使用列表推导式过滤掉包含要排除的元素的字符串。
            - 如果文件没有访问权限，函数将捕获异常，并输出错误信息。
        """

        
        # 获取目录中的文件列表
        dirname_list = os.listdir(os.path.dirname(self.node_attr[node_name]['path']))

        # 储存过滤出来的文件名字变量
        tex_name_list = []
        
        # 遍历文件列表
        for file_name in dirname_list:
            # 构建完整的文件路径
            directory = os.path.dirname(self.node_attr[node_name]['path'])
            file_path = os.path.join(directory, file_name)
            
            # 判断文件是否为图像类型
            try:
                if imghdr.what(file_path):
                    tex_name_list.append(file_name)
            except Exception as e:
                self.feedback.CP(f'{file_name}:此贴图没有权限访问 无法获得更高权限访问 详细报错:[{e}]')
                
        # 使用列表推导式过滤掉包含要排除的元素的字符串
        tex_name_list = [name for name in tex_name_list if all(exclude not in name for exclude in exclude_list)]
        
        return tex_name_list

    # 匹配零时组建数据库的文件
    def process_name_data(self, node_name, tex_name_list, length_weight, format_list, filter_dict, case_sensitive):
        """
        处理文件名并计算相似度。

        该函数接受节点名称、文件名列表、长度权重、格式列表、过滤器字典以及其他过滤器数据，
        用于处理和过滤文件名，并计算源文件名和目标文件名之间的相似度。

        参数:
            node_name (str): 节点的名称。
            tex_name_list (list): 包含文件名的列表。
            length_weight (float): 长度相似度的权重。取值范围应为 [0, 1]。
            format_list (list): 文件格式列表，用于过滤文件名后缀。
            filter_dict (dict): 过滤器字典，包含过滤器名称和值。
            TexFirstFilterData (dict): 第一批过滤器数据。
            TexSoloFilterData (dict): 单个过滤器数据。

        返回:
            dict: 相似度字典，其中键是目标文件名，值是与源文件名的相似度。

        注意:
            - 函数首先根据过滤器字典对文件名列表进行过滤。
            - 接着对源文件名和目标文件名进行处理和切片。
            - 然后使用 `calculate_similarity` 方法计算源文件名和目标文件名之间的相似度。
            - 最终返回一个字典 `similarity_dict`，其中包含源文件名和目标文件名的相似度。

        """
        
        new_file_list = []

        # 1，处理列表，只能是标准的PBR命名等贴图
        for file in tex_name_list:
            # 对于每个文件名，检查是否有任何过滤器的值出现在文件名中
            for filter_name, filter_values in filter_dict.items():
                for value in filter_values:
                    if value.lower() in file.lower():
                        new_file_list.append(file)
                        break  # 如果找到匹配项，则不再继续查找其他过滤器值
                else:
                    continue  # 如果在当前过滤器名称中未找到匹配项，则继续查找下一个过滤器名称
                break  # 如果找到匹配项，则不再继续查找其他过滤器名称

        # 2，进行匹配源名字进行处理
        sl_node_texname = os.path.basename(self.node_attr[node_name]['path'])
        pattern = '|'.join(format_list) # 构建正则表达式，匹配任何格式列表中的格式
        sl_node_texname_pro = re.sub(r'\.(' + pattern + ')$', '', sl_node_texname) # 使用正则表达式进行匹配和替换
        
        # 3，进行匹配名字进行处理
        tex_name_list_pro = self.remove_formats(new_file_list, format_list)
        
        # 4，进行匹配源名字进行切片
        sl_node_texname_dict_pro = {sl_node_texname_pro: sl_node_texname_pro.split('_')}
        sl_node_texname_dict_lastpro = self.match_and_remove_dict(sl_node_texname_dict_pro, filter_dict)
        # 5，进行匹配源名字进行切片    
        tex_name_dict_pro= {key: key.split('_') for key in tex_name_list_pro}
        tex_name_dict_lastpro = self.match_and_remove_dict(tex_name_dict_pro, filter_dict)

        similarity_dict = {}
        # 6。匹配相似度
        self.feedback.CP("===================================匹配相似度=================================")
        for key1, value1 in sl_node_texname_dict_lastpro.items():
            for key2, value2 in tex_name_dict_lastpro.items():
                # 计算相似度
                similarity = self.calculate_similarity(value1, value2, length_weight, case_sensitive)
                similarity_dict[key2] = similarity
                self.feedback.CP(f"匹配源：{key1}，匹配目标：{key2}，相似度：{similarity}")
        
        return similarity_dict
    
    # 判断数据匹配数据
    def determine_connection(self, similarity_dict, auto_max_val, similarity_max, similarity_range, near_one_value):
        """
        判断数据匹配数据，并返回匹配列表。

        该函数接收一个相似度字典（`similarity_dict`）和其他参数，
        根据给定条件判断数据匹配情况，并返回匹配目标的列表。

        参数:
            similarity_dict (dict): 相似度字典，键是目标，值是相似度。
            auto_max_val (bool): 是否自动获取最大相似值。
            similarity_max (float): 用户指定的最大相似值。
            similarity_range (float): 相似度范围，用于过滤匹配目标。
            near_one_value (bool): 是否只考虑接近相似度最大值的匹配目标。

        返回:
            list: 匹配目标列表。

        注意:
            - `similarity_dict` 是一个字典，包含目标和相似度。
            - `auto_max_val` 为 `True` 时，函数会自动获取最大相似值作为阈值，否则使用用户指定的 `similarity_max`。
            - 使用列表推导式过滤匹配目标，根据相似度范围或是否接近最大相似值。
            - 结果通过 `self.feedback.CP` 输出日志信息。
        """
        matching_list = []
        
        # 0. 制作相似度列表
        similarity_list = []
        for key in similarity_dict:
            similarity_list.append(similarity_dict[key])
         
        # 1. 获取最大相似值
        if auto_max_val == True:
            similarity_threshold = max(similarity_list)
        else:
            similarity_threshold = similarity_max
            
        # 2. 过滤匹配目标
        if near_one_value == True:
            filtered_matches = [(target, similarity) for target, similarity in similarity_dict.items() 
                                if similarity >= similarity_threshold]
        else:
            filtered_matches = [(target, similarity) for target, similarity in similarity_dict.items() 
                                if similarity >= similarity_threshold - similarity_range 
                                and similarity <= similarity_threshold + similarity_range]
        

        # 输出匹配结果
        self.feedback.CP("===================================完成匹配列表=================================")
        for target, similarity in filtered_matches:
            matching_list.append(target)
            self.feedback.CP(f"完成匹配| 匹配目标：{target}，相似度：{similarity}")
            
        return matching_list
    
    # 从给定的文件名列表中删除与指定格式列表中任何格式相匹配的部分，并返回新的文件名列表
    def remove_formats(self, file_list, format_list):
        """
        从给定的文件名列表中删除与指定格式列表中任何格式相匹配的部分，并返回新的文件名列表。

        参数：
        file_list (list): 包含文件名的列表。
        format_list (list): 包含要删除的文件格式的列表。

        返回：
        list: 处理后的新文件名列表，其中任何与指定格式列表中的格式匹配的部分都已被删除。
        """
        new_file_list = []  # 创建一个空列表，用于存储处理后的文件名
        pattern = '|'.join(format_list)  # 构建匹配任何格式列表中的格式的正则表达式模式
        for filename in file_list:  # 遍历文件名列表
            new_filename = re.sub(r'\.(' + pattern + ')$', '', filename)  # 使用正则表达式删除与格式列表中任何格式相匹配的部分
            new_file_list.append(new_filename)  # 将处理后的文件名添加到新列表中
            
        return new_file_list  # 返回处理后的新文件名列表
    
    # 计算相似度函数
    def calculate_similarity(self, value1, value2, length_weight, case_sensitive):
        """
        计算两个字符串之间的相似度。

        该函数接收两个字符串（`value1` 和 `value2`）以及一个权重参数 `length_weight`，
        计算两个字符串之间的内容相似度和长度相似度，并返回综合相似度。

        参数:
            value1 (str): 第一个字符串。
            value2 (str): 第二个字符串。
            length_weight (float): 长度相似度的权重。取值范围应为 [0, 1]。

        返回:
            float: 综合相似度。取值范围在 [0, 1] 之间。

        注意:
            - 使用 `difflib.SequenceMatcher` 计算两个字符串之间的内容相似度。
            - 计算长度相似度为两个字符串长度的较小值与较大值的比值。
            - 综合相似度是内容相似度和长度相似度的加权平均。
        """
        # 计算内容相似度
        
        # 将 value1 和 value2 都转换为小写
        if case_sensitive == False :
            value1 = [item.lower() for item in value1]
            value2 = [item.lower() for item in value2]
        
        content_similarity = difflib.SequenceMatcher(None, value1, value2).ratio()
        
        # 计算长度相似度
        length_similarity = min(len(value1), len(value2)) / max(len(value1), len(value2))
        
        # 结合内容相似度和长度相似度计算综合相似度
        similarity = (1 - length_weight) * content_similarity + length_weight * length_similarity
        
        return similarity

    # 从 dict1 中删除与 dict2 中值匹配的元素
    def match_and_remove_dict(self, dict1, dict2):
        """
        从 dict1 中删除与 dict2 中值匹配的元素。

        参数:
            dict1 (dict): 待处理的字典。
            dict2 (dict): 用于比较的字典。

        返回:
            dict: 删除匹配项后的字典 dict1。
        """
        # 遍历 dict1 中的键值对
        for dict1_key in dict1:
            # 遍历 dict1 中每个列表中的元素
            for index, val in enumerate(dict1[dict1_key]):
                # 遍历 dict2 中的键值对
                for dict2_key in dict2:
                    # 检查 dict2 中的值是否与 dict1 中的当前元素匹配
                    result = any(val.upper() == item for item in dict2[dict2_key])
                    if result:
                        # 如果匹配，则删除 dict1 中的当前元素
                        del dict1[dict1_key][index]  # 从 dict1 中删除当前元素
                        break  # 跳出当前循环，继续下一个元素的处理
        # 返回处理后的字典 dict1
        return dict1

    # 从列表中删除与目标字符串匹配的元素
    def remove_matching_elements(self, target_string, list):
        """
        从列表中删除与目标字符串匹配的元素。

        该函数接收一个目标字符串 (`target_string`) 和一个列表 (`list`)，
        并返回一个新的列表，其中不包含与目标字符串匹配的元素。

        参数:
            target_string (str): 目标字符串，用于匹配列表中的元素。
            lst (list): 要进行过滤的列表。

        返回:
            list: 一个新的列表，其中不包含与目标字符串匹配的元素。

        注意:
            - 目标字符串先删除最后一个点 (`.`) 和之后的部分，以去除格式后缀。
            - 使用列表推导式创建一个新的列表，其中不包含与去除格式后的目标字符串相匹配的元素。
        """
        # 从目标字符串中删除最后一个点和之后的部分（去除格式）
        formatted_string = target_string.rsplit('.', 1)[0]
        
        # 使用列表推导式创建一个新的列表，不包含与去除格式后的目标字符串匹配的元素
        new_list = [element for element in list if element != formatted_string]
        
        # 返回新的列表
        return new_list

    # 创建纹理节点并设置文件纹理路径。
    def create_node(self, path, node_list, format_list):
        """
        创建纹理节点并设置文件纹理路径。

        该函数接受一个文件路径、文件名列表和格式列表作为参数，
        创建纹理节点，并根据文件名列表和格式列表在指定路径下查找文件，
        将找到的文件设置为节点的文件纹理。

        参数:
            path (str): 文件路径，用于查找文件。
            node_list (list): 文件名列表，用于创建节点和查找文件。
            format_list (list): 文件格式列表，用于查找文件。

        返回:
            list: 创建的纹理节点列表。

        注意:
            - 函数使用 `cmds.shadingNode` 创建名为 `tex_name` 的文件纹理节点。
            - 在节点创建后，函数根据格式列表在指定路径下查找文件，并将文件路径设置为节点的 `fileTextureName` 属性。
            - 使用 `os.path.exists()` 检查文件是否存在于指定路径。

        """
        # 创建纹理节点列表
        node_name_list = []
        
        # 遍历文件名列表
        for tex_name in node_list:
            # 创建文件纹理节点
            node_name = cmds.shadingNode('file', asTexture=True, name=tex_name)
            # 将节点添加到节点列表中
            node_name_list.append(node_name)
            
            # 遍历格式列表
            for format_name in format_list:
                # 构建文件路径
                file_path = os.path.join(path, tex_name + '.' + format_name)
                
                # 检查文件是否存在
                if os.path.exists(file_path):
                    # 将文件路径设置为节点的 fileTextureName 属性
                    cmds.setAttr(node_name + '.fileTextureName', file_path, type='string')
                    break  # 找到文件后退出循环
        
        # 返回创建的节点列表
        return node_name_list

#   节点处理的库
class NodeProcessor(object):
    def __init__(self):
        self.FP = FeedbackPrompt()
        self.feedback = FeedbackPrompt() # 错误提示模块

    #   对贴图文件的名称进行处理
    def ProcessTextureName(self, TextureName):
        """
        对贴图文件的名称进行处理。

        该函数接受一个贴图文件的路径（`TextureName`），对其名称进行以下处理：
        - 获取贴图文件的基本名称（去除路径部分）。
        - 删除所有标点符号。
        - 将名称转换为大写字母。
        - 返回处理后的贴图名称。

        参数:
            TextureName (str): 贴图文件的完整路径。

        返回:
            str: 处理后的贴图名称，仅包括文件名部分，删除了标点符号，并转换为大写。
        """
        # 获取贴图文件的基本名称（去除路径部分）
        BaseName = os.path.basename(TextureName)

        # 删除所有标点符号
        ProcessedName = re.sub(r'[^\w\s]', '', BaseName)

        # 将名称转换为大写
        ProcessedName = ProcessedName.upper()

        return ProcessedName
    
    #   匹配贴图节点的通道
    def MatchingChannels(self, NodeList, FilterData):
        """
        匹配贴图节点的通道。

        该函数接收一个贴图节点的名称（`NodeName`）和过滤数据（`FilterData`），并执行以下操作：
        1. 获取节点的贴图文件名称并进行处理。
        2. 使用过滤数据匹配贴图名称以确定相应的通道。

        参数:
            NodeName (str): 贴图节点的名称。
            FilterData (dict): 包含通道名称和相关值的过滤数据字典。

        返回:
            str: 匹配的通道名称。如果没有找到匹配项，则返回 None。
        """
        MatchingChannelsDict = {}
        
        # 1. 获取节点的贴图文件名称并进行处理
        for NodeName in NodeList:
            FileTexNameOri = cmds.getAttr(NodeName + '.fileTextureName')
            FileTexNamePro = self.ProcessTextureName(FileTexNameOri)
            MatchingChannels = self.FilterData(FileTexNamePro, FilterData)

            MatchingChannelsDict[NodeName] = MatchingChannels

        # 返回匹配的通道名称
        return MatchingChannelsDict

    #   把名字筛选出正确的通道
    def FilterData(self, NewTexName, FilterData):
        """
        使用Aho-Corasick算法根据通道过滤贴图名称。

        参数：
            NewTexName (str)：处理后的贴图名称。
            FilterData (dict)：包含通道名称和关联值列表的字典。

        返回：
            str：匹配的通道名称；如果没有找到匹配项，则返回None。
        """
        from ahocorapy.keywordtree import KeywordTree

        # 构建关键词到通道的映射
        value_to_channel = {}
        for channel, value_list in FilterData.items():
            for value in value_list:
                value_to_channel[value.lower()] = channel

        # 构建关键词树
        kwtree = KeywordTree(case_insensitive=True)
        for value in value_to_channel.keys():
            kwtree.add(value)
        kwtree.finalize()

        # 在NewTexName中搜索模式
        for keyword, index in kwtree.search_all(NewTexName):
            # 打印match对象，调试用
            # print(f"Match: keyword={keyword}, index={index}")
            matched_value_lower = keyword.lower()
            channel = value_to_channel.get(matched_value_lower)
            if channel:
                return channel  # 返回第一个匹配的通道

        return None  # 未找到匹配项
    
    #   根据给定的优先级列表 PriorityList 重新排序字典 MatchingDict。
    def ReorderdictionaryByPriority(self, MatchingDict, PriorityList=None):
        """
        根据给定的优先级列表 PriorityList 重新排序字典 MatchingDict。

        参数：
        - MatchingDict (dict): 要重新排序的字典，其中键是字符串，值是优先级类别。
        - PriorityList (list): 优先级列表，包含要按照优先级排序的类别。默认为默认优先级列表。

        返回：
        - dict: 一个有序字典，其中键值对按照给定的优先级列表排序。

        函数逻辑：
        1. 初始化一个空的字典 ordered_dict，用于存储按优先级排序的键值对。
        2. 遍历给定的优先级列表 PriorityList。
        3. 对于每个优先级类别，遍历 MatchingDict 字典中的键值对。
        4. 如果字典中的值与当前优先级类别匹配，将键值对添加到 ordered_dict 中。
        5. 返回排序后的有序字典 ordered_dict。
        """
        if PriorityList is None:
            # 默认优先级列表
            PriorityList = [
                'base', 'baseColor', 'diffuseRoughness', 'metalness', 'specular', 'specularColor',
                'specularRoughness', 'specularAnisotropy', 'specularRotation', 'subsurface', 'subsurfaceColor',
                'subsurfaceRadius', 'emission', 'emissionColor', 'opacity', 'normalCamera', 'ao', 'bump',
                'displacement'
            ]
        
        # 创建一个空的有序字典来存储按优先级排序的键值对
        ordered_dict = {}

        # 遍历优先级列表
        for priority in PriorityList:
            # 在字典中查找与优先级匹配的值
            for key, value in MatchingDict.items():
                if value == priority:
                    # 将匹配的键值对添加到有序字典中
                    ordered_dict[key] = value

        # 返回排序后的有序字典
        return ordered_dict

    #   连接并创建处理节点
    def ConnectTexFileNodeToProNode(self, Tex_name, NodeList, InputPort, MatChannel, InputPortList=None, OutputPortList=None):
        """
        此函数用于将纹理文件节点连接到提供的节点列表，并将提供的输入端口和材质通道与这些节点关联。

        参数:
        Tex_name (str): 纹理文件节点的名称。
        NodeList (list of str): 一个包含节点类型的列表，用于创建并连接到纹理文件节点的节点。
        InputPort (str): 第一个节点的输入端口。
        MatChannel (str): 材质通道，用于确定纹理文件节点的输出端口（'outColor' 或 'outAlpha'）。
        InputPortList (list of str, optional): 输入端口的列表。如果未提供，则默认为 ["input", "passthrough"]。
        OutputPortList (list of str, optional): 输出端口的列表。如果未提供，则默认为 ["outColor", "outAlpha", "outValue", "outTransparency", "outColorR", "outColorG", "outColorB"]。

        返回:
        str: 已创建的最后一个节点的名称。

        过程:
        - 根据提供的材质通道确定纹理文件节点的输出端口 ('outColor' 或 'outAlpha')。
        - 使用节点列表中的第一个节点创建并连接到纹理文件节点。
        - 如果连接不成功，则在提供的输入端口列表和输出端口列表之间进行尝试。
        - 遍历节点列表，为每个节点创建并将其连接到先前的节点。
        - 返回最后创建的节点名称。
        
        注意:
        - 当输入的材质通道未在定义的列表中找到时，会引发 ValueError 异常。
        - 在尝试连接节点时，可能会发生异常。如果发生异常，会在尝试列表中进行循环尝试。
        """
        # 定义灰色和彩色列表
        GraysList = ["base", 'diffuseRoughness', 'metalness', 'specularRoughness', 'subsurface', 'emission', 'ao', 'bump', 'displacement']
        ColorList = ['baseColor', 'specularColor', 'subsurfaceColor', 'subsurfaceRadius', 'emissionColor', 'opacity', 'normalCamera']

        # 如果没有提供输入端口列表，则设置默认值
        if InputPortList is None:
            InputPortList = ["input", "passthrough"]

        if OutputPortList is None:
            OutputPortList = ["outColor", "outAlpha", "outValue", "outTransparency", "outColorR", "outColorG", "outColorB"]

        # 根据材质通道确定纹理文件节点的输出端口
        if MatChannel in ColorList:
            TexFileOutPort = 'outColor'
        elif MatChannel in GraysList:
            TexFileOutPort = 'outAlpha'


        # 从NodeList中创建第一个节点，并将其连接到纹理文件节点
        FirstNodeType = NodeList[0]
        FirstNode = cmds.createNode(FirstNodeType, name=f"{Tex_name}_{FirstNodeType}")
        
        try:
            # 将纹理文件节点连接到第一个节点
            if MatChannel in ColorList:
                self.NodeConnect(Tex_name, TexFileOutPort, FirstNode, InputPort)
            elif MatChannel in GraysList:
                for Color in ['R', 'G', 'B']:
                    self.NodeConnect(Tex_name, TexFileOutPort, FirstNode, InputPort + Color)
        except:
            for InputPort in InputPortList:
                for OutProt in OutputPortList:
                    try:
                        self.NodeConnect(Tex_name, OutProt, FirstNode, InputPort)
                        break              
                    except:
                        pass

        PreviousNode = FirstNode

        # 遍历NodeList进行节点的创建和连接
        for index in range(1, len(NodeList)):

            CurrentNodeType = NodeList[index]

            # 创建当前节点
            CurrentNode = cmds.createNode(CurrentNodeType, name=f"{Tex_name}_{CurrentNodeType}")
            
            for InputPort in InputPortList:
                for OutProt in OutputPortList:
                    try:
                        self.NodeConnect(PreviousNode, OutProt, CurrentNode, InputPort)
                        break
                    except:
                        pass

            PreviousNode = CurrentNode

        return PreviousNode
    
    #   连接到材质球。此函数根据匹配字典和最后节点字典，将节点与材质球连接。
    def ConnectToMaterial(self, MatchingDict, LastNodeDict, ProcessingNodeData, MaterialName=None, OutputPortList=None, DisplacementShader=None):
        """
        连接到材质球。此函数根据匹配字典和最后节点字典，将节点与材质球连接。
        
        参数：
        - MatchingDict (dict): 节点名称与材质通道的映射字典。
        - LastNodeDict (dict): 节点名称与节点对象的映射字典。
        - ProcessingNodeData (dict): 处理节点数据。
        - MaterialName (str): 材质球名称（可选）。
        - OutputPortList (list): 输出端口列表（可选）。
        - DisplacementShader (str): 置换着色器名称（可选）。

        返回：
        无
        """



        # 如果没有提供 OutputPortList，则使用默认值
        if OutputPortList is None:
            OutputPortList = ["outColor", "outAlpha", "outValue", "outTransparency", "outColorR", "outColorG", "outColorB", "displacement"]
            
        def ContToNode(Node, NodeName, NodeChannel):
            """
            将一个节点的输出端口连接到另一个节点的输入端口。
            
            参数：
            - Node (str): 节点名称。
            - NodeName (str): 目标节点名称。
            - NodeChannel (str): 目标节点的通道。
            """
            for OutPort in OutputPortList:
                try:
                    # 尝试连接节点
                    self.NodeConnect(Node, OutPort, NodeName, NodeChannel)
                    break
                except Exception as e:
                    # 如果连接失败，继续尝试下一个端口
                    pass
            
        # 初始化 normal map 节点为 None
        aiNormalMap = None

        # 遍历 MatchingDict 中的节点名称和材质通道
        for NodeName, MatChannel in MatchingDict.items():

            # 处理 normalCamera 通道
            if MatChannel == "normalCamera":
                # 创建 aiNormalMap 节点
                aiNormalMap = cmds.createNode("aiNormalMap", name=NodeName + "aiNormalMap")
                
                # 尝试连接 aiNormalMap 的输入端口
                try:
                    ContToNode(LastNodeDict[self.FindKeyByChannel(MatchingDict, 'normalCamera')], aiNormalMap, "input")
                except:
                    ContToNode(NodeName, aiNormalMap, "input")
                
                # 将 aiNormalMap 连接到材质球的 normalCamera 通道
                ContToNode(aiNormalMap, MaterialName, 'normalCamera')

            # 处理 AO 通道
            elif MatChannel == "ao":
                if 'baseColor' in MatchingDict.values():
                    # 创建 aiMultiply 节点
                    aiMultiply = cmds.createNode("aiMultiply", name=NodeName + "_aiMultiply")
                    
                    # 连接 aiMultiply 的输入端口
                    try:
                        ContToNode(LastNodeDict[self.FindKeyByChannel(MatchingDict, 'baseColor')], aiMultiply, "input1")
                    except:
                        ContToNode(self.FindKeyByChannel(MatchingDict, 'baseColor'), aiMultiply, "input1")
                    try:
                        ContToNode(LastNodeDict[NodeName], aiMultiply, "input2")
                    except:
                        ContToNode(NodeName, aiMultiply, "input2")
                    
                    # 将 aiMultiply 连接到材质球的 baseColor 通道
                    ContToNode(aiMultiply, MaterialName, 'baseColor')
                    
            # 处理 Bump 通道
            elif MatChannel == "bump":
                # 创建 aiBump2d 节点
                aiBump2d = cmds.createNode("aiBump2d", name=NodeName + "_aiBump2d")
                
                # 根据是否存在 aiNormalMap，连接相应的通道
                if aiNormalMap == None:
                    try: 
                        ContToNode(LastNodeDict[self.FindKeyByChannel(MatchingDict, 'Bump')], aiBump2d, 'bumpMap')
                    except Exception as e:
                        ContToNode(self.FindKeyByChannel(MatchingDict, 'Bump'), aiBump2d, 'bumpMap')
                    ContToNode(aiBump2d, MaterialName, 'normalCamera')
                else:
                    try:
                        ContToNode(LastNodeDict[self.FindKeyByChannel(MatchingDict, 'Bump')], aiBump2d, 'bumpMap')
                    except Exception as e:
                        ContToNode(self.FindKeyByChannel(MatchingDict, 'Bump'), aiBump2d, 'bumpMap')
                        
                    ContToNode(aiBump2d, aiNormalMap, 'normal')
                
            # 处理 Displacement 通道
            elif MatChannel == "displacement":
                # 创建 displacementShader 节点
                displacementShader = cmds.createNode("displacementShader", name=NodeName + "displacementShader")
                
                # 将 displacementShader 连接到材质球的 Displacement 通道
                try:
                    ContToNode(LastNodeDict[self.FindKeyByChannel(MatchingDict, 'Displacement')], displacementShader, "displacement")
                except Exception as e:
                    ContToNode(self.FindKeyByChannel(MatchingDict, 'Displacement'), displacementShader, "displacement")
                    
                # 如果提供了 DisplacementShader，则将 displacementShader 连接到 DisplacementShader 的 displacementShader 通道
                if DisplacementShader is not None:
                    ContToNode(displacementShader, DisplacementShader, "displacementShader")

            # 处理其他通道
            else:
                try:
                    # 尝试将节点连接到材质球的指定通道
                    ContToNode(LastNodeDict[NodeName], MaterialName, MatChannel)
                except:
                    ContToNode(NodeName, MaterialName, MatChannel)

            # self.feedback.CP('{}, {}'.format(NodeName, MatChannel))

    #   在给定的字典中查找与指定通道名称匹配的键
    def FindKeyByChannel(self, texture_dict, search_channel):
        """
        在给定的字典中查找与指定通道名称匹配的键。

        参数:
            texture_dict (dict): 包含纹理文件节点名称和通道名称的字典。
            search_channel (str): 要寻找的通道名称。

        返回:
            str 或 None: 如果找到匹配的键，则返回纹理文件节点名称；如果没有找到匹配项，则返回 None。
        """
        # 遍历字典的键值对
        for key, value in texture_dict.items():
            # 如果值与给定的通道名称匹配
            if value == search_channel:
                # 返回匹配的键
                return key
        
        # 如果没有找到匹配项，返回 None
        return None
    
    #   统一 UV 节点
    def unify_uv_node(self, node_list, uv_list = None):     
        """
        统一 UV 节点。

        该函数接受一个节点列表 (`node_list`)，然后删除旧的 UV 节点，
        创建一个新的 UV 节点，并将新的 UV 节点与节点列表中的每个文件纹理节点连接。

        参数:
            node_list (list): 要连接到新的 UV 节点的文件纹理节点列表。
            uv_list (list, optional): 要删除的旧的 UV 节点列表。如果未提供，则跳过删除步骤。

        返回:
            无返回值。该函数直接对节点进行操作。

        注意:
            - 函数首先删除旧的 UV 节点（如果提供了 `uv_list`）。
            - 然后创建一个新的 UV 节点 (`place2dTexture`)。
            - 将新的 UV 节点的属性与节点列表中的每个文件纹理节点的对应属性连接。
            - 使用预定义的属性列表 `connect_plug` 列出要连接的属性，包括例如 `coverage`、`translateFrame` 等。
            - 特殊处理 'outUV' 和 'outUvFilterSize' 属性，它们需要单独连接。

        """
        # 创建预定义的连接属性列表
        connect_plug = [
            'coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV',
            'stagger', 'wrapU', 'wrapV', 'repeatUV', 'offset', 'rotateUV',
            'noiseUV', 'vertexUvOne', 'vertexUvTwo', 'vertexUvThree',
            'vertexCameraOne'
                        ]

        # 如果提供了 uv_list，则删除旧的 UV 节点
        if uv_list is not None:
            try:
                for uv_node in uv_list:
                    cmds.delete(uv_node)
            except:
                pass
        
        # 创建一个新的 UV 节点
        new_uv_node = cmds.shadingNode('place2dTexture', at=True, name='place2dTexture')
        
        # 使用新的 UV 节点与节点列表中的每个文件纹理节点进行连接
        for file_tex_node in node_list:
            for plug in connect_plug:
                self.NodeConnect(new_uv_node, plug, file_tex_node, plug, True)

            # 单独连接 'outUV' 和 'outUvFilterSize' 属性
            self.NodeConnect(new_uv_node, 'outUV', file_tex_node, 'uvCoord', True)
            self.NodeConnect(new_uv_node, 'outUvFilterSize', file_tex_node, 'uvFilterSize', True)

    #   自动连接节点函数
    def AutoNodeConnect(self, SlNode, MatName, FilterData, ProcessingNodeData, ContOptions, Auto_Node_Connection_Options):
        """
        自动连接贴图至材质球。（包括处理节点的连接）
        
        参数：
        - SlNode: 选择的节点列表
        - MatName: 材质名称
        - FilterData: 优先顺序排名的字典
        - ProcessingNodeData: 相应贴图节点的参数
        - ContOptions: 相应贴图是否要连接的参数
        - Auto_Node_Connection_Options: 相应贴图是否要连接相应的节点

        返回：
        无
        """
        # 3.重新排序贴图顺序
        MatchingDict = self.ReorderdictionaryByPriority(self.MatchingChannels(SlNode['file'], FilterData))


        LastNodeDict = {}
    
        # 4.连接并创建相应的处理节点
        for NodeName, MatChannel in MatchingDict.items():

            if Auto_Node_Connection_Options [MatChannel]== False:
                continue

            LastNodeDict[NodeName] = self.ConnectTexFileNodeToProNode(NodeName,
                                                                        ProcessingNodeData[MatChannel]["NodeList"],
                                                                        ProcessingNodeData[MatChannel]["InputPort"],
                                                                        MatChannel)

        # 5.连接至材质球
        if 'shadingEngine' in SlNode:
            DisplacementShader = SlNode['shadingEngine'][0]
        else:
            DisplacementShader = None

        self.ConnectToMaterial(MatchingDict, LastNodeDict, ProcessingNodeData, MatName, DisplacementShader= DisplacementShader)
        
        self.feedback.CP(f'完成{MatName}材质球连接')
    
    #   自动匹配色彩空间并设置
    def AutoSetTexColorSpace(self, AutoSetColorSpaceConfig,  NodeList, FilterData, MatchingChannel = None):
        """
        输入节点自动匹配色彩空间
        
        
        参数:
        NodeList -- 包含节点名称的列表
        FilterData -- 用于过滤节点的相关数据

        
        """


        # 1, 使用MatchingChannels函数匹配通道
        if MatchingChannel == None:
            MatchingChannel = self.MatchingChannels(NodeList, FilterData)
        
        # 2，进行设置色彩空间相关设置
        for NodeNmae, Channel in MatchingChannel.items():
            if Channel in AutoSetColorSpaceConfig:
                TexColorSpace = AutoSetColorSpaceConfig[Channel]
                
                # 设置色彩空间
                cmds.setAttr(NodeNmae + '.colorSpace', TexColorSpace, type='string')
                
                # 把alpha是亮度还有忽略色彩空间规则开启
                cmds.setAttr(NodeNmae + '.alphaIsLuminance', 1)
                cmds.setAttr(NodeNmae + '.ignoreColorSpaceFileRules', 1)
                
                self.feedback.CP(f"{NodeNmae}节点设置为 <{TexColorSpace}> 色彩空间")
                
    #   连接节点属性
    def NodeConnect(self, source_node, source_attr, target_node, target_attr, force = True):
        """
        连接节点属性。

        该函数将源节点的指定属性 (`source_attr`) 连接到目标节点的指定属性 (`target_attr`)。
        如果目标属性已经被其他属性连接，则可以通过设置 `force` 参数为 True 来强制连接。

        参数:
            source_node (str): 源节点的名称。
            source_attr (str): 源节点的属性名称。
            target_node (str): 目标节点的名称。
            target_attr (str): 目标节点的属性名称。
            force (bool, optional): 是否强制连接。如果为 True，则即使目标属性已经连接到其他属性，也会强制连接。默认为 True。

        返回:
            无返回值。该函数直接对节点进行连接操作。
        """
        # 使用 Maya cmds.connectAttr() 函数连接源节点和目标节点的属性
        cmds.connectAttr(source_node+ '.'+ source_attr, target_node+ '.'+ target_attr, f=force)

#   获取节点数据的库
class GetNodeData():
    
    def __init__(self):

        self.feedback = FeedbackPrompt() # 错误提示模块
    
    #   获取指定类型的所有节点名称。
    def GetAllNodeData(self, NodeTypes):
        """
        获取指定类型的所有节点名称。

        参数:
        NodeTypes (list): 包含节点类型的列表，例如 ['lambert', 'phong', 'blinn']。

        返回:
        list: 包含所有符合条件的节点名称的列表。
        """
        #   创建一个空列表来存储过滤后的节点
        NodeNameList = []

        #   遍历所有的材质类型并获取对应的节点
        for NodeType in NodeTypes:
            nodes = cmds.ls(type=NodeType)
            if nodes:
                NodeNameList.extend(nodes)

        return NodeNameList
    
    #   上游节点查找器
    def UpStreamNodeFinder(self, Node, NodeTypes):
        """查找当前选择的材质球连接的所有特定类型（如file类型）节点。

        参数:
            Node: 要查找的起始节点的名称（字符串）。
            NodeTypes: 要查找的节点类型列表（字符串列表），例如["file"]。

        返回:
            finder_list: 一个包含所有找到的特定类型节点的列表。
        """
        finder_list = []

        def find_nodes_same_type(Node, NodeTypes):
            """递归查找给定节点的所有指定类型节点。

            参数:
                Node: 当前正在检查的节点的名称（字符串）。
                NodeTypes: 要查找的节点类型列表（字符串列表）。

            返回:
                found_nodes: 一个包含当前节点及其上游连接中所有找到的特定类型节点的列表。
            """
            found_nodes = []
            # 获取当前节点的所有上游连接节点
            connections = cmds.listConnections(Node, s=True, d=False) or []

            for conn in connections:
                # 检查连接节点的类型
                if cmds.nodeType(conn) in NodeTypes:  # 支持多个节点类型
                    found_nodes.append(conn)
                else:
                    # 如果连接节点不是目标类型，继续递归查找其上游连接
                    found_nodes.extend(find_nodes_same_type(conn, NodeTypes))

            return found_nodes

        # 获取传入节点的所有上游连接节点
        connections = cmds.listConnections(Node, s=True, d=False) or []

        for conn in connections:
            # 对每个上游连接节点进行递归查找
            
            #   如果第上游的第一个节点是相同类型的节点就不用递归去检查
            if cmds.nodeType(conn) in NodeTypes:
                finder_list.append(conn)
            else:
                file_nodes = find_nodes_same_type(conn, NodeTypes)
                finder_list.extend(file_nodes)
                
        return finder_list

    #   批量获取file节点的路径
    def GetFileNodePath(self, NodeList):
        """
        批量获取file节点的路径。

        参数:
            NodeList (list): 包含节点名称的列表，这些节点应为 'file' 类型。

        返回:
            dict: 一个字典，键为节点名称，值为对应的文件路径。
        """
        
        NodePathDict = {}  # 创建一个空字典，用于存储节点及其对应的文件路径
        
        # 遍历提供的节点列表
        for node in NodeList:
            # 获取当前 file 节点的 fileTextureName 属性的值，即文件路径
            file_path = cmds.getAttr(node + '.fileTextureName')
            
            # 将节点名称和对应的文件路径添加到字典中
            NodePathDict[node] = file_path

        # 返回包含所有节点及其文件路径的字典
        return NodePathDict

    #   获取所有材质节点的详细信息，包括路径、加载状态、文件名、格式、引用次数、文件大小和分辨率
    def GetMterialNodeAllInfo(self , __material_node_tyoes_list = None):

        """
        获取所有材质节点的详细信息，包括路径、加载状态、文件名、格式、引用次数、文件大小和分辨率。

        参数:
        - __material_node_tyoes_list: 列表，包含要查找的材质节点类型。如果未提供，将使用默认的材质节点类型列表。

        返回:
        - MterialNodeAllInfoDict: 字典，包含每个材质节点及其相关的详细信息。
        """

        if __material_node_tyoes_list == None:
            __material_node_tyoes_list = ['aiStandardSurface', 'aiStandardVolume', 'aiStandardHair' ,
                                          'blinn' ,'phongE', 'phong', 'blinn', 'lambert', 'standardSurface']

        #   获取所有的材质节点名称
        MaterialNodeNameList = self.GetAllNodeData(__material_node_tyoes_list)

        MterialNodeAllInfoDict = {}

        for matName in MaterialNodeNameList:
            #   使用材质名称创建一个口字典
            MterialNodeAllInfoDict[matName] = {}

            UpStreamNodeList = self.UpStreamNodeFinder(matName, 'file')

            for nodeNmae in UpStreamNodeList:
                #   使用节点名称创建一个口字典
                MterialNodeAllInfoDict[matName][nodeNmae] = {}

                #   获取路径
                nodePath = cmds.getAttr(nodeNmae + '.fileTextureName')
                MterialNodeAllInfoDict[matName][nodeNmae]["Path"] = nodePath

                #   获取连接状态
                MterialNodeAllInfoDict[matName][nodeNmae]["isLoaded"] = os.path.exists(nodePath)

                #   获取文件名
                fileName = os.path.basename(nodePath)
                MterialNodeAllInfoDict[matName][nodeNmae]["fileName"] = fileName

                #   获取格式名称
                Format = pathlib.Path(nodePath).suffix.replace('.', '')
                MterialNodeAllInfoDict[matName][nodeNmae]["Format"] = Format

                #   获取贴图引用次数
                usageCountList = cmds.listConnections(nodeNmae, source=False, destination=True)
                MterialNodeAllInfoDict[matName][nodeNmae]["usageCount"] = len(usageCountList)

                #   获取文件大小
                try:
                    Size = os.path.getsize(nodePath)  # 通过 os 获取文件大小
                    Size = Size / (1024 * 1024)  # 字节换算为MB
                except IOError as e:
                    # self.feedback.CP(f'因{nodeNmae}无法连接，所以无法读取大小')
                    Size = False

                MterialNodeAllInfoDict[matName][nodeNmae]["Size"] = Size

                #   初始化分辨率
                width, height = 0, 0
                #   获取分辨率
                try:
                    #   使用 Pillow 读取图像
                    with Image.open(nodePath) as image:
                        #   获取像素大小
                        width, height = image.size
                except :

                    #   如果无法获取分辨率大小，尝试用其他库去获取
                    try:
                        if Format == 'exr':
                            exr_file = pyexr.open(nodePath)
                            # 获取图像的宽度和高度
                            width = exr_file.width
                            height = exr_file.height
                    except:
                        # self.feedback.CP(f'因{nodeNmae}无法读取，所以无法读取像素大小')
                        width, height = 0, 0

                MterialNodeAllInfoDict[matName][nodeNmae]["Dimensions"] = [width, height]

                MterialNodeAllInfoDict[matName][nodeNmae]["Dimensions"]




        # indent = 0
        # def print_dict(d, indent=0):
        #     for key, value in d.items():
        #         print(' ' * indent + str(key) + ':', end=' ')
        #         if isinstance(value, dict):
        #             print()  # 打印键后换行
        #             print_dict(value, indent + 4)  # 递归调用增加缩进
        #         else:
        #             print(value)  # 打印值
        #
        # # 调用打印函数
        # print_dict(MterialNodeAllInfoDict)

        return MterialNodeAllInfoDict

    #   查找未列出的纹理文件
    def FindUnlistedTextures(self, TexturesList):
        """
        查找未列出的纹理文件。

        参数:
        - TexturesList: 列表，包含当前节点使用的所有纹理文件的文件名。

        返回:
        - missing_elements: 集合，包含all_file_list中存在但TexturesList中缺少的文件名。
        """

        # 获取所有节点中的文件名列表，参数 ['file'] 指定从节点中提取文件类型的数据
        all_file_list = self.GetAllNodeData(['file'])
        # 转换为集合，便于集合操作
        textures_set = set(TexturesList)
        all_files_set = set(all_file_list)

        # 找出all_file_list中有，但TexturesList中没有的元素
        missing_elements = all_files_set - textures_set

        return missing_elements

    #   获取贴图的详细信息，包括路径、加载状态、文件名、格式、引用次数、文件大小和分辨率
    def GetTexturesNodeAllInfo(self, TexturesList):

        TexturesNodeAllInfoDict = {}

        TexturesNodeAllInfoDict['Unlisted Textures'] = {}

        for texName in TexturesList:
            #   使用节点名称创建一个口字典

            TexturesNodeAllInfoDict['Unlisted Textures'][texName] = {}

            #   获取路径
            nodePath = cmds.getAttr(texName + '.fileTextureName')
            TexturesNodeAllInfoDict['Unlisted Textures'][texName]["Path"] = nodePath

            #   获取连接状态
            TexturesNodeAllInfoDict['Unlisted Textures'][texName]["isLoaded"] = os.path.exists(nodePath)

            #   获取文件名
            fileName = os.path.basename(nodePath)
            fileName_Pro = fileName.rsplit('.', 1)[0]  # 去掉扩展名
            TexturesNodeAllInfoDict['Unlisted Textures'][texName]["fileName"] = fileName_Pro


            #   获取格式名称
            Format = pathlib.Path(nodePath).suffix.replace('.', '')
            TexturesNodeAllInfoDict['Unlisted Textures'][texName]["Format"] = Format

            #   获取贴图引用次数
            usageCountList = cmds.listConnections(texName, source=False, destination=True)

            TexturesNodeAllInfoDict['Unlisted Textures'][texName]["usageCount"] = len(usageCountList)

            #   获取文件大小
            try:
                Size = os.path.getsize(nodePath)  # 通过 os 获取文件大小
                Size = Size / (1024 * 1024)  # 字节换算为MB
            except IOError as e:
                # self.feedback.CP(f'因{nodeNmae}无法连接，所以无法读取大小')
                Size = False

            TexturesNodeAllInfoDict['Unlisted Textures'][texName]["Size"] = Size

            #   初始化分辨率
            width, height = 0, 0
            #   获取分辨率
            try:
                #   使用 Pillow 读取图像
                with Image.open(nodePath) as image:
                    #   获取像素大小
                    width, height = image.size
            except:

                #   如果无法获取分辨率大小，尝试用其他库去获取
                try:
                    if Format == 'exr':
                        exr_file = pyexr.open(nodePath)
                        # 获取图像的宽度和高度
                        width = exr_file.width
                        height = exr_file.height
                except:
                    # self.feedback.CP(f'因{nodeNmae}无法读取，所以无法读取像素大小')
                    width, height = 0, 0

            TexturesNodeAllInfoDict['Unlisted Textures'][texName]["Dimensions"] = [width, height]

        return TexturesNodeAllInfoDict

    #   更新数据列表中的分辨率等的数据
    def TM_StickerUpdateStatusDict(self, target_diact, update_dict):

        # 使用前一定要先更改一次路径先
        for nodeName, matName in target_diact.items():

            nodePath = update_dict[matName][nodeName]['Path']

            #   获取连接状态
            update_dict[matName][nodeName]["isLoaded"] = os.path.exists(nodePath)

            #   获取格式名称
            Format = pathlib.Path(nodePath).suffix.replace('.', '')
            update_dict[matName][nodeName]["Format"] = Format

            #   获取文件大小
            try:
                Size = os.path.getsize(nodePath)  # 通过 os 获取文件大小
                Size = Size / (1024 * 1024)  # 字节换算为MB
            except IOError as e:
                # self.feedback.CP(f'因{nodeNmae}无法连接，所以无法读取大小')
                Size = False

            update_dict[matName][nodeName]["Size"] = Size

            #   初始化分辨率
            width, height = 0, 0
            #   获取分辨率
            try:
                #   使用 Pillow 读取图像
                with Image.open(nodePath) as image:
                    #   获取像素大小
                    width, height = image.size
            except:

                #   如果无法获取分辨率大小，尝试用其他库去获取
                try:
                    if Format == 'exr':
                        exr_file = pyexr.open(nodePath)
                        # 获取图像的宽度和高度
                        width = exr_file.width
                        height = exr_file.height
                except:
                    # self.feedback.CP(f'因{nodeNmae}无法读取，所以无法读取像素大小')
                    width, height = 0, 0

            update_dict[matName][nodeName]["Dimensions"] = [width, height]


        return update_dict

    # 获取指定路径下的内容
    def GetDirectoryContentsWithOptions(self, Path, SearchSubfolders=True, MultipleSubfolderSearch=True, Extensions=None):
        """
        获取指定路径下的内容，并根据选项决定是否搜索子文件夹。

        参数：
        - Path: 要搜索的目录路径。
        - SearchSubfolders (bool): 是否搜索子文件夹，默认值为True。
        - MultipleSubfolderSearch (bool): 是否搜索多层子文件夹，默认值为True。
            - 注意：只有当SearchSubfolders为True时，此参数才有效。
        - Extensions (list): 要包含的文件扩展名列表，例如 ['.txt', '.jpg']，默认值为None，表示不进行扩展名过滤。

        返回：
        - ContentsDict (dict): 包含目录内容的字典，键为文件的完整路径，值为其名称。
        """

        ContentsDict = {}

        if Extensions:
            # 将扩展名转换为小写集合，便于快速查找
            Extensions = set(ext.lower() for ext in Extensions)
        else:
            Extensions = None

        # 如果MultipleSubfolderSearch开启，确保SearchSubfolders也开启
        if MultipleSubfolderSearch and not SearchSubfolders:
            # 如果未开启搜索子文件夹，但开启了多层子文件夹搜索，则关闭多层搜索
            MultipleSubfolderSearch = False

        def scan_directory(path, level):
            try:
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_file():
                            if Extensions:
                                # 获取文件的扩展名并转换为小写
                                ext = os.path.splitext(entry.name)[1].lower()
                                if ext not in Extensions:
                                    continue  # 跳过不符合扩展名的文件
                            ContentsDict[entry.name] = entry.path
                        elif entry.is_dir():
                            ContentsDict[entry.name] = entry.path
                            if SearchSubfolders:
                                if MultipleSubfolderSearch or level == 0:
                                    # 递归扫描子目录
                                    scan_directory(entry.path, level + 1)
            except PermissionError:
                pass  # 忽略没有权限的文件夹

        # 标准化初始路径
        Path = os.path.normpath(Path)
        scan_directory(Path, level=0)

        return ContentsDict  # 返回包含内容路径和名称的字典

#   专门负责各种数据的处理
class DataProcessor():
    def __init__(self):
        self.feedback = FeedbackPrompt() # 错误提示模块

        # 插件路径
        Script_path = os.path.join(os.path.dirname(__file__))

        # 实例化数据管理类
        dataM = DataManager()



        # 获取语言设置
        language_config = dataM.ascii_load_data(os.path.join(Script_path, 'Datas', 'settings', 'language_config.json'))['language_config']
        # 获取语言
        self.language = dataM.ascii_load_data(os.path.join(Script_path, 'Datas', 'languages', f'{language_config}.json'))['ArnoldMagicNodeLibs']['DataP']


    def SimpleSearchAndReplaceData(self, OriginalContent, SearchContent, ReplaceContent, case_sensitive=True, use_regex=False):
        # 检查是否输入为字符串类型
        if not isinstance(OriginalContent, str) or not isinstance(SearchContent, str) or not isinstance(ReplaceContent,
                                                                                                        str):
            self.feedback.CP(self.language['SSARD']['01'])
            return False

        # 如果使用正则表达式
        if use_regex:
            # 根据是否区分大小写进行匹配
            if case_sensitive:
                flags = re.IGNORECASE
            else:
                flags = 0

            try:
                result = re.sub(SearchContent, ReplaceContent, OriginalContent, flags=flags)
                return result
            except re.error as e:
                self.feedback.CP(f"{self.language['SSARD']['02']}{e}")
                return False
        else:
            # 普通字符串替换，根据是否区分大小写处理
            if case_sensitive:
                # 如果不区分大小写
                result = re.sub(re.escape(SearchContent), ReplaceContent, OriginalContent, flags=re.IGNORECASE)
                return result
            else:
                # 普通的字符串替换（区分大小写）
                result = OriginalContent.replace(SearchContent, ReplaceContent)
                return result

    def filter_material_textures(self, filtered_textures, data):
        """
        过滤 self.MterialNodeAllInfoDict 中的纹理数据，并返回包含符合条件的纹理信息的字典。

        参数:
        - filtered_textures: 包含需要保留的纹理的集合或列表。

        返回:
        - filtered_data: 一个字典，其中包含所有符合条件的纹理数据，以材质为键，过滤后的纹理信息为值。
        """
        filtered_data = {}
        for material, textures in data.items():
            # 使用传入的 filtered_textures 而不是 target_list
            filtered_texture_data = {texture: details for texture, details in textures.items() if
                                     texture in filtered_textures}
            if filtered_texture_data:
                filtered_data[material] = filtered_texture_data
        return filtered_data

    def remove_duplicate_keys(self, data):
        """
        移除给定字典中所有子字典里重复的键。

        参数:
        data (dict): 包含多个子字典的父字典，其中每个子字典可能包含相同的键。

        返回:
        dict: 处理后的字典，其中重复的键已被删除。
        """

        # 用于跟踪已经遇到的子字典键的集合
        keys_to_check = set()

        # 遍历父字典中的每个键，即每个子字典的名字
        for parent_key in list(data.keys()):
            sub_dict = data[parent_key]  # 获取当前子字典

            # 遍历子字典中的每个键
            for key in list(sub_dict.keys()):
                if key in keys_to_check:
                    # 如果当前键已经在 keys_to_check 集合中存在
                    # 删除该子字典中的此键，因为它是重复的
                    del sub_dict[key]
                else:
                    # 如果当前键不在 keys_to_check 集合中
                    # 将此键加入集合，表示该键已经出现过
                    keys_to_check.add(key)

        # 返回处理后的字典，重复键已被移除
        return data

    # 使用Aho-Corasick算法在search_content的键中搜索target_dict的键
    def searchKeysInDictUsingAhoCorapy(self, target_dict, search_content, ignore_case = False):
        """
        使用Aho-Corasick算法在search_content的键中搜索target_dict的键。
        如果找到匹配项，打印出search_content中的匹配键。

        参数：
        - target_dict: dict，包含要搜索的键
        - search_content: dict，其键将被用于搜索匹配
        - ignore_case: bool，默认为False，是否忽略大小写
        """
        # 根据ignore_case参数设置是否区分大小写
        kwtree = KeywordTree(case_insensitive=ignore_case)

        # 匹配完后正确的路径 字典
        correct_path_dictionary = {}

        # 将target_dict的键添加到关键字树中
        for key in target_dict.keys():
            kwtree.add(key)
        kwtree.finalize()

        # 在search_content的键中进行搜索
        for content_key in search_content.keys():
            matches = kwtree.search_all(content_key)
            for match in matches:
                self.feedback.CP(f'{content_key}成功匹配 -> {search_content[content_key]}')

                correct_path_dictionary[content_key] = search_content[content_key] # 路径

                break  # 找到第一个匹配项后停止对该键的搜索

        return correct_path_dictionary

# 专门用来处理图像
class ImageProcessor():
    def __init__(self):
        self.feedback = FeedbackPrompt() # 错误提示模块

        # 插件路径
        Script_path = os.path.join(os.path.dirname(__file__))

        # 实例化数据管理类
        dataM = DataManager()



        # 获取语言设置
        language_config = dataM.ascii_load_data(os.path.join(Script_path, 'Datas', 'settings', 'language_config.json'))['language_config']
        # 获取语言
        self.language = dataM.ascii_load_data(os.path.join(Script_path, 'Datas', 'languages', f'{language_config}.json'))['ArnoldMagicNodeLibs']

    def resize_image(self, input_path, output_path, scale_percent=100, resample_mode='1'):
        """
        缩放图片
        参数：
            input_path (str): 输入图片的路径
            output_path (str): 输出图片的路径
            scale_percent (int): 缩放比例（默认100%，不缩放）
            resample_mode (str): 重采样模式，默认使用cv2.INTER_LINEAR
        返回：
            None
        """

        # 检查缩放比例是否合法
        if scale_percent <= 0 or scale_percent > 100:
            self.feedback.CP(f"缩放比例无效: {scale_percent}，请设置0到100之间的有效值。")
            return False

        # 合法的重采样模式
        interpolation_methods = {
            '0': cv2.INTER_NEAREST,  # 最近邻插值
            '1': cv2.INTER_LINEAR,  # 双线性插值
            '2': cv2.INTER_CUBIC,  # 三次插值
            '3': cv2.INTER_LANCZOS4,  # Lanczos 插值
            '4': cv2.INTER_AREA  # 区域插值（主要用于缩小图像）
        }

        # 尝试读取图片
        try:
            with open(input_path, 'rb') as f:
                img_array = np.asarray(bytearray(f.read()), dtype=np.uint8)
                image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        except Exception as e:
            self.feedback.CP(f"读取图片失败：{e}")
            return False

        # 如果缩放比例为100%，不做任何的缩放
        if scale_percent == 100:
            return False

        # 计算缩放后的尺寸
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)

        # 执行缩放操作
        resized_image = cv2.resize(image, dim, interpolation=interpolation_methods[resample_mode])

        # 使用 Unicode 路径转为字节路径来保存图片
        try:
            success, encoded_image = cv2.imencode('.jpg', resized_image)
            if success:
                with open(output_path, 'wb') as f:
                    f.write(encoded_image)

        except PermissionError as e:
            self.feedback.CP(f"文件写入权限错误：{e}")
        except Exception as e:
            self.feedback.CP(f"保存图片失败：{e}")

    def convert_image_format(self, input_path, output_path, output_format=None, jpg_quality=95, png_compression=3):
        """
         转换图片格式
         参数：
             input_path (str): 输入图片的路径
             output_path (str): 输出图片的路径
             output_format (str): 转换后的格式（如'jpg', 'png'），如果为None，保持原格式
             jpg_quality (int): jpg质量（1-100，默认95）
             png_compression (int): png压缩等级（0-9，默认3）
         返回：
             None
         """

        # 尝试读取图片
        try:
            with open(input_path, 'rb') as f:
                img_array = np.asarray(bytearray(f.read()), dtype=np.uint8)
                image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        except Exception as e:
            self.feedback.CP(f"转换格式-读取图片失败：{e}")
            return

        if image is None:
            self.feedback.CP(f"转换格式-读取图片缓存失败：" + os.path.basename(input_path))
            return

        # 检查输出格式
        try:
            if output_format.lower() in ['jpg', 'jpeg']:
                success, encoded_image = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])
                if success:
                    with open(output_path, 'wb') as f:
                        f.write(encoded_image)
            elif output_format.lower() == 'png':
                success, encoded_image = cv2.imencode('.png', image,
                                                      [int(cv2.IMWRITE_PNG_COMPRESSION), png_compression])
                if success:
                    with open(output_path, 'wb') as f:
                        f.write(encoded_image)
            # 如果输出格式为其他格式，使用指定的格式进行编码
            else:
                # 根据指定的输出格式进行编码，格式需以 ".格式" 的方式传入
                success, encoded_image = cv2.imencode(f'.{output_format}', image)
                # 如果编码成功，则以二进制写模式保存图像到指定的路径
                if success:
                    with open(output_path, 'wb') as f:
                        f.write(encoded_image)

            self.feedback.CP(f"{os.path.basename(input_path)} 已转换为{output_format}格式 新路径：{output_path}")

        except Exception as e:
            self.feedback.CP(f"转换格式-保存图片失败：{e}")


    def check_and_set_permission(self, file_path):
        if os.path.exists(file_path):
            # 获取文件状态
            file_status = os.stat(file_path)

            # 检查文件是否有写权限
            if not os.access(file_path, os.W_OK):
                self.feedback.CP(f"文件 {file_path} 没有写权限，正在尝试修改权限...")
                try:
                    # 给文件赋予读写权限
                    os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
                    self.feedback.CP(f"已成功修改 {file_path} 的权限。")
                except Exception as e:
                    self.feedback.CP(f"修改权限失败：{e}")
            else:
                self.feedback.CP(f"文件 {file_path} 已有写权限。")
        else:
            self.feedback.CP(f"文件 {file_path} 不存在。")











# 正确的结构应类似于以下
# 参考字典 = {
#     'mat_name': {
#         'node_01': {
#             'Path': 'xxxx',
#             'isLoaded': True,
#             'Size': 13.21,
#             'Format': 'jpg',
#             'Dimensions': [1024, 1024],
#             'usageCount': 3,
#             'filename' : 'texture_diffuse.jpg'
#         },
#         'node_02': {
#             # 其他节点的属性
#         }
#     }
# }








#   错误提示的库
class FeedbackPrompt():
    """
    FeedbackPrompt此类是一个反馈错误的模块
    """


    def __init__(self):
        current_time = datetime.now()
        self.primary_contact = "\nmail:1925250542@qq.com\nWeChat:13549971630"
        self.DefContent = '@Arnold Tool 插件提醒 {} | '.format(current_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    def CP (self, Content):
        print(self.DefContent+ Content)
        
    def CPW (self, Content= None, EC = None):
        if EC == None:
            cmds.warning(str(self.DefContent) + str(Content))
        else:
            print(str(self.DefContent) + "错误警告，报错问题在下面"+ str(Content))
            print("↓"*65)
            cmds.warning(str(EC))

    def CPE (self, Content= None, EC = None):
        # 构建基础错误消息
        error_message = str(self.DefContent) + f"严重错误，触发请联系开发者去修复，联系方式：{self.primary_contact}"

        # 追加 EC 信息（如果存在）
        if EC:
            error_message += '\n' + str(EC)

        # 追加 Content 信息（如果存在）
        if Content:
            error_message += '\n' + str(Content)

        # 抛出异常
        cmds.warning(error_message)
        # raise ValueError(error_message)



def process_sl_data(sl_data = None):
    """ 函数可以批量归类选择的节点 """
    
    feedback = FeedbackPrompt() # 错误提示模块
    
    # 创建空的字典
    sl_dict = {}
    FilterData = {}

    # 获取选择数据数据
    if sl_data == None:
        sl_data = cmds.ls(sl=True)

    # 判断是否有选择数据
    if sl_data == []:
        feedback.CP('请你先选择相应的节点哦！')
        return None

    # 创建一个字典并存储节点的类型
    for i in sl_data:
        sl_dict[i] = cmds.nodeType((i))

    FilterData = {v: [] for v in sl_dict.values()}

    for k, v in sl_dict.items():
        FilterData[v].append(k)

    return FilterData



class DataManager:
    def __init__(self):
        pass

    # 保存数据为二进制格式
    def bin_save_data(self, file_path, data):
        with open(file_path, 'wb') as file:  # 'wb' 表示写入二进制文件
            packed_data = msgpack.packb(data)  # 将数据序列化为 MessagePack 格式
            file.write(packed_data)

    # 读取二进制数据并转换回 Python 对象
    def bin_load_data(self, file_path):
        with open(file_path, 'rb') as file:  # 'rb' 表示读取二进制文件
            packed_data = file.read()  # 读取整个二进制文件内容
            data = msgpack.unpackb(packed_data)  # 将 MessagePack 格式的数据反序列化回 Python 对象
        return data



    def ascii_save_data(self, file_path, data):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def ascii_load_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def ascii_write_data(self, file_path, data):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            file.write('\n')

    def ProcessInputString(self):
        pass

    def ModifyConfigurationFile(self, value, key_path):
            """
            修改配置文件函数。

            参数:
            value -- 要设置的新值
            key_path -- 包含要修改的键的路径，以列表形式传递，例如 ["ProcSet_Options", "MagicConnectionSetColorSpace"]
            """
            # 读取文件
            TEX_PROCESSING_DATA = load_data('TEX_PROCESSING_DATA')

            # 根据给定的键路径设置值
            current_level = TEX_PROCESSING_DATA
            for key in key_path[:-1]:  # 迭代到倒数第二个键
                current_level = current_level[key]  # 进入下一层级
            current_level[key_path[-1]] = value  # 设置最终键的值

            # 修改并写回文件
            write_data(Script_path + '\TEX_PROCESSING_DATA.json', TEX_PROCESSING_DATA)

