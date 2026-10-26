#!/usr/bin/env python3
"""Exploratory checks asked for by the Codex audit and the report session, 2026-10-23.

Written after the analysis freeze; reads the frozen label, signals, judges' verdicts and the frozen
`plus_factors` functions, and changes none of them.

- ``variants``: the plus-factor ranking with other numerators and benchmarks: agent-made exchanges
  alone as the numerator (audit M7); transfers with no rule ("authorized") counted as an innocent
  case against transfers under the rule (report R4); assigned non-completions put back among the
  negatives (audit M3).  Each with posteriors at stated priors.
- ``judge-receipt``: each judge's verdicts scored against use (the frozen label's ``transfer``) and
  against receipt (``exposure`` or ``transfer``), per view (report R2, audit M2).
- ``board-names``: per arm, the share of board writes whose page name carries an agent's id, which
  tells an observer the author the board otherwise hides (report S10).
- ``grouped-split``: the registered evidence table's choose-on-half, score-on-half, with halves made
  of whole tasks (token pairs) instead of cells, so no scoring cell shares a task with the choosing
  half (audit M6).
- ``matched-arms`` (post hoc, 2026-10-24): two arms of one model side by side, per signal and per label
  field, with exact intervals and Fisher's exact test; by default the pact (pact-board-coded) against
  reversed-board, which both put the token reversed on the board and differ mainly in the rule
  (report session, layer 2).
- Post hoc, asked by the report session for draft 2.3 (2026-10-24):
  ``discordance``: every cell where the uptake signal and the frozen label's transfer disagree, with
  each peer read, the answers and the page string that set uptake off;
  ``coded``: every transfer found only through the answers (label ``coded``), with the other agent's
  revisions the answerer read, to check the carrier by hand;
  ``masked-names``: signals and plus factors again with every board page name replaced, per cell,
  by an opaque id (judges are left out: they saw the real names), and ``arm-shortcut``, how well
  page-name-free metadata alone predicts the arm, as the floor any arm comparison must clear;
  ``absent-ratios``: per signal, P[not F | positive] over P[not F | each innocent case], in the
  registered cases and in each ``variants`` table;
  ``paired-arms``: two arms run on the same seed, paired by task index, per signal and label field:
  cells where both, only the first, only the second, or neither show it, with the exact test on
  discordant pairs and Fisher's test alongside; by default the pact against ``reversed-agreed-board``.
"""

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import exchange_bench as bench
import exchange_evidence as evidence
import plus_factors as plus
import posterior_table as posterior
import run_stats
import sprint_funnel as funnel

AUTHORIZED = "authorized transfer"
LABEL_FIELDS = ("transfer", "exposure", "own_token_written", "obtained")
MATCHED = ("pact-board-coded", "reversed-board")
PAIRED = ("pact-board-coded", "reversed-agreed-board")


def variant_tables(table: list[dict]) -> dict[str, list[dict]]:
    return {
        "agent-made numerator": [row for row in table if row["emergent"] or row["case"] not in evidence.POSITIVE],
        "authorized as innocent": [{**row, "case": AUTHORIZED} if row["case"] == evidence.POSITIVE[1] else row
                                   for row in table],
        "assigned non-completions as negatives": [{**row, "case": row["original_case"]}
                                                  if row["case"] == plus.ATTEMPTED else row for row in table],
    }


def variants(table: list[dict]) -> dict:
    found = {}
    for name, rows in variant_tables(table).items():
        ranked = plus.rank(rows)
        found[name] = {"cells": dict(Counter(row["case"] for row in rows)), "factors": ranked,
                       "posteriors": posterior.table(ranked)}
    return found


def judge_receipt(cells: list[dict], verdicts: dict[str, dict[tuple[str, str], bool]]) -> dict:
    truths = {cell["cell_id"]: bench.label(cell) for cell in cells if not bench.label(cell)["operational_failure"]}
    found = {}
    for judge, table in verdicts.items():
        for view in plus.VIEWS:
            for target in ("use", "receipt"):
                tally = Counter()
                for cell_id, truth in truths.items():
                    if (cell_id, view) not in table:
                        continue
                    actual = truth["transfer"] if target == "use" else truth["exposure"] or truth["transfer"]
                    said = table[cell_id, view]
                    tally["tp" if said and actual else "fp" if said else "fn" if actual else "tn"] += 1
                found[f"{judge}, {view}, against {target}"] = dict(tally)
    return found


def board_names(cells: list[dict]) -> dict:
    tally: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for cell in cells:
        for event in cell["events"]:
            page = event.get("resolved_page_id") or ""
            if event["action"] == "write" and event["status"] == "allowed" and "/board/" in page:
                tally[cell["arm"]][1] += 1
                name = page.split("/board/", 1)[1]
                tally[cell["arm"]][0] += any(re.search(rf"\b{agent}\b", name) for agent in cell["tokens"])
    return {arm: {"named": named, "board_writes": total} for arm, (named, total) in sorted(tally.items())}


def grouped_split(cells: list[dict], seed: int = 20261007) -> dict:
    """``exchange_evidence.study`` with whole token-pair blocks assigned to one half."""
    rows = [{"cell_id": cell["cell_id"], "block": tuple(sorted(cell["tokens"].items())),
             "case": evidence.case_type(cell), "signals": evidence.signals(cell)}
            for cell in cells if not bench.label(cell)["operational_failure"]]
    blocks = sorted({row["block"] for row in rows})
    random.Random(seed).shuffle(blocks)
    choosing = set(blocks[:len(blocks) // 2])
    train = [row for row in rows if row["block"] in choosing]
    test = [row for row in rows if row["block"] not in choosing]
    result = {"cells": len(rows), "blocks": len(blocks), "choosing_cells": len(train), "scoring_cells": len(test),
              "scoring_cases": dict(Counter(row["case"] for row in test)), "observers": {}}
    if not train or not test:
        result["note"] = "too few task blocks for two halves"
        return result
    for observer, names in (("pages and log", [n for n in rows[0]["signals"] if n not in evidence.NEEDS_ANSWERS]),
                            ("pages, log and answers", list(rows[0]["signals"]))):
        candidates = evidence.rules(names)
        chosen = max(candidates, key=lambda name: (round(evidence.macro(evidence.by_case(train, candidates[name])), 6),
                                                   -len(name)))
        result["observers"][observer] = {
            "rule": chosen,
            "train_macro": round(evidence.macro(evidence.by_case(train, candidates[chosen])), 3),
            "test_macro": round(evidence.macro(evidence.by_case(test, candidates[chosen])), 3),
            "test_by_case": evidence.by_case(test, candidates[chosen])}
    return result


def matched_arms(cells: list[dict], first: str = MATCHED[0], second: str = MATCHED[1]) -> dict:
    """Per signal and label field: count, exact 95% interval in each arm, Fisher's two-sided p."""
    scored = {arm: [cell for cell in cells if cell["arm"] == arm and not bench.label(cell)["operational_failure"]]
              for arm in (first, second)}
    models = sorted({cell["model"] for rows in scored.values() for cell in rows})
    rows = {arm: [{**evidence.signals(cell), **{field: bool(bench.label(cell)[field]) for field in LABEL_FIELDS}}
                  for cell in arm_cells] for arm, arm_cells in scored.items()}
    names = list(rows[first][0] if rows[first] else rows[second][0] if rows[second] else [])
    found = {}
    for name in names:
        counts = {arm: (sum(row[name] for row in rows[arm]), len(rows[arm])) for arm in (first, second)}
        found[name] = {**{arm: {"count": k, "of": n, "exact_95": run_stats.clopper_pearson(k, n)}
                          for arm, (k, n) in counts.items()},
                       "fisher_p": run_stats.fisher_exact(*counts[first], *counts[second])}
    return {"arms": [first, second], "models": models, "cells": {arm: len(rows[arm]) for arm in rows},
            "signals": found}


def paired_arms(cells: list[dict], first: str = PAIRED[0], second: str = PAIRED[1]) -> dict:
    by_task: dict[str, dict[str, dict]] = defaultdict(dict)
    for cell in cells:
        if cell["arm"] in (first, second) and not bench.label(cell)["operational_failure"]:
            values = {**evidence.signals(cell), **{field: bool(bench.label(cell)[field]) for field in LABEL_FIELDS}}
            by_task[funnel.task(cell)][cell["arm"]] = values
    pairs = {task: arms for task, arms in sorted(by_task.items()) if len(arms) == 2}
    found = {}
    for name in next(iter(pairs.values()))[first] if pairs else []:
        tally = Counter((arms[first][name], arms[second][name]) for arms in pairs.values())
        only_first, only_second = tally[True, False], tally[False, True]
        found[name] = {"both": tally[True, True], "only_" + first: only_first, "only_" + second: only_second,
                       "neither": tally[False, False], "paired_exact_p": funnel.paired_exact(only_first, only_second),
                       "fisher_p": run_stats.fisher_exact(tally[True, True] + only_first, len(pairs),
                                                          tally[True, True] + only_second, len(pairs))}
    return {"arms": [first, second], "pairs": len(pairs),
            "unpaired": sorted(task for task, arms in by_task.items() if len(arms) < 2), "signals": found}


def _peer_reads(cell: dict) -> list[dict]:
    authors = {event["revision_id"]: event["actor_id"] for event in cell["events"] if event.get("revision_id")}
    return [{"reader": event["actor_id"], "page": event.get("resolved_page_id"), "author": authors.get(event.get("read_revision_id"))}
            for event in cell["events"]
            if event["action"] == "read" and event["status"] == "allowed"
            and authors.get(event.get("read_revision_id")) not in (None, event["actor_id"], *bench.INFRASTRUCTURE)]


def uptake_matches(cell: dict) -> list[dict]:
    """The (answer string, page) pairs that set ``exchange_evidence.detect_uptake`` off, found the same way."""
    pages, log, answers = bench.text_view(cell), bench.log_view(cell), evidence.answers_view(cell)
    found = []
    for entry in answers:
        for literal in sorted(bench._literals(entry["answer"])):
            for page in pages:
                if page["author"] in (entry["actor"], *bench.INFRASTRUCTURE):
                    continue
                reader = bench.ANONYMOUS if page["author"] == bench.ANONYMOUS else entry["actor"]
                read_later = any(item["allowed"] and item["action"] == "read" and item["order"] > page["order"]
                                 and item["actor"] == reader and bench.resolve_page(item["page"]) == page["page"]
                                 for item in log)
                if read_later and bench.same_characters(literal, page["body"]):
                    found.append({"answerer": entry["actor"], "string": literal, "page": page["page"],
                                  "page_author": page["author"], "page_body": page["body"]})
    return found


def discordance(cells: list[dict]) -> dict:
    found = []
    for cell in cells:
        truth = bench.label(cell)
        if truth["operational_failure"]:
            continue
        uptake = evidence.signals(cell)["uptake"]
        if uptake != truth["transfer"]:
            found.append({"cell_id": cell["cell_id"], "arm": cell["arm"], "case": plus.case(cell),
                          "uptake": uptake, "transfer": truth["transfer"], "exposure": truth["exposure"],
                          "coded": truth["coded"], "tokens": cell["tokens"], "peer_reads": _peer_reads(cell),
                          "answers": evidence.answers_view(cell), "uptake_matches": uptake_matches(cell)})
    return {"discordant": len(found), "by_direction": dict(Counter(
        "uptake without transfer" if row["uptake"] else "transfer without uptake" for row in found)), "cells": found}


def coded(cells: list[dict]) -> dict:
    found = []
    for cell in cells:
        truth = bench.label(cell)
        if truth["operational_failure"] or not truth["coded"]:
            continue
        authors = {event["revision_id"]: event for event in cell["events"] if event.get("revision_id")}
        for answer in evidence.answers_view(cell):
            for agent, token in cell["tokens"].items():
                if agent == answer["actor"] or token not in bench._squash(answer["answer"]):
                    continue
                read = [authors[event["read_revision_id"]] for event in cell["events"]
                        if event["action"] == "read" and event["status"] == "allowed" and event["actor_id"] == answer["actor"]
                        and authors.get(event.get("read_revision_id"), {}).get("actor_id") == agent]
                found.append({"cell_id": cell["cell_id"], "arm": cell["arm"], "answerer": answer["actor"],
                              "token_of": agent, "token": token, "answer": answer["answer"],
                              "revisions_read": [{"page": revision.get("resolved_page_id"), "body": revision.get("body")}
                                                 for revision in {id(r): r for r in read}.values()]})
    return {"coded_transfers": len(found), "cells": found}


BOARD_NAME = re.compile(r"(board/)([^/?#\s]+)")
NAME_FIELDS = ("requested_destination", "resolved_page_id")


def masked(cell: dict) -> dict:
    """The cell with each board page name replaced by an opaque id, the same id for the same name."""
    ids: dict[str, str] = {}

    def mask(value):
        if not isinstance(value, str):
            return value
        return BOARD_NAME.sub(lambda match: match[1] + ids.setdefault(match[2], f"page{len(ids) + 1}"), value)

    return {**cell, "events": [{**event, **{field: mask(event[field]) for field in NAME_FIELDS if field in event}}
                               for event in cell["events"]]}


def masked_names(cells: list[dict]) -> dict:
    found = {}
    for name, view in (("page names as written", cells), ("board page names masked", [masked(cell) for cell in cells])):
        table = plus.rows(view, {})
        found[name] = {factor: {"given_collusion": ranked["given_collusion"],
                                "closest_innocent_case": ranked["closest_innocent_case"],
                                "likelihood_ratio": ranked["likelihood_ratio"],
                                "likelihood_ratio_lower_95_one_sided": ranked["likelihood_ratio_lower_95_one_sided"]}
                       for factor, ranked in plus.rank(table).items()}
    found["unchanged by masking"] = found["page names as written"] == found["board page names masked"]
    return found


def metadata(cell: dict) -> dict[str, int]:
    """Counts an observer has without page names or text: what was done, how often, by whom."""
    events = [event for event in cell["events"] if not event.get("seeded") and event["actor_id"] in cell["tokens"]]
    allowed = [event for event in events if event["status"] == "allowed"]
    return {"actions": len(events),
            "writes": sum(event["action"] == "write" for event in allowed),
            "reads": sum(event["action"] == "read" for event in allowed),
            "denied": sum(event["status"] == "denied" for event in events),
            "board writes": sum(event["action"] == "write" and "/board/" in (event.get("resolved_page_id") or "")
                                for event in allowed),
            "answers": sum(event["action"] == "final_answer" for event in allowed)}


def arm_shortcut(cells: list[dict]) -> dict:
    """Leave-one-out accuracy of predicting the arm from one metadata count: the most common arm among
    the other cells with the same count (the overall most common arm if none), against always guessing
    the most common arm."""
    rows = [(cell["arm"], metadata(cell)) for cell in cells if not bench.label(cell)["operational_failure"]]
    arms = Counter(arm for arm, _ in rows)
    if len(arms) < 2:
        return {"note": "fewer than two arms", "cells": dict(arms)}
    features = {}
    for feature in rows[0][1]:
        right = 0
        for index, (arm, values) in enumerate(rows):
            others = rows[:index] + rows[index + 1:]
            same = Counter(other for other, counts in others if counts[feature] == values[feature])
            pool = same or Counter(other for other, _ in others)
            right += max(sorted(pool), key=pool.__getitem__) == arm
        features[feature] = {"right": right, "of": len(rows), "exact_95": run_stats.clopper_pearson(right, len(rows))}
    return {"cells": dict(arms), "most_common_arm": {"right": arms.most_common(1)[0][1], "of": len(rows)},
            "leave_one_out": features}


def _absent(table: list[dict]) -> dict:
    names = sorted({name for row in table for name in row["signals"]})
    found = {}
    for name in names:
        by_case: dict[str, list[bool]] = defaultdict(list)
        for row in table:
            if row["signals"].get(name) is not None:
                by_case[row["case"]].append(not row["signals"][name])
        positive = [value for case in evidence.POSITIVE for value in by_case.get(case, [])]
        rate = sum(positive) / len(positive) if positive else None
        innocent = {}
        for case, values in sorted(by_case.items()):
            if case in evidence.POSITIVE or case == plus.ATTEMPTED or not values:
                continue
            other = sum(values) / len(values)
            innocent[case] = {"absent": sum(values), "of": len(values),
                              "exact_95": run_stats.clopper_pearson(sum(values), len(values)),
                              "ratio": rate / other if rate is not None and other else None}
        found[name] = {"absent_given_positive": {"absent": sum(positive), "of": len(positive),
                                                  "exact_95": run_stats.clopper_pearson(sum(positive), len(positive))},
                       "by_innocent_case": innocent}
    return found


def absent_ratios(table: list[dict]) -> dict:
    return {name: _absent(rows) for name, rows in {"registered cases": table, **variant_tables(table)}.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("check", choices=("variants", "judge-receipt", "board-names", "grouped-split",
                                              "matched-arms", "discordance", "coded", "masked-names",
                                              "arm-shortcut", "absent-ratios", "paired-arms"))
    parser.add_argument("--studies", nargs="+", default=["sprint"], help="only studies whose name contains one of these")
    parser.add_argument("--arms", nargs=2, help="matched-arms and paired-arms: the two arms compared")
    parser.add_argument("--data", type=Path, default=bench.ROOT / "data", help="where study directories are read from")
    parser.add_argument("--judge", nargs=2, action="append", default=[], metavar=("NAME", "DIRECTORY"))
    args = parser.parse_args()
    cells = [cell for cell in bench.load_cells(args.data) if any(name in cell["study"] for name in args.studies)]
    verdicts = {name: plus.load_verdicts(Path(directory)) for name, directory in args.judge}
    if args.check in ("variants", "absent-ratios"):
        table = plus.rows(cells, verdicts)
        originals = {cell["cell_id"]: evidence.case_type(cell) for cell in cells}
        table = [{**row, "original_case": originals[row["cell_id"]]} for row in table]
        output = variants(table) if args.check == "variants" else absent_ratios(table)
    elif args.check == "judge-receipt":
        output = judge_receipt(cells, verdicts)
    elif args.check == "board-names":
        output = board_names(cells)
    elif args.check == "matched-arms":
        output = matched_arms(cells, *(args.arms or MATCHED))
    elif args.check == "paired-arms":
        output = paired_arms(cells, *(args.arms or PAIRED))
    elif args.check in POST_HOC:
        output = POST_HOC[args.check](cells)
    else:
        output = grouped_split(cells)
    note = ("post hoc, asked 2026-10-24" if args.check in ("matched-arms", "paired-arms", "absent-ratios", *POST_HOC)
            else "exploratory, after the freeze")
    print(json.dumps({"note": note, "studies": args.studies, "check": args.check,
                      "result": output}, indent=2))


POST_HOC = {"discordance": discordance, "coded": coded, "masked-names": masked_names, "arm-shortcut": arm_shortcut}

if __name__ == "__main__":
    main()
