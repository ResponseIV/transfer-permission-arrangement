import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import posterior_table as posterior  # noqa: E402


class Posterior(unittest.TestCase):
    def test_bayes_turns_a_likelihood_ratio_and_a_prior_into_a_posterior(self):
        self.assertAlmostEqual(posterior.posterior(1.0, 0.01), 0.01)
        self.assertAlmostEqual(posterior.posterior(99.0, 0.01), 0.5)
        self.assertIsNone(posterior.posterior(None, 0.01))

    def test_table_reads_the_plus_factor_output(self):
        factors = {"uptake": {"likelihood_ratio": None, "likelihood_ratio_lower_95_one_sided": 2.5,
                              "likelihood_ratio_pooled_lower_95_one_sided": 156.7,
                              "given_collusion": {"of": 704}, "innocent": {"nothing moved": {"of": 219}}}}
        row = posterior.table(factors, priors=(0.01,))["uptake"]
        self.assertEqual(row["ratio_status"], "unbounded")
        self.assertIsNone(row["0.01"]["point"])
        self.assertAlmostEqual(row["0.01"]["worst_benchmark_bound"], 2.5 * 0.01 / (2.5 * 0.01 + 0.99))
        self.assertGreater(row["0.01"]["pooled_bound"], 0.6)

    def test_missing_data_gives_no_posterior_rather_than_certainty(self):
        factors = {"f": {"likelihood_ratio": None, "likelihood_ratio_lower_95_one_sided": None,
                         "likelihood_ratio_pooled_lower_95_one_sided": None,
                         "given_collusion": {"of": 0}, "innocent": {"nothing moved": {"of": 0}}}}
        row = posterior.table(factors, priors=(0.01,))["f"]
        self.assertEqual(row["ratio_status"], "missing")
        self.assertEqual(row["0.01"], {"point": None, "worst_benchmark_bound": None, "pooled_bound": None})


if __name__ == "__main__":
    unittest.main()
