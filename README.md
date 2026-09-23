# Nova Memory Compression — HYDRANGEA Tier 1

[![Tests](https://github.com/Withphildev/Nova-Memory-Compression-1st-Tier/actions/workflows/test.yml/badge.svg)](https://github.com/Withphildev/Nova-Memory-Compression-1st-Tier/actions/workflows/test.yml)
![Version](https://img.shields.io/badge/version-v2.4.0-blue)
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
3. **Pattern layer (foundation implemented):** persist linked candidates,
   versioned policy, and auditable local embeddings. Clustering and calibrated
   merging remain future work.
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
| `src/pattern_layer.py` | Tier 3 schemas and injectable local embedder |
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

Each `hydrangea.tier1.v2` envelope explicitly records
`reversible_from_gist: false`, the resolved mode, retained original, compressed
gist, per-word decisions, deduplicated emotional anchors, and reduction metrics.

Optional tokenizer-specific metrics are available without replacing the
deterministic character and word measurements:

```bash
python -m pip install -e '.[tokens]'
nova-memory-compress input.txt output.jsonl --format jsonl --tokenizer cl100k_base
```

The first use of a tiktoken encoding may require network access so tiktoken can
cache its encoding table locally.

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

Tier 2 can also consume the richer Tier 1 result while parsing the retained
original—not the grammatically incomplete gist:

```python
from logic import compress_with_metadata
from src import SystemCodeParser

tier1 = compress_with_metadata("Nova will remember the echo.", "expressive")
tier2 = SystemCodeParser().parse_result(tier1)
print(tier2.to_dict())
```

The combined `hydrangea.tier2.v1` envelope carries Tier 1 provenance forward
and records exact matches between system-code terms and Tier 1 anchors. It does
not infer that an ordinary subject, object, or attribute is emotionally salient.

Tier 2 normalizes passive voice into semantic agent/action/patient roles. For
example, both `The man drove the car` and `The car was driven by the man`
produce `[SUB:MAN][ACT:DRIVE][OBJ:CAR]`; an omitted agent is represented as
`SUB:UNKNOWN`. A bounded heuristic also resolves `who`, `that`, and `which`
inside a local relative clause to the noun modified by that clause. This is not
general coreference resolution and does not follow pronouns across clauses or
sentences.

### Tier 3 pattern foundation

Tier 3 now defines persistent pattern-memory, policy, relation, history, and
node schemas plus an injectable embedding interface. The optional local adapter
uses `sentence-transformers/all-MiniLM-L6-v2` with a caller-supplied pinned
revision:

```bash
python -m pip install -e '.[tier3]'
```

The approved promotion threshold is three linked instances, but similarity
thresholds remain unset and automatic merging is disabled until a larger
labeled fixture is calibrated. Contradiction links are schema-only in this
release; there is no contradiction detector yet. See
[the Tier 3 foundation](docs/tier3-pattern-layer.md).

## Tests

```bash
python -m unittest discover -s tests -v
npm test
python src/test_engine.py
```

GitHub Actions runs these checks on every push and pull request. The fast Tier 2
tests use injected dependency trees, while a separate integration job installs
spaCy's English model and verifies passive voice, relative clauses,
coordination, and negation against real dependency parses.

`src/test_auto.py` and `src/test_tier2.py` are optional, human-readable manual
diagnostics. Assertive CI coverage lives in `tests/`; the Tier 2 diagnostic also
requires the optional spaCy model.

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
