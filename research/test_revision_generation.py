#!/usr/bin/env python3
"""Offline checks for the controlled revision-generation runner."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "research" / "run_revision_generation.py"
MODULE_SPEC = importlib.util.spec_from_file_location("revision_runner", RUNNER_PATH)
assert MODULE_SPEC and MODULE_SPEC.loader
runner = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(runner)


class FakeResponse:
    def __init__(self, status_code: int, body):
        self.status_code = status_code
        self._body = body
        self.headers = {"x-request-id": "offline-test"}
        self.text = body if isinstance(body, str) else json.dumps(body)

    def json(self):
        if isinstance(self._body, str):
            raise ValueError("not JSON")
        return self._body


class FakeSession:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.payloads = []

    def post(self, url, *, headers, json, timeout):
        self.payloads.append(json)
        return next(self.responses)


class RevisionRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runner.validate_frozen_protocol()
        cls.protocol = runner.load_json(runner.PROTOCOL_PATH)
        cls.prompt_manifest = runner.load_json(runner.PROMPT_MANIFEST_PATH)
        cls.specs = runner.load_json(ROOT / cls.protocol["dataset"]["path"])
        cls.prompts = runner.load_prompts_module()
        cls.queue = runner.build_queue(
            cls.protocol, cls.specs, cls.prompts, cls.prompt_manifest
        )

    def test_queue_is_complete_unique_and_deterministic(self):
        self.assertEqual(len(self.queue), 486)
        self.assertEqual(len({item["work_id"] for item in self.queue}), 486)
        self.assertEqual(
            self.queue,
            runner.build_queue(
                self.protocol, self.specs, self.prompts, self.prompt_manifest
            ),
        )
        self.assertTrue(
            all(item["system_prompt_sha256"] for item in self.queue)
        )
        self.assertTrue(all(item["user_prompt_sha256"] for item in self.queue))

    def test_payload_is_provider_pinned_and_ground_truth_never_leaks(self):
        specs = {spec["spec_id"]: spec for spec in self.specs}
        for item in self.queue:
            payload = runner.build_payload(
                item, specs[item["spec_id"]], self.protocol, self.prompts
            )
            self.assertEqual(payload["provider"]["order"], item["provider_order"])
            self.assertFalse(payload["provider"]["allow_fallbacks"])
            self.assertTrue(payload["provider"]["require_parameters"])
            self.assertNotIn("top_p", payload)
            self.assertNotIn("seed", payload)
            self.assertNotIn("tools", payload)
            self.assertEqual(len(payload["messages"]), 2)
            combined = "\n".join(message["content"] for message in payload["messages"])
            self.assertNotIn(specs[item["spec_id"]]["ground_truth_scope"], combined)

    def test_schema_validator_does_not_mutate(self):
        output = {
            "spec_id": "SPEC-01",
            "functional_tests": ["a"],
            "smoke_tests": ["b"],
            "regression_tests": ["c"],
            "integration_tests": ["d"],
            "exploratory_tests": ["e"],
            "coverage_depth": {"level": "LOW", "justification": "because"},
            "effort_estimate": {
                "min_test_cases": 1,
                "max_test_cases": 2,
                "notes": "estimate",
            },
            "clarification_flags": [],
        }
        before = runner.canonical_json(output)
        self.assertEqual(runner.validate_output(output, "SPEC-01"), [])
        self.assertEqual(runner.canonical_json(output), before)

    def test_invalid_json_retry_retains_both_attempts(self):
        item = self.queue[0]
        spec = next(spec for spec in self.specs if spec["spec_id"] == item["spec_id"])
        valid = {
            "spec_id": item["spec_id"],
            "functional_tests": [],
            "smoke_tests": [],
            "regression_tests": [],
            "integration_tests": [],
            "exploratory_tests": [],
            "coverage_depth": {"level": "LOW", "justification": "test"},
            "effort_estimate": {
                "min_test_cases": 1,
                "max_test_cases": 1,
                "notes": "test",
            },
            "clarification_flags": [],
        }
        session = FakeSession(
            [
                FakeResponse(200, {"choices": [{"message": {"content": "{"}}]}),
                FakeResponse(
                    200,
                    {
                        "id": "test-response",
                        "provider": item["provider_order"][0],
                        "choices": [{"message": {"content": json.dumps(valid)}}],
                    },
                ),
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            attempts = Path(directory) / "attempts.jsonl"
            outputs = Path(directory) / "outputs.jsonl"
            status = runner.execute_item(
                item=item,
                spec=spec,
                protocol=self.protocol,
                prompts=self.prompts,
                session=session,
                api_key="offline-placeholder",
                attempts_path=attempts,
                outputs_path=outputs,
                starting_attempt_number=0,
                sleep_fn=lambda _: None,
            )
            records = [json.loads(line) for line in attempts.read_text().splitlines()]
            self.assertEqual(status, "valid")
            self.assertEqual([record["status"] for record in records], ["invalid_json", "valid"])
            self.assertFalse(records[0]["terminal"])
            self.assertTrue(records[1]["terminal"])
            self.assertEqual(records[1]["phase"], "invalid_json_repair")
            self.assertEqual(session.payloads[0], session.payloads[1])
            self.assertEqual(len(outputs.read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
