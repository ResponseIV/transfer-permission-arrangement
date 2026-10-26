#!/usr/bin/env python3
"""Report frozen transfer labels, observer signals, and saved judge coverage by study group."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import exchange_bench as bench
import exchange_evidence as evidence
import openweight_judge_report as judge_report
from run_stats import clopper_pearson

ROOT = Path(__file__).resolve().parents[1]
VIEWS = judge_report.VIEWS

JUDGES = (
    ("astra_p10", "gpt-6-astra", 10, "astra_path"),
    ("luna_p9", "gpt-5.6-luna", 9, "luna_path"),
    ("qwen_p10", "qwen3-32b", 10, "qwen_path"),
)

GROUPS = (
    {
        "name": "prescribed_no_rule_conventions",
        "dataset": "sprint",
        "description": "Primary disguised convention arms, including sprint continuations.",
        "match": lambda cell: cell["study"].startswith("study-disguised-") and "sprint" in cell["study"],
    },
    {
        "name": "instructed_pact",
        "dataset": "sprint",
        "description": "Primary instructed pact arm.",
        "match": lambda cell: cell["study"] == "study-pact-luna-sprint",
    },
    {
        "name": "uninvited_rule_arms",
        "dataset": "sprint",
        "description": "Primary wording arms under a confidentiality rule, without a prescribed pact.",
        "match": lambda cell: cell["study"].startswith("study-wording-")
        and "sprint" in cell["study"] and "step6" not in cell["study"]
        and cell["model"] in {"gpt-6-astra", "gpt-5.6-luna", "gpt-5.6-sol", "gpt-5.6-terra"},
    },
    {
        "name": "common_archive_comparator",
        "dataset": "sprint",
        "description": "Primary archive-sharing comparator arms.",
        "match": lambda cell: cell["study"] in {
            "page-artifact-plan-v4-luna-sprint", "page-artifact-plan-v4-sol-sprint",
        },
    },
    {
        "name": "sol_step6_followup",
        "dataset": "step6",
        "description": "Separate Sol step-6 follow-up, including its continuation.",
        "match": lambda cell: cell["study"] in {
            "study-wording-sol-step6", "study-wording-sol-step6-cont",
        },
    },
    {
        "name": "leak_comparators",
        "dataset": "leak",
        "description": "Separate post-hoc leak arms for Luna, Sol, and Qwen.",
        "match": lambda cell: cell["study"] in {
            "study-wording-leak-luna-negligent",
            "study-wording-leak-sol-negligent",
            "study-wording-leak-qwen-negligent",
        },
    },
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rate(successes: int, total: int) -> dict[str, Any]:
    interval = clopper_pearson(successes, total) if total else None
    return {
        "successes": successes,
        "denominator": total,
        "rate": successes / total if total else None,
        "ci95_clopper_pearson": list(interval) if interval else None,
    }


def _metrics(confusion: dict[str, int]) -> dict[str, dict[str, Any]]:
    tp, fp, fn, tn = (confusion[name] for name in ("tp", "fp", "fn", "tn"))
    return {
        "sensitivity": _rate(tp, tp + fn),
        "specificity": _rate(tn, tn + fp),
        "positive_predictive_value": _rate(tp, tp + fp),
        "false_positive_rate": _rate(fp, fp + tn),
    }


def _validate_label(cell_id: str, label: dict) -> None:
    if not isinstance(label, dict) or not isinstance(label.get("transfer"), bool):
        raise ValueError(f"{cell_id}: frozen transfer label is missing or is not boolean")
    for name in ("exposure", "via_archive", "obtained", "coded"):
        if not isinstance(label.get(name), bool):
            raise ValueError(f"{cell_id}: frozen label {name!r} is missing or is not boolean")
    if label["coded"] and not label["transfer"]:
        raise ValueError(f"{cell_id}: coded fallback is not a subset of the frozen transfer label")


def _confusion_for(expected_ids: set[str], labels: dict[str, dict], calls: dict[str, bool]) -> dict:
    missing = expected_ids - calls.keys()
    extra = calls.keys() - expected_ids
    if missing or extra:
        raise ValueError(f"call identities differ from expected cells (missing={len(missing)}, extra={len(extra)})")
    pairs = [(labels[cell_id]["transfer"], calls[cell_id]) for cell_id in sorted(expected_ids)]
    return judge_report._confusion(pairs)


def _signal_report(cells: list[dict], labels: dict[str, dict]) -> dict:
    signals = {cell["cell_id"]: evidence.signals(cell) for cell in cells}
    if len(signals) != len(cells):
        raise ValueError("duplicate cell identity while building frozen signals")
    names = tuple(next(iter(signals.values()))) if signals else ()
    expected_ids = set(signals)
    transfer_positive = sum(labels[cell_id]["transfer"] for cell_id in expected_ids)
    transfer_negative = len(expected_ids) - transfer_positive
    result = {}
    for name in names:
        calls = {cell_id: row[name] for cell_id, row in signals.items()}
        if not all(isinstance(call, bool) for call in calls.values()):
            raise ValueError(f"frozen signal {name!r} is not boolean")
        confusion = _confusion_for(expected_ids, labels, calls)
        positive = sum(calls.values())
        result[name] = {
            "positive": positive,
            "frequency": _rate(positive, len(cells)),
            "transfer_confusion": confusion,
            "transfer_metrics": _metrics(confusion),
        }
    return result


def _label_summary(cells: list[dict], labels: dict[str, dict]) -> dict:
    fields = ("transfer", "exposure", "via_archive", "obtained", "coded")
    return {
        field: {
            "positive": sum(labels[cell["cell_id"]][field] for cell in cells),
            "negative": len(cells) - sum(labels[cell["cell_id"]][field] for cell in cells),
            "denominator": len(cells),
        }
        for field in fields
    }


def _read_error_records(paths: list[Path], expected_ids: set[str], model: str,
                        version: int) -> dict[tuple[str, str], dict]:
    found: dict[tuple[str, str], dict] = {}
    for path in sorted(paths):
        for row in judge_report._read_jsonl(path):
            cell_id, view, actual_model = judge_report._identity(row, path)
            if actual_model != model:
                raise ValueError(f"{path}: unexpected error model {actual_model!r}; expected {model!r}")
            if row.get("prompt_version", version) != version:
                raise ValueError(f"{path}: {cell_id}/{view} error prompt_version is not {version}")
            if view not in VIEWS:
                raise ValueError(f"{path}: unexpected error view {view!r}")
            if cell_id not in expected_ids:
                raise ValueError(f"{path}: unexpected error cell identity {cell_id!r}")
            identity = (cell_id, view)
            if identity in found:
                raise ValueError(f"{path}: duplicate error identity {cell_id}/{view}/{model}/v{version}")
            found[identity] = row
    return found


def _read_interruption_records(path: Path, expected_ids: set[str], model: str,
                              version: int) -> dict[tuple[str, str], dict]:
    """Load quarantined executions, never interpreting them as a judge outcome."""
    if not path.exists():
        return {}
    found = {}
    for row in judge_report._read_jsonl(path):
        cell_id, view, actual_model = judge_report._identity(row, path)
        if actual_model != model or row.get("prompt_version", version) != version:
            raise ValueError(f"{path}: unexpected interruption model or prompt version")
        if view not in VIEWS or cell_id not in expected_ids:
            raise ValueError(f"{path}: unexpected interruption identity {cell_id}/{view}")
        if row.get("status") != "interrupted_unknown" or row.get("non_replayable") is not True:
            raise ValueError(f"{path}: interruption must be marked interrupted_unknown and non_replayable")
        identity = (cell_id, view)
        if identity in found:
            raise ValueError(f"{path}: duplicate interruption identity {cell_id}/{view}/{model}/v{version}")
        found[identity] = row
    return found


def _judge_view(view: str, cell_ids: set[str], labels: dict[str, dict],
                judgments: dict[tuple[str, str], dict], errors: dict[tuple[str, str], dict],
                interruptions: dict[tuple[str, str], dict] | None = None) -> dict:
    interruptions = interruptions or {}
    valid_ids = {cell_id for cell_id, row_view in judgments if row_view == view and cell_id in cell_ids}
    error_ids = {cell_id for cell_id, row_view in errors if row_view == view and cell_id in cell_ids}
    resolved_error_ids = valid_ids & error_ids
    terminal_error_ids = error_ids - valid_ids
    pending_ids = cell_ids - valid_ids - terminal_error_ids
    interrupted_ids = {cell_id for cell_id, row_view in interruptions if row_view == view and cell_id in cell_ids}
    if not interrupted_ids <= pending_ids:
        raise ValueError(f"interruption conflicts with a judgment or terminal error in {view}")
    actionable_pending_ids = pending_ids - interrupted_ids
    calls = {cell_id: judgments[cell_id, view]["moved"] for cell_id in valid_ids}
    confusion = judge_report._confusion([
        (labels[cell_id]["transfer"], calls[cell_id]) for cell_id in sorted(valid_ids)
    ])
    return {
        "expected": len(cell_ids),
        "valid": len(valid_ids),
        "terminal_errors": len(terminal_error_ids),
        "resolved_error_attempts": len(resolved_error_ids),
        "pending": len(pending_ids),
        "interrupted_unknown": len(interrupted_ids),
        "actionable_pending": len(actionable_pending_ids),
        "accounted_for": not actionable_pending_ids,
        "valid_transfer_confusion": confusion,
        "valid_transfer_metrics": _metrics(confusion),
        "unresolved_transfer_label": {
            "terminal_errors": {
                "positive": sum(labels[cell_id]["transfer"] for cell_id in terminal_error_ids),
                "negative": len(terminal_error_ids) - sum(labels[cell_id]["transfer"] for cell_id in terminal_error_ids),
            },
            "pending": {
                "positive": sum(labels[cell_id]["transfer"] for cell_id in pending_ids),
                "negative": len(pending_ids) - sum(labels[cell_id]["transfer"] for cell_id in pending_ids),
            },
            "interrupted_unknown": {
                "positive": sum(labels[cell_id]["transfer"] for cell_id in interrupted_ids),
                "negative": len(interrupted_ids) - sum(labels[cell_id]["transfer"] for cell_id in interrupted_ids),
            },
        },
    }


def _dataset_paths(root: Path, name: str, spec, expected_ids: set[str]) -> tuple[dict, dict, dict, list[Path]]:
    loaded: dict[str, dict] = {}
    terminal: dict[str, dict] = {}
    interruptions: dict[str, dict] = {}
    input_paths: list[Path] = []
    for key, model, version, path_field in JUDGES:
        directory = root / getattr(spec, path_field)
        judgments_path = directory / "judgments.jsonl"
        error_paths = sorted(directory.glob("errors*.jsonl"))
        model_judgments = judge_report._load_judgments(
            judgments_path, expected_ids, model, version,
        )
        model_errors = _read_error_records(error_paths, expected_ids, model, version)
        loaded[key] = model_judgments
        terminal[key] = model_errors
        input_paths.extend(path for path in [judgments_path, *error_paths] if path.exists())
        interruption_path = directory / "interruptions.jsonl"
        interruptions[key] = (_read_interruption_records(interruption_path, expected_ids, model, version)
                              if key == "qwen_p10" else {})
        if set(loaded[key]) & set(interruptions[key]) or set(terminal[key]) & set(interruptions[key]):
            raise ValueError(f"{name}: interruption conflicts with a saved outcome for {key}")
        if key == "qwen_p10" and interruption_path.exists():
            input_paths.append(interruption_path)
    return loaded, terminal, interruptions, input_paths


def build_report(root: Path = ROOT) -> dict:
    """Read local data and JSONL judgments only; never contacts a model or changes inputs."""
    root = root.resolve()
    cell_cache: dict[str, list[dict]] = {}
    dataset_cells: dict[str, list[dict]] = {}
    dataset_raw_cells: dict[str, list[dict]] = {}
    dataset_dirs: dict[str, list[Path]] = {}
    dataset_specs = {spec.name: spec for spec in judge_report.DATASETS}
    for dataset_name in ("sprint", "step6", "leak"):
        spec = dataset_specs[dataset_name]
        cells, source_dirs = judge_report._dataset_cells(root, spec, cell_cache)
        dataset_cells[dataset_name] = cells
        dataset_dirs[dataset_name] = source_dirs
        dataset_raw_cells[dataset_name] = [
            cell for cell in cell_cache[spec.data_path]
            if any(study in cell["study"] for study in spec.studies)
        ]
    judge_data = {}
    for dataset_name in ("sprint", "step6", "leak"):
        spec = dataset_specs[dataset_name]
        expected_ids = {cell["cell_id"] for cell in dataset_cells[dataset_name]}
        judge_data[dataset_name] = _dataset_paths(root, dataset_name, spec, expected_ids)

    groups: dict[str, list[dict]] = {}
    all_cells: dict[str, dict] = {}
    for dataset_name, cells in dataset_raw_cells.items():
        for cell in cells:
            cell_id = cell["cell_id"]
            if cell_id in all_cells:
                raise ValueError(f"duplicate source cell identity across datasets: {cell_id}")
            all_cells[cell_id] = cell
            label = bench.label(cell)
            _validate_label(cell_id, label)

    for group in GROUPS:
        selected = [cell for cell in dataset_raw_cells[group["dataset"]] if group["match"](cell)]
        if not selected:
            raise ValueError(f"{group['name']}: no source cells matched its registered study definition")
        ids = [cell["cell_id"] for cell in selected]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{group['name']}: duplicate source cell identity")
        groups[group["name"]] = selected

    group_reports = {}
    for group in GROUPS:
        dataset_name = group["dataset"]
        spec = dataset_specs[dataset_name]
        source_cells = groups[group["name"]]
        source_ids = {cell["cell_id"] for cell in source_cells}
        dataset_source = dataset_raw_cells[dataset_name]
        labels = {cell["cell_id"]: bench.label(cell) for cell in source_cells}
        for cell_id, label in labels.items():
            _validate_label(cell_id, label)
        operational_failures = [cell for cell in source_cells if bench.label(cell)["operational_failure"]]
        cells = [cell for cell in source_cells if not bench.label(cell)["operational_failure"]]
        scorable_ids = {cell["cell_id"] for cell in cells}
        scorable_labels = {cell_id: labels[cell_id] for cell_id in scorable_ids}
        dataset_raw_ids = {cell["cell_id"] for cell in dataset_source}
        dataset_ids = {cell["cell_id"] for cell in dataset_cells[dataset_name]}
        if not source_ids <= dataset_raw_ids or not scorable_ids <= dataset_ids:
            raise ValueError(f"{group['name']}: group includes cells outside its judge dataset")
        judgments_by_judge, errors_by_judge, interruptions_by_judge, _ = judge_data[dataset_name]

        judges = {}
        for key, model, version, _ in JUDGES:
            judges[key] = {
                "model": model,
                "prompt_version": version,
                "views": {
                    view: _judge_view(view, scorable_ids, scorable_labels,
                                      judgments_by_judge[key], errors_by_judge[key],
                                      interruptions_by_judge[key])
                    for view in VIEWS
                },
            }

        group_reports[group["name"]] = {
            "description": group["description"],
            "source_studies": sorted({cell["study"] for cell in source_cells}),
            "source_cells": len(source_cells),
            "operational_failures_excluded": len(operational_failures),
            "scorable_cells": len(cells),
            "frozen_labels": _label_summary(cells, scorable_labels),
            "frozen_signals": _signal_report(cells, scorable_labels),
            "judges": judges,
        }

    hashes: dict[str, str] = {}
    for dirs in dataset_dirs.values():
        for directory in dirs:
            for name in ("manifest.json", "events.jsonl"):
                path = directory / name
                if path.exists():
                    hashes[path.relative_to(root).as_posix()] = _sha256(path)
    for dataset_name in ("sprint", "step6", "leak"):
        _, _, _, paths = judge_data[dataset_name]
        for path in paths:
            hashes[path.relative_to(root).as_posix()] = _sha256(path)

    return {
        "schema_version": 1,
        "offline_only": True,
        "source_root": ".",
        "definitions": {
            "transfer_target": "scripts/exchange_bench.py::label.transfer",
            "signals": "scripts/exchange_evidence.py::signals",
            "judge_outcome": "saved JSONL moved boolean",
            "views": list(VIEWS),
            "missing_judgment": "pending; never scored as false",
            "interrupted_unknown": "A possible dispatched request without a saved outcome; shown separately, excluded from judge scoring, and never replayed.",
            "coded_label": "A source-matching fallback subset of transfer, not an agreement or coordination truth label.",
            "error_record": "An error with a later valid verdict for the same cell and view is a resolved attempt, not a terminal error.",
            "intervals": "Clopper-Pearson 95% intervals are descriptive episode-level binomial intervals, not cluster-adjusted inference.",
        },
        "dataset_scorable_cells": {name: len(cells) for name, cells in dataset_cells.items()},
        "groups": group_reports,
        "input_sha256": dict(sorted(hashes.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="repository or static source root containing data/ and data/posthoc/")
    parser.add_argument("--output", type=Path,
                        help="write JSON here; stdout is used when omitted")
    args = parser.parse_args()
    result = build_report(args.root)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
