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

### 3. Pattern layer: planned

Repeated instances should become a pattern node with links back to every
supporting source. Consolidation may reduce repetition, but it must not destroy
the evidence required for trustworthy recall.

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
```

## Out of scope

- production memory persistence;
- semantic-vector clustering;
- sensory encoding;
- source-fragment encryption;
- pattern-node governance;
- Bloom and Reverse Bloom execution.
