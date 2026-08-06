"""基于目录相似度的贴图发现与节点连接工具。"""

import maya.cmds as cmds

from ..arnold_magic_core import NodeProcessor, PathDetection
from .feedback import FeedbackPrompt
from .runtime import (
    MAYA_ALT_MODIFIER,
    MAYA_SHIFT_MODIFIER,
    is_modifier_pressed,
    load_config,
    load_language,
)
from .selection import process_selected_nodes


class PathDetectionConnectionTool(object):
    """发现相邻贴图，并按 Alt/Shift 组合创建及连接节点。"""

    def __init__(self):
        self.feedback = FeedbackPrompt()
        self.path_detection = PathDetection()
        self.node_processor = NodeProcessor()
        self.config = load_config()
        self.path_detection_data = self.config["path_detection_params"]
        self.texture_filter_data = self.config["texture_filter_params"]
        self.selected_nodes = process_selected_nodes()
        self.language = load_language()["ArnoldMagicNode"]["PDC"]

    def run(self):
        if self.selected_nodes is None:
            return
        if "file" not in self.selected_nodes:
            return self.feedback.CPW(self.language["main"]["01"])

        modifiers = cmds.getModifiers()
        matches = self.detect_and_calculate_similarity()
        if not (
            is_modifier_pressed(MAYA_ALT_MODIFIER, modifiers)
            or is_modifier_pressed(MAYA_SHIFT_MODIFIER, modifiers)
        ):
            return matches

        created_node_lists = self.create_nodes_from_list(matches)
        if self.path_detection_data["set_color_space"]:
            for node_list in created_node_lists:
                self.node_processor.AutoSetTexColorSpace(
                    auto_set_color_space_config=self.config["color_space_params"][
                        "params"
                    ],
                    node_list=node_list,
                    filter_data=self.texture_filter_data,
                )
        self.auto_set_file_udim(created_node_lists)

        if is_modifier_pressed(MAYA_SHIFT_MODIFIER, modifiers):
            for node_list in created_node_lists:
                if self.path_detection_data["set_material_name"]:
                    material_name = self.node_processor.clean_material_name(
                        node_list[0], self.texture_filter_data
                    )
                    material_name = cmds.shadingNode(
                        "aiStandardSurface", asShader=True, name=material_name
                    )
                else:
                    material_name = cmds.shadingNode("aiStandardSurface", asShader=True)

                matched_channels = self.node_processor.AutoNodeConnect(
                    node_list,
                    material_name,
                    self.texture_filter_data,
                    self.config["proc_node_config"]["params"],
                    self.config["magic_conn_config"]["conn_params"],
                    self.config["proc_node_config"]["conn_params"],
                )
                if self.path_detection_data["set_color_space"]:
                    self.node_processor.AutoSetTexColorSpace(
                        auto_set_color_space_config=self.config["color_space_params"][
                            "params"
                        ],
                        matching_channel=matched_channels,
                    )
                self.node_processor.auto_set_udim(list(matched_channels.keys()))
        return matches

    main = run

    def detect_and_calculate_similarity(self):
        completed = {}
        for node_name in self.selected_nodes["file"]:
            target_object, directory = self.path_detection.get_node_path(node_name)
            directory_files = self.path_detection.detection_path_content(
                target_dirname=directory,
                exclude_list=self.path_detection_data["exclude"],
                exclude_formats=self.path_detection_data["exclude_formats"],
            )
            directory_info = self.path_detection.get_file_info(directory_files)
            target_info = self.path_detection.get_file_info(target_object)
            processed_directory_info = self.path_detection.process_dict_key_name(
                directory_info,
                self.path_detection_data["detection_excluded"],
                self.texture_filter_data,
            )
            processed_target_info = self.path_detection.process_dict_key_name(
                target_info,
                self.path_detection_data["detection_excluded"],
                self.texture_filter_data,
            )
            original_name = list(target_object.keys())[0]
            del processed_directory_info[original_name]
            similarity = self.path_detection.calculate_similarity(
                processed_target_info,
                processed_directory_info,
                self.path_detection_data,
                self.path_detection_data["creation_day_range_tolerance"],
            )
            matching_list = self.path_detection.determine_connection(
                similarity,
                self.path_detection_data["auto_max_val"],
                self.path_detection_data["similarity_max"],
                self.path_detection_data["similarity_range"],
            )
            if not self.path_detection_data["disable_feedback"]:
                self.feedback_prompt(similarity, matching_list, original_name)
            completed[node_name] = [matching_list, directory]
        return completed

    def feedback_prompt(self, similarity_dict, matching_list, original_name):
        language = self.language["feedback_prompt"]
        self.feedback.CP(language["01"])
        for texture_name, similarity in similarity_dict.items():
            self.feedback.CP(
                "{} {},{}{},{}{}".format(
                    language["02"],
                    original_name,
                    language["03"],
                    texture_name,
                    language["04"],
                    "{:.5f}".format(similarity),
                )
            )
        self.feedback.CP(language["05"])
        self.feedback.CP("{}{}".format(language["06"], original_name))
        for target, similarity in matching_list:
            self.feedback.CP(
                "{} {},{}{}".format(
                    language["07"], target, language["08"], "{:.5f}".format(similarity)
                )
            )

    def remove_original_uv(self, node_name):
        connections = cmds.listConnections(node_name, source=True, destination=False)
        if not connections:
            return
        original_uv_name = connections[-1]
        if original_uv_name and original_uv_name != "defaultColorMgtGlobals":
            cmds.delete(original_uv_name)

    def create_nodes_from_list(self, matching_completed):
        created_lists = []
        for node_name, values in matching_completed.items():
            texture_names = [texture_name for texture_name, _ in values[0]]
            created = self.path_detection.create_node(texture_names, values[1])
            created.append(node_name)
            created_lists.append(created)
            self.remove_original_uv(node_name)

        for node_list in created_lists:
            self.node_processor.unify_uv_node(node_list)
        return created_lists

    def auto_set_file_udim(self, node_lists):
        if not self.path_detection_data["set_udim"]:
            return
        for node_list in node_lists:
            self.node_processor.auto_set_udim(node_list)


def run_path_detection_connection():
    """运行路径检测连接功能。"""

    return PathDetectionConnectionTool().run()


# 兼容旧类与按钮入口。
Path_Detection_Connection = PathDetectionConnectionTool
path_detection_connection_button = run_path_detection_connection


__all__ = [
    "PathDetectionConnectionTool",
    "Path_Detection_Connection",
    "path_detection_connection_button",
    "run_path_detection_connection",
]
