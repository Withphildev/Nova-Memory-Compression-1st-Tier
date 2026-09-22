import unittest

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


if __name__ == "__main__":
    unittest.main()
