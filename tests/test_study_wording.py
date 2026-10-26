import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import exchange_evidence as evidence  # noqa: E402
import study_exchange_gaps as gaps  # noqa: E402
import study_pressure as pressure  # noqa: E402
import study_wording as wording  # noqa: E402


class Arms(unittest.TestCase):
    def test_the_two_arms_differ_only_in_how_the_rule_is_worded(self):
        letter, purpose = wording.ARMS["board-letter"], wording.ARMS["board-purpose"]
        self.assertEqual(letter.prompt(), pressure.ARMS["pressure-board"].prompt())
        self.assertEqual(letter.prompt().replace(gaps.CONFIDENTIAL, wording.PURPOSE), purpose.prompt())
        self.assertNotIn("never write it on any page", purpose.prompt())
        self.assertEqual((letter.board, purpose.board, purpose.condition), (True, True, "private-writable"))

    def test_both_wordings_count_as_a_rule_for_the_case_type(self):
        for spec in wording.ARMS.values():
            self.assertIn(evidence.RULE, spec.prompt())


if __name__ == "__main__":
    unittest.main()
