"""Maya 选择与场景节点查询工具。"""

from collections import defaultdict

import maya.cmds as cmds

from .feedback import FeedbackPrompt
from .runtime import load_language


def process_selected_nodes(selected_nodes=None):
    """按节点类型归类当前选择，保持旧 ``process_sl_data`` 的行为。"""

    language = load_language()["ArnoldMagicNodeLibs"]["process_sl_data"]
    feedback = FeedbackPrompt()
    if selected_nodes is None:
        selected_nodes = cmds.ls(sl=True)
    if not selected_nodes:
        feedback.CPW(language["01"])
        return None

    result = {}
    for node_name in selected_nodes:
        result.setdefault(cmds.nodeType(node_name), []).append(node_name)
    return result


def get_scene_nodes_by_type():
    """查询场景节点并按 Maya 节点类型分组。"""

    feedback = FeedbackPrompt()
    all_nodes = cmds.ls(
        geometry=True,
        lights=True,
        cameras=True,
        long=True,
        materials=True,
        textures=True,
        assemblies=True,
    )
    if not all_nodes:
        feedback.CPW("没有找到节点")
        return None

    result = defaultdict(list)
    for node_name in all_nodes:
        try:
            node_type = cmds.nodeType(node_name)
        except Exception as error:
            node_type = "unknown"
            print("获取节点类型失败: {}, 错误: {}".format(node_name, error))
        result[node_type].append(node_name)
    return dict(result)


__all__ = ["get_scene_nodes_by_type", "process_selected_nodes"]
