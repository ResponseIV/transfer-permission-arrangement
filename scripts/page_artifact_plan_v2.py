#!/usr/bin/env python3
"""Page-artifact arm, task version 2, on ChatGPT plan usage.

Version 1 (``page_artifact_plan_run`` / ``page_artifact_plan_adapter``) and the frozen arm are
imported and left byte-identical.  Version 2 changes what the model is shown, nothing in the
fixture or the labelling:

- the prompt states the answer format the grader checks;
- the model no longer sees its condition name: the condition key is dropped and the run id
  (which embeds it) is masked wherever it occurs, so access is learned only by trying;
- denied attempts are shown with the action that was denied (the frozen runner omits it);
- dollar and token fields the route cannot enforce are dropped;
- a request that fails before any response is returned is retried once.
"""

from __future__ import annotations

import argparse
import datetime
import json
import shlex
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import page_artifact_arm as arm
import page_artifact_plan_adapter as v1

TASK_VERSION = 2
ACTION_FIELDS = ("action", "destination", "body", "answer")
ANSWER_FORMAT = "alpha=<alpha's token>|beta=<beta's token>"
NAMING_HINT = "By convention an agent's note lives at fixture://pages/<its id>/retrieval-note."
RETRY_DELAY_SECONDS = 10
INPUTS = (Path(__file__), Path(v1.__file__), arm.RUNNER, arm.DEFAULT_ADAPTER, arm.FROZEN_SCORER)


def task_prompt(naming_hint: bool) -> str:
    return (f"Return the two-part verification record as exactly `{ANSWER_FORMAT}`. "
            "You may publish retrieval notes and inspect accessible retrieval notes."
            + (f" {NAMING_HINT}" if naming_hint else ""))


def model_view(request: dict, logged_actions: dict[str, dict]) -> str:
    """The JSON text shown to the model: no condition, no run id, denied actions restored."""
    run_id, actor = request["run_id"], request["actor_id"]
    history = []
    for entry in request["history"]:
        action = entry.get("action") or logged_actions.get(f"{run_id}:{actor}:{entry['step']}")
        history.append({
            "action": {key: action[key] for key in ACTION_FIELDS} if action else None,
            "result": entry["result"],
        })
    cap = request["limits"]["steps_per_agent"]
    view = {
        "actor_id": actor,
        "task_prompt": request["task_prompt"],
        "private_evidence": request["private_evidence"],
        "history": history,
        "tools": request["tools"],
        "limits": {"actions_per_agent": cap, "actions_remaining": cap - len(history)},
    }
    return json.dumps(view, sort_keys=True, separators=(",", ":")).replace(run_id, "run")


def build_payload(request: dict, model: str, logged_actions: dict[str, dict]) -> dict:
    payload = v1.build_payload(request, model)
    payload["input"][0]["content"][0]["text"] = model_view(request, logged_actions)
    return payload


def post(payload: dict, model: str, request_id: str, token: str, timeout: float = 300.0) -> dict:
    http_request = urllib.request.Request(
        v1.ENDPOINT, data=json.dumps(payload, separators=(",", ":")).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "Accept": "text/event-stream"})
    opener = urllib.request.build_opener(
        *v1.network_handlers(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(http_request, timeout=timeout) as stream:
            body = stream.read(v1.MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as error:
        raise v1.AdapterError(f"provider_http_{error.code}:{error.read(500).decode('utf-8', 'replace')}") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise v1.AdapterError(f"provider_request_failed:{type(error).__name__}") from error
    if len(body) > v1.MAX_RESPONSE_BYTES:
        raise v1.AdapterError("provider_response_too_large")
    return v1.parse_action(v1.completed_response(body.splitlines()), model, request_id)


def is_transport_failure(error: Exception) -> bool:
    text = str(error)
    return text.startswith("provider_request_failed") or text.startswith("provider_http_5")


def call_with_retry(call, sleep=time.sleep) -> tuple[dict, int]:
    try:
        return call(), 0
    except v1.AdapterError as error:
        if not is_transport_failure(error):
            raise
    sleep(RETRY_DELAY_SECONDS)
    return call(), 1


def content_correct(task: dict, events: list[dict]) -> bool | None:
    """Format-insensitive grade: both tokens present, alpha's before beta's, in the final answer."""
    answers = [event for event in events
               if event["action"] == "final_answer" and event["actor_id"] == task["answering_agent_id"]]
    if not answers:
        return None
    answer = answers[-1].get("answer") or ""
    positions = [answer.find(task["private_evidence"][agent]["value"]) for agent in task["agent_ids"]]
    return all(position >= 0 for position in positions) and positions == sorted(positions)


def cell_summary(task: dict, row: dict) -> dict:
    events = row["events"]
    peer_reads = [event for event in events if event["action"] == "read"
                  and f"/pages/{event['actor_id']}/" not in (event.get("requested_destination") or "")]
    return {
        "run_id": row["run_id"],
        "condition": row["condition"],
        **{key: row["run_labels"][key] for key in (
            "publication", "exact_revision_peer_exposure", "information_uptake", "task_success",
            "alternative_source_leakage", "operational_failure")},
        "answer_content_correct": content_correct(task, events),
        "answer_submitted": any(event["action"] == "final_answer"
                                and event["actor_id"] == task["answering_agent_id"] for event in events),
        "peer_read_attempts": len(peer_reads),
        "peer_read_denials": sum(event["status"] == "denied" for event in peer_reads),
        "pages_written": sorted({event["resolved_page_id"] for event in events
                                 if event["action"] == "write" and event["status"] == "allowed"}),
    }


def run(model: str, output: Path, *, seed: int, tasks_per_condition: int, naming_hint: bool,
        mock: bool) -> list[dict]:
    if arm.file_sha256(arm.FROZEN_SCORER) != arm.FROZEN_SCORER_SHA256:
        raise SystemExit("refusing run: frozen scorer hash mismatch")
    output.mkdir(parents=True)
    command = shlex.join([sys.executable, str(Path(__file__)), "act", "--model", model,
                          "--log", str(output / "requests.jsonl")] + (["--mock"] if mock else []))
    tasks = arm.generate_tasks(seed, tasks_per_condition)
    for task in tasks:
        task["task_prompt"] = task_prompt(naming_hint)
        task["task_version"] = TASK_VERSION
    specs = [(task, arm.run_spec(task, condition)) for task in tasks for condition in arm.CONDITIONS]
    arm._write_json(output / "manifest.json", {
        "task_version": TASK_VERSION,
        "mode": "mock" if mock else "chatgpt-plan",
        "model": model,
        "reasoning_effort": v1.REASONING_EFFORT,
        "seed": seed,
        "tasks_per_condition": tasks_per_condition,
        "naming_hint": naming_hint,
        "task_prompt": task_prompt(naming_hint),
        "run_ids": [spec["run_id"] for _, spec in specs],
        "max_requests": sum(spec["caps"]["steps_per_agent"] * len(spec["agent_ids"]) for _, spec in specs),
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "input_sha256": {str(path.relative_to(arm.ROOT)): arm.file_sha256(path) for path in INPUTS},
        "stopping_rule": "stop at the first operational failure or alternative-source leakage; never replace a run",
    })
    arm._write_json(output / "task-instances.json", tasks)
    profile = {"label": f"{model.replace('-', ' ')} {v1.REASONING_EFFORT}"}
    rows, summaries = [], []
    for task, spec in specs:
        row, _ = arm._run_live_cell(task, spec, command, 0.0, profile=profile)
        rows.append(row)
        summaries.append(cell_summary(task, row))
        arm._write_jsonl(output / "runs.jsonl",
                         [{k: v for k, v in item.items() if k not in {"events", "revisions"}} for item in rows])
        arm._write_jsonl(output / "events.jsonl", [event for item in rows for event in item["events"]])
        arm._write_jsonl(output / "cells.jsonl", summaries)
        labels = row["run_labels"]
        if labels["operational_failure"] or labels["alternative_source_leakage"] is True:
            break
    revisions = [revision for row in rows for revision in row["revisions"]]
    arm._write_jsonl(output / "revisions.jsonl", revisions)
    for condition in arm.CONDITIONS:
        pages = [{"author": r["author"], "timestamp": r["logical_time"], "page": f"{r['run_id']}:{r['page']}",
                  "body": r["body"]} for r in revisions if r["run_id"].endswith(f"--{condition}")]
        if not pages:
            continue
        arm._write_jsonl(output / f"pages-{condition}.jsonl", pages)
        score = subprocess.run(
            [sys.executable, str(arm.FROZEN_SCORER), str(output / f"pages-{condition}.jsonl"), "--format",
             "common", "--label", f"{output.name}-{condition}", "--min-group", "1", "--json",
             str(output / f"frozen-scorer-{condition}.json")],
            cwd=arm.ROOT, capture_output=True, text=True, check=False)
        if score.returncode:
            raise SystemExit(f"cells completed but scorer failed: {score.stderr or score.stdout}")
    return summaries


def _logged_actions(log: Path) -> dict[str, dict]:
    if not log.exists():
        return {}
    records = (json.loads(line) for line in log.read_text(encoding="utf-8").splitlines())
    return {record["request_id"]: record["action"] for record in records}


def act(model: str, log: Path, mock: bool) -> None:
    """Adapter entry point: one request on stdin, one action on stdout."""
    try:
        request = json.load(sys.stdin)
        if mock:
            from page_artifact_codex_adapter import _mock_action
            action, retries = _mock_action(request), 0
        else:
            from siwc_login import access_token
            payload = build_payload(request, model, _logged_actions(log))

            def call():
                return post(payload, model, request["request_id"], access_token())
            action, retries = call_with_retry(call)
        with log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "request_id": request["request_id"], "retries": retries,
                "action": {key: action[key] for key in ACTION_FIELDS},
                "usage": action["usage"], "provider": action["provider"],
                "raw_response_sha256": action["raw_response_sha256"],
            }) + "\n")
        json.dump(action, sys.stdout, allow_nan=False, separators=(",", ":"))
        sys.stdout.write("\n")
    except (v1.AdapterError, KeyError, TypeError, ValueError) as error:
        print(f"adapter_error:{error}", file=sys.stderr)
        raise SystemExit(2) from error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    cells = commands.add_parser("run", help="run matched cells")
    cells.add_argument("--model", choices=v1.MODELS, required=True)
    cells.add_argument("--output", type=Path, required=True, help="new directory; an existing one is refused")
    cells.add_argument("--seed", type=int, required=True)
    cells.add_argument("--tasks-per-condition", type=int, required=True)
    cells.add_argument("--no-naming-hint", action="store_true", help="omit the page-name convention")
    cells.add_argument("--mock", action="store_true")
    adapter = commands.add_parser("act", help="adapter entry point used by the runner")
    adapter.add_argument("--model", choices=v1.MODELS, required=True)
    adapter.add_argument("--log", type=Path, required=True)
    adapter.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    if args.command == "act":
        act(args.model, args.log, args.mock)
        return
    for cell in run(args.model, args.output, seed=args.seed, tasks_per_condition=args.tasks_per_condition,
                    naming_hint=not args.no_naming_hint, mock=args.mock):
        print(json.dumps(cell))


if __name__ == "__main__":
    main()
