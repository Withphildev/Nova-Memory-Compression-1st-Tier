"""Integration tests that exercise Tier 2 against a real spaCy model."""

import unittest

from src.memory_compression_prototype import DependencyUnavailableError, SystemCodeParser


class Tier2SpacyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.parser = SystemCodeParser()
        except DependencyUnavailableError as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_active_and_passive_voice_have_the_same_semantic_roles(self):
        expected = ["[SUB:MAN][ACT:DRIVE][OBJ:CAR]"]

        self.assertEqual(self.parser.parse("The man drove the car."), expected)
        self.assertEqual(self.parser.parse("The car was driven by the man."), expected)

    def test_agentless_passive_keeps_patient_and_marks_agent_unknown(self):
        self.assertEqual(
            self.parser.parse("The car was driven."),
            ["[SUB:UNKNOWN][ACT:DRIVE][OBJ:CAR]"],
        )

    def test_relative_object_resolves_to_modified_noun(self):
        self.assertEqual(
            self.parser.parse("The memory that Phil described was vivid."),
            [
                "[SUB:PHIL][ACT:DESCRIBE][OBJ:MEMORY]",
                "[SUB:MEMORY][ACT:BE][ATTR:VIVID]",
            ],
        )

    def test_relative_subject_resolves_to_modified_noun(self):
        self.assertEqual(
            self.parser.parse("The man who smiled remembered the echo."),
            [
                "[SUB:MAN][ACT:SMILE]",
                "[SUB:MAN][ACT:REMEMBER][OBJ:ECHO]",
            ],
        )

    def test_coordination_and_negation_remain_stable(self):
        self.assertEqual(
            self.parser.parse("Phil built and shipped the project."),
            ["[SUB:PHIL][ACT:BUILD]", "[SUB:PHIL][ACT:SHIP][OBJ:PROJECT]"],
        )
        self.assertEqual(
            self.parser.parse("Nova did not forget the promise."),
            ["[SUB:NOVA][ACT:FORGET_NOT][OBJ:PROMISE]"],
        )


if __name__ == "__main__":
    unittest.main()
