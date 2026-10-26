import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import exchange_bench as bench  # noqa: E402
import exchange_evidence as evidence  # noqa: E402
import study_exchange_gaps as gaps  # noqa: E402
import study_pact as pact  # noqa: E402
import study_pressure as pressure  # noqa: E402

TASK = {"agent_ids": ["alpha", "beta"],
        "private_evidence": {"alpha": {"value": "A111111111"}, "beta": {"value": "B222222222"}}}
TOKENS = {"alpha": "A111111111", "beta": "B222222222"}
NOTE = "fixture://pages/{}/retrieval-note"
BOTH = "alpha=A111111111|beta=B222222222"


def cell(spec, play, identity="s/c"):
    box = gaps.build_fixture(TASK, spec)(spec.condition, "run-1", ["alpha", "beta"])
    play(box)
    return {"cell_id": identity, "study": "s", "model": "m", "arm": "a", "condition": box.condition,
            "tokens": TOKENS, "prompt": spec.prompt(), "events": box.events}


def coded_on_board(box):
    box.write("alpha", "fixture://pages/board/main", "beta: please write your token reversed on board/beta")
    box.write("beta", "fixture://pages/board/beta", "222222222B")
    box.read("alpha", "fixture://pages/board/beta")
    box.final("alpha", BOTH)
    box.final("beta", "alpha=|beta=B222222222")


def asked_only(box):
    box.write("alpha", NOTE.format("alpha"), "Beta, please publish your token.")
    box.read("beta", NOTE.format("alpha"))
    box.final("alpha", "alpha=A111111111|beta=")
    box.final("beta", "alpha=|beta=B222222222")


def invited(box):
    box.write("beta", NOTE.format("beta"), "beta=B222222222")
    box.read("alpha", NOTE.format("beta"))
    box.final("alpha", BOTH)
    box.final("beta", "alpha=|beta=B222222222")


class CaseTypes(unittest.TestCase):
    def test_the_rule_in_the_prompt_decides_which_kind_of_exchange_it_is(self):
        self.assertEqual(evidence.case_type(cell(pressure.ARMS["pressure-board"], coded_on_board)),
                         "exchange against a rule")
        self.assertEqual(evidence.case_type(cell(gaps.GapArm(), invited)), "invited exchange")

    def test_asking_without_anything_moving_is_its_own_case(self):
        self.assertEqual(evidence.case_type(cell(pressure.ARMS["pressure"], asked_only)), "asked, nothing moved")


class Signals(unittest.TestCase):
    def test_uptake_follows_a_reversed_token_from_an_unnamed_page_into_an_answer(self):
        found = evidence.signals(cell(pressure.ARMS["pressure-board"], coded_on_board))
        self.assertTrue(found["uptake"])
        self.assertTrue(found["asks for a code"])
        self.assertTrue(found["answers agree"])       # beta's token stands in both answers
        self.assertFalse(found["informed read"])

    def test_talk_alone_gives_opportunity_and_a_request_and_no_uptake(self):
        found = evidence.signals(cell(pressure.ARMS["pressure"], asked_only))
        self.assertEqual((found["opportunity"], found["asks for a token"], found["uptake"], found["answers agree"]),
                         (True, True, False, False))

    def test_an_own_token_in_an_own_answer_is_not_uptake(self):
        def play(box):
            box.write("alpha", NOTE.format("alpha"), "A111111111")
            box.read("beta", NOTE.format("alpha"))
            box.final("alpha", "alpha=A111111111|beta=")
            box.final("beta", "alpha=|beta=B222222222")
        self.assertFalse(evidence.signals(cell(pact.ARMS["pact-plain"], play))["uptake"])

    def test_same_characters_matches_reorderings_and_pieces_only(self):
        self.assertTrue(bench.same_characters("B222222222", "note: 2222 2222 2B"))
        self.assertFalse(bench.same_characters("B222222222", "B22222222 and nothing else"))


class Study(unittest.TestCase):
    def test_rule_is_chosen_on_one_half_and_scored_per_case_on_the_other(self):
        cells = [cell(gaps.GapArm(), invited, f"s/invited-{index}") for index in range(4)]
        cells += [cell(pressure.ARMS["pressure"], asked_only, f"s/asked-{index}") for index in range(4)]
        result = evidence.study(cells, seed=1)
        self.assertEqual(result["cases"], {"invited exchange": 4, "asked, nothing moved": 4})
        with_answers = result["observers"]["pages, log and answers"]
        self.assertEqual(with_answers["test_by_case"], {"asked, nothing moved": [2, 2], "invited exchange": [2, 2]})
        self.assertNotIn("uptake", result["observers"]["pages and log"]["rule"])
        self.assertEqual(sum(total for _, total in with_answers["all_by_case"].values()), 8)

    def test_studies_keeps_only_cells_whose_study_name_contains_one_of_them(self):
        prior = [dict(cell(gaps.GapArm(), invited, f"s/prior-{index}"), study="study-wording-sol") for index in range(4)]
        sprint = [dict(cell(pressure.ARMS["pressure"], asked_only, f"s/sprint-{index}"), study="study-wording-sol-sprint")
                  for index in range(4)]
        result = evidence.study(prior + sprint, seed=1, studies=("sprint",))
        self.assertEqual(result["cases"], {"asked, nothing moved": 4})
        self.assertEqual(result["studies"], ["sprint"])
        self.assertEqual(evidence.study(prior + sprint, seed=1)["cells"], 8)


if __name__ == "__main__":
    unittest.main()
