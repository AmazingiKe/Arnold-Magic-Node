import unittest

from arnold_magic_node.core.naming import replacement_name


class ReplacementNameTests(unittest.TestCase):
    def test_replaces_all_literal_occurrences(self):
        self.assertEqual(
            replacement_name("prefix_mesh_prefix_", "prefix_", ""),
            "mesh_",
        )

    def test_can_ignore_case(self):
        self.assertEqual(
            replacement_name("PASTED__mesh", "pasted__", "", ignore_case=True),
            "mesh",
        )

    def test_returns_none_when_disabled_or_not_matched(self):
        self.assertIsNone(replacement_name("mesh", "mesh", "geo", enabled=False))
        self.assertIsNone(replacement_name("mesh", "prefix_", ""))


if __name__ == "__main__":
    unittest.main()
