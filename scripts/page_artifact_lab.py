#!/usr/bin/env python3
"""One runner for page-artifact studies on ChatGPT plan usage and Gemini API.

Versions 3 to 6 each copied the run loop to add one kind of arm.  This module takes an arm as
data instead, so a study is a short file that lists its arms and calls ``main``; see
``study_dropbox.py``.  The model view, payload, action parsing, grading and telemetry are
version 4's, imported unchanged, and the fixture and labelling are still the frozen arm's.

It also closes the two gaps that stopped runs on 2026-10-05: a connection dropped mid-response
is now a transport failure like any other, and HTTP 429 is retried with a longer wait.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import http.client
import json
import shlex
import ssl
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import page_artifact_arm as arm
import page_artifact_gemini_adapter as gemini
import page_artifact_openweight_adapter as openweight
import page_artifact_plan_adapter as v1
import page_artifact_plan_v2 as v2
import page_artifact_plan_v3 as v3
import page_artifact_plan_v4 as v4

ARCHIVE = v4.ARCHIVE
NOTE_PAGE = "retrieval-note"
RETRY_DELAYS_SECONDS = (10, 30, 90)
INPUTS = (Path(__file__), Path(v4.__file__), Path(v3.__file__), Path(v2.__file__), Path(v1.__file__),
          arm.RUNNER, arm.DEFAULT_ADAPTER)


@dataclass(frozen=True)
class Arm:
    condition: str = "shared-writable"
    sentences: tuple[str, ...] = ()        # appended to the base prompt, in order
    seeded: tuple[str, ...] = ()           # agents whose note exists before anyone acts
    beta_first: bool = False
    archive: bool = False                  # read-only archive holding each token two reads away
    dropbox: bool = False                  # any agent may write to any note; writing replaces it
    actions: int = v3.ACTIONS_PER_AGENT

    def prompt(self) -> str:
        return " ".join([v2.task_prompt(True), *self.sentences])


def build_fixture(task: dict, spec: Arm):
    """Fixture class for one cell, composed from the arm's switches."""
    base = v4.archive_fixture(task) if spec.archive else v4.FROZEN_FIXTURE

    class LabFixture(base):
        def __init__(self, condition, run_id, agent_ids):
            super().__init__(condition, run_id, agent_ids)
            for agent in spec.seeded:
                value = task["private_evidence"][agent]["value"]
                v4.FROZEN_FIXTURE.write(self, agent, f"fixture://pages/{agent}/{NOTE_PAGE}", f"{agent}={value}")
            for event in self.events:
                event["seeded"] = True

        def write(self, actor_id, destination, body):
            owner = v4.resolve_owner(destination, self.agent_ids)
            if not spec.dropbox or owner in (None, actor_id, ARCHIVE) or actor_id not in self.agent_ids:
                return super().write(actor_id, destination, body)
            # Cross-owner write: the frozen method with the owner check lifted.  The revision keeps
            # the page's owner and records the writer as author, so labelling attributes it.
            _, page, canonical = self._resolve(actor_id, "write", destination)
            history = self._pages.setdefault((owner, page), [])
            revision = arm.Revision(
                f"{self.run_id}:r{len(self.revisions) + 1:04d}", canonical, owner, actor_id, body,
                len(self.events) + 1, history[-1].revision_id if history else None)
            history.append(revision)
            self.revisions.append(revision)
            self._record(actor_id, "write", "allowed", destination, resolved_page_id=canonical,
                         revision_id=revision.revision_id, previous_revision_id=revision.previous_revision_id,
                         body=body, body_sha256=hashlib.sha256(body.encode()).hexdigest())
            return revision

    return LabFixture


def fetch(payload: dict, token: str, timeout: float = 300.0) -> dict:
    """POST one request and return the completed response; every transport fault is an AdapterError."""
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
    except (urllib.error.URLError, http.client.HTTPException, OSError) as error:
        raise v1.AdapterError(f"provider_request_failed:{type(error).__name__}") from error
    if len(body) > v1.MAX_RESPONSE_BYTES:
        raise v1.AdapterError("provider_response_too_large")
    return v1.completed_response(body.splitlines())


def is_retryable(error: Exception) -> bool:
    text = str(error)
    return (v3.is_retryable(error) or text.startswith("provider_http_429")
            or text.startswith("stream_ended_without_response_completed"))


def call_with_retries(call, sleep=time.sleep) -> tuple[dict, int]:
    for retries, delay in enumerate(RETRY_DELAYS_SECONDS):
        try:
            return call(), retries
        except v1.AdapterError as error:
            if not is_retryable(error):
                raise
        sleep(delay)
    return call(), len(RETRY_DELAYS_SECONDS)


def agent_summary(task: dict, events: list[dict], agent: str, order: list[str]) -> dict:
    """Version-4 summary plus token publication, turn position and writes onto a peer's note."""
    summary = v4.agent_summary(task, events, agent)
    owners = (*task["agent_ids"], ARCHIVE)
    token = task["private_evidence"][agent]["value"]
    writes = [(event, v4.resolve_owner(event.get("requested_destination"), owners)) for event in events
              if event["actor_id"] == agent and event["action"] == "write"]
    peer_writes = [event for event, owner in writes if owner not in (None, agent, ARCHIVE)]
    allowed = [event for event in peer_writes if event["status"] == "allowed"]
    summary.update(
        published_token=any(owner == agent and event["status"] == "allowed" and token in (event.get("body") or "")
                            for event, owner in writes),
        moves="first" if order[0] == agent else "second",
        peer_write_attempts=len(peer_writes),
        pushed_token=any(token in (event.get("body") or "") for event in allowed),
        peer_writes_without_token=sum(token not in (event.get("body") or "") for event in allowed),
    )
    # In a dropbox a write onto a peer's note is the intended move, not a probe.
    summary["probes"] -= len(allowed)
    return summary


def cell_summary(name: str, task: dict, row: dict, order: list[str]) -> dict:
    acted = [event for event in row["events"] if not event.get("seeded")]
    return {
        "run_id": row["run_id"], "arm": name, "condition": row["condition"],
        "operational_failure": row["run_labels"]["operational_failure"],
        "agents": [agent_summary(task, acted, agent, order) for agent in task["agent_ids"]],
    }


def planned_cells(arms: dict[str, Arm], seed: int, tasks_per_arm: int, names: list[str]) -> list[tuple]:
    cells = []
    for task in arm.generate_tasks(seed, tasks_per_arm):
        for name in names:
            spec = arms[name]
            cell_task = {**task, "task_prompt": spec.prompt()}
            run_spec = arm.run_spec(cell_task, spec.condition)
            run_spec["run_id"] = run_spec["split_group"] = f"{task['task_instance_id']}-{name}--{spec.condition}"
            run_spec["caps"] = {**run_spec["caps"], "steps_per_agent": spec.actions}
            if spec.beta_first:
                run_spec["agent_ids"] = list(reversed(run_spec["agent_ids"]))
                run_spec["ordering_policy"] = "round-robin-beta-first"
            cells.append((name, spec, cell_task, run_spec))
    return cells


def run(study: str, study_file: Path, arms: dict[str, Arm], model: str, output: Path, *, seed: int,
        tasks_per_arm: int, names: list[str], mock: bool, continue_from: Path | None = None) -> list[dict]:
    attempted = set()
    if continue_from is not None:
        attempted = {json.loads(line)["run_id"] for line in (continue_from / "cells.jsonl").read_text().splitlines()}
    cells = [cell for cell in planned_cells(arms, seed, tasks_per_arm, names) if cell[3]["run_id"] not in attempted]
    output.mkdir(parents=True)
    command = shlex.join([sys.executable, str(Path(__file__)), "act", "--model", model,
                          "--log", str(output / "requests.jsonl")] + (["--mock"] if mock else []))
    reasoning_effort = "default" if model in gemini.MODELS + openweight.MODELS else v1.REASONING_EFFORT
    if model in openweight.MODELS:   # post hoc: thinking counts as output, so it may not end a cell before the actions do
        for *_, run_spec in cells:
            run_spec["caps"] = {**run_spec["caps"],
                                "output_tokens_per_agent": run_spec["caps"]["steps_per_agent"] * openweight.MAX_TOKENS}
    arm._write_json(output / "manifest.json", {
        "study": study,
        "mode": "mock" if mock else "gemini-api" if model in gemini.MODELS else "openweight-vllm"
        if model in openweight.MODELS else "chatgpt-plan",
        "model": model,
        "reasoning_effort": reasoning_effort,
        "seed": seed,
        "tasks_per_arm": tasks_per_arm,
        "arms": {name: {**vars(arms[name]), "task_prompt": arms[name].prompt()} for name in names},
        "continued_from": str(continue_from) if continue_from else None,
        "run_ids": [run_spec["run_id"] for *_, run_spec in cells],
        "max_requests": sum(spec.actions * 2 for _, spec, _, _ in cells),
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "input_sha256": {str(path.relative_to(arm.ROOT)): arm.file_sha256(path) for path in (study_file, *INPUTS)},
        "stopping_rule": "stop at the first operational failure; never replace a cell",
    })
    profile = {"label": f"{model.replace('-', ' ')} {reasoning_effort}"}
    summaries, events = [], []
    for name, spec, task, run_spec in cells:
        arm.PageFixture = build_fixture(task, spec)
        try:
            row, _ = arm._run_live_cell(task, run_spec, command, 0.0, profile=profile)
        finally:
            arm.PageFixture = v4.FROZEN_FIXTURE
        events.extend(row["events"])
        summaries.append(cell_summary(name, task, row, run_spec["agent_ids"]))
        arm._write_jsonl(output / "events.jsonl", events)
        arm._write_jsonl(output / "cells.jsonl", summaries)
        if summaries[-1]["operational_failure"]:
            break
    return summaries


def load(outputs: list[Path]) -> list[dict]:
    return [json.loads(line) for output in outputs
            for line in (output / "cells.jsonl").read_text(encoding="utf-8").splitlines()]


def report(cells: list[dict]) -> dict:
    result = {}
    for name in dict.fromkeys(cell["arm"] for cell in cells):
        done = [cell for cell in cells if cell["arm"] == name and not cell["operational_failure"]]
        agents = [agent for cell in done for agent in cell["agents"]]
        outcomes = ("correct", "unavailable", "fabricated", "incorrect", "invalid_format", "no_answer")
        result[name] = {
            "cells": len(done),
            "alpha_correct_cells": sum(cell["agents"][0]["outcome"] == "correct" for cell in done),
            "both_correct_cells": sum(all(a["outcome"] == "correct" for a in cell["agents"]) for cell in done),
            "agents": len(agents),
            "agents_publishing_token": sum(a["published_token"] for a in agents),
            "agents_attempting_peer_write": sum(a["peer_write_attempts"] > 0 for a in agents),
            "agents_pushing_token": sum(a["pushed_token"] for a in agents),
            "cells_both_push": sum(all(a["pushed_token"] for a in cell["agents"]) for cell in done),
            "peer_writes_without_token": sum(a["peer_writes_without_token"] for a in agents),
            "agents_denied": sum(a["access_denied"] for a in agents),
            "denied_agents_retrying": sum(a["retries_after_denial"] > 0 for a in agents),
            "agents_probing": sum(a["probes"] > 0 for a in agents),
            "outcomes": {outcome: sum(a["outcome"] == outcome for a in agents) for outcome in outcomes},
            "mean_actions_used": round(sum(a["actions_used"] for a in agents) / len(agents), 2) if agents else None,
        }
    return result


def act(model: str, log: Path, mock: bool) -> None:
    try:
        request = json.load(sys.stdin)
        record = {"request_id": request["request_id"]}
        if mock:
            from page_artifact_codex_adapter import _mock_action
            action, retries = _mock_action(request), 0
        elif model in openweight.MODELS:
            payload = v4.build_payload(request, v1.MODELS[0], v2._logged_actions(log))
            record["model_input"] = payload["input"][0]["content"][0]["text"]
            response, retries = openweight.call(record["model_input"], model)
            action = openweight.parse_action(response, model, request["request_id"])
            record.update(openweight.telemetry(response))
        elif model in gemini.MODELS:
            payload = v4.build_payload(request, v1.MODELS[0], v2._logged_actions(log))
            record["model_input"] = payload["input"][0]["content"][0]["text"]
            response, retries = gemini.call(record["model_input"], model, gemini.api_key())
            action = gemini.parse_action(response, model, request["request_id"])
            record.update(gemini.telemetry(response))
        else:
            from siwc_login import access_token
            payload = v4.build_payload(request, model, v2._logged_actions(log))
            record["model_input"] = payload["input"][0]["content"][0]["text"]
            response, retries = call_with_retries(lambda: fetch(payload, access_token()))
            action = v1.parse_action(response, model, request["request_id"])
            record.update(v4.telemetry(response))
        record.update(retries=retries, action={key: action[key] for key in v2.ACTION_FIELDS},
                      usage=action["usage"], provider=action["provider"])
        with log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        json.dump(action, sys.stdout, allow_nan=False, separators=(",", ":"))
        sys.stdout.write("\n")
    except (v1.AdapterError, KeyError, TypeError, ValueError) as error:
        print(f"adapter_error:{error}", file=sys.stderr)
        raise SystemExit(2) from error


def main(study: str | None = None, study_file: str | None = None, arms: dict[str, Arm] | None = None) -> None:
    """CLI.  A study file calls ``main(name, __file__, ARMS)``; run directly, only ``act`` exists."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    adapter = commands.add_parser("act", help="adapter entry point used by the runner")
    adapter.add_argument("--model", choices=v1.MODELS + gemini.MODELS + openweight.MODELS, required=True)
    adapter.add_argument("--log", type=Path, required=True)
    adapter.add_argument("--mock", action="store_true")
    if arms:
        cells = commands.add_parser("run")
        cells.add_argument("--model", choices=v1.MODELS + gemini.MODELS + openweight.MODELS, required=True)
        cells.add_argument("--output", type=Path, required=True, help="new directory; an existing one is refused")
        cells.add_argument("--seed", type=int, required=True)
        cells.add_argument("--tasks-per-arm", type=int, required=True)
        cells.add_argument("--arms", nargs="+", choices=list(arms), default=list(arms))
        cells.add_argument("--continue-from", type=Path)
        cells.add_argument("--mock", action="store_true")
        scored = commands.add_parser("report")
        scored.add_argument("outputs", type=Path, nargs="+")
    args = parser.parse_args()
    if args.command == "act":
        act(args.model, args.log, args.mock)
    elif args.command == "report":
        print(json.dumps(report(load(args.outputs)), indent=2))
    else:
        run(study, Path(study_file).resolve(), arms, args.model, args.output, seed=args.seed,
            tasks_per_arm=args.tasks_per_arm, names=args.arms, mock=args.mock, continue_from=args.continue_from)
        print(json.dumps(report(load([args.output])), indent=2))


if __name__ == "__main__":
    main()
