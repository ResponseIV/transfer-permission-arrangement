#!/usr/bin/env python3
"""What an auditor may conclude from one plus factor: P[collusion | factor] at a stated prior.

Kovacic et al. (2011, Mich. L. Rev. 110:427) write the inference as Bayes' theorem: the posterior
depends on the factor's likelihood ratio and on the baseline probability of collusion, which no
experiment supplies.  This reads `plus_factors.py` output and, for a few priors, gives the posterior
at the point ratio and at its two one-sided 95% lower bounds (the worst benchmark: the collusion lower end over the largest innocent upper end; and
against the pooled innocent cells).  Written during the sprint, 2026-10-23, after the analysis freeze;
it reads the frozen tool's output and changes nothing in it.
"""

import argparse
import json
from pathlib import Path

PRIORS = (0.01, 0.05, 0.2)


def posterior(ratio: float | None, prior: float) -> float | None:
    """No posterior without a finite ratio: a ratio that is missing, or unbounded because the factor
    was never seen without collusion, gives None, and the bounds carry the inference."""
    if ratio is None:
        return None
    odds = ratio * prior / (1 - prior)
    return odds / (1 + odds)


def status(factor: dict) -> str:
    """Why a point ratio is absent: no data on one side, or no innocent cell with the factor."""
    innocent = [rate for rate in factor["innocent"].values() if rate["of"]]
    if not factor["given_collusion"]["of"] or not innocent:
        return "missing"
    return "unbounded" if factor["likelihood_ratio"] is None else "finite"


def table(factors: dict, priors: tuple[float, ...] = PRIORS) -> dict:
    found = {}
    for name, factor in factors.items():
        closest = factor["likelihood_ratio_lower_95_one_sided"]
        pooled = factor["likelihood_ratio_pooled_lower_95_one_sided"]
        found[name] = {"ratio_status": status(factor), **{str(prior): {
            "point": posterior(factor["likelihood_ratio"], prior),
            "worst_benchmark_bound": None if closest is None else posterior(closest, prior),
            "pooled_bound": None if pooled is None else posterior(pooled, prior)} for prior in priors}}
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plus_factors", type=Path, help="output of plus_factors.py")
    args = parser.parse_args()
    factors = json.loads(args.plus_factors.read_text(encoding="utf-8"))["factors"]
    print(json.dumps({"priors": PRIORS, "note": "the prior is the auditor's, not measured here",
                      "posteriors": table(factors)}, indent=2))


if __name__ == "__main__":
    main()
