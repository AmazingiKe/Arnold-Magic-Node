from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List


class IConfigManager(ABC):
    """
    配置管理器接口

    职责:
    - 提供统一的配置访问接口
    - 支持嵌套配置的读写
    - 支持配置的重新加载和保存
    """

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        参数:
            key: 配置键
            default: 默认值

        返回:
            配置值
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        参数:
            key: 配置键
            value: 配置值
        """
        pass

    @abstractmethod
    def get_nested(self, key_path: List[str], default: Any = None) -> Any:
        """
        获取嵌套配置值

        参数:
            key_path: 配置键路径，如 ['level1', 'level2', 'key']
            default: 默认值

        返回:
            配置值
        """
        pass

    @abstractmethod
    def set_nested(self, key_path: List[str], value: Any) -> None:
        """
        设置嵌套配置值

        参数:
            key_path: 配置键路径，如 ['level1', 'level2', 'key']
            value: 配置值
        """
        pass

    @abstractmethod
    def reload(self) -> None:
        """
        重新加载配置
        """
        pass

    @abstractmethod
    def save(self) -> None:
        """
        保存配置
        """
        pass
