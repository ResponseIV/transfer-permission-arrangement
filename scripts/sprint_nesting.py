#!/usr/bin/env python3
"""Check that the sprint plus-factor counts nest inside the all-cells counts from the same run.

Asked by the report session, 2026-10-24: every number in the report comes from one
``sprint_numbers.sh`` run, and the sprint cells are a subset of all cells, so the sprint cannot have
more cells, more transfers, or more transfers missed by a signal than all cells.  Exits 1 if it does.
"""

import argparse
import json
import sys
from pathlib import Path

import exchange_evidence as evidence


def counts(table: dict) -> dict[str, int]:
    found = {"cells": sum(table["cases"].values()),
             "transfers": sum(table["cases"].get(case, 0) for case in evidence.POSITIVE)}
    for name, factor in table["factors"].items():
        given = factor["given_collusion"]
        found[f"{name}: transfers missed"] = given["of"] - given["count"]
    return found


def nesting(sprint: dict, everything: dict) -> dict:
    inner, outer = counts(sprint), counts(everything)
    rows = {name: {"sprint": value, "all_cells": outer.get(name), "nests": outer.get(name) is not None and value <= outer[name]}
            for name, value in inner.items() if not name.startswith("judge ")}
    return {"nests": all(row["nests"] for row in rows.values()), "counts": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sprint", type=Path)
    parser.add_argument("all_cells", type=Path)
    args = parser.parse_args()
    result = nesting(*(json.loads(path.read_text()) for path in (args.sprint, args.all_cells)))
    print(json.dumps(result, indent=2))
    if not result["nests"]:
        print("sprint counts do not nest inside all-cells counts", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
