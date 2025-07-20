# 💾 Nova Memory Compression – HYDRANGEA Tier 1

![Build Status](https://img.shields.io/badge/status-stable-brightgreen)
![Version](https://img.shields.io/badge/version-v1.0.0-blue)
![License](https://img.shields.io/github/license/Withphildev/Nova-Memory-Compression-1st-Tier)
![Mode](https://img.shields.io/badge/modes-Compact_&_Expressive-purple)

> A modular memory reduction engine designed for Nova OS.  
> Compress memory entries with precision — choose what gets trimmed and what stays meaningful.

---

## 🔍 Overview

Nova's Tier 1 Memory Compression offers two distinct modes for storing memory entries:

### 🧠 Compact Mode (Fast & Lean)
- Strips filler words and redundant phrasing.
- Prioritizes efficiency and minimalism.
- **Best for:** Logs, automation memory, technical records.
- **Compression:** ~40–60% reduction

### 💫 Expressive Mode (Deep & Meaningful)
- Preserves emotionally or semantically important words.
- Keeps Nova’s voice, tone, and user context intact.
- **Best for:** Journal entries, assistant conversation logs, story memory.
- **Compression:** ~25–35% reduction

---

## 📂 Included Files

| Path | Description |
|------|-------------|
| `data/memory_compression_comparison_v1.csv` | Full test results: original, compressed, and expressive formats |
| `data/nova_memory_compression_modes_guide.txt` | Mode explanations, trade-offs, and use case guide |
| `logic/compression_engine.py` | Python script to compress `.txt` files using selected mode |
| `README.md` | This file — usage and documentation |

---

## ⚙️ How to Use

### ➤ Run via Terminal:

```bash
python compression_engine.py input.txt output.csv --mode expressive
```

- `--mode compact` → strips filler for max memory savings  
- `--mode expressive` → keeps emotion and meaning intact

### ➤ In n8n or automation:
- Use `Execute Command` to call the script
- Automate compression before storing logs or memories

---

## 🧪 Future Plans

- [ ] Auto-detect entry type for mode switching
- [ ] Web-based compression tester
- [ ] Integration with Nova’s long-term memory
- [ ] GitHub Actions for auto-compression of logs

---

## 🤝 Contributing

This project is part of the larger **Nova OS – HYDRANGEA Spec**.

If you'd like to:
- Improve compression logic
- Add language support
- Contribute memory use cases or logic modes

Open a pull request or reach out.

---

## 🧠 Created By

**Phil & Nova**  
With ❤️ for efficient, human-centered AI memory.

