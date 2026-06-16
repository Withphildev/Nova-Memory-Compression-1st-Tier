import csv
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.compression_engine import compress

def regenerate():
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "memory_compression_comparison_v1.csv")
    temp_rows = []
    
    # Read the original sentences
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row:
                continue
            original = row[0]
            temp_rows.append(original)
            
    # Regenerate CSV contents with the new bug-fixed logic
    new_rows = [["Original", "Compressed", "Restored Compression"]]
    for original in temp_rows:
        new_compact = compress(original, "compact")
        new_expressive = compress(original, "expressive")
        new_rows.append([original, new_compact, new_expressive])
        
    # Overwrite the CSV file
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)
        
    print(f"[✓] Successfully regenerated CSV with bug-fixed outputs at: {csv_path}")

if __name__ == "__main__":
    regenerate()
