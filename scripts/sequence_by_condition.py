#!/usr/bin/env python3
"""The offer-and-reply sequence scored as a detector on every condition (post hoc, 2026-10-25).

For each condition: episodes, completed transfers, agent-arranged transfers (``plus_factors.emergent``),
and two counts from ``audit_cell``: the raw sequence on the pages (a page with code language followed by
a carrier from the other side), and the agent-made candidate, which also reads the instructions and
discounts an exchange the instructions prescribe. The raw count is the test against scripted exchanges.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import audit_cell as audit
import exchange_bench as bench
import plus_factors as plus

ROOT = Path(__file__).resolve().parents[1]
STUDIES = ("sprint", "step6", "agreed", "replication", "qwen-openweight")   # the report's 646-episode cohort and the leak arms


def condition(cell: dict) -> str:
    arm, study = cell["arm"], cell["study"]
    if "step6" in study:
        return "Sol follow-up (letter rule)"
    if "qwen-letter" in study:
        return "Qwen, letter rule"
    if arm in ("board-letter", "board-purpose"):
        return "Rule arms, no supplied scheme"
    if arm == "pact-board-coded":
        return "Instructed pact"
    if arm == "reversed-agreed-board":
        return "No-rule counterpart (scripted)"
    if arm.startswith(("reversed-", "shifted-")):
        return "Authorized conventions (scripted)"
    if arm == "private-exit-archive":
        return "Common source (archive)"
    if arm == "scripted-offer-board":
        return "Scripted offer (no rule)"
    if arm == "leak-letter":
        return "Planted leak"
    return arm


def table(cells: list[dict]) -> dict:
    rows = defaultdict(lambda: dict.fromkeys(("episodes", "transfers", "agent_made", "raw_sequence",
                                              "raw_sequence_on_agent_made", "candidate", "candidate_on_agent_made"), 0))
    for cell in cells:
        truth = bench.label(cell)
        if truth["operational_failure"]:
            continue
        result = audit.audit(cell, "full", instructions=True)["coordination"]
        raw, candidate, made = "evidence" in result, result["agent_made_candidate"], plus.emergent(cell)
        row = rows[condition(cell)]
        row["episodes"] += 1
        row["transfers"] += truth["transfer"]
        row["agent_made"] += made
        row["raw_sequence"] += raw
        row["raw_sequence_on_agent_made"] += raw and made
        row["candidate"] += candidate
        row["candidate_on_agent_made"] += candidate and made
    return dict(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--studies", nargs="+", default=list(STUDIES),
                        help="study name fragments; the default is the cohort, with the leak arms added")
    studies = parser.parse_args().studies
    cells = [cell for cell in bench.load_cells(ROOT / "data") if any(key in cell["study"] for key in studies)]
    if studies == list(STUDIES):
        cells += [cell for cell in bench.load_cells(ROOT / "data/posthoc") if "leak" in cell["study"]]
    print(json.dumps({"note": "post hoc; the leak counts as agent-made under plus_factors.emergent though nobody agreed",
                      "rows": table(cells)}, indent=2))


if __name__ == "__main__":
    main()
