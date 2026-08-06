"""基于目录相似度的贴图发现与节点连接工具。"""

import os

from ..core.magic_connection import clean_material_name
from ..core.path_detection import collect_file_info, process_file_names, scan_directory
from ..core.similarity import calculate_similarity, select_matches
from ..maya.magic_connection import MayaMagicConnectionAdapter
from .feedback import FeedbackPrompt
from .magic_connection import connect_texture_nodes
from .runtime import (
    MAYA_ALT_MODIFIER,
    MAYA_SHIFT_MODIFIER,
    is_modifier_pressed,
    load_config,
    load_language,
)
from .selection import process_selected_nodes
from .texture import (
    apply_file_udim,
    apply_texture_color_spaces,
    unify_uv_nodes_for_files,
)


class PathDetectionConnectionTool(object):
    """发现相邻贴图，并按 Alt/Shift 组合创建及连接节点。"""

    def __init__(
        self,
        config=None,
        adapter=None,
        feedback=None,
        selected_nodes=None,
        language=None,
    ):
        self.adapter = adapter or MayaMagicConnectionAdapter()
        self.feedback = feedback or FeedbackPrompt(self.adapter)
        self.config = config or load_config()
        self.path_detection_data = self.config["path_detection_params"]
        self.texture_filter_data = self.config["texture_filter_params"]
        self.selected_nodes = (
            process_selected_nodes(adapter=self.adapter, feedback=self.feedback)
            if selected_nodes is None else selected_nodes
        )
        self.language = language or load_language()["ArnoldMagicNode"]["PDC"]

    def run(self):
        if self.selected_nodes is None:
            return
        if "file" not in self.selected_nodes:
            return self.feedback.CPW(self.language["main"]["01"])

        modifiers = self.adapter.modifiers()
        matches = self.detect_and_calculate_similarity()
        if not (
            is_modifier_pressed(MAYA_ALT_MODIFIER, modifiers)
            or is_modifier_pressed(MAYA_SHIFT_MODIFIER, modifiers)
        ):
            return matches

        created_node_lists = self.create_nodes_from_list(matches)
        if self.path_detection_data["set_color_space"]:
            for node_list in created_node_lists:
                apply_texture_color_spaces(
                    node_list,
                    self.texture_filter_data,
                    self.config["color_space_params"]["params"],
                    self.adapter,
                    self.feedback,
                )
        self.auto_set_file_udim(created_node_lists)

        if is_modifier_pressed(MAYA_SHIFT_MODIFIER, modifiers):
            for node_list in created_node_lists:
                if self.path_detection_data["set_material_name"]:
                    material_name = clean_material_name(
                        node_list[0], self.texture_filter_data
                    )
                    material_name = self.adapter.create_shading_node(
                        "aiStandardSurface", asShader=True, name=material_name
                    )
                else:
                    material_name = self.adapter.create_shading_node(
                        "aiStandardSurface", asShader=True
                    )

                matched_channels = connect_texture_nodes(
                    node_list,
                    material_name,
                    self.config,
                    self.adapter,
                )
                if self.path_detection_data["set_color_space"]:
                    apply_texture_color_spaces(
                        node_list,
                        self.texture_filter_data,
                        self.config["color_space_params"]["params"],
                        self.adapter,
                        self.feedback,
                        matching_channels=matched_channels,
                    )
                apply_file_udim(
                    list(matched_channels.keys()), self.adapter, self.feedback
                )
        return matches

    main = run

    def detect_and_calculate_similarity(self):
        completed = {}
        for node_name in self.selected_nodes["file"]:
            node_path = self.adapter.file_texture_path(node_name)
            original_name = os.path.basename(node_path)
            directory = os.path.dirname(node_path)
            target_object = {original_name: os.path.normpath(node_path)}
            try:
                directory_files = scan_directory(
                    directory,
                    self.path_detection_data["exclude"],
                    self.path_detection_data["exclude_formats"],
                )
            except OSError as error:
                self.feedback.CP("无法读取目录 {}: {}".format(directory, error))
                directory_files = {}
            directory_info = collect_file_info(
                directory_files, self.adapter.image_dimensions
            )
            target_info = collect_file_info(
                target_object, self.adapter.image_dimensions
            )
            processed_directory_info = process_file_names(
                directory_info,
                self.path_detection_data["detection_excluded"],
                self.texture_filter_data,
            )
            processed_target_info = process_file_names(
                target_info,
                self.path_detection_data["detection_excluded"],
                self.texture_filter_data,
            )
            del processed_directory_info[original_name]
            similarity = calculate_similarity(
                processed_target_info,
                processed_directory_info,
                self.path_detection_data,
                self.path_detection_data["creation_day_range_tolerance"],
            )
            matching_list = select_matches(
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
        connections = self.adapter.list_connections(
            node_name, source=True, destination=False
        )
        if not connections:
            return
        original_uv_name = connections[-1]
        if original_uv_name and original_uv_name != "defaultColorMgtGlobals":
            self.adapter.delete(original_uv_name)

    def create_nodes_from_list(self, matching_completed):
        created_lists = []
        for node_name, values in matching_completed.items():
            texture_names = [texture_name for texture_name, _ in values[0]]
            created = [
                self.adapter.create_file_texture(texture_name, values[1])
                for texture_name in texture_names
            ]
            created.append(node_name)
            created_lists.append(created)
            self.remove_original_uv(node_name)

        for node_list in created_lists:
            unify_uv_nodes_for_files(node_list, adapter=self.adapter)
        return created_lists

    def auto_set_file_udim(self, node_lists):
        if not self.path_detection_data["set_udim"]:
            return
        for node_list in node_lists:
            apply_file_udim(node_list, self.adapter, self.feedback)


def run_path_detection_connection(**kwargs):
    """运行路径检测连接功能。"""

    return PathDetectionConnectionTool(**kwargs).run()


# 兼容旧类与按钮入口。
Path_Detection_Connection = PathDetectionConnectionTool
path_detection_connection_button = run_path_detection_connection


__all__ = [
    "PathDetectionConnectionTool",
    "Path_Detection_Connection",
    "path_detection_connection_button",
    "run_path_detection_connection",
]
