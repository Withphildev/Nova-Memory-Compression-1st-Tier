import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.compression_engine import detect_mode

TEST_CASES = [
    ("Silence isn't empty—it's full of answers.", "expressive"),
    ("Together, they built something that could dream.", "expressive"),
    ("{\"status\": \"active\", \"user\": \"Phil\", \"tags\": [\"specs\"]}", "compact"),
    ("[{\"action\": \"create\", \"id\": 102}]", "compact"),
    ("2026-06-16 11:15:28 ERROR - Database connection timeout", "compact"),
    ("Traceback (most recent call last):\n  File \"app.js\", line 140", "compact"),
    ("Warning: Punctuation leak detected in CSV parser.", "compact"),
    ("Nova smiled as the data flowed in.", "expressive")
]

def run_tests():
    print("==================================================")
    print("Running Auto-Detection Mode Classifier Tests")
    print("==================================================")
    
    passed = 0
    for text, expected in TEST_CASES:
        detected = detect_mode(text)
        preview = text.replace("\n", " ")[:40] + ("..." if len(text) > 40 else "")
        if detected == expected:
            print(f"  [OK] \"{preview}\" -> Detected: {detected}")
            passed += 1
        else:
            print(f"  [FAIL] \"{preview}\" -> Detected: {detected} | Expected: {expected}")
            
    print("==================================================")
    print(f"Passed: {passed}/{len(TEST_CASES)}")
    print("==================================================")
    
    if passed == len(TEST_CASES):
        print("All auto-detection tests passed successfully!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
