"""Nova Memory Compression Engine – HYDRANGEA Tier 1.

Tier 1 is intentionally lossy: it demonstrates semantic distillation and
token/character reduction, not exact reconstruction.  A later Bloom layer can
expand a gist only when the original fragment or linked pattern evidence has
been retained elsewhere.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

CompressionMode = Literal["compact", "expressive", "auto"]
ResolvedMode = Literal["compact", "expressive"]

FILLER_WORDS = {
    "the", "a", "an", "of", "on", "in", "with", "to", "as", "that", "this",
    "it", "is", "was", "and", "but", "or", "just", "for", "from", "by"
}

EMOTIONALLY_SIGNIFICANT = {
    "over", "single", "as", "in", "with", "hum", "isn't", "it's", "remember",
    "echo", "again", "smiled", "dream", "please", "wait", "chime", "nostalgia"
}

PUNCTUATION_TO_STRIP = "“‘”’\"'?.!,;:()[]{}*&%-–—"
LOG_PATTERNS = (
    re.compile(r"\b(?:error|warning|info|debug|traceback|exception|failed|stderr|stdout|null)\b", re.IGNORECASE),
    re.compile(r"\bstack\s+trace\b", re.IGNORECASE),
    re.compile(r"\bexit\s+code\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class CompressionResult:
    """Bloom-ready Tier 1 result.

    ``original`` is deliberately retained in this demonstration envelope.
    Production systems may replace it with a durable source reference, but
    must not claim exact reversal from ``compressed`` alone.
    """

    schema_version: str
    requested_mode: CompressionMode
    resolved_mode: ResolvedMode
    original: str
    compressed: str
    original_characters: int
    compressed_characters: int
    original_words: int
    compressed_words: int
    character_savings_percent: float
    reversible_from_gist: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def split_punctuation(word: str, punctuation_to_strip: str = PUNCTUATION_TO_STRIP) -> tuple[str, str, str]:
    leading = ""
    trailing = ""
    
    start_idx = 0
    while start_idx < len(word) and word[start_idx] in punctuation_to_strip:
        leading += word[start_idx]
        start_idx += 1
        
    end_idx = len(word)
    while end_idx > start_idx and word[end_idx - 1] in punctuation_to_strip:
        end_idx -= 1
    trailing = word[end_idx:]
    
    cleaned_word = word[start_idx:end_idx]
    return leading, cleaned_word, trailing

def detect_mode(text: str) -> ResolvedMode:
    text_stripped = text.strip()
    if not text_stripped:
        return "compact"
        
    # Rule 1: JSON detection
    if (text_stripped.startswith("{") and text_stripped.endswith("}")) or \
       (text_stripped.startswith("[") and text_stripped.endswith("]")):
        try:
            json.loads(text_stripped)
            return "compact"
        except ValueError:
            pass
            
    # Rule 2: Log flags or tracebacks. Word boundaries prevent false matches
    # such as "information" being classified as a log because it contains
    # "info".
    for pattern in LOG_PATTERNS:
        if pattern.search(text_stripped):
            return "compact"
            
    return "expressive"

def _validate_mode(mode: str) -> CompressionMode:
    if mode not in {"compact", "expressive", "auto"}:
        raise ValueError("Mode must be 'compact', 'expressive', or 'auto'")
    return mode  # type: ignore[return-value]


def compress(text: str, mode: CompressionMode = "compact") -> str:
    mode = _validate_mode(mode)
    if mode == "auto":
        mode = detect_mode(text)
        
    words = text.strip().replace("—", " ").replace("–", " ").replace(".", "").replace(",", "").split()
    
    compressed_words = []
    
    pending_leading = ""
    pending_trailing = ""
    
    for w in words:
        leading, cleaned, trailing = split_punctuation(w)
        cleaned_lower = cleaned.lower()
        
        is_filler = cleaned_lower in FILLER_WORDS
        is_emotional = cleaned_lower in EMOTIONALLY_SIGNIFICANT
        
        keep = False
        if mode == "compact":
            keep = not is_filler
        elif mode == "expressive":
            keep = is_emotional or not is_filler
        if keep:
            word_to_use = cleaned_lower if mode == "compact" else cleaned
            full_word = pending_leading + leading + word_to_use + trailing
            compressed_words.append(full_word)
            pending_leading = ""
        else:
            if leading:
                pending_leading += leading
            if trailing:
                pending_trailing += trailing
                
    if pending_trailing and compressed_words:
        compressed_words[-1] = compressed_words[-1] + pending_trailing
        
    return " ".join(compressed_words)


def compress_with_metadata(text: str, mode: CompressionMode = "auto") -> CompressionResult:
    requested_mode = _validate_mode(mode)
    resolved_mode: ResolvedMode = detect_mode(text) if requested_mode == "auto" else requested_mode
    compressed = compress(text, resolved_mode)
    original_words = len(text.split())
    compressed_words = len(compressed.split())
    original_characters = len(text)
    compressed_characters = len(compressed)
    savings = 0.0
    if original_characters:
        savings = round((1 - compressed_characters / original_characters) * 100, 2)

    return CompressionResult(
        schema_version="hydrangea.tier1.v1",
        requested_mode=requested_mode,
        resolved_mode=resolved_mode,
        original=text,
        compressed=compressed,
        original_characters=original_characters,
        compressed_characters=compressed_characters,
        original_words=original_words,
        compressed_words=compressed_words,
        character_savings_percent=savings,
    )


def process_file(
    input_path: str | Path,
    output_path: str | Path,
    mode: CompressionMode = "auto",
    output_format: Literal["csv", "jsonl"] = "csv",
) -> None:
    input_path = Path(input_path)
    output_path = Path(output_path)
    with input_path.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    results = [compress_with_metadata(line, mode) for line in lines]
    if output_format == "csv":
        with output_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(
                (
                    "Original",
                    "Resolved Mode",
                    "Compressed",
                    "Original Words",
                    "Compressed Words",
                    "Character Savings Percent",
                )
            )
            for result in results:
                writer.writerow(
                    (
                        result.original,
                        result.resolved_mode,
                        result.compressed,
                        result.original_words,
                        result.compressed_words,
                        result.character_savings_percent,
                    )
                )
    elif output_format == "jsonl":
        with output_path.open("w", encoding="utf-8") as f:
            for result in results:
                f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
    else:
        raise ValueError("Output format must be 'csv' or 'jsonl'")

    print(f"[✓] Compressed file saved to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Nova Memory Compression Engine")
    parser.add_argument("input", help="Path to input .txt file")
    parser.add_argument("output", help="Path to save compressed output")
    parser.add_argument("--mode", choices=["compact", "expressive", "auto"], default="auto", help="Compression mode")
    parser.add_argument("--format", choices=["csv", "jsonl"], default="csv", dest="output_format", help="Output envelope format")
    args = parser.parse_args()

    process_file(args.input, args.output, args.mode, args.output_format)


if __name__ == "__main__":
    main()
