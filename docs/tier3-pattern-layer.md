# Tier 3 pattern-layer foundation

## Status

Release 2.4.0 implements the Tier 3 persistence schema and an injectable local
embedding boundary. It does **not** cluster memories, assign similarity bands,
merge instances, or detect contradictions.

This staging is intentional: the historical 100-row Tier 1 fixture was built
to validate lexical compression, not semantic similarity. It must be expanded
with labeled same-pattern, ambiguous, contradictory, and unrelated pairs
before similarity thresholds can be trusted.

## Approved decisions

- Default local model: `sentence-transformers/all-MiniLM-L6-v2`.
- Embeddings use retained original text. Tier 2 system codes are secondary
  evidence and are never substituted for the original sentence.
- A candidate is eligible for promotion after three linked source instances.
- Ambiguous relationships and confirmed contradictions are stored separately.
- Every policy records its embedding model, pinned revision, metric, promotion
  threshold, and any future calibrated similarity thresholds.
- Source links and interpretation history are append-only design invariants.

## Schemas

`PatternMemory` is the durable Tier 1/Tier 2 handoff. It records the source ID,
observation time, retained original text, anchors, system codes, and upstream
schema versions.

`PatternNode` represents either a candidate or a promoted pattern. It records:

- a durable pattern and policy ID;
- every linked source instance and a real representative source;
- recurrence, first/last observation, anchor counts, and cohesion;
- separate ambiguity and contradiction links;
- append-only history events;
- embedding model, revision, dimensions, and centroid;
- the promotion threshold snapshot used for the decision.

The node schema does not delete or rewrite source memories. Serialized objects
round-trip through `to_dict()` and `from_dict()` while preserving invariants.

## Injectable embedder

`PatternEncoder` depends on the small `Embedder` protocol, so calibration can
use deterministic fakes and production can use a local model without changing
the schema. `SentenceTransformerEmbedder` is the optional CPU-local MiniLM
adapter. It requires an explicit model revision and records that revision on
every embedded memory.

Install the optional runtime when real local embeddings are needed:

```bash
python -m pip install -e '.[tier3]'
```

The current automated tests inject an embedder and do not download a model.
No remote embedding API is used.

## Deliberate caveats

### Contradiction detection is schema-only

The schema can retain human-confirmed or future-detector contradiction links,
but this release contains no contradiction classifier. Similarity alone must
not be interpreted as contradiction.

### Calibration requires a larger fixture

`merge_threshold` and `ambiguity_threshold` remain `None`, and auto-merge is
disabled. The next stage is to expand and label the calibration fixture, run
MiniLM against it, inspect errors, then approve versioned thresholds. Promotion
at three recurrence links does not bypass that similarity calibration.

## Not included in JavaScript

Tier 3 is a persistence and model-integration layer, not part of the static
Tier 1 browser sandbox. There is no duplicated JavaScript implementation to
drift from the Python schema.
