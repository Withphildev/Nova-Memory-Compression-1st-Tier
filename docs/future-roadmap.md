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

## Next: stabilize Tier 1

- Publish a versioned filler-word and emotional-anchor policy.
- Add Unicode and multilingual fixtures.
- Add property tests for punctuation and whitespace invariants.
- Benchmark across multiple explicitly named tokenizers instead of
  extrapolating from character counts.

## Then: define the memory-node schema

- Durable source IDs and provenance.
- Gist, system-code, and pattern-node fields.
- Evidence links for every Bloom operation.
- Append-only interpretation and re-weighting history.
- Contradiction and ambiguity representation.

## Later: Bloom and Reverse Bloom prototypes

- Evidence-backed gist expansion.
- Pattern consolidation with reversible links to instances.
- Query-selectable recall modes: blurred, gist, and full detail.
- Reverse Bloom annotations that preserve prior weights and interpretations.
- Human-readable Transcipher explanations for every transformation.

These later stages belong in separate modules once their schemas and evaluation
criteria are defined. They should not be implied by Tier 1's lexical demo.
