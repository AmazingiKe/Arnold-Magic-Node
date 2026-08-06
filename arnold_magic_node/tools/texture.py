"""贴图、UV 与直接节点连接工具。"""

from ..core.magic_connection import (
    contains_udim_number,
    match_texture_channels,
    normalize_texture_name,
)
from ..maya.textures import MayaTextureAdapter
from .feedback import FeedbackPrompt
from .runtime import (
    load_config,
    load_language,
)
from .selection import process_selected_nodes


_direct_output_node = None

UV_CONNECTION_ATTRIBUTES = (
    "coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV",
    "stagger", "wrapU", "wrapV", "repeatUV", "offset", "rotateUV",
    "noiseUV", "vertexUvOne", "vertexUvTwo", "vertexUvThree",
    "vertexCameraOne",
)


def apply_texture_color_spaces(
    node_list,
    filter_data,
    color_space_config,
    adapter,
    feedback=None,
    matching_channels=None,
):
    """匹配贴图通道并通过 Maya 适配器设置颜色空间。"""

    if matching_channels is None:
        texture_files = {
            node_name: adapter.file_texture_path(node_name)
            for node_name in node_list
        }
        matching_channels = match_texture_channels(texture_files, filter_data)
    for node_name, channel in matching_channels.items():
        color_space = color_space_config.get(channel)
        if color_space is None:
            continue
        adapter.set_color_space(node_name, color_space)
        if feedback is not None:
            feedback.CP(
                "{} 设置为色彩空间 <{}>".format(node_name, color_space)
            )
    return matching_channels


def apply_file_udim(node_list, adapter, feedback=None):
    """根据贴图路径检测 UDIM 并写入对应节点。"""

    result = {}
    for node_name in node_list:
        file_path = adapter.file_texture_path(node_name)
        enabled = contains_udim_number(normalize_texture_name(file_path))
        adapter.set_udim(node_name, enabled)
        result[node_name] = enabled
        if feedback is not None:
            feedback.CP("{} {} UDIM".format(node_name, "启用" if enabled else "关闭"))
    return result


def unify_uv_nodes_for_files(node_list, uv_list=None, adapter=None):
    """删除指定旧 UV 节点，并让 file 节点共享一个 place2dTexture。"""

    adapter = adapter or MayaTextureAdapter()
    if uv_list is not None:
        for uv_node in uv_list:
            try:
                adapter.delete(uv_node)
            except Exception:
                pass
    new_uv_node = adapter.create_shading_node(
        "place2dTexture", at=True, name="place2dTexture"
    )
    for file_node in node_list:
        for attribute in UV_CONNECTION_ATTRIBUTES:
            adapter.connect_attr(
                new_uv_node + "." + attribute,
                file_node + "." + attribute,
                force=True,
            )
        adapter.connect_attr(
            new_uv_node + ".outUV", file_node + ".uvCoord", force=True
        )
        adapter.connect_attr(
            new_uv_node + ".outUvFilterSize",
            file_node + ".uvFilterSize",
            force=True,
        )
    return new_uv_node


def set_uv_preset(uv_preset, adapter=None):
    """将所选 file 节点的 UV 平铺模式设为菜单指定值。"""

    adapter = adapter or MayaTextureAdapter()
    feedback = FeedbackPrompt(adapter)
    language = load_language()["ArnoldMagicNode"]
    widget_language = language["AMDUI_WIN"]["create_widgets"]
    tool_language = language["UVPM"]
    selected = process_selected_nodes(adapter=adapter, feedback=feedback)
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
            adapter.set_attr(node_name + ".uvTilingMode", mode)
            feedback.CP(
                "{}<{}>{}{}".format(
                    tool_language["01"], node_name, tool_language["02"], mode
                )
            )
    except Exception as error:
        feedback.CPW("{} :{}".format(tool_language["03"], error))


def set_color_space_preset(color_space_preset, adapter=None):
    """为所选 file 节点写入颜色空间。"""

    adapter = adapter or MayaTextureAdapter()
    feedback = FeedbackPrompt(adapter)
    selected = process_selected_nodes(adapter=adapter, feedback=feedback)
    language = load_language()["ArnoldMagicNode"]["CSPM"]
    if selected is None:
        return
    if "file" not in selected:
        feedback.CPW(language["01"])
        return

    for node_name in selected["file"]:
        adapter.set_attr(
            node_name + ".colorSpace", color_space_preset, value_type="string"
        )
        feedback.CP(
            "{}<{}>{}<{}>".format(
                language["02"], node_name, language["02"], color_space_preset
            )
        )


def auto_set_texture_color_space(adapter=None):
    """按用户配置为选中贴图自动设置颜色空间。"""

    adapter = adapter or MayaTextureAdapter()
    feedback = FeedbackPrompt(adapter)
    language = load_language()["ArnoldMagicNode"]["ASTCS"]
    config = load_config()
    selected = process_selected_nodes(adapter=adapter, feedback=feedback)
    if selected is None:
        return
    if "file" not in selected:
        feedback.CP(language["01"])
        return

    return apply_texture_color_spaces(
        selected["file"],
        config["texture_filter_params"],
        config["color_space_params"]["params"],
        adapter,
        feedback,
    )


def auto_set_file_node_udim(adapter=None):
    """为选中的 file 节点自动识别并设置 UDIM。"""

    adapter = adapter or MayaTextureAdapter()
    feedback = FeedbackPrompt(adapter)
    selected = process_selected_nodes(adapter=adapter, feedback=feedback)
    language = load_language()["ArnoldMagicNode"]["ASFNU"]
    if selected is None:
        return
    if "file" not in selected:
        feedback.CP(language["01"])
        return
    return apply_file_udim(selected["file"], adapter, feedback)


class DirectConnectionTool(object):
    """两次触发式的材质输出节点直连工具。"""

    def __init__(self, adapter=None):
        global _direct_output_node

        self.adapter = adapter or MayaTextureAdapter()
        self.feedback = FeedbackPrompt(self.adapter)
        self.language = load_language()["ArnoldMagicNode"]["DC_Button"]
        self.selected = process_selected_nodes(
            adapter=self.adapter, feedback=self.feedback
        )
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
                    existing = self.adapter.list_connections(
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
                        self.adapter.connect_attr(
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


def connect_directly(adapter=None):
    """执行一次直接连接操作。"""

    return DirectConnectionTool(adapter=adapter)


def unify_uv_nodes(adapter=None):
    """将所选 file 节点复用为同一组 UV 节点。"""

    adapter = adapter or MayaTextureAdapter()
    selected = process_selected_nodes(adapter=adapter)
    if selected is None or "file" not in selected:
        return
    uv_nodes = selected.get("place2dTexture")
    return unify_uv_nodes_for_files(selected["file"], uv_nodes, adapter)


# 旧 UI 与 Shelf 调用的兼容名称；新代码使用上方 snake_case API。
uv_preset_menu = set_uv_preset
color_space_preset_menu = set_color_space_preset
AutoSet_TexColorSpace = auto_set_texture_color_space
direct_connection_button = connect_directly
unify_uv_node_button = unify_uv_nodes


__all__ = [
    "AutoSet_TexColorSpace",
    "DirectConnectionTool",
    "apply_file_udim",
    "apply_texture_color_spaces",
    "auto_set_file_node_udim",
    "auto_set_texture_color_space",
    "color_space_preset_menu",
    "connect_directly",
    "direct_connection_button",
    "set_color_space_preset",
    "set_uv_preset",
    "unify_uv_node_button",
    "unify_uv_nodes_for_files",
    "unify_uv_nodes",
    "uv_preset_menu",
]
