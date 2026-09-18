#!/usr/bin/env python3
"""Validate frozen ATSR revision protocol inputs before generation."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_prompts_module():
    module_spec = importlib.util.spec_from_file_location(
        "revision_protocol_prompts", HERE / "prompts.py"
    )
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError("Unable to load prompts.py")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def main() -> int:
    errors: list[str] = []
    protocol = json.loads((HERE / "protocol.json").read_text())
    manifest = json.loads((HERE / "prompt-manifest.json").read_text())
    availability = json.loads(
        (HERE / "model-availability-2026-09-13.json").read_text()
    )
    lock = json.loads((HERE / "protocol-lock.json").read_text())
    prompts = load_prompts_module()

    for relative_path, expected_hash in lock["files"].items():
        actual_hash = sha256_bytes((ROOT / relative_path).read_bytes())
        if actual_hash != expected_hash:
            errors.append(f"locked file hash mismatch: {relative_path}")

    dataset = ROOT / protocol["dataset"]["path"]
    dataset_hash = sha256_bytes(dataset.read_bytes())
    if dataset_hash != protocol["dataset"]["sha256"]:
        errors.append("dataset hash differs from protocol.json")
    if dataset_hash != manifest["dataset"]["sha256"]:
        errors.append("dataset hash differs from prompt-manifest.json")
    specification_count = len(json.loads(dataset.read_text()))
    if specification_count != protocol["dataset"]["specification_count"]:
        errors.append("dataset specification count differs from protocol.json")

    source_hash = sha256_bytes((HERE / "prompts.py").read_bytes())
    if source_hash != manifest["source_file"]["sha256"]:
        errors.append("prompts.py source hash differs from manifest")

    for name, value in prompts.PROMPTS.items():
        entry = manifest["prompts"].get(name)
        if entry is None:
            errors.append(f"prompt {name} missing from manifest")
            continue
        encoded = value.encode()
        if sha256_bytes(encoded) != entry["sha256"]:
            errors.append(f"runtime hash mismatch for prompt {name}")
        if len(encoded) != entry["utf8_bytes"]:
            errors.append(f"runtime byte count mismatch for prompt {name}")

    schema_encoded = prompts.OUTPUT_SCHEMA.encode()
    if sha256_bytes(schema_encoded) != manifest["shared_output_schema"]["sha256"]:
        errors.append("shared output schema hash mismatch")
    if len(schema_encoded) != manifest["shared_output_schema"]["utf8_bytes"]:
        errors.append("shared output schema byte count mismatch")

    historical_encoded = prompts.HISTORICAL_ATSR_SYSTEM_PROMPT.encode()
    historical_entry = manifest["archived_historical_atsr_prompt"]
    if sha256_bytes(historical_encoded) != historical_entry["sha256"]:
        errors.append("archived historical ATSR prompt hash mismatch")
    if len(historical_encoded) != historical_entry["utf8_bytes"]:
        errors.append("archived historical ATSR prompt byte count mismatch")

    builder_hash = sha256_bytes(inspect.getsource(prompts.build_user_prompt).encode())
    if builder_hash != manifest["shared_user_prompt_builder_source"]["sha256"]:
        errors.append("shared user prompt builder source hash mismatch")

    expected_outputs = (
        specification_count
        * len(protocol["conditions"])
        * len(protocol["models"])
        * protocol["generation"]["runs_per_model_condition_specification"]
    )
    if expected_outputs != protocol["generation"]["expected_outputs"]:
        errors.append("expected output count does not match factorial design")

    protocol_models = {model["openrouter_model_id"] for model in protocol["models"]}
    availability_models = {
        model["openrouter_model_id"] for model in availability["models"]
    }
    if protocol_models != availability_models:
        errors.append("protocol and availability model sets differ")

    # Confirm exact preservation of the two historical system prompts.
    sys.path.insert(0, str(ROOT))
    import atsr_tool  # noqa: PLC0415
    import baseline_tool  # noqa: PLC0415

    if prompts.HISTORICAL_ATSR_SYSTEM_PROMPT != atsr_tool.SYSTEM_PROMPT:
        errors.append("archived historical ATSR prompt differs from runtime prompt")
    if prompts.NAIVE_SYSTEM_PROMPT != baseline_tool.BASELINE_SYSTEM_PROMPT:
        errors.append("frozen naive prompt differs from historical runtime prompt")
    if not all(value.endswith(prompts.OUTPUT_SCHEMA) for value in prompts.PROMPTS.values()):
        errors.append("generation conditions do not share the byte-identical schema suffix")

    if errors:
        print("PROTOCOL VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS protocol {protocol['protocol_id']}")
    print(f"PASS dataset: {specification_count} specifications, {dataset_hash}")
    print(f"PASS prompt conditions: {len(prompts.PROMPTS)}")
    print(f"PASS models: {len(protocol_models)}")
    print(f"PASS factorial output count: {expected_outputs}")
    print("PASS historical ATSR and naive prompt identity")
    print("PASS byte-identical schema suffix across generation conditions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
