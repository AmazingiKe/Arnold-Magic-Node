"""场景节点名称优化工具。"""

from arnold_magic_node.core.naming import replacement_name
from arnold_magic_node.maya.scene import MayaSceneAdapter
from arnold_magic_node._qt_compat import QCoreApplication
from .feedback import FeedbackPrompt
from .runtime import load_config
from .selection import get_scene_nodes_by_type


class SceneNameOptimizationTool(object):
    """依照用户配置批量替换场景节点名称。"""

    def __init__(self, adapter=None, scene_nodes=None, config=None):
        self.adapter = adapter or MayaSceneAdapter()
        self.feedback = FeedbackPrompt(self.adapter)
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
                            self.feedback.print_message(
                                QCoreApplication.translate(
                                    "SceneNameOptimizationTool", "Renamed: {0} -> {1}"
                                ).format(part_name, new_name)
                            )
                        except Exception as error:
                            self.feedback.warn(
                                QCoreApplication.translate(
                                    "SceneNameOptimizationTool",
                                    "Rename failed: {0} -> {1}, error: {2}",
                                ).format(part_name, new_name, error)
                            )


__all__ = [
    "SceneNameOptimizationTool",
]
