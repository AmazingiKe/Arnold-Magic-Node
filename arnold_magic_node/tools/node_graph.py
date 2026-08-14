"""快速连接与 Arnold 节点混合工具。"""

from arnold_magic_node.maya.nodes import MayaNodeAdapter
from .feedback import FeedbackPrompt
from .runtime import MAYA_ALT_MODIFIER, load_config
from .selection import process_selected_nodes


class QuickConnectTool(object):
    """按选择顺序尝试连接相邻的两个节点。"""

    def __init__(self, adapter=None, config=None):
        self.adapter = adapter or MayaNodeAdapter()
        self.config = config or load_config()["node_connection_mixer_config"][
            "quick_connect_node_parms"
        ]

    def get_selected_nodes(self):
        return self.adapter.list_nodes(selection=True)

    def run(self):
        nodes = self.get_selected_nodes()
        if len(nodes) < 2:
            self.adapter.warning("至少需要两个节点来建立连接！")
            return

        for source_node, destination_node in zip(nodes, nodes[1:]):
            connected = False
            for output_attribute, input_attribute in self.config[
                "priority_order"
            ].items():
                if not (
                    self.adapter.attribute_exists(source_node, output_attribute)
                    and self.adapter.attribute_exists(destination_node, input_attribute)
                ):
                    continue
                try:
                    self.adapter.connect_attr(
                        "{}.{}".format(source_node, output_attribute),
                        "{}.{}".format(destination_node, input_attribute),
                    )
                    connected = True
                    break
                except Exception:
                    continue
            if connected:
                continue

            for output_attribute in self.config["out_port"]:
                if connected:
                    break
                for input_attribute in self.config["input_port"]:
                    if not (
                        self.adapter.attribute_exists(source_node, output_attribute)
                        and self.adapter.attribute_exists(destination_node, input_attribute)
                    ):
                        continue
                    try:
                        self.adapter.connect_attr(
                            "{}.{}".format(source_node, output_attribute),
                            "{}.{}".format(destination_node, input_attribute),
                        )
                        connected = True
                        break
                    except Exception:
                        continue
            if not connected:
                self.adapter.warning(
                    "{} → {} 未找到可连接属性，已跳过。".format(
                        source_node, destination_node
                    )
                )


class NodeMixTool(object):
    """按节点类别创建对应的 Arnold Layer 节点并连接选择对象。"""

    UTILITY_SHADER_TYPES = (
        "file", "aiBlackbody", "aiBump2d", "aiBump3d", "aiCameraProjection",
        "aiClamp", "aiColorConvert", "aiColorCorrect", "aiColorJitter",
        "aiComplexIor", "aiComposite", "aiDistance", "aiFacingRatio",
        "aiMotionVector", "aiNormalMap", "aiOslShader", "aiRampFloat",
        "aiRampRgb", "aiRange", "aiRoundCorners", "aiShuffle",
        "aiSpaceTransform", "aiStateFloat", "aiStateInt", "aiStateVector",
        "aiTraceSet", "aiUvProjection", "aiUvTransform", "aiVectorMap",
    )
    MATH_TYPES = (
        "aiAbs", "aiAdd", "aiAtan", "aiCompare", "aiComplement", "aiCross",
        "aiDivide", "aiDot", "aiExp", "aiFraction", "aiIsFinite", "aiLength",
        "aiLog", "aiMatrixInterpolate", "aiMatrixMultiplyVector",
        "aiMatrixTransform", "aiMax", "aiMin", "aiModulo", "aiMultiply",
        "aiNegate", "aiNormalize", "aiPow", "aiRandom", "aiReciprocal",
        "aiSign", "aiSqrt", "aiSubtract", "aiTrigo",
    )
    SHADER_TYPES = (
        "aiStandardSurface", "standardSurface", "aiLambert", "aiStandardHair", "aiToon"
    )
    MIX_TYPES = ("aiLayerFloat", "aiLayerRgba", "aiLayerShader")
    COLOR_OUTPUT_PORTS = ("outColor", "outValue")
    GRAY_OUTPUT_PORTS = (
        "outColorR", "outColorG", "outColorB", "outAlpha", "outValueX",
        "outValueY", "outValueZ",
    )

    def __init__(self, adapter=None):
        self.adapter = adapter or MayaNodeAdapter()
        self.feedback = FeedbackPrompt(self.adapter)
        self.type_to_category = {}
        for category, node_types in {
            "utility": self.UTILITY_SHADER_TYPES,
            "math": self.MATH_TYPES,
            "shader": self.SHADER_TYPES,
            "mix": self.MIX_TYPES,
        }.items():
            for node_type in node_types:
                self.type_to_category[node_type] = category

    def intelligent_mix_process(self, selected_nodes):
        for node_type, node_names in selected_nodes.items():
            category = self.type_to_category.get(node_type)
            if category in ("utility", "math"):
                self.handle_utility_shader(node_names)
            elif category == "shader":
                self.handle_shader(node_names)
            elif category == "mix":
                self.handle_mix(node_type, node_names)
            else:
                self.feedback.warn("未知的节点类型：{}".format(node_type))

    def handle_utility_shader(self, nodes):
        modifiers = self.adapter.modifiers()
        if modifiers == MAYA_ALT_MODIFIER:
            self.handle_grayscale_shader_mix(nodes)
        else:
            self.handle_color_shader_mix(nodes)

    def handle_color_shader_mix(self, nodes):
        mix_node = self.adapter.create_node("aiLayerRgba", name="shader_mix")
        for index, node_name in enumerate(nodes, start=1):
            for output_port in self.COLOR_OUTPUT_PORTS:
                try:
                    self.adapter.connect_attr(
                        "{}.{}".format(node_name, output_port),
                        "{}.input{}".format(mix_node, index),
                        force=True,
                    )
                    break
                except Exception:
                    pass

    def handle_grayscale_shader_mix(self, nodes):
        mix_node = self.adapter.create_node("aiLayerFloat", name="grays_shader_mix")
        for index, node_name in enumerate(nodes, start=1):
            for output_port in self.GRAY_OUTPUT_PORTS:
                try:
                    self.adapter.connect_attr(
                        "{}.{}".format(node_name, output_port),
                        "{}.input{}".format(mix_node, index),
                        force=True,
                    )
                    break
                except Exception:
                    pass

    def handle_shader(self, nodes):
        mix_node = self.adapter.create_node("aiLayerShader", name="shader_mix")
        for index, node_name in enumerate(nodes, start=1):
            self.adapter.connect_attr(
                node_name + ".outColor",
                "{}.input{}".format(mix_node, index),
                force=True,
            )

    def _create_node(self, node_type, name):
        return self.adapter.create_node(node_type, name=name)

    def handle_mix(self, node_type, nodes):
        mapping = {
            "aiLayerFloat": ("aiLayerFloat", "LayerFloat", "outValue"),
            "aiLayerRgba": ("aiLayerRgba", "LayerRgba", "outColor"),
            "aiLayerShader": ("aiLayerShader", "LayerShader", "outColor"),
        }
        mix_type, name, output_port = mapping[node_type]
        mix_node = self._create_node(mix_type, name)
        for index, node_name in enumerate(nodes, start=1):
            self.adapter.connect_attr(
                "{}.{}".format(node_name, output_port),
                "{}.input{}".format(mix_node, index),
                force=True,
            )

    def run(self):
        selected_nodes = process_selected_nodes(
            adapter=self.adapter, feedback=self.feedback
        )
        if not selected_nodes:
            return self.feedback.warn("至少需要两个节点来建立连接！")
        nodes = []
        for node_names in selected_nodes.values():
            if isinstance(node_names, (list, tuple, set)):
                nodes.extend(node_names)
            else:
                nodes.append(node_names)
        if len(nodes) < 2:
            return self.feedback.warn("至少需要两个节点来建立连接！")
        return self.intelligent_mix_process(selected_nodes)


__all__ = [
    "NodeMixTool",
    "QuickConnectTool",
]
