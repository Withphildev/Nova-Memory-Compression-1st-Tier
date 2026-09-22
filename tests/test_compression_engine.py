import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from logic.compression_engine import (
    TokenizerUnavailableError,
    compress,
    compress_with_metadata,
    detect_mode,
    process_file,
)


ROOT = Path(__file__).resolve().parents[1]


class CompressionEngineTests(unittest.TestCase):
    def test_historical_csv_remains_a_regression_baseline(self):
        csv_path = ROOT / "data" / "memory_compression_comparison_v1.csv"
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for line_number, row in enumerate(csv.DictReader(handle), start=2):
                with self.subTest(line=line_number, original=row["Original"]):
                    self.assertEqual(compress(row["Original"], "compact"), row["Compressed"])
                    self.assertEqual(
                        compress(row["Original"], "expressive"),
                        row["Restored Compression"],
                    )

    def test_auto_detection_uses_whole_log_words(self):
        self.assertEqual(detect_mode("ERROR: database unavailable"), "compact")
        self.assertEqual(detect_mode('{"status": "active"}'), "compact")
        self.assertEqual(detect_mode("This information matters."), "expressive")
        self.assertEqual(detect_mode("A terrifying but meaningful memory."), "expressive")

    def test_metadata_marks_tier_one_as_lossy(self):
        result = compress_with_metadata("The man is driving a red car.", "compact")
        self.assertEqual(result.compressed, "man driving red car")
        self.assertEqual(result.resolved_mode, "compact")
        self.assertFalse(result.reversible_from_gist)
        self.assertGreater(result.character_savings_percent, 0)
        self.assertEqual(result.original_words, 7)
        self.assertEqual(result.compressed_words, 4)
        self.assertEqual(result.schema_version, "hydrangea.tier1.v2")
        self.assertEqual(
            [decision.status for decision in result.tokens],
            ["stripped", "kept", "stripped", "kept", "stripped", "kept", "kept"],
        )
        self.assertEqual(result.tokens[-1].text, "car.")
        self.assertEqual(result.tokens[-1].cleaned, "car")
        self.assertEqual(result.anchors, [])

    def test_expressive_metadata_retains_real_emotional_anchors(self):
        result = compress_with_metadata("Nova smiled as the echo returned.", "expressive")

        self.assertEqual(result.anchors, ["smiled", "as", "echo"])
        self.assertEqual(result.tokens[2].status, "emotional")
        self.assertIsNone(result.tokenizer)
        self.assertIsNone(result.token_savings_percent)

    def test_invalid_mode_is_rejected_even_for_empty_text(self):
        with self.assertRaises(ValueError):
            compress("", "unknown")  # type: ignore[arg-type]

    def test_tokenizer_metrics_fail_clearly_when_extra_is_missing(self):
        with mock.patch.dict("sys.modules", {"tiktoken": None}):
            with self.assertRaisesRegex(TokenizerUnavailableError, r"\.\[tokens\]"):
                compress_with_metadata("A small memory.", tokenizer="cl100k_base")

    def test_file_exports_are_bloom_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "memories.txt"
            csv_output = Path(temp_dir) / "memories.csv"
            jsonl_output = Path(temp_dir) / "memories.jsonl"
            source.write_text("The man is driving a red car.\n", encoding="utf-8")

            process_file(source, csv_output, "compact", "csv")
            process_file(source, jsonl_output, "compact", "jsonl")

            with csv_output.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["Compressed"], "man driving red car")
            self.assertEqual(rows[0]["Resolved Mode"], "compact")

            payload = json.loads(jsonl_output.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "hydrangea.tier1.v2")
            self.assertEqual(payload["original"], "The man is driving a red car.")
            self.assertFalse(payload["reversible_from_gist"])
            self.assertEqual(len(payload["tokens"]), 7)
            self.assertEqual(payload["anchors"], [])


if __name__ == "__main__":
    unittest.main()
