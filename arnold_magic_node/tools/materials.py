"""旧材质转换与智能贴图修复工具。"""

import json
import os

from arnold_magic_node.core.path_detection import collect_file_info, process_file_names, scan_directory
from arnold_magic_node.core.similarity import calculate_similarity, select_matches
from arnold_magic_node.core.paths import PROJECT_ROOT
from arnold_magic_node.maya.magic_connection import MayaMagicConnectionAdapter
from arnold_magic_node._qt_compat import QCoreApplication
from .feedback import FeedbackPrompt
from .magic_connection import connect_texture_nodes
from .runtime import load_config
from .selection import get_scene_nodes_by_type, process_selected_nodes
from .texture import (
    apply_file_udim,
    apply_texture_color_spaces,
    unify_uv_nodes_for_files,
)


class MaterialConversionTool(object):
    """将受支持的旧材质转换为 Arnold 材质并复用已有连接。"""

    def __init__(
        self,
        select_all=False,
        adapter=None,
        feedback=None,
        convert_info=None,
        materials=None,
    ):
        self.adapter = adapter or MayaMagicConnectionAdapter()
        if convert_info is None:
            config_path = os.path.join(
                str(PROJECT_ROOT), "config", "shader_convert_map.json"
            )
            with open(config_path, "r") as config_file:
                convert_info = json.load(config_file)
        self.convert_info = convert_info
        self.feedback = feedback or FeedbackPrompt(self.adapter)
        self.materials = (
            self.get_materials_node(select_all) if materials is None else materials
        )

    def get_materials_node(self, select_all=False):
        wanted_types = list(self.convert_info.keys())
        scene_nodes = (
            get_scene_nodes_by_type(adapter=self.adapter, feedback=self.feedback)
            if select_all
            else process_selected_nodes(adapter=self.adapter, feedback=self.feedback)
        )
        if not scene_nodes:
            return {}

        result = {}
        for material_type in wanted_types:
            material_nodes = scene_nodes.get(material_type, {})
            if isinstance(material_nodes, dict):
                names = list(material_nodes.keys())
            elif isinstance(material_nodes, list):
                if material_nodes and isinstance(material_nodes[0], dict):
                    names = [item["name"] for item in material_nodes if "name" in item]
                else:
                    names = material_nodes[:]
            else:
                continue
            names = [name for name in names if name != "lambert1"]
            if names:
                result[material_type] = names
        return result

    def get_materials_input_data(self, material_name):
        pairs = self.adapter.list_connections(
            material_name, s=True, d=False, c=True, p=True
        )
        return {
            pairs[index]: pairs[index + 1]
            for index in range(0, len(pairs), 2)
        }

    def get_materials_output_data(self, material_name):
        pairs = self.adapter.list_connections(
            material_name, s=False, d=True, c=True, p=True
        )
        return {
            pairs[index]: pairs[index + 1]
            for index in range(0, len(pairs), 2)
        }

    def run(self):
        for material_type, material_names in self.materials.items():
            for material_name in material_names:
                if not self.adapter.object_exists(material_name):
                    continue
                input_data = self.get_materials_input_data(material_name)
                output_data = self.get_materials_output_data(material_name)
                new_material = self.adapter.create_shading_node(
                    self.convert_info[material_type]["arnold_shader"],
                    asShader=True,
                    name=material_name + "_ACArnold",
                )
                for destination, source in input_data.items():
                    source_node, source_port = source.split(".", 1)
                    material_input_port = destination.split(".", 1)[1]
                    self.adapter.connect_attr(
                        "{}.{}".format(source_node, source_port),
                        "{}.{}".format(
                            new_material,
                            self.convert_info[material_type]["attribute_map"][
                                material_input_port
                            ],
                        ),
                        force=True,
                    )
                for source, destination in output_data.items():
                    output_port = source.split(".", 1)[1]
                    try:
                        self.adapter.connect_attr(
                            "{}.{}".format(new_material, output_port),
                            destination,
                            force=True,
                        )
                    except Exception as error:
                        self.feedback.print_message(
                            QCoreApplication.translate(
                                "MaterialConversionTool", "Connection failed: {0}"
                            ).format(error)
                        )
                self.adapter.delete(material_name)


class IntelligentMaterialRepairTool(object):
    """根据已有贴图路径寻找同目录贴图并补全材质连接。"""

    MATERIAL_TYPES = (
        "aiStandardSurface",
        "standardSurface",
        "aiLambert",
        "aiStandardHair",
    )

    def __init__(self, select_all=False, adapter=None, feedback=None):
        self.adapter = adapter or MayaMagicConnectionAdapter()
        self.feedback = feedback or FeedbackPrompt(self.adapter)
        self.materials = self.get_materials_node(select_all)

    def get_materials_node(self, select_all=False):
        scene_nodes = (
            get_scene_nodes_by_type(adapter=self.adapter, feedback=self.feedback)
            if select_all
            else process_selected_nodes(adapter=self.adapter, feedback=self.feedback)
        )
        if not scene_nodes:
            return {node_type: [] for node_type in self.MATERIAL_TYPES}
        return {
            node_type: scene_nodes.get(node_type, [])
            for node_type in self.MATERIAL_TYPES
        }

    def detect_and_calculate_similarity(self, node_path):
        config = load_config()
        path_config = config["path_detection_params"]
        texture_filter_data = config["texture_filter_params"]
        directory = os.path.dirname(node_path)
        filename = os.path.basename(node_path)
        directory_paths = scan_directory(
            directory,
            path_config["exclude"],
            path_config["exclude_formats"],
        )
        directory_info = collect_file_info(
            directory_paths, self.adapter.image_dimensions
        )
        target_info = collect_file_info(
            {filename: node_path}, self.adapter.image_dimensions
        )
        processed_directory_info = process_file_names(
            directory_info,
            path_config["detection_excluded"],
            texture_filter_data,
        )
        processed_target_info = process_file_names(
            target_info,
            path_config["detection_excluded"],
            texture_filter_data,
        )
        del processed_directory_info[filename]
        similarity = calculate_similarity(
            processed_target_info,
            processed_directory_info,
            path_config,
            path_config["creation_day_range_tolerance"],
        )
        return select_matches(
            similarity,
            path_config["auto_max_val"],
            path_config["similarity_max"],
            path_config["similarity_range"],
        )

    def create_nodes_from_list(self, first_node_name, directory, matching_completed):
        filenames = []
        for values in matching_completed.values():
            filenames = [name for name, _ in values]
        created_nodes = [
            self.adapter.create_file_texture(filename, directory)
            for filename in filenames
        ]
        created_nodes.append(first_node_name)
        unify_uv_nodes_for_files(created_nodes, adapter=self.adapter)
        return created_nodes

    def run(self):
        settings = load_config()
        for material_names in self.materials.values():
            for material_name in material_names:
                material_textures = self.adapter.file_texture_paths(material_name)
                if not material_textures:
                    continue
                node_name, node_path = next(iter(material_textures.items()))
                matches = self.detect_and_calculate_similarity(node_path)
                if not matches or len(matches) > 9:
                    self.feedback.warn(
                        "[{}] 的贴图 [{}] 匹配结果异常，数量：{}，已跳过修复".format(
                            material_name, node_name, len(matches)
                        )
                    )
                    continue
                created_nodes = self.create_nodes_from_list(
                    node_name,
                    os.path.normpath(os.path.dirname(node_path)),
                    {node_name: matches},
                )
                if settings["path_detection_params"]["set_color_space"]:
                    apply_texture_color_spaces(
                        created_nodes,
                        settings["texture_filter_params"],
                        settings["color_space_params"]["params"],
                        self.adapter,
                        self.feedback,
                    )
                if settings["path_detection_params"]["set_udim"]:
                    apply_file_udim(created_nodes, self.adapter, self.feedback)
                connect_texture_nodes(
                    created_nodes,
                    material_name,
                    settings,
                    self.adapter,
                )


__all__ = [
    "IntelligentMaterialRepairTool",
    "MaterialConversionTool",
]
