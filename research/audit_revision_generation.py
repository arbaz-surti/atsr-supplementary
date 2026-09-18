#!/usr/bin/env python3
"""Audit and summarize the ATSR-SREP-R2-v1.0 production-generation archive."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = json.loads(
    (ROOT / "research/revision_protocol/protocol.json").read_text(encoding="utf-8")
)
BASE = ROOT / "research/revision_outputs" / PROTOCOL["protocol_id"]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nested_status(rows: list[dict], field: str) -> dict[str, dict[str, int]]:
    groups: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        groups[row[field]][row["status"]] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(groups.items())}


def main() -> int:
    manifest = json.loads((BASE / "queue-manifest.json").read_text(encoding="utf-8"))
    attempts = load_jsonl(BASE / "attempts.jsonl")
    outputs = load_jsonl(BASE / "outputs.jsonl")
    queue = manifest["queue"]
    terminal = [row for row in attempts if row.get("terminal") is True]
    errors: list[str] = []

    queue_ids = [row["work_id"] for row in queue]
    terminal_ids = [row["work_id"] for row in terminal]
    output_ids = [row["work_id"] for row in outputs]
    if len(queue) != PROTOCOL["generation"]["expected_outputs"]:
        errors.append("queue count differs from protocol")
    if len(queue_ids) != len(set(queue_ids)):
        errors.append("duplicate work ID in queue")
    if len(terminal_ids) != len(set(terminal_ids)):
        errors.append("duplicate terminal work ID")
    if set(queue_ids) != set(terminal_ids):
        errors.append("queue and terminal work-ID sets differ")
    valid_terminal_ids = {
        row["work_id"]
        for row in terminal
        if row["status"] in {"valid", "schema_invalid"}
    }
    if len(output_ids) != len(set(output_ids)):
        errors.append("duplicate parsed output work ID")
    if set(output_ids) != valid_terminal_ids:
        errors.append("parsed output set differs from JSON-parsed terminal set")

    expected_provider = {
        model["openrouter_model_id"]: model["provider_order"][0]
        for model in PROTOCOL["models"]
    }
    provider_mismatches = []
    returned_models: dict[str, set[str]] = defaultdict(set)
    for row in attempts:
        if row.get("http_status") == 200:
            if row.get("returned_provider") != expected_provider[row["model_id"]]:
                provider_mismatches.append(row["work_id"])
            if row.get("returned_model"):
                returned_models[row["model_id"]].add(row["returned_model"])
        payload = row["request_payload"]
        if payload["provider"]["order"] != row["provider_order"]:
            errors.append(f"provider payload mismatch: {row['work_id']}")
        if payload["provider"].get("allow_fallbacks") is not False:
            errors.append(f"fallback enabled: {row['work_id']}")
        if payload["model"] != row["model_id"]:
            errors.append(f"model payload mismatch: {row['work_id']}")
    if provider_mismatches:
        errors.append(f"returned-provider mismatches: {len(provider_mismatches)}")

    usage = Counter()
    reported_cost = 0.0
    for row in attempts:
        item_usage = row.get("usage") or {}
        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            if isinstance(item_usage.get(key), (int, float)):
                usage[key] += item_usage[key]
        if isinstance(item_usage.get("cost"), (int, float)):
            reported_cost += item_usage["cost"]

    artifact_hashes = {
        name: sha256(BASE / name)
        for name in ("queue-manifest.json", "attempts.jsonl", "outputs.jsonl")
    }
    report = {
        "protocol_id": PROTOCOL["protocol_id"],
        "audit_status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "queue_items": len(queue),
        "attempt_records": len(attempts),
        "terminal_records": len(terminal),
        "parsed_outputs": len(outputs),
        "terminal_statuses": dict(sorted(Counter(r["status"] for r in terminal).items())),
        "attempt_statuses": dict(sorted(Counter(r["status"] for r in attempts).items())),
        "attempt_phases": dict(sorted(Counter(r["phase"] for r in attempts).items())),
        "terminal_by_condition": nested_status(terminal, "condition"),
        "terminal_by_model": nested_status(terminal, "model_id"),
        "returned_models": {
            key: sorted(value) for key, value in sorted(returned_models.items())
        },
        "provider_mismatches": len(provider_mismatches),
        "usage": dict(usage),
        "reported_cost_usd": round(reported_cost, 6),
        "first_attempt_at": min(row["attempt_started_at"] for row in attempts),
        "last_attempt_recorded_at": max(
            row.get("attempt_ended_at", row["attempt_started_at"]) for row in attempts
        ),
        "artifact_sha256": artifact_hashes,
    }
    output_path = BASE / "generation-audit.json"
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['audit_status']} generation archive {PROTOCOL['protocol_id']}")
    print(f"queue={len(queue)} attempts={len(attempts)} terminal={len(terminal)} outputs={len(outputs)}")
    print(f"terminal_statuses={report['terminal_statuses']}")
    print(f"provider_mismatches={len(provider_mismatches)}")
    print(f"reported_cost_usd={report['reported_cost_usd']}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
