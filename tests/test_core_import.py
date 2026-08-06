import ast
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "arnold_magic_node"
CORE_STANDARD_LIBRARY = {
    "collections",
    "copy",
    "dataclasses",
    "datetime",
    "difflib",
    "json",
    "os",
    "pathlib",
    "re",
    "tempfile",
    "time",
    "typing",
}


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


def internal_layer_dependencies(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    current_layer = path.parent.name
    dependencies = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level == 1:
            dependencies.add(current_layer)
        elif node.level >= 2 and node.module:
            dependencies.add(node.module.split(".", 1)[0])
        elif node.level == 0 and node.module:
            module_parts = node.module.split(".")
            if module_parts[0] == "arnold_magic_node" and len(module_parts) > 1:
                dependencies.add(module_parts[1])
    return dependencies


def python_files(layer):
    return (PACKAGE_ROOT / layer).glob("*.py")


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
        for path in python_files("tools"):
            self.assertNotIn("application", import_modules(path), path.name)

    def test_tools_use_package_adapters_instead_of_host_modules(self):
        for path in python_files("tools"):
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

    def test_core_only_depends_on_the_standard_library_and_core(self):
        for path in python_files("core"):
            dependencies = internal_layer_dependencies(path)
            self.assertTrue(dependencies <= {"core"}, path.name)

            imported_roots = {
                name.split(".", 1)[0]
                for name in direct_host_imports(path)
            }
            self.assertTrue(
                imported_roots <= CORE_STANDARD_LIBRARY,
                path.name,
            )

    def test_maya_layer_only_depends_on_core_and_maya(self):
        for path in python_files("maya"):
            dependencies = internal_layer_dependencies(path)
            self.assertTrue(dependencies <= {"core", "maya"}, path.name)

    def test_tools_only_depend_on_core_maya_and_tools(self):
        for path in python_files("tools"):
            dependencies = internal_layer_dependencies(path)
            self.assertTrue(
                dependencies <= {"core", "maya", "tools"},
                path.name,
            )

    def test_legacy_core_monolith_is_removed(self):
        self.assertFalse((PACKAGE_ROOT / "arnold_magic_core.py").exists())
        self.assertFalse((PROJECT_ROOT / "core.py").exists())


if __name__ == "__main__":
    unittest.main()
