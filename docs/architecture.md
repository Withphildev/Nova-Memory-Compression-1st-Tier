# HYDRANGEA memory-compression architecture

## Purpose

This repository demonstrates the first two ideas in a larger nonlinear memory
architecture. It is not a complete memory store and does not implement Reverse
Blooming.

## Layer model

### 1. Gist layer: Tier 1

Tier 1 performs lexical semantic distillation:

```text
The man is driving a red car.
        ↓
man driving red car
```

Compact and Expressive modes trade prose fidelity for size reduction. The
output is useful for scanning, clustering, and prompt-budget experiments. It is
not an exact encoding of the input.

### 2. System-code layer: Tier 2 prototype

Tier 2 uses a dependency parse to identify a subject, action, object, and
attributes:

```text
[SUB:MAN][ACT:DRIVE][OBJ:CAR][ATTR:RED]
```

The current parser is experimental. It does not yet define a stable wire format,
an ontology, or cross-language behavior.

It normalizes passive voice into semantic agent/action/patient roles and uses a
bounded local heuristic for WH relative pronouns inside `relcl` dependencies.
That heuristic is not general coreference resolution: it does not chase
pronouns across clauses or sentences.

For subject-less coordinated clauses, Tier 2 inherits the governing clause's
raw grammatical subject before deciding whether the sibling is active or
passive. This prevents a passive clause's semantic agent from being assigned to
an active sibling and prevents an inherited patient from being mislabeled as a
passive sibling's actor.

### 3. Pattern layer: foundation implemented

Tier 3 now defines versioned persistence schemas and an injectable local
embedding boundary. Repeated instances can be represented as candidates or
promoted pattern nodes with links back to every supporting source. The approved
promotion threshold is three instances. Similarity calibration, clustering,
and automatic merging are not implemented yet.

Ambiguity and contradiction links are distinct. Contradiction detection is
schema-only: no classifier currently creates those links automatically.

### 4. Bloom layer: planned

Bloom expands a gist or pattern into useful context. A trustworthy Bloom may use:

- retained source fragments;
- links to original events;
- pattern membership and recurrence counts;
- emotion, sensory, spatial, and intent metadata;
- the current retrieval query.

It must distinguish recalled evidence from generated connective language.
Exact reconstruction is possible only when the original text or a reversible
encoding was retained.

### 5. Reverse Blooming: planned

Reverse Blooming is not decompression. A later insight can re-weight, annotate,
or reframe older nodes while preserving their previous versions and provenance.
It must not silently rewrite source events.

## Tier 1 envelope

`compress_with_metadata()` returns `hydrangea.tier1.v2` with:

- requested and resolved modes;
- the original fragment (or, in a future store, a durable source reference);
- the compressed gist;
- a per-word `kept`, `stripped`, or `emotional` decision trace;
- deduplicated emotional anchors that were actually retained;
- character and word metrics;
- optional named-tokenizer metrics;
- `reversible_from_gist: false`.

The CLI can emit this envelope as JSON Lines. CSV output includes the original,
resolved mode, compressed gist, and reduction metrics. Tokenizer metrics are
only populated when a tokenizer is explicitly requested.

## Tier 1 → Tier 2 contract

`SystemCodeParser.parse_result()` accepts a `CompressionResult` and returns a
`hydrangea.tier2.v1` combined envelope. It always dependency-parses the retained
original because the gist has intentionally lost grammar. For each generated
system code it reports exact matches against the Tier 1 anchors.

Exact matching is a deliberate trust boundary: Tier 2 does not invent salience
for unrelated attributes, and it does not currently stem or semantically expand
anchors. Those behaviors require an explicit, separately evaluated policy.

## Trust invariants

1. A gist is never labeled as the full memory.
2. Bloomed details need provenance or an explicit generated label.
3. Reverse Blooming appends interpretation; it does not mutate historical fact.
4. Historical test artifacts remain separate from current validation claims.
5. Token savings are tokenizer-specific; this project reports deterministic
   character and word reductions unless a tokenizer is explicitly selected.

## Current data flow

```text
text line
  → mode detection
  → lexical filtering + decision capture
  → compact gist + emotional anchors
  → hydrangea.tier1.v2 envelope

optional experiment:
tier1 envelope
  → spaCy parses retained original
  → system-code tags + exact anchor matches
  → hydrangea.tier2.v1 envelope

optional Tier 3 foundation:
tier1 + optional tier2 envelope
  → durable PatternMemory retaining original text
  → injectable local embedder with pinned model revision
  → auditable EmbeddedMemory for future calibration
```

## Out of scope

- production memory persistence;
- semantic-vector clustering and calibrated similarity thresholds;
- sensory encoding;
- source-fragment encryption;
- automatic pattern merging and contradiction detection;
- Bloom and Reverse Bloom execution.
