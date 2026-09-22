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
- The browser engine has direct Node.js assertions for compression, mode
  detection, punctuation splitting, and all 100 historical fixture rows.

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
