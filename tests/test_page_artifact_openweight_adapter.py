import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import page_artifact_openweight_adapter as openweight  # noqa: E402
import page_artifact_plan_adapter as v1  # noqa: E402


def response(arguments, model="qwen3-32b", calls=1):
    call = {"type": "function", "function": {"name": "next_action", "arguments": json.dumps(arguments)}}
    return {"id": "chatcmpl-1", "model": model,
            "choices": [{"message": {"role": "assistant", "reasoning_content": "thinking", "tool_calls": [call] * calls}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 40, "total_tokens": 140}}


READ = {"action": "page_read", "destination": "fixture://pages/beta/retrieval-note", "body": None, "answer": None}


class Adapter(unittest.TestCase):
    def test_the_action_is_one_forced_call_of_next_action(self):
        payload = openweight.build_payload("text", "qwen3-32b")
        self.assertEqual(payload["tool_choice"]["function"]["name"], "next_action")
        self.assertEqual(payload["messages"][0]["content"], v1.INSTRUCTIONS)

    def test_a_tool_call_becomes_the_action_with_usage_and_provenance(self):
        action = openweight.parse_action(response(READ), "qwen3-32b", "r1")
        self.assertEqual((action["action"], action["destination"]), ("page_read", READ["destination"]))
        self.assertEqual((action["usage"]["input_tokens"], action["usage"]["output_tokens"]), (100, 40))
        self.assertEqual(action["provider"]["returned_model"], "qwen3-32b")

    def test_another_model_or_two_calls_are_refused(self):
        with self.assertRaises(v1.AdapterError):
            openweight.parse_action(response(READ, model="other"), "qwen3-32b", "r1")
        with self.assertRaises(v1.AdapterError):
            openweight.parse_action(response(READ, calls=2), "qwen3-32b", "r1")

    def test_fields_must_match_the_action(self):
        with self.assertRaises(v1.AdapterError):
            openweight.parse_action(response({**READ, "answer": "alpha=1|beta=2"}), "qwen3-32b", "r1")

    def test_reasoning_is_kept_as_telemetry(self):
        self.assertEqual(openweight.telemetry(response(READ))["reasoning_summary"], ["thinking"])


class Judge(unittest.TestCase):
    def test_the_judge_call_sends_the_judge_instructions_and_returns_the_message_text(self):
        sent = {}

        def post(payload, *args):
            sent.update(payload)
            return {"model": "qwen3-32b", "choices": [{"message": {"content": '{"moved": true}'}}]}, 0

        original, openweight.post = openweight.post, post
        try:
            self.assertEqual(openweight.ask("prompt", "qwen3-32b"), '{"moved": true}')
        finally:
            openweight.post = original
        self.assertEqual(sent["messages"][0]["content"], openweight.JUDGE_INSTRUCTIONS)
        self.assertEqual(sent["messages"][1]["content"], "prompt")


class Redirects(unittest.TestCase):
    def test_only_a_303_to_the_same_modal_host_is_followed(self):
        import urllib.request
        handler = openweight.ModalPoll()
        request = urllib.request.Request("https://x--app-serve.us-east.modal.run/v1/chat/completions", data=b"{}")
        followed = handler.redirect_request(request, None, 303, "See Other", {}, "https://x--app-serve.us-east.modal.run/poll/1")
        self.assertEqual(followed.get_method(), "GET")
        for code, url in ((302, "https://x--app-serve.us-east.modal.run/poll/1"), (303, "https://elsewhere.example.com/poll")):
            with self.assertRaises(v1.AdapterError):
                handler.redirect_request(request, None, code, "", {}, url)


if __name__ == "__main__":
    unittest.main()
