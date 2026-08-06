import ast
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "arnold_magic_node"
ICONS_ROOT = PROJECT_ROOT / "icons"


class PackageStructureTests(unittest.TestCase):
    def test_application_monolith_is_removed(self):
        self.assertFalse((PACKAGE_ROOT / "application.py").exists())

    def test_feature_tools_are_split_by_user_function(self):
        expected_modules = {
            "magic_connection.py",
            "materials.py",
            "node_graph.py",
            "path_detection.py",
            "rendering.py",
            "scene.py",
            "texture.py",
        }
        actual_modules = {path.name for path in (PACKAGE_ROOT / "tools").glob("*.py")}
        self.assertTrue(expected_modules.issubset(actual_modules))

    def test_tools_do_not_depend_on_ui(self):
        for path in (PACKAGE_ROOT / "tools").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
            imports = {
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            }
            self.assertFalse(
                any(module == "ui" or module.startswith("ui.") for module in imports),
                path.name,
            )

    def test_icons_remain_module_level_public_static_resources(self):
        self.assertTrue(ICONS_ROOT.is_dir())
        self.assertTrue((ICONS_ROOT / "Logo_B.svg").is_file())

    def test_installer_uses_the_root_package_entry(self):
        installer_source = (PROJECT_ROOT / "installer.py").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("arnold_magic_node.show", installer_source)


if __name__ == "__main__":
    unittest.main()
