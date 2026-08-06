import ast
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "arnold_magic_node"
RUNTIME_PATH = PACKAGE_ROOT / "tools" / "runtime.py"


class KeyboardDependencyRemovalTests(unittest.TestCase):
    def test_keyboard_package_is_not_installed_or_imported(self):
        sources = []
        for path in PACKAGE_ROOT.rglob("*.py"):
            sources.append(path.read_text(encoding="utf-8-sig"))
        source = "\n".join(sources)
        self.assertFalse((PROJECT_ROOT / "dependencies.py").exists())
        self.assertNotIn("keyboard.is_pressed", source)
        self.assertNotIn("import keyboard", source)

    def test_maya_modifier_helper_supports_shift_alt_and_combinations(self):
        tree = ast.parse(RUNTIME_PATH.read_text(encoding="utf-8-sig"))
        helper_nodes = [
            node
            for node in tree.body
            if (
                isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Name)
                    and target.id in {"MAYA_SHIFT_MODIFIER", "MAYA_ALT_MODIFIER"}
                    for target in node.targets
                )
            )
            or (
                isinstance(node, ast.FunctionDef)
                and node.name == "is_modifier_pressed"
            )
        ]
        module = ast.fix_missing_locations(
            ast.Module(body=helper_nodes, type_ignores=[])
        )
        namespace = {}
        exec(compile(module, "runtime.py", "exec"), namespace)

        is_pressed = namespace["is_modifier_pressed"]
        shift = namespace["MAYA_SHIFT_MODIFIER"]
        alt = namespace["MAYA_ALT_MODIFIER"]
        self.assertFalse(is_pressed(shift, 0))
        self.assertTrue(is_pressed(shift, shift))
        self.assertTrue(is_pressed(alt, alt))
        self.assertTrue(is_pressed(shift, shift | alt))
        self.assertTrue(is_pressed(alt, shift | alt))

    def test_tools_use_maya_modifier_masks(self):
        source = RUNTIME_PATH.read_text(encoding="utf-8-sig")
        self.assertIn("MAYA_SHIFT_MODIFIER", source)
        self.assertIn("MAYA_ALT_MODIFIER", source)
        self.assertIn("is_modifier_pressed", source)


if __name__ == "__main__":
    unittest.main()
