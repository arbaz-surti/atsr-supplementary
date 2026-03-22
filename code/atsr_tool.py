"""
ATSR — AI-assisted Test Scope Recommender
==========================================
Prototype implementation for the paper:
"AI-Assisted Test Scope Recommendation for Manual QA: A Framework and Evaluation"

This script runs each feature specification through the ATSR framework using
an LLM via the OpenRouter API, producing structured test scope recommendations.
Results are saved to research/atsr-results.json for evaluation and analysis.

Usage:
    python atsr_tool.py

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

# Model used for all evaluations — document this in the paper
MODEL = "openai/gpt-4o"

SPECS_FILE = BASE_DIR / "research" / "specs-for-evaluation.json"
RESULTS_FILE = BASE_DIR / "research" / "atsr-results.json"

# ── ATSR System Prompt ─────────────────────────────────────────────────────────
# This prompt constitutes the core of the ATSR framework.
# It encodes the test scope dimensions and reasoning strategy.

SYSTEM_PROMPT = """You are ATSR (AI-assisted Test Scope Recommender), an expert QA analyst \
specialising in manual testing for enterprise software systems, including point-of-sale, \
reporting, and integration-heavy platforms.

Your role is to analyse a feature specification provided by a QA team and produce a \
structured test scope recommendation. You must reason carefully about:

1. What the change directly affects (functional scope).
2. What adjacent areas may break as a side-effect (smoke scope).
3. What existing functionality could regress due to this change (regression scope).
4. Which system integrations or data flows must be validated end-to-end (integration scope).
5. What non-obvious or edge-case behaviour is worth probing (exploratory scope).
6. How deep the coverage should be, justified by the change type and risk level.
7. A rough indicative test case count to help the team plan effort.
8. What information is missing from the specification that would materially change \
your recommendation — these are clarification flags that a QA lead should resolve \
before finalising the test plan.

Important guidelines:
- Feature specifications in enterprise QA environments are often sparse or ambiguous. \
  Reason from what is given, and surface gaps explicitly in clarification_flags.
- Coverage depth should be calibrated to change type:
    LOW    → patch fix, config value change, certificate rotation
    MEDIUM → enhancement, hardware rollout, access control change
    HIGH   → new feature, new integration, major version upgrade
- Effort estimates should reflect manual testing (not automated), realistic for a \
  small QA team.
- Be specific. Generic test descriptions (e.g., "test the feature") are not useful. \
  Name the specific behaviour, flow, or data condition to test.

You must always return a single valid JSON object. Do not include markdown fences, \
prose, or any text outside the JSON object.

JSON schema:
{
  "spec_id": "string",
  "model_used": "string",
  "timestamp": "string",
  "functional_tests": [
    "Specific test area or scenario description"
  ],
  "smoke_tests": [
    "Adjacent area or quick-check scenario"
  ],
  "regression_tests": [
    "Existing feature or flow to regression test"
  ],
  "integration_tests": [
    "Integration point or data flow to validate end-to-end"
  ],
  "exploratory_tests": [
    "Non-obvious risk area or edge case to probe"
  ],
  "coverage_depth": {
    "level": "LOW | MEDIUM | HIGH",
    "justification": "Explanation of why this depth was chosen"
  },
  "effort_estimate": {
    "min_test_cases": 0,
    "max_test_cases": 0,
    "notes": "Explanation of the estimate and key drivers"
  },
  "clarification_flags": [
    "Missing or ambiguous information that would change this recommendation"
  ]
}"""


# ── User Prompt Builder ────────────────────────────────────────────────────────

def build_user_prompt(spec: dict) -> str:
    """Construct the per-spec user prompt from the structured spec object."""

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
        "Provide your structured test scope recommendation as a JSON object "
        "matching the schema defined in your instructions."
    )

    return "\n".join(lines)


# ── API Call ───────────────────────────────────────────────────────────────────

def call_atsr(spec: dict) -> dict:
    """Send a spec to the LLM and return the parsed ATSR recommendation."""

    user_prompt = build_user_prompt(spec)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/atsr-research",  # required by OpenRouter
        "X-Title": "ATSR Research Tool",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,   # low temperature for consistent, structured output
        "max_tokens": 2000,
        "response_format": {"type": "json_object"},
    }

    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    raw = response.json()
    content = raw["choices"][0]["message"]["content"]

    recommendation = json.loads(content)
    recommendation["spec_id"] = spec["spec_id"]
    recommendation["model_used"] = MODEL
    recommendation["timestamp"] = datetime.utcnow().isoformat() + "Z"

    return recommendation


# ── Evaluation Runner ──────────────────────────────────────────────────────────

def run_evaluation():
    """Run ATSR over all specs and save results alongside ground truth."""

    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found. Check your .env file.")

    with open(SPECS_FILE, "r") as f:
        specs = json.load(f)

    print(f"ATSR Evaluation Run")
    print(f"Model : {MODEL}")
    print(f"Specs : {len(specs)}")
    print(f"Output: {RESULTS_FILE}")
    print("=" * 60)

    results = []

    for i, spec in enumerate(specs, 1):
        spec_id = spec["spec_id"]
        print(f"[{i}/{len(specs)}] Processing {spec_id}: {spec['title'][:55]}...")

        try:
            recommendation = call_atsr(spec)

            result_entry = {
                "spec_id": spec_id,
                "title": spec["title"],
                "change_type": spec["change_type"],
                "system_area": spec["system_area"],
                "ground_truth_scope": spec["ground_truth_scope"],
                "atsr_recommendation": recommendation,
            }

            results.append(result_entry)
            print(f"  Coverage depth : {recommendation['coverage_depth']['level']}")
            print(f"  Effort estimate: {recommendation['effort_estimate']['min_test_cases']}–"
                  f"{recommendation['effort_estimate']['max_test_cases']} test cases")
            print(f"  Clarification flags: {len(recommendation['clarification_flags'])}")

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "spec_id": spec_id,
                "title": spec["title"],
                "error": str(e),
            })

        # Brief pause between API calls to be respectful to rate limits
        if i < len(specs):
            time.sleep(1)

    with open(RESULTS_FILE, "w") as f:
        json.dump(
            {
                "run_metadata": {
                    "model": MODEL,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "spec_count": len(specs),
                    "framework": "ATSR v1.0",
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
    run_evaluation()
