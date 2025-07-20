"""
compression_engine.py

Nova Memory Compression Engine – Tier 1
Supports Compact and Expressive memory modes.

Author: Phil & Nova
Version: 1.0
"""

import csv

FILLER_WORDS = {
    "the", "a", "an", "of", "on", "in", "with", "to", "as", "that", "this",
    "it", "is", "was", "and", "but", "or", "just", "for", "from", "by"
}

EMOTIONALLY_SIGNIFICANT = {
    "over", "single", "as", "in", "with", "hum", "isn't", "it's", "remember",
    "echo", "again", "smiled", "dream", "please", "wait", "chime", "nostalgia"
}

def compress(text, mode="compact"):
    words = text.strip().replace("—", " ").replace("–", " ").replace(".", "").replace(",", "").split()
    words_lower = [w.lower() for w in words]

    if mode == "compact":
        return " ".join([w for w in words_lower if w not in FILLER_WORDS])
    elif mode == "expressive":
        return " ".join([
            w for w in words if w.lower() in EMOTIONALLY_SIGNIFICANT or w.lower() not in FILLER_WORDS
        ])
    else:
        raise ValueError("Mode must be 'compact' or 'expressive'")

def process_file(input_path, output_path, mode="compact"):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    output_data = [("Original", "Compressed")]
    for line in lines:
        compressed = compress(line, mode)
        output_data.append((line, compressed))

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(output_data)

    print(f"[✓] Compressed file saved to: {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Nova Memory Compression Engine")
    parser.add_argument("input", help="Path to input .txt file")
    parser.add_argument("output", help="Path to save compressed .csv file")
    parser.add_argument("--mode", choices=["compact", "expressive"], default="compact", help="Compression mode")
    args = parser.parse_args()

    process_file(args.input, args.output, args.mode)
