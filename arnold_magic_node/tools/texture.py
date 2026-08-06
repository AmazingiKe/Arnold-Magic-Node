"""贴图、UV 与直接节点连接工具。"""

import maya.cmds as cmds

from ..arnold_magic_core import NodeProcessor
from .feedback import FeedbackPrompt
from .runtime import (
    load_config,
    load_language,
)
from .selection import process_selected_nodes


_direct_output_node = None


def set_uv_preset(uv_preset):
    """将所选 file 节点的 UV 平铺模式设为菜单指定值。"""

    feedback = FeedbackPrompt()
    language = load_language()["ArnoldMagicNode"]
    widget_language = language["AMDUI_WIN"]["create_widgets"]
    tool_language = language["UVPM"]
    selected = process_selected_nodes()
    if selected is None:
        return
    if "file" not in selected:
        feedback.CPW(tool_language["04"])
        return

    mode_values = {
        widget_language["uv_preset"][0]: 0,
        widget_language["uv_preset"][1]: 1,
        widget_language["uv_preset"][2]: 2,
        widget_language["uv_preset"][3]: 3,
        widget_language["uv_preset"][4]: 4,
    }
    mode = mode_values.get(uv_preset)
    if mode is None:
        return

    try:
        for node_name in selected["file"]:
            cmds.setAttr(node_name + ".uvTilingMode", mode)
            feedback.CP(
                "{}<{}>{}{}".format(
                    tool_language["01"], node_name, tool_language["02"], mode
                )
            )
    except Exception as error:
        feedback.CPW("{} :{}".format(tool_language["03"], error))


def set_color_space_preset(color_space_preset):
    """为所选 file 节点写入颜色空间。"""

    feedback = FeedbackPrompt()
    selected = process_selected_nodes()
    language = load_language()["ArnoldMagicNode"]["CSPM"]
    if selected is None:
        return
    if "file" not in selected:
        feedback.CPW(language["01"])
        return

    for node_name in selected["file"]:
        cmds.setAttr(node_name + ".colorSpace", color_space_preset, type="string")
        feedback.CP(
            "{}<{}>{}<{}>".format(
                language["02"], node_name, language["02"], color_space_preset
            )
        )


def auto_set_texture_color_space():
    """按用户配置为选中贴图自动设置颜色空间。"""

    node_processor = NodeProcessor()
    feedback = FeedbackPrompt()
    language = load_language()["ArnoldMagicNode"]["ASTCS"]
    config = load_config()
    selected = process_selected_nodes()
    if selected is None:
        return
    if "file" not in selected:
        feedback.CP(language["01"])
        return

    node_processor.AutoSetTexColorSpace(
        config["color_space_params"]["params"],
        selected["file"],
        config["texture_filter_params"],
    )


def auto_set_file_node_udim():
    """为选中的 file 节点自动识别并设置 UDIM。"""

    node_processor = NodeProcessor()
    feedback = FeedbackPrompt()
    selected = process_selected_nodes()
    language = load_language()["ArnoldMagicNode"]["ASFNU"]
    if selected is None:
        return
    if "file" not in selected:
        feedback.CP(language["01"])
        return
    node_processor.auto_set_udim(selected["file"])


class DirectConnectionTool(object):
    """两次触发式的材质输出节点直连工具。"""

    def __init__(self):
        global _direct_output_node

        self.feedback = FeedbackPrompt()
        self.language = load_language()["ArnoldMagicNode"]["DC_Button"]
        self.selected = process_selected_nodes()
        if self.selected is None:
            return

        shading_engines = self.selected.get("shadingEngine") or []
        if shading_engines:
            _direct_output_node = shading_engines[0]
            self.feedback.CP(
                "{}<{}>".format(self.language["__init__"]["01"], _direct_output_node)
            )
            return

        if _direct_output_node is None:
            self.feedback.CP(self.language["__init__"]["02"])
            return

        self.connect()

    def connect(self):
        output_ports = ("outColor", "outAlpha", "outValue")
        language = self.language["connection_node"]
        for node_names in self.selected.values():
            for node_name in node_names:
                for output_port in output_ports:
                    existing = cmds.listConnections(
                        _direct_output_node,
                        source=True,
                        destination=False,
                        plugs=True,
                    )
                    existing_node_name = None
                    if existing:
                        existing_node_name = existing[0].split(".")[0]
                    if existing_node_name == node_name:
                        continue

                    try:
                        cmds.connectAttr(
                            node_name + "." + output_port,
                            _direct_output_node + ".surfaceShader",
                            force=True,
                        )
                        return
                    except Exception:
                        self.feedback.CPW(
                            "{}<{}:{}>{}<{}:shadingEngine>{}".format(
                                language["01"],
                                node_name,
                                output_port,
                                language["02"],
                                _direct_output_node,
                                language["03"],
                            )
                        )


def connect_directly():
    """执行一次直接连接操作。"""

    return DirectConnectionTool()


def unify_uv_nodes():
    """将所选 file 节点复用为同一组 UV 节点。"""

    selected = process_selected_nodes()
    if selected is None or "file" not in selected:
        return
    uv_nodes = selected.get("place2dTexture")
    NodeProcessor().unify_uv_node(selected["file"], uv_nodes)


# 旧 UI 与 Shelf 调用的兼容名称；新代码使用上方 snake_case API。
uv_preset_menu = set_uv_preset
color_space_preset_menu = set_color_space_preset
AutoSet_TexColorSpace = auto_set_texture_color_space
direct_connection_button = connect_directly
unify_uv_node_button = unify_uv_nodes


__all__ = [
    "AutoSet_TexColorSpace",
    "DirectConnectionTool",
    "auto_set_file_node_udim",
    "auto_set_texture_color_space",
    "color_space_preset_menu",
    "connect_directly",
    "direct_connection_button",
    "set_color_space_preset",
    "set_uv_preset",
    "unify_uv_node_button",
    "unify_uv_nodes",
    "uv_preset_menu",
]
