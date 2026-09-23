"""
memory_compression_prototype.py

Nova Memory Compression – Tier 2
Implements EchoMemory Layer 2: Pre-Compression in System Code.
Parses natural language into Subject-Action-Object-Attribute system codes.

Author: Phil & Nova
Repository release: 2.5.0
"""

from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logic.compression_engine import CompressionResult


@dataclass(frozen=True)
class SystemCodeEntry:
    """One system-code statement plus exact Tier 1 anchor matches."""

    code: str
    anchor_matches: list[str]


@dataclass(frozen=True)
class Tier2ParseResult:
    """Combined Tier 1 → Tier 2 handoff envelope."""

    schema_version: str
    tier1: dict[str, object]
    system_codes: list[SystemCodeEntry]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class DependencyUnavailableError(RuntimeError):
    """Raised when the optional Tier 2 NLP dependency is unavailable."""


class SystemCodeParser:
    def __init__(self, nlp=None, model="en_core_web_sm"):
        if nlp is not None:
            self.nlp = nlp
            return

        try:
            import spacy
        except ImportError as exc:
            raise DependencyUnavailableError(
                "Tier 2 requires spaCy. Install it with: pip install -e '.[tier2]'"
            ) from exc

        try:
            self.nlp = spacy.load(model)
        except OSError as exc:
            raise DependencyUnavailableError(
                f"spaCy model '{model}' is not installed. Run: python -m spacy download {model}"
            ) from exc

    def parse(self, text):
        return [code for code, _source_terms in self._parse_doc(self.nlp(text))]

    @staticmethod
    def _resolve_relative_token(token, verb):
        """Resolve a local WH relative pronoun to the noun its clause modifies.

        This is intentionally a bounded heuristic, not general coreference
        resolution. It only handles WDT/WP/WP$ tokens attached within a
        ``relcl`` whose head is the nearby antecedent noun. It does not resolve
        pronouns across clauses or sentence boundaries.
        """

        if (
            getattr(token, "tag_", "") in {"WDT", "WP", "WP$"}
            and verb.dep_ == "relcl"
            and verb.head != verb
        ):
            return verb.head
        return token

    def _parse_doc(self, doc):
        results = []
        
        # Identify verbs and auxiliary roots of clauses
        verbs = [
            t
            for t in doc
            if t.pos_ in ("VERB", "AUX") and t.dep_ not in ("aux", "auxpass", "aux:pass")
        ]
        
        if not verbs:
            # Fallback for simple noun phrases
            subject_tokens = [t for t in doc if t.pos_ in ("NOUN", "PROPN")]
            attr_tokens = [t for t in doc if t.pos_ == "ADJ"]
            sub_str = subject_tokens[0].text.upper() if subject_tokens else "UNKNOWN"
            code = f"[SUB:{sub_str}]"
            if attr_tokens:
                code += "".join([f"[ATTR:{token.text.upper()}]" for token in attr_tokens])
            source_terms = [token.text for token in subject_tokens + attr_tokens]
            return [(code, source_terms)]

        for verb in verbs:
            subject = None
            obj = None
            passive_patient = None
            passive_agent = None
            attrs = []
            negated = False
            source_terms = [verb.text]
            
            # Check children of the verb
            for child in verb.children:
                if child.dep_ == "nsubj":
                    resolved = self._resolve_relative_token(child, verb)
                    subject = resolved.text.upper()
                    source_terms.append(resolved.text)
                elif child.dep_ in ("nsubjpass", "nsubj:pass"):
                    resolved = self._resolve_relative_token(child, verb)
                    passive_patient = resolved.text.upper()
                    source_terms.append(resolved.text)
                    for gc in resolved.children:
                        if gc.dep_ == "amod":
                            attrs.append(gc.text.upper())
                            source_terms.append(gc.text)
                elif child.dep_ in ("dobj", "obj", "pobj", "attr", "oprd"):
                    resolved = self._resolve_relative_token(child, verb)
                    obj = resolved.text.upper()
                    source_terms.append(resolved.text)
                    # Check for adjective modifiers on the object
                    for gc in resolved.children:
                        if gc.dep_ == "amod":
                            attrs.append(gc.text.upper())
                            source_terms.append(gc.text)
                elif child.dep_ == "acomp":
                    attrs.append(child.text.upper())
                    source_terms.append(child.text)
                elif child.dep_ == "neg":
                    negated = True
                elif child.dep_ == "agent":
                    for gc in child.children:
                        if gc.dep_ in ("pobj", "obj"):
                            resolved = self._resolve_relative_token(gc, verb)
                            passive_agent = resolved.text.upper()
                            source_terms.append(resolved.text)
                elif child.dep_ == "prep":
                    for gc in child.children:
                        if gc.dep_ == "pobj":
                            obj = gc.text.upper()
                            source_terms.append(gc.text)
                            for ggc in gc.children:
                                if ggc.dep_ == "amod":
                                    attrs.append(ggc.text.upper())
                                    source_terms.append(ggc.text)
                elif child.dep_ == "prt":
                    attrs.append(child.text.upper())
                    source_terms.append(child.text)
            
            # Normalize passive voice to semantic agent/action/patient roles.
            if passive_patient:
                subject = passive_agent
                obj = passive_patient

            # Inherit subject from a governing verb for coordinated clauses.
            if not subject and not passive_patient and verb.head != verb:
                for child in verb.head.children:
                    if child.dep_ == "nsubj":
                        resolved = self._resolve_relative_token(child, verb.head)
                        subject = resolved.text.upper()
                        source_terms.append(resolved.text)

            # Compile semantic tags
            sub_tag = f"[SUB:{subject}]" if subject else "[SUB:UNKNOWN]"
            
            verb_lemma = verb.lemma_.upper()
            if negated:
                act_tag = f"[ACT:{verb_lemma}_NOT]"
            else:
                act_tag = f"[ACT:{verb_lemma}]"
                
            obj_tag = f"[OBJ:{obj}]" if obj else ""
            attr_tag = "".join([f"[ATTR:{a}]" for a in attrs])
            
            results.append((f"{sub_tag}{act_tag}{obj_tag}{attr_tag}", source_terms))
            
        return results

    def parse_result(self, result: CompressionResult) -> Tier2ParseResult:
        """Parse the retained original and enrich codes with Tier 1 anchors.

        Dependency parsing always uses ``result.original`` because the compact
        gist intentionally lacks grammar. Anchor matching is exact and does not
        infer salience for unrelated attributes.
        """

        anchors = {anchor.casefold(): anchor for anchor in result.anchors}
        entries = []
        for code, source_terms in self._parse_doc(self.nlp(result.original)):
            normalized_terms = {term.casefold() for term in source_terms}
            matches = [
                anchor
                for normalized, anchor in anchors.items()
                if normalized in normalized_terms
            ]
            entries.append(SystemCodeEntry(code=code, anchor_matches=matches))

        return Tier2ParseResult(
            schema_version="hydrangea.tier2.v1",
            tier1=result.to_dict(),
            system_codes=entries,
        )


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: python src/memory_compression_prototype.py <phrase>")
        sys.exit(2)

    try:
        parser = SystemCodeParser()
    except DependencyUnavailableError as exc:
        print(f"[!] {exc}", file=sys.stderr)
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    codes = parser.parse(text)
    print(f"Original: \"{text}\"")
    print("System Code Output:")
    for c in codes:
        print(f"  {c}")
