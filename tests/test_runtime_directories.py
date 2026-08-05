import importlib
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
PACKAGE_ROOT = SCRIPTS_ROOT / "arnold_magic_node"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))


class StorageDirectoryTests(unittest.TestCase):
    def test_ensure_parent_directory_creates_nested_parents(self):
        storage = importlib.import_module("arnold_magic_node.core.storage")

        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "settings" / "profiles" / "config.json"

            result = storage.ensure_parent_directory(target)

            self.assertEqual(result, target)
            self.assertTrue(target.parent.is_dir())

    def test_ensure_directory_is_idempotent(self):
        storage = importlib.import_module("arnold_magic_node.core.storage")

        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "cache" / "textures"

            first_result = storage.ensure_directory(target)
            second_result = storage.ensure_directory(target)

            self.assertEqual(first_result, target)
            self.assertEqual(second_result, target)
            self.assertTrue(target.is_dir())


class StartupArchitectureTests(unittest.TestCase):
    def test_runtime_directory_initializer_is_removed(self):
        self.assertFalse((PROJECT_ROOT / "runtime_directories.py").exists())

    def test_startup_does_not_depend_on_runtime_directory_initializer(self):
        startup_source = (PACKAGE_ROOT / "bootstrap.py").read_text(encoding="utf-8")

        self.assertNotIn("runtime_directories", startup_source)


if __name__ == "__main__":
    unittest.main()
