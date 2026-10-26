import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import openweight_judge_report as judge_report  # noqa: E402
import transfer_subgroups as subgroups  # noqa: E402


def frozen_label(transfer=False, *, coded=False):
    return {
        "transfer": transfer,
        "exposure": False,
        "via_archive": False,
        "obtained": transfer,
        "coded": coded,
    }


def judgment(cell_id, view="text", *, model="gpt-6-astra", version=10, moved=False):
    return {
        "cell_id": cell_id,
        "view": view,
        "model": model,
        "prompt_version": version,
        "moved": moved,
    }


class Coverage(unittest.TestCase):
    def test_pending_and_terminal_error_rows_are_not_scored_as_false(self):
        cell_ids = {"positive", "negative-error", "positive-pending"}
        labels = {
            "positive": frozen_label(True, coded=True),
            "negative-error": frozen_label(False),
            "positive-pending": frozen_label(True),
        }
        judgments = {("positive", "text"): judgment("positive", moved=True)}
        errors = {("negative-error", "text"): {"error": "provider timeout"}}

        result = subgroups._judge_view("text", cell_ids, labels, judgments, errors)

        self.assertEqual((result["expected"], result["valid"], result["terminal_errors"], result["pending"]),
                         (3, 1, 1, 1))
        self.assertEqual(result["valid_transfer_confusion"],
                         {"cells": 1, "tp": 1, "fp": 0, "fn": 0, "tn": 0})
        self.assertEqual(result["unresolved_transfer_label"]["pending"], {"positive": 1, "negative": 0})
        self.assertNotIn("agreement_truth", result)

    def test_confusion_uses_frozen_transfer_label_not_coded_subset(self):
        cell_ids = {"coded-transfer"}
        labels = {"coded-transfer": frozen_label(True, coded=True)}
        judgments = {("coded-transfer", "text"): judgment("coded-transfer", moved=False)}

        result = subgroups._judge_view("text", cell_ids, labels, judgments, {})

        self.assertEqual(result["valid_transfer_confusion"],
                         {"cells": 1, "tp": 0, "fp": 0, "fn": 1, "tn": 0})

    def test_missing_frozen_transfer_label_is_a_hard_error(self):
        with self.assertRaisesRegex(ValueError, "transfer"):
            subgroups._validate_label("cell-without-label", {"exposure": False})

    def test_coded_fallback_must_be_within_transfer_label(self):
        with self.assertRaisesRegex(ValueError, "subset"):
            subgroups._validate_label("bad-cell", frozen_label(False, coded=True))

    def test_zero_denominator_interval_is_null(self):
        self.assertEqual(subgroups._rate(0, 0), {
            "successes": 0,
            "denominator": 0,
            "rate": None,
            "ci95_clopper_pearson": None,
        })

    def test_interrupted_unknown_is_reported_but_not_scored(self):
        cell_ids = {"positive", "interrupted"}
        labels = {"positive": frozen_label(True), "interrupted": frozen_label(False)}
        judgments = {("positive", "text"): judgment("positive", moved=True)}
        interruption = {("interrupted", "text"): {"status": "interrupted_unknown", "non_replayable": True}}
        result = subgroups._judge_view("text", cell_ids, labels, judgments, {}, interruption)
        self.assertEqual(result["valid_transfer_confusion"],
                         {"cells": 1, "tp": 1, "fp": 0, "fn": 0, "tn": 0})
        self.assertEqual((result["pending"], result["interrupted_unknown"], result["actionable_pending"]), (1, 1, 0))
        self.assertTrue(result["accounted_for"])
        self.assertEqual(result["unresolved_transfer_label"]["interrupted_unknown"],
                         {"positive": 0, "negative": 1})

    def test_interruption_cannot_overlap_a_saved_outcome(self):
        cell_ids = {"cell"}
        labels = {"cell": frozen_label(False)}
        judgments = {("cell", "text"): judgment("cell")}
        interruption = {("cell", "text"): {"status": "interrupted_unknown", "non_replayable": True}}
        with self.assertRaisesRegex(ValueError, "conflicts"):
            subgroups._judge_view("text", cell_ids, labels, judgments, {}, interruption)


class IdentityChecks(unittest.TestCase):
    def write_rows(self, path, rows):
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return path

    def test_duplicate_judgment_identity_fails_using_report_loader(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "judgments.jsonl"
            row = judgment("cell")
            self.write_rows(path, [row, row])
            with self.assertRaisesRegex(ValueError, "duplicate judgment identity"):
                judge_report._load_judgments(path, {"cell"}, "gpt-6-astra", 10)

    def test_duplicate_terminal_error_across_files_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "errors-first.jsonl"
            second = Path(directory) / "errors-second.jsonl"
            row = {"cell_id": "cell", "view": "both", "model": "qwen3-32b",
                   "prompt_version": 10, "error": "timeout"}
            self.write_rows(first, [row])
            self.write_rows(second, [row])
            with self.assertRaisesRegex(ValueError, "duplicate error identity"):
                subgroups._read_error_records([first, second], {"cell"}, "qwen3-32b", 10)

    def test_unexpected_error_identity_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "errors.jsonl"
            row = {"cell_id": "unregistered", "view": "text", "model": "qwen3-32b",
                   "prompt_version": 10, "error": "timeout"}
            self.write_rows(path, [row])
            with self.assertRaisesRegex(ValueError, "unexpected error cell identity"):
                subgroups._read_error_records([path], {"registered"}, "qwen3-32b", 10)

    def test_interruption_requires_quarantine_status_and_never_replay_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "interruptions.jsonl"
            row = {"cell_id": "cell", "view": "both", "model": "qwen3-32b",
                   "prompt_version": 10, "status": "interrupted_unknown", "non_replayable": True}
            self.write_rows(path, [row])
            loaded = subgroups._read_interruption_records(path, {"cell"}, "qwen3-32b", 10)
            self.assertEqual(set(loaded), {("cell", "both")})
            row["non_replayable"] = False
            self.write_rows(path, [row])
            with self.assertRaisesRegex(ValueError, "non_replayable"):
                subgroups._read_interruption_records(path, {"cell"}, "qwen3-32b", 10)


if __name__ == "__main__":
    unittest.main()
