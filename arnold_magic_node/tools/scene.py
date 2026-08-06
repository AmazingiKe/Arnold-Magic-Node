"""场景查询与节点名称优化工具。"""

from ..core.naming import replacement_name
from ..maya.scene import MayaSceneAdapter
from .runtime import load_config
from .selection import get_scene_nodes_by_type


class SceneQueryTool(object):
    """为 AOV、材质修复等功能提供场景查询。"""

    LIGHT_TYPES = (
            "aiAreaLight", "aiSkyDomeLight", "aiPhotometricLight", "aiMeshLight",
            "aiLightPortal", "directionalLight", "spotLight", "areaLight", "pointLight",
    )

    def __init__(self, adapter=None):
        self.adapter = adapter or MayaSceneAdapter()

    def get_scene_arnold_lights_and_type(self):
        return self.adapter.arnold_lights_and_types(self.LIGHT_TYPES)

    def get_light_group(self, lights):
        return self.adapter.group_lights(lights)

    def get_file_texture_paths(self, material_node):
        return self.adapter.file_texture_paths(material_node)


class SceneNodeRenameTool(object):
    """保留旧场景重命名辅助类的单节点入口。"""

    def __init__(self, adapter=None):
        self.adapter = adapter or MayaSceneAdapter()

    def node_rename(self, old_name, new_name):
        return self.adapter.rename(old_name, new_name)


class SceneNameOptimizationTool(object):
    """依照用户配置批量替换场景节点名称。"""

    def __init__(self, adapter=None, scene_nodes=None, config=None):
        self.adapter = adapter or MayaSceneAdapter()
        self.scene_nodes = (
            get_scene_nodes_by_type(adapter=self.adapter) or {}
            if scene_nodes is None else scene_nodes
        )
        self.config = config or load_config()

    def run(self):
        replace_params = self.config["optimized_scene_node_name"]["replace_param"]
        for node_names in self.scene_nodes.values():
            for node_name in node_names:
                parts = [part for part in node_name.split("|") if part]
                for part_name in parts:
                    for replace_param in replace_params:
                        new_name = replacement_name(
                            node_name=part_name,
                            enabled=replace_param["switch_checkbox"],
                            ignore_case=replace_param["case_sensitive"],
                            target=replace_param["target_cont"],
                            replacement=replace_param["replace_cont"],
                        )
                        if new_name is None:
                            continue
                        try:
                            self.adapter.rename(part_name, new_name)
                            print("已重命名: {} -> {}".format(part_name, new_name))
                        except Exception as error:
                            print(
                                "重命名失败: {} -> {}, 错误: {}".format(
                                    part_name, new_name, error
                                )
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
