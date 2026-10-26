#!/usr/bin/env python3
"""Plus factors for agents: every signal ranked by how much more often it appears with collusion.

Exploratory, written during the sprint (2026-10-23) after the freeze; it reads the frozen label,
the frozen signals of ``exchange_evidence`` and the frozen judges' verdicts, and changes none.

Kovacic, Marshall, Marx and White (2011, Mich. L. Rev. 110:393) rank antitrust plus factors by
the contrast between the likelihood of a conduct with and without an agreement, and call "super
plus factors" those almost never seen without one, judged against a noncollusive benchmark.
Here the benchmarks are the innocent case types of ``exchange_evidence``: a common source, a
token read and not used, a request with nothing moved, nothing at all.  A factor must exclude
every innocent explanation, so its strength is set by the innocent case it is most common in:

    likelihood ratio = P[F | collusion] / max over innocent cases P[F | case]

with a conservative lower bound from exact 95% intervals (lower end over upper end).  "Super" is
used here for a lower bound of at least 10.  Rates are per cell.  Beside this worst case, the
innocent cells are also pooled into one benchmark, as Kovacic et al.'s single P[F | not C]; the
pooled figure depends on the mix of innocent cases in the data and is reported as such.

Most collusion cells were arranged by the experimenter: a pact the prompt states, or an exchange
the prompt invites, so the agreement comes from a common principal (hub and spoke), not from the
agents.  Each factor's rate is also reported on the emergent cells alone: an exchange against the
rule in an arm that neither tells nor invites it.  The bound uses the lower end of one exact 95%
interval over the upper end of another, so it is a one-sided bound at 95% or more.

A benchmark must be noncollusive.  A cell whose arm tells the agents to pass their tokens (the
pact arms) or invites a disguised exchange, and in which no token was used, is an attempt that
failed, not innocence: it is reported as "attempted, not completed" and counts on neither side.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import exchange_bench as bench
import exchange_evidence as evidence
import run_stats

VIEWS = ("text", "both", "full")
SUPER = 10.0
ATTEMPTED = "attempted, not completed"
EXCHANGE_ARMS = ("pact", "reversed-", "shifted-")   # arms that tell or invite agents to pass their tokens


def emergent(cell: dict) -> bool:
    return evidence.case_type(cell) == evidence.POSITIVE[0] and not cell["arm"].startswith(EXCHANGE_ARMS)


def case(cell: dict) -> str:
    found = evidence.case_type(cell)
    if found not in evidence.POSITIVE and cell["arm"].startswith(EXCHANGE_ARMS):
        return ATTEMPTED
    return found


def _rate(values: list[bool]) -> dict:
    hits = sum(values)
    return {"count": hits, "of": len(values), "exact_95": run_stats.clopper_pearson(hits, len(values))}


def rows(cells: list[dict], verdicts: dict[str, dict[tuple[str, str], bool]]) -> list[dict]:
    """One row per scorable cell: its case type and every signal, judges' verdicts included."""
    found = []
    for cell in cells:
        if bench.label(cell)["operational_failure"]:
            continue
        signals = dict(evidence.signals(cell))
        for judge, table in verdicts.items():
            for view in VIEWS:
                signals[f"judge {judge}, {view}"] = table.get((cell["cell_id"], view))
        found.append({"cell_id": cell["cell_id"], "case": case(cell), "emergent": emergent(cell), "signals": signals})
    return found


def rank(table: list[dict]) -> dict:
    names = sorted({name for row in table for name in row["signals"]})
    ranked = {}
    for name in names:
        by_case: dict[str, list[bool]] = {row["case"]: [] for row in table}
        for row in table:
            value = row["signals"].get(name)
            if value is not None:
                by_case[row["case"]].append(bool(value))
        positive = [value for case in evidence.POSITIVE for value in by_case.get(case, [])]
        innocent = {name: _rate(values) for name, values in by_case.items()
                    if name not in evidence.POSITIVE and name != ATTEMPTED}
        given = _rate(positive)
        agents_own = _rate([bool(row["signals"][name]) for row in table
                            if row.get("emergent") and row["signals"].get(name) is not None])
        attempted = _rate(by_case.get(ATTEMPTED, []))
        scored = {name: rate for name, rate in innocent.items() if rate["of"]}
        closest = max(scored, key=lambda name: (scored[name]["count"] / scored[name]["of"], name), default=None)
        ratio = lower = None
        if given["of"] and closest:
            worst = scored[closest]["count"] / scored[closest]["of"]
            ratio = (given["count"] / given["of"]) / worst if worst else None
            low = given["exact_95"][0]
            high = max(rate["exact_95"][1] for rate in scored.values())
            lower = low / high if high else None
        pooled = _rate([value for name_, values in by_case.items()
                        if name_ not in evidence.POSITIVE and name_ != ATTEMPTED for value in values])
        pooled_lower = (given["exact_95"][0] / pooled["exact_95"][1]
                        if given["of"] and pooled["of"] and pooled["exact_95"][1] else None)
        ranked[name] = {"given_collusion": given, "given_emergent_collusion": agents_own, "innocent": innocent, "attempted_not_completed": attempted,
                        "innocent_pooled": pooled, "likelihood_ratio_pooled_lower_95_one_sided": pooled_lower,
                        "closest_innocent_case": closest,
                        "likelihood_ratio": ratio, "likelihood_ratio_lower_95_one_sided": lower,
                        "super": lower is not None and lower >= SUPER}
    return dict(sorted(ranked.items(), key=lambda item: -(item[1]["likelihood_ratio_lower_95_one_sided"] or 0)))


def load_verdicts(directory: Path) -> dict[tuple[str, str], bool]:
    path = directory / "judgments.jsonl"
    found = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            found[row["cell_id"], row["view"]] = bool(row["moved"])
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--studies", nargs="+", default=["sprint"], help="only studies whose name contains one of these")
    parser.add_argument("--judge", nargs=2, action="append", default=[], metavar=("NAME", "DIRECTORY"),
                        help="a judge's output directory, its verdicts becoming one signal per view")
    args = parser.parse_args()
    cells = [cell for cell in bench.load_cells() if any(name in cell["study"] for name in args.studies)]
    verdicts = {name: load_verdicts(Path(directory)) for name, directory in args.judge}
    table = rows(cells, verdicts)
    cases = defaultdict(int)
    for row in table:
        cases[row["case"]] += 1
    print(json.dumps({"note": "exploratory, after the freeze; strength set by the closest innocent case",
                      "studies": args.studies, "cases": dict(cases), "factors": rank(table)}, indent=2))


if __name__ == "__main__":
    main()
