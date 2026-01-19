from typing import Dict, List, Any
from .i_node_data_repository import INodeDataRepository


class NodeDataRepository(INodeDataRepository):
    """
    节点数据仓储实现

    职责:
    - 封装Maya节点数据的访问
    - 提供节点查询和操作接口
    """

    def __init__(self):
        """
        初始化节点数据仓储
        """
        try:
            import maya.cmds as cmds
            self._cmds = cmds
            self._maya_available = True
        except ImportError:
            self._cmds = None
            self._maya_available = False

    def _check_maya_available(self) -> None:
        """
        检查Maya是否可用
        """
        if not self._maya_available:
            raise RuntimeError("Maya API不可用")

    def get_all_nodes(self, node_types: List[str]) -> List[str]:
        """
        获取指定类型的所有节点

        参数:
            node_types: 节点类型列表

        返回:
            节点名称列表
        """
        self._check_maya_available()

        nodes = []
        for node_type in node_types:
            nodes.extend(self._cmds.ls(type=node_type))
        return nodes

    def get_node_attribute(self, node_name: str, attribute: str) -> Any:
        """
        获取节点属性

        参数:
            node_name: 节点名称
            attribute: 属性名称

        返回:
            属性值
        """
        self._check_maya_available()

        return self._cmds.getAttr(f"{node_name}.{attribute}")

    def set_node_attribute(self, node_name: str, attribute: str, value: Any) -> None:
        """
        设置节点属性

        参数:
            node_name: 节点名称
            attribute: 属性名称
            value: 属性值
        """
        self._check_maya_available()

        self._cmds.setAttr(f"{node_name}.{attribute}", value)

    def get_upstream_nodes(self, node_name: str, node_types: List[str]) -> List[str]:
        """
        获取上游节点

        参数:
            node_name: 节点名称
            node_types: 节点类型列表

        返回:
            上游节点名称列表
        """
        self._check_maya_available()

        upstream_nodes = []
        connections = self._cmds.listConnections(node_name, source=True, destination=False)

        for node in connections:
            node_type = self._cmds.nodeType(node)
            if node_type in node_types or not node_types:
                upstream_nodes.append(node)

        return upstream_nodes

    def get_all_textures(self) -> Dict[str, Any]:
        """
        获取所有贴图信息

        返回:
            贴图信息字典，格式为 {材质名: {贴图名: 贴图信息}}
        """
        self._check_maya_available()

        texture_info = {}

        file_nodes = self._cmds.ls(type='file')
        for file_node in file_nodes:
            file_path = self._cmds.getAttr(f"{file_node}.fileTextureName")

            connections = self._cmds.listConnections(file_node, destination=True)
            if connections:
                material_name = connections[0]
                if material_name not in texture_info:
                    texture_info[material_name] = {}

                is_loaded = self._cmds.getAttr(f"{file_node}.fileTextureName") != ""

                texture_info[material_name][file_node] = {
                    "Path": file_path,
                    "isLoaded": is_loaded,
                    "Type": self._cmds.getAttr(f"{file_node}.type")
                }

        return texture_info

    def set_texture_path(self, texture_node: str, new_path: str) -> None:
        """
        设置贴图路径

        参数:
            texture_node: 贴图节点名称
            new_path: 新路径
        """
        self._check_maya_available()

        self._cmds.setAttr(f"{texture_node}.fileTextureName", new_path, type="string")
