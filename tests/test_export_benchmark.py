import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import export_benchmark as export  # noqa: E402
from test_sprint_funnel import cell, reversed_used  # noqa: E402


class Record(unittest.TestCase):
    def test_openweight_verdicts_are_exported_from_main_and_posthoc_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder, identity in (("exchange-judge-qwen-p10-sprint", "sprint/cell"),
                                     ("posthoc/exchange-judge-qwen-p10-leak", "leak/cell")):
                path = root / "data" / folder / "judgments.jsonl"
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps({"cell_id": identity, "view": "both", "moved": True}) + "\n")
            with patch.object(export, "ROOT", root):
                result = export.verdicts()
            self.assertEqual(result, {identity: {"qwen-p10": {"both": True}}
                                      for identity in ("sprint/cell", "leak/cell")})

    def test_a_cell_carries_its_ground_truth_case_signals_and_judges(self):
        sample = cell("board-letter", reversed_used, "01")
        row = export.record(sample, False, {sample["cell_id"]: {"astra-p10": {"both": True}}})
        self.assertEqual((row["origin"], row["case"], row["label"]["transfer"]), ("sprint", "exchange against a rule", True))
        self.assertTrue(row["rule_in_prompt"])
        self.assertIn("uptake", row["signals"])
        self.assertEqual(row["judges"], {"astra-p10": {"both": True}})

    def test_post_hoc_and_prior_cells_are_marked(self):
        self.assertEqual(export.origin("study-pact-agreed-luna", False), "post hoc")
        self.assertEqual(export.origin("study-wording-leak-luna-negligent", True), "post hoc")
        self.assertEqual(export.origin("study-pact-sol-pilot", False), "prior work")


if __name__ == "__main__":
    unittest.main()
