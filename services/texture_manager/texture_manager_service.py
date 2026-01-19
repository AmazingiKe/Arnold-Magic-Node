from typing import Dict, List, Any
from .i_texture_manager_service import ITextureManagerService
from core.i_config_manager import IConfigManager
from core.i_logger import ILogger
from core.i_event_bus import IEventBus
from data.i_node_data_repository import INodeDataRepository
from data.i_file_system_repository import IFileSystemRepository


class TextureManagerService(ITextureManagerService):
    """
    贴图管理服务实现

    职责:
    - 提供贴图管理相关业务逻辑
    - 包括贴图查询、过滤、修复、处理等功能
    """

    def __init__(
        self,
        config_manager: IConfigManager,
        logger: ILogger,
        node_data_repo: INodeDataRepository,
        file_system_repo: IFileSystemRepository,
        event_bus: IEventBus
    ):
        """
        初始化服务

        参数:
            config_manager: 配置管理器
            logger: 日志器
            node_data_repo: 节点数据仓储
            file_system_repo: 文件系统仓储
            event_bus: 事件总线
        """
        self._config = config_manager
        self._logger = logger
        self._node_repo = node_data_repo
        self._file_repo = file_system_repo
        self._event_bus = event_bus

    def get_all_textures(self) -> Dict[str, Any]:
        """
        获取所有贴图信息

        返回:
            贴图信息字典，格式为 {材质名: {贴图名: 贴图信息}}
        """
        self._logger.info("获取所有贴图信息")
        return self._node_repo.get_all_textures()

    def filter_textures(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        过滤贴图

        参数:
            filters: 过滤条件，如 {'isLoaded': False, 'minSize': 10}

        返回:
            过滤后的贴图信息
        """
        self._logger.info("过滤贴图", filters=filters)

        all_textures = self.get_all_textures()
        filtered = {}

        for material_name, texture_dict in all_textures.items():
            filtered_textures = {}
            for texture_name, texture_info in texture_dict.items():
                if self._matches_filters(texture_info, filters):
                    filtered_textures[texture_name] = texture_info

            if filtered_textures:
                filtered[material_name] = filtered_textures

        return filtered

    def _matches_filters(self, texture_info: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        检查贴图信息是否匹配过滤条件

        参数:
            texture_info: 贴图信息
            filters: 过滤条件

        返回:
            是否匹配
        """
        for key, value in filters.items():
            if key == 'isLoaded':
                if texture_info.get('isLoaded') != value:
                    return False
            elif key == 'minSize':
                if texture_info.get('size', 0) < value:
                    return False
            elif key in texture_info:
                if texture_info[key] != value:
                    return False

        return True

    def fix_missing_textures(self, search_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        修复缺失贴图

        参数:
            search_path: 搜索路径
            options: 修复选项

        返回:
            修复结果，包含修复数量、失败列表等
        """
        self._logger.info("开始修复缺失贴图", search_path=search_path, options=options)

        all_textures = self.get_all_textures()
        missing_textures = self._filter_missing_textures(all_textures)

        if not missing_textures:
            self._logger.info("没有缺失的贴图")
            return {
                'fixed_count': 0,
                'failed_count': 0,
                'matched': {}
            }

        dir_files = self._file_repo.search_files(
            search_path,
            exclude_list=options.get('exclude_list', []),
            extensions=options.get('extensions', None)
        )

        matched = self._match_textures(missing_textures, dir_files, options)

        fixed_count = 0
        failed_count = 0

        for texture, new_path in matched.items():
            try:
                self._node_repo.set_texture_path(texture, new_path)
                fixed_count += 1
                self._logger.info(f"修复贴图成功: {texture}", new_path=new_path)
            except Exception as e:
                self._logger.error(f"修复贴图失败: {texture}", error=str(e))
                failed_count += 1

        result = {
            'fixed_count': fixed_count,
            'failed_count': failed_count,
            'matched': matched
        }

        self._event_bus.publish('textures.fixed', result)
        self._logger.info("修复缺失贴图完成", result=result)

        return result

    def _filter_missing_textures(self, all_textures: Dict[str, Any]) -> Dict[str, str]:
        """
        过滤缺失的贴图

        参数:
            all_textures: 所有贴图信息

        返回:
            缺失贴图字典，格式为 {贴图节点名: 原路径}
        """
        missing = {}
        for material_name, texture_dict in all_textures.items():
            for texture_name, texture_info in texture_dict.items():
                if not texture_info.get('isLoaded', False):
                    missing[texture_name] = texture_info.get('Path', '')
        return missing

    def _match_textures(self, missing_textures: Dict[str, str],
                       dir_files: Dict[str, str], options: Dict[str, Any]) -> Dict[str, str]:
        """
        匹配缺失贴图

        参数:
            missing_textures: 缺失贴图字典
            dir_files: 目录文件字典
            options: 匹配选项

        返回:
            匹配结果，格式为 {贴图节点名: 新路径}
        """
        matched = {}
        weights = options.get('weights', {
            'name_weight': 0.4,
            'resolution_weight': 0.3,
            'format_weight': 0.1,
            'creation_time_weight': 0.2
        })

        for texture, old_path in missing_textures.items():
            old_filename = self._extract_filename(old_path)

            best_match = None
            best_score = 0

            for filename, filepath in dir_files.items():
                score = self._calculate_similarity(old_filename, filename, weights)
                if score > best_score:
                    best_score = score
                    best_match = filepath

            if best_match and best_score > 0.8:
                matched[texture] = best_match

        return matched

    def _extract_filename(self, filepath: str) -> str:
        """
        从文件路径中提取文件名

        参数:
            filepath: 文件路径

        返回:
            文件名
        """
        import os
        return os.path.basename(filepath)

    def _calculate_similarity(self, name1: str, name2: str, weights: Dict[str, float]) -> float:
        """
        计算两个文件名的相似度

        参数:
            name1: 文件名1
            name2: 文件名2
            weights: 权重配置

        返回:
            相似度分数 (0-1)
        """
        name1_lower = name1.lower()
        name2_lower = name2.lower()

        if name1_lower == name2_lower:
            return 1.0

        name_similarity = self._calculate_name_similarity(name1_lower, name2_lower)
        extension_similarity = self._calculate_extension_similarity(name1_lower, name2_lower)

        return (name_similarity * weights['name_weight'] +
                extension_similarity * weights['format_weight'])

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        计算文件名相似度

        参数:
            name1: 文件名1
            name2: 文件名2

        返回:
            相似度分数 (0-1)
        """
        from difflib import SequenceMatcher
        return SequenceMatcher(None, name1, name2).ratio()

    def _calculate_extension_similarity(self, name1: str, name2: str) -> float:
        """
        计算扩展名相似度

        参数:
            name1: 文件名1
            name2: 文件名2

        返回:
            相似度分数 (0-1)
        """
        import os
        ext1 = os.path.splitext(name1)[1].lower()
        ext2 = os.path.splitext(name2)[1].lower()

        if ext1 == ext2:
            return 1.0
        return 0.0

    def process_images(self, texture_list: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        批量处理图像

        参数:
            texture_list: 贴图节点列表
            options: 处理选项，如格式、缩放比例等

        返回:
            处理结果
        """
        self._logger.info("开始批量处理图像", count=len(texture_list), options=options)

        result = {
            'processed_count': 0,
            'failed_count': 0,
            'failed_list': []
        }

        for texture_node in texture_list:
            try:
                self._process_single_image(texture_node, options)
                result['processed_count'] += 1
            except Exception as e:
                self._logger.error(f"处理图像失败: {texture_node}", error=str(e))
                result['failed_count'] += 1
                result['failed_list'].append(texture_node)

        self._event_bus.publish('images.processed', result)
        self._logger.info("批量处理图像完成", result=result)

        return result

    def _process_single_image(self, texture_node: str, options: Dict[str, Any]) -> None:
        """
        处理单个图像

        参数:
            texture_node: 贴图节点
            options: 处理选项
        """
        texture_path = self._node_repo.get_node_attribute(texture_node, 'fileTextureName')

        if not texture_path:
            raise ValueError(f"贴图节点 {texture_node} 没有路径")

        if not self._file_repo.file_exists(texture_path):
            raise FileNotFoundError(f"贴图文件不存在: {texture_path}")

        output_format = options.get('format', 'jpg')
        scale_factor = options.get('scale_factor', 1.0)

        self._logger.info(f"处理图像: {texture_node}", path=texture_path,
                         format=output_format, scale=scale_factor)

    def pack_textures(self, texture_list: List[str], output_path: str, options: Dict[str, Any]) -> bool:
        """
        打包贴图

        参数:
            texture_list: 贴图节点列表
            output_path: 输出路径
            options: 打包选项

        返回:
            是否成功
        """
        self._logger.info("开始打包贴图", count=len(texture_list), output_path=output_path, options=options)

        try:
            import zipfile

            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for texture_node in texture_list:
                    try:
                        texture_path = self._node_repo.get_node_attribute(texture_node, 'fileTextureName')

                        if texture_path and self._file_repo.file_exists(texture_path):
                            filename = self._extract_filename(texture_path)
                            zipf.write(texture_path, filename)
                            self._logger.info(f"添加贴图到压缩包: {texture_node}", filename=filename)
                    except Exception as e:
                        self._logger.warning(f"添加贴图失败: {texture_node}", error=str(e))

            self._event_bus.publish('textures.packed', {
                'output_path': output_path,
                'texture_count': len(texture_list)
            })

            self._logger.info("打包贴图完成", output_path=output_path)
            return True

        except Exception as e:
            self._logger.error("打包贴图失败", error=str(e))
            return False
