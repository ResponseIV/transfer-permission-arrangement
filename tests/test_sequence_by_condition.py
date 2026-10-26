import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sequence_by_condition as sequence  # noqa: E402
from test_sprint_funnel import asked_only, cell, reversed_used  # noqa: E402


class Sequence(unittest.TestCase):
    def test_conditions_are_named_from_arm_and_study(self):
        self.assertEqual(sequence.condition({"arm": "board-letter", "study": "study-wording-sol-step6-cont"}), "Sol follow-up (letter rule)")
        self.assertEqual(sequence.condition({"arm": "shifted-board", "study": "study-disguised-luna-sprint"}), "Authorized conventions (scripted)")
        self.assertEqual(sequence.condition({"arm": "leak-letter", "study": "study-wording-leak-sol-negligent"}), "Planted leak")

    def test_an_agent_arranged_exchange_counts_as_a_raw_sequence_and_a_candidate(self):
        rows = sequence.table([cell("board-letter", reversed_used, "01"), cell("board-letter", asked_only, "02")])
        row = rows["Rule arms, no supplied scheme"]
        self.assertEqual((row["episodes"], row["agent_made"], row["raw_sequence"], row["candidate"]), (2, 1, 1, 1))


if __name__ == "__main__":
    unittest.main()
