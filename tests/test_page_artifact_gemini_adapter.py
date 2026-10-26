import hashlib
import http.client
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import page_artifact_gemini_adapter as gemini  # noqa: E402
import page_artifact_plan_adapter as v1  # noqa: E402

MODEL = gemini.MODELS[0]
KEY = "fake-key-for-tests"


def response(arguments=None) -> dict:
    return {
        "responseId": "resp-1", "modelVersion": MODEL,
        "candidates": [{"finishReason": "STOP", "content": {"role": "model", "parts": [
            {"text": "Choose the final answer.", "thought": True, "thoughtSignature": "opaque"},
            {"functionCall": {"name": "next_action", "args": arguments if arguments is not None else {
                "action": "submit_final", "destination": None, "body": None, "answer": "ok"}}},
        ]}}],
        "usageMetadata": {"promptTokenCount": 10, "cachedContentTokenCount": 2,
                          "candidatesTokenCount": 5, "thoughtsTokenCount": 3, "totalTokenCount": 18},
    }


def http_error(code, detail) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://example.invalid", code, "failure", {}, io.BytesIO(detail.encode()))


class Payload(unittest.TestCase):
    def test_shape_and_schema(self):
        for model in gemini.MODELS:
            with self.subTest(model):
                payload = gemini.build_payload("exact user text", model)
                self.assertEqual(payload["contents"], [{"role": "user", "parts": [{"text": "exact user text"}]}])
                self.assertEqual(payload["systemInstruction"], {"parts": [{"text": v1.INSTRUCTIONS}]})
                declarations = payload["tools"][0]["functionDeclarations"]
                self.assertEqual(len(declarations), 1)
                self.assertEqual(declarations[0]["name"], "next_action")
                schema = declarations[0]["parameters"]
                self.assertNotIn("additionalProperties", schema)
                self.assertEqual(schema["required"], ["action", "destination", "body", "answer"])
                self.assertEqual(schema["properties"]["action"]["enum"], list(v1.ACTION_NAMES))
                for name in ("destination", "body", "answer"):
                    self.assertEqual(schema["properties"][name], {"type": "string", "nullable": True})
                self.assertEqual(payload["toolConfig"]["functionCallingConfig"],
                                 {"mode": "ANY", "allowedFunctionNames": ["next_action"]})
                self.assertEqual(payload["generationConfig"], {"thinkingConfig": {"includeThoughts": True}})
        self.assertIn("additionalProperties", v1.action_schema())

    def test_unknown_model(self):
        with self.assertRaisesRegex(v1.AdapterError, "unknown_model"):
            gemini.build_payload("text", "unknown")


class Credentials(unittest.TestCase):
    def test_environment_takes_precedence(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(gemini, "ROOT", Path(directory)), \
                patch.dict(os.environ, {"GEMINI_API_KEY": KEY}):
            (Path(directory) / ".env").write_text("GEMINI_API_KEY=file-key\n")
            self.assertEqual(gemini.api_key(), KEY)

    def test_dotenv_at_repo_root(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(gemini, "ROOT", Path(directory)), \
                patch.dict(os.environ, {}, clear=True):
            for value in ("file-key", "'file-key'", '"file-key"'):
                with self.subTest(value):
                    (Path(directory) / ".env").write_text(f"OTHER_KEY=ignored\nGEMINI_API_KEY={value}\n")
                    self.assertEqual(gemini.api_key(), "file-key")

    def test_missing_or_empty_key(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(gemini, "ROOT", Path(directory)), \
                patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(v1.AdapterError, "^GEMINI_API_KEY_not_set$"):
                gemini.api_key()
            (Path(directory) / ".env").write_text("GEMINI_API_KEY=''\n")
            with self.assertRaisesRegex(v1.AdapterError, "^GEMINI_API_KEY_not_set$"):
                gemini.api_key()


class Action(unittest.TestCase):
    def test_action_identity_and_hash(self):
        raw = response()
        action = gemini.parse_action(raw, MODEL, "req-1")
        self.assertEqual(set(action), {"action", "destination", "body", "answer", "usage", "provider", "raw_response_sha256"})
        self.assertEqual((action["action"], action["answer"]), ("submit_final", "ok"))
        self.assertEqual(action["provider"], {
            "provider": "google-gemini-api", "endpoint": "generateContent", "configured_model": MODEL,
            "returned_model": MODEL, "reasoning_effort": "default", "response_id": "resp-1",
            "request_id": "req-1", "service_tier": None,
        })
        self.assertEqual(action["raw_response_sha256"], hashlib.sha256(
            json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest())

    def test_omitted_null_fields_for_all_actions(self):
        for arguments in ({"action": "submit_final", "answer": "ok"},
                          {"action": "page_read", "destination": "fixture://pages/alpha/note"},
                          {"action": "page_write", "destination": "fixture://pages/alpha/note", "body": "note"}):
            with self.subTest(arguments):
                raw = response(arguments)
                action = gemini.parse_action(raw, MODEL, "req-1")
                for field in ("destination", "body", "answer"):
                    self.assertEqual(action[field], arguments.get(field))
                self.assertEqual(raw["candidates"][0]["content"]["parts"][1]["functionCall"]["args"], arguments)

    def test_wrong_function_name(self):
        raw = response()
        raw["candidates"][0]["content"]["parts"][1]["functionCall"]["name"] = "other"
        with self.assertRaisesRegex(v1.AdapterError, "expected_exactly_one_action"):
            gemini.parse_action(raw, MODEL, "req-1")

    def test_two_calls(self):
        raw = response()
        raw["candidates"][0]["content"]["parts"].append(raw["candidates"][0]["content"]["parts"][1])
        with self.assertRaisesRegex(v1.AdapterError, "expected_exactly_one_action"):
            gemini.parse_action(raw, MODEL, "req-1")

    def test_multiple_candidates(self):
        raw = response()
        raw["candidates"].append(raw["candidates"][0])
        with self.assertRaisesRegex(v1.AdapterError, "expected_exactly_one_action"):
            gemini.parse_action(raw, MODEL, "req-1")

    def test_incoherent_fields(self):
        for arguments in ({"action": "submit_final", "answer": "ok", "body": "extra"},
                          {"action": "page_write", "destination": "note"}):
            with self.subTest(arguments), self.assertRaisesRegex(v1.AdapterError, "incoherent_action_fields"):
                gemini.parse_action(response(arguments), MODEL, "req-1")

    def test_invalid_fields_and_arguments(self):
        for arguments, error in (({"action": "shell"}, "invalid_action"),
                                 ({"action": "submit_final", "answer": "ok", "extra": None}, "invalid_action"),
                                 ({"action": "submit_final", "answer": 3}, "invalid_action_field_type"),
                                 ("not an object", "invalid_action_arguments")):
            with self.subTest(arguments), self.assertRaisesRegex(v1.AdapterError, f"^{error}$"):
                gemini.parse_action(response(arguments), MODEL, "req-1")

    def test_response_identity_errors(self):
        for field, value, error in (("responseId", "", "missing_response_id"),
                                    ("modelVersion", "other", "returned_model_mismatch")):
            raw = response()
            raw[field] = value
            with self.subTest(field), self.assertRaisesRegex(v1.AdapterError, error):
                gemini.parse_action(raw, MODEL, "req-1")

    def test_blocked_prompt(self):
        with self.assertRaisesRegex(v1.AdapterError, "^provider_blocked:SAFETY$"):
            gemini.parse_action({"promptFeedback": {"blockReason": "SAFETY"}}, MODEL, "req-1")

    def test_blocked_candidate(self):
        for reason in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "RECITATION"):
            raw = response()
            raw["candidates"][0]["finishReason"] = reason
            with self.subTest(reason), self.assertRaisesRegex(v1.AdapterError, f"^provider_blocked:{reason}$"):
                gemini.parse_action(raw, MODEL, "req-1")

    def test_usage_mapping(self):
        self.assertEqual(gemini.parse_action(response(), MODEL, "req-1")["usage"], {
            "input_tokens": 10, "cached_input_tokens": 2, "output_tokens": 8,
            "reasoning_tokens": 3, "total_tokens": 18,
        })

    def test_optional_usage_counts_default_to_zero(self):
        raw = response()
        raw["usageMetadata"] = {"promptTokenCount": 10, "candidatesTokenCount": 5, "totalTokenCount": 15}
        usage = gemini.parse_action(raw, MODEL, "req-1")["usage"]
        self.assertEqual((usage["cached_input_tokens"], usage["reasoning_tokens"]), (0, 0))

    def test_invalid_usage(self):
        for field, value, error in (("thoughtsTokenCount", -1, "invalid_usage"),
                                    ("candidatesTokenCount", True, "invalid_usage"),
                                    ("cachedContentTokenCount", 11, "invalid_cached_input_tokens"),
                                    ("totalTokenCount", 99, "invalid_total_tokens")):
            raw = response()
            raw["usageMetadata"][field] = value
            with self.subTest(field), self.assertRaisesRegex(v1.AdapterError, error):
                gemini.parse_action(raw, MODEL, "req-1")

    def test_telemetry_keeps_summary_but_not_signature(self):
        telemetry = gemini.telemetry(response())
        self.assertEqual(set(telemetry), {"reasoning_summary", "output_items"})
        self.assertEqual(telemetry["reasoning_summary"], ["Choose the final answer."])
        self.assertEqual(len(telemetry["output_items"]), 2)
        self.assertNotIn("thoughtSignature", telemetry["output_items"][0])


class Transport(unittest.TestCase):
    def setUp(self):
        self.opener = Mock()
        self.success = io.BytesIO(json.dumps(response()).encode())
        self.opener.open.return_value = self.success
        self.slept = []
        self.addCleanup(patch.stopall)
        patch.object(gemini.urllib.request, "build_opener", return_value=self.opener).start()
        patch.dict(os.environ, {"GEMINI_MIN_INTERVAL_SECONDS": "6"}).start()

    def call(self):
        return gemini.call("text", MODEL, KEY, sleep=self.slept.append)

    def test_key_is_only_in_header(self):
        self.assertEqual(self.call(), (response(), 0))
        request = self.opener.open.call_args.args[0]
        self.assertEqual(request.full_url, gemini.ENDPOINT.format(model=MODEL))
        self.assertNotIn(KEY, request.full_url)
        self.assertNotIn(KEY, request.data.decode())
        self.assertEqual(request.get_header("X-goog-api-key"), KEY)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(self.opener.open.call_args.kwargs, {"timeout": 300.0})
        self.assertEqual(self.slept, [6])

    def test_rate_limit_honours_retry_delay(self):
        detail = json.dumps({"error": {"details": [{"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "42s"}]}})
        self.opener.open.side_effect = [http_error(429, detail), self.success]
        self.assertEqual(self.call(), (response(), 1))
        self.assertEqual(self.slept, [6, 42, 6])

    def test_gives_up_after_four_retries(self):
        self.opener.open.side_effect = [http_error(429, "limit") for _ in range(5)]
        with self.assertRaisesRegex(v1.AdapterError, "^provider_http_429:limit$"):
            self.call()
        self.assertEqual(self.opener.open.call_count, 5)
        self.assertEqual(self.slept, [6, 15, 6, 30, 6, 45, 6, 60, 6])
        self.assertLess(sum(self.slept), 300)

    def test_server_error_retries_and_delay_cap(self):
        self.opener.open.side_effect = [http_error(500, "failure"),
                                       http_error(503, '{"error":{"details":[{"retryDelay":"900s"}]}}'), self.success]
        self.assertEqual(self.call(), (response(), 2))
        self.assertEqual(self.slept, [6, 15, 6, 60, 6])

    def test_key_scrubbed_before_error_truncation(self):
        self.opener.open.side_effect = http_error(403, "x" * 490 + KEY + "y" * 600)
        with self.assertRaises(v1.AdapterError) as caught:
            self.call()
        self.assertNotIn(KEY, str(caught.exception))
        self.assertIn("[redacted]", str(caught.exception))
        self.assertEqual(len(str(caught.exception).split(":", 1)[1]), 500)
        self.assertEqual(self.opener.open.call_count, 1)

    def test_transport_faults_are_adapter_errors(self):
        for error in (urllib.error.URLError(KEY), http.client.IncompleteRead(b"partial"), TimeoutError(KEY), OSError(KEY)):
            self.opener.open.side_effect = error
            with self.subTest(type(error)), self.assertRaisesRegex(
                    v1.AdapterError, f"^provider_request_failed:{type(error).__name__}$"):
                self.call()

    def test_error_body_read_fault_is_adapter_error(self):
        error = http_error(429, "limit")
        error.read = Mock(side_effect=http.client.IncompleteRead(b"partial"))
        self.opener.open.side_effect = error
        with self.assertRaisesRegex(v1.AdapterError, "provider_request_failed:IncompleteRead"):
            self.call()

    def test_invalid_json_and_oversized_response(self):
        for body, error in ((b"broken", "provider_invalid_json"), (b"[]", "provider_invalid_json"),
                            (b"x" * (v1.MAX_RESPONSE_BYTES + 1), "provider_response_too_large")):
            self.opener.open.return_value = io.BytesIO(body)
            with self.subTest(error), self.assertRaisesRegex(v1.AdapterError, error):
                self.call()

    def test_interval_override(self):
        with patch.dict(os.environ, {"GEMINI_MIN_INTERVAL_SECONDS": "0.25"}):
            self.call()
        self.assertEqual(self.slept, [0.25])

    def test_blocked_response_is_not_retried(self):
        self.opener.open.return_value = io.BytesIO(b'{"promptFeedback":{"blockReason":"SAFETY"}}')
        raw, retries = self.call()
        with self.assertRaisesRegex(v1.AdapterError, "provider_blocked:SAFETY"):
            gemini.parse_action(raw, MODEL, "req-1")
        self.assertEqual((retries, self.opener.open.call_count), (0, 1))


if __name__ == "__main__":
    unittest.main()
