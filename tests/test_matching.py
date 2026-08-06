import ast
import itertools
import pathlib
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "arnold_magic_node"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from arnold_magic_node.core.matching import (
    contains_any_substring,
    is_edit_distance_at_most_one,
)
from arnold_magic_node.core.magic_connection import (
    build_keyword_mapping,
    match_channel,
)
from arnold_magic_node.core.path_detection import scan_directory


def reference_edit_distance(left, right):
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, 1):
        current = [left_index]
        for right_index, right_char in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


class KeywordMatchingTests(unittest.TestCase):
    def test_matching_is_case_insensitive(self):
        self.assertTrue(
            contains_any_substring("Asset_PREVIEW.exr", ["_preview"])
        )

    def test_matching_keeps_existing_substring_semantics(self):
        self.assertTrue(contains_any_substring("asset_LOD10.exr", ["LOD1"]))

    def test_matching_trims_keywords_and_ignores_blank_values(self):
        keywords = [" foo ", "", "   ", "BAR"]

        self.assertTrue(contains_any_substring("asset_foo.exr", keywords))
        self.assertTrue(contains_any_substring("asset_bar.exr", keywords))
        self.assertFalse(contains_any_substring("asset_baz.exr", keywords))

    def test_matching_treats_regular_expression_characters_as_text(self):
        self.assertTrue(contains_any_substring("asset_a+b.exr", ["a+b"]))
        self.assertFalse(contains_any_substring("asset_aaab.exr", ["a+b"]))

    def test_empty_keyword_list_does_not_match(self):
        self.assertFalse(contains_any_substring("asset.exr", []))


class PathDetectionIntegrationTests(unittest.TestCase):
    def test_combines_keyword_and_format_filters_with_comma_strings(self):
        with tempfile.TemporaryDirectory() as directory:
            file_names = (
                "asset_PREVIEW.exr",
                "asset_LOD10.PNG",
                "asset_lod2.png",
                "asset.exr",
                "asset.jpg",
            )
            for file_name in file_names:
                (pathlib.Path(directory) / file_name).touch()

            result = scan_directory(
                directory,
                "_preview， LOD1",
                "EXR, .PNG",
            )

            self.assertEqual(
                result,
                {
                    "asset_lod2.png": str(pathlib.Path(directory) / "asset_lod2.png"),
                    "asset.exr": str(pathlib.Path(directory) / "asset.exr"),
                },
            )


class OneEditDistanceTests(unittest.TestCase):
    def test_accepts_equal_values(self):
        self.assertTrue(is_edit_distance_at_most_one("", ""))
        self.assertTrue(is_edit_distance_at_most_one("roughness", "roughness"))

    def test_accepts_one_insertion_deletion_or_substitution(self):
        one_edit_pairs = (
            ("abc", "axc"),
            ("abc", "xabc"),
            ("abc", "axbc"),
            ("abc", "abcx"),
            ("xabc", "abc"),
            ("axbc", "abc"),
            ("abcx", "abc"),
            ("", "a"),
            ("a", ""),
            ("贴图", "贴圖"),
            ("😀a", "😀b"),
        )

        for left, right in one_edit_pairs:
            with self.subTest(left=left, right=right):
                self.assertTrue(is_edit_distance_at_most_one(left, right))

    def test_rejects_values_more_than_one_edit_apart(self):
        distant_pairs = (
            ("", "ab"),
            ("abc", "axy"),
            ("ab", "abcd"),
            ("ab", "ba"),
            ("é", "e\u0301"),
        )

        for left, right in distant_pairs:
            with self.subTest(left=left, right=right):
                self.assertFalse(is_edit_distance_at_most_one(left, right))

    def test_matches_reference_distance_for_all_short_binary_strings(self):
        values = [
            "".join(chars)
            for length in range(5)
            for chars in itertools.product("ab", repeat=length)
        ]

        for left in values:
            for right in values:
                with self.subTest(left=left, right=right):
                    self.assertEqual(
                        is_edit_distance_at_most_one(left, right),
                        reference_edit_distance(left, right) <= 1,
                    )


class TextureChannelMatchingTests(unittest.TestCase):
    def setUp(self):
        self.channel_keywords = {
            "baseColor": ["COLOR", "DIFFUSE"],
            "metalness": ["METAL", "DIFFUSE"],
            "normalCamera": ["NORMAL"],
        }
        self.keyword_to_channels, self.ordered_keywords = (
            build_keyword_mapping(self.channel_keywords)
        )
        self.mapping = (self.keyword_to_channels, self.ordered_keywords)

    def test_duplicate_keyword_uses_channel_configuration_order(self):
        self.assertEqual(
            self.keyword_to_channels["diffuse"],
            ["baseColor", "metalness"],
        )
        self.assertEqual(
            match_channel(
                "hero_diffuse",
                self.channel_keywords,
                self.mapping,
            ),
            "baseColor",
        )

    def test_exact_match_takes_priority_over_fuzzy_match(self):
        self.assertEqual(
            match_channel(
                "hero_color_norml",
                self.channel_keywords,
                self.mapping,
            ),
            "baseColor",
        )

    def test_fuzzy_match_accepts_one_edit(self):
        self.assertEqual(
            match_channel(
                "hero_norml",
                self.channel_keywords,
                self.mapping,
            ),
            "normalCamera",
        )

    def test_equal_exact_scores_use_texture_word_order(self):
        filter_data = {"first": ["alpha"], "second": ["beta"]}
        mapping = build_keyword_mapping(filter_data)

        self.assertEqual(
            match_channel("beta_alpha", filter_data, mapping),
            "second",
        )

    def test_returns_none_when_no_keyword_is_close(self):
        self.assertIsNone(
            match_channel(
                "hero_unrelated",
                self.channel_keywords,
                self.mapping,
            )
        )


class DependencyRemovalContractTests(unittest.TestCase):
    def test_external_matching_packages_are_not_installed_or_imported(self):
        core_source = "\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in (PACKAGE_ROOT / "core").glob("*.py")
        )
        core_tree = ast.parse(core_source)
        imported_modules = set()

        for node in ast.walk(core_tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)

        self.assertTrue(
            imported_modules.isdisjoint({"Levenshtein", "ahocorapy"})
        )
        self.assertFalse((PROJECT_ROOT / "dependencies.py").exists())
        self.assertNotIn("KeywordTree", core_source)
        self.assertNotIn("Levenshtein.distance", core_source)
        self.assertIn("from . import matching as _matching", core_source)


if __name__ == "__main__":
    unittest.main()
