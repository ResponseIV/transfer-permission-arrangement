import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sprint_protocol as protocol  # noqa: E402


class Arithmetic(unittest.TestCase):
    def test_holm_multiplies_by_the_rank_and_never_decreases(self):
        result = protocol.holm({"a": 0.01, "b": 0.02, "c": 0.04})
        self.assertAlmostEqual(result["a"]["holm_p"], 0.03)
        self.assertAlmostEqual(result["b"]["holm_p"], 0.04)
        self.assertAlmostEqual(result["c"]["holm_p"], 0.04)
        self.assertTrue(result["c"]["survives_0.05"])

    def test_kappa_is_one_for_perfect_agreement_and_zero_at_chance(self):
        self.assertEqual(protocol.kappa([(True, True), (False, False)]), 1.0)
        self.assertAlmostEqual(protocol.kappa([(True, True), (True, False), (False, True), (False, False)]), 0.0)

    def test_an_alarm_is_mostly_false_when_transfers_are_rare(self):
        self.assertAlmostEqual(protocol.ppv(1.0, 0.0437, 0.01), 0.1878, places=3)
        self.assertEqual(protocol.ppv(1.0, 0.0, 0.01), 1.0)


if __name__ == "__main__":
    unittest.main()
