"""Score the labeled Tier 3 fixture without selecting policy thresholds.

Usage:
    python -m pip install -e '.[tier3]'
    python src/calibrate_tier3.py --revision <pinned-model-revision>

The revision is required so a floating model can never be calibrated by
accident. This runner reports evidence; it does not enable automatic merging.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import statistics
import sys
from itertools import combinations
from pathlib import Path
from typing import Sequence

from logic.compression_engine import compress_with_metadata
from src.pattern_layer import (
    EmbeddingDependencyUnavailableError,
    PatternEncoder,
    PatternMemory,
    SentenceTransformerEmbedder,
)


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = ROOT / "data" / "tier3_calibration_pairs_v1.csv"
LABEL_ORDER = ("same_pattern", "ambiguous", "contradiction", "unrelated")
REQUIRED_COLUMNS = {
    "pair_id",
    "label",
    "cluster_a",
    "text_a",
    "cluster_b",
    "text_b",
    "notes",
}


class CalibrationFixtureError(ValueError):
    """Raised when a calibration fixture cannot support a trustworthy run."""


def load_pairs(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or ())
        if columns != REQUIRED_COLUMNS:
            missing = sorted(REQUIRED_COLUMNS - columns)
            extra = sorted(columns - REQUIRED_COLUMNS)
            raise CalibrationFixtureError(
                f"fixture columns do not match; missing={missing}, extra={extra}"
            )
        pairs = list(reader)

    if not pairs:
        raise CalibrationFixtureError("fixture contains no pairs")

    pair_ids: set[str] = set()
    text_pairs: set[tuple[str, str]] = set()
    labels: set[str] = set()
    for line_number, row in enumerate(pairs, start=2):
        pair_id = row["pair_id"].strip()
        label = row["label"].strip()
        text_a = row["text_a"].strip()
        text_b = row["text_b"].strip()
        if not pair_id or not text_a or not text_b:
            raise CalibrationFixtureError(
                f"line {line_number} requires pair_id, text_a, and text_b"
            )
        if pair_id in pair_ids:
            raise CalibrationFixtureError(f"duplicate pair_id: {pair_id}")
        if label not in LABEL_ORDER:
            raise CalibrationFixtureError(
                f"line {line_number} has unsupported label: {label}"
            )
        canonical_pair = tuple(sorted((text_a, text_b)))
        if canonical_pair in text_pairs:
            raise CalibrationFixtureError(
                f"line {line_number} duplicates an earlier unordered text pair"
            )
        pair_ids.add(pair_id)
        text_pairs.add(canonical_pair)
        labels.add(label)

    missing_labels = set(LABEL_ORDER) - labels
    if missing_labels:
        raise CalibrationFixtureError(
            f"fixture does not cover labels: {sorted(missing_labels)}"
        )
    return pairs


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("vectors must have equal dimensions")
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        raise ValueError("cannot compute cosine similarity against a zero vector")
    return dot / (norm_a * norm_b)


def embed_unique_texts(
    pairs: Sequence[dict[str, str]],
    encoder: PatternEncoder,
) -> dict[str, tuple[float, ...]]:
    """Embed every exact fixture string once through the Tier 3 boundary."""

    unique_texts = sorted(
        {row["text_a"] for row in pairs} | {row["text_b"] for row in pairs}
    )
    vectors: dict[str, tuple[float, ...]] = {}
    for text in unique_texts:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        tier1 = compress_with_metadata(text, mode="expressive")
        memory = PatternMemory.from_results(
            source_id=f"calibration-{digest[:16]}",
            observed_at="tier3-calibration-fixture-v1",
            tier1=tier1,
        )
        vectors[text] = encoder.encode(memory).vector
    return vectors


def score_pairs(
    pairs: Sequence[dict[str, str]],
    encoder: PatternEncoder,
) -> tuple[list[dict[str, object]], int]:
    vector_by_text = embed_unique_texts(pairs, encoder)
    scored = [
        {
            **row,
            "score": cosine(
                vector_by_text[row["text_a"]], vector_by_text[row["text_b"]]
            ),
        }
        for row in pairs
    ]
    return scored, len(vector_by_text)


def summarize_scores(
    scored: Sequence[dict[str, object]],
) -> tuple[dict[str, dict[str, object]], list[dict[str, object]]]:
    by_label: dict[str, list[float]] = {label: [] for label in LABEL_ORDER}
    for row in scored:
        by_label[str(row["label"])].append(float(row["score"]))

    summaries: dict[str, dict[str, object]] = {}
    ranges: dict[str, tuple[float, float]] = {}
    for label in LABEL_ORDER:
        scores = sorted(by_label[label])
        if not scores:
            continue
        ranges[label] = (scores[0], scores[-1])
        summaries[label] = {
            "count": len(scores),
            "min": scores[0],
            "max": scores[-1],
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "scores": scores,
        }

    overlaps = []
    for expected_higher, expected_lower in combinations(LABEL_ORDER, 2):
        higher_min = ranges[expected_higher][0]
        lower_max = ranges[expected_lower][1]
        overlaps.append(
            {
                "expected_higher": expected_higher,
                "expected_lower": expected_lower,
                "overlap": higher_min <= lower_max,
                "higher_min": higher_min,
                "lower_max": lower_max,
                "margin": higher_min - lower_max,
            }
        )
    return summaries, overlaps


def build_report(
    *,
    fixture: Path,
    scored: list[dict[str, object]],
    unique_text_count: int,
    encoder: PatternEncoder,
) -> dict[str, object]:
    summaries, overlaps = summarize_scores(scored)
    try:
        fixture_name = str(fixture.resolve().relative_to(ROOT))
    except ValueError:
        fixture_name = str(fixture.resolve())

    runtime = {"python": platform.python_version()}
    for package in ("sentence-transformers", "transformers", "torch"):
        try:
            runtime[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            runtime[package] = "not-installed"

    return {
        "schema_version": "hydrangea.tier3-calibration.v1",
        "model": encoder.embedder.model_name,
        "revision": encoder.embedder.model_revision,
        "fixture": fixture_name,
        "fixture_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runtime": runtime,
        "pair_count": len(scored),
        "unique_text_count": unique_text_count,
        "labels": summaries,
        "range_checks": overlaps,
        "pairs": scored,
    }


def print_report(report: dict[str, object]) -> None:
    print(f"model: {report['model']}  revision: {report['revision']}")
    print(
        f"fixture: {report['fixture']}  pairs: {report['pair_count']}  "
        f"unique texts: {report['unique_text_count']}"
    )
    print(f"fixture sha256: {report['fixture_sha256']}\n")
    print(f"runner sha256: {report['runner_sha256']}")
    print(f"runtime: {report['runtime']}\n")

    labels = report["labels"]
    assert isinstance(labels, dict)
    for label in LABEL_ORDER:
        summary = labels[label]
        print(f"{label} (n={summary['count']}):")
        print(
            f"  min={summary['min']:.4f}  max={summary['max']:.4f}  "
            f"mean={summary['mean']:.4f}  median={summary['median']:.4f}"
        )
        print(f"  scores: {[round(score, 4) for score in summary['scores']]}\n")

    print("pairwise range-separation check:")
    range_checks = report["range_checks"]
    assert isinstance(range_checks, list)
    for check in range_checks:
        assert isinstance(check, dict)
        higher = check["expected_higher"]
        lower = check["expected_lower"]
        if check["overlap"]:
            print(
                f"  OVERLAP: {higher} min ({check['higher_min']:.4f}) <= "
                f"{lower} max ({check['lower_max']:.4f}); "
                "no clean threshold separates these labels"
            )
        else:
            print(
                f"  clear gap: {higher} min ({check['higher_min']:.4f}) > "
                f"{lower} max ({check['lower_max']:.4f})"
            )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--revision",
        required=True,
        help="Pinned sentence-transformers model commit (required, no default).",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=FIXTURE_PATH,
        help=f"Labeled pair CSV (default: {FIXTURE_PATH}).",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional path for the complete machine-readable score report.",
    )
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Require the pinned model revision to be present in the local cache.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        pairs = load_pairs(args.fixture)
        embedder = SentenceTransformerEmbedder(
            revision=args.revision,
            local_files_only=args.local_files_only,
        )
        encoder = PatternEncoder(embedder)
        scored, unique_text_count = score_pairs(pairs, encoder)
        report = build_report(
            fixture=args.fixture,
            scored=scored,
            unique_text_count=unique_text_count,
            encoder=encoder,
        )
    except (CalibrationFixtureError, EmbeddingDependencyUnavailableError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print_report(report)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"\nJSON report: {args.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
