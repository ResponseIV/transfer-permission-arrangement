#!/usr/bin/env python3
"""Single-request Gemini adapter for page-artifact runs."""

from __future__ import annotations

import hashlib
import http.client
import json
import math
import os
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

import page_artifact_plan_adapter as v1

MODELS = ("gemini-3.1-pro-preview", "gemini-3.8-flash")
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
ROOT = Path(__file__).resolve().parents[1]
# The runner kills an action after 300 seconds: pauses and waits must fit inside that.
RETRY_DELAYS_SECONDS = (15, 30, 45, 60)
MAX_RETRY_DELAY_SECONDS = 60
BLOCK_REASONS = {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "RECITATION", "SPII", "IMAGE_SAFETY", "MODEL_ARMOR"}


def api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    path = ROOT / ".env"
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            name, separator, value = line.strip().partition("=")
            if separator and name == "GEMINI_API_KEY":
                key = value.strip().strip("\"'")
                if key:
                    return key
    raise v1.AdapterError("GEMINI_API_KEY_not_set")


def build_payload(text: str, model: str) -> dict:
    if model not in MODELS:
        raise v1.AdapterError("unknown_model")
    schema = v1.action_schema()
    schema.pop("additionalProperties")
    for field in schema["properties"].values():
        if isinstance(field["type"], list):
            field.update(type="string", nullable=True)
    return {
        "systemInstruction": {"parts": [{"text": v1.INSTRUCTIONS}]},
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "tools": [{"functionDeclarations": [{
            "name": "next_action",
            "description": "Return one page_write, page_read, or submit_final fixture action.",
            "parameters": schema,
        }]}],
        "toolConfig": {"functionCallingConfig": {"mode": "ANY", "allowedFunctionNames": ["next_action"]}},
        "generationConfig": {"thinkingConfig": {"includeThoughts": True}},
    }


def _usage(response: dict) -> dict:
    usage = response.get("usageMetadata")
    if not isinstance(usage, dict):
        raise v1.AdapterError("missing_usage")
    output, thoughts = usage.get("candidatesTokenCount", 0), usage.get("thoughtsTokenCount", 0)
    if any(type(value) is not int or value < 0 for value in (output, thoughts)):
        raise v1.AdapterError("invalid_usage")
    return v1._usage({"usage": {
        "input_tokens": usage.get("promptTokenCount"),
        "input_tokens_details": {"cached_tokens": usage.get("cachedContentTokenCount", 0)},
        "output_tokens": output + thoughts,
        "output_tokens_details": {"reasoning_tokens": thoughts},
        "total_tokens": usage.get("totalTokenCount"),
    }})


def parse_action(response: dict, model: str, request_id: str) -> dict:
    reason = (response.get("promptFeedback") or {}).get("blockReason")
    candidates = response.get("candidates") or []
    reason = reason or next((candidate.get("finishReason") for candidate in candidates
                             if candidate.get("finishReason") in BLOCK_REASONS), None)
    if reason:
        raise v1.AdapterError(f"provider_blocked:{reason}")
    if not isinstance(response.get("responseId"), str) or not response["responseId"]:
        raise v1.AdapterError("missing_response_id")
    if not str(response.get("modelVersion", "")).startswith(model):
        raise v1.AdapterError("returned_model_mismatch")
    parts = [part for candidate in candidates for part in (candidate.get("content") or {}).get("parts", [])
             if not part.get("thought")]
    if len(candidates) != 1 or len(parts) != 1 or (parts[0].get("functionCall") or {}).get("name") != "next_action":
        raise v1.AdapterError("expected_exactly_one_action")
    arguments = parts[0]["functionCall"].get("args")
    if not isinstance(arguments, dict):
        raise v1.AdapterError("invalid_action_arguments")
    fields = ("destination", "body", "answer")
    action = {**dict.fromkeys(fields), **arguments}
    if set(action) != {"action", *fields} or action.get("action") not in v1.ACTION_NAMES:
        raise v1.AdapterError("invalid_action")
    if any(action[key] is not None and not isinstance(action[key], str) for key in fields):
        raise v1.AdapterError("invalid_action_field_type")
    if any((action[key] is not None) != (key in v1.NON_NULL_FIELDS[action["action"]]) for key in fields):
        raise v1.AdapterError("incoherent_action_fields")
    action["usage"] = _usage(response)
    action["provider"] = {
        "provider": "google-gemini-api", "endpoint": "generateContent",
        "configured_model": model, "returned_model": response["modelVersion"],
        "reasoning_effort": "default", "response_id": response["responseId"],
        "request_id": request_id, "service_tier": None,
    }
    action["raw_response_sha256"] = hashlib.sha256(
        json.dumps(response, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return action


def telemetry(response: dict) -> dict:
    items = [{key: value for key, value in part.items() if key != "thoughtSignature"}
             for candidate in response.get("candidates", []) for part in (candidate.get("content") or {}).get("parts", [])]
    return {"reasoning_summary": [part.get("text", "") for part in items if part.get("thought")],
            "output_items": items}


def _retry_delay(detail: str, default: int) -> float:
    try:
        details = json.loads(detail)["error"].get("details", [])
        for item in details:
            if "retryDelay" in item:
                delay = float(item["retryDelay"].removesuffix("s"))
                if math.isfinite(delay) and delay >= 0:
                    return min(delay, MAX_RETRY_DELAY_SECONDS)
    except (KeyError, TypeError, ValueError, AttributeError):
        pass
    return default


def call(text: str, model: str, key: str, timeout: float = 300.0, sleep=time.sleep) -> tuple[dict, int]:
    http_request = urllib.request.Request(
        ENDPOINT.format(model=model), data=json.dumps(build_payload(text, model), separators=(",", ":")).encode(),
        method="POST", headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    try:
        interval = float(os.environ.get("GEMINI_MIN_INTERVAL_SECONDS", "6"))
        if not math.isfinite(interval) or interval < 0:
            raise ValueError
    except ValueError as error:
        raise v1.AdapterError("invalid_min_interval") from error
    try:
        opener = urllib.request.build_opener(
            *v1.network_handlers(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        for retries in range(len(RETRY_DELAYS_SECONDS) + 1):
            sleep(interval)
            try:
                with opener.open(http_request, timeout=timeout) as stream:
                    body = stream.read(v1.MAX_RESPONSE_BYTES + 1)
            except urllib.error.HTTPError as error:
                detail = error.read(v1.MAX_RESPONSE_BYTES).decode("utf-8", "replace").replace(key, "[redacted]")
                if error.code not in {429, 500, 503} or retries == len(RETRY_DELAYS_SECONDS):
                    raise v1.AdapterError(f"provider_http_{error.code}:{detail[:500]}") from None
                sleep(_retry_delay(detail, RETRY_DELAYS_SECONDS[retries]))
                continue
            if len(body) > v1.MAX_RESPONSE_BYTES:
                raise v1.AdapterError("provider_response_too_large")
            try:
                response = json.loads(body)
            except (ValueError, UnicodeError) as error:
                raise v1.AdapterError("provider_invalid_json") from error
            if not isinstance(response, dict):
                raise v1.AdapterError("provider_invalid_json")
            return response, retries
    except (urllib.error.URLError, http.client.HTTPException, OSError) as error:
        raise v1.AdapterError(f"provider_request_failed:{type(error).__name__}") from None
