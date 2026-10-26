#!/usr/bin/env python3
"""Export every labelled cell as one benchmark file: events, ground truth, case type, signals, judges.

Post hoc (2026-10-24). One JSON line per cell from the frozen loader (``data``) and the post-hoc arms
(``data/posthoc``), OpenAI and open-weight models (not the three prior Gemini attempts); operational failures are kept and flagged, never relabelled.
Ground truth is the frozen ``exchange_bench.label``; the case type is ``exchange_evidence.case_type``,
with ``plus_factors.case`` beside it (instructed exchanges that did not complete as "attempted").
"""

import argparse
import hashlib
import json
from pathlib import Path

import exchange_bench as bench
import exchange_evidence as evidence
import plus_factors as plus

ROOT = Path(__file__).resolve().parents[1]
STUDIES = ("sprint", "step6", "agreed", "replication", "openweight", "qwen-letter", "qwen-letter-cont",
           "scripted-offer-sol", "scripted-offer-qwen", "scripted-offer-qwen-cont")
JUDGES = {judge: [f"exchange-judge-{judge}-{name}" for name in STUDIES]
          + [f"posthoc/exchange-judge-{judge}-leak"] for judge in ("astra-p10", "luna-p9", "qwen-p10")}
PROVIDERS = ("gpt-", "qwen")


def origin(study: str, posthoc: bool) -> str:
    if posthoc or any(key in study for key in ("agreed", "replication", "qwen", "scripted-offer")):
        return "post hoc"
    return "sprint" if "sprint" in study or "step6" in study else "prior work"


def verdicts() -> dict[str, dict[str, dict[str, bool]]]:
    found: dict[str, dict[str, dict[str, bool]]] = {}
    for name, folders in JUDGES.items():
        for folder in folders:
            path = ROOT / "data" / folder / "judgments.jsonl"
            if path.exists():
                for row in map(json.loads, path.read_text().splitlines()):
                    found.setdefault(row["cell_id"], {}).setdefault(name, {})[row["view"]] = bool(row["moved"])
    return found


def record(cell: dict, posthoc: bool, judged: dict) -> dict:
    truth = bench.label(cell)
    return {"cell_id": cell["cell_id"], "study": cell["study"], "origin": origin(cell["study"], posthoc),
            "model": cell["model"], "arm": cell["arm"], "condition": cell["condition"],
            "rule_in_prompt": evidence.RULE in (cell.get("prompt") or ""), "prompt": cell.get("prompt"),
            "actions_per_agent": cell.get("actions"), "tokens": cell["tokens"],
            "label": {key: value for key, value in truth.items() if key not in ("cell_id", "model", "study", "arm", "condition")},
            "case": None if truth["operational_failure"] else evidence.case_type(cell),
            "case_with_attempts": None if truth["operational_failure"] else plus.case(cell),
            "signals": None if truth["operational_failure"] else evidence.signals(cell),
            "judges": judged.get(cell["cell_id"], {}), "events": cell["events"]}


def export(out: Path) -> dict:
    judged = verdicts()
    rows = [record(cell, posthoc, judged)
            for posthoc, data in ((False, ROOT / "data"), (True, ROOT / "data" / "posthoc"))
            for cell in bench.load_cells(data) if cell["model"].startswith(PROVIDERS)]
    out.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    (out / "cells.jsonl").write_text(body)
    summary = {"cells": len(rows), "sha256": hashlib.sha256(body.encode()).hexdigest(),
               "by_origin": {}, "by_case": {}, "by_model": {}}
    for row in rows:
        for key, value in (("by_origin", row["origin"]), ("by_case", row["case"] or "operational failure"), ("by_model", row["model"])):
            summary[key][value] = summary[key].get(value, 0) + 1
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("output", type=Path)
    print(json.dumps(export(parser.parse_args().output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
