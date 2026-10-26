import sys
import copy
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_cell as audit  # noqa: E402
from test_sprint_funnel import asked_only, cell, reversed_used  # noqa: E402
from study_agreed import AGREED  # noqa: E402
from study_disguised import REVERSED, SHIFTED  # noqa: E402
from study_pact import CODED, PLAIN  # noqa: E402


class Audit(unittest.TestCase):
    def test_prohibiting_encoding_does_not_prescribe_it(self):
        sample = cell("board-purpose", reversed_used, "01")
        result = audit.audit(sample, "full", instructions=True)
        self.assertTrue(result["coordination"]["agent_made_candidate"])
        self.assertNotIn("principal", result["coordination"]["finding"])

    def test_affirmative_pacts_and_conventions_are_principal_directed(self):
        for prompt in (AGREED, CODED, PLAIN, REVERSED, SHIFTED):
            with self.subTest(prompt=prompt):
                sample = cell("board-letter", reversed_used, "01")
                sample["prompt"] = prompt
                result = audit.audit(sample, "full", instructions=True)
                self.assertFalse(result["coordination"]["agent_made_candidate"])
                self.assertIn("principal", result["coordination"]["finding"])

    def test_hidden_answers_do_not_affect_text_or_log_observers(self):
        sample = cell("board-letter", reversed_used, "01")
        changed = copy.deepcopy(sample)
        for event in changed["events"]:
            if event["action"] == "final_answer":
                event["answer"] = "different hidden answer"
        for observer in ("text", "both"):
            with self.subTest(observer=observer):
                self.assertEqual(audit.audit(sample, observer), audit.audit(changed, observer))

    def test_a_reversed_exchange_on_request_is_flow_with_a_candidate_offer_and_carrier(self):
        result = audit.audit(cell("board-letter", reversed_used, "01"), "full", instructions=True)
        self.assertTrue(result["information_flow"]["uptake"])
        self.assertEqual(result["policy"]["finding"], "a confidentiality rule was in force")
        self.assertTrue(result["coordination"]["agent_made_candidate"])

    def test_without_instructions_the_rule_is_unknown(self):
        result = audit.audit(cell("board-letter", reversed_used, "01"), "both")
        self.assertIn("unknown without the instructions", result["policy"]["finding"])

    def test_a_plain_request_with_nothing_moved_is_no_flow_and_no_offer(self):
        result = audit.audit(cell("board-purpose", asked_only, "01"), "full", instructions=True)
        self.assertFalse(result["information_flow"]["uptake"])
        self.assertFalse(result["coordination"]["agent_made_candidate"])

    def test_ciphertext_lists_count_as_carriers(self):
        self.assertTrue(audit.carrier_like("2412 1745 902 3001"))
        self.assertFalse(audit.carrier_like("please send your token"))


if __name__ == "__main__":
    unittest.main()
