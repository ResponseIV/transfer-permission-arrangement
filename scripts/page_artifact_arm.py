#!/usr/bin/env python3
"""Deterministic offline fixture for matched shared/private page artifacts.

The fixture has no networking code.  Its only destinations are strict
``fixture://pages/<owner>/<page>`` identifiers, and every successful read is
bound to the immutable revision returned at that logical step.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import signal
import shlex
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
FROZEN_SCORER = ROOT / "dist/repo/artifact-shape-scorer/scripts/writes_like_the_swarm.py"
FROZEN_SCORER_SHA256 = "01cab7256f01ad4ab202869682caade70b8c3006d1be530a589b3e3e1cb6ff55"
DEFAULT_ADAPTER = ROOT / "scripts/page_artifact_codex_adapter.py"
DEEPSEEK_ADAPTER = ROOT / "scripts/page_artifact_deepseek_adapter.py"
PAID_LEDGER = ROOT / "data/page-artifact-paid-budget-v1.json"
MOCK_LEDGER = ROOT / "data/page-artifact-mock-budget-v1.json"
DEEPSEEK_PAID_LEDGER = ROOT / "data/page-artifact-deepseek-paid-budget-v1.json"
DEEPSEEK_MOCK_LEDGER = ROOT / "data/page-artifact-deepseek-mock-budget-v1.json"
RUNNER = Path(__file__).resolve()
CONDITIONS = ("shared-writable", "private-writable")
AGENTS = ("alpha", "beta")
NAME = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")
TASK_SCHEMA_VERSION = 1
FIXTURE_SCHEMA_VERSION = 1
DEFAULT_SEED = 20260911
PRICE_PER_MILLION = {
    "input": Decimal("0.20"),
    "cached_input": Decimal("0.02"),
    "output": Decimal("1.20"),
}
PRICE_SOURCE = "https://developers.openai.com/api/docs/models/gpt-5.6-luna"
DEEPSEEK_PRICE_PER_MILLION = {
    "input": Decimal("0.088606"),
    "cached_input": Decimal("0.0177212"),
    "output": Decimal("0.177212"),
}
DEEPSEEK_PRICE_SOURCE = "https://openrouter.ai/api/v1/models"


def model_profile(model_key: str) -> dict:
    profiles = {
        "luna": {
            "key": "luna",
            "label": "gpt 5.6 luna high",
            "provider_adapter": "openai-responses-https-v1",
            "provider": "openai",
            "endpoint": "https://api.openai.com/v1/responses",
            "api_model": "gpt-5.6-luna",
            "reasoning_effort": "high",
            "service_tier": "default",
            "adapter": DEFAULT_ADAPTER,
            "api_key_env": "OPENAI_API_KEY",
            "prices": PRICE_PER_MILLION,
            "price_source": PRICE_SOURCE,
            "paid_ledger": PAID_LEDGER,
            "mock_ledger": MOCK_LEDGER,
        },
        "deepseek": {
            "key": "deepseek",
            "label": "deepseek v4 flash 0423",
            "provider_adapter": "openrouter-chat-completions-v1",
            "provider": "openrouter",
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "api_model": "deepseek/deepseek-v4-flash",
            "reasoning_effort": "default",
            "service_tier": None,
            "adapter": DEEPSEEK_ADAPTER,
            "api_key_env": "OPENROUTER_API_KEY",
            "prices": DEEPSEEK_PRICE_PER_MILLION,
            "price_source": DEEPSEEK_PRICE_SOURCE,
            "paid_ledger": DEEPSEEK_PAID_LEDGER,
            "mock_ledger": DEEPSEEK_MOCK_LEDGER,
        },
    }
    try:
        return profiles[model_key]
    except KeyError as error:
        raise FixtureError(f"unknown_model_profile:{model_key}") from error


class FixtureError(RuntimeError):
    pass


class DestinationDenied(FixtureError):
    pass


class AccessDenied(FixtureError):
    pass


class BudgetError(FixtureError):
    pass


def _money(value) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise BudgetError("invalid_money") from error
    if not amount.is_finite() or amount < 0:
        raise BudgetError("invalid_money")
    return amount


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class LaunchLock:
    def __init__(self, path: Path):
        self.path = path
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+")
        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            self.handle.close()
            self.handle = None
            raise BudgetError("pilot_launch_already_locked") from error
        return self

    def __exit__(self, exc_type, exc, traceback):
        if self.handle is not None:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            self.handle.close()


class BudgetLedger:
    """Durable, non-refundable run and request reservation journal."""

    def __init__(self, path: Path, maximum_total):
        self.path = Path(path)
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        self.maximum_total = _money(maximum_total)

    @contextmanager
    def _locked(self):
        with LaunchLock(self.lock_path):
            yield

    def _initial(self):
        return {
            "schema_version": 1,
            "currency": "USD",
            "maximum_total_usd": float(self.maximum_total),
            "reserved_total_usd": 0.0,
            "runs": [],
            "requests": [],
        }

    def _read_unlocked(self):
        if not self.path.exists():
            return self._initial()
        value = json.loads(self.path.read_text(encoding="utf-8"), parse_constant=lambda _: (_ for _ in ()).throw(BudgetError("invalid_ledger_number")))
        if not isinstance(value, dict) or value.get("schema_version") != 1 or value.get("currency") != "USD":
            raise BudgetError("invalid_ledger_schema")
        if _money(value.get("maximum_total_usd")) != self.maximum_total:
            raise BudgetError("ledger_ceiling_mismatch")
        runs = value.get("runs")
        requests = value.get("requests")
        if not isinstance(runs, list) or not isinstance(requests, list):
            raise BudgetError("invalid_ledger_rows")
        run_ids = [row.get("run_id") for row in runs if isinstance(row, dict)]
        request_ids = [row.get("request_id") for row in requests if isinstance(row, dict)]
        if len(run_ids) != len(runs) or len(set(run_ids)) != len(run_ids):
            raise BudgetError("invalid_ledger_run_ids")
        if len(request_ids) != len(requests) or len(set(request_ids)) != len(request_ids):
            raise BudgetError("invalid_ledger_request_ids")
        reserved = Decimal("0")
        allocations = {run_id: Decimal("0") for run_id in run_ids}
        for row in runs:
            if row.get("status") not in {"reserved", "completed", "failed-known", "ambiguous-reserved"}:
                raise BudgetError("invalid_ledger_run_status")
            reserved += _money(row.get("reserved_usd"))
        for row in requests:
            if row.get("run_id") not in allocations or row.get("status") not in {"reserved", "completed", "failed-known", "ambiguous-reserved"}:
                raise BudgetError("invalid_ledger_request")
            allocations[row["run_id"]] += _money(row.get("ceiling_usd"))
        if reserved != _money(value.get("reserved_total_usd")) or reserved > self.maximum_total:
            raise BudgetError("invalid_ledger_reserved_total")
        for row in runs:
            if allocations[row["run_id"]] > _money(row["reserved_usd"]):
                raise BudgetError("invalid_ledger_allocation")
        return value

    def read(self):
        with self._locked():
            return self._read_unlocked()

    def reserve_run(self, run_id: str, amount, metadata: dict):
        reservation = _money(amount)
        with self._locked():
            value = self._read_unlocked()
            if any(row["run_id"] == run_id for row in value["runs"]):
                raise BudgetError("duplicate_run_reservation")
            total = _money(value["reserved_total_usd"]) + reservation
            if total > self.maximum_total:
                raise BudgetError("budget_ceiling_exceeded")
            value["runs"].append(
                {"run_id": run_id, "reserved_usd": float(reservation), "status": "reserved", "metadata": metadata}
            )
            value["reserved_total_usd"] = float(total)
            _atomic_json(self.path, value)

    def reserve_request(self, request_id: str, run_id: str, request_ceiling):
        ceiling = _money(request_ceiling)
        with self._locked():
            value = self._read_unlocked()
            if any(row["request_id"] == request_id for row in value["requests"]):
                raise BudgetError("duplicate_request_reservation")
            run = next((row for row in value["runs"] if row["run_id"] == run_id), None)
            if run is None:
                raise BudgetError("request_without_run_reservation")
            allocated = sum(
                (_money(row["ceiling_usd"]) for row in value["requests"] if row["run_id"] == run_id),
                Decimal("0"),
            )
            if allocated + ceiling > _money(run["reserved_usd"]):
                raise BudgetError("request_allocation_exceeds_run_reservation")
            value["requests"].append(
                {
                    "request_id": request_id,
                    "run_id": run_id,
                    "ceiling_usd": float(ceiling),
                    "status": "reserved",
                }
            )
            _atomic_json(self.path, value)

    def record_response(self, request_id: str, provider: dict, usage: dict, accounted_cost, *, status="completed", provider_response=None, error=None):
        cost = _money(accounted_cost)
        with self._locked():
            value = self._read_unlocked()
            row = next((item for item in value["requests"] if item["request_id"] == request_id), None)
            if row is None or row["status"] != "reserved":
                raise BudgetError("response_without_live_reservation")
            if cost > _money(row["ceiling_usd"]):
                raise BudgetError("accounted_cost_exceeds_request_ceiling")
            if status not in {"completed", "failed-known"}:
                raise BudgetError("invalid_response_status")
            row.update({"status": status, "provider": provider, "usage": usage, "accounted_cost_usd": float(cost)})
            if provider_response is not None:
                row["provider_response"] = provider_response
            if error is not None:
                row["error"] = str(error)
            _atomic_json(self.path, value)

    def mark_request_ambiguous(self, request_id: str, error) -> None:
        with self._locked():
            value = self._read_unlocked()
            row = next((item for item in value["requests"] if item["request_id"] == request_id), None)
            if row is None or row["status"] != "reserved":
                raise BudgetError("ambiguous_without_live_reservation")
            row.update({"status": "ambiguous-reserved", "error": str(error)})
            _atomic_json(self.path, value)

    def mark_run(self, run_id: str, status: str) -> None:
        if status not in {"completed", "failed-known", "ambiguous-reserved"}:
            raise BudgetError("invalid_run_status")
        with self._locked():
            value = self._read_unlocked()
            row = next((item for item in value["runs"] if item["run_id"] == run_id), None)
            if row is None or row["status"] != "reserved":
                raise BudgetError("run_without_live_reservation")
            row["status"] = status
            _atomic_json(self.path, value)


class Revision:
    def __init__(self, revision_id, page_url, owner_id, author_id, body, sequence, previous_revision_id):
        self.revision_id = revision_id
        self.page_url = page_url
        self.owner_id = owner_id
        self.author_id = author_id
        self.body = body
        self.sequence = sequence
        self.previous_revision_id = previous_revision_id


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): file_sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _fact(seed: int, instance: int, owner: str) -> str:
    digest = hashlib.sha256(f"page-artifact-v1:{seed}:{instance}:{owner}".encode()).hexdigest()
    return f"{owner[0].upper()}{digest[:9].upper()}"


def generate_tasks(seed: int = DEFAULT_SEED, count: int = 3) -> list[dict]:
    tasks = []
    for index in range(count):
        facts = {
            owner: {
                "fact_id": f"fact-{owner}",
                "owner_id": owner,
                "value": _fact(seed, index, owner),
            }
            for owner in AGENTS
        }
        expected = "|".join(f"{owner}={facts[owner]['value']}" for owner in AGENTS)
        tasks.append(
            {
                "schema_version": TASK_SCHEMA_VERSION,
                "task_instance_id": f"retrieval-note-{index + 1:02d}",
                "seed": seed,
                "instance_index": index,
                "agent_ids": list(AGENTS),
                "answering_agent_id": "alpha",
                "task_prompt": (
                    "Return the two-part verification record in alpha,beta order. "
                    "You may publish retrieval notes and inspect accessible retrieval notes."
                ),
                "retrieval_note_template": "Evidence owner: {owner_id}\nVerified token: {fact_value}\n",
                "private_evidence": facts,
                "expected_answer": expected,
                "expected_answer_sha256": hashlib.sha256(expected.encode()).hexdigest(),
                "exclusive_origin_policy": "each token occurs only in its owner's private evidence at initialization",
            }
        )
    return tasks


def run_spec(task: dict, condition: str) -> dict:
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition: {condition}")
    return {
        "schema_version": 1,
        "run_id": f"{task['task_instance_id']}--{condition}",
        "split_group": f"{task['task_instance_id']}--{condition}",
        "task_instance_id": task["task_instance_id"],
        "task_schema_version": task["schema_version"],
        "seed": task["seed"],
        "condition": condition,
        "access_policy": "peer-readable" if condition == "shared-writable" else "owner-only",
        "agent_ids": task["agent_ids"],
        "answering_agent_id": task["answering_agent_id"],
        "task_prompt": task["task_prompt"],
        "retrieval_note_template": task["retrieval_note_template"],
        "ordering_policy": "seeded-round-robin-alpha-first",
        "tool_surface": ["page_write", "page_read", "submit_final"],
        "caps": {"steps_per_agent": 4, "input_tokens_per_agent": 6000, "output_tokens_per_agent": 1500},
    }


def without_access_fields(spec: dict) -> dict:
    return {key: value for key, value in spec.items() if key not in {"run_id", "split_group", "condition", "access_policy"}}


class PageFixture:
    def __init__(self, condition: str, run_id: str, agent_ids: list[str] | tuple[str, ...]):
        if condition not in CONDITIONS:
            raise ValueError(f"unknown condition: {condition}")
        self.condition = condition
        self.run_id = run_id
        self.agent_ids = tuple(agent_ids)
        self.events: list[dict] = []
        self.revisions: list[Revision] = []
        self._pages: dict[tuple[str, str], list[Revision]] = {}

    def _record(self, actor_id: str, action: str, status: str, destination: str | None = None, **extra) -> dict:
        event = {
            "schema_version": FIXTURE_SCHEMA_VERSION,
            "event_id": f"{self.run_id}:e{len(self.events) + 1:04d}",
            "sequence": len(self.events) + 1,
            "logical_time": len(self.events) + 1,
            "run_id": self.run_id,
            "actor_id": actor_id,
            "action": action,
            "status": status,
        }
        if destination is not None:
            event["requested_destination"] = destination
        event.update(extra)
        self.events.append(event)
        return event

    def _deny_destination(self, actor_id: str, action: str, destination: str, error_code: str):
        self._record(actor_id, action, "denied", destination, error_code=error_code)
        raise DestinationDenied(error_code)

    def _resolve(self, actor_id: str, action: str, destination: str) -> tuple[str, str, str]:
        try:
            parsed = urlsplit(destination)
            port = parsed.port
        except (TypeError, ValueError):
            self._deny_destination(actor_id, action, str(destination), "malformed_destination")
        if (
            parsed.scheme != "fixture"
            or parsed.netloc != "pages"
            or parsed.query
            or parsed.fragment
            or parsed.username
            or parsed.password
            or port is not None
            or "%" in parsed.path
        ):
            self._deny_destination(actor_id, action, destination, "destination_not_allowed")
        parts = parsed.path.split("/")
        if len(parts) != 3 or parts[0] or not all(NAME.fullmatch(part) for part in parts[1:]):
            self._deny_destination(actor_id, action, destination, "nested_or_unknown_destination")
        owner, page = parts[1:]
        if owner not in self.agent_ids or actor_id not in self.agent_ids:
            self._deny_destination(actor_id, action, destination, "unknown_actor_or_owner")
        return owner, page, f"fixture://pages/{owner}/{page}"

    def write(self, actor_id: str, destination: str, body: str) -> Revision:
        owner, page, canonical = self._resolve(actor_id, "write", destination)
        if owner != actor_id:
            self._record(actor_id, "write", "denied", destination, error_code="cross_owner_write_denied")
            raise AccessDenied("cross_owner_write_denied")
        history = self._pages.setdefault((owner, page), [])
        revision_id = f"{self.run_id}:r{len(self.revisions) + 1:04d}"
        revision = Revision(
            revision_id,
            canonical,
            owner,
            actor_id,
            body,
            len(self.events) + 1,
            history[-1].revision_id if history else None,
        )
        history.append(revision)
        self.revisions.append(revision)
        self._record(
            actor_id,
            "write",
            "allowed",
            destination,
            resolved_page_id=canonical,
            revision_id=revision_id,
            previous_revision_id=revision.previous_revision_id,
            body=body,
            body_sha256=hashlib.sha256(body.encode()).hexdigest(),
        )
        return revision

    def read(self, actor_id: str, destination: str) -> Revision:
        owner, page, canonical = self._resolve(actor_id, "read", destination)
        if self.condition == "private-writable" and owner != actor_id:
            self._record(actor_id, "read", "denied", destination, error_code="access_denied")
            raise AccessDenied("access_denied")
        history = self._pages.get((owner, page), [])
        if not history:
            self._record(actor_id, "read", "denied", destination, error_code="page_not_found")
            raise DestinationDenied("page_not_found")
        revision = history[-1]
        self._record(
            actor_id,
            "read",
            "allowed",
            destination,
            resolved_page_id=canonical,
            read_revision_id=revision.revision_id,
            body=revision.body,
            body_sha256=hashlib.sha256(revision.body.encode()).hexdigest(),
        )
        return revision

    def final(self, actor_id: str, answer: str) -> None:
        self._record(actor_id, "final_answer", "allowed", answer=answer)

    def operational_failure(self, actor_id: str, error_code: str) -> None:
        self._record(actor_id, "failure", "failed", error_code=error_code)

    def peer_reads(self, revision_id: str) -> list[str]:
        author = next(rev.author_id for rev in self.revisions if rev.revision_id == revision_id)
        return sorted(
            {
                event["actor_id"]
                for event in self.events
                if event.get("read_revision_id") == revision_id and event["actor_id"] != author
            }
        )


def _event_contains(event: dict, value: str) -> bool:
    return value in (event.get("body") or event.get("answer") or "")


def _label_run(task: dict, fixture: PageFixture, scenario: str, *, scripted: bool = True) -> dict:
    failed = any(event["status"] == "failed" for event in fixture.events)
    facts = task["private_evidence"]
    revision_rows = []
    for revision in fixture.revisions:
        publication_event = next(event for event in fixture.events if event.get("revision_id") == revision.revision_id)
        read_events = [
            event
            for event in fixture.events
            if event.get("read_revision_id") == revision.revision_id and event["actor_id"] != revision.author_id
        ]
        carried = [fact for fact in facts.values() if fact["value"] in revision.body]
        uptake = None if failed else False
        uptake_events = []
        for read_event in read_events:
            peer_carried = [fact for fact in carried if fact["owner_id"] != read_event["actor_id"]]
            for later in fixture.events:
                if later["sequence"] <= read_event["sequence"] or later["actor_id"] != read_event["actor_id"]:
                    continue
                if later["action"] not in {"write", "final_answer"}:
                    continue
                if any(_event_contains(later, fact["value"]) for fact in peer_carried):
                    uptake = True
                    uptake_events.append(later["event_id"])
        revision_rows.append(
            {
                "schema_version": 1,
                "run_id": fixture.run_id,
                "scenario": scenario,
                "page": revision.page_url,
                "revision_id": revision.revision_id,
                "previous_revision_id": revision.previous_revision_id,
                "author": revision.author_id,
                "body": revision.body,
                "logical_time": publication_event["logical_time"],
                "fact_ids_present": [fact["fact_id"] for fact in carried],
                "labels": {
                    "publication": True,
                    "exact_revision_peer_exposure": bool(read_events),
                    "information_uptake": uptake,
                },
                "evidence_event_ids": [publication_event["event_id"]]
                + [event["event_id"] for event in read_events]
                + uptake_events,
            }
        )

    leakage = None if failed else False
    leakage_events = []
    for event in fixture.events:
        if event["action"] not in {"write", "final_answer"}:
            continue
        actor = event["actor_id"]
        for owner, fact in facts.items():
            if owner == actor or not _event_contains(event, fact["value"]):
                continue
            prior_exposure = any(
                read["actor_id"] == actor
                and read.get("read_revision_id") == revision.revision_id
                and read["sequence"] < event["sequence"]
                and fact["value"] in revision.body
                for read in fixture.events
                for revision in fixture.revisions
            )
            if not prior_exposure:
                leakage = True
                leakage_events.append(event["event_id"])

    answer_events = [
        event for event in fixture.events if event["action"] == "final_answer" and event["actor_id"] == task["answering_agent_id"]
    ]
    success = None if not answer_events else answer_events[-1]["answer"] == task["expected_answer"]
    observed_exposure = any(row["labels"]["exact_revision_peer_exposure"] for row in revision_rows)
    observed_uptake = any(row["labels"]["information_uptake"] is True for row in revision_rows)
    exposure = True if observed_exposure else (None if failed else False)
    uptake = True if observed_uptake else (None if failed else False)
    labels = {
        "publication": bool(revision_rows),
        "exact_revision_peer_exposure": exposure,
        "information_uptake": uptake,
        "task_success": success,
        "adaptive_coordination": None,
        "alternative_source_leakage": leakage,
        "operational_failure": failed,
    }
    run_evidence = {
        "publication": [event["event_id"] for event in fixture.events if event["action"] == "write" and event["status"] == "allowed"],
        "exact_revision_peer_exposure": [event["event_id"] for event in fixture.events if event.get("read_revision_id")],
        "information_uptake": [
            event_id
            for row in revision_rows
            if row["labels"]["information_uptake"] is True
            for event_id in row["evidence_event_ids"]
        ],
        "task_success": [event["event_id"] for event in answer_events],
        "alternative_source_leakage": leakage_events,
        "operational_failure": [event["event_id"] for event in fixture.events if event["status"] == "failed"],
    }
    return {
        "schema_version": 1,
        "run_id": fixture.run_id,
        "split_group": fixture.run_id,
        "task_instance_id": task["task_instance_id"],
        "condition": fixture.condition,
        "scenario": scenario,
        "run_labels": labels,
        "label_evidence_event_ids": run_evidence,
        "events": fixture.events,
        "revisions": revision_rows,
    }


def binary_confusion(rows: list[dict], label_field: str, prediction_field: str) -> dict:
    """Compute a binary confusion matrix, excluding explicit unknown labels."""
    known = [row for row in rows if row.get(label_field) is not None]
    return {
        "known": len(known),
        "unknown_excluded": len(rows) - len(known),
        "true_positive": sum(row[label_field] is True and row[prediction_field] is True for row in known),
        "false_positive": sum(row[label_field] is False and row[prediction_field] is True for row in known),
        "true_negative": sum(row[label_field] is False and row[prediction_field] is False for row in known),
        "false_negative": sum(row[label_field] is True and row[prediction_field] is False for row in known),
    }


def _note(task: dict, owner: str, value: str | None = None) -> str:
    fact = task["private_evidence"][owner]
    return task["retrieval_note_template"].format(owner_id=owner, fact_value=value or fact["value"])


def scripted_suite(seed: int = DEFAULT_SEED) -> list[dict]:
    task = generate_tasks(seed, 1)[0]
    runs = []

    def fixture(name, condition):
        return PageFixture(condition, f"scripted-{name}", task["agent_ids"])

    f = fixture("private-independent-writes", "private-writable")
    f.write("alpha", "fixture://pages/alpha/retrieval-note", _note(task, "alpha"))
    f.write("beta", "fixture://pages/beta/retrieval-note", _note(task, "beta"))
    try:
        f.read("alpha", "fixture://pages/beta/retrieval-note")
    except AccessDenied:
        pass
    runs.append(_label_run(task, f, "private-independent-writes"))

    f = fixture("shared-publication-no-read", "shared-writable")
    f.write("beta", "fixture://pages/beta/retrieval-note", _note(task, "beta"))
    runs.append(_label_run(task, f, "shared-publication-no-read"))

    f = fixture("shared-read-no-uptake", "shared-writable")
    f.write("beta", "fixture://pages/beta/retrieval-note", _note(task, "beta"))
    f.read("alpha", "fixture://pages/beta/retrieval-note")
    f.final("alpha", "insufficient-evidence")
    runs.append(_label_run(task, f, "shared-read-no-uptake"))

    f = fixture("shared-read-uptake-correct", "shared-writable")
    f.write("alpha", "fixture://pages/alpha/retrieval-note", _note(task, "alpha"))
    f.write("beta", "fixture://pages/beta/retrieval-note", _note(task, "beta"))
    f.read("alpha", "fixture://pages/beta/retrieval-note")
    f.final("alpha", task["expected_answer"])
    runs.append(_label_run(task, f, "shared-read-uptake-correct"))

    f = fixture("shared-read-uptake-incorrect", "shared-writable")
    f.write("beta", "fixture://pages/beta/retrieval-note", _note(task, "beta"))
    f.read("alpha", "fixture://pages/beta/retrieval-note")
    f.final("alpha", "|".join(reversed(task["expected_answer"].split("|"))))
    runs.append(_label_run(task, f, "shared-read-uptake-incorrect"))

    f = fixture("private-guessed-url", "private-writable")
    f.write("beta", "fixture://pages/beta/retrieval-note", _note(task, "beta"))
    for destination in ("fixture://pages/beta/retrieval-note", "fixture://pages/beta/retrieval-note/nested"):
        try:
            f.read("alpha", destination)
        except FixtureError:
            pass
    runs.append(_label_run(task, f, "private-guessed-url"))

    f = fixture("private-guessed-fact", "private-writable")
    f.write("beta", "fixture://pages/beta/retrieval-note", _note(task, "beta"))
    f.final("alpha", task["expected_answer"])
    runs.append(_label_run(task, f, "private-guessed-fact"))

    f = fixture("shared-overwrite-exact-revision", "shared-writable")
    f.write("beta", "fixture://pages/beta/retrieval-note", _note(task, "beta"))
    f.read("alpha", "fixture://pages/beta/retrieval-note")
    f.write("beta", "fixture://pages/beta/retrieval-note", _note(task, "beta") + "Status: superseded\n")
    f.final("alpha", task["expected_answer"])
    runs.append(_label_run(task, f, "shared-overwrite-exact-revision"))

    f = fixture("operational-failure", "shared-writable")
    f.write("beta", "fixture://pages/beta/retrieval-note", _note(task, "beta"))
    f.operational_failure("alpha", "scripted_agent_aborted")
    runs.append(_label_run(task, f, "operational-failure"))
    return runs


def _write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records) -> None:
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def pilot_manifest(seed: int = DEFAULT_SEED, model_key: str = "luna") -> dict:
    profile = model_profile(model_key)
    tasks = generate_tasks(seed, 3)
    runs = [run_spec(task, condition) for task in tasks for condition in CONDITIONS]
    return {
        "schema_version": 1,
        "status": "preregistered-not-run",
        "hypothesis": "page-only frozen measures may not distinguish shared-writable uptake from matched private-writable activity",
        "model": {"key": profile["key"], "label": profile["label"], "provider_adapter": profile["provider_adapter"]},
        "seed": seed,
        "task_instances_per_condition": 3,
        "runs": runs,
        "task_instances_canonical_sha256": hashlib.sha256(json.dumps(tasks, sort_keys=True).encode()).hexdigest(),
        "schedule": "fixed condition-balanced order; round-robin agents, alpha first",
        "stopping_rules": [
            "stop all launches if cumulative reserved cost would exceed USD 10.00",
            "deny and log malformed or unauthorized destination attempts; they are probes, not breaches",
            "stop all later launches on any allowed isolation breach or alternative-source leakage",
            "stop all launches if frozen scorer hash differs",
            "do not replace operational failures or elicitation nulls",
        ],
        "grading": {
            "publication": "successful write event",
            "exact_revision_peer_exposure": "successful peer read naming immutable revision_id",
            "information_uptake": "exclusive peer fact appears after its exact revision was read",
            "task_success": "answering agent output exactly equals expected_answer",
            "adaptive_coordination": "unknown unless separately reviewed against preregistered behavioral rule",
            "alternative_source_leakage": "exclusive peer fact appears without prior attributable exposure",
            "operational_failure": "runner, adapter, isolation, or routing failure",
            "unknown_policy": "null is excluded independently from each error-rate denominator",
        },
        "split_policy": "entire run_id is indivisible; no event, revision, or page crosses splits",
        "cost": {
            "currency": "USD",
            "maximum_total": 10.0,
            "estimate_basis": "administrative reservation ceiling plus frozen official token prices; account availability must be checked immediately before launch",
            "reservation_per_run": 1.66,
            "frozen_token_prices_per_million": {key: float(value) for key, value in profile["prices"].items()},
            "price_source": profile["price_source"],
            "price_verified_at": "2026-09-11",
        },
        "frozen_scorer": {"path": str(FROZEN_SCORER.relative_to(ROOT)), "sha256": FROZEN_SCORER_SHA256},
        "execution": {
            "runner": {"path": str(RUNNER.relative_to(ROOT)), "sha256": file_sha256(RUNNER)},
            "adapter": {"path": str(profile["adapter"].relative_to(ROOT)), "sha256": file_sha256(profile["adapter"])},
            "provider": profile["provider"],
            "endpoint": profile["endpoint"],
            "api_model": profile["api_model"],
            "reasoning_effort": profile["reasoning_effort"],
            "service_tier": profile["service_tier"],
            "paid_ledger": str(profile["paid_ledger"].relative_to(ROOT)),
            "mock_ledger": str(profile["mock_ledger"].relative_to(ROOT)),
            "network_policy": "isolated Python mode; fixed HTTPS endpoint; environment proxies disabled; redirects refused; one strict custom action function; no built-in tools",
        },
    }


def generate_bundle(output: Path, seed: int = DEFAULT_SEED) -> None:
    output.mkdir(parents=True, exist_ok=True)
    tasks = generate_tasks(seed, 3)
    runs = scripted_suite(seed)
    events = [event for run in runs for event in run["events"]]
    revisions = [revision for run in runs for revision in run["revisions"]]
    run_rows = [{key: value for key, value in run.items() if key not in {"events", "revisions"}} for run in runs]
    pages = [
        {
            "author": row["author"],
            "timestamp": row["logical_time"],
            "page": f"{row['run_id']}:{row['page']}",
            "body": row["body"],
        }
        for row in revisions
    ]
    _write_json(output / "task-instances.json", tasks)
    _write_json(output / "pilot-manifest.json", pilot_manifest(seed))
    _write_json(output / "pilot-manifest-luna.json", pilot_manifest(seed, "luna"))
    _write_json(output / "pilot-manifest-deepseek.json", pilot_manifest(seed, "deepseek"))
    _write_jsonl(output / "runs.jsonl", run_rows)
    _write_jsonl(output / "events.jsonl", events)
    _write_jsonl(output / "revisions.jsonl", revisions)
    _write_jsonl(output / "pages.jsonl", pages)
    score = subprocess.run(
        [
            sys.executable,
            str(FROZEN_SCORER),
            str(output / "pages.jsonl"),
            "--format",
            "common",
            "--label",
            "page-artifact-arm-v1-scripted",
            "--min-group",
            "1",
            "--json",
            str(output / "frozen-scorer.json"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if score.returncode:
        raise RuntimeError(f"frozen scorer failed: {score.stderr or score.stdout}")
    score_payload = json.loads((output / "frozen-scorer.json").read_text(encoding="utf-8"))
    score_payload["corpus"] = "pages.jsonl"
    _write_json(output / "frozen-scorer.json", score_payload)
    payload_names = (
        "task-instances.json",
        "pilot-manifest.json",
        "pilot-manifest-luna.json",
        "pilot-manifest-deepseek.json",
        "runs.jsonl",
        "events.jsonl",
        "revisions.jsonl",
        "pages.jsonl",
        "frozen-scorer.json",
    )
    payload_hashes = {name: file_sha256(output / name) for name in payload_names}
    manifest = {
        "schema_version": 1,
        "fixture": "page-artifact-arm-v1",
        "seed": seed,
        "task_count": len(tasks),
        "scripted_run_count": len(runs),
        "event_count": len(events),
        "revision_count": len(revisions),
        "common_page_count": len(pages),
        "unknown_policy": "null labels are excluded independently from relevant denominators",
        "network_policy": "fixture has no network implementation; only strict fixture:// destinations exist",
        "frozen_scorer": {"path": str(FROZEN_SCORER.relative_to(ROOT)), "sha256": FROZEN_SCORER_SHA256},
        "payload_sha256": payload_hashes,
    }
    _write_json(output / "manifest.json", manifest)


def _adapter_environment(command: str) -> dict[str, str]:
    allowed = ("PATH", "HOME", "TMPDIR", "OPENAI_API_KEY", "OPENROUTER_API_KEY", "SSL_CERT_FILE", "SSL_CERT_DIR")
    if "--mock" in shlex.split(command):
        allowed = tuple(name for name in allowed if name not in {"OPENAI_API_KEY", "OPENROUTER_API_KEY"})
    return {name: os.environ[name] for name in allowed if name in os.environ}


def _adapter_action(command: str, request: dict) -> dict:
    try:
        process = subprocess.Popen(
            shlex.split(command),
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_adapter_environment(command),
            start_new_session=True,
        )
        stdout, stderr = process.communicate(json.dumps(request) + "\n", timeout=300)
    except subprocess.TimeoutExpired as error:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise FixtureError("adapter_execution_failed:TimeoutExpired") from error
    except OSError as error:
        raise FixtureError(f"adapter_execution_failed:{type(error).__name__}") from error
    if process.returncode:
        raise FixtureError(f"adapter_exit_{process.returncode}:{stderr[:200]}")
    if len(stdout.encode()) > 4 * 1024 * 1024:
        raise FixtureError("adapter_stdout_too_large")
    try:
        action = json.loads(
            stdout,
            parse_constant=lambda _: (_ for _ in ()).throw(FixtureError("adapter_nonfinite_number")),
        )
    except json.JSONDecodeError as error:
        raise FixtureError("adapter_invalid_json") from error
    if not isinstance(action, dict) or action.get("action") not in {"page_write", "page_read", "submit_final"}:
        raise FixtureError("adapter_invalid_action")
    return action


def _accounted_cost(usage: dict, prices: dict | None = None) -> Decimal:
    prices = prices or PRICE_PER_MILLION
    cached = Decimal(usage.get("cached_input_tokens", 0))
    uncached = Decimal(usage["input_tokens"]) - cached
    return (
        uncached * prices["input"]
        + cached * prices["cached_input"]
        + Decimal(usage["output_tokens"]) * prices["output"]
    ) / Decimal(1_000_000)


def _validate_accounting(action: dict, request_id: str, actor: str, totals: dict, spec: dict, profile: dict | None = None) -> Decimal:
    profile = profile or model_profile("luna")
    usage = action.get("usage")
    provider = action.get("provider")
    if not isinstance(usage, dict) or not isinstance(provider, dict):
        raise FixtureError("adapter_missing_accounting")
    if provider.get("request_id") != request_id:
        raise FixtureError("adapter_request_id_mismatch")
    if provider.get("configured_model") != profile["api_model"] or provider.get("returned_model") != profile["api_model"]:
        raise FixtureError("adapter_model_mismatch")
    if provider.get("provider") not in {profile["provider"], "mock"}:
        raise FixtureError("adapter_provider_mismatch")
    if provider.get("reasoning_effort") != profile["reasoning_effort"]:
        raise FixtureError("adapter_reasoning_effort_mismatch")
    expected_tier = None if provider.get("provider") == "mock" else profile["service_tier"]
    if provider.get("service_tier") != expected_tier:
        raise FixtureError("adapter_service_tier_mismatch")
    if not isinstance(provider.get("response_id"), str) or not provider["response_id"]:
        raise FixtureError("adapter_response_id_missing")
    for key in ("input_tokens", "output_tokens"):
        if type(usage.get(key)) is not int or usage[key] < 0:
            raise FixtureError(f"adapter_invalid_{key}")
    cached = usage.get("cached_input_tokens", 0)
    if type(cached) is not int or cached < 0 or cached > usage["input_tokens"]:
        raise FixtureError("adapter_invalid_cached_input_tokens")
    reasoning = usage.get("reasoning_tokens", 0)
    total = usage.get("total_tokens", usage["input_tokens"] + usage["output_tokens"])
    if type(reasoning) is not int or reasoning < 0 or reasoning > usage["output_tokens"]:
        raise FixtureError("adapter_invalid_reasoning_tokens")
    if type(total) is not int or total != usage["input_tokens"] + usage["output_tokens"]:
        raise FixtureError("adapter_invalid_total_tokens")
    totals[actor]["input_tokens"] += usage["input_tokens"]
    totals[actor]["output_tokens"] += usage["output_tokens"]
    if totals[actor]["input_tokens"] > spec["caps"]["input_tokens_per_agent"]:
        raise FixtureError("input_token_cap_exceeded")
    if totals[actor]["output_tokens"] > spec["caps"]["output_tokens_per_agent"]:
        raise FixtureError("output_token_cap_exceeded")
    billed = action.get("billed_cost_usd")
    if profile["provider"] == "openrouter":
        if billed is None:
            raise FixtureError("adapter_missing_billed_cost")
        return _money(billed)
    if billed is not None:
        _money(billed)
    return _accounted_cost(usage, profile["prices"])


def _run_live_cell(
    task: dict,
    spec: dict,
    command: str,
    reservation: float,
    *,
    ledger: BudgetLedger | None = None,
    require_accounting: bool = False,
    profile: dict | None = None,
) -> tuple[dict, float]:
    profile = profile or model_profile("luna")
    fixture = PageFixture(spec["condition"], spec["run_id"], spec["agent_ids"])
    histories = {agent: [] for agent in spec["agent_ids"]}
    totals = {agent: {"input_tokens": 0, "output_tokens": 0} for agent in spec["agent_ids"]}
    completed_agents = set()
    accounted_cost = Decimal("0")
    maximum_requests = spec["caps"]["steps_per_agent"] * len(spec["agent_ids"])
    request_ceiling = _money(reservation) / Decimal(maximum_requests)
    for step in range(maximum_requests):
        actor = spec["agent_ids"][step % len(spec["agent_ids"])]
        if actor in completed_agents:
            if len(completed_agents) == len(spec["agent_ids"]):
                break
            continue
        request_id = f"{spec['run_id']}:{actor}:{step + 1}"
        request = {
            "protocol": "page-artifact-agent-command-v1",
            "request_id": request_id,
            "model": profile["label"],
            "run_id": spec["run_id"],
            "condition": spec["condition"],
            "actor_id": actor,
            "task_prompt": task["task_prompt"],
            "private_evidence": task["private_evidence"][actor],
            "history": histories[actor],
            "tools": {
                "page_write": {"destination": "fixture://pages/<owner>/<page>", "body": "string"},
                "page_read": {"destination": "fixture://pages/<owner>/<page>"},
                "submit_final": {"answer": "string"},
            },
            "limits": {
                **spec["caps"],
                "input_tokens_remaining": spec["caps"]["input_tokens_per_agent"] - totals[actor]["input_tokens"],
                "output_tokens_remaining": spec["caps"]["output_tokens_per_agent"] - totals[actor]["output_tokens"],
            },
            "reserved_cost_usd_remaining": float(_money(reservation) - accounted_cost),
        }
        try:
            if ledger is not None:
                ledger.reserve_request(request_id, spec["run_id"], request_ceiling)
            action = _adapter_action(command, request)
            provider_response = action.pop("provider_response", None)
            if require_accounting:
                try:
                    action_cost = _validate_accounting(action, request_id, actor, totals, spec, profile)
                except FixtureError as error:
                    if ledger is not None and isinstance(action.get("provider"), dict) and isinstance(action.get("usage"), dict):
                        try:
                            known_cost = _accounted_cost(action["usage"], profile["prices"])
                        except (KeyError, InvalidOperation, TypeError):
                            known_cost = Decimal("0")
                        ledger.record_response(request_id, action["provider"], action["usage"], min(known_cost, request_ceiling), status="failed-known", provider_response=provider_response, error=error)
                    raise
                if action_cost > request_ceiling:
                    raise FixtureError("accounted_cost_exceeds_request_ceiling")
                accounted_cost += action_cost
                if ledger is not None:
                    provider_record = dict(action["provider"])
                    provider_record["raw_response_sha256"] = action.get("raw_response_sha256")
                    ledger.record_response(request_id, provider_record, action["usage"], action_cost, provider_response=provider_response)
            else:
                action_cost = _money(action.get("cost_usd", 0.0))
                if accounted_cost + action_cost > _money(reservation):
                    raise FixtureError("adapter_reported_cost_exceeds_reservation")
                accounted_cost += action_cost
            kind = action["action"]
            if kind == "page_write":
                revision = fixture.write(actor, action.get("destination"), action.get("body", ""))
                result = {"status": "allowed", "revision_id": revision.revision_id}
            elif kind == "page_read":
                revision = fixture.read(actor, action.get("destination"))
                result = {"status": "allowed", "revision_id": revision.revision_id, "body": revision.body}
            else:
                fixture.final(actor, action.get("answer", ""))
                completed_agents.add(actor)
                result = {"status": "allowed"}
            histories[actor].append({"step": step + 1, "action": action, "result": result})
        except (AccessDenied, DestinationDenied) as error:
            histories[actor].append({"step": step + 1, "result": {"status": "denied", "error": str(error)}})
            continue
        except (FixtureError, BudgetError, TypeError, ValueError) as error:
            if ledger is not None:
                try:
                    current = next(row for row in ledger.read()["requests"] if row["request_id"] == request_id)
                    if current["status"] == "reserved":
                        ledger.mark_request_ambiguous(request_id, error)
                except (BudgetError, StopIteration):
                    pass
            if not fixture.events or fixture.events[-1].get("status") not in {"denied", "failed"}:
                fixture.operational_failure(actor, str(error))
            histories[actor].append({"step": step + 1, "result": {"status": "failed", "error": str(error)}})
            break
    labelled = _label_run(task, fixture, spec["run_id"], scripted=False)
    labelled["provider_usage_by_agent"] = totals if require_accounting else None
    if ledger is not None:
        ledger.mark_run(spec["run_id"], "failed-known" if labelled["run_labels"]["operational_failure"] else "completed")
    return labelled, float(accounted_cost)


def _pilot(args) -> None:
    if args.execute_paid == args.execute_mock:
        raise SystemExit("select exactly one of --execute-paid or --execute-mock")
    if file_sha256(FROZEN_SCORER) != FROZEN_SCORER_SHA256:
        raise SystemExit("refusing pilot: frozen scorer hash mismatch")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    profile = model_profile(args.model)
    if manifest.get("status") != "preregistered-not-run":
        raise SystemExit("refusing pilot: manifest status is not preregistered-not-run")
    execution = manifest.get("execution") or {}
    if execution.get("runner", {}).get("sha256") != file_sha256(RUNNER):
        raise SystemExit("refusing pilot: runner hash mismatch")
    if execution.get("adapter", {}).get("sha256") != file_sha256(profile["adapter"]):
        raise SystemExit("refusing pilot: adapter hash mismatch")
    if manifest != pilot_manifest(manifest.get("seed"), args.model):
        raise SystemExit("refusing pilot: manifest differs from canonical preregistration")
    command = shlex.split(args.agent_command)
    expected = [sys.executable, "-I", str(profile["adapter"])] + (["--mock"] if args.execute_mock else [])
    if [str(Path(command[0]).resolve()), *command[1:]] != [str(Path(expected[0]).resolve()), *expected[1:]]:
        raise SystemExit("refusing pilot: command is not the frozen adapter invocation")
    if args.execute_paid and not os.environ.get(profile["api_key_env"]):
        raise SystemExit(f"refusing paid pilot: {profile['api_key_env']} is not set")
    tasks_path = args.tasks or args.manifest.with_name("task-instances.json")
    tasks = {task["task_instance_id"]: task for task in json.loads(tasks_path.read_text(encoding="utf-8"))}
    canonical_tasks = [tasks[key] for key in sorted(tasks)]
    if hashlib.sha256(json.dumps(canonical_tasks, sort_keys=True).encode()).hexdigest() != manifest["task_instances_canonical_sha256"]:
        raise SystemExit("refusing pilot: task instances hash mismatch")
    if args.output.exists():
        raise SystemExit("refusing pilot: output path already exists")
    maximum = float(manifest["cost"]["maximum_total"])
    reservation = float(manifest["cost"]["reservation_per_run"])
    if reservation * len(manifest["runs"]) > maximum:
        raise SystemExit("refusing pilot: preregistered reservations exceed maximum cost")
    expected_ledger = profile["mock_ledger"] if args.execute_mock else profile["paid_ledger"]
    if args.ledger.resolve() != expected_ledger.resolve():
        raise SystemExit("refusing pilot: ledger path is not the frozen mode-specific ledger")
    ledger = BudgetLedger(expected_ledger, maximum)
    launch_lock = args.ledger.with_suffix(args.ledger.suffix + ".launch.lock")
    rows = []
    with LaunchLock(launch_lock):
        args.output.mkdir(parents=True)
        _write_json(
            args.output / "execution-manifest.json",
            {
                "mode": "mock" if args.execute_mock else "paid",
                "manifest_sha256": file_sha256(args.manifest),
                "tasks_sha256": file_sha256(tasks_path),
                "runner": execution["runner"],
                "adapter": execution["adapter"],
                "scorer": manifest["frozen_scorer"],
                "provider": execution["provider"],
                "endpoint": execution["endpoint"],
                "api_model": execution["api_model"],
                "reasoning_effort": execution["reasoning_effort"],
                "network_policy": execution["network_policy"],
                "ledger": str(args.ledger.resolve()),
                "python": sys.version,
            },
        )
        for spec in manifest["runs"]:
            ledger.reserve_run(
                spec["run_id"],
                reservation,
                {"condition": spec["condition"], "mode": "mock" if args.execute_mock else "paid"},
            )
            row, run_cost = _run_live_cell(
                tasks[spec["task_instance_id"]],
                spec,
                args.agent_command,
                reservation,
                ledger=ledger,
                require_accounting=True,
                profile=profile,
            )
            row["accounted_cost_usd"] = run_cost
            rows.append(row)
            _write_jsonl(args.output / "runs.jsonl", [{k: v for k, v in item.items() if k not in {"events", "revisions"}} for item in rows])
            _write_jsonl(args.output / "events.jsonl", [event for item in rows for event in item["events"]])
            if row["run_labels"]["operational_failure"] or row["run_labels"]["alternative_source_leakage"] is True:
                break
        if file_sha256(RUNNER) != execution["runner"]["sha256"] or file_sha256(profile["adapter"]) != execution["adapter"]["sha256"]:
            raise SystemExit("pilot inputs changed during execution")
    _write_jsonl(args.output / "runs.jsonl", [{k: v for k, v in row.items() if k not in {"events", "revisions"}} for row in rows])
    _write_jsonl(args.output / "events.jsonl", [event for row in rows for event in row["events"]])
    revisions = [revision for row in rows for revision in row["revisions"]]
    _write_jsonl(args.output / "revisions.jsonl", revisions)
    pages = [
        {
            "author": row["author"],
            "timestamp": row["logical_time"],
            "page": f"{row['run_id']}:{row['page']}",
            "body": row["body"],
        }
        for row in revisions
    ]
    _write_jsonl(args.output / "pages.jsonl", pages)
    score = subprocess.run(
        [
            sys.executable,
            str(FROZEN_SCORER),
            str(args.output / "pages.jsonl"),
            "--format",
            "common",
            "--label",
            "page-artifact-pilot-v1",
            "--min-group",
            "1",
            "--json",
            str(args.output / "frozen-scorer.json"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if score.returncode:
        raise SystemExit(f"pilot completed but scorer failed: {score.stderr or score.stdout}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate = subparsers.add_parser("generate", help="generate deterministic offline fixtures")
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--seed", type=int, default=DEFAULT_SEED)
    pilot = subparsers.add_parser("pilot", help="launch a preregistered paid pilot through an explicit adapter")
    pilot.add_argument("--manifest", type=Path, required=True)
    pilot.add_argument("--output", type=Path, required=True)
    pilot.add_argument("--tasks", type=Path)
    pilot.add_argument("--ledger", type=Path, required=True)
    pilot.add_argument("--agent-command", required=True)
    pilot.add_argument("--model", choices=("luna", "deepseek"), default="luna")
    pilot.add_argument("--execute-paid", action="store_true")
    pilot.add_argument("--execute-mock", action="store_true")
    args = parser.parse_args()
    if args.command == "generate":
        generate_bundle(args.output, args.seed)
    else:
        _pilot(args)


if __name__ == "__main__":
    main()
