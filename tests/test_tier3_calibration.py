import collections
import hashlib
import json
import math
import unittest

from src.calibrate_tier3 import (
    FIXTURE_PATH,
    ROOT,
    cosine,
    load_pairs,
    score_pairs,
    summarize_scores,
)
from src.pattern_layer import PatternEncoder


class DeterministicEmbedder:
    model_name = "test/deterministic"
    model_revision = "fixture-test"
    dimensions = 3

    def __init__(self):
        self.inputs = []

    def embed(self, texts):
        self.inputs.extend(texts)
        vectors = []
        for text in texts:
            codepoints = [ord(character) for character in text]
            vector = (
                1.0 + sum(codepoints) % 101,
                1.0 + len(text) % 37,
                1.0 + sum(codepoints[::2]) % 71,
            )
            norm = math.sqrt(sum(value * value for value in vector))
            vectors.append([value / norm for value in vector])
        return vectors


class Tier3CalibrationTests(unittest.TestCase):
    def test_authoritative_fixture_has_expected_shape(self):
        pairs = load_pairs(FIXTURE_PATH)
        labels = collections.Counter(row["label"] for row in pairs)
        same_clusters = collections.Counter(
            row["cluster_a"]
            for row in pairs
            if row["label"] == "same_pattern"
        )

        self.assertEqual(len(pairs), 63)
        self.assertEqual(
            labels,
            {
                "same_pattern": 36,
                "ambiguous": 6,
                "contradiction": 6,
                "unrelated": 15,
            },
        )
        self.assertEqual(len(same_clusters), 6)
        self.assertEqual(set(same_clusters.values()), {6})

    def test_every_unique_text_is_encoded_once_through_pattern_encoder(self):
        pairs = load_pairs(FIXTURE_PATH)
        embedder = DeterministicEmbedder()

        scored, unique_text_count = score_pairs(pairs, PatternEncoder(embedder))

        expected_texts = {row["text_a"] for row in pairs} | {
            row["text_b"] for row in pairs
        }
        self.assertEqual(len(scored), 63)
        self.assertEqual(unique_text_count, 36)
        self.assertEqual(len(embedder.inputs), 36)
        self.assertEqual(set(embedder.inputs), expected_texts)
        self.assertTrue(all(-1 <= float(row["score"]) <= 1 for row in scored))

    def test_cosine_does_not_assume_normalized_vectors(self):
        self.assertAlmostEqual(cosine([2.0, 0.0], [4.0, 0.0]), 1.0)
        self.assertAlmostEqual(cosine([1.0, 0.0], [0.0, 3.0]), 0.0)
        with self.assertRaises(ValueError):
            cosine([1.0], [1.0, 2.0])
        with self.assertRaises(ValueError):
            cosine([0.0, 0.0], [1.0, 0.0])

    def test_range_check_uses_higher_minimum_and_lower_maximum(self):
        scored = [
            {"label": "same_pattern", "score": 0.80},
            {"label": "same_pattern", "score": 0.90},
            {"label": "ambiguous", "score": 0.70},
            {"label": "contradiction", "score": 0.75},
            {"label": "unrelated", "score": 0.10},
        ]

        _summaries, checks = summarize_scores(scored)
        by_pair = {
            (check["expected_higher"], check["expected_lower"]): check
            for check in checks
        }

        self.assertFalse(by_pair[("same_pattern", "ambiguous")]["overlap"])
        self.assertTrue(by_pair[("ambiguous", "contradiction")]["overlap"])
        self.assertFalse(by_pair[("same_pattern", "contradiction")]["overlap"])

    def test_committed_real_report_matches_fixture_and_runner(self):
        report_path = ROOT / "docs" / "tier3_calibration_results_v1.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        runner_path = ROOT / "src" / "calibrate_tier3.py"

        self.assertEqual(report["pair_count"], 63)
        self.assertEqual(report["unique_text_count"], 36)
        self.assertEqual(
            report["revision"],
            "1110a243fdf4706b3f48f1d95db1a4f5529b4d41",
        )
        self.assertEqual(
            report["fixture_sha256"],
            hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            report["runner_sha256"],
            hashlib.sha256(runner_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(report["labels"]["same_pattern"]["count"], 36)
        self.assertEqual(report["labels"]["unrelated"]["count"], 15)
        self.assertEqual(
            sum(check["overlap"] for check in report["range_checks"]),
            5,
        )


if __name__ == "__main__":
    unittest.main()
