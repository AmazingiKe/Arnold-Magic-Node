"""Magic Connection 用户功能工具。"""

import os
from dataclasses import dataclass
from typing import Dict, Optional

from arnold_magic_node.core.magic_connection import (
    build_magic_connection_plan,
    clean_material_name,
    contains_udim_number,
)
from arnold_magic_node.maya.magic_connection import (
    MayaMagicConnectionAdapter,
    MayaMagicConnectionExecutor,
)
from .feedback import FeedbackPrompt


MATERIAL_TYPES = ("aiStandardSurface", "standardSurface", "aiOpenPBRSurface")


@dataclass(frozen=True)
class MagicConnectionResult:
    """一次运行的可观察结果。"""

    matched_channels: Dict[str, str]
    material_name: Optional[str]
    renamed_material_name: Optional[str]
    created_material: bool


def connect_texture_nodes(
    node_list,
    material_name,
    config,
    adapter,
    shading_engine_name=None,
):
    """为显式 file 节点构建 core 计划并通过 Maya 适配器执行。"""

    texture_files = {
        node_name: adapter.file_texture_path(node_name)
        for node_name in node_list
    }
    plan = build_magic_connection_plan(
        texture_files=texture_files,
        filter_data=config["texture_filter_params"],
        processing_data=config["proc_node_config"]["params"],
        magic_connection_options=config["magic_conn_config"]["conn_params"],
        processing_options=config["proc_node_config"]["conn_params"],
        material_name=material_name,
        shading_engine_name=shading_engine_name,
    )
    MayaMagicConnectionExecutor(adapter).execute(plan)
    return {texture.node_name: texture.channel for texture in plan.textures}


class MagicConnectionTool:
    """组合 core、配置和 Maya 适配器，执行一次 Magic Connection。"""

    def __init__(self, config=None, adapter=None, feedback=None, config_path=None):
        self.config = config or self._load_config(config_path)
        if adapter is None:
            adapter = MayaMagicConnectionAdapter()
        self.adapter = adapter
        self.feedback = feedback or FeedbackPrompt(adapter)

    def run(self, shift_pressed=None):
        selection = self.adapter.selected_nodes_by_type() or {}
        if not selection:
            return self._result({}, None, None, False)

        file_nodes = selection.get("file") or []
        if not file_nodes:
            self._report("没有选择纹理节点，请选择纹理节点", warning=True)
            return self._result({}, None, None, False)

        material_name = self._find_material(selection)
        created_material = False
        if material_name is None:
            if shift_pressed is None:
                shift_pressed = self.adapter.is_shift_pressed()
            if shift_pressed:
                material_name = self.adapter.create_shader("aiStandardSurface")
                created_material = True

        shading_engine_names = selection.get("shadingEngine") or []
        shading_engine_name = shading_engine_names[0] if shading_engine_names else None
        texture_files = {
            node_name: self.adapter.file_texture_path(node_name)
            for node_name in file_nodes
        }

        config = self.config
        plan = build_magic_connection_plan(
            texture_files=texture_files,
            filter_data=config["texture_filter_params"],
            processing_data=config["proc_node_config"]["params"],
            magic_connection_options=config["magic_conn_config"]["conn_params"],
            processing_options=config["proc_node_config"]["conn_params"],
            material_name=material_name,
            shading_engine_name=shading_engine_name,
        )

        MayaMagicConnectionExecutor(self.adapter).execute(plan)
        self._apply_post_processing(plan, texture_files)

        renamed_material_name = None
        if material_name is not None:
            renamed_material_name = material_name
            if config["magic_conn_config"].get("set_material_name", False):
                first_file = os.path.basename(texture_files[file_nodes[0]])
                new_name = clean_material_name(
                    first_file, config["texture_filter_params"]
                )
                if new_name:
                    renamed_material_name = self.adapter.rename(
                        material_name, new_name
                    )
                    self._report(
                        "已将 {} 材质名称修改成 {}".format(
                            material_name, renamed_material_name
                        )
                    )

            self._report("已完成 {} 材质连接".format(renamed_material_name))

        return self._result(
            {texture.node_name: texture.channel for texture in plan.textures},
            material_name,
            renamed_material_name,
            created_material,
        )

    def _apply_post_processing(self, plan, texture_files):
        magic_config = self.config["magic_conn_config"]
        color_spaces = self.config.get(
            "color_space_params", {}).get("params", {})

        for texture in plan.textures:
            node_name = texture.node_name
            file_path = texture_files[node_name]
            if magic_config.get("set_udim", False):
                self.adapter.set_udim(
                    node_name, contains_udim_number(file_path))

            if magic_config.get("set_color_space", False):
                color_space = color_spaces.get(texture.channel)
                if color_space:
                    self.adapter.set_color_space(node_name, color_space)

    def _find_material(self, selection):
        for material_type in MATERIAL_TYPES:
            material_names = selection.get(material_type) or []
            if material_names:
                return material_names[0]
        return None

    def _report(self, message, warning=False):
        if warning:
            self.feedback.warn(message)
        else:
            self.feedback.print_message(message)

    @staticmethod
    def _result(matched_channels, material_name, renamed_material_name, created):
        return MagicConnectionResult(
            matched_channels=matched_channels,
            material_name=material_name,
            renamed_material_name=renamed_material_name,
            created_material=created,
        )

    @staticmethod
    def _load_config(config_path=None):
        from arnold_magic_node.core.paths import user_settings_dir
        from arnold_magic_node.core.storage import load_json
        from arnold_magic_node.maya.environment import get_user_data_root

        if config_path is None:
            config_path = os.path.join(
                str(user_settings_dir(get_user_data_root())),
                "Arnold_Magic_Settings.json",
            )
        return load_json(config_path)


def run_magic_connection(config=None, adapter=None, feedback=None, config_path=None):
    """执行一次 Magic Connection，供 Qt 和调试脚本直接调用。"""

    return MagicConnectionTool(
        config=config,
        adapter=adapter,
        feedback=feedback,
        config_path=config_path,
    ).run()


__all__ = [
    "MagicConnectionResult",
    "MagicConnectionTool",
    "connect_texture_nodes",
    "run_magic_connection",
]
