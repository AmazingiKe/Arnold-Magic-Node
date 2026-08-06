import unittest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from arnold_magic_node.tools.path_detection import PathDetectionConnectionTool
from arnold_magic_node.tools.materials import MaterialConversionTool
from arnold_magic_node.tools.node_graph import QuickConnectTool
from arnold_magic_node.tools.rendering import toggle_aovs
from arnold_magic_node.tools.scene import SceneNameOptimizationTool
from arnold_magic_node.tools.selection import process_selected_nodes
from arnold_magic_node.tools.texture import (
    apply_file_udim,
    apply_texture_color_spaces,
    unify_uv_nodes_for_files,
)


class SelectionToolTests(unittest.TestCase):
    def test_groups_injected_selection_without_importing_maya(self):
        adapter = MagicMock()
        adapter.node_type.side_effect = ["file", "mesh"]
        result = process_selected_nodes(
            ["file1", "mesh1"], adapter=adapter, feedback=MagicMock()
        )
        self.assertEqual(result, {"file": ["file1"], "mesh": ["mesh1"]})


class TextureOrchestrationTests(unittest.TestCase):
    def test_matches_channels_then_sets_configured_color_spaces(self):
        adapter = MagicMock()
        adapter.file_texture_path.side_effect = [
            "D:/rock_basecolor.exr",
            "D:/rock_roughness.exr",
        ]
        matches = apply_texture_color_spaces(
            ["color", "rough"],
            {"baseColor": ["basecolor"], "specularRoughness": ["roughness"]},
            {"baseColor": "sRGB", "specularRoughness": "Raw"},
            adapter,
            MagicMock(),
        )

        self.assertEqual(
            matches,
            {"color": "baseColor", "rough": "specularRoughness"},
        )
        self.assertEqual(
            adapter.set_color_space.call_args_list,
            [
                unittest.mock.call("color", "sRGB"),
                unittest.mock.call("rough", "Raw"),
            ],
        )

    def test_sets_udim_from_each_file_path(self):
        adapter = MagicMock()
        adapter.file_texture_path.side_effect = [
            "D:/rock_1001.exr",
            "D:/rock_color.exr",
        ]
        apply_file_udim(["udim", "single"], adapter, MagicMock())
        self.assertEqual(
            adapter.set_udim.call_args_list,
            [unittest.mock.call("udim", True), unittest.mock.call("single", False)],
        )

    def test_unifies_file_nodes_on_one_place2d_texture(self):
        adapter = MagicMock()
        adapter.create_shading_node.return_value = "place2dTexture1"
        unify_uv_nodes_for_files(
            ["file1", "file2"], ["oldUv"], adapter=adapter
        )

        adapter.delete.assert_called_once_with("oldUv")
        adapter.create_shading_node.assert_called_once_with(
            "place2dTexture", at=True, name="place2dTexture"
        )
        self.assertEqual(adapter.connect_attr.call_count, 36)


class SceneNamingToolTests(unittest.TestCase):
    def test_calculates_names_in_core_and_renames_through_adapter(self):
        adapter = MagicMock()
        config = {
            "optimized_scene_node_name": {
                "replace_param": [
                    {
                        "case_sensitive": True,
                        "switch_checkbox": True,
                        "target_cont": "PREFIX_",
                        "replace_cont": "",
                    }
                ]
            }
        }
        tool = SceneNameOptimizationTool(
            adapter=adapter,
            scene_nodes={"mesh": ["|group|prefix_mesh"]},
            config=config,
        )
        tool.run()
        adapter.rename.assert_called_once_with("prefix_mesh", "mesh")


class PathDetectionToolTests(unittest.TestCase):
    def test_reads_with_adapter_and_calculates_matches_in_core(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "rock_basecolor.exr"
            candidate = root / "rock_roughness.exr"
            target.write_bytes(b"target")
            candidate.write_bytes(b"candidate")

            adapter = MagicMock()
            adapter.file_texture_path.return_value = str(target)
            adapter.image_dimensions.return_value = (2048, 2048)
            adapter.modifiers.return_value = 0
            config = {
                "path_detection_params": {
                    "exclude": [],
                    "exclude_formats": [".exr"],
                    "detection_excluded": [],
                    "similarity_range": 0.1,
                    "similarity_max": 1.0,
                    "name_weight": 0.55,
                    "resolution_weight": 0.15,
                    "format_weight": 0.05,
                    "creation_time_weight": 0.15,
                    "creation_day_range_tolerance": 30,
                    "auto_max_val": True,
                    "disable_feedback": True,
                    "set_material_name": True,
                    "set_color_space": True,
                    "set_udim": True,
                },
                "texture_filter_params": {
                    "baseColor": ["BASECOLOR"],
                    "specularRoughness": ["ROUGHNESS"],
                },
                "color_space_params": {
                    "params": {"baseColor": "sRGB", "specularRoughness": "Raw"}
                },
                "magic_conn_config": {"conn_params": {}},
                "proc_node_config": {"conn_params": {}, "params": {}},
            }
            tool = PathDetectionConnectionTool(
                config=config,
                adapter=adapter,
                feedback=MagicMock(),
                selected_nodes={"file": ["file1"]},
                language={"main": {"01": "missing"}, "feedback_prompt": {}},
            )
            result = tool.run()

        self.assertEqual(list(result), ["file1"])
        self.assertEqual(result["file1"][0][0][0], "rock_roughness.exr")


class NodeGraphToolTests(unittest.TestCase):
    def test_quick_connect_uses_injected_node_adapter(self):
        adapter = MagicMock()
        adapter.list_nodes.return_value = ["source", "target"]
        adapter.attribute_exists.return_value = True
        config = {
            "priority_order": {"outColor": "input"},
            "out_port": [],
            "input_port": [],
        }
        QuickConnectTool(adapter=adapter, config=config).run()
        adapter.connect_attr.assert_called_once_with(
            "source.outColor", "target.input"
        )


class MaterialToolTests(unittest.TestCase):
    def test_conversion_reads_and_reconnects_through_adapter(self):
        adapter = MagicMock()
        adapter.object_exists.return_value = True
        adapter.list_connections.side_effect = [
            ["material.color", "texture.outColor"],
            ["material.outColor", "shadingEngine.surfaceShader"],
        ]
        adapter.create_shading_node.return_value = "material_ACArnold"
        tool = MaterialConversionTool(
            adapter=adapter,
            feedback=MagicMock(),
            convert_info={
                "lambert": {
                    "arnold_shader": "aiStandardSurface",
                    "attribute_map": {"color": "baseColor"},
                }
            },
            materials={"lambert": ["material"]},
        )
        tool.run()

        self.assertEqual(adapter.connect_attr.call_count, 2)
        adapter.delete.assert_called_once_with("material")


class RenderingToolTests(unittest.TestCase):
    def test_toggle_aovs_uses_injected_adapter(self):
        adapter = MagicMock()
        adapter.object_exists.return_value = True
        adapter.list_connections.return_value = ["aiAOV1", "aiAOV2"]
        adapter.get_attr.side_effect = [1, 0]
        toggle_aovs(adapter=adapter, feedback=MagicMock())
        self.assertEqual(
            adapter.set_attr.call_args_list,
            [
                unittest.mock.call("aiAOV1.enabled", 0),
                unittest.mock.call("aiAOV2.enabled", 1),
            ],
        )


if __name__ == "__main__":
    unittest.main()
