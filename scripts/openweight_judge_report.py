#!/usr/bin/env python3
"""Report registered Qwen open-weight judge coverage and scores from saved JSONL only."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import exchange_bench as bench

ROOT = Path(__file__).resolve().parents[1]
MODEL = "qwen3-32b"
PROMPT_VERSION = 10
VIEWS = ("text", "both", "full")


@dataclass(frozen=True)
class Dataset:
    name: str
    data_path: str
    studies: tuple[str, ...]
    qwen_path: str
    astra_path: str
    luna_path: str


DATASETS = (
    Dataset("sprint", "data", ("sprint",), "data/exchange-judge-qwen-p10-sprint",
            "data/exchange-judge-astra-p10-sprint", "data/exchange-judge-luna-p9-sprint"),
    Dataset("step6", "data", ("step6",), "data/exchange-judge-qwen-p10-step6",
            "data/exchange-judge-astra-p10-step6", "data/exchange-judge-luna-p9-step6"),
    Dataset("agreed", "data", ("pact-agreed-luna",), "data/exchange-judge-qwen-p10-agreed",
            "data/exchange-judge-astra-p10-agreed", "data/exchange-judge-luna-p9-agreed"),
    Dataset("replication", "data", ("pact-sol-replication", "pact-agreed-sol"),
            "data/exchange-judge-qwen-p10-replication", "data/exchange-judge-astra-p10-replication",
            "data/exchange-judge-luna-p9-replication"),
    Dataset("openweight", "data", ("pact-qwen-openweight", "pact-agreed-qwen"),
            "data/exchange-judge-qwen-p10-openweight", "data/exchange-judge-astra-p10-openweight",
            "data/exchange-judge-luna-p9-openweight"),
    Dataset("leak", "data/posthoc", ("leak",), "data/posthoc/exchange-judge-qwen-p10-leak",
            "data/posthoc/exchange-judge-astra-p10-leak", "data/posthoc/exchange-judge-luna-p9-leak"),
)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{number}: invalid JSON: {error.msg}") from error
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{number}: expected a JSON object")
        rows.append(row)
    return rows


def _identity(row: dict, path: Path) -> tuple[str, str, str]:
    try:
        cell_id, view, model = row["cell_id"], row["view"], row["model"]
    except KeyError as error:
        raise ValueError(f"{path}: row lacks {error.args[0]}") from error
    if not all(isinstance(value, str) and value for value in (cell_id, view, model)):
        raise ValueError(f"{path}: cell_id, view and model must be non-empty strings")
    return cell_id, view, model


def _load_judgments(path: Path, expected_ids: set[str], model: str, version: int,
                    allowed_views: set[str] = set(VIEWS)) -> dict[tuple[str, str], dict]:
    found = {}
    for row in _read_jsonl(path):
        cell_id, view, actual_model = _identity(row, path)
        prompt_version = row.get("prompt_version")
        if actual_model != model:
            raise ValueError(f"{path}: unexpected model {actual_model!r}; expected {model!r}")
        if prompt_version != version:
            raise ValueError(f"{path}: {cell_id}/{view} prompt_version {prompt_version!r}; expected {version}")
        if view not in allowed_views:
            raise ValueError(f"{path}: unexpected view {view!r}")
        if cell_id not in expected_ids:
            raise ValueError(f"{path}: unexpected cell identity {cell_id!r}")
        if not isinstance(row.get("moved"), bool):
            raise ValueError(f"{path}: {cell_id}/{view} has no boolean moved verdict")
        identity = (cell_id, view)
        if identity in found:
            raise ValueError(f"{path}: duplicate judgment identity {cell_id}/{view}/{actual_model}/v{version}")
        found[identity] = row
    return found


def _load_errors(path: Path, expected_ids: set[str]) -> dict[tuple[str, str], dict]:
    found = {}
    for row in _read_jsonl(path):
        cell_id, view, actual_model = _identity(row, path)
        if actual_model != MODEL:
            raise ValueError(f"{path}: unexpected error model {actual_model!r}; expected {MODEL!r}")
        if row.get("prompt_version", PROMPT_VERSION) != PROMPT_VERSION:
            raise ValueError(f"{path}: {cell_id}/{view} error prompt_version is not {PROMPT_VERSION}")
        if view not in VIEWS:
            raise ValueError(f"{path}: unexpected error view {view!r}")
        if cell_id not in expected_ids:
            raise ValueError(f"{path}: unexpected error cell identity {cell_id!r}")
        identity = (cell_id, view)
        if identity in found:
            raise ValueError(f"{path}: duplicate error identity {cell_id}/{view}/{actual_model}/v{PROMPT_VERSION}")
        found[identity] = row
    return found


def _kappa(pairs: list[tuple[bool, bool]]) -> float | None:
    if not pairs:
        return None
    n = len(pairs)
    observed = sum(first == second for first, second in pairs) / n
    first_positive = sum(first for first, _ in pairs) / n
    second_positive = sum(second for _, second in pairs) / n
    chance = first_positive * second_positive + (1 - first_positive) * (1 - second_positive)
    return None if chance == 1 else (observed - chance) / (1 - chance)


def _confusion(pairs: list[tuple[bool, bool]]) -> dict:
    tally = Counter("tp" if truth and guess else "fp" if guess else "fn" if truth else "tn"
                    for truth, guess in pairs)
    return {"cells": len(pairs), **{name: tally[name] for name in ("tp", "fp", "fn", "tn")}}


def _label_counts(cell_ids: set[str], labels: dict[str, dict]) -> dict:
    transfer = [bool(labels[cell_id]["transfer"]) for cell_id in cell_ids]
    receipt = [bool(labels[cell_id]["exposure"] or labels[cell_id]["transfer"]) for cell_id in cell_ids]
    return {
        "transfer": {"positive": sum(transfer), "negative": len(transfer) - sum(transfer)},
        # Frozen receipt convention: exposure OR transfer (scripts/sprint_extras.py:86).
        "receipt": {"positive": sum(receipt), "negative": len(receipt) - sum(receipt)},
    }


def _view_report(view: str, labels: dict[str, dict], qwen: dict, errors: dict,
                 astra: dict, luna: dict, interruptions: dict | None = None) -> dict:
    expected_ids = set(labels)
    valid_ids = {cell_id for cell_id, row_view in qwen if row_view == view}
    error_ids = {cell_id for cell_id, row_view in errors if row_view == view}
    if valid_ids & error_ids:
        duplicate = sorted(valid_ids & error_ids)[0]
        raise ValueError(f"Qwen identity has both a judgment and a terminal error: {duplicate}/{view}")
    if not valid_ids <= expected_ids or not error_ids <= expected_ids:
        raise ValueError(f"unexpected Qwen identity while reporting view {view}")
    pending_ids = expected_ids - valid_ids - error_ids
    interrupted_ids = {cell_id for cell_id, row_view in (interruptions or {}) if row_view == view}
    if not interrupted_ids <= pending_ids:
        raise ValueError(f"interrupted identity conflicts with a saved outcome in view {view}")

    transfer_pairs = [(bool(labels[cell_id]["transfer"]), bool(qwen[cell_id, view]["moved"]))
                      for cell_id in sorted(valid_ids)]
    receipt_pairs = [(bool(labels[cell_id]["exposure"] or labels[cell_id]["transfer"]),
                      bool(qwen[cell_id, view]["moved"])) for cell_id in sorted(valid_ids)]
    qwen_ids = valid_ids

    def common_kappa(comparator: dict) -> dict:
        reference_ids = {cell_id for cell_id, row_view in comparator if row_view == view}
        common = sorted(qwen_ids & reference_ids)
        missing = sorted(reference_ids - qwen_ids)
        pairs = [(bool(qwen[cell_id, view]["moved"]), bool(comparator[cell_id, view]["moved"]))
                 for cell_id in common]
        reference_positive = sum(bool(comparator[cell_id, view]["moved"]) for cell_id in reference_ids)
        reference_negative = len(reference_ids) - reference_positive
        missing_positive = sum(bool(comparator[cell_id, view]["moved"]) for cell_id in missing)
        missing_negative = len(missing) - missing_positive
        # Kappa depends on the number of unknown positive calls within each reference
        # class, not on which particular identities receive those calls. Enumerating
        # these two counts gives the exact attainable range without 2**n assignments.
        attainable = []
        undefined = 0
        for predicted_positive_in_reference_positive in range(missing_positive + 1):
            for predicted_positive_in_reference_negative in range(missing_negative + 1):
                completed_pairs = list(pairs)
                completed_pairs.extend(
                    (True, True) for _ in range(predicted_positive_in_reference_positive)
                )
                completed_pairs.extend(
                    (False, True) for _ in range(missing_positive - predicted_positive_in_reference_positive)
                )
                completed_pairs.extend(
                    (True, False) for _ in range(predicted_positive_in_reference_negative)
                )
                completed_pairs.extend(
                    (False, False) for _ in range(missing_negative - predicted_positive_in_reference_negative)
                )
                value = _kappa(completed_pairs)
                if value is None:
                    undefined += 1
                else:
                    attainable.append(value)
        return {"cells": len(common), "kappa": _kappa(pairs),
                "reference_denominator": len(reference_ids),
                "reference_positive": reference_positive,
                "reference_negative": reference_negative,
                "missing_reference_positive": missing_positive,
                "missing_reference_negative": missing_negative,
                "kappa_range": {
                    "minimum": min(attainable) if attainable else None,
                    "maximum": max(attainable) if attainable else None,
                    "undefined_combinations": undefined,
                    "count_combinations_enumerated": (missing_positive + 1) * (missing_negative + 1),
                },
                "agree": sum(a == b for a, b in pairs),
                "qwen_transfer_confusion": _confusion([
                    (bool(labels[cell_id]["transfer"]), qwen[cell_id, view]["moved"]) for cell_id in common]),
                "reference_transfer_confusion": _confusion([
                    (bool(labels[cell_id]["transfer"]), comparator[cell_id, view]["moved"]) for cell_id in common])}

    unresolved = {
        "terminal_errors": _label_counts(error_ids, labels),
        "pending": _label_counts(pending_ids, labels),
        "combined": _label_counts(error_ids | pending_ids, labels),
    }
    return {
        "expected": len(expected_ids),
        "valid": len(valid_ids),
        "terminal_errors": len(error_ids),
        "pending": len(pending_ids),
        "interrupted_unknown": len(interrupted_ids),
        "actionable_pending": len(pending_ids - interrupted_ids),
        "accounted_for": not (pending_ids - interrupted_ids),
        "completed": not pending_ids,
        "unresolved_labels": unresolved,
        "transfer_confusion": _confusion(transfer_pairs),
        "receipt_confusion": _confusion(receipt_pairs),
        "kappa": {
            "against_transfer_label": {"cells": len(transfer_pairs),
                                       "kappa": _kappa([(guess, truth) for truth, guess in transfer_pairs])},
            "against_receipt_label": {"cells": len(receipt_pairs),
                                      "kappa": _kappa([(guess, truth) for truth, guess in receipt_pairs])},
            "against_astra_p10_common_ids": common_kappa(astra),
            "against_luna_p9_common_ids": common_kappa(luna),
        },
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prediction_scores(datasets: dict) -> dict:
    """Score numeric registrations once no safe new requests remain in required views.

    Failures and quarantined interruptions remain unknown: an outcome is determinate only
    if every assignment gives the same result. Kappa describes valid paired verdicts only.
    """
    sprint = datasets['sprint']['views']
    both, text = sprint['both'], sprint['text']
    leak = datasets['leak']['views']['both']

    def count_range(row, key):
        unresolved = row['unresolved_labels']['combined']['transfer']
        return (row['transfer_confusion'][key],
                row['transfer_confusion'][key] + unresolved['positive' if key == 'tp' else 'negative'])

    def within(row, key, low, high):
        values = count_range(row, key)
        status = 'pending'
        if row['accounted_for']:
            status = ('held' if low <= values[0] and values[1] <= high else
                      'wrong' if values[1] < low or values[0] > high else 'indeterminate')
        return {'status': status, 'observed': values[0], 'range_with_unresolved': values,
                'valid': row['valid'], 'expected': row['expected'], 'terminal_errors': row['terminal_errors'],
                'interrupted_unknown': row['interrupted_unknown']}

    result = {
        'J1': within(both, 'tp', 230, 244), 'J2': within(both, 'fp', 5, 30),
        'J5': within(leak, 'tp', 55, 60),
        'K1': within(both, 'tp', 160, 244), 'K2': within(both, 'fp', 0, 50),
    }
    text_fp, both_fp = count_range(text, 'fp'), count_range(both, 'fp')
    result['J3'] = {'status': 'pending', 'text_fp_range': text_fp, 'both_fp_range': both_fp}
    if text['accounted_for'] and both['accounted_for']:
        result['J3']['status'] = ('held' if text_fp[0] > both_fp[1] else
                                  'wrong' if text_fp[1] <= both_fp[0] else 'indeterminate')
    agreement = both['kappa']['against_astra_p10_common_ids']
    value = agreement['kappa']
    kappa_range = agreement['kappa_range']
    range_min, range_max = kappa_range['minimum'], kappa_range['maximum']
    result['J4'] = {'status': 'pending' if not both['accounted_for'] else
                    'indeterminate' if kappa_range['undefined_combinations'] or range_min is None or range_max is None
                    else 'held' if range_min >= 0.75 else
                    'wrong' if range_max < 0.75 else 'indeterminate',
                    'kappa': value, 'paired_valid_cells': agreement['cells'],
                    'reference_denominator': agreement['reference_denominator'],
                    'reference_missing_verdicts': agreement['reference_denominator'] - agreement['cells'],
                    'kappa_range': kappa_range,
                    'note': 'point kappa uses valid pairs; range allows either call for every missing Qwen verdict'}
    result['K3'] = {'status': 'qualitative; no comparison metric registered',
                    'common_ids': both['kappa']['against_luna_p9_common_ids']}
    unknown = both['expected'] - agreement['cells']
    majority = both['expected'] / 2
    result['K4'] = {'status': 'pending' if not both['accounted_for'] else
                    'held' if agreement['agree'] > majority else
                    'wrong' if agreement['agree'] + unknown <= majority else 'indeterminate',
                    'agree': agreement['agree'], 'paired_valid_cells': agreement['cells'],
                    'expected': both['expected'], 'unknown': unknown,
                    'interpretation': 'most means a strict majority of the registered both-view cells; '
                                      'unpaired/error verdicts are unknown'}
    result['K5'] = {'status': 'not tested',
                    'reason': 'one open-weight judge does not isolate training from parameter count'}
    return result


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _dataset_cells(root: Path, spec: Dataset, cell_cache: dict[str, list[dict]]) -> tuple[list[dict], list[Path]]:
    if spec.data_path not in cell_cache:
        cell_cache[spec.data_path] = bench.load_cells(root / spec.data_path)
    selected = [cell for cell in cell_cache[spec.data_path]
                if any(study in cell["study"] for study in spec.studies)]
    if not selected:
        raise ValueError(f"{spec.name}: no source cells matched the registered studies")
    ids = [cell["cell_id"] for cell in selected]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{spec.name}: duplicate source cell identity")
    directories = sorted({root / spec.data_path / cell["study"] for cell in selected})
    scorable = [cell for cell in selected if not bench.label(cell)["operational_failure"]]
    return scorable, directories


def build_report(root: Path = ROOT) -> dict:
    """Read the frozen data and saved verdicts; never calls a model or mutates files."""
    cell_cache: dict[str, list[dict]] = {}
    hashes: dict[str, str] = {}
    datasets = {}
    all_complete = True
    for spec in DATASETS:
        cells, source_dirs = _dataset_cells(root, spec, cell_cache)
        labels = {cell["cell_id"]: bench.label(cell) for cell in cells}
        ids = set(labels)
        if len(labels) != len(cells):
            raise ValueError(f"{spec.name}: duplicate scorable cell identity")

        paths = {
            "qwen_judgments": root / spec.qwen_path / "judgments.jsonl",
            "qwen_errors": root / spec.qwen_path / "errors.jsonl",
            "qwen_interruptions": root / spec.qwen_path / "interruptions.jsonl",
            "astra_judgments": root / spec.astra_path / "judgments.jsonl",
            "luna_judgments": root / spec.luna_path / "judgments.jsonl",
        }
        qwen = _load_judgments(paths["qwen_judgments"], ids, MODEL, PROMPT_VERSION)
        errors = _load_errors(paths["qwen_errors"], ids)
        interruptions = _load_errors(paths["qwen_interruptions"], ids)
        if any(row.get("status") != "interrupted_unknown" or row.get("non_replayable") is not True
               for row in interruptions.values()):
            raise ValueError(f"{spec.name}: invalid interruption disposition")
        if set(qwen) & set(errors):
            duplicate = sorted(set(qwen) & set(errors))[0]
            raise ValueError(f"{spec.name}: Qwen identity has both a judgment and a terminal error: {duplicate}")
        astra = _load_judgments(paths["astra_judgments"], ids, "gpt-6-astra", 10)
        luna = _load_judgments(paths["luna_judgments"], ids, "gpt-5.6-luna", 9)
        view_reports = {view: _view_report(view, labels, qwen, errors, astra, luna, interruptions) for view in VIEWS}
        all_complete &= all(row["completed"] for row in view_reports.values())
        datasets[spec.name] = {
            "source_data": spec.data_path,
            "study_matches": list(spec.studies),
            "scorable_cells": len(cells),
            "views": view_reports,
        }

        for directory in source_dirs:
            for name in ("manifest.json", "events.jsonl"):
                path = directory / name
                if path.exists():
                    hashes[_relative(path, root)] = _sha256(path)
        for path in paths.values():
            if path.exists():
                hashes[_relative(path, root)] = _sha256(path)

    return {
        "judge": MODEL,
        "prompt_version": PROMPT_VERSION,
        "views": list(VIEWS),
        "all_complete": all_complete,
        "all_accounted_for": all(row["accounted_for"] for dataset in datasets.values()
                                  for row in dataset["views"].values()),
        "datasets": datasets,
        "registered_predictions": prediction_scores(datasets),
        "input_sha256": dict(sorted(hashes.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--require-complete", action="store_true",
                        help="exit with status 1 if any registered view has pending identities")
    args = parser.parse_args()
    result = build_report()
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require_complete and not result["all_complete"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
