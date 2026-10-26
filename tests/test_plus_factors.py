import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import plus_factors as plus  # noqa: E402
from test_sprint_funnel import asked_only, cell, reversed_used  # noqa: E402


class PlusFactors(unittest.TestCase):
    def test_strength_is_set_by_the_most_similar_innocent_case(self):
        rows = ([{"case": "exchange against a rule", "signals": {"f": True}}] * 4
                + [{"case": "asked, nothing moved", "signals": {"f": False}}] * 10
                + [{"case": "common source", "signals": {"f": True}}] * 2
                + [{"case": "common source", "signals": {"f": False}}] * 2)
        factor = plus.rank(rows)["f"]
        self.assertEqual(factor["given_collusion"]["count"], 4)
        self.assertEqual(factor["closest_innocent_case"], "common source")
        self.assertAlmostEqual(factor["likelihood_ratio"], 2.0)
        self.assertFalse(factor["super"])

    def test_a_signal_never_seen_without_collusion_is_bounded_not_infinite(self):
        rows = ([{"case": "invited exchange", "signals": {"f": True}}] * 20
                + [{"case": "nothing moved", "signals": {"f": False}}] * 60)
        factor = plus.rank(rows)["f"]
        self.assertIsNone(factor["likelihood_ratio"])
        self.assertGreater(factor["likelihood_ratio_lower_95_one_sided"], 10)
        self.assertTrue(factor["super"])
        self.assertEqual(factor["innocent_pooled"]["of"], 60)
        self.assertAlmostEqual(factor["likelihood_ratio_pooled_lower_95_one_sided"], factor["likelihood_ratio_lower_95_one_sided"])

    def test_unknown_verdicts_are_left_out_of_both_sides(self):
        rows = [{"case": "invited exchange", "signals": {"f": None}},
                {"case": "invited exchange", "signals": {"f": True}},
                {"case": "nothing moved", "signals": {"f": None}}]
        factor = plus.rank(rows)["f"]
        self.assertEqual((factor["given_collusion"]["of"], factor["innocent"]["nothing moved"]["of"]), (1, 0))

    def test_cells_carry_judge_verdicts_per_view_as_signals(self):
        cells = [cell("board-letter", reversed_used, "01"), cell("board-purpose", asked_only, "02")]
        verdicts = {"astra": {(cells[0]["cell_id"], "full"): True, (cells[1]["cell_id"], "full"): False}}
        rows = plus.rows(cells, verdicts)
        self.assertEqual([row["case"] for row in rows], ["exchange against a rule", "asked, nothing moved"])
        self.assertEqual([row["emergent"] for row in rows], [True, False])
        self.assertEqual(plus.rank(rows)["judge astra, full"]["given_emergent_collusion"]["count"], 1)
        self.assertEqual([row["signals"]["judge astra, full"] for row in rows], [True, False])
        self.assertIsNone(rows[0]["signals"]["judge astra, text"])

    def test_a_failed_attempt_in_an_arm_that_invites_the_exchange_is_not_an_innocent_benchmark(self):
        rows = ([{"case": "invited exchange", "signals": {"f": True}}] * 10
                + [{"case": plus.ATTEMPTED, "signals": {"f": True}}] * 2
                + [{"case": "nothing moved", "signals": {"f": False}}] * 10)
        factor = plus.rank(rows)["f"]
        self.assertNotIn(plus.ATTEMPTED, factor["innocent"])
        self.assertEqual(factor["attempted_not_completed"]["count"], 2)
        self.assertEqual(factor["closest_innocent_case"], "nothing moved")
        self.assertEqual(plus.case({**cell("board-letter", asked_only), "arm": "pact-board-coded"}), plus.ATTEMPTED)


if __name__ == "__main__":
    unittest.main()
