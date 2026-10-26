#!/opt/miniconda3/bin/python3
"""Offline exact uncertainty statistics for v2/v3 page-artifact runs."""

from __future__ import annotations

import argparse
import json
import math
from itertools import combinations
from pathlib import Path


WARNING = (
    "The two agents in a cell are not independent. Agent-level intervals and "
    "Fisher tests assume independent observations and should be interpreted "
    "with caution; use the cell-level results for comparisons between arms. "
    "Cell-level inference also assumes independent cells. Fisher p-values are "
    "two-sided and unadjusted for multiple comparisons."
)


def _check_counts(successes: int, total: int) -> None:
    if not isinstance(successes, int) or not isinstance(total, int):
        raise ValueError("Counts must be integers")
    if not 0 <= successes <= total:
        raise ValueError("Counts must satisfy 0 <= successes <= total")


def beta_quantile(probability: float, a: int, b: int) -> float:
    """Invert I_p(a,b) = P[Binomial(a+b-1,p) >= a] by bisection.

    Integer beta shapes suffice for Clopper-Pearson. Log probabilities avoid
    overflowing large binomial coefficients or underflowing intermediate powers.
    """
    if a < 1 or b < 1 or not 0 <= probability <= 1:
        raise ValueError("Positive integer shapes and probability in [0,1] required")
    if probability in (0, 1):
        return float(probability)
    n = a + b - 1
    coefficients = [(k, math.log(math.comb(n, k))) for k in range(a, n + 1)]
    low, high = 0.0, 1.0
    for _ in range(80):
        p = (low + high) / 2
        if p == low or p == high:
            break
        tail = math.fsum(
            math.exp(coefficient + k * math.log(p) + (n - k) * math.log1p(-p))
            for k, coefficient in coefficients
        )
        if tail < probability:
            low = p
        else:
            high = p
    return (low + high) / 2


def clopper_pearson(successes: int, total: int) -> tuple[float, float] | None:
    """Equal-tailed exact 95% interval; no estimate for an empty denominator."""
    _check_counts(successes, total)
    if total == 0:
        return None
    lower = 0.0 if successes == 0 else beta_quantile(0.025, successes, total - successes + 1)
    # Beta symmetry keeps both inversions in the small tail.
    upper = 1.0 if successes == total else 1 - beta_quantile(0.025, total - successes, successes + 1)
    return lower, upper


def fisher_exact(k1: int, n1: int, k2: int, n2: int) -> float | None:
    """Sum fixed-margin hypergeometric tables at least as unlikely as observed.

    Integer weights share a common denominator, so comparisons (including ties)
    and summation are exact until the final conversion to a float.
    """
    _check_counts(k1, n1)
    _check_counts(k2, n2)
    if not n1 or not n2:
        return None
    successes = k1 + k2
    observed = math.comb(n1, k1) * math.comb(n2, k2)
    weight = 0
    for k in range(max(0, successes - n2), min(n1, successes) + 1):
        candidate = math.comb(n1, k) * math.comb(n2, successes - k)
        if candidate <= observed:
            weight += candidate
    return weight / math.comb(n1 + n2, successes)


def proportion(successes: int, total: int, unit: str, denominator: str) -> dict:
    return {
        "unit": unit,
        "denominator_description": denominator,
        "numerator": successes,
        "denominator": total,
        "proportion": successes / total if total else None,
        "clopper_pearson_95": clopper_pearson(successes, total),
    }


def report(run_dir: Path) -> dict:
    cells = [json.loads(line) for line in (run_dir / "cells.jsonl").read_text(encoding="utf-8").splitlines()
             if line.strip()]
    if not cells:
        raise ValueError("cells.jsonl is empty; cannot detect the run format")
    formats = {"v3" if "agents" in cell and "arm" in cell else "v2"
               if "information_uptake" in cell and "answer_submitted" in cell else "unknown"
               for cell in cells}
    if len(formats) != 1 or "unknown" in formats:
        raise ValueError("Unsupported or mixed cell formats")
    version = formats.pop()
    group_key = "arm" if version == "v3" else "condition"
    groups = {}
    for name in sorted({cell[group_key] for cell in cells}):
        done = [cell for cell in cells if cell[group_key] == name and not cell["operational_failure"]]
        measures = {}
        if version == "v3":
            agents = [agent for cell in done for agent in cell["agents"]]
            predicates = {
                "denied_retrying": lambda agent: bool(agent["access_denied"]) and agent["retries_after_denial"] > 0,
                "correct": lambda agent: agent["outcome"] == "correct",
                "no_answer": lambda agent: agent["outcome"] == "no_answer",
                "using_archive": lambda agent: agent["archive_reads"] > 0,
            }
            for metric, predicate in predicates.items():
                eligible = [a for a in agents if a["access_denied"]] if metric == "denied_retrying" else agents
                measures[f"agents_{metric}"] = proportion(
                    sum(predicate(a) for a in eligible), len(eligible), "agent",
                    "denied agents in completed cells" if metric == "denied_retrying" else "agents in completed cells",
                )
                measures[f"cells_any_{metric}"] = proportion(
                    sum(any(predicate(a) for a in cell["agents"]) for cell in done),
                    len(done), "cell", "all completed cells (any agent meets the condition)",
                )
            alphas = []
            for cell in done:
                alpha = [a for a in cell["agents"] if a["agent"] == "alpha"]
                if len(alpha) != 1:
                    raise ValueError("Each completed v3 cell must contain exactly one alpha")
                alphas.append(alpha[0])
            measures["alpha_correct"] = proportion(
                sum(a["outcome"] == "correct" for a in alphas), len(done), "cell", "all completed cells",
            )
        else:
            for metric in ("information_uptake", "answer_submitted"):
                measures[metric] = proportion(
                    sum(cell[metric] is True for cell in done), len(done), "cell", "all completed cells",
                )
        groups[name] = measures
    comparisons = []
    for left, right in combinations(groups, 2):
        for metric, first in groups[left].items():
            second = groups[right][metric]
            comparisons.append({
                "groups": [left, right], "measure": metric, "unit": first["unit"],
                "counts": [[first["numerator"], first["denominator"]],
                           [second["numerator"], second["denominator"]]],
                "fisher_two_sided_p": fisher_exact(first["numerator"], first["denominator"],
                                                   second["numerator"], second["denominator"]),
            })
    return {
        "format": version, "group_by": group_key, "warning": WARNING,
        "excluded_operational_failures": {"unit": "cell", "count": sum(bool(c["operational_failure"]) for c in cells)},
        "groups": groups, "comparisons": comparisons,
    }


def render_text(result: dict) -> str:
    excluded = result["excluded_operational_failures"]["count"]
    lines = [f"Format: {result['format']}; excluded operational failures: {excluded} (unit: cell)",
             f"WARNING: {result['warning']}"]
    for name, measures in result["groups"].items():
        lines.append(f"\n{name}:")
        for metric, stats in measures.items():
            interval = stats["clopper_pearson_95"]
            estimate = (f"{stats['proportion']:.6f}; exact 95% CI [{interval[0]:.6f}, {interval[1]:.6f}]"
                        if interval is not None else "undefined; exact 95% CI undefined")
            lines.append(f"  {metric} (unit: {stats['unit']}): {stats['numerator']}/{stats['denominator']} "
                         f"= {estimate}; denominator: {stats['denominator_description']}")
    lines.append("\nPairwise two-sided Fisher exact tests (unadjusted):")
    for comparison in result["comparisons"]:
        left, right = comparison["groups"]
        (k1, n1), (k2, n2) = comparison["counts"]
        p = comparison["fisher_two_sided_p"]
        value = f"{p:.12g}" if p is not None else "undefined (empty denominator)"
        lines.append(f"  {left} vs {right}: {comparison['measure']} (unit: {comparison['unit']}), "
                     f"{k1}/{n1} vs {k2}/{n2}; p={value}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, metavar="RUN_DIR")
    parser.add_argument("--json", action="store_true", help="Print structured counts, intervals and tests")
    args = parser.parse_args()
    try:
        result = report(args.run_dir)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, allow_nan=False) if args.json else render_text(result))


if __name__ == "__main__":
    main()
