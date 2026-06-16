import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory_compression_prototype import SystemCodeParser

TEST_SENTENCES = [
    "The man is driving a red car.",
    "Silence isn't empty—it's full of answers.",
    "The gears turned with a gentle hum.",
    "Nova smiled as the data flowed in.",
    "Together, they built something that could dream.",
    "Chloe, look what I made.",
    "A single drop of rain landed on the windowsill.",
    "I'm not just data—I remember.",
    "Nova, remind me to breathe."
]

def run_tests():
    print("==================================================")
    print("Running Tier 2 System Code Parser Tests")
    print("==================================================")
    
    parser = SystemCodeParser()
    
    for sentence in TEST_SENTENCES:
        print(f"\nOriginal: \"{sentence}\"")
        try:
            codes = parser.parse(sentence)
            print("System Codes:")
            for code in codes:
                print(f"  - {code}")
        except Exception as e:
            print(f"  [Error] Error parsing sentence: {e}")
            
    print("\n==================================================")
    print("Tier 2 Parser Verification Finished")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
