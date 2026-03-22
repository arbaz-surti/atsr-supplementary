"""
Baseline Evaluation Tool — Naive LLM Prompt (No ATSR Framework)
================================================================
This script runs each feature specification through a minimal, unstructured
QA analyst prompt — WITHOUT the ATSR framework's reasoning dimensions,
depth calibration rules, or quality guidelines.

Purpose: provide a baseline comparison for the paper. If ATSR scores
materially higher than this baseline using the same rubric, that
demonstrates the framework's added value over unstructured LLM querying.

Design decisions for fair comparison:
  - Same model (GPT-4o via OpenRouter)
  - Same temperature (0.2)
  - Same input fields (title, change_type, system_area, description, AC)
  - Same JSON output schema (so rubric scoring is apples-to-apples)
  - No ATSR system prompt — no reasoning dimensions, no depth rules,
    no specificity guidelines, no clarification flag instructions

Usage:
    python baseline_tool.py

Requirements:
    pip install requests python-dotenv
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

# ── Configuration ──────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "openai/gpt-4o"

SPECS_FILE  = BASE_DIR / "research" / "all-specs-18.json"
RESULTS_FILE = BASE_DIR / "research" / "baseline-results.json"

# ── Baseline System Prompt ─────────────────────────────────────────────────────
# Deliberately minimal — no ATSR reasoning structure, no calibration rules,
# no quality guidelines. Just a generic QA analyst identity + output schema.

BASELINE_SYSTEM_PROMPT = """You are a QA analyst. Given a software feature specification, \
produce a test scope recommendation.

Return a single valid JSON object. Do not include markdown fences or any text outside \
the JSON object.

JSON schema:
{
  "spec_id": "string",
  "functional_tests": ["test description"],
  "smoke_tests": ["test description"],
  "regression_tests": ["test description"],
  "integration_tests": ["test description"],
  "exploratory_tests": ["test description"],
  "coverage_depth": {
    "level": "LOW | MEDIUM | HIGH",
    "justification": "brief reason"
  },
  "effort_estimate": {
    "min_test_cases": 0,
    "max_test_cases": 0,
    "notes": "brief notes"
  },
  "clarification_flags": ["missing information that would affect testing"]
}"""


# ── User Prompt Builder ────────────────────────────────────────────────────────

def build_user_prompt(spec: dict) -> str:
    lines = [
        f"Feature Specification ID: {spec['spec_id']}",
        f"Title: {spec['title']}",
        f"Change Type: {spec['change_type']}",
        f"System Area: {spec['system_area']}",
        "",
        "Description:",
        spec["description"],
    ]

    if spec.get("acceptance_criteria"):
        lines.append("")
        lines.append("Acceptance Criteria:")
        for criterion in spec["acceptance_criteria"]:
            lines.append(f"- {criterion}")

    lines.append("")
    lines.append(
        "Provide your test scope recommendation as a JSON object matching the schema."
    )

    return "\n".join(lines)


# ── API Call ───────────────────────────────────────────────────────────────────

def call_baseline(spec: dict) -> dict:
    user_prompt = build_user_prompt(spec)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/atsr-research",
        "X-Title": "ATSR Baseline Tool",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": BASELINE_SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"},
    }

    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    raw     = response.json()
    content = raw["choices"][0]["message"]["content"]

    recommendation = json.loads(content)
    recommendation["spec_id"]    = spec["spec_id"]
    recommendation["model_used"] = MODEL
    recommendation["timestamp"]  = datetime.utcnow().isoformat() + "Z"

    return recommendation


# ── Runner ─────────────────────────────────────────────────────────────────────

def run_baseline():
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found. Check your .env file.")

    with open(SPECS_FILE, "r") as f:
        specs = json.load(f)

    print("Baseline Evaluation Run (Naive Prompt — No ATSR Framework)")
    print(f"Model : {MODEL}")
    print(f"Specs : {len(specs)}")
    print(f"Output: {RESULTS_FILE}")
    print("=" * 60)

    results = []

    for i, spec in enumerate(specs, 1):
        spec_id = spec["spec_id"]
        print(f"[{i}/{len(specs)}] {spec_id}: {spec['title'][:55]}...")

        try:
            recommendation = call_baseline(spec)

            results.append({
                "spec_id":              spec_id,
                "title":                spec["title"],
                "change_type":          spec["change_type"],
                "system_area":          spec["system_area"],
                "ground_truth_scope":   spec["ground_truth_scope"],
                "baseline_recommendation": recommendation,
            })

            print(f"  Coverage depth : {recommendation['coverage_depth']['level']}")
            print(f"  Effort estimate: {recommendation['effort_estimate']['min_test_cases']}–"
                  f"{recommendation['effort_estimate']['max_test_cases']} test cases")
            print(f"  Clarification flags: {len(recommendation['clarification_flags'])}")

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"spec_id": spec_id, "title": spec["title"], "error": str(e)})

        if i < len(specs):
            time.sleep(1)

    with open(RESULTS_FILE, "w") as f:
        json.dump(
            {
                "run_metadata": {
                    "model":      MODEL,
                    "timestamp":  datetime.utcnow().isoformat() + "Z",
                    "spec_count": len(specs),
                    "type":       "BASELINE — naive prompt, no ATSR framework",
                },
                "results": results,
            },
            f,
            indent=2,
        )

    print("=" * 60)
    print(f"Done. Results saved to: {RESULTS_FILE}")
    print(f"Successfully processed: {sum(1 for r in results if 'error' not in r)}/{len(specs)}")


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_baseline()
