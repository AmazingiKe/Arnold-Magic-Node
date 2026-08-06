import ast
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "arnold_magic_node"
UI_ROOT = PACKAGE_ROOT / "ui"


def module_tree(path):
    return ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))


def imported_modules(path):
    return {
        node.module
        for node in ast.walk(module_tree(path))
        if isinstance(node, ast.ImportFrom) and node.module
    }


class UiStructureTests(unittest.TestCase):
    def test_ui_modules_use_tools_not_application_or_legacy_core(self):
        excluded = {"__init__.py", "qt.py", "workspace.py", "texture_batch_importer.py"}
        for path in UI_ROOT.glob("*.py"):
            imports = imported_modules(path)
            self.assertNotIn("application", imports, path.name)
            self.assertNotIn("arnold_magic_core", imports, path.name)
            if path.name not in excluded:
                self.assertTrue(
                    any(module.startswith("tools") for module in imports), path.name
                )

    def test_main_window_actions_are_backed_by_tools(self):
        imports = imported_modules(UI_ROOT / "main_window.py")
        expected = {
            "tools.magic_connection", "tools.materials", "tools.node_graph",
            "tools.path_detection", "tools.rendering", "tools.runtime",
            "tools.scene", "tools.texture",
        }
        self.assertTrue(expected.issubset(imports))

    def test_ui_package_stays_lazy(self):
        tree = module_tree(UI_ROOT / "__init__.py")
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertEqual(imports, [])

    def test_qt_compatibility_imports_are_centralized(self):
        qt_source = (UI_ROOT / "qt.py").read_text(encoding="utf-8-sig")
        self.assertIn("PySide", qt_source)
        for path in UI_ROOT.glob("*.py"):
            if path.name == "qt.py":
                continue
            source = path.read_text(encoding="utf-8-sig")
            self.assertNotIn("from PySide", source, path.name)
            self.assertNotIn("from shiboken", source, path.name)

    def test_bootstrap_builds_main_window_without_reload_bridge(self):
        bootstrap_path = PACKAGE_ROOT / "bootstrap.py"
        source = bootstrap_path.read_text(encoding="utf-8-sig")
        self.assertIn("from .ui.main_window import MainWindow", source)
        self.assertIn("return MainWindow()", source)
        self.assertNotIn("importlib.reload", source)
        self.assertNotIn("import application", source)


if __name__ == "__main__":
    unittest.main()
