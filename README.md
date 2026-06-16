# 💾 Nova Memory Compression — HYDRANGEA Specification

![Build Status](https://img.shields.io/badge/status-stable-brightgreen)
![Version](https://img.shields.io/badge/version-v2.0.0-blue)
![License](https://img.shields.io/github/license/Withphildev/Nova-Memory-Compression-1st-Tier)
![Modes](https://img.shields.io/badge/modes-Compact_&_Expressive-purple)
![Sandbox](https://img.shields.io/badge/sandbox-active-emerald)

> A modular memory compression suite built for Nova OS. Compresses natural language memories with precision, optimizing token efficiency and preserving semantic meaning.

---

## 🔍 Overview

This repository implements the first two layers of the **HYDRANGEA Memory Architecture**:

### 🧠 Tier 1: Lexical Stop-Word Filter (Dual Mode)
Strips redundant tokens through highly optimized lexical set checking, utilizing custom emotional whitelists.
* **Compact Mode (Fast & Lean):** Strips all common filler words for maximal token efficiency (~40–60% reduction). Best for logs and automation data.
* **Expressive Mode (Deep & Meaningful):** Preserves emotionally or semantically significant words (e.g. *chime, nostalgia, echo, smiled*), maintaining Nova's unique voice and context (~25–35% reduction). Best for conversation logs and journals.
* Includes a **Quote Migration** engine that dynamically balances punctuation so quotes (`“`, `”`, `?`) are never lost when bordering words are stripped.

### 🤖 Tier 2: Grammatical System Code Parser
Uses **spaCy's** English dependency grammar trees to extract semantic relationships from natural language, compiling them into a machine-native tag format:
`"The gears turned with a gentle hum."` $\rightarrow$ `[SUB:GEARS][ACT:TURN][OBJ:HUM][ATTR:GENTLE]`

---

## 📂 Included Files

| Path | Description |
|------|-------------|
| `logic/compression_engine.py` | Python core for Tier 1 Compact/Expressive compression |
| `src/memory_compression_prototype.py` | Python parser implementing the Tier 2 System Code triplet extractor |
| `src/test_tier2.py` | Validation tests running Tier 2 parser against benchmark sentences |
| `tester/` | Web Sandbox interface (HTML/CSS/JS) with real-time stats and visual Transcipher tokenization |
| `data/memory_compression_comparison_v1.csv` | Regenerated test comparisons containing original, compressed, and restored rows |

---

## ⚙️ How to Run

### 1. Launch the Web Sandbox
Open the sandbox interface to interactively test the engine:
```bash
python -m http.server 8001 --directory tester
```
Once started, navigate to **http://localhost:8001** in your browser.

### 2. Run Tier 1 Compression via CLI
Compress a text file of memory logs:
```bash
python logic/compression_engine.py input.txt output.csv --mode expressive
```

### 3. Run Tier 2 Triplet Parser via CLI
Compile a sentence into structured System Code:
```bash
python src/memory_compression_prototype.py "Silence isn't empty — it's full of answers."
```

---

## 🧪 Future Plans

- [x] Web-based compression tester sandbox
- [ ] Auto-detect entry type for mode switching
- [ ] Integration with Nova’s long-term memory stack
- [ ] GitHub Actions for auto-compression of logs

---

## 🤝 Contributing

This project is part of the larger **Nova OS – HYDRANGEA Spec**. Open a pull request or issue to improve parsing rules, add language support, or expand the whitelists.

Created with ❤️ by **Phil & Nova** for efficient, human-centered AI memory.
