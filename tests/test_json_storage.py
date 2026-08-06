import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "arnold_magic_node"
CORE_SOURCE_PATH = PACKAGE_ROOT / "arnold_magic_core.py"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from arnold_magic_node.core.storage import load_json, save_json


class JsonStorageTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "名称": "基础色",
            "配置": {
                "通道": ["漫反射", "法线"],
                "启用": True,
                "备注": None,
            },
            "阈值": 0.5,
        }

    def test_json_file_is_utf8_and_human_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested" / "settings.json"

            result = save_json(target, self.data)
            text = target.read_text(encoding="utf-8")

            self.assertEqual(result, target)
            self.assertIn('"名称": "基础色"', text)
            self.assertEqual(json.loads(text), self.data)

    def test_unicode_and_nested_data_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "settings.json"

            save_json(target, self.data)

            self.assertEqual(load_json(target), self.data)

    def test_mapping_order_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "ordered.json"
            ordered_data = {"first": 1, "second": 2, "third": 3}

            save_json(target, ordered_data)

            self.assertEqual(list(load_json(target)), list(ordered_data))

    def test_missing_file_raises_file_not_found(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "missing.json"

            with self.assertRaises(FileNotFoundError):
                load_json(target)

    def test_invalid_json_raises_decode_error_without_rewriting_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "invalid.json"
            invalid_content = "{ invalid json"
            target.write_text(invalid_content, encoding="utf-8")

            with self.assertRaises(json.JSONDecodeError):
                load_json(target)

            self.assertEqual(target.read_text(encoding="utf-8"), invalid_content)

    def test_failed_save_keeps_previous_file_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "settings.json"
            save_json(target, self.data)

            with self.assertRaises(TypeError):
                save_json(target, {"unsupported": {"set value"}})

            self.assertEqual(load_json(target), self.data)
            self.assertEqual(list(target.parent.glob("settings.json.*.tmp")), [])

    def test_non_finite_numbers_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "settings.json"

            with self.assertRaises(ValueError):
                save_json(target, {"invalid": float("nan")})

    def test_cleanup_failure_does_not_hide_serialization_error(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "settings.json"

            with patch(
                "arnold_magic_node.core.storage.Path.unlink",
                side_effect=PermissionError("locked"),
            ):
                with self.assertRaises(TypeError):
                    save_json(target, {"unsupported": {"set value"}})


def load_data_manager_class():
    source = CORE_SOURCE_PATH.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    class_node = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "DataManager"
    )
    isolated_module = ast.fix_missing_locations(
        ast.Module(body=[class_node], type_ignores=[])
    )
    namespace = {
        "load_json_file": load_json,
        "save_json_file": save_json,
    }
    exec(compile(isolated_module, "arnold_magic_core.py", "exec"), namespace)
    return namespace["DataManager"]


class DataManagerIntegrationTests(unittest.TestCase):
    def test_data_manager_delegates_to_json_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "config.json"
            data = {"中文": [1, True, None]}
            manager = load_data_manager_class()()

            manager.save_json(target, data)

            self.assertEqual(manager.load_json(target), data)


class DefaultConfigIntegrationTests(unittest.TestCase):
    def test_complete_default_config_round_trips_through_json(self):
        from arnold_magic_node import default_config

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "default.json"

            save_json(target, default_config.Arnold_Magic_Settings)

            self.assertEqual(
                load_json(target),
                default_config.Arnold_Magic_Settings,
            )

    def test_initializer_creates_and_repairs_json_config(self):
        from arnold_magic_node import default_config

        with tempfile.TemporaryDirectory() as directory:
            data = {"setting": "默认值"}
            default_config.detecting_initial_config_files(
                directory,
                "settings",
                data,
            )
            target = Path(directory) / "settings.json"

            self.assertEqual(load_json(target), data)

            target.write_text("", encoding="utf-8")
            default_config.detecting_initial_config_files(
                directory,
                "settings",
                data,
            )

            self.assertEqual(load_json(target), data)


class JsonMigrationContractTests(unittest.TestCase):
    def test_msgpack_binary_files_and_dependency_bootstrap_are_removed(self):
        production_files = tuple(PACKAGE_ROOT.rglob("*.py"))
        combined_source = "\n".join(
            file_path.read_text(encoding="utf-8-sig")
            for file_path in production_files
        )
        imported_modules = set()

        for file_path in production_files:
            tree = ast.parse(
                file_path.read_text(encoding="utf-8-sig")
            )
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported_modules.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported_modules.add(node.module)

        self.assertNotIn("msgpack", imported_modules)
        self.assertNotIn("msgpack", combined_source.lower())
        self.assertNotIn("packb", combined_source)
        self.assertNotIn("unpackb", combined_source)
        self.assertNotIn(".bin", combined_source)
        self.assertNotIn("bin_load_data", combined_source)
        self.assertNotIn("bin_save_data", combined_source)
        self.assertFalse((PROJECT_ROOT / "dependencies.py").exists())
        self.assertNotIn(
            "dependencies",
            (PACKAGE_ROOT / "bootstrap.py").read_text(encoding="utf-8-sig"),
        )
        self.assertGreaterEqual(
            combined_source.count('endswith(".json")'),
            2,
        )

        for language_file in ("zh_CN.json", "en_US.json"):
            with self.subTest(language_file=language_file):
                language = load_json(
                    PACKAGE_ROOT / "resources" / "i18n" / language_file
                )
                self.assertNotIn("DLibs", language)


if __name__ == "__main__":
    unittest.main()
