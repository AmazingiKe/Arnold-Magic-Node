"""Magic Connection 的 Maya 适配和节点网络执行器。"""

from ..core.magic_connection import GRAY_CHANNELS
from .scene import MayaSceneAdapter
from .textures import MayaTextureAdapter


DEFAULT_INPUT_PORTS = ("input", "passthrough", "input1", "input2")
DEFAULT_OUTPUT_PORTS = (
    "outColor",
    "outAlpha",
    "outValue",
    "outTransparency",
    "outColorR",
    "outColorG",
    "outColorB",
    "displacement",
)


class MagicConnectionExecutionError(RuntimeError):
    """Maya 节点图无法按计划建立连接时抛出的异常。"""


class MayaMagicConnectionAdapter(MayaTextureAdapter, MayaSceneAdapter):
    """对 ``maya.cmds`` 的最小封装，便于服务层和测试替换。"""

    def __init__(self, cmds_module=None):
        super(MayaMagicConnectionAdapter, self).__init__(cmds_module)

    def selected_nodes_by_type(self):
        selected = self.cmds.ls(sl=True) or []
        result = {}
        for node_name in selected:
            node_type = self.cmds.nodeType(node_name)
            result.setdefault(node_type, []).append(node_name)
        return result

    def file_texture_path(self, node_name):
        return super(MayaMagicConnectionAdapter, self).file_texture_path(node_name)

    def is_shift_pressed(self):
        return bool(self.cmds.getModifiers() & 1)

    def create_shader(self, shader_type):
        return self.create_shading_node(shader_type, asShader=True)

    def create_node(self, node_type, name=None):
        if name:
            return self.cmds.createNode(node_type, name=name)
        return self.cmds.createNode(node_type)

    def connect(self, source_node, source_port, target_node, target_port):
        try:
            self.connect_attr(
                source_node + "." + source_port,
                target_node + "." + target_port,
                force=True,
            )
            return True
        except Exception:
            return False

    def set_udim(self, node_name, enabled):
        return super(MayaMagicConnectionAdapter, self).set_udim(node_name, enabled)

    def set_color_space(self, node_name, color_space):
        return super(MayaMagicConnectionAdapter, self).set_color_space(
            node_name, color_space
        )

    def rename_node(self, old_name, new_name):
        return self.rename(old_name, new_name)

    def report(self, message, warning=False):
        if warning:
            self.warning(message)
        else:
            self.warning(message)


class MayaMagicConnectionExecutor:
    """把 core 生成的计划转换成 Maya 节点和属性连接。"""

    def __init__(self, adapter):
        self.adapter = adapter

    def execute(self, plan):
        sources = {}
        for texture in plan.textures:
            if texture.processing is None:
                sources[texture.node_name] = (
                    texture.node_name,
                    texture.source_output_port,
                )
            else:
                final_node = self._create_processing_chain(texture)
                sources[texture.node_name] = (
                    final_node,
                    texture.processing.output_port,
                )

        normal_map_node = None
        for texture in plan.textures:
            if not texture.connect_enabled:
                continue

            channel = texture.channel
            if channel == "normalCamera":
                if plan.material_name is None:
                    continue
                normal_map_node = self.adapter.create_node(
                    "aiNormalMap", texture.node_name + "aiNormalMap"
                )
                self._connect_source(
                    sources[texture.node_name], normal_map_node, "input"
                )
                self._connect(
                    normal_map_node,
                    "outValue",
                    plan.material_name,
                    "normalCamera",
                )

            elif channel == "ao":
                if plan.material_name is None:
                    continue
                base_color = self._find_texture(plan, "baseColor")
                if base_color is None:
                    continue
                multiply_node = self.adapter.create_node(
                    "aiMultiply", texture.node_name + "_aiMultiply"
                )
                self._connect_source(
                    sources[base_color.node_name], multiply_node, "input1"
                )
                self._connect_source(
                    sources[texture.node_name], multiply_node, "input2"
                )
                self._connect(
                    multiply_node,
                    "outColor",
                    plan.material_name,
                    "baseColor",
                )

            elif channel == "bump":
                if plan.material_name is None:
                    continue
                bump_node = self.adapter.create_node(
                    "aiBump2d", texture.node_name + "_aiBump2d"
                )
                self._connect_source(
                    sources[texture.node_name], bump_node, "bumpMap"
                )
                if normal_map_node is None:
                    self._connect(
                        bump_node,
                        "outValue",
                        plan.material_name,
                        "normalCamera",
                    )
                else:
                    self._connect(bump_node, "outValue",
                                  normal_map_node, "normal")

            elif channel == "displacement":
                if plan.material_name is None and plan.shading_engine_name is None:
                    continue
                displacement_node = self.adapter.create_node(
                    "displacementShader", texture.node_name + "displacementShader"
                )
                self._connect_source(
                    sources[texture.node_name], displacement_node, "displacement"
                )
                if plan.shading_engine_name is not None:
                    self._connect(
                        displacement_node,
                        "displacement",
                        plan.shading_engine_name,
                        "displacementShader",
                    )

            elif plan.material_name is not None:
                self._connect_source(
                    sources[texture.node_name],
                    plan.material_name,
                    channel,
                )

        return sources

    def _create_processing_chain(self, texture):
        processing = texture.processing
        previous_node = texture.node_name
        previous_outputs = [texture.source_output_port]
        previous_outputs.extend(DEFAULT_OUTPUT_PORTS)

        for index, node_type in enumerate(processing.node_types):
            node_name = self.adapter.create_node(
                node_type,
                texture.node_name + "_" + node_type,
            )
            if index == 0 and texture.channel in GRAY_CHANNELS:
                input_ports = (
                    processing.input_port + "R",
                    processing.input_port + "G",
                    processing.input_port + "B",
                )
            else:
                input_ports = (processing.input_port,) + DEFAULT_INPUT_PORTS

            if not self._connect_first(
                previous_node, previous_outputs, node_name, input_ports
            ):
                raise MagicConnectionExecutionError(
                    f"无法连接 {str(previous_node)}, {str(previous_outputs)} 到处理节点 {str(node_name)}, {str(input_ports)}"
                )

            previous_node = node_name
            previous_outputs = [processing.output_port]
            previous_outputs.extend(DEFAULT_OUTPUT_PORTS)

        return previous_node

    def _connect_source(self, source, target_node, target_port):
        if not self._connect_first(
            source[0], (source[1],) +
            DEFAULT_OUTPUT_PORTS, target_node, (target_port,)
        ):
            raise MagicConnectionExecutionError(
                "无法连接 {}.{} 到 {}.{}".format(
                    source[0], source[1], target_node, target_port
                )
            )

    def _connect(self, source_node, source_port, target_node, target_port):
        if not self.adapter.connect(source_node, source_port, target_node, target_port):
            raise MagicConnectionExecutionError(
                "无法连接 {}.{} 到 {}.{}".format(
                    source_node, source_port, target_node, target_port
                )
            )

    def _connect_first(
        self, source_node, source_ports, target_node, target_ports
    ):
        for target_port in target_ports:
            for source_port in source_ports:
                if self.adapter.connect(
                    source_node, source_port, target_node, target_port
                ):
                    return True
        return False

    @staticmethod
    def _find_texture(plan, channel):
        for texture in plan.textures:
            if texture.channel == channel:
                return texture
        return None


__all__ = [
    "MagicConnectionExecutionError",
    "MayaMagicConnectionAdapter",
    "MayaMagicConnectionExecutor",
]
