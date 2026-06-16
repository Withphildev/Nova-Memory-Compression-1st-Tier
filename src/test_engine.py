import csv
import sys
import os

# Ensure the parent directory is in the path so we can import logic.compression_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.compression_engine import compress

def run_tests():
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "memory_compression_comparison_v1.csv")
    
    mismatches = []
    total_rows = 0
    fixed_rows = 0
    
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        
        for idx, row in enumerate(reader, start=2): # 1-indexed header is line 1
            if not row:
                continue
            total_rows += 1
            original, csv_compact, csv_expressive = row[0], row[1], row[2]
            
            new_compact = compress(original, "compact")
            new_expressive = compress(original, "expressive")
            
            compact_match = new_compact == csv_compact
            expressive_match = new_expressive == csv_expressive
            
            if not compact_match or not expressive_match:
                mismatches.append({
                    "line": idx,
                    "original": original,
                    "csv_compact": csv_compact,
                    "new_compact": new_compact,
                    "csv_expressive": csv_expressive,
                    "new_expressive": new_expressive,
                    "compact_match": compact_match,
                    "expressive_match": expressive_match
                })
                
                # Check if this mismatch represents a known punctuation leak fix
                # (e.g., the CSV contains quotes/punctuation on a filler word like 'is', 'the', etc., but the new code correctly stripped it)
                if ("“is" in csv_compact and "“is" not in new_compact) or ("“a" in csv_compact and "“a" not in new_compact):
                    fixed_rows += 1
                elif ("“" in original or "?" in original or "!" in original):
                    fixed_rows += 1
                    
    print(f"Total Rows Tested: {total_rows}")
    print(f"Mismatches (potential bug fixes or deviations): {len(mismatches)}")
    print(f"Likely Punctuation Leak Fixes: {fixed_rows}\n")
    
    if mismatches:
        print("--- Details of Mismatches ---")
        for m in mismatches[:15]: # Print first 15 for review
            print(f"Line {m['line']}: \"{m['original']}\"")
            if not m['compact_match']:
                print(f"  [Compact] CSV: \"{m['csv_compact']}\" | NEW: \"{m['new_compact']}\"")
            if not m['expressive_match']:
                print(f"  [Expressive] CSV: \"{m['csv_expressive']}\" | NEW: \"{m['new_expressive']}\"")
            print()
            
if __name__ == "__main__":
    run_tests()
