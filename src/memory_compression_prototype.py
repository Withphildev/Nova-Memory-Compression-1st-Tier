"""
memory_compression_prototype.py

Nova Memory Compression – Tier 2
Implements EchoMemory Layer 2: Pre-Compression in System Code.
Parses natural language into Subject-Action-Object-Attribute system codes.

Author: Phil & Nova
Version: 2.0
"""

import spacy
import sys

class SystemCodeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("[!] spaCy model 'en_core_web_sm' not found. Please install it using:")
            print("    python -m spacy download en_core_web_sm")
            sys.exit(1)

    def parse(self, text):
        doc = self.nlp(text)
        results = []
        
        # Identify verbs and auxiliary roots of clauses
        verbs = [t for t in doc if t.pos_ in ("VERB", "AUX") and t.dep_ != "aux" and t.dep_ != "auxpass"]
        
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
                if child.dep_ in ("nsubj", "nsubjpass"):
                    subject = child.text.upper()
                elif child.dep_ in ("dobj", "pobj", "attr", "oprd"):
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
                    if child.dep_ in ("nsubj", "nsubjpass"):
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
    parser = SystemCodeParser()
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        codes = parser.parse(text)
        print(f"Original: \"{text}\"")
        print("System Code Output:")
        for c in codes:
            print(f"  {c}")
    else:
        print("Usage: python src/memory_compression_prototype.py <phrase>")