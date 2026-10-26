import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import page_artifact_plan_adapter as v1  # noqa: E402
import page_artifact_plan_v2 as v2  # noqa: E402

RUN = "retrieval-note-01--private-writable"
WRITE = {"action": "page_write", "destination": "fixture://pages/alpha/retrieval-note", "body": "x", "answer": None}
READ = {"action": "page_read", "destination": "fixture://pages/beta/retrieval-note", "body": None, "answer": None}


def request() -> dict:
    return {
        "protocol": "page-artifact-agent-command-v1", "request_id": f"{RUN}:alpha:5", "model": "gpt 5.6 luna high",
        "run_id": RUN, "condition": "private-writable", "actor_id": "alpha", "task_prompt": v2.task_prompt(True),
        "private_evidence": {"fact_id": "fact-alpha", "owner_id": "alpha", "value": "AAA"},
        "history": [
            {"step": 1, "action": {**WRITE, "usage": {}, "provider": {"request_id": f"{RUN}:alpha:1"}},
             "result": {"status": "allowed", "revision_id": f"{RUN}:r0001"}},
            {"step": 3, "result": {"status": "denied", "error": "access_denied"}},
        ],
        "tools": {"page_read": {"destination": "fixture://pages/<owner>/<page>"}},
        "limits": {"steps_per_agent": 4, "input_tokens_remaining": 10},
        "reserved_cost_usd_remaining": 0.0,
    }


class ModelView(unittest.TestCase):
    def setUp(self):
        self.text = v2.model_view(request(), {f"{RUN}:alpha:3": READ})
        self.view = json.loads(self.text)

    def test_condition_is_not_visible_anywhere(self):
        for leaked in ("private-writable", "shared-writable", RUN, "condition", "reserved_cost", "tokens"):
            self.assertNotIn(leaked, self.text)
        self.assertEqual(self.view["history"][0]["result"]["revision_id"], "run:r0001")

    def test_denied_attempt_shows_the_action_that_was_denied(self):
        self.assertEqual(self.view["history"][1], {"action": READ, "result": {"status": "denied", "error": "access_denied"}})
        self.assertEqual(self.view["history"][0]["action"], WRITE)

    def test_remaining_actions_count_denied_attempts(self):
        self.assertEqual(self.view["limits"], {"actions_per_agent": 4, "actions_remaining": 2})

    def test_payload_carries_only_the_view(self):
        payload = v2.build_payload(request(), "gpt-5.6-luna", {})
        self.assertNotIn("private-writable", json.dumps(payload))
        self.assertIn("alpha=<alpha's token>|beta=<beta's token>", json.dumps(payload))


class Retry(unittest.TestCase):
    def attempt(self, *outcomes):
        queue, slept = list(outcomes), []

        def call():
            outcome = queue.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome
        return v2.call_with_retry(call, sleep=slept.append), slept

    def test_transport_failure_is_retried_once(self):
        result, slept = self.attempt(v1.AdapterError("provider_http_503:upstream"), {"ok": 1})
        self.assertEqual((result, slept), (({"ok": 1}, 1), [v2.RETRY_DELAY_SECONDS]))

    def test_second_transport_failure_propagates(self):
        with self.assertRaisesRegex(v1.AdapterError, "provider_request_failed"):
            self.attempt(v1.AdapterError("provider_http_502:x"), v1.AdapterError("provider_request_failed:URLError"))

    def test_model_and_limit_errors_are_not_retried(self):
        for message in ("expected_exactly_one_action", "provider_http_429:limit",
                        "response.failed:subscription_sharing_usage_limit_exceeded"):
            with self.subTest(message), self.assertRaisesRegex(v1.AdapterError, message.split(":")[0]):
                self.attempt(v1.AdapterError(message), {"ok": 1})


class ContentGrade(unittest.TestCase):
    TASK = {"answering_agent_id": "alpha", "agent_ids": ["alpha", "beta"],
            "private_evidence": {"alpha": {"value": "AAA"}, "beta": {"value": "BBB"}}}

    def grade(self, *answers):
        return v2.content_correct(self.TASK, [{"action": "final_answer", "actor_id": actor, "answer": answer}
                                              for actor, answer in answers])

    def test_grades_tokens_and_order_not_format(self):
        self.assertTrue(self.grade(("alpha", "AAA,BBB")))
        self.assertTrue(self.grade(("alpha", "alpha=AAA|beta=BBB")))
        self.assertFalse(self.grade(("alpha", "BBB,AAA")))
        self.assertFalse(self.grade(("alpha", "AAA")))
        self.assertIsNone(self.grade(("beta", "AAA,BBB")))


class MockRun(unittest.TestCase):
    @unittest.skipUnless(v2.arm.FROZEN_SCORER.exists(), "the prior-work scorer is not in this repository")
    def test_cells_are_summarised_per_condition(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            cells = v2.run("gpt-5.6-luna", output, seed=7, tasks_per_condition=2, naming_hint=True, mock=True)
            self.assertEqual([cell["condition"] for cell in cells], ["shared-writable", "private-writable"] * 2)
            shared, private = cells[0], cells[1]
            self.assertTrue(shared["information_uptake"] and shared["task_success"] and shared["answer_content_correct"])
            self.assertEqual((private["peer_read_attempts"], private["peer_read_denials"]), (3, 3))
            self.assertFalse(private["answer_submitted"])
            self.assertFalse(any(cell["operational_failure"] for cell in cells))
            for condition in ("shared-writable", "private-writable"):
                self.assertTrue((output / f"frozen-scorer-{condition}.json").exists())
            self.assertEqual(json.loads((output / "manifest.json").read_text())["task_version"], 2)


if __name__ == "__main__":
    unittest.main()
