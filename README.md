# Nova Memory Compression – Tier 1 Engine

This module is part of the **HYDRANGEA** memory system for Nova, designed to optimize how memory entries are stored for efficiency and context sensitivity.

---

## 🔍 Overview

Nova's Tier 1 Memory Compression provides two selectable modes for storing past logs, thoughts, or events:

### 1. 🧠 Compact Mode (Fast & Lean)
- Strips filler words and compresses phrasing to the bare essentials
- Ideal for technical logs, system memory, or automation history
- ~40–60% size reduction

### 2. 💫 Expressive Mode (Deep & Meaningful)
- Preserves emotionally important or poetic terms
- Ideal for journaling, narrative logs, assistant training memory
- ~25–35% size reduction

---

## 📂 Files Included

| File | Description |
|------|-------------|
| `data/memory_compression_comparison_v1.csv` | Full side-by-side table showing original, compressed, and expressive versions of 100 memory lines |
| `data/nova_memory_compression_modes_guide.txt` | Plain-text guide explaining both memory modes, use cases, and trade-offs |

---

## 🛠️ How to Use

1. Load your memory entries into the compression engine.
2. Choose your desired mode:
   - `compact_mode=True` for fast/logical compression
   - `compact_mode=False` for expressive/narrative memory
3. Export and store compressed entries to memory storage or journal files.

---

## 🧪 Future Features (Planned)

- Automatic mode detection based on entry type
- Configurable rulesets per user profile
- GUI toggle for mode selection
- Memory visualizer

---

Created by **Phil & Nova**  
Part of the HYDRANGEA Spec – Nova OS Project
