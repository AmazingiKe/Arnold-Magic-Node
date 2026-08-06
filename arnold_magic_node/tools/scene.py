"""场景查询与节点名称优化工具。"""

import maya.cmds as cmds

from ..arnold_magic_core import NodeProcessor
from .runtime import load_config
from .selection import get_scene_nodes_by_type


class SceneQueryTool(object):
    """为 AOV、材质修复等功能提供场景查询。"""

    @staticmethod
    def get_scene_arnold_lights_and_type():
        result = {}
        light_types = (
            "aiAreaLight", "aiSkyDomeLight", "aiPhotometricLight", "aiMeshLight",
            "aiLightPortal", "directionalLight", "spotLight", "areaLight", "pointLight",
        )
        for light_type in light_types:
            for light_shape in cmds.ls(type=light_type) or []:
                parents = cmds.listRelatives(light_shape, parent=True) or []
                if parents:
                    result[parents[0]] = light_type
        return result

    @staticmethod
    def get_light_group(lights):
        result = {}
        for light_name in lights:
            try:
                light_group = cmds.getAttr("{}.aiAov".format(light_name))
                if not isinstance(light_group, str):
                    light_group = "default"
            except Exception:
                light_group = "default"
            result.setdefault(light_group, []).append(light_name)
        return result

    @staticmethod
    def get_file_texture_paths(material_node):
        file_paths = {}
        visited = set()

        def traverse(node_name):
            if node_name in visited:
                return
            visited.add(node_name)
            upstream_nodes = cmds.listConnections(
                node_name,
                source=True,
                destination=False,
                skipConversionNodes=True,
            ) or []
            for source_node in upstream_nodes:
                if cmds.nodeType(source_node) == "file":
                    attribute = source_node + ".fileTextureName"
                    if cmds.objExists(attribute):
                        file_paths[source_node] = cmds.getAttr(attribute)
                else:
                    traverse(source_node)

        traverse(material_node)
        return file_paths


class SceneNodeRenameTool(object):
    """保留旧场景重命名辅助类的单节点入口。"""

    @staticmethod
    def node_rename(old_name, new_name):
        return cmds.rename(old_name, new_name)


class SceneNameOptimizationTool(object):
    """依照用户配置批量替换场景节点名称。"""

    def __init__(self):
        self.node_processor = NodeProcessor()
        self.scene_nodes = get_scene_nodes_by_type() or {}
        self.config = load_config()

    def run(self):
        replace_params = self.config["optimized_scene_node_name"]["replace_param"]
        for node_names in self.scene_nodes.values():
            for node_name in node_names:
                parts = [part for part in node_name.split("|") if part]
                for part_name in parts:
                    for replace_param in replace_params:
                        self.node_processor.replace_node_name(
                            enabled=replace_param["switch_checkbox"],
                            ignore_case=replace_param["case_sensitive"],
                            target=replace_param["target_cont"],
                            replacement=replace_param["replace_cont"],
                            node_name=part_name,
                        )

    main = run


def optimize_scene_names():
    return SceneNameOptimizationTool().run()


# 兼容旧名称。
GetNodeData = SceneQueryTool
Scene_Name_optimization = SceneNodeRenameTool
SceneNameOptimization = SceneNameOptimizationTool


__all__ = [
    "GetNodeData",
    "SceneNameOptimization",
    "SceneNameOptimizationTool",
    "SceneNodeRenameTool",
    "SceneQueryTool",
    "Scene_Name_optimization",
    "optimize_scene_names",
]
