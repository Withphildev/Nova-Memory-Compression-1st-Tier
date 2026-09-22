# Nova Memory Compression — HYDRANGEA Tier 1

[![Tests](https://github.com/Withphildev/Nova-Memory-Compression-1st-Tier/actions/workflows/test.yml/badge.svg)](https://github.com/Withphildev/Nova-Memory-Compression-1st-Tier/actions/workflows/test.yml)
![Version](https://img.shields.io/badge/version-v2.1.0-blue)
![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)

A reference implementation of the first semantic-distillation layer from the
HYDRANGEA memory design.

> **Design contract:** Tier 1 is intentionally lossy. It demonstrates how a
> natural-language memory can be reduced to a compact gist, such as
> `The man is driving a red car.` → `man driving red car`. The gist alone cannot
> reconstruct the exact original sentence.

## Where Tier 1 fits

The larger design separates four responsibilities:

1. **Gist layer (this repository):** remove low-information grammar while
   retaining content words and selected emotional anchors.
2. **System-code layer (experimental prototype):** express subject, action,
   object, and attributes in a machine-oriented form.
3. **Pattern layer (future work):** consolidate repeated instances into linked
   concept nodes.
4. **Bloom layer (future work):** expand a gist using retained source fragments,
   pattern evidence, and context. Reverse Blooming later re-weights or reframes
   older nodes when new insight arrives.

Blooming is therefore evidence-backed expansion, not decompression by guessing.
See [the architecture](docs/architecture.md) for the trust boundary.

## Tier 1 modes

- **Compact:** removes the complete filler-word set and lowercases retained
  words. Useful for technical memories and rough token-saving experiments.
- **Expressive:** retains configured emotional anchors and original casing.
  Useful for narrative or relational memories.
- **Auto:** selects Compact for valid JSON and explicit log/error vocabulary;
  otherwise selects Expressive.

The browser sandbox reports **character savings**, not tokenizer-specific token
savings. Actual token counts vary by model and tokenizer.

## Repository layout

| Path | Purpose |
| --- | --- |
| `logic/compression_engine.py` | Tier 1 engine, metadata envelope, and CLI |
| `src/memory_compression_prototype.py` | Experimental spaCy Tier 2 parser |
| `tester/` | Browser-based Tier 1 sandbox |
| `tests/` | Assertive Python unit and regression tests |
| `data/memory_compression_comparison_v1.csv` | Historical 100-row benchmark |
| `docs/architecture.md` | Layer boundaries and Bloom requirements |

The historical CSV predates the finalized Master Memories design. Its
`Restored Compression` column is the old name for **Expressive output**; it is
retained unchanged as a regression artifact and is not proof of reversibility.

## Quick start

Requires Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Compress a text file to a CSV report:

```bash
nova-memory-compress input.txt output.csv --mode expressive
```

Create a Bloom-ready JSON Lines envelope that retains each original fragment:

```bash
nova-memory-compress input.txt output.jsonl --mode auto --format jsonl
```

Each envelope explicitly records `reversible_from_gist: false`, the resolved
mode, the retained original, compressed gist, and reduction metrics.

### Browser sandbox

```bash
python -m http.server 8001 --directory tester
```

Open <http://localhost:8001>.

### Experimental Tier 2 parser

Tier 2 is optional and requires spaCy plus its English model:

```bash
python -m pip install -e '.[tier2]'
python -m spacy download en_core_web_sm
python src/memory_compression_prototype.py "The man is driving a red car."
```

## Tests

```bash
python -m unittest discover -s tests -v
npm test
python src/test_engine.py
```

GitHub Actions runs these checks on every push and pull request. Tier 2's parser
logic is tested with an injected dependency tree, so the normal CI path does not
need to download a language model.

## Safety and scope

- Do not replace source memories with a Tier 1 gist unless exact wording is
  intentionally disposable.
- Do not present generated detail as recalled fact during Bloom.
- Preserve source references and provenance when Tier 1 is integrated into a
  production memory stack.
- Recompression and Reverse Bloom operations should be auditable and retain
  prior node versions.

## License

Creative Commons Attribution-NonCommercial 4.0 International. See
[`LICENSE.txt`](LICENSE.txt).

Created by **Phil & Nova**.
