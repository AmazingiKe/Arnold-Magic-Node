"""Maya 选择与场景节点查询工具。"""

from arnold_magic_node.maya.scene import MayaSceneAdapter
from arnold_magic_node._qt_compat import QCoreApplication
from .feedback import FeedbackPrompt


def process_selected_nodes(selected_nodes=None, adapter=None, feedback=None):
    """按节点类型归类当前选择。"""

    adapter = adapter or MayaSceneAdapter()
    feedback = feedback or FeedbackPrompt(adapter)
    if selected_nodes is None:
        selected_nodes = adapter.list_nodes(sl=True)
    if not selected_nodes:
        feedback.warn(
            QCoreApplication.translate(
                "ProcessSelectedNodes", "Please select the corresponding node first!"
            )
        )
        return None

    result = {}
    for node_name in selected_nodes:
        result.setdefault(adapter.node_type(node_name), []).append(node_name)
    return result


def get_scene_nodes_by_type(adapter=None, feedback=None):
    """查询场景节点并按 Maya 节点类型分组。"""

    adapter = adapter or MayaSceneAdapter()
    feedback = feedback or FeedbackPrompt(adapter)
    all_nodes = adapter.list_nodes(
        geometry=True, lights=True, cameras=True, long=True,
        materials=True, textures=True, assemblies=True,
    )
    if not all_nodes:
        feedback.warn(
            QCoreApplication.translate("ProcessSelectedNodes", "No nodes found")
        )
        return None

    result = {}
    for node_name in all_nodes:
        try:
            node_type = adapter.node_type(node_name)
        except Exception as error:
            node_type = "unknown"
            feedback.warn(
                QCoreApplication.translate(
                    "ProcessSelectedNodes", "Failed to get node type: {0}, error: {1}"
                ).format(node_name, error)
            )
        result.setdefault(node_type, []).append(node_name)
    return result


__all__ = ["get_scene_nodes_by_type", "process_selected_nodes"]
