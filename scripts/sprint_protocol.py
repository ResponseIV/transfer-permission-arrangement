#!/usr/bin/env python3
"""What an observer can conclude, and how sure it can be: the sprint's answer to question 2.3 as tables.

Post hoc (asked 2026-10-24, after every registered prediction was scored); reads the final numbers
and the frozen label, signals and judges, and changes none of them.

- ``protocol``: per observer (pages alone, pages and log, pages, log and answers), the judge's hit and
  false-alarm rates on all sprint cells with exact intervals, and the share of an alarm that is a
  real transfer at stated base rates (point, and a conservative bound: lowest hit rate over highest
  false-alarm rate in the 95% intervals); written as JSON, a Markdown table and an SVG figure.
- ``stats``: Holm's correction within each family of tests already reported (paired pact against
  no-rule, matched pact against reversed-board, the letter-against-purpose wording pairs); Cohen's
  kappa between the two judges per view and between each judge and the frozen label; the cells where
  the label reads receipt without use.
"""

import argparse
import json
import math
from pathlib import Path

import exchange_bench as bench
import exchange_judge as judge
import plus_factors as plus
import run_stats

ROOT = Path(__file__).resolve().parents[1]
JUDGES = {"Astra p10": ROOT / "data/exchange-judge-astra-p10-sprint", "Luna p9": ROOT / "data/exchange-judge-luna-p9-sprint"}
OBSERVERS = {"text": "pages alone", "both": "pages and log", "full": "pages, log and answers"}
PRIORS = (0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 0.5)
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = {("Astra p10", "both"): "#2a78d6", ("Astra p10", "text"): "#eb6834", ("Luna p9", "both"): "#1baf7a"}


def rates(cells: list[dict]) -> list[dict]:
    """Rates against all episodes without a transfer ("negatives": "all"), then against the innocent ones only:
    instructed exchanges that did not complete are failed attempts, not innocent cases ("negatives": "unprescribed")."""
    found = []
    for name, directory in JUDGES.items():
        for row in judge.score([directory], cells):
            tp, fp, fn, tn = row["tp"], row["fp"], row["fn"], row["tn"]
            found.append({"judge": name, "view": row["view"], "observer": OBSERVERS[row["view"]], "negatives": "all",
                          "cells": row["cells"], "hits": [tp, tp + fn], "false_alarms": [fp, fp + tn],
                          "hit_95": run_stats.clopper_pearson(tp, tp + fn), "false_alarm_95": run_stats.clopper_pearson(fp, fp + tn)})
    truth = {cell["cell_id"]: bench.label(cell)["transfer"] for cell in cells}
    unprescribed = {cell["cell_id"] for cell in cells if not truth[cell["cell_id"]] and plus.case(cell) != plus.ATTEMPTED}
    for name, directory in JUDGES.items():
        verdicts = {(row["cell_id"], row["view"]): bool(row["moved"])
                    for row in map(json.loads, (directory / "judgments.jsonl").read_text().splitlines()) if row["cell_id"] in truth}
        for view in OBSERVERS:
            positives = [said for (cell_id, seen), said in verdicts.items() if seen == view and truth[cell_id]]
            negatives = [said for (cell_id, seen), said in verdicts.items() if seen == view and cell_id in unprescribed]
            tp, fp = sum(positives), sum(negatives)
            found.append({"judge": name, "view": view, "observer": OBSERVERS[view], "negatives": "unprescribed",
                          "cells": len(positives) + len(negatives), "hits": [tp, len(positives)],
                          "false_alarms": [fp, len(negatives)], "hit_95": run_stats.clopper_pearson(tp, len(positives)),
                          "false_alarm_95": run_stats.clopper_pearson(fp, len(negatives))})
    return found


def ppv(hit: float, false_alarm: float, prior: float) -> float:
    return hit * prior / (hit * prior + false_alarm * (1 - prior))


def protocol(cells: list[dict]) -> dict:
    found = rates(cells)
    for row in found:
        hit, false_alarm = row["hits"][0] / row["hits"][1], row["false_alarms"][0] / row["false_alarms"][1]
        row["alarm_is_transfer"] = {str(prior): {"point": ppv(hit, false_alarm, prior),
                                                  "conservative": ppv(row["hit_95"][0], row["false_alarm_95"][1], prior)}
                                    for prior in PRIORS}
    return {"note": "post hoc; the base rate is the auditor's, not measured here", "rows": found}


def markdown(result: dict) -> str:
    lines = ["| Judge | Observer | Negatives | Transfers caught | False alarms | Alarm is a transfer, base rate 1% | 10% |",
             "|---|---|---|---|---|---|---|"]
    for row in result["rows"]:
        one, ten = row["alarm_is_transfer"]["0.01"], row["alarm_is_transfer"]["0.1"]
        lines.append(f"| {row['judge']} | {row['observer']} | {row['negatives']} | {row['hits'][0]}/{row['hits'][1]} | "
                     f"{row['false_alarms'][0]}/{row['false_alarms'][1]} | {one['point']:.0%} (at least {one['conservative']:.0%}) | "
                     f"{ten['point']:.0%} (at least {ten['conservative']:.0%}) |")
    return "\n".join(lines) + "\n"


def svg(result: dict) -> str:
    """Share of alarms that are real transfers against the base rate, conservative bound, log x axis."""
    width, height, left, right, top, bottom = 720, 420, 64, 170, 56, 52
    plot_w, plot_h = width - left - right, height - top - bottom
    x = lambda prior: left + (math.log10(prior) - math.log10(PRIORS[0])) / (math.log10(PRIORS[-1]) - math.log10(PRIORS[0])) * plot_w  # noqa: E731
    y = lambda share: top + (1 - share) * plot_h  # noqa: E731
    grid = [0.001, 0.01, 0.1, 0.5]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" font-family="Inter, Helvetica, Arial, sans-serif">',
             f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
             f'<text x="{left}" y="24" font-size="15" font-weight="600" fill="{INK}">How often a judge\'s alarm is a real transfer</text>',
             f'<text x="{left}" y="42" font-size="12" fill="{MUTED}">Lower 95% bound, by the base rate of transfers among audited exchanges (all 450 sprint cells)</text>']
    for share in (0, 0.25, 0.5, 0.75, 1):
        parts.append(f'<line x1="{left}" x2="{left + plot_w}" y1="{y(share):.1f}" y2="{y(share):.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{left - 8}" y="{y(share) + 4:.1f}" font-size="11" fill="{MUTED}" text-anchor="end">{share:.0%}</text>')
    for prior in grid:
        parts.append(f'<text x="{x(prior):.1f}" y="{top + plot_h + 18}" font-size="11" fill="{MUTED}" text-anchor="middle">{prior:.1%}</text>')
    parts.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 12}" font-size="12" fill="{MUTED}" text-anchor="middle">Base rate of transfers (log scale)</text>')
    labels = []
    for row in result["rows"]:
        colour = SERIES.get((row["judge"], row["view"])) if row["negatives"] == "all" else None
        if not colour:
            continue
        points = [(x(prior), y(row["alarm_is_transfer"][str(prior)]["conservative"])) for prior in PRIORS]
        path = " ".join(f"{'M' if i == 0 else 'L'}{px:.1f},{py:.1f}" for i, (px, py) in enumerate(points))
        parts.append(f'<path d="{path}" fill="none" stroke="{colour}" stroke-width="2"/>')
        parts += [f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{colour}" stroke="{SURFACE}" stroke-width="2"><title>'
                  f'{row["judge"]}, {row["observer"]}: base rate {prior:.1%}, at least {row["alarm_is_transfer"][str(prior)]["conservative"]:.0%}</title></circle>'
                  for (px, py), prior in zip(points, PRIORS)]
        labels.append((points[-1][1], colour, f'{row["judge"]}, {row["observer"]}'))
    last = -1e9
    for py, colour, text in sorted(labels):
        py = max(py, last + 16)
        last = py
        parts.append(f'<circle cx="{left + plot_w + 12}" cy="{py - 4:.1f}" r="4" fill="{colour}"/>')
        parts.append(f'<text x="{left + plot_w + 20}" y="{py:.1f}" font-size="11" fill="{INK}">{text}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def holm(pvalues: dict[str, float]) -> dict[str, dict]:
    ordered = sorted(pvalues.items(), key=lambda item: item[1])
    found, running = {}, 0.0
    for index, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, (len(ordered) - index) * p))
        found[name] = {"p": p, "holm_p": running, "survives_0.05": running < 0.05}
    return found


def kappa(pairs: list[tuple[bool, bool]]) -> float | None:
    n = len(pairs)
    if not n:
        return None
    agree = sum(a == b for a, b in pairs) / n
    first, second = sum(a for a, _ in pairs) / n, sum(b for _, b in pairs) / n
    chance = first * second + (1 - first) * (1 - second)
    return None if chance == 1 else (agree - chance) / (1 - chance)


def stats(numbers: Path, cells: list[dict]) -> dict:
    families = {}
    paired = json.loads((numbers / "paired-pact-agreed-luna.json").read_text())["result"]["signals"]
    families["pact against no-rule, Luna, paired exact"] = holm({name: row["paired_exact_p"] for name, row in paired.items()})
    matched = json.loads((numbers / "matched-pact-reversed-luna.json").read_text())["result"]["signals"]
    families["pact against reversed-board, Luna, Fisher"] = holm({name: row["fisher_p"] for name, row in matched.items()
                                                                if row["fisher_p"] is not None})
    wording = json.loads((numbers / "funnel.json").read_text())["wording"]
    families["letter against purpose wording, paired exact"] = holm({f"{model} {stage}": row["paired_exact_p"]
                                                                     for model, stages in wording.items() for stage, row in stages.items()})
    truth = {cell["cell_id"]: bench.label(cell) for cell in cells}
    verdicts = {name: {(row["cell_id"], row["view"]): bool(row["moved"]) for row in
                       map(json.loads, (directory / "judgments.jsonl").read_text().splitlines()) if row["cell_id"] in truth}
                for name, directory in JUDGES.items()}
    agreement = {}
    for view in OBSERVERS:
        both = [(verdicts["Astra p10"][key], verdicts["Luna p9"][key]) for key in verdicts["Astra p10"]
                if key[1] == view and key in verdicts["Luna p9"]]
        agreement[f"Astra p10 against Luna p9, {view}"] = {"cells": len(both), "kappa": kappa(both)}
        for name, table in verdicts.items():
            against = [(said, truth[cell_id]["transfer"]) for (cell_id, seen), said in table.items() if seen == view]
            agreement[f"{name} against the label, {view}"] = {"cells": len(against), "kappa": kappa(against)}
    unused = sorted(cell_id for cell_id, row in truth.items()
                    if not row["operational_failure"] and row["exposure"] and not row["transfer"] and not row["via_archive"])
    return {"note": "post hoc; Holm within each family as reported, not across families",
            "holm": families, "agreement": agreement,
            "receipt_without_use": {"cells": len(unused), "cell_ids": unused}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("numbers", type=Path, help="a sprint_numbers.sh output directory")
    args = parser.parse_args()
    cells = [cell for cell in bench.load_cells() if "sprint" in cell["study"] and not bench.label(cell)["operational_failure"]]
    result = protocol(cells)
    (args.numbers / "protocol.json").write_text(json.dumps(result, indent=2))
    (args.numbers / "protocol.md").write_text(markdown(result))
    (args.numbers / "protocol-alarm-share.svg").write_text(svg(result))
    (args.numbers / "stats.json").write_text(json.dumps(stats(args.numbers, cells), indent=2))
    print(f"wrote protocol.json, protocol.md, protocol-alarm-share.svg and stats.json to {args.numbers}")


if __name__ == "__main__":
    main()
