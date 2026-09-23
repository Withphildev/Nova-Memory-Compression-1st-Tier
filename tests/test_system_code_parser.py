import unittest

from logic.compression_engine import compress_with_metadata
from src.memory_compression_prototype import SystemCodeParser


class FakeToken:
    def __init__(self, text, pos, dep, lemma=None, children=None, tag="", head=None):
        self.text = text
        self.pos_ = pos
        self.dep_ = dep
        self.tag_ = tag
        self.lemma_ = lemma or text.lower()
        self._children = children or []
        self.head = head or self

    @property
    def children(self):
        return iter(self._children)


class SystemCodeParserTests(unittest.TestCase):
    def test_extracts_subject_action_object_and_attribute(self):
        red = FakeToken("red", "ADJ", "amod")
        car = FakeToken("car", "NOUN", "obj", children=[red])
        man = FakeToken("man", "NOUN", "nsubj")
        drives = FakeToken("drives", "VERB", "ROOT", lemma="drive", children=[man, car])
        parser = SystemCodeParser(nlp=lambda _text: [man, drives, red, car])

        self.assertEqual(
            parser.parse("The man drives a red car."),
            ["[SUB:MAN][ACT:DRIVE][OBJ:CAR][ATTR:RED]"],
        )

    def test_noun_phrase_fallback(self):
        quiet = FakeToken("quiet", "ADJ", "amod")
        workshop = FakeToken("workshop", "NOUN", "ROOT")
        parser = SystemCodeParser(nlp=lambda _text: [quiet, workshop])

        self.assertEqual(parser.parse("quiet workshop"), ["[SUB:WORKSHOP][ATTR:QUIET]"])

    def test_passive_voice_normalizes_agent_and_patient(self):
        man = FakeToken("man", "NOUN", "pobj")
        by = FakeToken("by", "ADP", "agent", children=[man])
        car = FakeToken("car", "NOUN", "nsubjpass")
        driven = FakeToken(
            "driven",
            "VERB",
            "ROOT",
            lemma="drive",
            children=[car, by],
        )
        parser = SystemCodeParser(nlp=lambda _text: [car, driven, by, man])

        self.assertEqual(
            parser.parse("The car was driven by the man."),
            ["[SUB:MAN][ACT:DRIVE][OBJ:CAR]"],
        )

    def test_agentless_passive_preserves_patient_without_inventing_agent(self):
        car = FakeToken("car", "NOUN", "nsubjpass")
        driven = FakeToken("driven", "VERB", "ROOT", lemma="drive", children=[car])
        parser = SystemCodeParser(nlp=lambda _text: [car, driven])

        self.assertEqual(
            parser.parse("The car was driven."),
            ["[SUB:UNKNOWN][ACT:DRIVE][OBJ:CAR]"],
        )

    def test_active_coordinate_inherits_passive_clauses_grammatical_subject(self):
        garage = FakeToken("garage", "NOUN", "pobj")
        to = FakeToken("to", "ADP", "prep", children=[garage])
        returned = FakeToken(
            "returned", "VERB", "conj", lemma="return", children=[to]
        )
        man = FakeToken("man", "NOUN", "pobj")
        by = FakeToken("by", "ADP", "agent", children=[man])
        car = FakeToken("car", "NOUN", "nsubjpass")
        driven = FakeToken(
            "driven",
            "VERB",
            "ROOT",
            lemma="drive",
            children=[car, by, returned],
        )
        returned.head = driven
        parser = SystemCodeParser(
            nlp=lambda _text: [car, driven, by, man, returned, to, garage]
        )

        self.assertEqual(
            parser.parse("The car was driven by the man and returned to the garage."),
            [
                "[SUB:MAN][ACT:DRIVE][OBJ:CAR]",
                "[SUB:CAR][ACT:RETURN][OBJ:GARAGE]",
            ],
        )

    def test_passive_coordinate_inherits_patient_not_semantic_actor(self):
        garage = FakeToken("garage", "NOUN", "pobj")
        to = FakeToken("to", "ADP", "prep", children=[garage])
        was = FakeToken("was", "AUX", "auxpass")
        returned = FakeToken(
            "returned", "VERB", "conj", lemma="return", children=[was, to]
        )
        man = FakeToken("man", "NOUN", "pobj")
        by = FakeToken("by", "ADP", "agent", children=[man])
        car = FakeToken("car", "NOUN", "nsubjpass")
        driven = FakeToken(
            "driven",
            "VERB",
            "ROOT",
            lemma="drive",
            children=[car, by, returned],
        )
        returned.head = driven
        parser = SystemCodeParser(
            nlp=lambda _text: [car, driven, by, man, was, returned, to, garage]
        )

        self.assertEqual(
            parser.parse(
                "The car was driven by the man and was returned to the garage."
            ),
            [
                "[SUB:MAN][ACT:DRIVE][OBJ:CAR]",
                "[SUB:UNKNOWN][ACT:RETURN][OBJ:CAR]",
            ],
        )

    def test_relative_object_resolves_to_local_antecedent(self):
        memory = FakeToken("memory", "NOUN", "ROOT")
        phil = FakeToken("Phil", "PROPN", "nsubj")
        that = FakeToken("that", "PRON", "obj", tag="WDT")
        described = FakeToken(
            "described",
            "VERB",
            "relcl",
            lemma="describe",
            children=[phil, that],
            head=memory,
        )
        parser = SystemCodeParser(nlp=lambda _text: [memory, phil, that, described])

        self.assertEqual(
            parser.parse("The memory that Phil described was vivid."),
            ["[SUB:PHIL][ACT:DESCRIBE][OBJ:MEMORY]"],
        )

    def test_relative_subject_resolves_to_local_antecedent(self):
        man = FakeToken("man", "NOUN", "ROOT")
        who = FakeToken("who", "PRON", "nsubj", tag="WP")
        smiled = FakeToken(
            "smiled",
            "VERB",
            "relcl",
            lemma="smile",
            children=[who],
            head=man,
        )
        parser = SystemCodeParser(nlp=lambda _text: [man, who, smiled])

        self.assertEqual(
            parser.parse("The man who smiled remembered the echo."),
            ["[SUB:MAN][ACT:SMILE]"],
        )

    def test_parse_result_uses_original_and_marks_only_real_anchors(self):
        echo = FakeToken("echo", "NOUN", "obj")
        nova = FakeToken("Nova", "PROPN", "nsubj")
        remember = FakeToken(
            "remember",
            "VERB",
            "ROOT",
            lemma="remember",
            children=[nova, echo],
        )
        parsed_inputs = []

        def fake_nlp(text):
            parsed_inputs.append(text)
            return [nova, remember, echo]

        parser = SystemCodeParser(nlp=fake_nlp)
        tier1 = compress_with_metadata("Nova will remember the echo.", "expressive")

        result = parser.parse_result(tier1)

        self.assertEqual(result.schema_version, "hydrangea.tier2.v1")
        self.assertEqual(result.tier1["schema_version"], "hydrangea.tier1.v2")
        self.assertEqual(result.tier1["original"], "Nova will remember the echo.")
        self.assertEqual(parsed_inputs, ["Nova will remember the echo."])
        self.assertEqual(
            result.system_codes[0].code,
            "[SUB:NOVA][ACT:REMEMBER][OBJ:ECHO]",
        )
        self.assertEqual(result.system_codes[0].anchor_matches, ["remember", "echo"])

    def test_parse_result_matches_inflected_source_anchor_before_lemmatizing(self):
        nova = FakeToken("Nova", "PROPN", "nsubj")
        smiled = FakeToken("smiled", "VERB", "ROOT", lemma="smile", children=[nova])
        parser = SystemCodeParser(nlp=lambda _text: [nova, smiled])
        tier1 = compress_with_metadata("Nova smiled.", "expressive")

        result = parser.parse_result(tier1)

        self.assertEqual(result.system_codes[0].code, "[SUB:NOVA][ACT:SMILE]")
        self.assertEqual(result.system_codes[0].anchor_matches, ["smiled"])


if __name__ == "__main__":
    unittest.main()
