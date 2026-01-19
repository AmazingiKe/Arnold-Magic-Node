from abc import ABC, abstractmethod
from typing import Dict, List, Any


class IFileSystemRepository(ABC):
    """
    文件系统仓储接口

    职责:
    - 封装文件系统操作
    - 提供文件搜索和操作接口
    """

    @abstractmethod
    def search_files(self, search_path: str, exclude_list: List[str] = None,
                    extensions: List[str] = None) -> Dict[str, str]:
        """
        搜索文件

        参数:
            search_path: 搜索路径
            exclude_list: 排除列表
            extensions: 文件扩展名列表

        返回:
            文件名字典，格式为 {文件名: 文件路径}
        """
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在

        参数:
            file_path: 文件路径

        返回:
            是否存在
        """
        pass

    @abstractmethod
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件信息

        参数:
            file_path: 文件路径

        返回:
            文件信息字典，包含大小、修改时间等
        """
        pass

    @abstractmethod
    def create_directory(self, dir_path: str) -> bool:
        """
        创建目录

        参数:
            dir_path: 目录路径

        返回:
            是否成功
        """
        pass
