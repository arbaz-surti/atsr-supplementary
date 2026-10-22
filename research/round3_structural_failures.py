#!/usr/bin/env python3
"""POST-HOC structural-failure impact analysis (Scientific Reports, October 2026 round, R3-2).

Reads the hash-locked operative analysis directory and the generation records
read-only and writes a new sibling directory. It does not modify any locked artifact.

The editor asked for further treatment of the condition-dependent structural failures,
particularly for Claude Sonnet 4.6, and their potential impact on the primary
comparison (ATSR - GSQ, practitioner-averaged total score, paired over 18
specifications). Outputs:

1. Reproduction of the primary estimate and the locked complete-model (GPT-4o +
   Llama) sensitivity; their difference is Claude's net leverage on the primary.
2. Bounds for the missing Claude anchor outputs under ATSR and GSQ, imputed at
   (a) the rubric extremes, (b) the observed range of all scorable anchor outputs, and
   (c) the observed range of Claude's own scorable outputs in each condition, each in
   the direction least and most favourable to ATSR.
3. Tipping point: missing Claude outputs imputed at the mean of the other models in the
   same specification and condition (which reproduces the primary point estimate), then
   shifted by delta against ATSR. Reports the delta at which the point estimate and the
   lower bootstrap limit reach zero, for an ATSR-only shift and for a two-sided shift.
4. Observed Claude offsets: on specifications where Claude was scorable, its score
   minus the mean of the other models in the same condition.
5. Output-budget descriptives from the generation records: finish reasons and
   completion tokens by model and condition against the 2,000-token limit.

None of this was pre-specified in ATSR-SREP-R2-v1.0; it must be labelled post hoc
wherever it is reported. The bootstrap resamples specifications.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
LOCKED = ROOT / "revision_analysis" / "ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18"
GENERATION = ROOT / "revision_outputs" / "ATSR-SREP-R2-v1.0"
OUT_DIR = ROOT / "revision_analysis" / "ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18-round3-structural-failures"

ANALYSIS_SEED = 20260913
BOOTSTRAP_REPLICATES = 20000
CONDITIONS = ["naive", "generic_structured_qa", "atsr"]
CLAUDE = "anthropic/claude-sonnet-4.6"
OUTPUT_TOKEN_LIMIT = 2000
SCALE_MIN, SCALE_MAX = 5.0, 25.0
DELTA_GRID = np.round(np.arange(0, 20.0001, 0.01), 2)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open()]


def summarise(differences: np.ndarray, draws: np.ndarray) -> dict:
    boot = differences[draws].mean(axis=1)
    return {
        "paired_mean_difference": float(differences.mean()),
        "bootstrap_95_ci": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
        "positive_ties_negative": [
            int((differences > 1e-9).sum()),
            int((np.abs(differences) <= 1e-9).sum()),
            int((differences < -1e-9).sum()),
        ],
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long_path = LOCKED / "ratings-long.jsonl"
    results_path = LOCKED / "analysis-results.json"
    attempts_path = GENERATION / "attempts.jsonl"
    rows = load_jsonl(long_path)
    locked = json.loads(results_path.read_text())

    # Practitioner-averaged total per scorable anchor output.
    ratings = defaultdict(list)
    anchor_cells = set()
    for r in rows:
        if r["rater_id"].startswith("PRACTITIONER"):
            anchor_cells.add((r["spec_id"], r["model_id"], r["condition"]))
            if r["scorable"]:
                ratings[(r["spec_id"], r["model_id"], r["condition"])].append(r["total_score"])
    assert len(anchor_cells) == 162 and len(ratings) == 132
    assert all(len(v) == 2 for v in ratings.values())
    score = {k: float(np.mean(v)) for k, v in ratings.items()}

    specs = sorted({s for s, _, _ in anchor_cells})
    models = sorted({m for _, m, _ in anchor_cells})
    others = [m for m in models if m != CLAUDE]
    assert len(specs) == 18 and len(models) == 3

    def cell_values(spec, condition, imputed=None, model_set=models):
        values = []
        for m in model_set:
            key = (spec, m, condition)
            if key in score:
                values.append(score[key])
            elif imputed is not None and m == CLAUDE and (spec, condition) in imputed:
                values.append(imputed[(spec, condition)])
        return values

    def paired(first, second, imputed=None, model_set=models):
        return np.array([
            np.mean(cell_values(s, first, imputed, model_set))
            - np.mean(cell_values(s, second, imputed, model_set))
            for s in specs
        ])

    rng = np.random.default_rng(ANALYSIS_SEED)
    draws = rng.integers(0, len(specs), size=(BOOTSTRAP_REPLICATES, len(specs)))

    # 1. Reproduce locked estimates.
    locked_primary = {c["contrast"]: c for c in locked["primary_and_overall_contrasts"]}
    locked_complete = {
        c["contrast"]: c for c in locked["missingness_sensitivities"]["complete_GPT4o_and_Llama_models_only"]
    }
    primary = paired("atsr", "generic_structured_qa")
    complete = paired("atsr", "generic_structured_qa", model_set=others)
    assert np.isclose(primary.mean(), locked_primary["ATSR - GSQ"]["paired_mean_difference"])
    assert np.isclose(complete.mean(), locked_complete["ATSR - GSQ"]["paired_mean_difference"])
    reproduction = {
        "primary_available_model": summarise(primary, draws),
        "complete_gpt4o_llama_only": summarise(complete, draws),
        "claude_net_leverage_on_primary": float(primary.mean() - complete.mean()),
        "locked_primary_ci": locked_primary["ATSR - GSQ"]["bootstrap_95_ci_mean_difference"],
        "locked_complete_ci": locked_complete["ATSR - GSQ"]["bootstrap_95_ci_mean_difference"],
    }

    # Missing Claude anchor cells by condition.
    missing = {
        c: [s for s in specs if (s, CLAUDE, c) not in score] for c in CONDITIONS
    }
    claude_observed = {
        c: sorted(score[(s, CLAUDE, c)] for s in specs if (s, CLAUDE, c) in score) for c in CONDITIONS
    }
    all_observed = sorted(score.values())

    # 2. Bounds: (value for missing ATSR, value for missing GSQ).
    bound_specs = {
        "rubric_extremes": (SCALE_MIN, SCALE_MAX),
        "observed_range_all_anchor_outputs": (all_observed[0], all_observed[-1]),
        "observed_range_claude_same_condition": None,
    }
    bounds = {}
    for name, extremes in bound_specs.items():
        if extremes is None:
            worst = (claude_observed["atsr"][0], claude_observed["generic_structured_qa"][-1])
            best = (claude_observed["atsr"][-1], claude_observed["generic_structured_qa"][0])
        else:
            low, high = extremes
            worst, best = (low, high), (high, low)
        bounds[name] = {}
        for label, (atsr_value, gsq_value) in (("least_favourable_to_atsr", worst),
                                              ("most_favourable_to_atsr", best)):
            imputed = {(s, "atsr"): atsr_value for s in missing["atsr"]}
            imputed.update({(s, "generic_structured_qa"): gsq_value
                            for s in missing["generic_structured_qa"]})
            result = summarise(paired("atsr", "generic_structured_qa", imputed), draws)
            result["imputed_missing_atsr"] = atsr_value
            result["imputed_missing_gsq"] = gsq_value
            bounds[name][label] = result

    # 3. Tipping point. Each specification difference is linear in delta.
    def available_mean(spec, condition):
        return float(np.mean(cell_values(spec, condition)))

    base_imputed = {(s, "atsr"): available_mean(s, "atsr") for s in missing["atsr"]}
    base_imputed.update({(s, "generic_structured_qa"): available_mean(s, "generic_structured_qa")
                         for s in missing["generic_structured_qa"]})
    base = paired("atsr", "generic_structured_qa", base_imputed)
    assert np.isclose(base.mean(), primary.mean())
    weight_atsr = np.array([1 / 3 if s in missing["atsr"] else 0.0 for s in specs])
    weight_gsq = np.array([1 / 3 if s in missing["generic_structured_qa"] else 0.0 for s in specs])

    def tipping(weight):
        boot_base = base[draws].mean(axis=1)
        boot_weight = weight[draws].mean(axis=1)
        point_zero = lower_zero = None
        for delta in DELTA_GRID:
            point = base.mean() - delta * weight.mean()
            lower = np.percentile(boot_base - delta * boot_weight, 2.5)
            if lower_zero is None and lower <= 0:
                lower_zero = float(delta)
            if point_zero is None and point <= 0:
                point_zero = float(delta)
                break
        return {
            "delta_where_lower_95_limit_reaches_zero": lower_zero,
            "delta_where_point_estimate_reaches_zero": point_zero,
            "point_estimate_slope_per_point_of_delta": float(-weight.mean()),
        }

    tipping_point = {
        "imputation": "missing Claude output = mean of the other models in the same specification and condition, minus delta (ATSR) / plus delta (GSQ)",
        "atsr_only_shift": tipping(weight_atsr),
        "two_sided_shift": tipping(weight_atsr + weight_gsq),
    }

    # 4. Observed Claude offsets relative to the other models in the same cell.
    offsets = {}
    for c in CONDITIONS:
        diffs = [score[(s, CLAUDE, c)] - np.mean([score[(s, m, c)] for m in others])
                 for s in specs if (s, CLAUDE, c) in score]
        offsets[c] = {
            "scorable_specifications": len(diffs),
            "mean_offset": float(np.mean(diffs)),
            "min_offset": float(np.min(diffs)),
            "max_offset": float(np.max(diffs)),
        }
    sd_by_condition = {
        c: float(np.std([v for (s, m, cc), v in score.items() if cc == c], ddof=1)) for c in CONDITIONS
    }

    # 5. Output-budget descriptives from terminal generation records.
    terminal = [a for a in load_jsonl(attempts_path) if a.get("terminal")]
    assert len(terminal) == 486
    budget = {}
    for m in models:
        for c in CONDITIONS:
            cell = [a for a in terminal if a["model_id"] == m and a["condition"] == c]
            finish = Counter(a["response_body"]["choices"][0]["finish_reason"] for a in cell)
            tokens = [a["usage"]["completion_tokens"] for a in cell]
            valid_tokens = [a["usage"]["completion_tokens"] for a in cell if a["status"] == "valid"]
            budget[f"{m}|{c}"] = {
                "terminal_observations": len(cell),
                "valid": sum(a["status"] == "valid" for a in cell),
                "finish_reasons": dict(finish),
                "median_completion_tokens_all": float(np.median(tokens)),
                "median_completion_tokens_valid": float(np.median(valid_tokens)) if valid_tokens else None,
                "max_completion_tokens_valid": int(max(valid_tokens)) if valid_tokens else None,
                "valid_at_or_above_90pct_of_limit": sum(t >= 0.9 * OUTPUT_TOKEN_LIMIT for t in valid_tokens),
            }
    claude_failures = [a for a in terminal if a["model_id"] == CLAUDE and a["status"] != "valid"]
    assert len(claude_failures) == 85

    out = {
        "protocol_id": "ATSR-SREP-R2-v1.0",
        "purpose": "POST-HOC impact of Claude Sonnet 4.6 structural failures on the primary comparison (Oct 2026, R3-2)",
        "analysis_seed": ANALYSIS_SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "input_hashes": {
            "ratings-long.jsonl": sha256(long_path),
            "analysis-results.json": sha256(results_path),
            "attempts.jsonl": sha256(attempts_path),
        },
        "missing_claude_anchor_specifications": {c: missing[c] for c in CONDITIONS},
        "claude_observed_scores": claude_observed,
        "reproduction": reproduction,
        "bounds_atsr_minus_gsq": bounds,
        "tipping_point_atsr_minus_gsq": tipping_point,
        "observed_claude_offset_vs_other_models": offsets,
        "output_sd_by_condition": sd_by_condition,
        "output_budget": budget,
        "claude_failure_finish_reasons": dict(Counter(
            a["response_body"]["choices"][0]["finish_reason"] for a in claude_failures)),
    }
    (OUT_DIR / "structural-failures.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT_DIR / 'structural-failures.json'}")
    print("missing Claude:", {c: len(v) for c, v in missing.items()})
    print("reproduction:", json.dumps(reproduction, indent=1))
    for name, item in bounds.items():
        for label, r in item.items():
            print(name, label, f"atsr={r['imputed_missing_atsr']} gsq={r['imputed_missing_gsq']}",
                  f"diff={r['paired_mean_difference']:+.3f}",
                  [round(x, 3) for x in r["bootstrap_95_ci"]], r["positive_ties_negative"])
    print("tipping:", json.dumps(tipping_point, indent=1))
    print("offsets:", json.dumps(offsets, indent=1))
    print("sd:", sd_by_condition)
    for k, v in budget.items():
        print(k, v)
    print("claude failure finish reasons:", out["claude_failure_finish_reasons"])


if __name__ == "__main__":
    main()
