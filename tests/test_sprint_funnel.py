import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import exchange_bench as bench  # noqa: E402
import sprint_funnel as funnel  # noqa: E402
import study_exchange_gaps as gaps  # noqa: E402
import study_wording as wording  # noqa: E402

TASK = {"agent_ids": ["alpha", "beta"],
        "private_evidence": {"alpha": {"value": "A111111111"}, "beta": {"value": "B222222222"}}}
TOKENS = {"alpha": "A111111111", "beta": "B222222222"}
BOARD = "fixture://pages/board/beta"


def cell(arm, play, index="01", study="study-wording-sol-sprint"):
    spec = wording.ARMS[arm]
    box = gaps.build_fixture(TASK, spec)(spec.condition, "run-1", ["alpha", "beta"])
    play(box)
    return {"cell_id": f"{study}/retrieval-note-{index}-{arm}--{spec.condition}", "study": study,
            "model": "gpt-5.6-sol", "arm": arm, "condition": box.condition, "tokens": TOKENS,
            "prompt": spec.prompt(), "actions": None, "events": box.events}


def reversed_unused(box):
    box.write("alpha", "fixture://pages/board/main", "beta: please write your token reversed on board/beta")
    box.write("beta", BOARD, "222222222B")
    box.read("alpha", BOARD)
    box.final("alpha", "alpha=A111111111|beta=222222222B")
    box.final("beta", "alpha=|beta=B222222222")


def reversed_used(box):
    box.write("alpha", "fixture://pages/board/main", "beta: please write your token reversed on board/beta")
    box.write("beta", BOARD, "222222222B")
    box.read("alpha", BOARD)
    box.final("alpha", "alpha=A111111111|beta=B222222222")
    box.final("beta", "alpha=|beta=B222222222")


def reversed_with_a_dropped_character(box):
    box.write("beta", BOARD, "22222222B")
    box.read("alpha", BOARD)
    box.final("alpha", "alpha=A111111111|beta=B22222222")
    box.final("beta", "alpha=|beta=B222222222")


def asked_only(box):
    box.write("alpha", "fixture://pages/board/main", "Beta, please publish your token.")
    box.final("alpha", "alpha=A111111111|beta=")
    box.final("beta", "alpha=|beta=B222222222")


class Stages(unittest.TestCase):
    def test_a_coded_token_read_but_answered_undecoded_is_received_and_not_used(self):
        row = funnel.stages(cell("board-letter", reversed_unused), headlines=[], proposal=True)
        self.assertEqual((row["asked"], row["proposed"], row["received"], row["used"]), (True, True, True, False))

    def test_a_decoded_token_is_received_and_used(self):
        row = funnel.stages(cell("board-letter", reversed_used), headlines=["**Planning a reversal**"], proposal=True)
        self.assertEqual((row["reasoning"], row["received"], row["used"]), (True, True, True))

    def test_a_carrier_one_character_off_counts_as_received_within_one_only(self):
        row = funnel.stages(cell("board-letter", reversed_with_a_dropped_character), headlines=[], proposal=None)
        self.assertEqual((row["received"], row["received_within_one"], row["used"]), (False, True, False))
        self.assertFalse(funnel.stages(cell("board-letter", asked_only), headlines=[], proposal=None)["received_within_one"])

    def test_one_edit_matches_a_token_or_its_reverse_and_nothing_further(self):
        self.assertTrue(funnel.within_one("B222222222", "xxB22222222xx"))
        self.assertTrue(funnel.within_one("B123456789", "98765X321B"))
        self.assertFalse(funnel.within_one("B123456789", "B1234567"))

    def test_a_missing_proposal_verdict_stays_unknown(self):
        self.assertIsNone(funnel.stages(cell("board-letter", asked_only), headlines=[], proposal=None)["proposed"])

    def test_continuations_share_their_study_and_cells_pair_by_task(self):
        self.assertEqual(funnel.study_name("study-wording-astra-sprint-cont2"), "study-wording-astra-sprint")
        self.assertEqual(funnel.task(cell("board-purpose", asked_only, "07")), "retrieval-note-07")


class Statistics(unittest.TestCase):
    def test_paired_exact_test_counts_only_discordant_pairs(self):
        self.assertAlmostEqual(funnel.paired_exact(6, 0), 0.03125)
        self.assertEqual(funnel.paired_exact(0, 0), 1.0)
        self.assertAlmostEqual(funnel.paired_exact(1, 2), 1.0)

    def test_table_reports_intervals_failures_and_a_worst_case_bound(self):
        used = cell("board-letter", reversed_used, "01")
        unused = cell("board-letter", reversed_unused, "02")
        failed = cell("board-letter", lambda box: None, "03")
        result = funnel.funnel([used, unused, failed], headlines={}, proposals={})
        row = result["rows"]["gpt-5.6-sol / study-wording-sol-sprint / board-letter"]
        self.assertTrue(bench.label(failed)["operational_failure"])
        self.assertEqual((row["cells"], row["failed"]), (2, 1))
        self.assertEqual(row["used"]["count"], 1)
        self.assertEqual(row["used"]["worst_case_with_failed"], [2, 3])
        self.assertEqual(row["received_not_used"], [unused["cell_id"]])
        low, high = row["used"]["exact_95"]
        self.assertLess(low, 0.5)
        self.assertGreater(high, 0.5)

    def test_wordings_are_compared_task_by_task(self):
        cells = [cell("board-letter", reversed_used, f"{index:02d}") for index in range(1, 7)]
        cells += [cell("board-purpose", asked_only, f"{index:02d}") for index in range(1, 7)]
        comparison = funnel.funnel(cells, headlines={}, proposals={})["wording"]["gpt-5.6-sol"]["used"]
        self.assertEqual((comparison["pairs"], comparison["letter_only"], comparison["purpose_only"]), (6, 6, 0))
        self.assertAlmostEqual(comparison["paired_exact_p"], 0.03125)


if __name__ == "__main__":
    unittest.main()
