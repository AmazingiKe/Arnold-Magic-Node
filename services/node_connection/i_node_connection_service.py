from abc import ABC, abstractmethod
from typing import Dict, List, Any


class INodeConnectionService(ABC):
    """
    节点连接服务接口

    职责:
    - 提供节点连接相关业务逻辑
    - 包括自动连接、直接连接、UV统一等功能
    """

    @abstractmethod
    def auto_connect_nodes(self, material_name: str, texture_nodes: List[str],
                          options: Dict[str, Any]) -> Dict[str, Any]:
        """
        自动连接节点

        参数:
            material_name: 材质名称
            texture_nodes: 贴图节点列表
            options: 连接选项

        返回:
            连接结果
        """
        pass

    @abstractmethod
    def direct_connect_nodes(self, material_name: str, texture_nodes: List[str],
                            channel_map: Dict[str, str]) -> bool:
        """
        直接连接节点

        参数:
            material_name: 材质名称
            texture_nodes: 贴图节点列表
            channel_map: 通道映射

        返回:
            是否成功
        """
        pass

    @abstractmethod
    def unify_uv_nodes(self, texture_nodes: List[str]) -> bool:
        """
        统一UV节点

        参数:
            texture_nodes: 贴图节点列表

        返回:
            是否成功
        """
        pass

    @abstractmethod
    def set_color_space(self, texture_nodes: List[str], color_space: str) -> bool:
        """
        设置色彩空间

        参数:
            texture_nodes: 贴图节点列表
            color_space: 色彩空间

        返回:
            是否成功
        """
        pass

    @abstractmethod
    def set_udim_mode(self, texture_nodes: List[str]) -> bool:
        """
        设置UDIM模式

        参数:
            texture_nodes: 贴图节点列表

        返回:
            是否成功
        """
        pass
