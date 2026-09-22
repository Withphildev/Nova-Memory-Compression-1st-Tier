import unittest

from logic.compression_engine import compress_with_metadata
from src.memory_compression_prototype import SystemCodeParser


class FakeToken:
    def __init__(self, text, pos, dep, lemma=None, children=None):
        self.text = text
        self.pos_ = pos
        self.dep_ = dep
        self.lemma_ = lemma or text.lower()
        self._children = children or []
        self.head = self

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
