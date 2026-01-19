import os
from typing import Dict, List, Any
from .i_file_system_repository import IFileSystemRepository


class FileSystemRepository(IFileSystemRepository):
    """
    文件系统仓储实现

    职责:
    - 封装文件系统操作
    - 提供文件搜索和操作接口
    """

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
        if not os.path.exists(search_path):
            return {}

        if exclude_list is None:
            exclude_list = []

        files_dict = {}

        for root, dirs, files in os.walk(search_path):
            for filename in files:
                filepath = os.path.join(root, filename)

                if self._should_exclude(filepath, exclude_list):
                    continue

                if extensions and not self._has_extension(filename, extensions):
                    continue

                files_dict[filename] = filepath

        return files_dict

    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在

        参数:
            file_path: 文件路径

        返回:
            是否存在
        """
        return os.path.exists(file_path) and os.path.isfile(file_path)

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件信息

        参数:
            file_path: 文件路径

        返回:
            文件信息字典，包含大小、修改时间等
        """
        if not self.file_exists(file_path):
            return {}

        stat_info = os.stat(file_path)

        return {
            "size": stat_info.st_size,
            "modified_time": stat_info.st_mtime,
            "created_time": stat_info.st_ctime,
            "extension": os.path.splitext(file_path)[1]
        }

    def create_directory(self, dir_path: str) -> bool:
        """
        创建目录

        参数:
            dir_path: 目录路径

        返回:
            是否成功
        """
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败: {dir_path}, 错误: {e}")
            return False

    def _should_exclude(self, filepath: str, exclude_list: List[str]) -> bool:
        """
        检查是否应该排除该文件

        参数:
            filepath: 文件路径
            exclude_list: 排除列表

        返回:
            是否应该排除
        """
        for exclude_pattern in exclude_list:
            if exclude_pattern in filepath:
                return True
        return False

    def _has_extension(self, filename: str, extensions: List[str]) -> bool:
        """
        检查文件是否有指定扩展名

        参数:
            filename: 文件名
            extensions: 扩展名列表

        返回:
            是否有指定扩展名
        """
        _, ext = os.path.splitext(filename)
        return ext.lower() in [e.lower() if e.startswith('.') else f'.{e.lower()}' for e in extensions]
