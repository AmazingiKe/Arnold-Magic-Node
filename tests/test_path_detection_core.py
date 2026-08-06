import tempfile
import unittest
from pathlib import Path

from arnold_magic_node.core.path_detection import (
    collect_file_info,
    process_file_names,
    scan_directory,
)
from arnold_magic_node.core.similarity import (
    calculate_similarity,
    creation_time_similarity,
    file_type_similarity,
    processed_name_similarity,
    resolution_similarity,
    select_matches,
)


class DirectoryScanTests(unittest.TestCase):
    def test_filters_keywords_and_keeps_requested_formats(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for filename in ("rock_color.PNG", "rock_preview.png", "rock.txt"):
                (root / filename).write_bytes(b"data")

            result = scan_directory(
                root,
                exclude_keywords="preview, lod1",
                include_formats="png, exr",
            )

        self.assertEqual(list(result), ["rock_color.PNG"])
        self.assertTrue(result["rock_color.PNG"].endswith("rock_color.PNG"))

    def test_missing_directory_raises_the_original_os_error(self):
        with self.assertRaises(OSError):
            scan_directory(Path("definitely-missing-directory"), [], None)


class FileInformationTests(unittest.TestCase):
    def test_collects_creation_time_type_and_injected_dimensions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "asset.exr"
            path.write_bytes(b"image")
            result = collect_file_info(
                {"asset.exr": str(path)},
                image_dimensions=lambda file_path: (2048, 1024),
            )

        self.assertEqual(result["asset.exr"]["file_type"], ".exr")
        self.assertEqual(result["asset.exr"]["resolution"], (2048, 1024))
        self.assertRegex(
            result["asset.exr"]["creation_time"],
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
        )

    def test_processes_names_without_mutating_the_source_mapping(self):
        source = {
            "Rock_BaseColor_2K.exr": {
                "file_type": ".exr",
                "resolution": (2, 2),
                "creation_time": "2026-01-01 00:00:00",
            }
        }
        result = process_file_names(
            source,
            excluded_words=["2K"],
            texture_filters={"baseColor": ["BASECOLOR"]},
        )

        self.assertNotIn("processed_name", source["Rock_BaseColor_2K.exr"])
        self.assertEqual(result["Rock_BaseColor_2K.exr"]["processed_name"], "ROCK")


class SimilarityTests(unittest.TestCase):
    def test_individual_similarity_functions_preserve_existing_rules(self):
        self.assertEqual(processed_name_similarity("Rock", "rock"), 1.0)
        self.assertEqual(processed_name_similarity("", "rock"), 0.0)
        self.assertEqual(resolution_similarity((2048, 2048), (2048, 2048)), 1.0)
        self.assertEqual(resolution_similarity((0, 0), (2048, 2048)), 0.0)
        self.assertEqual(file_type_similarity(".EXR", ".exr"), 1.0)
        self.assertEqual(
            creation_time_similarity(
                "2026-01-01 00:00:00", "2026-01-02 00:00:00", 2
            ),
            0.5,
        )

    def test_calculates_weighted_similarity_for_each_candidate(self):
        target = {
            "target.exr": {
                "processed_name": "ROCK",
                "resolution": (2, 2),
                "file_type": ".exr",
                "creation_time": "2026-01-01 00:00:00",
            }
        }
        candidates = {
            "candidate.exr": {
                "processed_name": "ROCK",
                "resolution": (2, 2),
                "file_type": ".exr",
                "creation_time": "2026-01-01 00:00:00",
            }
        }
        weights = {
            "name_weight": 0.55,
            "resolution_weight": 0.15,
            "format_weight": 0.05,
            "creation_time_weight": 0.15,
        }

        result = calculate_similarity(target, candidates, weights, max_diff=30)
        self.assertAlmostEqual(
            result["candidate.exr"],
            0.9,
        )

    def test_selects_values_around_the_threshold_in_descending_order(self):
        result = select_matches(
            {"a": 0.95, "b": 0.9, "c": 0.7},
            auto_max_value=True,
            similarity_max=1.0,
            similarity_range=0.06,
        )
        self.assertEqual(result, [("a", 0.95), ("b", 0.9)])

    def test_empty_similarity_mapping_preserves_max_error(self):
        with self.assertRaises(ValueError):
            select_matches({}, True, 1.0, 0.1)


if __name__ == "__main__":
    unittest.main()
