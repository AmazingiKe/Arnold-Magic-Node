import unittest

from arnold_magic_node.core.magic_connection import (
    DEFAULT_CHANNEL_PRIORITY,
    MagicConnectionConfigError,
    build_magic_connection_plan,
    match_channel,
    normalize_texture_name,
    reorder_matches,
)


class MagicConnectionMatchingTests(unittest.TestCase):
    def test_normalizes_texture_filename_before_matching(self):
        self.assertEqual(
            normalize_texture_name("hero-body_BASE_COLOR.1001.exr"),
            "HERO BODY BASE COLOR 1001",
        )

    def test_exact_match_wins_over_fuzzy_match(self):
        filter_data = {
            "baseColor": ["COLOR"],
            "normalCamera": ["NORMAL"],
        }

        self.assertEqual(
            match_channel("hero_COLOR_norml.exr", filter_data),
            "baseColor",
        )

    def test_fuzzy_match_accepts_one_edit(self):
        self.assertEqual(
            match_channel("hero_norml.exr", {"normalCamera": ["NORMAL"]}),
            "normalCamera",
        )

    def test_no_match_returns_none(self):
        self.assertIsNone(
            match_channel("hero_unrelated.exr", {"baseColor": ["COLOR"]})
        )


class MagicConnectionPlanTests(unittest.TestCase):
    def setUp(self):
        self.filter_data = {
            "baseColor": ["ALBEDO"],
            "specularRoughness": ["ROUGHNESS"],
            "normalCamera": ["NORMAL"],
            "displacement": ["HEIGHT"],
        }
        self.processing_data = {
            "baseColor": {
                "NodeList": ["aiColorCorrect"],
                "InputPort": "input",
                "OutputPort": "outColor",
            },
            "specularRoughness": {
                "NodeList": ["aiRampRgb", "aiRange"],
                "InputPort": "input",
                "OutputPort": "outColorR",
            },
            "normalCamera": {
                "NodeList": ["aiColorCorrect"],
                "InputPort": "input",
                "OutputPort": "outColor",
            },
            "displacement": {
                "NodeList": ["aiRange"],
                "InputPort": "input",
                "OutputPort": "outValue",
            },
        }

    def test_reorders_matches_by_material_channel_priority(self):
        matches = {
            "normal_file": "normalCamera",
            "roughness_file": "specularRoughness",
            "base_file": "baseColor",
            "unknown_file": None,
        }

        self.assertEqual(
            list(reorder_matches(matches)),
            [
                ("base_file", "baseColor"),
                ("roughness_file", "specularRoughness"),
                ("normal_file", "normalCamera"),
            ],
        )

    def test_plan_uses_configured_processing_output_port(self):
        plan = build_magic_connection_plan(
            texture_files={"roughness_file": "hero_ROUGHNESS.exr"},
            filter_data=self.filter_data,
            processing_data=self.processing_data,
            magic_connection_options={"specularRoughness": True},
            processing_options={"specularRoughness": True},
            material_name="shader1",
        )

        self.assertEqual(len(plan.textures), 1)
        self.assertEqual(
            plan.textures[0].processing.output_port,
            "outColorR",
        )
        self.assertTrue(plan.textures[0].connect_enabled)

    def test_plan_keeps_processing_and_material_connection_switches_separate(self):
        plan = build_magic_connection_plan(
            texture_files={"base_file": "hero_ALBEDO.exr"},
            filter_data=self.filter_data,
            processing_data=self.processing_data,
            magic_connection_options={"baseColor": False},
            processing_options={"baseColor": True},
            material_name="shader1",
        )

        self.assertIsNotNone(plan.textures[0].processing)
        self.assertFalse(plan.textures[0].connect_enabled)

    def test_plan_rejects_missing_processing_nodes(self):
        with self.assertRaises(MagicConnectionConfigError):
            build_magic_connection_plan(
                texture_files={"roughness_file": "hero_ROUGHNESS.exr"},
                filter_data=self.filter_data,
                processing_data={},
                magic_connection_options={"specularRoughness": True},
                processing_options={"specularRoughness": True},
                material_name="shader1",
            )

    def test_default_priority_contains_all_supported_channels(self):
        self.assertIn("specularAnisotropy", DEFAULT_CHANNEL_PRIORITY)
        self.assertIn("specularRotation", DEFAULT_CHANNEL_PRIORITY)


if __name__ == "__main__":
    unittest.main()
