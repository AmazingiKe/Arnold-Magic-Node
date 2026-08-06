"""渲染预设与 Arnold AOV 执行工具。"""

import os
import re

import maya.cmds as cmds

from .feedback import FeedbackPrompt
from .runtime import DataManager, get_runtime_paths, load_config, load_language


ATTRIBUTE_TYPES = ("bool", "int", "float", "string")


class RenderingPresetTool(object):
    """读取一个保存的渲染预设并写入当前 Maya 场景。"""

    def __init__(self, preset_name):
        self.feedback = FeedbackPrompt()
        self.data_manager = DataManager()
        self.paths = get_runtime_paths()
        self.preset_name = preset_name
        self.render_settings = self.data_manager.load_json(
            os.path.normpath(
                os.path.join(self.paths.render_preset_path, preset_name + ".json")
            )
        )
        self.config = load_config(self.paths)["render_preset_params"]
        self.language = load_language(self.paths)["ArnoldMagicNode"]["RenderPM"]

    def apply(self):
        """依照配置选择性写入默认渲染、Arnold 和 AOV 参数。"""

        if self.config["default_rendering_properties_write_options"]:
            try:
                self.set_default_rendering_properties()
                self.feedback.CP(
                    "<{}> {}".format(
                        self.preset_name, self.language["__init__"]["01"]
                    )
                )
            except Exception as error:
                self.feedback.CP(
                    "<{}> {} {}".format(
                        self.preset_name, self.language["__init__"]["02"], error
                    )
                )

        if not cmds.objExists("defaultArnoldRenderOptions"):
            self.feedback.CPW(self.language["__init__"]["03"])
            return

        if self.config.get("rendering_properties_write_options"):
            try:
                self.set_rendering_properties()
                self.feedback.CP(
                    "<{}> {}".format(
                        self.preset_name, self.language["__init__"]["04"]
                    )
                )
            except Exception as error:
                self.feedback.CP(
                    "<{}> {} {}".format(
                        self.preset_name, self.language["__init__"]["05"], error
                    )
                )

        if self.config.get("AOV_properties_properties_write_options"):
            try:
                self.delete_original_aovs()
            except Exception as error:
                self.feedback.CP(
                    "<{}> {} {}".format(
                        self.preset_name, self.language["__init__"]["06"], error
                    )
                )

            try:
                aov_properties = self.render_settings.get("AOV_properties")
                if aov_properties:
                    self.set_aovs()
                    self.feedback.CP(
                        "<{}> {}".format(
                            self.preset_name, self.language["__init__"]["07"]
                        )
                    )
                else:
                    self.feedback.CP(
                        "<{}> {}".format(
                            self.preset_name, self.language["__init__"]["08"]
                        )
                    )
            except Exception as error:
                self.feedback.CP(
                    "<{}> {} {}".format(
                        self.preset_name, self.language["__init__"]["09"], error
                    )
                )

    def _set_attributes(self, node_name, attributes):
        for attribute_name, value in attributes.items():
            try:
                cmds.setAttr("{}.{}".format(node_name, attribute_name), value)
                continue
            except Exception:
                pass
            for attribute_type in ATTRIBUTE_TYPES:
                try:
                    cmds.setAttr(
                        "{}.{}".format(node_name, attribute_name),
                        value,
                        type=attribute_type,
                    )
                    break
                except Exception:
                    pass

    def _set_node_group_attributes(self, key):
        for node_name, attributes in self.render_settings[key].items():
            self._set_attributes(node_name, attributes)

    def set_default_rendering_properties(self):
        self._set_node_group_attributes("default_rendering_properties")

    def set_rendering_properties(self):
        self._set_node_group_attributes("rendering_properties")

    def set_aovs(self):
        aov_data = self.render_settings["AOV_properties"]
        cryptomatte_node_name = None
        for aov_name in aov_data:
            if re.search("CRYPTO", aov_name.upper(), re.IGNORECASE):
                cryptomatte_node_name = cmds.shadingNode("cryptomatte", app=True)
                break

        aov_index = 0
        for aov_key, values in aov_data.items():
            aov_node = cmds.shadingNode(
                "aiAOV", app=True, name=values[0]["aov_name"]
            )
            self._set_attributes(aov_node, values[1]["aov_attributes"])

            driver_data = values[2]["driver"]
            driver_node = cmds.shadingNode(
                "aiAOVDriver", app=True, name=driver_data["driver_name"]
            )
            self._set_attributes(driver_node, driver_data["driver_attribute"])
            cmds.connectAttr(
                driver_node + ".message", aov_node + ".outputs[0].driver"
            )

            filter_data = values[3]["filter"]
            filter_node = cmds.shadingNode(
                "aiAOVFilter", app=True, name=filter_data["filter_name"]
            )
            self._set_attributes(filter_node, filter_data["filter_attribute"])
            cmds.connectAttr(
                filter_node + ".message", aov_node + ".outputs[0].filter"
            )
            cmds.connectAttr(
                aov_node + ".message",
                "defaultArnoldRenderOptions.aovList[{}]".format(aov_index),
                force=True,
            )

            if re.search("CRYPTO", aov_key.upper(), re.IGNORECASE):
                cmds.connectAttr(
                    cryptomatte_node_name + ".outColor",
                    aov_node + ".defaultValue",
                    force=True,
                )
            aov_index += 1

    def delete_original_aovs(self):
        nodes_to_keep = {
            "persp", "top", "front", "side", "defaultLightSet", "defaultObjectSet",
            "defaultLayer", "layerManager", "dof1", "dynController1",
            "globalCacheControl", "hardwareRenderGlobals", "hardwareRenderingGlobals",
            "defaultHardwareRenderGlobals", "ikSystem", "lambert1", "lightLinker1",
            "particleCloud1", "characterPartition", "renderPartition",
            "poseInterpolatorManager", "sequenceManager1", "shaderGlow1",
            "shapeEditorManager", "standardSurface1", "strokeGlobals", "time1",
            "defaultViewColorManager", "defaultArnoldDisplayDriver",
            "defaultArnoldDriver", "defaultArnoldFilter", "defaultArnoldRenderOptions",
        }
        aov_nodes = cmds.listConnections(
            "defaultArnoldRenderOptions.aovList", source=True
        )
        if aov_nodes is None:
            return

        nodes_to_delete = list(aov_nodes)
        for aov_node in aov_nodes:
            nodes_to_delete.extend(
                cmds.listConnections(
                    "{}.outputs[0].filter".format(aov_node), source=True
                )
                or []
            )
            nodes_to_delete.extend(
                cmds.listConnections(
                    "{}.outputs[0].driver".format(aov_node), source=True
                )
                or []
            )

        for node_name in nodes_to_delete:
            try:
                if node_name not in nodes_to_keep:
                    cmds.delete(node_name)
            except Exception:
                pass


def apply_rendering_preset(preset_name):
    """执行指定的渲染预设。"""

    tool = RenderingPresetTool(preset_name)
    tool.apply()
    return tool


def toggle_aovs():
    """切换当前 Arnold AOV 的 enabled 状态。"""

    feedback = FeedbackPrompt()
    if not cmds.objExists("defaultArnoldRenderOptions.aovList"):
        return feedback.CPW("未创建AOV")
    connections = cmds.listConnections(
        "defaultArnoldRenderOptions.aovList", source=True
    )
    if connections is None:
        return feedback.CPW("未创建AOV")
    for aov_node in connections:
        enabled = cmds.getAttr(aov_node + ".enabled")
        cmds.setAttr(aov_node + ".enabled", 0 if enabled == 1 else 1)


# 旧调用名称，便于现有 Shelf 命令平滑切换。
rendering_preset_menu = apply_rendering_preset
ai_aov_switch_button = toggle_aovs


__all__ = [
    "RenderingPresetTool",
    "ai_aov_switch_button",
    "apply_rendering_preset",
    "rendering_preset_menu",
    "toggle_aovs",
]
