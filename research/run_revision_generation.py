#!/usr/bin/env python3
"""Controlled generator for protocol ATSR-SREP-R2-v1.0.

The safe default is a read-only dry run. Network requests require both --execute and
an exact --confirm-protocol-id value. Every HTTP attempt is appended to JSONL before
the next queue item is considered, allowing deterministic resume without replacing
terminal failures.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import random
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_DIR = ROOT / "research" / "revision_protocol"
PROTOCOL_PATH = PROTOCOL_DIR / "protocol.json"
PROMPT_MANIFEST_PATH = PROTOCOL_DIR / "prompt-manifest.json"
VALIDATOR_PATH = PROTOCOL_DIR / "validate_protocol.py"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OUTPUT_ROOT = ROOT / "research" / "revision_outputs"
RETRIABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
JSONL_WRITE_LOCK = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_local_env(path: Path) -> None:
    """Load simple KEY=VALUE entries without logging credential values."""

    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value[:1] == value[-1:] and value[:1] in {"'", '"'}:
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def load_prompts_module():
    module_spec = importlib.util.spec_from_file_location(
        "revision_protocol_prompts_runtime", PROTOCOL_DIR / "prompts.py"
    )
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError("Unable to load frozen prompts.py")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def validate_frozen_protocol() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH)],
        cwd=ROOT,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"Frozen protocol validation failed:\n{detail}")


def build_queue(
    protocol: dict, specifications: list[dict], prompts: Any, prompt_manifest: dict
) -> list[dict]:
    """Build and deterministically shuffle the complete factorial queue."""

    items: list[dict] = []
    run_count = protocol["generation"]["runs_per_model_condition_specification"]
    for spec in specifications:
        for condition in protocol["conditions"]:
            for model in protocol["models"]:
                for run_number in range(1, run_count + 1):
                    identity = {
                        "protocol_id": protocol["protocol_id"],
                        "model_id": model["openrouter_model_id"],
                        "provider_order": model["provider_order"],
                        "condition": condition,
                        "spec_id": spec["spec_id"],
                        "run": run_number,
                    }
                    items.append(
                        {
                            "work_id": sha256_text(canonical_json(identity))[:20],
                            **identity,
                            "system_prompt_sha256": prompt_manifest["prompts"][condition][
                                "sha256"
                            ],
                            "user_prompt_sha256": sha256_text(
                                prompts.build_user_prompt(spec)
                            ),
                        }
                    )
    random.Random(protocol["generation"]["queue_randomization_seed"]).shuffle(items)
    return items


def build_payload(item: dict, spec: dict, protocol: dict, prompts: Any) -> dict:
    generation = protocol["generation"]
    payload = {
        "model": item["model_id"],
        "messages": [
            {"role": "system", "content": prompts.PROMPTS[item["condition"]]},
            {"role": "user", "content": prompts.build_user_prompt(spec)},
        ],
        "temperature": generation["temperature"],
        "max_tokens": generation["max_tokens"],
        "response_format": generation["response_format"],
        "provider": {
            "order": item["provider_order"],
            "allow_fallbacks": False,
            "require_parameters": True,
        },
    }
    return payload


def validate_output(value: Any, expected_spec_id: str) -> list[str]:
    """Return schema/content flags without modifying or repairing model content."""

    errors: list[str] = []
    if not isinstance(value, dict):
        return ["root_not_object"]

    list_fields = (
        "functional_tests",
        "smoke_tests",
        "regression_tests",
        "integration_tests",
        "exploratory_tests",
        "clarification_flags",
    )
    required = ("spec_id", *list_fields, "coverage_depth", "effort_estimate")
    errors.extend(f"missing:{name}" for name in required if name not in value)

    if value.get("spec_id") != expected_spec_id:
        errors.append("spec_id_mismatch")
    for field in list_fields:
        field_value = value.get(field)
        if not isinstance(field_value, list) or not all(
            isinstance(entry, str) for entry in field_value
        ):
            errors.append(f"invalid_type:{field}")

    depth = value.get("coverage_depth")
    if not isinstance(depth, dict):
        errors.append("invalid_type:coverage_depth")
    else:
        if depth.get("level") not in {"LOW", "MEDIUM", "HIGH"}:
            errors.append("invalid_value:coverage_depth.level")
        if not isinstance(depth.get("justification"), str):
            errors.append("invalid_type:coverage_depth.justification")

    effort = value.get("effort_estimate")
    if not isinstance(effort, dict):
        errors.append("invalid_type:effort_estimate")
    else:
        for field in ("min_test_cases", "max_test_cases"):
            if not isinstance(effort.get(field), int) or isinstance(
                effort.get(field), bool
            ):
                errors.append(f"invalid_type:effort_estimate.{field}")
        if not isinstance(effort.get("notes"), str):
            errors.append("invalid_type:effort_estimate.notes")
        minimum, maximum = effort.get("min_test_cases"), effort.get("max_test_cases")
        if isinstance(minimum, int) and isinstance(maximum, int) and minimum > maximum:
            errors.append("invalid_range:effort_estimate")
    return errors


def append_jsonl(path: Path, record: dict) -> None:
    with JSONL_WRITE_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def terminal_work_ids(attempts_path: Path) -> set[str]:
    completed: set[str] = set()
    if not attempts_path.exists():
        return completed
    with attempts_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid JSONL at {attempts_path}:{line_number}; refusing resume"
                ) from exc
            if record.get("terminal") is True:
                completed.add(record["work_id"])
    return completed


def attempt_counts(attempts_path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not attempts_path.exists():
        return counts
    with attempts_path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            work_id = record["work_id"]
            counts[work_id] = max(counts.get(work_id, 0), record["request_attempt"])
    return counts


def request_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/atsr-research",
        "X-Title": "ATSR Scientific Reports Revision Experiment",
    }


def response_content(body: Any) -> str:
    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("API response lacks choices[0].message.content") from exc


def make_attempt_record(
    *, item: dict, phase: str, attempt_number: int, payload: dict
) -> dict:
    return {
        **item,
        "phase": phase,
        "request_attempt": attempt_number,
        "attempt_started_at": utc_now(),
        "request_payload_sha256": sha256_text(canonical_json(payload)),
        "request_payload": payload,
        "terminal": False,
    }


def execute_item(
    *,
    item: dict,
    spec: dict,
    protocol: dict,
    prompts: Any,
    session: requests.Session,
    api_key: str,
    attempts_path: Path,
    outputs_path: Path,
    starting_attempt_number: int = 0,
    sleep_fn=time.sleep,
) -> str:
    """Execute one queue item and return its terminal status."""

    payload = build_payload(item, spec, protocol, prompts)
    max_transport_attempts = protocol["retry_policy"][
        "transport_or_rate_limit_attempts"
    ]
    invalid_repairs = protocol["retry_policy"]["invalid_json_repair_attempts"]
    transport_attempt = starting_attempt_number
    phase = "initial"
    repairs_used = 0

    while True:
        transport_attempt += 1
        record = make_attempt_record(
            item=item,
            phase=phase,
            attempt_number=transport_attempt,
            payload=payload,
        )
        started = time.monotonic()
        try:
            response = session.post(
                API_URL,
                headers=request_headers(api_key),
                json=payload,
                timeout=120,
            )
            record["latency_ms"] = round((time.monotonic() - started) * 1000)
            record["http_status"] = response.status_code
            record["response_headers"] = {
                key: value
                for key, value in response.headers.items()
                if key.lower()
                in {"x-request-id", "retry-after", "x-ratelimit-remaining"}
            }
            try:
                body: Any = response.json()
            except ValueError:
                body = response.text
            record["response_body"] = body
            if isinstance(body, dict):
                record["response_id"] = body.get("id")
                record["returned_model"] = body.get("model")
                record["returned_provider"] = body.get("provider")
                record["usage"] = body.get("usage")

            if response.status_code >= 400:
                record["status"] = "http_error"
                retriable = response.status_code in RETRIABLE_STATUS_CODES
                record["terminal"] = not (
                    retriable and transport_attempt < max_transport_attempts
                )
                append_jsonl(attempts_path, record)
                if record["terminal"]:
                    return "http_error"
                delay = 2 ** (transport_attempt - 1)
                sleep_fn(delay)
                continue

            try:
                content = response_content(body)
            except ValueError as exc:
                record["status"] = "malformed_api_response"
                record["error"] = str(exc)
                record["terminal"] = True
                append_jsonl(attempts_path, record)
                return "malformed_api_response"

            record["raw_content"] = content
            try:
                parsed = json.loads(content)
            except (json.JSONDecodeError, TypeError) as exc:
                record["status"] = "invalid_json"
                record["parse_error"] = str(exc)
                can_repair = repairs_used < invalid_repairs
                record["terminal"] = not can_repair
                append_jsonl(attempts_path, record)
                if not can_repair:
                    return "invalid_json"
                repairs_used += 1
                phase = "invalid_json_repair"
                continue

            schema_errors = validate_output(parsed, item["spec_id"])
            status = "valid" if not schema_errors else "schema_invalid"
            record["status"] = status
            record["schema_errors"] = schema_errors
            record["parsed_output"] = parsed
            record["terminal"] = True
            append_jsonl(attempts_path, record)
            append_jsonl(
                outputs_path,
                {
                    **item,
                    "status": status,
                    "schema_errors": schema_errors,
                    "output": parsed,
                    "response_id": body.get("id") if isinstance(body, dict) else None,
                    "returned_model": body.get("model") if isinstance(body, dict) else None,
                    "returned_provider": body.get("provider")
                    if isinstance(body, dict)
                    else None,
                    "usage": body.get("usage") if isinstance(body, dict) else None,
                    "completed_at": utc_now(),
                },
            )
            return status
        except requests.RequestException as exc:
            record["latency_ms"] = round((time.monotonic() - started) * 1000)
            record["status"] = "transport_error"
            record["error_type"] = type(exc).__name__
            record["error"] = str(exc)
            record["terminal"] = transport_attempt >= max_transport_attempts
            append_jsonl(attempts_path, record)
            if record["terminal"]:
                return "transport_error"
            delay = 2 ** (transport_attempt - 1)
            sleep_fn(delay)


def manifest_for(queue: list[dict], protocol: dict, prompt_manifest: dict) -> dict:
    queue_hash = sha256_text(canonical_json(queue))
    return {
        "protocol_id": protocol["protocol_id"],
        "created_at": utc_now(),
        "queue_randomization_seed": protocol["generation"][
            "queue_randomization_seed"
        ],
        "queue_items": len(queue),
        "queue_sha256": queue_hash,
        "dataset_sha256": protocol["dataset"]["sha256"],
        "prompt_source_sha256": prompt_manifest["source_file"]["sha256"],
        "queue": queue,
    }


def write_or_verify_manifest(path: Path, manifest: dict) -> None:
    if path.exists():
        existing = load_json(path)
        comparison_fields = (
            "protocol_id",
            "queue_randomization_seed",
            "queue_items",
            "queue_sha256",
            "dataset_sha256",
            "prompt_source_sha256",
            "queue",
        )
        if any(existing.get(key) != manifest.get(key) for key in comparison_fields):
            raise RuntimeError("Existing queue manifest differs; refusing unsafe resume")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute", action="store_true", help="Make production OpenRouter calls"
    )
    parser.add_argument(
        "--confirm-protocol-id",
        help="Required with --execute; must exactly match the frozen protocol ID",
    )
    parser.add_argument(
        "--limit", type=int, help="Maximum pending queue items to process this invocation"
    )
    parser.add_argument(
        "--output-dir", type=Path, help="Override the protocol-specific output directory"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Concurrent queue workers (default: 1; concurrency does not alter payloads)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    validate_frozen_protocol()
    protocol = load_json(PROTOCOL_PATH)
    prompt_manifest = load_json(PROMPT_MANIFEST_PATH)
    specifications = load_json(ROOT / protocol["dataset"]["path"])
    prompts = load_prompts_module()
    queue = build_queue(protocol, specifications, prompts, prompt_manifest)
    manifest = manifest_for(queue, protocol, prompt_manifest)

    if len(queue) != protocol["generation"]["expected_outputs"]:
        raise RuntimeError("Queue length differs from frozen expected output count")

    first_item = queue[0]
    spec_by_id = {spec["spec_id"]: spec for spec in specifications}
    sample_payload = build_payload(
        first_item, spec_by_id[first_item["spec_id"]], protocol, prompts
    )
    print(f"PASS frozen protocol {protocol['protocol_id']}")
    print(f"PASS deterministic queue: {len(queue)} items, {manifest['queue_sha256']}")
    print(
        "PASS sample payload: "
        f"{first_item['model_id']} / {first_item['condition']} / "
        f"{first_item['spec_id']} / run {first_item['run']} / "
        f"{sha256_text(canonical_json(sample_payload))}"
    )

    if not args.execute:
        print("DRY RUN ONLY: no files written and no network completion calls made")
        return 0

    if args.confirm_protocol_id != protocol["protocol_id"]:
        raise RuntimeError(
            "--execute requires --confirm-protocol-id " + protocol["protocol_id"]
        )
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be at least 1")
    if args.workers < 1 or args.workers > 12:
        raise ValueError("--workers must be between 1 and 12")
    load_local_env(ROOT / ".env")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    output_dir = (args.output_dir or DEFAULT_OUTPUT_ROOT / protocol["protocol_id"]).resolve()
    manifest_path = output_dir / "queue-manifest.json"
    attempts_path = output_dir / "attempts.jsonl"
    outputs_path = output_dir / "outputs.jsonl"
    summary_path = output_dir / "run-summary.json"
    write_or_verify_manifest(manifest_path, manifest)
    complete = terminal_work_ids(attempts_path)
    previous_attempt_counts = attempt_counts(attempts_path)
    pending = [item for item in queue if item["work_id"] not in complete]
    selected = pending[: args.limit] if args.limit else pending
    print(f"Resume state: {len(complete)} terminal, {len(pending)} pending")

    counts: dict[str, int] = {}

    def run_selected(index: int, item: dict) -> tuple[int, dict, str]:
        print(
            f"[{index}/{len(selected)}] {item['work_id']} "
            f"{item['model_id']} {item['condition']} {item['spec_id']} r{item['run']}",
            flush=True,
        )
        with requests.Session() as session:
            status = execute_item(
                item=item,
                spec=spec_by_id[item["spec_id"]],
                protocol=protocol,
                prompts=prompts,
                session=session,
                api_key=api_key,
                attempts_path=attempts_path,
                outputs_path=outputs_path,
                starting_attempt_number=previous_attempt_counts.get(item["work_id"], 0),
            )
        return index, item, status

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(run_selected, index, item)
            for index, item in enumerate(selected, 1)
        ]
        for future in concurrent.futures.as_completed(futures):
            _, item, status = future.result()
            counts[status] = counts.get(status, 0) + 1

    total_terminal = len(terminal_work_ids(attempts_path))
    summary = {
        "protocol_id": protocol["protocol_id"],
        "updated_at": utc_now(),
        "queue_items": len(queue),
        "terminal_items": total_terminal,
        "pending_items": len(queue) - total_terminal,
        "this_invocation": counts,
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(canonical_json(summary))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
