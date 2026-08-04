##############################################################################################
# # ++ 导入所需的库和模块

# 1. Maya 库
import maya.cmds as cmds  # 导入 Maya 的 cmds 模块，用于执行 Maya 命令和操作场景
import maya.api.OpenMaya as om  # 使用 Maya 自带的图像读取能力获取贴图尺寸

# 2. 文件与系统操作
import os  # 提供与操作系统交互的功能，如文件路径操作、目录遍历等
import pathlib  # 提供面向对象的文件系统路径操作，增强对路径的处理能力

# 3. 数据处理
import json  # 用于序列化和反序列化 JSON 数据，方便与外部数据进行交换
import msgpack  # 用于高效的二进制序列化和反序列化，比 JSON 更节省空间和更快
import arnold_magic_matching as _matching
from collections import defaultdict
import difflib
# 4. 字符串处理
import re  # 提供正则表达式操作，用于模式匹配、搜索和替换字符串


# 5. 时间管理
import time  # 提供时间相关的函数，如时间戳获取、延时操作等
from datetime import datetime  # 提供日期和时间的对象和操作方法，支持更复杂的时间处理

from storage import ensure_parent_directory

Script_path = os.path.dirname(os.path.abspath(__file__))

# ##############################################################################################

def get_image_dimensions(file_path):
    """使用 Maya 原生图像读取器获取尺寸，读取失败时返回零值。"""
    try:
        image = om.MImage()
        image.readFromFile(os.path.normpath(str(file_path)), om.MImage.kUnknown)
        width, height = image.getSize()
        return [int(width), int(height)]
    except Exception:
        return [0, 0]

# 语言加载
def language_loading():
    dataM = DataManager()

    # 加载语言配置文件并获取 'language_config' 键的值
    language_config = dataM.ascii_load_data(
        os.path.join(Script_path, 'Datas', 'settings', 'language_config.json'))['language_config']

    # 动态加载相应语言的JSON文件
    language = dataM.ascii_load_data(
        os.path.join(Script_path, 'Datas', 'languages', f'{language_config}.json'))

    return language

# 路径识别判断的库
class PathDetection(object):
    """
    PathDetection 类用于处理路径检测和内容匹配。
    这个类实现了路径获取、内容检测、数据处理和匹配功能。
    """
    
    def __init__(self):
        self.node_attr = {} # ！此变量是零时变量，用来储存路径等的属性
        self.feedback = FeedbackPrompt() # 错误提示模块
        self.language = language_loading()['ArnoldMagicNodeLibs']['PathD'] # 加载相关语言模块

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
        self.node_attr = {}

        path = cmds.getAttr(f"{node_name}.fileTextureName")

        file_name = os.path.basename(path)
        self.node_attr[file_name] = os.path.normpath(path)

        return self.node_attr , os.path.dirname(path)

        # 获取指定目录下的图像文件并过滤

    def detection_path_content(self, target_dirname, exclude_list, exclude_formats=None):
        """
        返回一个字典 {文件名: 完整路径}，其中只包含：
          • 文件名 **没有** 命中 exclude_list 中的任何关键字
          • 如果 exclude_formats 不为 None，则文件扩展名必须在 exclude_formats 列表中

        参数:
            target_dirname (str): 需要扫描的目录路径
            exclude_list (list[str] | str): 要排除的关键字集合
                - 可以是 list，也可以是“一串逗号分隔的字符串”
                - 关键字不区分大小写
            exclude_formats (list[str] | str, 可选): 要保留的文件格式集合
                - 可以是 list，也可以是“一串逗号分隔的字符串”
                - 扩展名不区分大小写，支持带或不带 '.' 前缀
                - 如果为 None，则不做任何格式筛选

        异常处理:
            - 无法列目录或访问文件等情况都会通过 self.feedback.CP 输出错误信息，但函数本身始终返回 dict
        """
        lang = self.language['DPC']  # 多语言提示字典

        # 1. 获取文件列表
        try:
            file_list = os.listdir(target_dirname)
        except Exception as e:
            self.feedback.CP(f"{lang['01']} {target_dirname}，{lang['02']}:[{e}]")
            return {}

        # 2. 标准化要排除的关键字
        if isinstance(exclude_list, str):
            exclude_list = re.split(r'[,\uFF0C]', exclude_list)
        exclude_keywords = [
            keyword.strip()
            for keyword in exclude_list
            if keyword.strip()
        ]

        # 3. 处理格式筛选参数（只保留指定格式）
        include_format_set = None
        if exclude_formats:
            # 支持字符串或列表
            if isinstance(exclude_formats, str):
                exclude_formats = re.split(r'[,\uFF0C]', exclude_formats)
            # 标准化：去空，去点，转小写，然后加上前导点
            include_format_set = {
                '.' + fmt.strip().lstrip('.').lower()
                for fmt in exclude_formats
                if fmt.strip()
            }

        # 4. 遍历文件，过滤关键字和格式
        filtered_files = {}
        target_path = pathlib.Path(target_dirname)

        for file_name in file_list:
            # 4.1 关键字排除
            if _matching.contains_any_substring(file_name, exclude_keywords):
                continue

            file_path = target_path / file_name

            # 4.2 格式筛选：如果指定了格式列表，则只保留该列表中的格式
            suffix = file_path.suffix.lower()
            if include_format_set is not None and suffix not in include_format_set:
                continue

            # 文件通过所有检查，加入结果
            filtered_files[file_name] = str(file_path)

        return filtered_files

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
    def create_node(self, tex_name_list, path):

        # 创建纹理节点列表
        node_name_list = []
        
        # 遍历文件名列表
        for tex_name in tex_name_list:
            # 去除格式名称
            node_name_processing = os.path.splitext(tex_name)[0]

            # 创建文件纹理节点
            node_name = cmds.shadingNode('file', asTexture=True, name=node_name_processing)

            # 将节点添加到节点列表中
            node_name_list.append(node_name)

            file_path = os.path.join(path, tex_name)
            file_path_norm = os.path.normpath(file_path)

            # 检查文件是否存在
            if os.path.exists(file_path_norm):
                # 将文件路径设置为节点的 fileTextureName 属性
                cmds.setAttr(node_name + '.fileTextureName', file_path_norm, type='string')
            else:
                self.feedback.CPW(self.language['CN']['01']+ file_path_norm) # 此路径无法连接
        
        # 返回创建的节点列表
        return node_name_list

    # 获取图像的元属性，有创建时间、分辨率和文件类型
    def get_file_info(self, tex_dict):
        info_dict = {}
        for filename, filepath in tex_dict.items():
            file_info = {}

            # 获取创建时间
            creation_time = os.path.getctime(filepath)
            # 格式化创建时间
            creation_time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creation_time))
            file_info['creation_time'] = creation_time_formatted

            # 获取文件类型
            file_extension = os.path.splitext(filepath)[1]
            file_info['file_type'] = file_extension

            file_info['resolution'] = get_image_dimensions(filepath)

            info_dict[filename] = file_info


        return info_dict

    # 处理文件名并添加_namePro_key
    def process_dict_key_name(self, dir_file_dict, input_list_of_strings, TexFirstFilter):
        """
        按照以下步骤处理 dir_file_dict 中的键：
        1. 将所有键转换为大写。
        2. 使用 TexFirstFilter 删除专业名词。
        3. 使用输入的字符串列表删除其中的所有字符串。
        4. 使用字典中 'file_type' 的元素删除处理过的键。
        在字典的值中添加一个新的键 'processed_name'，其值为处理后的键。

        :param dir_file_dict: 以文件名为键，属性为值的字典。
        :param input_list_of_strings: 需要从键中删除的字符串列表。
        :param TexFirstFilter: 包含专业名词的字典。
        :return: 无。dir_file_dict 在原地被修改。
        """
        # 从 TexFirstFilter 中提取所有专业名词
        technical_terms = set()
        for key, terms in TexFirstFilter.items():
            technical_terms.add(key.upper())
            for term in terms:
                technical_terms.add(term.upper())

        # 合并专业名词和输入的字符串列表
        remove_words = technical_terms.union(set(s.upper() for s in input_list_of_strings))

        for original_key, value in dir_file_dict.items():

            # 将键转换为大写
            key_upper = original_key.upper()
            # 用空格替换分隔符（使用正则表达式）
            key_upper = re.sub(r'[_\-.]', ' ', key_upper)
            # 删除多余的空格
            key_upper = ' '.join(key_upper.split())
            # 分割成单词列表
            words = key_upper.split()
            # 删除专业名词和输入的字符串
            words = [word for word in words if word not in remove_words]
            # 根据 'file_type' 删除文件扩展名
            file_type = value['file_type'].upper().replace('.', '')
            words = [word for word in words if word != file_type]
            # 重新组合成 'namePro'
            namePro = ' '.join(words)
            # 在字典中添加 'namePro'
            dir_file_dict[original_key]['processed_name'] = namePro

        return dir_file_dict

    # 计算 processed_name 的相似度（Jaccard 相似系数）
    def processed_name_similarity(self, name1, name2):
        """
        计算两个文件名的相似度（基于 Jaccard 系数）。

        Args:
            name1 (str): 第一个文件名。
            name2 (str): 第二个文件名。

        Returns:
            float: 两个文件名的相似度（0-1 之间）。
        """
        if not name1 or not name2:
            return 0.0
        return difflib.SequenceMatcher(None, name1.lower(), name2.lower()).ratio()


    # 计算分辨率相似度
    def resolution_similarity(self, res1, res2):
        if (
            not res1
            or not res2
            or len(res1) != 2
            or len(res2) != 2
            or res1[0] <= 0
            or res1[1] <= 0
            or res2[0] <= 0
            or res2[1] <= 0
        ):
            return 0.0

        if res1 == res2:
            return 1.0
        else:
            res_diff = abs((res1[0] * res1[1]) - (res2[0] * res2[1]))
            max_res = max(res1[0] * res1[1], res2[0] * res2[1])
            return 1 - (res_diff / max_res)

    # 计算文件类型相似度z
    def file_type_similarity(self, type1, type2):
        """
        计算两个文件类型的相似度。

        Args:
            type1 (str): 第一个文件类型。
            type2 (str): 第二个文件类型。

        Returns:
            float: 文件类型相同则返回 1.0，否则返回 0.0。
        """
        return 1.0 if type1.lower() == type2.lower() else 0.0

    # 计算创建时间相似度
    def creation_time_similarity(self, time1, time2, creation_day_range_tolerance):

        # 转为天数
        max_diff = 3600 * 24 * creation_day_range_tolerance
        fmt = "%Y-%m-%d %H:%M:%S"

        t1 = datetime.strptime(time1, fmt)
        t2 = datetime.strptime(time2, fmt)
        time_diff = abs((t1 - t2).total_seconds())
        return 1 - min(time_diff / max_diff, 1.0)

    # 总体相似度计算函数
    def calculate_similarity(self, target_info, dir_info, weights, max_diff=30):

        results = {}
        target_filename = list(target_info.keys())[0]
        target = list(target_info.values())[0]
        target_processed_name = target['processed_name']

        for filename, info in dir_info.items():
            sim_scores = {}
            # processed_name 相似度
            dir_processed_name = info['processed_name']
            name_sim = self.processed_name_similarity(target_processed_name, dir_processed_name)
            sim_scores['name'] = name_sim

            # 分辨率相似度
            res_sim = self.resolution_similarity(target['resolution'], info['resolution'])
            sim_scores['resolution'] = res_sim

            # 文件类型相似度
            type_sim = self.file_type_similarity(target['file_type'], info['file_type'])
            sim_scores['type'] = type_sim

            # 创建时间相似度
            time_sim = self.creation_time_similarity(target['creation_time'], info['creation_time'], max_diff)
            sim_scores['time'] = time_sim

            # 总相似度
            overall_sim = (
                    weights['name_weight'] * sim_scores['name'] +
                    weights['resolution_weight'] * sim_scores['resolution'] +
                    weights['format_weight'] * sim_scores['type'] +
                    weights['creation_time_weight'] * sim_scores['time']
            )
            results[filename] = overall_sim

        return results

    # 判断数据匹配数据
    def determine_connection(self, similarity_dict, auto_max_val, similarity_max, similarity_range):
        """
        判断数据匹配情况，并返回匹配列表。

        参数:
            similarity_dict (dict): 相似度字典，键是目标，值是相似度 (0.0 - 1.0)。
            auto_max_val (bool): 是否自动获取最大相似值作为阈值。默认为 True。
            similarity_max (float): 用户指定的相似度阈值，当 auto_max_val 为 False 时使用。
            similarity_range (float): 相似度范围，用于过滤匹配目标。

        返回:
            list: 匹配目标的列表，每个元素为 (target, similarity) 的元组。

        示例:
            similarity_dict = {'A': 0.9, 'B': 0.85, 'C': 0.95}
            matches = determine_connection(similarity_dict, auto_max_val=True, similarity_range=0.05)
            # 返回 [('C', 0.95), ('A', 0.9)]
        """

        # 1. 获取相似度阈值
        if auto_max_val:
            similarity_threshold = max(similarity_dict.values())
        else:
            similarity_threshold = similarity_max

        # 2. 选择相似度在阈值附近的目标
        min_threshold = max(similarity_threshold - similarity_range, 0.0)
        max_threshold = min(similarity_threshold + similarity_range, 1.0)
        filtered_matches = [(target, similarity) for target, similarity in similarity_dict.items()
                            if min_threshold <= similarity <= max_threshold]

        # 3. 按相似度从高到低排序
        filtered_matches.sort(key=lambda x: x[1], reverse=True)

        # 返回匹配列表
        return filtered_matches

# 节点处理的库
class NodeProcessor(object):
    def __init__(self):
        self.FP = FeedbackPrompt()
        self.feedback = FeedbackPrompt() # 错误提示模块
        self.language = language_loading()['ArnoldMagicNodeLibs']['NodeP'] # 加载相关语言模块

    #   对贴图文件的名称进行处理
    def processed_texture_name(self, file_name):
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

        # 分离后缀名称
        name, ext = os.path.splitext(file_name)

        # 删除所有标点符号
        processed_name = re.sub(r'[^\w\s]', ' ', name)

        # 清理下划线
        cleaned_name = re.sub(r'_+', ' ', processed_name)

        # 将名称转换为大写
        cleaned_name = cleaned_name.upper()

        # 使用正则表达式替换多个空格为一个空格
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()

        return cleaned_name
    
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
            # 获取路径
            file_path = cmds.getAttr(NodeName + '.fileTextureName')

            # 路径转成名称
            file_name = os.path.basename(file_path)


            # 处理贴图名称
            processed_name = self.processed_texture_name(file_name)

            # 预处理
            keyword_to_channels, keywords_set = self.build_keyword_mapping(FilterData)

            # 匹配通道
            MatchingChannels = self.FilterData(processed_name, keyword_to_channels, keywords_set)

            MatchingChannelsDict[NodeName] = MatchingChannels

        # 返回匹配的通道名称
        return MatchingChannelsDict

    # 构建关键词到通道的映射以及关键词集合
    def build_keyword_mapping(self, FilterData):
        """
        构建关键词到通道的映射以及关键词集合。

        Args:
            FilterData (dict): 通道到关键词的映射字典。

        Returns:
            tuple: (keyword_to_channels, keywords_set)
        """
        keyword_to_channels = defaultdict(list)
        keywords_set = set()
        for channel, keywords in FilterData.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                keyword_to_channels[keyword_lower].append(channel)
                keywords_set.add(keyword_lower)
        return keyword_to_channels, keywords_set

    # 根据纹理名称匹配对应的通道
    def FilterData(self, NewTexName, keyword_to_channels, keywords_set):
        """
        根据纹理名称匹配对应的通道。

        Args:
            NewTexName (str): 纹理名称字符串。
            keyword_to_channels (dict): 关键词到通道的映射字典。
            keywords_set (set): 所有关键词的集合。

        Returns:
            str or None: 最佳匹配的通道名称，若无匹配则返回 None。
        """
        tex_name_lower = NewTexName.lower()

        # 将贴图名称拆分为单词列表（以空格、下划线或连字符为分隔符）
        tex_name_words = re.split(r'[\s_-]+', tex_name_lower)

        # 记录每个通道的匹配次数
        channel_scores = defaultdict(int)

        # 精确匹配阶段，仅匹配完整单词
        for word in tex_name_words:
            if word in keywords_set:
                channels = keyword_to_channels[word]
                for channel in channels:
                    channel_scores[channel] += 1

        # 如果未找到精确匹配，进行模糊匹配
        if not channel_scores:
            for word in tex_name_words:
                for keyword in keywords_set:
                    if _matching.is_edit_distance_at_most_one(word, keyword):
                        channels = keyword_to_channels[keyword]
                        for channel in channels:
                            channel_scores[channel] += 1

        # 选择得分最高的通道
        if channel_scores:
            best_match_channel = max(channel_scores.items(), key=lambda x: x[1])[0]

            return best_match_channel

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
    def ConnectTexFileNodeToProNode(self, texture_name, node_list, input_port, material_channel, input_port_list=None, output_port_list=None):
        """
        这个函数用于将纹理文件节点连接到提供的节点列表并将提供的输入端口和材质通道与这些节点关联。

        参数:
        texture_name (str): 纹理文件节点的名称。
        node_list (list of str): 一个包含节点类型的列表，用于创建并连接到纹理文件节点的节点。
        input_port (str): 第一个节点的输入端口。
        material_channel (str): 材质通道，用于确定纹理文件节点的输出端口（'outColor' 或 'outAlpha'）。
        input_port_list (list of str, optional): 输入端口的列表。如果未提供，则默认为 ["input", "passthrough"]。
        output_port_list (list of str, optional): 输出端口的列表。如果未提供，则默认为 ["outColor", "outAlpha", "outValue", "outTransparency", "outColorR", "outColorG", "outColorB"]。

        返回:
        str: 已创建的最后一个节点的名称。

        过程:
        - 根据提供的材质通道确定纹理文件节点的输出端口 ('outColor' 或 'outAlpha')。
        - 使用节点列表中的第一个节点创建并连接到纹理文件节点。
        - 如果连接不成功，则在提供的输入端口列表和输出端口列表之间进行尝试。
        - 遍历节点列表，为每个节点创建并将其连接到先前的节点。
        - 返回最后创建的节点名称。

        注意:
        - 当输入的材质通道未在定义的列表中时，会引发 ValueError 异常。
        - 在尝试连接节点时，可能会发生异常。如果发生异常，会在尝试列表中进行循环尝试。
        """
        # 定义灰色和彩色通道列表
        gray_channels = ["base", "diffuseRoughness", "metalness", "specularRoughness", "subsurface", "emission", "ao",
                         "bump", "displacement"]
        color_channels = ["baseColor", "specularColor", "subsurfaceColor", "subsurfaceRadius", "emissionColor",
                          "opacity", "normalCamera"]

        # 如果没有提供输入端口列表，则设置默认值
        if input_port_list is None:
            input_port_list = ["input", "passthrough", "input1", "input2"]

        if output_port_list is None:
            output_port_list = ["outColor", "outAlpha", "outValue", "outTransparency", "outColorR", "outColorG", "outColorB"]

        texture_output_port = ''

        # 确定纹理文件节点的输出端口
        if material_channel in color_channels:
            texture_output_port = 'outColor'
        elif material_channel in gray_channels:
            texture_output_port = 'outAlpha'
        else:
            self.feedback.CPE(self.language['CTFNTPN']['01']+  str(material_channel)) # 位置的材质通道

        # 创建第一个节点
        first_node_type = node_list[0]
        first_node = cmds.createNode(first_node_type, name=f"{texture_name}_{first_node_type}")

        # first_node_type 这个是第一个获取的节点类型
        # first_node 这个变量是第一个创建的处理节点名称

        # 储存创建节点方便后面调整参数
        create_node_name_list = []
        # 添加第一个创建的节点
        create_node_name_list.append(first_node)

        # 尝试将纹理文件节点连接到第一个节点
        try:
            if material_channel in color_channels:
                self.node_connect(texture_name, texture_output_port, first_node, input_port)
            elif material_channel in gray_channels:
                for color in ["R", "G", "B"]:
                    self.node_connect(texture_name, texture_output_port, first_node, input_port + color)
        except:
            for input_port in input_port_list:
                for output_port in output_port_list:
                    try:
                        self.node_connect(texture_name, output_port, first_node, input_port)
                        break
                    except:
                        pass

        # 保存上一个创建的节点
        previous_node = first_node

        # 遍历NodeList进行节点的创建和连接
        for index in range(1, len(node_list)):

            CurrentNodeType = node_list[index]

            # 创建当前节点
            current_node = cmds.createNode(CurrentNodeType, name=f"{texture_name}_{CurrentNodeType}")
            create_node_name_list.append(current_node)
            for input_port in input_port_list:
                for output_port in output_port_list:
                    try:
                        self.node_connect(previous_node, output_port, current_node, input_port)
                        break
                    except:
                        pass

            previous_node = current_node



        # 把 aiRampRgb 类型节点类型改成 custom
        for node_name in create_node_name_list:
            # 检查节点是否存在并且是 aiRampRgb 类型
            if cmds.objExists(node_name) and cmds.nodeType(node_name) == 'aiRampRgb':
                # 将 type 属性设置为 0
                cmds.setAttr(f"{node_name}.type", 0)


        return previous_node
    
    #   连接到材质球。此函数根据匹配字典和最后节点字典，将节点与材质球连接。
    def ConnectToMaterial(self, MatchingDict, LastNodeDict, ProcessingNodeData, magic_connection_options,  MaterialName=None, OutputPortList=None, DisplacementShader=None):
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
                    self.node_connect(Node, OutPort, NodeName, NodeChannel ,force=True)
                    break
                except Exception as e:
                    # 如果连接失败，继续尝试下一个端口
                    pass
            
        # 初始化 normal map 节点为 None
        aiNormalMap = None

        # 遍历 MatchingDict 中的节点名称和材质通道
        for NodeName, MatChannel in MatchingDict.items():

            # 如果节点没有打开连接将跳过这次连接
            if not magic_connection_options[MatChannel]:
                continue

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
                        ContToNode(LastNodeDict[self.FindKeyByChannel(MatchingDict, 'bump')], aiBump2d, 'bumpMap')
                    except Exception as e:
                        ContToNode(self.FindKeyByChannel(MatchingDict, 'bump'), aiBump2d, 'bumpMap')
                    ContToNode(aiBump2d, MaterialName, 'normalCamera')

                else:
                    try:
                        ContToNode(LastNodeDict[self.FindKeyByChannel(MatchingDict, 'bump')], aiBump2d, 'bumpMap')
                    except Exception as e:
                        ContToNode(self.FindKeyByChannel(MatchingDict, 'bump'), aiBump2d, 'bumpMap')
                    ContToNode(aiBump2d, aiNormalMap, 'normal')
                
            # 处理 Displacement 通道
            elif MatChannel == "displacement":

                # 创建 displacementShader 节点
                displacementShader = cmds.createNode("displacementShader", name=NodeName + "displacementShader")

                # 将 displacementShader 连接到材质球的 Displacement 通道
                try:
                    ContToNode(LastNodeDict[self.FindKeyByChannel(MatchingDict, 'displacement')], displacementShader, "displacement")
                except Exception as e:
                    ContToNode(self.FindKeyByChannel(MatchingDict, 'displacement'), displacementShader, "displacement")
                    
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
                self.node_connect(new_uv_node, plug, file_tex_node, plug, True)

            # 单独连接 'outUV' 和 'outUvFilterSize' 属性
            self.node_connect(new_uv_node, 'outUV', file_tex_node, 'uvCoord', True)
            self.node_connect(new_uv_node, 'outUvFilterSize', file_tex_node, 'uvFilterSize', True)

    #   自动连接节点函数
    def AutoNodeConnect(self, node_list, mat_name, FilterData, ProcessingNodeData, magic_connection_options, Auto_Node_Connection_Options, shading_engine_node = None):
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
        - 会返回匹配好的字典
        """
        # 3.重新排序贴图顺序

        MatchingDict = self.ReorderdictionaryByPriority(self.MatchingChannels(node_list, FilterData))


        LastNodeDict = {}
    
        # 4.连接并创建相应的处理节点
        for NodeName, MatChannel in MatchingDict.items():

            if not Auto_Node_Connection_Options[MatChannel]:
                continue

            LastNodeDict[NodeName] = self.ConnectTexFileNodeToProNode(NodeName,
                                                                        ProcessingNodeData[MatChannel]["NodeList"],
                                                                        ProcessingNodeData[MatChannel]["InputPort"],
                                                                        MatChannel)


        self.ConnectToMaterial(MatchingDict, LastNodeDict, ProcessingNodeData, magic_connection_options, mat_name, DisplacementShader= shading_engine_node)

        return MatchingDict

    #   自动匹配色彩空间并设置
    def AutoSetTexColorSpace(self, auto_set_color_space_config, node_list=None, filter_data=None, matching_channel=None):
        """
         输入节点自动匹配色彩空间

         参数:
         node_list -- 包含节点名称的列表
         filter_data -- 用于过滤节点的相关数据
         """
        lang = self.language['ASTCS']

        # 1. 使用 matching_channels 函数匹配通道
        if matching_channel is None:
            matching_channel = self.MatchingChannels(node_list, filter_data)

        # 2. 进行设置色彩空间相关设置
        for node_name, channel in matching_channel.items():
            if channel in auto_set_color_space_config:
                tex_color_space = auto_set_color_space_config[channel]

                # 设置色彩空间
                cmds.setAttr(node_name + '.colorSpace', tex_color_space, type='string')

                # 设置 alpha 是亮度，并忽略色彩空间规则
                cmds.setAttr(node_name + '.alphaIsLuminance', 1)
                cmds.setAttr(node_name + '.ignoreColorSpaceFileRules', 1)

                self.feedback.CP(f"{node_name} {lang['01']} <{tex_color_space}> {lang['02']}") # 节点设置为 色彩空间

    #   连接节点属性
    def node_connect(self, source_node, source_attr, target_node, target_attr, force = True):
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

    # 清洁材质名称
    def clean_material_name(self, filename: str, tex_filter: dict):

        # 将所有专业词汇扁平化为一个列表
        professional_terms = [term.upper() for sublist in tex_filter.values() for term in sublist]

        # 1. 删除数字及后面的下划线
        filename = re.sub(r'^\d+_', '', filename)

        # 2. 删除专业名词
        for term in professional_terms:
            # 使用正则表达式忽略大小写匹配并删除专业词汇
            filename = re.sub(term, '', filename, flags=re.IGNORECASE)

        # 3. 删除文件后缀
        filename = os.path.splitext(filename)[0]

        # 删除多余的下划线
        filename = re.sub(r'_+', '_', filename).strip('_')

        return filename

    # 自动udim
    def auto_set_udim(self, node_list):
        """
        作用：
            - 通过输入的node_list去检测是否是udim类型

        参数:
            - node_list 列表类型，输入的是节点名称列表

        返回:
            无返回值。该函数直接对节点进行连接操作。
        """

        for node_name in node_list:
            node_path = cmds.getAttr(node_name + '.fileTextureName')
            process_file_name = self.processed_texture_name(os.path.basename(node_path))
            if self.contains_udim_number(process_file_name):
                cmds.setAttr(node_name + '.uvTilingMode', 3)
                self.feedback.CP(f"{node_name} {self.language['ASU']['01']}")
            else:
                self.feedback.CP(f"{node_name} {self.language['ASU']['02']}")
                cmds.setAttr(node_name + '.uvTilingMode', 0)

    # 检测字符串中是否包含 UDIM 格式的数字（范围：1001-1999）
    def contains_udim_number(self, text):
        """
        检测字符串中是否包含 UDIM 格式的数字（范围：1001-1999）。
        """
        pattern = r"\b1[0-9]{3}\b"  # 匹配1001到1999之间的四位数字
        match = re.search(pattern, text)
        return bool(match)

    # ______________________________________________________________________________>>> Maya节点短名称替换工具
    def replace_node_name(self, enabled=True, ignore_case=False, target='', replacement='', node_name=''):
        """
        替换提供的Maya节点的短名称。

        参数：
            enabled (bool): 是否启用替换功能。
            ignore_case (bool): 是否忽略大小写。
            target (str): 目标字符串，需要被替换的内容。
            replacement (str): 替换后的字符串。
            node_name (str): 要进行替换的节点名称。
        """
        # 如果功能未启用，则直接返回
        if not enabled:
            return

        # __________________________________________________________________________>>> 匹配模式设置
        # 设置正则匹配的标志，支持大小写选项
        flags = re.IGNORECASE if ignore_case else 0
        pattern = re.compile(re.escape(target), flags)  # 转义目标字符串以进行精确匹配

        # __________________________________________________________________________>>> 节点名称替换逻辑
        # 检查目标字符串是否存在于节点名称中
        if pattern.search(node_name):
            # 执行替换操作
            new_name = pattern.sub(replacement, node_name)
            try:
                # 调用Maya命令重命名节点
                cmds.rename(node_name, new_name)
                print(f"已重命名: {node_name} -> {new_name}")
            except Exception as e:
                # 捕获异常，但不阻断程序运行
                print(f"重命名失败: {node_name} -> {new_name}, 错误: {str(e)}")
        else:
            # 如果没有匹配到目标字符串，直接返回
            print(f"未找到匹配的目标字符串: {target} 于节点: {node_name}")

# 获取节点数据的库
class GetNodeData():
    
    # 获取场景灯光节点和类
    def get_scene_arnold_lights_and_type(self):
        """
        获取场景中的所有灯光节点。

        返回:
        - lights (list): 包含所有灯光节点名称的列表。
        """
        arnold_lights_and_type= {}
        # Arnold 灯光类型列表
        arnold_light_types = [
            'aiAreaLight', 'aiSkyDomeLight', 'aiPhotometricLight',
            'aiMeshLight', 'aiLightPortal', 'directionalLight', 'spotLight',
            'areaLight' ,  'pointLight'
        ]
        # 遍历所有 Arnold 灯光类型
        for light_type in arnold_light_types:
            # 获取场景中当前类型的所有灯光形状节点
            light_shapes = cmds.ls(type=light_type)
            if light_shapes:
                for light_shape in light_shapes:
                    # 获取该形状节点的父节点，即灯光的名称
                    light_name = cmds.listRelatives(light_shape, parent=True)[0]
                    arnold_lights_and_type[light_name] = light_type

        return arnold_lights_and_type

    # 获取灯光的灯光组
    def get_light_group(self, lights):
        """获取灯光的 AOV light group 并使用 light group 去分类灯光
        参数:
            lights (dict): 格式为 {'灯光名称': '灯光类型'} 的字典
        返回:
            dict: 按照 light group 分类后的灯光字典，格式为 {'lightGroup': [灯光名称1, 灯光名称2, ...]}
        """
        light_groups = {}
        for light_name in lights:
            try:
                # 获取灯光的 AOV light group
                light_group = cmds.getAttr(f"{light_name}.aiAov")

                # 检查是否是字符串，确保类型正确
                if not isinstance(light_group, str):
                    light_group = 'default'

            except Exception as e:
                light_group = 'default'
            # 如果该 light group 尚未被记录，初始化列表
            if light_group not in light_groups:
                light_groups[light_group] = []
            # 将灯光名称添加到对应的 light group 分类下
            light_groups[light_group].append(light_name)

        return light_groups

    # 寻找材质的一条纹理路径
    def get_file_texture_paths(self, material_node):
        """
        获取指定材质节点连接链上所有 file 文件节点的贴图路径，
        并以字典形式返回：{file_node_name: fileTextureName}

        参数:
            material_node (str): 材质节点名称（例如 "aiStandardSurface1" 等）。
        返回:
            dict[str, str]: key 为 file 节点名称，value 为贴图路径 (fileTextureName)。
                             如果未找到任何 file 节点，则返回空字典。
        """
        file_paths = {}  # 用来存储 {file_node: texture_path}
        visited = set()  # 防止循环或重复遍历

        def _traverse(node):
            if node in visited:
                return
            visited.add(node)

            # 获取所有上游连接的源节点，跳过转换节点
            upstream_nodes = cmds.listConnections(node,
                                                  source=True,
                                                  destination=False,
                                                  skipConversionNodes=True) or []
            if not upstream_nodes:
                return

            for src_node in upstream_nodes:
                # 找到 file 节点就读它的 fileTextureName 属性
                if cmds.nodeType(src_node) == "file":
                    attr_name = src_node + ".fileTextureName"
                    if cmds.objExists(attr_name):
                        texture_path = cmds.getAttr(attr_name)
                        file_paths[src_node] = texture_path
                        # 如果只关心第一个文件，可以在这里 break
                else:
                    # 继续递归查找
                    _traverse(src_node)

        _traverse(material_node)
        return file_paths

# 专门处理节点混合
class BlendNodeManager():
    pass

# 错误提示的库
class FeedbackPrompt():
    """
    FeedbackPrompt此类是一个反馈错误的模块
    """


    def __init__(self):

        self.language = language_loading()['ArnoldMagicNodeLibs']['FeedbackPrompt']  # 加载相关语言模块

        current_time = datetime.now()
        self.primary_contact = "\nmail:1925250542@qq.com\nWeChat:13549971630"
        self.DefContent = f"{self.language['01']} {current_time.strftime('%Y-%m-%d %H:%M:%S')} | "
    
    def CP (self, Content):
        print(self.DefContent+ Content)
        
    def CPW (self, Content= None, EC = None):
        if EC == None:
            cmds.warning(str(self.DefContent) + str(Content))
        else:
            print(str(self.DefContent) + self.language['02']+ str(Content))
            print("↓"*65)
            cmds.warning(str(EC))

    def CPE (self, Content= None, EC = None):
        # 构建基础错误消息
        error_message = str(self.DefContent) + f"{self.language['03']}: {self.primary_contact}"

        # 追加 EC 信息（如果存在）
        if EC:
            error_message += '\n' + str(EC)

        # 追加 Content 信息（如果存在）
        if Content:
            error_message += '\n' + str(Content)

        # 抛出异常
        # cmds.warning(error_message)
        raise ValueError(error_message)

#______________________________________________________________________________>>> 处理选择的节点
def process_sl_data(sl_data=None):
    """函数用于批量归类选择的节点"""

    #__________________________________________________________________________>>> 加载语言模块和错误提示模块
    language = language_loading()['ArnoldMagicNodeLibs']['process_sl_data']  # 加载语言模块
    feedback = FeedbackPrompt()  # 错误提示模块

    # 初始化空字典
    sl_dict = {}
    FilterData = {}

    #__________________________________________________________________________>>> 获取选择的节点数据
    # 如果未传入参数，获取当前选中的节点
    if sl_data is None:
        sl_data = cmds.ls(sl=True)

    # 判断是否有选择的数据
    if not sl_data:
        feedback.CPW(language['01'])  # 输出提示信息
        return None

    #__________________________________________________________________________>>> 创建节点类型字典
    # 遍历选中的节点并获取其类型
    for i in sl_data:
        sl_dict[i] = cmds.nodeType(i)  # 获取节点类型并存入字典

    #__________________________________________________________________________>>> 初始化分类字典
    # 按节点类型初始化 FilterData 字典
    FilterData = {v: [] for v in sl_dict.values()}

    #__________________________________________________________________________>>> 分类节点
    # 根据节点类型将节点归类到 FilterData 中
    for k, v in sl_dict.items():
        FilterData[v].append(k)

    return FilterData  # 返回按类型归类的节点数据

#______________________________________________________________________________>>> 获取场景节点数据并分类
def get_scene_all_data():
    """获取场景中的所有节点并按类型分类"""

    # 初始化错误提示模块
    feedback = FeedbackPrompt()  # 错误提示模块

    # 创建空的字典用于存储节点及其类型
    all_dict = {}
    FilterData = defaultdict(list)  # 使用 defaultdict 自动处理列表初始化

    #__________________________________________________________________________>>> 获取所有节点
    # 获取场景中所有节点（包括 DAG 节点）
    all_nodes = cmds.ls(geometry=1,lights=1,cameras=1, long=1,materials=1,textures=1,assemblies=1)

    # 判断是否有节点存在
    if not all_nodes:
        feedback.CPW('没有找到节点')  # 返回错误提示
        return None

    # 调试输出 all_nodes，确认节点获取正确
    # print("获取到的所有节点:", all_nodes)

    #__________________________________________________________________________>>> 创建节点类型字典并分类节点
    # 遍历所有节点并获取节点类型，同时进行分类
    for node in all_nodes:
        try:
            node_type = cmds.nodeType(node)  # 获取节点类型
        except Exception as e:
            node_type = 'unknown'  # 捕获异常并标记为未知类型
            print(f"获取节点类型失败: {node}, 错误: {e}")

        # 将节点及其类型存入字典
        all_dict[node] = node_type

        # 将节点分类存储到 FilterData
        FilterData[node_type].append(node)

    # 将 defaultdict 转换为普通字典（可选）
    FilterData = dict(FilterData)

    # # 调试输出 FilterData，确认分类正确
    # print("分类后的节点数据:")
    # for node_type, nodes in FilterData.items():
    #     print(f"类型: {node_type}, 节点数量: {len(nodes)}")
    #     for node in nodes:
    #         print(f"  - {node}")

    return FilterData  # 返回按类型分类的节点数据


# 数据管理器
class DataManager:
    def __init__(self):
        pass

    # 读取二进制数据并转换回 Python 对象
    def bin_load_data(self, file_path):
        with open(file_path, 'rb') as file:  # 'rb' 表示读取二进制文件
            packed_data = file.read()  # 读取整个二进制文件内容
            data = msgpack.unpackb(packed_data)  # 将 MessagePack 格式的数据反序列化回 Python 对象
        return data

    # 保存数据为二进制格式
    def bin_save_data(self, file_path, data):
        file_path = ensure_parent_directory(file_path)
        with file_path.open('wb') as file:  # 'wb' 表示写入二进制文件
            packed_data = msgpack.packb(data)  # 将数据序列化为 MessagePack 格式
            file.write(packed_data)

    def bin_modify_data(self, key, cont, settings_path, file_name):
        config = self.bin_load_data(
            os.path.normpath(os.path.join(settings_path, file_name)))

        config[key] = cont

        self.bin_save_data(
            os.path.normpath(os.path.join(settings_path, file_name), config))

    def ascii_load_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def ascii_save_data(self, file_path, data):
        file_path = ensure_parent_directory(file_path)
        with file_path.open('w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)



# 数据管理器
# class DataManager_new:
#     def __init__(self, file_path, file_name):
#         """
#         初始化数据管理器实例。
#
#         :param file_path: 文件的路径
#         :param file_name: 文件名
#         """
#         self.feedback = FeedbackPrompt() # 反馈模块
#         self.file_path = os.path.normpath(os.path.join(file_path, file_name))
#
#     # 读取二进制数据并转换回 Python 对象
#     def bin_load_data(self):
#         """
#         读取二进制文件并反序列化为 Python 对象。
#
#         :return: 反序列化后的数据（Python 对象）
#         """
#         try:
#             with open(self.file_path, 'rb') as file:  # 'rb' 表示读取二进制文件
#                 packed_data = file.read()  # 读取整个二进制文件内容
#                 data = msgpack.unpackb(packed_data)  # 使用 msgpack 反序列化数据
#             return data
#         except FileNotFoundError:
#             self.feedback.CPW(f"错误: 文件 {self.file_path} 未找到")
#             return False
#         except msgpack.exceptions.ExtraData:
#             self.feedback.CPW(f"错误: 文件 {self.file_path} 数据格式错误")
#             return False
#
#     # 保存数据为二进制格式
#     def bin_save_data(self, data):
#         """
#         将数据序列化为二进制格式并保存到文件。
#
#         :param data: 需要保存的数据
#         """
#         try:
#             with open(self.file_path, 'wb') as file:  # 'wb' 表示写入二进制文件
#                 packed_data = msgpack.packb(data)  # 使用 msgpack 序列化数据
#                 file.write(packed_data)  # 写入文件
#         except Exception as e:
#             self.feedback.CPW(f"保存数据时发生错误: {e}")
#             return False
#
#     def bin_modify_data(self, key, cont):
#         """
#         修改二进制文件中的指定键的值。
#
#         :param key: 需要修改的键
#         :param cont: 新的内容
#         :return: 修改后的数据
#         """
#
#
#         config = self.bin_load_data(self.file_path)
#         if config is None:
#             self.feedback.CPW(f"无法读取数据，无法修改")
#             return False
#
#         config[key] = cont
#         self.bin_save_data(config)
#
#         return config
#
#     def bin_modify_nested_data(self, key_path, cont):
#         """
#         修改嵌套数据结构中的指定键的值。
#
#         :param key_path: 键的路径（一个由多个键组成的列表）
#         :param cont: 新的内容
#         :return: 修改后的数据
#         """
#
#         if not key_path:
#             self.feedback.CPW("key_path 不能是空的")  # 确保key路径不为空
#             return False
#         config = self.bin_load_data(self.file_path)
#
#         if config is None:
#             self.feedback.CPW(f"无法读取数据，无法修改")
#             return False
#
#
#         # 根据给定的键路径逐层访问数据
#         current_level = config
#         for key in key_path[:-1]:  # 遍历到倒数第二个键
#
#             if key not in current_level:
#                 self.feedback.CPW(f"错误: 在路径 {' -> '.join(key_path)} 中找不到键 {key}")
#                 return False
#
#             current_level = current_level[key]  # 进入下一层级
#
#         # 设置最终键的值为新值
#         current_level[key_path[-1]] = cont
#
#         self.bin_save_data(config)
#
#         return config
#
#     def ascii_load_data(self):
#         """
#         读取 ASCII 格式的 JSON 文件并返回数据。
#
#         :return: 读取的 Python 对象
#         """
#         try:
#             with open(self.file_path, 'r', encoding='utf-8') as file:
#                 data = json.load(file)  # 使用 json 加载数据
#             return data
#         except FileNotFoundError:
#             self.feedback.CPW(f"错误: 文件 {self.file_path} 未找到")
#             return False
#         except json.JSONDecodeError:
#             self.feedback.CPW(f"错误: 文件 {self.file_path} 数据格式错误")
#             return False
#
#     def ascii_save_data(self, data):
#         """
#         将数据保存为 ASCII 格式的 JSON 文件。
#
#         :param data: 需要保存的数据
#         """
#         try:
#             with open(self.file_path, 'w', encoding='utf-8') as file:
#                 json.dump(data, file, indent=4)  # 使用 json 保存数据，并格式化
#         except Exception as e:
#             self.feedback.CPW(f"保存数据时发生错误: {e}")
#             return False



