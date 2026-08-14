"""渲染预设与 Arnold AOV 执行工具。"""

import os
import re

from arnold_magic_node.maya.nodes import MayaNodeAdapter
from .feedback import FeedbackPrompt
from .runtime import get_runtime_paths, load_config, load_json, load_language


ATTRIBUTE_TYPES = ("bool", "int", "float", "string")


class RenderingCaptureTool(object):
    """从 Maya 场景采集可序列化的渲染预设数据。"""

    def __init__(self, adapter=None, feedback=None):
        self.adapter = adapter or MayaNodeAdapter()
        self.feedback = feedback or FeedbackPrompt(self.adapter)

    def capture_node_groups(self, node_attributes):
        result = {}
        for node_name, attributes in node_attributes.items():
            result[node_name] = {}
            for attribute in attributes:
                try:
                    value = self.adapter.get_attr(
                        "{}.{}".format(node_name, attribute)
                    )
                except Exception:
                    value = None
                result[node_name][attribute] = value
        return result

    def driver_and_filter_nodes(self, aov_node):
        if not self.adapter.object_exists(aov_node):
            self.feedback.print_message("节点 {} 不存在".format(aov_node))
            return None, None
        driver_name = None
        filter_name = None
        for connection in self.adapter.list_connections(
            aov_node + ".outputs", source=True, destination=False
        ):
            node_type = self.adapter.node_type(connection)
            if node_type == "aiAOVDriver":
                driver_name = connection
            elif node_type == "aiAOVFilter":
                filter_name = connection
        return driver_name, filter_name

    def capture_aovs(
        self,
        aov_attributes,
        driver_attributes,
        filter_attributes,
    ):
        if not self.adapter.object_exists("defaultArnoldRenderOptions"):
            self.feedback.warn("没检测到阿诺德渲染器节点，无法写入阿诺德内容")
            return None
        aov_nodes = self.adapter.list_connections(
            "defaultArnoldRenderOptions.aovList", source=True
        )
        if not aov_nodes:
            self.feedback.print_message("还没有设置AOV，将不会写入AOV")
            return None

        result = {}
        for aov_node in aov_nodes:
            driver_name, filter_name = self.driver_and_filter_nodes(aov_node)
            aov_values = self.capture_node_groups(
                {aov_node: aov_attributes}
            )[aov_node]
            driver_values = self.capture_node_groups(
                {driver_name: driver_attributes}
            )[driver_name]
            filter_values = self.capture_node_groups(
                {filter_name: filter_attributes}
            )[filter_name]
            result[aov_node] = [
                {"aov_name": aov_node},
                {"aov_attributes": aov_values},
                {
                    "driver": {
                        "driver_name": driver_name,
                        "driver_attribute": driver_values,
                    }
                },
                {
                    "filter": {
                        "filter_name": filter_name,
                        "filter_attribute": filter_values,
                    }
                },
            ]
        return result


class RenderingPresetTool(object):
    """读取一个保存的渲染预设并写入当前 Maya 场景。"""

    def __init__(self, preset_name, adapter=None, feedback=None):
        self.adapter = adapter or MayaNodeAdapter()
        self.feedback = feedback or FeedbackPrompt(self.adapter)
        self.paths = get_runtime_paths()
        self.preset_name = preset_name
        self.render_settings = load_json(
            os.path.normpath(
                os.path.join(self.paths.render_preset_path, preset_name + ".json")
            )
        )
        self.config = load_config(self.paths)["render_preset_params"]
        self.language = load_language(self.paths)["ArnoldMagicNode"]["rendering_preset_menu"]

    def run(self):
        """依照配置选择性写入默认渲染、Arnold 和 AOV 参数。"""

        if self.config["default_rendering_properties_write_options"]:
            try:
                self.set_default_rendering_properties()
                self.feedback.print_message(
                    "<{}> {}".format(
                        self.preset_name, self.language["__init__"]["01"]
                    )
                )
            except Exception as error:
                self.feedback.print_message(
                    "<{}> {} {}".format(
                        self.preset_name, self.language["__init__"]["02"], error
                    )
                )

        if not self.adapter.object_exists("defaultArnoldRenderOptions"):
            self.feedback.warn(self.language["__init__"]["03"])
            return

        if self.config.get("rendering_properties_write_options"):
            try:
                self.set_rendering_properties()
                self.feedback.print_message(
                    "<{}> {}".format(
                        self.preset_name, self.language["__init__"]["04"]
                    )
                )
            except Exception as error:
                self.feedback.print_message(
                    "<{}> {} {}".format(
                        self.preset_name, self.language["__init__"]["05"], error
                    )
                )

        if self.config.get("AOV_properties_properties_write_options"):
            try:
                self.delete_original_aovs()
            except Exception as error:
                self.feedback.print_message(
                    "<{}> {} {}".format(
                        self.preset_name, self.language["__init__"]["06"], error
                    )
                )

            try:
                aov_properties = self.render_settings.get("AOV_properties")
                if aov_properties:
                    self.set_aovs()
                    self.feedback.print_message(
                        "<{}> {}".format(
                            self.preset_name, self.language["__init__"]["07"]
                        )
                    )
                else:
                    self.feedback.print_message(
                        "<{}> {}".format(
                            self.preset_name, self.language["__init__"]["08"]
                        )
                    )
            except Exception as error:
                self.feedback.print_message(
                    "<{}> {} {}".format(
                        self.preset_name, self.language["__init__"]["09"], error
                    )
                )

    def _set_attributes(self, node_name, attributes):
        for attribute_name, value in attributes.items():
            try:
                self.adapter.set_attr(
                    "{}.{}".format(node_name, attribute_name), value
                )
                continue
            except Exception:
                pass
            for attribute_type in ATTRIBUTE_TYPES:
                try:
                    self.adapter.set_attr(
                        "{}.{}".format(node_name, attribute_name),
                        value,
                        value_type=attribute_type,
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
                cryptomatte_node_name = self.adapter.create_shading_node(
                    "cryptomatte", app=True
                )
                break

        aov_index = 0
        for aov_key, values in aov_data.items():
            aov_node = self.adapter.create_shading_node(
                "aiAOV", app=True, name=values[0]["aov_name"]
            )
            self._set_attributes(aov_node, values[1]["aov_attributes"])

            driver_data = values[2]["driver"]
            driver_node = self.adapter.create_shading_node(
                "aiAOVDriver", app=True, name=driver_data["driver_name"]
            )
            self._set_attributes(driver_node, driver_data["driver_attribute"])
            self.adapter.connect_attr(
                driver_node + ".message", aov_node + ".outputs[0].driver"
            )

            filter_data = values[3]["filter"]
            filter_node = self.adapter.create_shading_node(
                "aiAOVFilter", app=True, name=filter_data["filter_name"]
            )
            self._set_attributes(filter_node, filter_data["filter_attribute"])
            self.adapter.connect_attr(
                filter_node + ".message", aov_node + ".outputs[0].filter"
            )
            self.adapter.connect_attr(
                aov_node + ".message",
                "defaultArnoldRenderOptions.aovList[{}]".format(aov_index),
                force=True,
            )

            if re.search("CRYPTO", aov_key.upper(), re.IGNORECASE):
                self.adapter.connect_attr(
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
        aov_nodes = self.adapter.list_connections(
            "defaultArnoldRenderOptions.aovList", source=True
        )
        if not aov_nodes:
            return

        nodes_to_delete = list(aov_nodes)
        for aov_node in aov_nodes:
            nodes_to_delete.extend(
                self.adapter.list_connections(
                    "{}.outputs[0].filter".format(aov_node), source=True
                )
                or []
            )
            nodes_to_delete.extend(
                self.adapter.list_connections(
                    "{}.outputs[0].driver".format(aov_node), source=True
                )
                or []
            )

        for node_name in nodes_to_delete:
            try:
                if node_name not in nodes_to_keep:
                    self.adapter.delete(node_name)
            except Exception:
                pass


def toggle_aovs(adapter=None, feedback=None):
    """切换当前 Arnold AOV 的 enabled 状态。"""

    adapter = adapter or MayaNodeAdapter()
    feedback = feedback or FeedbackPrompt(adapter)
    if not adapter.object_exists("defaultArnoldRenderOptions.aovList"):
        return feedback.warn("未创建AOV")
    connections = adapter.list_connections(
        "defaultArnoldRenderOptions.aovList", source=True
    )
    if not connections:
        return feedback.warn("未创建AOV")
    for aov_node in connections:
        enabled = adapter.get_attr(aov_node + ".enabled")
        adapter.set_attr(aov_node + ".enabled", 0 if enabled == 1 else 1)


__all__ = [
    "RenderingCaptureTool",
    "RenderingPresetTool",
    "toggle_aovs",
]
