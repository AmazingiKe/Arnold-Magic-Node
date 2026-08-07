import ast
import json
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


def all_imported_modules(path):
    imports = set(imported_modules(path))
    for node in ast.walk(module_tree(path)):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
    return imports


def maya_command_calls(path):
    calls = set()
    for node in ast.walk(module_tree(path)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "cmds":
            calls.add(node.func.attr)
    return calls


class UiStructureTests(unittest.TestCase):
    def test_ui_modules_use_tools_not_application_or_legacy_core(self):
        excluded = {"__init__.py", "_qt_compat.py", "_workspace.py", "texture_batch_importer_dialog.py"}
        for path in UI_ROOT.glob("*.py"):
            imports = all_imported_modules(path)
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

    def test_dialog_modules_match_their_primary_class_names(self):
        expected_dialogs = {
            "settings_dialog.py": "SettingsDialog",
            "aov_light_group_dialog.py": "AovLightGroupDialog",
            "rendering_preset_dialog.py": "RenderingPresetDialog",
            "texture_batch_importer_dialog.py": "TextureBatchImporterDialog",
        }
        actual_dialogs = {path.name for path in UI_ROOT.glob("*_dialog.py")}
        self.assertEqual(actual_dialogs, set(expected_dialogs))

        for filename, class_name in expected_dialogs.items():
            classes = {
                node.name
                for node in ast.walk(module_tree(UI_ROOT / filename))
                if isinstance(node, ast.ClassDef)
            }
            self.assertIn(class_name, classes, filename)

    def test_qt_compatibility_imports_are_centralized(self):
        qt_source = (UI_ROOT / "_qt_compat.py").read_text(encoding="utf-8-sig")
        self.assertIn("PySide", qt_source)
        for path in UI_ROOT.glob("*.py"):
            if path.name == "_qt_compat.py":
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

    def test_ui_only_uses_maya_for_window_construction(self):
        forbidden_commands = {
            "connectAttr", "delete", "getAttr", "listConnections", "ls",
            "nodeType", "objExists", "rename", "select", "setAttr",
            "shadingNode",
        }
        for path in UI_ROOT.glob("*.py"):
            self.assertEqual(
                maya_command_calls(path) & forbidden_commands,
                set(),
                path.name,
            )
            imports = imported_modules(path)
            self.assertFalse(
                any(module == "mtoa" or module.startswith("mtoa.") for module in imports),
                path.name,
            )

    def test_settings_preset_menu_is_removed(self):
        source = (UI_ROOT / "settings_dialog.py").read_text(encoding="utf-8-sig")
        removed_names = {
            "settings_presets_path",
            "settings_presets_menu",
            "load_settings_preset",
            "add_settings_preset",
            "modify_settings_preset",
            "delete_settings_preset",
        }
        for name in removed_names:
            self.assertNotIn(name, source)

    def test_settings_dialog_embeds_localized_ai_settings_widget(self):
        source = (UI_ROOT / "settings_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn("from .ai_settings_widget import AiSettingsWidget", source)
        self.assertIn("self.create_ai_settings_tab()", source)
        self.assertIn("def create_ai_settings_tab", source)
        self.assertIn("AiSettingsWidget(", source)

        required_keys = {
            "tab",
            "connection_section",
            "api_style_label",
            "responses_option",
            "chat_completions_option",
            "base_url_label",
            "model_label",
            "api_key_env_label",
            "api_key_env_hint",
            "limits_section",
            "timeout_seconds_label",
            "max_output_tokens_label",
            "max_request_bytes_label",
            "max_response_bytes_label",
            "chat_token_parameter_label",
            "session_key_section",
            "session_key_label",
            "session_key_placeholder",
            "session_key_hint",
            "session_target",
            "local_key_disabled",
            "session_configured",
            "session_not_configured",
            "environment_configured",
            "environment_not_configured",
            "save_button",
            "clear_key_button",
            "saved_message",
            "cleared_message",
            "error_prefix",
        }
        for language_name in ("zh_CN.json", "en_US.json"):
            language_path = (
                PACKAGE_ROOT / "resources" / "i18n" / language_name
            )
            language = json.loads(language_path.read_text(encoding="utf-8-sig"))
            ai_language = language["ArnoldMagicNode"]["AMNSP_WIN"][
                "create_ai_settings_tab"
            ]
            self.assertEqual(set(ai_language), required_keys, language_name)


if __name__ == "__main__":
    unittest.main()
