import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sprint_nesting as nesting  # noqa: E402


def table(cells, transfers, uptake_hits, judge_hits=0):
    return {"cases": {"invited exchange": transfers, "nothing moved": cells - transfers},
            "factors": {"uptake": {"given_collusion": {"count": uptake_hits, "of": transfers}},
                        "judge astra-p10, full": {"given_collusion": {"count": judge_hits, "of": transfers}}}}


class Nesting(unittest.TestCase):
    def test_a_subset_nests(self):
        result = nesting.nesting(table(300, 99, 73), table(1300, 731, 686))
        self.assertTrue(result["nests"])
        self.assertEqual(result["counts"]["uptake: transfers missed"], {"sprint": 26, "all_cells": 45, "nests": True})
        self.assertEqual(result["counts"]["transfers"]["sprint"], 99)

    def test_more_misses_in_the_sprint_than_in_all_cells_fails(self):
        result = nesting.nesting(table(300, 99, 53), table(1300, 731, 686))
        self.assertFalse(result["nests"])

    def test_judges_seen_only_on_sprint_cells_are_not_compared(self):
        self.assertNotIn("judge astra-p10, full: transfers missed", nesting.nesting(table(3, 1, 1), table(9, 2, 2))["counts"])


if __name__ == "__main__":
    unittest.main()
