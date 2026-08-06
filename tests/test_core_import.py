import ast
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "arnold_magic_node"


def import_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    return {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }


def direct_host_imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imports.add(node.module)
    return imports


class CoreImportTests(unittest.TestCase):
    def test_runtime_tool_uses_the_core_path_and_storage_layers(self):
        imports = import_modules(PACKAGE_ROOT / "tools" / "runtime.py")
        self.assertIn("core.paths", imports)
        self.assertIn("core.storage", imports)

    def test_settings_tool_uses_core_settings_instead_of_root_module(self):
        imports = import_modules(PACKAGE_ROOT / "tools" / "settings.py")
        self.assertIn("core.settings", imports)
        self.assertNotIn("default_config", imports)

    def test_tools_do_not_depend_on_the_deleted_monolith(self):
        for path in (PACKAGE_ROOT / "tools").glob("*.py"):
            self.assertNotIn("application", import_modules(path), path.name)

    def test_tools_use_package_adapters_instead_of_host_modules(self):
        for path in (PACKAGE_ROOT / "tools").glob("*.py"):
            imports = direct_host_imports(path)
            forbidden = {
                name
                for name in imports
                if name == "maya"
                or name.startswith("maya.")
                or name == "mtoa"
                or name.startswith("mtoa.")
            }
            self.assertEqual(forbidden, set(), path.name)

            relative_imports = import_modules(path)
            self.assertNotIn("arnold_magic_core", relative_imports, path.name)

    def test_generic_core_file_is_replaced_by_unique_module_name(self):
        self.assertTrue((PACKAGE_ROOT / "arnold_magic_core.py").is_file())
        self.assertFalse((PROJECT_ROOT / "core.py").exists())


if __name__ == "__main__":
    unittest.main()
