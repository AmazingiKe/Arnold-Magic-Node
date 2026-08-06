import unittest
from pathlib import Path
from unittest.mock import MagicMock

from arnold_magic_node.maya.aovs import MayaAovAdapter
from arnold_magic_node.maya.environment import MayaEnvironmentAdapter
from arnold_magic_node.maya.nodes import MayaNodeAdapter
from arnold_magic_node.maya.scene import MayaSceneAdapter
from arnold_magic_node.maya.textures import MayaTextureAdapter


class MayaNodeAdapterTests(unittest.TestCase):
    def setUp(self):
        self.cmds = MagicMock()
        self.adapter = MayaNodeAdapter(self.cmds)

    def test_normalizes_list_queries_and_delegates_node_queries(self):
        self.cmds.ls.return_value = None
        self.cmds.listConnections.return_value = None
        self.cmds.listRelatives.return_value = None
        self.cmds.nodeType.return_value = "file"
        self.cmds.attributeQuery.return_value = True
        self.cmds.objExists.return_value = True

        self.assertEqual(self.adapter.list_nodes(selection=True), [])
        self.assertEqual(self.adapter.list_connections("node"), [])
        self.assertEqual(self.adapter.list_relatives("node", parent=True), [])
        self.assertEqual(self.adapter.node_type("node"), "file")
        self.assertTrue(self.adapter.attribute_exists("node", "outColor"))
        self.assertTrue(self.adapter.object_exists("node.outColor"))

    def test_reads_writes_creates_connects_and_renames_nodes(self):
        self.cmds.getAttr.return_value = "value"
        self.cmds.createNode.return_value = "created"
        self.cmds.shadingNode.return_value = "shader"
        self.cmds.rename.return_value = "renamed"
        self.cmds.getModifiers.return_value = 9

        self.assertEqual(self.adapter.get_attr("node.attr"), "value")
        self.adapter.set_attr("node.attr", "text", value_type="string")
        self.assertEqual(self.adapter.create_node("aiRange", name="range1"), "created")
        self.assertEqual(
            self.adapter.create_shading_node("file", asTexture=True), "shader"
        )
        self.adapter.connect_attr("a.out", "b.input", force=True)
        self.adapter.delete("old")
        self.assertEqual(self.adapter.rename("old", "new"), "renamed")
        self.adapter.warning("warning")
        self.assertEqual(self.adapter.modifiers(), 9)

        self.cmds.setAttr.assert_called_once_with(
            "node.attr", "text", type="string"
        )
        self.cmds.connectAttr.assert_called_once_with(
            "a.out", "b.input", force=True
        )


class MayaTextureAdapterTests(unittest.TestCase):
    def test_reads_dimensions_with_injected_open_maya(self):
        image = MagicMock()
        image.getSize.return_value = (4096, 2048)
        image_class = MagicMock(return_value=image)
        open_maya = MagicMock(MImage=image_class)
        adapter = MayaTextureAdapter(MagicMock(), open_maya)

        self.assertEqual(adapter.image_dimensions("texture.exr"), (4096, 2048))
        image.readFromFile.assert_called_once()

    def test_dimension_failure_returns_zero_size(self):
        open_maya = MagicMock()
        open_maya.MImage.side_effect = RuntimeError("bad image")
        adapter = MayaTextureAdapter(MagicMock(), open_maya)
        self.assertEqual(adapter.image_dimensions("bad.exr"), (0, 0))

    def test_handles_file_paths_udim_color_space_and_texture_creation(self):
        cmds = MagicMock()
        cmds.getAttr.return_value = "D:/textures/rock.exr"
        cmds.shadingNode.return_value = "rock"
        adapter = MayaTextureAdapter(cmds, MagicMock())

        self.assertEqual(
            adapter.file_texture_path("file1"), "D:/textures/rock.exr"
        )
        adapter.set_udim("file1", True)
        adapter.set_color_space("file1", "Raw")
        result = adapter.create_file_texture("rock.exr", "D:/textures")

        self.assertEqual(result, "rock")
        cmds.shadingNode.assert_called_once_with(
            "file", asTexture=True, name="rock"
        )
        self.assertGreaterEqual(cmds.setAttr.call_count, 5)


class MayaSceneAdapterTests(unittest.TestCase):
    def test_groups_selected_and_scene_nodes_by_type(self):
        cmds = MagicMock()
        cmds.ls.side_effect = [["file1", "mesh1"], ["mesh1"]]
        cmds.nodeType.side_effect = ["file", "mesh", "mesh"]
        adapter = MayaSceneAdapter(cmds)

        self.assertEqual(
            adapter.selected_nodes_by_type(),
            {"file": ["file1"], "mesh": ["mesh1"]},
        )
        self.assertEqual(adapter.scene_nodes_by_type(), {"mesh": ["mesh1"]})

    def test_queries_lights_groups_and_upstream_file_textures(self):
        cmds = MagicMock()
        cmds.ls.side_effect = [["lightShape"], []]
        cmds.listRelatives.return_value = ["light"]
        cmds.getAttr.side_effect = ["key", "D:/key.exr"]
        cmds.listConnections.side_effect = [["file1"], []]
        cmds.nodeType.return_value = "file"
        cmds.objExists.return_value = True
        adapter = MayaSceneAdapter(cmds)

        lights = adapter.arnold_lights_and_types(["aiAreaLight", "spotLight"])
        self.assertEqual(lights, {"light": "aiAreaLight"})
        self.assertEqual(adapter.group_lights(lights), {"key": ["light"]})
        self.assertEqual(
            adapter.file_texture_paths("material"),
            {"file1": "D:/key.exr"},
        )


class MayaEnvironmentAdapterTests(unittest.TestCase):
    def test_exposes_user_root_language_and_modifiers(self):
        cmds = MagicMock()
        cmds.internalVar.return_value = "D:/maya/"
        cmds.about.return_value = "zh_CN"
        cmds.getModifiers.return_value = 9
        adapter = MayaEnvironmentAdapter(cmds)

        self.assertEqual(
            adapter.user_data_root(),
            Path("D:/maya/") / "arnold_magic_node",
        )
        self.assertEqual(adapter.ui_language(), "zh_CN")
        self.assertEqual(adapter.modifiers(), 9)


class MayaAovAdapterTests(unittest.TestCase):
    def test_creates_aov_through_injected_factory(self):
        interface = MagicMock()
        factory = MagicMock(return_value=interface)
        adapter = MayaAovAdapter(MagicMock(), factory)

        self.assertIs(adapter.create_aov("RGBA_key"), interface.addAOV.return_value)
        interface.addAOV.assert_called_once_with("RGBA_key")


if __name__ == "__main__":
    unittest.main()
