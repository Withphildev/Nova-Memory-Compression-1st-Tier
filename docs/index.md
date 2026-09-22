---
title: Nova Memory Compression
---

# 💾 Nova Memory Compression – HYDRANGEA Tier 1

Welcome to the documentation for **Nova Memory Compression**, a reference
implementation of HYDRANGEA's intentionally lossy Tier 1 gist layer.

> Part of **Nova OS (in development)** – designed to help AI preserve meaning, structure, and emotion under token limits.

---

## 🔍 Overview

Nova Memory Compression supports two optimized memory modes:

- 🧠 **Compact Mode:** Fast & lean — removes filler for automation or logs  
- 💫 **Expressive Mode:** Preserves tone and nuance — perfect for journaling or assistant memory

---

## 🚀 Quick Start

To run the compression engine:

```bash
python -m pip install -e .
nova-memory-compress input.txt output.csv --mode expressive
```

- Replace `expressive` with `compact` for minimal memory
- Input should be a `.txt` file with one memory line per row

---

## 📁 Key Files

- [`compression_engine.py`](../logic/compression_engine.py) – Dual-mode compressor
- [`README.md`](../README.md) – Full usage guide
- [`memory_compression_comparison_v1.csv`](../data/memory_compression_comparison_v1.csv) – Test results
- [`nova_memory_compression_modes_guide.txt`](../data/nova_memory_compression_modes_guide.txt) – Mode explanation
- [`architecture.md`](architecture.md) – Tier boundaries and Bloom trust contract
- [`validation.md`](validation.md) – Reproducible versus historical validation

Tier 1 does not reverse or recreate exact prose. Blooming requires retained
source fragments or linked evidence from later memory layers.

---

## 🤝 Want to Help?

Open an issue or pull request — contributions are welcome!

- Improve the compression engine
- Add new language models
- Build integrations with n8n, Notion, or custom APIs

---

Created by **Phil & Nova** – with care for thoughtful, scalable memory in AI.
