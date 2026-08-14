"""贴图、UV 与直接节点连接工具。"""

from arnold_magic_node.core.magic_connection import (
    contains_udim_number,
    match_texture_channels,
    normalize_texture_name,
)
from arnold_magic_node.maya.textures import MayaTextureAdapter
from arnold_magic_node._qt_compat import QCoreApplication
from .feedback import FeedbackPrompt
from .runtime import load_config
from .selection import process_selected_nodes


_direct_output_node = None

UV_CONNECTION_ATTRIBUTES = (
    "coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV",
    "stagger", "wrapU", "wrapV", "repeatUV", "offset", "rotateUV",
    "noiseUV", "vertexUvOne", "vertexUvTwo", "vertexUvThree",
    "vertexCameraOne",
)

def uv_preset_mode_map():
    """返回「显示名 -> 模式索引」映射，与主窗口菜单使用同一组译文。

    context 与 source 必须直接写在 translate() 内，lupdate 才能提取；
    列表顺序与 file 节点的 uvTilingMode 枚举值一一对应。
    """

    translated_names = [
        QCoreApplication.translate("UvPresetMenu", "Disabled"),
        QCoreApplication.translate("UvPresetMenu", "Type 0 (ZBrush)"),
        QCoreApplication.translate("UvPresetMenu", "Type 1 (Mudbox)"),
        QCoreApplication.translate("UvPresetMenu", "UDIM (Mari)"),
        QCoreApplication.translate("UvPresetMenu", "Show Tiling"),
    ]
    return {name: index for index, name in enumerate(translated_names)}


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
            feedback.print_message(
                QCoreApplication.translate(
                    "TextureTools", "{0} set to color space <{1}>"
                ).format(node_name, color_space)
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
            feedback.print_message(
                QCoreApplication.translate("TextureTools", "{0} {1} UDIM").format(
                    node_name,
                    QCoreApplication.translate("TextureTools", "Enabled")
                    if enabled
                    else QCoreApplication.translate("TextureTools", "Disabled"),
                )
            )
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
    selected = process_selected_nodes(adapter=adapter, feedback=feedback)
    if selected is None:
        return
    if "file" not in selected:
        feedback.warn(
            QCoreApplication.translate(
                "UvPresetMenu", "Please select a texture node"
            )
        )
        return

    mode = uv_preset_mode_map().get(uv_preset)
    if mode is None:
        return

    try:
        for node_name in selected["file"]:
            adapter.set_attr(node_name + ".uvTilingMode", mode)
            feedback.print_message(
                "{}<{}>{}{}".format(
                    QCoreApplication.translate("UvPresetMenu", "Set UV tiling mode for"),
                    node_name,
                    QCoreApplication.translate("UvPresetMenu", "node to:"),
                    mode,
                )
            )
    except Exception as error:
        feedback.warn(
            "{} :{}".format(
                QCoreApplication.translate("UvPresetMenu", "Error setting:"), error
            )
        )


def set_color_space_preset(color_space_preset, adapter=None):
    """为所选 file 节点写入颜色空间。"""

    adapter = adapter or MayaTextureAdapter()
    feedback = FeedbackPrompt(adapter)
    selected = process_selected_nodes(adapter=adapter, feedback=feedback)
    if selected is None:
        return
    if "file" not in selected:
        feedback.warn(
            QCoreApplication.translate(
                "ColorSpacePresetMenu", "Please select a texture node!"
            )
        )
        return

    for node_name in selected["file"]:
        adapter.set_attr(
            node_name + ".colorSpace", color_space_preset, value_type="string"
        )
        feedback.print_message(
            "{}<{}>{}<{}>".format(
                QCoreApplication.translate("ColorSpacePresetMenu", "Set"),
                node_name,
                QCoreApplication.translate("ColorSpacePresetMenu", "to"),
                color_space_preset,
            )
        )


def auto_set_texture_color_space(adapter=None):
    """按用户配置为选中贴图自动设置颜色空间。"""

    adapter = adapter or MayaTextureAdapter()
    feedback = FeedbackPrompt(adapter)
    config = load_config()
    selected = process_selected_nodes(adapter=adapter, feedback=feedback)
    if selected is None:
        return
    if "file" not in selected:
        feedback.print_message(
            QCoreApplication.translate(
                "AutoSetTextureColorSpace", "Please select a texture node!"
            )
        )
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
    if selected is None:
        return
    if "file" not in selected:
        feedback.print_message(
            QCoreApplication.translate(
                "AutoSetFileNodeUdim", "Please select a texture node"
            )
        )
        return
    return apply_file_udim(selected["file"], adapter, feedback)


def connect_directly(adapter=None):
    """两次触发式直连：第一次记录输出节点，第二次连接材质。"""

    global _direct_output_node

    adapter = adapter or MayaTextureAdapter()
    feedback = FeedbackPrompt(adapter)
    selected = process_selected_nodes(adapter=adapter, feedback=feedback)
    if selected is None:
        return

    shading_engines = selected.get("shadingEngine") or []
    if shading_engines:
        _direct_output_node = shading_engines[0]
        feedback.print_message(
            "{}<{}>".format(
                QCoreApplication.translate(
                    "DirectConnectionTool", "Node configured successfully"
                ),
                _direct_output_node,
            )
        )
        return

    if _direct_output_node is None:
        feedback.print_message(
            QCoreApplication.translate(
                "DirectConnectionTool", "Please select an output node first"
            )
        )
        return

    output_ports = ("outColor", "outAlpha", "outValue")
    for node_names in selected.values():
        for node_name in node_names:
            for output_port in output_ports:
                existing = adapter.list_connections(
                    _direct_output_node,
                    source=True,
                    destination=False,
                    plugs=True,
                )
                existing_node_name = existing[0].split(".")[0] if existing else None
                if existing_node_name == node_name:
                    continue

                try:
                    adapter.connect_attr(
                        node_name + "." + output_port,
                        _direct_output_node + ".surfaceShader",
                        force=True,
                    )
                    return
                except Exception:
                    feedback.warn(
                        "{}<{}:{}>{}<{}:shadingEngine>{}".format(
                            QCoreApplication.translate("DirectConnectionTool", "Your"),
                            node_name,
                            output_port,
                            QCoreApplication.translate(
                                "DirectConnectionTool", "node cannot connect to"
                            ),
                            _direct_output_node,
                            QCoreApplication.translate(
                                "DirectConnectionTool", "on the node"
                            ),
                        )
                    )


def unify_uv_nodes(adapter=None):
    """将所选 file 节点复用为同一组 UV 节点。"""

    adapter = adapter or MayaTextureAdapter()
    selected = process_selected_nodes(adapter=adapter)
    if selected is None or "file" not in selected:
        return
    uv_nodes = selected.get("place2dTexture")
    return unify_uv_nodes_for_files(selected["file"], uv_nodes, adapter)


__all__ = [
    "apply_file_udim",
    "apply_texture_color_spaces",
    "auto_set_file_node_udim",
    "auto_set_texture_color_space",
    "connect_directly",
    "set_color_space_preset",
    "set_uv_preset",
    "unify_uv_nodes_for_files",
    "unify_uv_nodes",
    "uv_preset_mode_map",
]
