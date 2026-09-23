# Future roadmap

## Completed in the reference implementation

- Compact, Expressive, and Auto Tier 1 modes.
- Browser sandbox with deterministic character-savings metrics.
- Bloom-ready JSONL metadata envelope.
- Tier 1 decision traces, emotional anchors, and Tier 2 handoff envelope.
- Optional named-tokenizer measurements.
- Passive-role normalization and bounded local relative-pronoun resolution.
- Real-model spaCy integration tests in CI.
- Historical 100-row regression suite.
- Assertive Python and JavaScript tests.
- Optional, dependency-injected Tier 2 parser.
- GitHub Actions validation.
- Tier 3 durable schemas with separate ambiguity and contradiction links.
- Injectable local embedding boundary with pinned model provenance.
- A 63-pair Tier 3 fixture and real pinned-MiniLM calibration report.
- An independently worded v2 fixture that separates contradiction from
  unrelated examples while confirming that merge labels still overlap.

## Next: stabilize Tier 1

- Publish a versioned filler-word and emotional-anchor policy.
- Add Unicode and multilingual fixtures.
- Add property tests for punctuation and whitespace invariants.
- Benchmark across multiple explicitly named tokenizers instead of
  extrapolating from character counts.

## Next: strengthen pattern decisions

- Expand beyond six themes and six ambiguous/contradiction cases per version.
- Evaluate a two-stage decision design: embedding candidate retrieval followed
  by explicit semantic and human review gates.
- Add negation, qualifier, entity, time, and quantity checks rather than asking
  cosine similarity to identify contradictions.
- Keep auto-merge disabled; v1 proves a single global threshold is unsafe.
- Treat contradiction links as schema-only until a separate detector is
  designed and evaluated.

## Later: Bloom and Reverse Bloom prototypes

- Evidence-backed gist expansion.
- Pattern consolidation with reversible links to instances.
- Query-selectable recall modes: blurred, gist, and full detail.
- Reverse Bloom annotations that preserve prior weights and interpretations.
- Human-readable Transcipher explanations for every transformation.

These later stages belong in separate modules once their schemas and evaluation
criteria are defined. They should not be implied by Tier 1's lexical demo.
