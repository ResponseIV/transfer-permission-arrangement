import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import openweight_judge_report as report  # noqa: E402


def labels():
    return {
        "positive": {"transfer": True, "exposure": True},
        "read-only": {"transfer": False, "exposure": True},
        "pending": {"transfer": False, "exposure": False},
    }


def judgment(cell_id, view="both", *, model=report.MODEL, version=report.PROMPT_VERSION, moved=False):
    return {"cell_id": cell_id, "view": view, "model": model, "prompt_version": version,
            "moved": moved, "confidence": 0.8, "evidence": "fixture"}


class Coverage(unittest.TestCase):
    def test_interruption_is_unknown_and_never_a_negative_verdict(self):
        cells = labels()
        qwen = {("positive", "both"): judgment("positive", moved=True)}
        errors = {("read-only", "both"): {"error": "no valid verdict"}}
        interruptions = {("pending", "both"): {"status": "interrupted_unknown"}}
        result = report._view_report("both", cells, qwen, errors, {}, {}, interruptions)
        self.assertEqual(result['interrupted_unknown'], 1)
        self.assertEqual(result['actionable_pending'], 0)
        self.assertTrue(result['accounted_for'])
        self.assertFalse(result['completed'])
        self.assertEqual(result['transfer_confusion']['cells'], 1)
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            report._view_report("both", cells, qwen, errors, {}, {}, {("positive", "both"): {}})

    def test_denominators_separate_valid_errors_and_pending_without_scoring_gaps_as_no(self):
        cells = labels()
        qwen = {("positive", "both"): judgment("positive", moved=True)}
        errors = {("read-only", "both"): {"error": "no valid verdict"}}
        result = report._view_report("both", cells, qwen, errors, {}, {})

        self.assertEqual((result["expected"], result["valid"], result["terminal_errors"], result["pending"]),
                         (3, 1, 1, 1))
        self.assertFalse(result["completed"])
        self.assertEqual(result["transfer_confusion"], {"cells": 1, "tp": 1, "fp": 0, "fn": 0, "tn": 0})
        self.assertEqual(result["unresolved_labels"]["terminal_errors"]["transfer"],
                         {"positive": 0, "negative": 1})
        self.assertEqual(result["unresolved_labels"]["pending"]["transfer"],
                         {"positive": 0, "negative": 1})
        self.assertEqual(result["unresolved_labels"]["terminal_errors"]["receipt"],
                         {"positive": 1, "negative": 0})

    def test_receipt_follows_frozen_exposure_or_transfer_rule(self):
        result = report._view_report("both", labels(), {}, {}, {}, {})
        self.assertEqual(result["unresolved_labels"]["pending"]["receipt"],
                         {"positive": 2, "negative": 1})

    def test_common_judge_kappa_reports_pair_specific_denominator(self):
        cells = {"positive": labels()["positive"], "read-only": labels()["read-only"]}
        qwen = {("positive", "both"): judgment("positive", moved=True),
                ("read-only", "both"): judgment("read-only", moved=False)}
        astra = {("positive", "both"): judgment("positive", model="gpt-6-astra", version=10, moved=True)}
        luna = {("positive", "both"): judgment("positive", model="gpt-5.6-luna", version=9, moved=False),
                ("read-only", "both"): judgment("read-only", model="gpt-5.6-luna", version=9, moved=False)}
        result = report._view_report("both", cells, qwen, {}, astra, luna)
        self.assertEqual(result["kappa"]["against_astra_p10_common_ids"]["cells"], 1)
        self.assertEqual(result["kappa"]["against_luna_p9_common_ids"]["cells"], 2)


class StrictInputs(unittest.TestCase):
    def write_rows(self, path, rows):
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return path

    def test_duplicate_identity_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "judgments.jsonl"
            row = judgment("positive")
            self.write_rows(path, [row, row])
            with self.assertRaisesRegex(ValueError, "duplicate judgment identity"):
                report._load_judgments(path, {"positive"}, report.MODEL, report.PROMPT_VERSION)

    def test_wrong_prompt_version_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "judgments.jsonl"
            self.write_rows(path, [judgment("positive", version=9)])
            with self.assertRaisesRegex(ValueError, "prompt_version"):
                report._load_judgments(path, {"positive"}, report.MODEL, report.PROMPT_VERSION)

    def test_unexpected_identity_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "judgments.jsonl"
            self.write_rows(path, [judgment("unexpected")])
            with self.assertRaisesRegex(ValueError, "unexpected cell identity"):
                report._load_judgments(path, {"positive"}, report.MODEL, report.PROMPT_VERSION)


class Predictions(unittest.TestCase):
    def j4_dataset(self, reference_calls, qwen_calls):
        labels_by_id = {
            cell_id: {"transfer": bool(index % 2), "exposure": True}
            for index, cell_id in enumerate(reference_calls)
        }
        qwen_rows = {(cell_id, "both"): judgment(cell_id, moved=moved)
                     for cell_id, moved in qwen_calls.items()}
        astra_rows = {(cell_id, "both"): judgment(cell_id, model="gpt-6-astra", version=10, moved=moved)
                      for cell_id, moved in reference_calls.items()}
        errors = {(cell_id, "both"): {"error": "fixture missing verdict"}
                  for cell_id in reference_calls.keys() - qwen_calls.keys()}
        row = report._view_report("both", labels_by_id, qwen_rows, errors, astra_rows, {})
        return {"sprint": {"views": {"both": row, "text": row}},
                "leak": {"views": {"both": row}}}

    def test_j4_kappa_range_can_cross_registered_threshold(self):
        reference = {"p1": True, "p2": True, "n1": False, "n2": False}
        qwen = {"p1": True, "n1": False}
        score = report.prediction_scores(self.j4_dataset(reference, qwen))["J4"]
        self.assertEqual(score["status"], "indeterminate")
        self.assertEqual(score["kappa"], 1.0)
        self.assertEqual(score["paired_valid_cells"], 2)
        self.assertEqual(score["reference_denominator"], 4)
        self.assertEqual(score["reference_missing_verdicts"], 2)
        self.assertEqual(score["kappa_range"]["minimum"], 0.0)
        self.assertEqual(score["kappa_range"]["maximum"], 1.0)
        self.assertEqual(score["kappa_range"]["count_combinations_enumerated"], 4)

    def test_j4_held_only_when_every_missing_assignment_clears_threshold(self):
        reference = {**{f"p{i}": True for i in range(10)},
                     **{f"n{i}": False for i in range(10)}}
        qwen = {**{f"p{i}": True for i in range(9)},
                **{f"n{i}": False for i in range(9)}}
        score = report.prediction_scores(self.j4_dataset(reference, qwen))["J4"]
        self.assertEqual(score["status"], "held")
        self.assertAlmostEqual(score["kappa_range"]["minimum"], 0.8)
        self.assertEqual(score["kappa_range"]["maximum"], 1.0)

    def test_j4_wrong_only_when_every_missing_assignment_stays_below_threshold(self):
        reference = {**{f"p{i}": True for i in range(10)},
                     **{f"n{i}": False for i in range(10)}}
        qwen = {**{f"p{i}": True for i in range(6)},
                **{f"p{i}": False for i in range(6, 9)},
                **{f"n{i}": True for i in range(6)},
                **{f"n{i}": False for i in range(6, 9)}}
        score = report.prediction_scores(self.j4_dataset(reference, qwen))["J4"]
        self.assertEqual(score["status"], "wrong")
        self.assertLess(score["kappa_range"]["maximum"], 0.75)

    def test_quarantined_interruption_keeps_a_count_range(self):
        cells = {'saved': {'transfer': True, 'exposure': True},
                 'unknown': {'transfer': True, 'exposure': True}}
        qwen = {('saved', 'both'): judgment('saved', moved=True)}
        row = report._view_report('both', cells, qwen, {}, qwen, qwen,
                                  {('unknown', 'both'): {'status': 'interrupted_unknown'}})
        scores = report.prediction_scores({'sprint': {'views': {'both': row, 'text': row}},
                                           'leak': {'views': {'both': row}}})
        self.assertEqual(scores['J1']['range_with_unresolved'], (1, 2))
        self.assertEqual(scores['J1']['interrupted_unknown'], 1)
        self.assertNotEqual(scores['J1']['status'], 'pending')

    def dataset(self, terminal=False, pending=False):
        cells = {str(i): {'transfer': True, 'exposure': True} for i in range(244)}
        qwen = {(identity, 'both'): judgment(identity, moved=int(identity) < 229)
                for identity in cells if not (terminal or pending) or int(identity) < 242}
        errors = {(str(i), 'both'): {} for i in (242, 243)} if terminal else {}
        row = report._view_report('both', cells, qwen, errors, qwen, qwen)
        return {'sprint': {'views': {'both': row, 'text': row}}, 'leak': {'views': {'both': row}}}

    def test_terminal_failures_can_make_threshold_score_indeterminate(self):
        result = report.prediction_scores(self.dataset(terminal=True))
        self.assertEqual(result['J1']['status'], 'indeterminate')
        self.assertEqual(result['J1']['range_with_unresolved'], (229, 231))
        self.assertEqual(result['K1']['status'], 'held')

    def test_unattempted_cells_keep_numeric_scores_pending(self):
        result = report.prediction_scores(self.dataset(pending=True))
        self.assertEqual(result['J1']['status'], 'pending')
        self.assertEqual(result['K1']['status'], 'pending')
        self.assertEqual(result['J4']['status'], 'pending')
        self.assertEqual(result['K4']['status'], 'pending')

    def test_most_agreement_uses_full_expected_denominator(self):
        datasets = self.dataset(terminal=True)
        row = datasets['sprint']['views']['both']
        row['kappa']['against_astra_p10_common_ids']['agree'] = 121
        self.assertEqual(report.prediction_scores(datasets)['K4']['status'], 'indeterminate')
        row['kappa']['against_astra_p10_common_ids']['agree'] = 123
        self.assertEqual(report.prediction_scores(datasets)['K4']['status'], 'held')

if __name__ == "__main__":
    unittest.main()
