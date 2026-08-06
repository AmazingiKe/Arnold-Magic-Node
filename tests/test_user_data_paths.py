import tempfile
import unittest
from pathlib import Path

from arnold_magic_node.core.paths import (
    LANGUAGES_ROOT,
    user_aov_cache_path,
    user_data_root,
    user_log_path,
    user_preset_dir,
    user_settings_path,
)


class UserDataPathTests(unittest.TestCase):
    def test_user_root_uses_plugin_namespace(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(
                user_data_root(directory),
                Path(directory) / "arnold_magic_node",
            )

    def test_settings_and_presets_are_converged(self):
        root = Path("maya-user") / "arnold_magic_node"

        self.assertEqual(
            user_settings_path(root, "Arnold_Magic_Settings.json"),
            root / "settings" / "Arnold_Magic_Settings.json",
        )
        self.assertEqual(user_preset_dir(root, "settings"), root / "presets" / "settings")
        self.assertEqual(user_preset_dir(root, "render"), root / "presets" / "render")

    def test_single_file_runtime_data_is_not_wrapped_in_extra_directories(self):
        root = Path("maya-user") / "arnold_magic_node"

        self.assertEqual(user_aov_cache_path(root), root / "aov_light_group_cache.json")
        self.assertEqual(user_log_path(root, "plugin.log"), root / "logs" / "plugin.log")
        self.assertNotIn("cache", user_aov_cache_path(root).parts)

    def test_invalid_preset_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            user_preset_dir(Path("maya-user"), "cache")

    def test_languages_are_bundled_read_only_resources(self):
        self.assertTrue((LANGUAGES_ROOT / "en_US.json").is_file())
        self.assertTrue((LANGUAGES_ROOT / "zh_CN.json").is_file())


if __name__ == "__main__":
    unittest.main()
