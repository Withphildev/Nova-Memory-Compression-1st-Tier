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

def split_punctuation(word, punctuation_to_strip):
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

def detect_mode(text):
    import json
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
            
    # Rule 2: Log flags or tracebacks (case-insensitive)
    log_keywords = {
        "error", "warning", "info", "debug", "traceback", "exception",
        "stack trace", "exit code", "failed", "stderr", "stdout", "null"
    }
    text_lower = text_stripped.lower()
    for kw in log_keywords:
        if kw in text_lower:
            return "compact"
            
    return "expressive"

def compress(text, mode="compact"):
    if mode == "auto":
        mode = detect_mode(text)
        
    words = text.strip().replace("—", " ").replace("–", " ").replace(".", "").replace(",", "").split()
    
    punctuation_to_strip = "“‘”’\"'?.!,;:()[]{}*&%-–—"
    compressed_words = []
    
    pending_leading = ""
    pending_trailing = ""
    
    for w in words:
        leading, cleaned, trailing = split_punctuation(w, punctuation_to_strip)
        cleaned_lower = cleaned.lower()
        
        is_filler = cleaned_lower in FILLER_WORDS
        is_emotional = cleaned_lower in EMOTIONALLY_SIGNIFICANT
        
        keep = False
        if mode == "compact":
            keep = not is_filler
        elif mode == "expressive":
            keep = is_emotional or not is_filler
        else:
            raise ValueError("Mode must be 'compact', 'expressive', or 'auto'")
            
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

def process_file(input_path, output_path, mode="auto"):
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
    parser.add_argument("--mode", choices=["compact", "expressive", "auto"], default="auto", help="Compression mode")
    args = parser.parse_args()

    process_file(args.input, args.output, args.mode)
