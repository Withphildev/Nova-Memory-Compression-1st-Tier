# Tier 3 pattern-layer foundation

## Status

Release 2.6.0 implements the Tier 3 persistence schema and an injectable local
embedding boundary. It does **not** cluster memories, assign similarity bands,
merge instances, or detect contradictions.

This staging is intentional: the historical 100-row Tier 1 fixture was built
to validate lexical compression, not semantic similarity. A separate labeled
Tier 3 fixture now measures same-pattern, ambiguous, contradictory, and
unrelated pairs without silently turning those measurements into policy.

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

### Calibration requires labeled evidence

`merge_threshold` and `ambiguity_threshold` remain `None`, and auto-merge is
disabled. Promotion at three recurrence links does not bypass similarity
calibration.

## Calibration v1 result

The v1 fixture contains 63 pairs across six four-phrase thematic clusters:

- 36 same-pattern combinations;
- 6 deliberately ambiguous near matches;
- 6 explicit contradictions;
- all 15 cross-cluster unrelated combinations.

`src/calibrate_tier3.py` embeds each of the 36 unique texts exactly once through
`PatternEncoder`, calculates cosine similarity, reports per-label statistics,
and checks every pair of label ranges. It requires an explicit pinned model
revision and can emit a provenance-stamped JSON report.

The real run used MiniLM revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41` and produced:

| Label | Count | Minimum | Maximum | Mean | Median |
| --- | ---: | ---: | ---: | ---: | ---: |
| Same pattern | 36 | 0.4754 | 0.9488 | 0.7873 | 0.8094 |
| Ambiguous | 6 | 0.8710 | 0.9845 | 0.9296 | 0.9232 |
| Contradiction | 6 | 0.5790 | 0.9552 | 0.8265 | 0.8647 |
| Unrelated | 15 | 0.1996 | 0.6281 | 0.4428 | 0.4876 |

These ranges overlap. In particular, contradictions can score above true
same-pattern paraphrases, subtle qualifiers produce extremely high ambiguous
scores, and the lowest same-pattern score falls below the highest unrelated
score. Therefore no single cosine threshold can safely implement the approved
four-way policy on this fixture.

Decision: retain MiniLM for candidate retrieval, keep auto-merge disabled, and
do not infer contradiction from embedding similarity. The complete pair-level
scores and reproducibility metadata are in
`docs/tier3_calibration_results_v1.json`.

## Calibration v2 comparison

V2 preserves all 63 labels, the six clusters, the same-pattern paraphrases,
and the unrelated pairs. It replaces only the ambiguous and contradiction
sentences with independently worded claims rather than minimal edits. V1 is
retained as evidence of the surface-overlap failure mode.

The same pinned model and runtime produced:

| Label | V1 range | V1 mean | V2 range | V2 mean |
| --- | ---: | ---: | ---: | ---: |
| Same pattern | 0.4754–0.9488 | 0.7873 | 0.4754–0.9488 | 0.7873 |
| Ambiguous | 0.8710–0.9845 | 0.9296 | 0.6739–0.8790 | 0.7838 |
| Contradiction | 0.5790–0.9552 | 0.8265 | 0.6571–0.8417 | 0.7334 |
| Unrelated | 0.1996–0.6281 | 0.4428 | 0.1996–0.6281 | 0.4428 |

The independently worded fixture meaningfully reduces the inflated similarity
of ambiguous and contradictory pairs. V2 has four overlapping range checks,
down from five in v1, and contradiction now clears unrelated by a narrow
`0.0290` margin (`0.6571 > 0.6281`). This confirms that part of v1's negative
result was caused by surface-form leakage.

The core finding survives: same-pattern still overlaps contradiction, ambiguous,
and unrelated ranges. A global cosine threshold would reject valid paraphrases
or accept incorrect relationships. MiniLM remains a candidate generator, while
semantic role, negation, qualifier, and human-review stages must make durable
merge and contradiction decisions. The full v2 report is in
`docs/tier3_calibration_results_v2.json`.

## Not included in JavaScript

Tier 3 is a persistence and model-integration layer, not part of the static
Tier 1 browser sandbox. There is no duplicated JavaScript implementation to
drift from the Python schema.
