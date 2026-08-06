import ast
import copy
import itertools
import os
import pathlib
import re
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "arnold_magic_node"
CORE_SOURCE_PATH = PACKAGE_ROOT / "arnold_magic_core.py"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from arnold_magic_node.core import matching as _matching
from arnold_magic_node.core.matching import (
    contains_any_substring,
    is_edit_distance_at_most_one,
)


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


def load_path_detection_class():
    core_source = CORE_SOURCE_PATH.read_text(encoding="utf-8-sig")
    core_tree = ast.parse(core_source)
    detection_node = next(
        node
        for node in core_tree.body
        if isinstance(node, ast.ClassDef) and node.name == "PathDetection"
    )
    detection_node = copy.deepcopy(detection_node)
    detection_node.name = "IsolatedPathDetection"
    detection_node.bases = []
    detection_node.keywords = []
    detection_node.decorator_list = []
    detection_node.body = [
        node
        for node in detection_node.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "detection_path_content"
    ]
    isolated_module = ast.fix_missing_locations(
        ast.Module(body=[detection_node], type_ignores=[])
    )
    namespace = {
        "_matching": _matching,
        "os": os,
        "pathlib": pathlib,
        "re": re,
    }
    exec(compile(isolated_module, str(CORE_SOURCE_PATH), "exec"), namespace)
    return namespace["IsolatedPathDetection"]


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

            detector = load_path_detection_class()()
            detector.language = {"DPC": {}}
            detector.feedback = None
            result = detector.detection_path_content(
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


def load_matching_processor_class():
    core_source = CORE_SOURCE_PATH.read_text(encoding="utf-8-sig")
    core_tree = ast.parse(core_source)
    processor_node = next(
        node
        for node in core_tree.body
        if isinstance(node, ast.ClassDef) and node.name == "NodeProcessor"
    )
    processor_node = copy.deepcopy(processor_node)
    processor_node.name = "IsolatedNodeProcessor"
    processor_node.bases = []
    processor_node.keywords = []
    processor_node.decorator_list = []
    processor_node.body = [
        node
        for node in processor_node.body
        if isinstance(node, ast.FunctionDef)
        and node.name in {"build_keyword_mapping", "FilterData"}
    ]
    isolated_module = ast.fix_missing_locations(
        ast.Module(body=[processor_node], type_ignores=[])
    )
    namespace = {
        "_matching": _matching,
        "defaultdict": defaultdict,
        "re": re,
    }
    exec(compile(isolated_module, str(CORE_SOURCE_PATH), "exec"), namespace)
    return namespace["IsolatedNodeProcessor"]


class TextureChannelMatchingTests(unittest.TestCase):
    def setUp(self):
        self.processor = load_matching_processor_class()()
        self.channel_keywords = {
            "baseColor": ["COLOR", "DIFFUSE"],
            "metalness": ["METAL", "DIFFUSE"],
            "normalCamera": ["NORMAL"],
        }
        self.keyword_to_channels, self.ordered_keywords = (
            self.processor.build_keyword_mapping(self.channel_keywords)
        )

    def test_duplicate_keyword_uses_channel_configuration_order(self):
        self.assertEqual(
            self.keyword_to_channels["diffuse"],
            ["baseColor", "metalness"],
        )
        self.assertEqual(
            self.processor.FilterData(
                "hero_diffuse",
                self.keyword_to_channels,
                self.ordered_keywords,
            ),
            "baseColor",
        )

    def test_exact_match_takes_priority_over_fuzzy_match(self):
        self.assertEqual(
            self.processor.FilterData(
                "hero_color_norml",
                self.keyword_to_channels,
                self.ordered_keywords,
            ),
            "baseColor",
        )

    def test_fuzzy_match_accepts_one_edit(self):
        self.assertEqual(
            self.processor.FilterData(
                "hero_norml",
                self.keyword_to_channels,
                self.ordered_keywords,
            ),
            "normalCamera",
        )

    def test_equal_exact_scores_use_texture_word_order(self):
        mapping, keywords = self.processor.build_keyword_mapping(
            {"first": ["alpha"], "second": ["beta"]}
        )

        self.assertEqual(
            self.processor.FilterData("beta_alpha", mapping, keywords),
            "second",
        )

    def test_returns_none_when_no_keyword_is_close(self):
        self.assertIsNone(
            self.processor.FilterData(
                "hero_unrelated",
                self.keyword_to_channels,
                self.ordered_keywords,
            )
        )


class DependencyRemovalContractTests(unittest.TestCase):
    def test_external_matching_packages_are_not_installed_or_imported(self):
        core_source = CORE_SOURCE_PATH.read_text(encoding="utf-8-sig")
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
        self.assertIn("from .core import matching as _matching", core_source)


if __name__ == "__main__":
    unittest.main()
