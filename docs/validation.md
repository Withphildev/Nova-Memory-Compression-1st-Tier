# Validation status

## Current automated checks

- The 100-row historical CSV remains behavior-compatible with the Python
  Compact and Expressive outputs.
- Auto detection recognizes valid JSON and explicit log vocabulary without
  treating ordinary words such as `information` as logs.
- Metadata envelopes retain their source fragment and declare that a gist is
  not independently reversible.
- Tier 1 decision traces and anchors flow into a combined Tier 2 envelope while
  dependency parsing still uses the retained original.
- CSV and JSONL exports are exercised in temporary directories.
- Tier 2 tag extraction is tested without requiring a downloaded spaCy model.
- A separate CI integration job installs the real spaCy English model and
  verifies active/passive equivalence, agentless passives, local relative
  clauses, coordination, and negation.
- The browser engine has direct Node.js assertions for compression, mode
  detection, punctuation splitting, and all 100 historical fixture rows.
- Tier 3 schema invariants, serialization, original-text embedding, model
  provenance, and injected-provider failures are covered without downloading a
  model.
- The 63-pair Tier 3 calibration fixture is structurally validated, every
  unique text is embedded once through `PatternEncoder`, and range-overlap math
  is regression-tested.

## Tier 3 calibration v1

A real local run used `sentence-transformers/all-MiniLM-L6-v2` pinned to
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. The complete report records the
fixture and runner SHA-256 values, package versions, all pair scores, summary
statistics, and pairwise range checks in
`tier3_calibration_results_v1.json`.

Five of the six pairwise label-range checks overlap. This is a valid negative
calibration result: MiniLM similarity cannot safely choose a merge threshold or
detect contradiction for this fixture. No policy thresholds were set.

## Historical results

`test-results-summary.txt` records experiments performed before the current
Master Memories design was consolidated. Those figures are preserved as design
history, not reproduced benchmark claims. They do not identify a tokenizer,
dataset fixture, hardware profile, or executable test harness and therefore
must not be presented as current CI evidence.

## Required for production claims

- fixed, publishable benchmark corpora;
- named tokenizers and model versions;
- semantic-retention scoring with human review;
- Bloom provenance and hallucination tests;
- privacy, deletion, and source-retention tests;
- performance and failure-mode measurements.
- broader Tier 3 themes and more adversarial qualifier/negation cases;
- separately evaluated contradiction detection before automatic links.
