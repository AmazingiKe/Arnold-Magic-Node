from abc import ABC, abstractmethod
from typing import Dict, Any


class IConfigRepository(ABC):
    """
    配置仓储接口

    职责:
    - 封装配置文件的读写操作
    - 提供配置验证功能
    """

    @abstractmethod
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件

        参数:
            config_path: 配置文件路径

        返回:
            配置字典
        """
        pass

    @abstractmethod
    def save_config(self, config_path: str, config: Dict[str, Any]) -> None:
        """
        保存配置文件

        参数:
            config_path: 配置文件路径
            config: 配置字典
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置

        参数:
            config: 配置字典

        返回:
            是否有效
        """
        pass
