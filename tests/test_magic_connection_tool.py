import unittest
import json
import tempfile

from arnold_magic_node.tools.magic_connection import MagicConnectionTool
from arnold_magic_node.maya.magic_connection import MayaMagicConnectionAdapter


class FakeMayaAdapter:
    def __init__(self, selection, paths):
        self.selection = selection
        self.paths = paths
        self.connections = []
        self.created_nodes = []
        self.renames = []
        self.udim_nodes = []
        self.color_spaces = []

    def selected_nodes_by_type(self):
        return self.selection

    def file_texture_path(self, node_name):
        return self.paths[node_name]

    def is_shift_pressed(self):
        return True

    def create_shader(self, shader_type):
        self.created_nodes.append((shader_type, "shader"))
        return "createdShader"

    def create_node(self, node_type, name=None):
        node_name = name or node_type
        self.created_nodes.append((node_type, node_name))
        return node_name

    def connect(self, source_node, source_port, target_node, target_port):
        self.connections.append(
            (source_node, source_port, target_node, target_port)
        )
        return True

    def set_udim(self, node_name, enabled):
        self.udim_nodes.append((node_name, enabled))

    def set_color_space(self, node_name, color_space):
        self.color_spaces.append((node_name, color_space))

    def rename_node(self, old_name, new_name):
        self.renames.append((old_name, new_name))
        return new_name


class FakeCmds:
    def __init__(self):
        self.connections = []
        self.attributes = []
        self.warnings = []

    def ls(self, sl=False):
        return ["file1", "shader1"] if sl else []

    def nodeType(self, node_name):
        return "file" if node_name == "file1" else "aiStandardSurface"

    def getAttr(self, attribute):
        if attribute == "file1.fileTextureName":
            return "hero_ALBEDO.exr"
        return None

    def getModifiers(self):
        return 1

    def shadingNode(self, node_type, asShader=False):
        return node_type + "1"

    def createNode(self, node_type, name=None):
        return name or node_type + "1"

    def connectAttr(self, source, target, force=False):
        if source.startswith("bad."):
            raise RuntimeError("connection rejected")
        self.connections.append((source, target, force))

    def setAttr(self, attribute, value, **kwargs):
        self.attributes.append((attribute, value, kwargs))

    def rename(self, old_name, new_name):
        return new_name

    def warning(self, message):
        self.warnings.append(message)


def make_config():
    return {
        "texture_filter_params": {
            "baseColor": ["ALBEDO"],
            "specularRoughness": ["ROUGHNESS"],
        },
        "magic_conn_config": {
            "conn_params": {
                "baseColor": True,
                "specularRoughness": True,
            },
            "set_color_space": True,
            "set_material_name": False,
            "set_udim": True,
        },
        "proc_node_config": {
            "conn_params": {
                "baseColor": False,
                "specularRoughness": True,
            },
            "params": {
                "specularRoughness": {
                    "NodeList": ["aiRange"],
                    "InputPort": "input",
                    "OutputPort": "outColorR",
                }
            },
        },
        "color_space_params": {
            "params": {"baseColor": "sRGB", "specularRoughness": "Raw"}
        },
    }


class MagicConnectionToolTests(unittest.TestCase):
    def test_empty_selection_returns_empty_result(self):
        adapter = FakeMayaAdapter({}, {})

        result = MagicConnectionTool(make_config(), adapter=adapter).run()

        self.assertEqual(result.matched_channels, {})

    def test_runs_core_plan_and_executes_maya_operations(self):
        adapter = FakeMayaAdapter(
            {
                "file": ["albedo_file", "roughness_file"],
                "aiStandardSurface": ["shader1"],
            },
            {
                "albedo_file": "hero_ALBEDO.exr",
                "roughness_file": "hero_ROUGHNESS.1001.exr",
            },
        )

        result = MagicConnectionTool(make_config(), adapter=adapter).run()

        self.assertEqual(result.material_name, "shader1")
        self.assertEqual(
            result.matched_channels,
            {
                "albedo_file": "baseColor",
                "roughness_file": "specularRoughness",
            },
        )
        self.assertIn(
            ("roughness_file_aiRange", "outColorR", "shader1", "specularRoughness"),
            adapter.connections,
        )
        self.assertIn(("roughness_file", True), adapter.udim_nodes)
        self.assertIn(("albedo_file", "sRGB"), adapter.color_spaces)

    def test_shift_creates_material_when_no_material_is_selected(self):
        adapter = FakeMayaAdapter(
            {"file": ["albedo_file"]},
            {"albedo_file": "hero_ALBEDO.exr"},
        )

        result = MagicConnectionTool(make_config(), adapter=adapter).run()

        self.assertTrue(result.created_material)
        self.assertIn(("aiStandardSurface", "shader"), adapter.created_nodes)
        self.assertIn(
            ("albedo_file", "outColor", "createdShader", "baseColor"),
            adapter.connections,
        )

    def test_missing_file_selection_does_not_touch_maya_graph(self):
        adapter = FakeMayaAdapter({"aiStandardSurface": ["shader1"]}, {})

        result = MagicConnectionTool(make_config(), adapter=adapter).run()

        self.assertEqual(result.matched_channels, {})
        self.assertEqual(adapter.connections, [])
        self.assertEqual(adapter.created_nodes, [])

    def test_special_channels_create_their_expected_intermediate_nodes(self):
        config = make_config()
        config["texture_filter_params"].update(
            {
                "normalCamera": ["NORMAL"],
                "ao": ["AO"],
                "bump": ["BUMP"],
                "displacement": ["HEIGHT"],
            }
        )
        config["magic_conn_config"]["conn_params"].update(
            {"normalCamera": True, "ao": True, "bump": True, "displacement": True}
        )
        config["proc_node_config"]["conn_params"].update(
            {"normalCamera": False, "ao": False, "bump": False, "displacement": False}
        )
        adapter = FakeMayaAdapter(
            {
                "file": ["albedo", "normal", "ao", "bump", "height"],
                "aiStandardSurface": ["shader1"],
                "shadingEngine": ["shader1SG"],
            },
            {
                "albedo": "hero_ALBEDO.exr",
                "normal": "hero_NORMAL.exr",
                "ao": "hero_AO.exr",
                "bump": "hero_BUMP.exr",
                "height": "hero_HEIGHT.exr",
            },
        )

        MagicConnectionTool(config, adapter=adapter).run()

        created_types = [node_type for node_type, _ in adapter.created_nodes]
        self.assertIn(("aiNormalMap"), created_types)
        self.assertIn(("aiMultiply"), created_types)
        self.assertIn(("aiBump2d"), created_types)
        self.assertIn(("displacementShader"), created_types)
        self.assertIn(
            ("heightdisplacementShader", "displacement", "shader1SG", "displacementShader"),
            adapter.connections,
        )

    def test_material_name_setting_and_feedback_are_forwarded(self):
        config = make_config()
        config["magic_conn_config"]["set_material_name"] = True

        class Feedback:
            def __init__(self):
                self.messages = []

            def CP(self, message):
                self.messages.append(message)

            def CPW(self, message):
                self.messages.append(message)

        feedback = Feedback()
        adapter = FakeMayaAdapter(
            {"file": ["albedo_file"], "aiStandardSurface": ["shader1"]},
            {"albedo_file": "hero_ALBEDO.exr"},
        )

        result = MagicConnectionTool(
            config, adapter=adapter, feedback=feedback
        ).run()

        self.assertEqual(result.renamed_material_name, "hero")
        self.assertEqual(adapter.renames, [("shader1", "hero")])
        self.assertEqual(len(feedback.messages), 2)

    def test_tool_can_load_a_config_from_an_explicit_path(self):
        config = make_config()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
            json.dump(config, handle)
            config_path = handle.name

        try:
            loaded = MagicConnectionTool._load_config(config_path)
        finally:
            import os

            os.unlink(config_path)

        self.assertEqual(loaded["texture_filter_params"], config["texture_filter_params"])


class MayaMagicConnectionAdapterTests(unittest.TestCase):
    def test_adapter_wraps_selection_attributes_connections_and_reporting(self):
        cmds = FakeCmds()
        adapter = MayaMagicConnectionAdapter(cmds_module=cmds)

        self.assertEqual(
            adapter.selected_nodes_by_type(),
            {"file": ["file1"], "aiStandardSurface": ["shader1"]},
        )
        self.assertEqual(adapter.file_texture_path("file1"), "hero_ALBEDO.exr")
        self.assertTrue(adapter.is_shift_pressed())
        self.assertEqual(adapter.create_shader("aiStandardSurface"), "aiStandardSurface1")
        self.assertEqual(adapter.create_node("aiRange", "range1"), "range1")
        self.assertTrue(adapter.connect("file1", "outColor", "shader1", "baseColor"))
        self.assertFalse(adapter.connect("bad", "outColor", "shader1", "baseColor"))
        adapter.set_udim("file1", True)
        adapter.set_udim("file1", False)
        adapter.set_color_space("file1", "Raw")
        self.assertEqual(adapter.rename_node("shader1", "renamed"), "renamed")
        adapter.report("info")
        adapter.report("warning", warning=True)

        self.assertEqual(len(cmds.connections), 1)
        self.assertEqual(len(cmds.attributes), 5)
        self.assertEqual(cmds.warnings, ["info", "warning"])


if __name__ == "__main__":
    unittest.main()
