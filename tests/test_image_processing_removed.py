import ast
import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from arnold_magic_node.core.similarity import resolution_similarity
from arnold_magic_node.maya.textures import MayaTextureAdapter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "arnold_magic_node"


def parse_module(relative_path):
    source = (PACKAGE_ROOT / relative_path).read_text(encoding="utf-8-sig")
    return source, ast.parse(source)


class ImageDependencyRemovalTests(unittest.TestCase):
    def test_image_processing_packages_are_not_installed(self):
        self.assertFalse((PROJECT_ROOT / "dependencies.py").exists())

    def test_core_has_no_external_image_processing_imports(self):
        imports = set()
        for path in (PACKAGE_ROOT / "core").glob("*.py"):
            _, tree = parse_module(str(path.relative_to(PACKAGE_ROOT)))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module)
        self.assertTrue(
            imports.isdisjoint({"numpy", "PIL", "pyexr", "OpenEXR", "Imath"})
        )


class TextureManagerRemovalTests(unittest.TestCase):
    REMOVED_SYMBOLS = {
        "TextureManagerWin", "TM_FindAndReplace", "TM_RepathFiles", "TM_TexturePack",
        "TextureManagerWinInstance", "NonEditableColumnsModel", "CenterDelegate",
        "LeftAlignDelegate", "TM_ImageProcessing", "ImageProcessing",
        "image_processing_Win", "switch_source_tex_files", "_parse_udim_filename",
        "delete_processed_files", "texture_list_find_processed_textures",
        "add_suffix_to_filename", "modify_node_path", "refresh_table",
    }

    def test_texture_manager_classes_and_entry_points_are_removed(self):
        package_symbols = set()
        package_source = []
        for python_file in PACKAGE_ROOT.rglob("*.py"):
            source = python_file.read_text(encoding="utf-8-sig")
            package_source.append(source)
            tree = ast.parse(source)
            package_symbols.update(
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.ClassDef, ast.FunctionDef))
            )
        self.assertTrue(package_symbols.isdisjoint(self.REMOVED_SYMBOLS))
        source = "\n".join(package_source)
        self.assertNotIn("_TMProc", source)
        self.assertNotIn("texture_manager", source)
        self.assertNotIn("TXManagerShelf_200.png", source)

    def test_texture_manager_language_resources_are_removed(self):
        for relative_path in (
            "arnold_magic_node/resources/i18n/zh_CN.json",
            "arnold_magic_node/resources/i18n/en_US.json",
        ):
            language = json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))
            feature_language = language["ArnoldMagicNode"]
            self.assertTrue(
                feature_language.keys().isdisjoint(
                    {"TM_WIN", "TM_FAR_WIN", "TM_RF_WIN", "TM_TP_WIN", "TM_IP_WIN"}
                )
            )
            self.assertNotIn("ttglq_menu", feature_language["AMDUI_WIN"]["create_widgets"])

    def test_texture_manager_icon_is_removed(self):
        self.assertFalse((PROJECT_ROOT / "icons/TXManagerShelf_200.png").exists())

    def test_missing_image_dimensions_do_not_count_as_a_match(self):
        self.assertEqual(resolution_similarity([0, 0], [0, 0]), 0.0)
        self.assertEqual(resolution_similarity([1024, 1024], [0, 0]), 0.0)

    def test_image_dimensions_use_maya_and_fall_back_to_zero(self):
        calls = []

        class FakeImage(object):
            kUnknown = object()

            def readFromFile(self, path, pixel_type):
                calls.append((path, pixel_type))

            def getSize(self):
                return 2048, 1024

        maya_api = SimpleNamespace(MImage=FakeImage)
        adapter = MayaTextureAdapter(SimpleNamespace(), maya_api)
        self.assertEqual(adapter.image_dimensions("textures/../source.exr"), (2048, 1024))
        self.assertEqual(len(calls), 1)

        class UnreadableImage(FakeImage):
            def readFromFile(self, path, pixel_type):
                raise RuntimeError("unsupported image")

        maya_api.MImage = UnreadableImage
        self.assertEqual(adapter.image_dimensions("missing.exr"), (0, 0))


if __name__ == "__main__":
    unittest.main()
