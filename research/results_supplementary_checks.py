#!/usr/bin/env python3
"""Supplementary cross-checks for the Results section (execution step 4).

Reads the hash-locked operative analysis directory read-only and writes a new
sibling directory. It does not modify any locked artifact.

Outputs (all traceable to `ratings-long.jsonl` and `attempts.jsonl`):

1. Per-specification condition means (practitioner-averaged, then model-averaged)
   validated against the locked `specification_differences`.
2. Direction of coverage-depth disagreement with consensus on scorable anchor outputs.
3. Cross-tabulation of practitioner Risk Calibration scores against depth distance
   from consensus (rubric-anchor adherence check).
4. POST-HOC sensitivity: condition contrasts on the four-dimension total that excludes
   Risk Calibration (5-20), using the locked analysis conventions.
5. Provider finish reasons for the 85 terminal invalid-JSON observations.

Item 4 was not pre-specified in ATSR-SREP-R2-v1.0 and must be labelled post hoc
wherever it is reported.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent
LOCKED = ROOT / "revision_analysis" / "ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18"
ATTEMPTS = ROOT / "revision_outputs" / "ATSR-SREP-R2-v1.0" / "attempts.jsonl"
OUT_DIR = ROOT / "revision_analysis" / "ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18-results-checks"

ANALYSIS_SEED = 20260913
BOOTSTRAP_REPLICATES = 20000
CONDITIONS = ["naive", "generic_structured_qa", "atsr"]
CONTRASTS = [
    ("ATSR - GSQ", "atsr", "generic_structured_qa"),
    ("ATSR - Naive", "atsr", "naive"),
    ("GSQ - Naive", "generic_structured_qa", "naive"),
]
DIMENSIONS = [
    "completeness",
    "specificity",
    "risk_calibration",
    "integration_awareness",
    "clarification_flag_quality",
]
DEPTH_LEVEL = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def holm_adjust(p_values: list[float]) -> list[float]:
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=float)
    running = 0.0
    count = len(p_values)
    for rank, index in enumerate(order):
        current = min(1.0, (count - rank) * float(p_values[index]))
        running = max(running, current)
        adjusted[index] = running
    return adjusted.tolist()


def rank_biserial(differences: np.ndarray) -> float:
    nonzero = differences[differences != 0]
    if len(nonzero) == 0:
        return 0.0
    ranks = stats.rankdata(np.abs(nonzero), method="average")
    positive = float(ranks[nonzero > 0].sum())
    negative = float(ranks[nonzero < 0].sum())
    return (positive - negative) / (positive + negative)


def contrast(spec_means: dict[tuple[str, str], float], label: str, first: str,
             second: str, rng: np.random.Generator) -> dict:
    specs = sorted({s for s, _ in spec_means})
    diffs = np.array([spec_means[(s, first)] - spec_means[(s, second)] for s in specs])
    n = len(diffs)
    samples = diffs[rng.integers(0, n, size=(BOOTSTRAP_REPLICATES, n))].mean(axis=1)
    ci = np.percentile(samples, [2.5, 97.5])
    test = stats.wilcoxon(diffs, alternative="two-sided", method="auto")
    return {
        "contrast": label,
        "n_specifications": n,
        "first_mean": float(np.mean([spec_means[(s, first)] for s in specs])),
        "second_mean": float(np.mean([spec_means[(s, second)] for s in specs])),
        "paired_mean_difference": float(diffs.mean()),
        "paired_median_difference": float(np.median(diffs)),
        "bootstrap_95_ci_mean_difference": [float(ci[0]), float(ci[1])],
        "wilcoxon_statistic": float(test.statistic),
        "wilcoxon_p_value": float(test.pvalue),
        "rank_biserial": float(rank_biserial(diffs)),
        "positive_ties_negative": {
            "positive": int((diffs > 0).sum()),
            "ties": int((diffs == 0).sum()),
            "negative": int((diffs < 0).sum()),
        },
        "specification_differences": {s: float(d) for s, d in zip(specs, diffs)},
    }


def spec_condition_means(rows: list[dict], value) -> dict[tuple[str, str], float]:
    """Average the two practitioners per output, then average outputs across models."""
    per_output: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for r in rows:
        per_output[(r["spec_id"], r["condition"], r["model_id"])].append(value(r))
    assert all(len(v) == 2 for v in per_output.values()), "expected two practitioner ratings per output"
    per_sc: dict[tuple[str, str], list[float]] = defaultdict(list)
    for (s, c, _m), v in per_output.items():
        per_sc[(s, c)].append(float(np.mean(v)))
    return {k: float(np.mean(v)) for k, v in per_sc.items()}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long_path = LOCKED / "ratings-long.jsonl"
    results_path = LOCKED / "analysis-results.json"
    rows = [json.loads(line) for line in long_path.open()]
    locked = json.loads(results_path.read_text())

    practitioners = [r for r in rows if r["rater_id"].startswith("PRACTITIONER") and r["scorable"]]
    assert len(practitioners) == 264

    # 1. Per-specification condition means, validated against locked differences.
    total_means = spec_condition_means(practitioners, lambda r: r["total_score"])
    specs = sorted({s for s, _ in total_means})
    per_spec_table = []
    contributing = defaultdict(lambda: defaultdict(set))
    for r in practitioners:
        contributing[r["spec_id"]][r["condition"]].add(r["model_id"])
    for s in specs:
        per_spec_table.append({
            "spec_id": s,
            **{c: total_means[(s, c)] for c in CONDITIONS},
            "atsr_minus_gsq": total_means[(s, "atsr")] - total_means[(s, "generic_structured_qa")],
            "contributing_models": {c: len(contributing[s][c]) for c in CONDITIONS},
        })
    locked_primary = {item["contrast"]: item for item in locked["primary_and_overall_contrasts"]}
    validation = {}
    for label, first, second in CONTRASTS:
        ref = locked_primary[label]["specification_differences"]
        mine = {s: total_means[(s, first)] - total_means[(s, second)] for s in specs}
        validation[label] = all(abs(mine[s] - ref[s]) < 1e-9 for s in specs)
    assert all(validation.values()), validation

    # 2. Depth-direction on scorable anchor outputs (one row per output).
    anchor_outputs = {r["work_id"]: r for r in practitioners if r["rater_id"] == "PRACTITIONER-01"}
    assert len(anchor_outputs) == 132
    depth_direction = {}
    for c in CONDITIONS:
        counter = Counter()
        assigned = Counter()
        for r in anchor_outputs.values():
            if r["condition"] != c:
                continue
            delta = DEPTH_LEVEL[r["candidate_depth"]] - DEPTH_LEVEL[r["consensus_depth"]]
            counter["under" if delta < 0 else "over" if delta > 0 else "exact"] += 1
            assigned[r["candidate_depth"]] += 1
        depth_direction[c] = {
            "scorable": sum(counter.values()),
            "exact": counter["exact"],
            "under_assigned": counter["under"],
            "over_assigned": counter["over"],
            "assigned_depth_counts": dict(assigned),
        }

    # 3. Risk Calibration score vs depth distance (practitioner ratings).
    rc_crosstab = {}
    for c in CONDITIONS:
        table = defaultdict(Counter)
        for r in practitioners:
            if r["condition"] == c:
                table[int(r["depth_distance"])][r["scores"]["risk_calibration"]] += 1
        rc_crosstab[c] = {
            str(dist): {
                "n_ratings": sum(cnt.values()),
                "score_counts": {str(k): cnt[k] for k in range(1, 6)},
                "scored_4_or_5": cnt[4] + cnt[5],
            }
            for dist, cnt in sorted(table.items())
        }

    # 4. POST-HOC sensitivity: four-dimension total excluding Risk Calibration.
    rng = np.random.default_rng(ANALYSIS_SEED)
    four_dim = spec_condition_means(
        practitioners,
        lambda r: sum(r["scores"][d] for d in DIMENSIONS if d != "risk_calibration"),
    )
    post_hoc = [contrast(four_dim, label, first, second, rng) for label, first, second in CONTRASTS]
    for item, adj in zip(post_hoc, holm_adjust([i["wilcoxon_p_value"] for i in post_hoc])):
        item["holm_adjusted_p_value"] = adj

    # 5. Finish reasons for terminal invalid-JSON observations.
    finish = Counter()
    for line in ATTEMPTS.open():
        a = json.loads(line)
        if a.get("terminal") and a.get("status") == "invalid_json":
            choice = ((a.get("response_body") or {}).get("choices") or [{}])[0]
            finish[str(choice.get("finish_reason"))] += 1
    assert sum(finish.values()) == 85

    out = {
        "protocol_id": "ATSR-SREP-R2-v1.0",
        "purpose": "Results-section cross-checks; item 4 is a POST-HOC sensitivity analysis",
        "analysis_seed": ANALYSIS_SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "input_hashes": {
            "ratings-long.jsonl": sha256(long_path),
            "analysis-results.json": sha256(results_path),
            "attempts.jsonl": sha256(ATTEMPTS),
        },
        "per_specification_condition_means": per_spec_table,
        "per_specification_validation_against_locked_differences": validation,
        "depth_direction_on_scorable_anchor_outputs": depth_direction,
        "risk_calibration_score_by_depth_distance_practitioner_ratings": rc_crosstab,
        "post_hoc_four_dimension_total_excluding_risk_calibration": post_hoc,
        "terminal_invalid_json_finish_reasons": dict(finish),
    }
    (OUT_DIR / "results-checks.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT_DIR / 'results-checks.json'}")
    print("validation:", validation)
    print("depth direction:", json.dumps(depth_direction, indent=1))
    for item in post_hoc:
        print(item["contrast"], round(item["paired_mean_difference"], 3),
              [round(x, 3) for x in item["bootstrap_95_ci_mean_difference"]],
              "p=%.4g" % item["wilcoxon_p_value"], "holm=%.4g" % item["holm_adjusted_p_value"],
              item["positive_ties_negative"])
    print("finish reasons:", dict(finish))


if __name__ == "__main__":
    main()
