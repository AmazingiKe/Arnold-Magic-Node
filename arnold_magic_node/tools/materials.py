"""旧材质转换与智能贴图修复工具。"""

import json
import os

import maya.cmds as cmds

from ..arnold_magic_core import GetNodeData, NodeProcessor, PathDetection
from ..core.paths import PROJECT_ROOT
from .feedback import FeedbackPrompt
from .runtime import load_config
from .selection import get_scene_nodes_by_type, process_selected_nodes


class MaterialConversionTool(object):
    """将受支持的旧材质转换为 Arnold 材质并复用已有连接。"""

    def __init__(self, select_all=False):
        config_path = os.path.join(str(PROJECT_ROOT), "config", "shader_convert_map.json")
        with open(config_path, "r") as config_file:
            self.convert_info = json.load(config_file)
        self.feedback = FeedbackPrompt()
        self.materials = self.get_materials_node(select_all)

    def get_materials_node(self, select_all=False):
        wanted_types = list(self.convert_info.keys())
        scene_nodes = (
            get_scene_nodes_by_type() if select_all else process_selected_nodes()
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

    @staticmethod
    def get_materials_input_data(material_name):
        pairs = cmds.listConnections(
            material_name, s=True, d=False, c=True, p=True
        ) or []
        return {
            pairs[index]: pairs[index + 1]
            for index in range(0, len(pairs), 2)
        }

    @staticmethod
    def get_materials_output_data(material_name):
        pairs = cmds.listConnections(
            material_name, s=False, d=True, c=True, p=True
        ) or []
        return {
            pairs[index]: pairs[index + 1]
            for index in range(0, len(pairs), 2)
        }

    def run(self):
        for material_type, material_names in self.materials.items():
            for material_name in material_names:
                if not cmds.objExists(material_name):
                    continue
                input_data = self.get_materials_input_data(material_name)
                output_data = self.get_materials_output_data(material_name)
                new_material = cmds.shadingNode(
                    self.convert_info[material_type]["arnold_shader"],
                    asShader=True,
                    name=material_name + "_ACArnold",
                )
                for destination, source in input_data.items():
                    source_node, source_port = source.split(".", 1)
                    material_input_port = destination.split(".", 1)[1]
                    cmds.connectAttr(
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
                        cmds.connectAttr(
                            "{}.{}".format(new_material, output_port),
                            destination,
                            force=True,
                        )
                    except Exception as error:
                        self.feedback.CP("连接失败: {}".format(error))
                cmds.delete(material_name)

    process = run


class IntelligentMaterialRepairTool(object):
    """根据已有贴图路径寻找同目录贴图并补全材质连接。"""

    MATERIAL_TYPES = (
        "aiStandardSurface",
        "standardSurface",
        "aiLambert",
        "aiStandardHair",
    )

    def __init__(self, select_all=False):
        self.feedback = FeedbackPrompt()
        self.path_detection = PathDetection()
        self.node_processor = NodeProcessor()
        self.node_data = GetNodeData()
        self.materials = self.get_materials_node(select_all)

    def get_materials_node(self, select_all=False):
        scene_nodes = (
            get_scene_nodes_by_type() if select_all else process_selected_nodes()
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
        directory_paths = self.path_detection.detection_path_content(
            target_dirname=directory,
            exclude_list=path_config["exclude"],
            exclude_formats=path_config["exclude_formats"],
        )
        directory_info = self.path_detection.get_file_info(directory_paths)
        target_info = self.path_detection.get_file_info({filename: node_path})
        processed_directory_info = self.path_detection.process_dict_key_name(
            directory_info,
            path_config["detection_excluded"],
            texture_filter_data,
        )
        processed_target_info = self.path_detection.process_dict_key_name(
            target_info,
            path_config["detection_excluded"],
            texture_filter_data,
        )
        del processed_directory_info[filename]
        similarity = self.path_detection.calculate_similarity(
            processed_target_info,
            processed_directory_info,
            path_config,
            path_config["creation_day_range_tolerance"],
        )
        return self.path_detection.determine_connection(
            similarity,
            path_config["auto_max_val"],
            path_config["similarity_max"],
            path_config["similarity_range"],
        )

    def create_nodes_from_list(self, first_node_name, directory, matching_completed):
        filenames = []
        for values in matching_completed.values():
            filenames = [name for name, _ in values]
        created_nodes = self.path_detection.create_node(filenames, directory)
        created_nodes.append(first_node_name)
        self.node_processor.unify_uv_node(created_nodes)
        return created_nodes

    def run(self):
        settings = load_config()
        for material_names in self.materials.values():
            for material_name in material_names:
                material_textures = self.node_data.get_file_texture_paths(material_name)
                if not material_textures:
                    continue
                node_name, node_path = next(iter(material_textures.items()))
                matches = self.detect_and_calculate_similarity(node_path)
                if not matches or len(matches) > 9:
                    self.feedback.CPW(
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
                    self.node_processor.AutoSetTexColorSpace(
                        auto_set_color_space_config=settings["color_space_params"][
                            "params"
                        ],
                        node_list=created_nodes,
                        filter_data=settings["texture_filter_params"],
                    )
                if settings["path_detection_params"]["set_udim"]:
                    self.node_processor.auto_set_udim(created_nodes)
                self.node_processor.AutoNodeConnect(
                    created_nodes,
                    material_name,
                    settings["texture_filter_params"],
                    settings["proc_node_config"]["params"],
                    settings["magic_conn_config"]["conn_params"],
                    settings["proc_node_config"]["conn_params"],
                )

    process = run


def convert_all_old_materials_to_arnold():
    tool = MaterialConversionTool(select_all=True)
    return tool.run()


def convert_selected_old_materials_to_arnold():
    tool = MaterialConversionTool(select_all=False)
    return tool.run()


def repair_all_materials():
    tool = IntelligentMaterialRepairTool(select_all=True)
    return tool.run()


def repair_selected_materials():
    tool = IntelligentMaterialRepairTool(select_all=False)
    return tool.run()


# 兼容旧入口。
ConvertOldMaterialsToArnold = MaterialConversionTool
IntelligentMaterialRepair = IntelligentMaterialRepairTool
all_convert_old_materials_to_arnold_button = convert_all_old_materials_to_arnold
select_convert_old_materials_to_arnold_button = convert_selected_old_materials_to_arnold
all_intelligent_material_repair_button = repair_all_materials
select_intelligent_material_repair_button = repair_selected_materials


__all__ = [
    "ConvertOldMaterialsToArnold",
    "IntelligentMaterialRepair",
    "IntelligentMaterialRepairTool",
    "MaterialConversionTool",
    "all_convert_old_materials_to_arnold_button",
    "convert_all_old_materials_to_arnold",
    "convert_selected_old_materials_to_arnold",
    "repair_all_materials",
    "repair_selected_materials",
    "select_convert_old_materials_to_arnold_button",
]
