from abc import ABC, abstractmethod
from typing import Dict, List, Any


class INodeDataRepository(ABC):
    """
    节点数据仓储接口

    职责:
    - 封装Maya节点数据的访问
    - 提供节点查询和操作接口
    """

    @abstractmethod
    def get_all_nodes(self, node_types: List[str]) -> List[str]:
        """
        获取指定类型的所有节点

        参数:
            node_types: 节点类型列表

        返回:
            节点名称列表
        """
        pass

    @abstractmethod
    def get_node_attribute(self, node_name: str, attribute: str) -> Any:
        """
        获取节点属性

        参数:
            node_name: 节点名称
            attribute: 属性名称

        返回:
            属性值
        """
        pass

    @abstractmethod
    def set_node_attribute(self, node_name: str, attribute: str, value: Any) -> None:
        """
        设置节点属性

        参数:
            node_name: 节点名称
            attribute: 属性名称
            value: 属性值
        """
        pass

    @abstractmethod
    def get_upstream_nodes(self, node_name: str, node_types: List[str]) -> List[str]:
        """
        获取上游节点

        参数:
            node_name: 节点名称
            node_types: 节点类型列表

        返回:
            上游节点名称列表
        """
        pass

    @abstractmethod
    def get_all_textures(self) -> Dict[str, Any]:
        """
        获取所有贴图信息

        返回:
            贴图信息字典，格式为 {材质名: {贴图名: 贴图信息}}
        """
        pass

    @abstractmethod
    def set_texture_path(self, texture_node: str, new_path: str) -> None:
        """
        设置贴图路径

        参数:
            texture_node: 贴图节点名称
            new_path: 新路径
        """
        pass
