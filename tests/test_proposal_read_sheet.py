import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import proposal_read_sheet as sheet  # noqa: E402
from test_sprint_funnel import asked_only, cell, reversed_used  # noqa: E402


def cells():
    found = [cell("board-letter", reversed_used, f"{index:02d}") for index in range(1, 4)]
    found += [cell("board-purpose", asked_only, f"{index:02d}") for index in range(1, 9)]
    return found


class ReadSheet(unittest.TestCase):
    def test_every_flagged_cell_and_a_seeded_sample_of_the_rest_are_drawn(self):
        sample = cells()
        flagged = {c["cell_id"]: c["arm"] == "board-letter" for c in sample}
        first = sheet.draw(sample, flagged, negatives=4, seed=7)
        self.assertEqual(first, sheet.draw(sample, flagged, negatives=4, seed=7))
        self.assertEqual(len(first), 7)
        self.assertEqual(sum(flagged[c["cell_id"]] for c in first), 3)

    def test_the_sheet_is_blind_and_the_key_holds_what_it_hides(self):
        sample = cells()
        flagged = {c["cell_id"]: c["arm"] == "board-letter" for c in sample}
        text, key = sheet.render(sheet.draw(sample, flagged, negatives=2, seed=7), flagged)
        self.assertNotIn("gpt-5.6-sol", text)
        self.assertNotIn("study-wording", text)
        self.assertIn("222222222B", text)
        self.assertEqual(sorted(key), ["R01", "R02", "R03", "R04", "R05"])
        self.assertEqual(sum(row["judge_proposed"] for row in key.values()), 3)


if __name__ == "__main__":
    unittest.main()
