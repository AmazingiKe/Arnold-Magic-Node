from abc import ABC, abstractmethod
from typing import Dict, List, Any


class ITextureManagerService(ABC):
    """
    贴图管理服务接口

    职责:
    - 提供贴图管理相关业务逻辑
    - 包括贴图查询、过滤、修复、处理等功能
    """

    @abstractmethod
    def get_all_textures(self) -> Dict[str, Any]:
        """
        获取所有贴图信息

        返回:
            贴图信息字典，格式为 {材质名: {贴图名: 贴图信息}}
        """
        pass

    @abstractmethod
    def filter_textures(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        过滤贴图

        参数:
            filters: 过滤条件，如 {'isLoaded': False, 'minSize': 10}

        返回:
            过滤后的贴图信息
        """
        pass

    @abstractmethod
    def fix_missing_textures(self, search_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        修复缺失贴图

        参数:
            search_path: 搜索路径
            options: 修复选项

        返回:
            修复结果，包含修复数量、失败列表等
        """
        pass

    @abstractmethod
    def process_images(self, texture_list: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        批量处理图像

        参数:
            texture_list: 贴图节点列表
            options: 处理选项，如格式、缩放比例等

        返回:
            处理结果
        """
        pass

    @abstractmethod
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
        pass
