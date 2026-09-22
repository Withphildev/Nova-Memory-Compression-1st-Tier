"""
memory_compression_prototype.py

Nova Memory Compression – Tier 2
Implements EchoMemory Layer 2: Pre-Compression in System Code.
Parses natural language into Subject-Action-Object-Attribute system codes.

Author: Phil & Nova
Version: 2.0
"""

import sys


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
        doc = self.nlp(text)
        results = []
        
        # Identify verbs and auxiliary roots of clauses
        verbs = [
            t
            for t in doc
            if t.pos_ in ("VERB", "AUX") and t.dep_ not in ("aux", "auxpass", "aux:pass")
        ]
        
        if not verbs:
            # Fallback for simple noun phrases
            subjects = [t.text.upper() for t in doc if t.pos_ in ("NOUN", "PROPN")]
            attrs = [t.text.upper() for t in doc if t.pos_ == "ADJ"]
            sub_str = subjects[0] if subjects else "UNKNOWN"
            code = f"[SUB:{sub_str}]"
            if attrs:
                code += "".join([f"[ATTR:{a}]" for a in attrs])
            return [code]

        for verb in verbs:
            subject = None
            obj = None
            attrs = []
            negated = False
            
            # Check children of the verb
            for child in verb.children:
                if child.dep_ in ("nsubj", "nsubjpass", "nsubj:pass"):
                    subject = child.text.upper()
                elif child.dep_ in ("dobj", "obj", "pobj", "attr", "oprd"):
                    obj = child.text.upper()
                    # Check for adjective modifiers on the object
                    for gc in child.children:
                        if gc.dep_ == "amod":
                            attrs.append(gc.text.upper())
                elif child.dep_ == "acomp":
                    attrs.append(child.text.upper())
                elif child.dep_ == "neg":
                    negated = True
                elif child.dep_ == "prep":
                    for gc in child.children:
                        if gc.dep_ == "pobj":
                            obj = gc.text.upper()
                            for ggc in gc.children:
                                if ggc.dep_ == "amod":
                                    attrs.append(ggc.text.upper())
                elif child.dep_ == "prt":
                    attrs.append(child.text.upper())
            
            # Inherit subject from head verb if missing in subordinate clause
            if not subject and verb.head != verb:
                for child in verb.head.children:
                    if child.dep_ in ("nsubj", "nsubjpass", "nsubj:pass"):
                        subject = child.text.upper()

            # Compile semantic tags
            sub_tag = f"[SUB:{subject}]" if subject else "[SUB:UNKNOWN]"
            
            verb_lemma = verb.lemma_.upper()
            if negated:
                act_tag = f"[ACT:{verb_lemma}_NOT]"
            else:
                act_tag = f"[ACT:{verb_lemma}]"
                
            obj_tag = f"[OBJ:{obj}]" if obj else ""
            attr_tag = "".join([f"[ATTR:{a}]" for a in attrs])
            
            results.append(f"{sub_tag}{act_tag}{obj_tag}{attr_tag}")
            
        return results


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
