#!/usr/bin/env python3
"""POST-HOC coverage-depth baseline analysis (Scientific Reports, October 2026 round, R3-3).

Reads the hash-locked operative analysis directory read-only and writes a new
sibling directory. It does not modify any locked artifact.

The editor asked for an appropriate simple baseline given the imbalanced consensus
depth distribution (15 HIGH / 3 MEDIUM). Outputs:

1. Majority-class (always-HIGH) baseline, at specification level and on each
   condition's own scorable anchor outputs (same specifications, same weights).
2. Per-condition exact agreement, balanced accuracy (mean recall over the consensus
   classes present), and Cohen's kappa, unweighted and linear-weighted, against
   consensus. The always-HIGH rule has kappa 0 and balanced accuracy 0.5 by
   construction.
3. Exact agreement split by consensus class (HIGH vs MEDIUM specifications).
4. Specification-cluster bootstrap 95% CI for condition minus always-HIGH exact
   agreement on matched outputs.

None of this was pre-specified in ATSR-SREP-R2-v1.0; it must be labelled post hoc
wherever it is reported. Outputs are nested within specifications, so the figures
are descriptive; the bootstrap resamples specifications, not outputs.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
LOCKED = ROOT / "revision_analysis" / "ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18"
OUT_DIR = ROOT / "revision_analysis" / "ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18-round3-depth-baseline"

ANALYSIS_SEED = 20260913
BOOTSTRAP_REPLICATES = 20000
CONDITIONS = ["naive", "generic_structured_qa", "atsr"]
LEVELS = ["LOW", "MEDIUM", "HIGH"]
DEPTH_LEVEL = {level: i for i, level in enumerate(LEVELS)}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kappa(reference: list[str], predicted: list[str], weighted: bool) -> float:
    """Cohen's kappa over LOW/MEDIUM/HIGH; linear weights when `weighted`."""
    k = len(LEVELS)
    observed = np.zeros((k, k))
    for r, p in zip(reference, predicted):
        observed[DEPTH_LEVEL[r], DEPTH_LEVEL[p]] += 1
    observed /= observed.sum()
    expected = np.outer(observed.sum(axis=1), observed.sum(axis=0))
    i, j = np.indices((k, k))
    disagreement = np.abs(i - j) / (k - 1) if weighted else (i != j).astype(float)
    expected_disagreement = (disagreement * expected).sum()
    if expected_disagreement == 0:
        return 0.0
    return float(1 - (disagreement * observed).sum() / expected_disagreement)


def balanced_accuracy(reference: list[str], predicted: list[str]) -> float:
    recalls = []
    for level in sorted(set(reference)):
        pairs = [p for r, p in zip(reference, predicted) if r == level]
        recalls.append(sum(p == level for p in pairs) / len(pairs))
    return float(np.mean(recalls))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long_path = LOCKED / "ratings-long.jsonl"
    results_path = LOCKED / "analysis-results.json"
    rows = [json.loads(line) for line in long_path.open()]
    locked = json.loads(results_path.read_text())

    anchor_outputs = [
        r for r in rows
        if r["rater_id"] == "PRACTITIONER-01" and r["scorable"]
    ]
    assert len(anchor_outputs) == 132

    consensus = {r["spec_id"]: r["consensus_depth"] for r in rows}
    assert len(consensus) == 18
    consensus_counts = Counter(consensus.values())
    assert consensus_counts == Counter({"HIGH": 15, "MEDIUM": 3})

    # 1. Specification-level majority-class baseline.
    spec_level = {
        "specifications": len(consensus),
        "consensus_counts": dict(consensus_counts),
        "always_high_exact": consensus_counts["HIGH"],
        "always_high_exact_rate": consensus_counts["HIGH"] / len(consensus),
        "always_high_mean_distance": float(np.mean(
            [DEPTH_LEVEL["HIGH"] - DEPTH_LEVEL[d] for d in consensus.values()])),
    }

    # 2-4. Per-condition metrics on each condition's own scorable anchor outputs.
    locked_depth = {
        item["condition"]: item for item in locked["depth_reference_sensitivity"]
        if item["reference"] == "consensus"
    }
    rng = np.random.default_rng(ANALYSIS_SEED)
    specs = sorted(consensus)
    by_condition = {}
    for c in CONDITIONS:
        outputs = [r for r in anchor_outputs if r["condition"] == c]
        reference = [r["consensus_depth"] for r in outputs]
        predicted = [r["candidate_depth"] for r in outputs]
        always_high = ["HIGH"] * len(outputs)
        exact = sum(r == p for r, p in zip(reference, predicted))
        high_exact = sum(r == "HIGH" for r in reference)
        assert exact == locked_depth[c]["exact"] and len(outputs) == locked_depth[c]["scorable"]

        by_class = {}
        for level in ("HIGH", "MEDIUM"):
            pairs = [(r, p) for r, p in zip(reference, predicted) if r == level]
            by_class[level] = {
                "outputs": len(pairs),
                "exact": sum(r == p for r, p in pairs),
                "assigned_depth_counts": dict(Counter(p for _, p in pairs)),
            }

        # Specification-cluster bootstrap of (condition exact rate - always-HIGH rate).
        per_spec = defaultdict(lambda: [0, 0, 0])  # outputs, condition exact, always-HIGH exact
        for r in outputs:
            cell = per_spec[r["spec_id"]]
            cell[0] += 1
            cell[1] += int(r["candidate_depth"] == r["consensus_depth"])
            cell[2] += int(r["consensus_depth"] == "HIGH")
        present = [s for s in specs if s in per_spec]
        counts = np.array([per_spec[s] for s in present], dtype=float)
        draws = rng.integers(0, len(present), size=(BOOTSTRAP_REPLICATES, len(present)))
        sampled = counts[draws].sum(axis=1)
        differences = (sampled[:, 1] - sampled[:, 2]) / sampled[:, 0]

        by_condition[c] = {
            "scorable_outputs": len(outputs),
            "specifications_represented": len(present),
            "exact": exact,
            "exact_rate": exact / len(outputs),
            "always_high_exact_on_same_outputs": high_exact,
            "always_high_exact_rate_on_same_outputs": high_exact / len(outputs),
            "difference_vs_always_high": exact / len(outputs) - high_exact / len(outputs),
            "difference_vs_always_high_spec_bootstrap_95_ci": [
                float(np.percentile(differences, 2.5)),
                float(np.percentile(differences, 97.5)),
            ],
            "balanced_accuracy": balanced_accuracy(reference, predicted),
            "always_high_balanced_accuracy": balanced_accuracy(reference, always_high),
            "cohen_kappa": kappa(reference, predicted, weighted=False),
            "cohen_kappa_linear_weighted": kappa(reference, predicted, weighted=True),
            "always_high_cohen_kappa": kappa(reference, always_high, weighted=False),
            "exact_by_consensus_class": by_class,
            "assigned_depth_counts": dict(Counter(predicted)),
        }

    out = {
        "protocol_id": "ATSR-SREP-R2-v1.0",
        "purpose": "POST-HOC majority-class depth baseline requested by the editor (Oct 2026, R3-3)",
        "analysis_seed": ANALYSIS_SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "input_hashes": {
            "ratings-long.jsonl": sha256(long_path),
            "analysis-results.json": sha256(results_path),
        },
        "specification_level_majority_baseline": spec_level,
        "by_condition_on_scorable_anchor_outputs": by_condition,
    }
    (OUT_DIR / "depth-baseline.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT_DIR / 'depth-baseline.json'}")
    print(json.dumps(spec_level, indent=1))
    for c, item in by_condition.items():
        print(
            c, f"n={item['scorable_outputs']}",
            f"exact={item['exact_rate']:.3f}",
            f"always-HIGH={item['always_high_exact_rate_on_same_outputs']:.3f}",
            f"diff={item['difference_vs_always_high']:+.3f}",
            [round(x, 3) for x in item["difference_vs_always_high_spec_bootstrap_95_ci"]],
            f"BA={item['balanced_accuracy']:.3f}",
            f"kappa={item['cohen_kappa']:.3f}",
            f"wkappa={item['cohen_kappa_linear_weighted']:.3f}",
            item["exact_by_consensus_class"],
        )


if __name__ == "__main__":
    main()
