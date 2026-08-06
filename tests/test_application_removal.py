"""拆除 legacy application 模块后的依赖边界测试。"""

import ast
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "arnold_magic_node"


def imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    return [
        (node.level, node.module)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    ]


class ApplicationRemovalTests(unittest.TestCase):
    def test_legacy_application_module_is_deleted(self):
        self.assertFalse((PACKAGE_ROOT / "application.py").exists())

    def test_ui_uses_tools_instead_of_application_or_legacy_core(self):
        for path in (PACKAGE_ROOT / "ui").glob("*.py"):
            modules = imported_modules(path)
            imported_names = {module for _, module in modules}
            self.assertNotIn("application", imported_names, path.name)
            self.assertNotIn("arnold_magic_core", imported_names, path.name)

            if path.name not in {
                "__init__.py",
                "qt.py",
                "workspace.py",
                "texture_batch_importer.py",
            }:
                self.assertTrue(
                    any(module and module.startswith("tools") for _, module in modules),
                    path.name,
                )

    def test_bootstrap_no_longer_delegates_to_application(self):
        tree = ast.parse(
            (PACKAGE_ROOT / "bootstrap.py").read_text(encoding="utf-8-sig")
        )
        imported_names = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        self.assertNotIn("application", imported_names)

    def test_feature_tools_are_present(self):
        expected = {
            "runtime.py",
            "texture.py",
            "rendering.py",
            "path_detection.py",
            "materials.py",
            "node_graph.py",
            "scene.py",
        }
        actual = {path.name for path in (PACKAGE_ROOT / "tools").glob("*.py")}
        self.assertTrue(expected.issubset(actual))

    def test_runtime_tool_resolves_paths_without_importing_maya(self):
        from arnold_magic_node.tools.runtime import get_runtime_paths

        paths = get_runtime_paths(Path("C:/tmp/maya/arnold_magic_node"))
        self.assertTrue(paths.settings_path.endswith("arnold_magic_node\\settings"))
        self.assertTrue(
            paths.render_preset_path.endswith("arnold_magic_node\\presets\\render")
        )

    def test_runtime_data_manager_delegates_to_core_storage(self):
        from arnold_magic_node.tools.runtime import DataManager

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            data_manager = DataManager()
            data_manager.save_json(path, {"enabled": True})
            self.assertEqual(data_manager.load_json(path), {"enabled": True})


if __name__ == "__main__":
    unittest.main()
