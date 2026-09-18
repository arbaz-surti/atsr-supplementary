#!/usr/bin/env python3
"""Validate, join, and analyze the operative ATSR v1 rating set.

The HTML-extracted ratings remain blinded until they are joined here to the
locked analysis metadata by (rater_id, blind_item_id). Existing analysis
artifacts are inputs only and are never overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import warnings
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels
import statsmodels.formula.api as smf


PROTOCOL_ID = "ATSR-SREP-R2-v1.0"
ANALYSIS_DATE = "2026-09-18"
ANALYSIS_SEED = 20260913
BOOTSTRAP_REPLICATES = 20_000
RELIABILITY_BOOTSTRAP_REPLICATES = 5_000

DIMENSIONS = [
    "completeness",
    "specificity",
    "risk_calibration",
    "integration_awareness",
    "clarification_flag_quality",
]
CONTRASTS = [
    ("ATSR - GSQ", "atsr", "generic_structured_qa"),
    ("ATSR - Naive", "atsr", "naive"),
    ("GSQ - Naive", "generic_structured_qa", "naive"),
]
MODEL_LABELS = {
    "openai/gpt-4o-2024-11-20": "GPT-4o",
    "anthropic/claude-sonnet-4.6": "Claude Sonnet 4.6",
    "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
}
DEPTH_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ratings", type=Path, required=True)
    parser.add_argument("--locked-long", type=Path, required=True)
    parser.add_argument("--locked-results", type=Path, required=True)
    parser.add_argument("--extraction-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def validate_and_join(
    extracted: list[dict[str, str]], locked: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    errors: list[str] = []
    extracted_keys = [(row["rater_id"], row["blind_item_id"]) for row in extracted]
    locked_keys = [(row["rater_id"], row["blind_item_id"]) for row in locked]

    if len(extracted) != 810:
        errors.append(f"Expected 810 extracted assignments, found {len(extracted)}")
    if len(locked) != 810:
        errors.append(f"Expected 810 locked assignments, found {len(locked)}")
    if len(set(extracted_keys)) != len(extracted_keys):
        errors.append("Duplicate (rater_id, blind_item_id) keys in extracted ratings")
    if len(set(locked_keys)) != len(locked_keys):
        errors.append("Duplicate (rater_id, blind_item_id) keys in locked ratings")
    if set(extracted_keys) != set(locked_keys):
        errors.append("Extracted and locked rating keys do not match exactly")

    extracted_index = {
        (row["rater_id"], row["blind_item_id"]): row for row in extracted
    }
    joined: list[dict[str, Any]] = []
    scorable = 0
    invalid = 0
    score_range_ok = True
    totals_ok = True
    invalid_blanks_ok = True
    spec_ids_ok = True
    status_alignment_ok = True

    for source in locked:
        key = (source["rater_id"], source["blind_item_id"])
        row = extracted_index[key]
        output = dict(source)
        spec_ids_ok &= row["spec_id"] == source["spec_id"]

        is_scorable = row["observation_status"] == "Scorable"
        complete = row["rating_status"] == "Complete"
        status_alignment_ok &= is_scorable == bool(source["scorable"])
        status_alignment_ok &= complete == is_scorable

        if is_scorable:
            scorable += 1
            scores: dict[str, int] = {}
            for dimension in DIMENSIONS:
                try:
                    value = int(row[dimension])
                except (TypeError, ValueError):
                    errors.append(f"Non-integer {dimension} at {key}")
                    value = -999
                score_range_ok &= 1 <= value <= 5
                scores[dimension] = value
            try:
                total = int(row["total_score"])
            except (TypeError, ValueError):
                errors.append(f"Non-integer total_score at {key}")
                total = -999
            totals_ok &= total == sum(scores.values())
            output["scores"] = scores
            output["total_score"] = total
            output["rationale"] = None
        else:
            invalid += 1
            invalid_blanks_ok &= all(row[dimension] == "" for dimension in DIMENSIONS)
            invalid_blanks_ok &= row["total_score"] == ""
            output["scores"] = None
            output["total_score"] = None
            output["rationale"] = None
        joined.append(output)

    if not spec_ids_ok:
        errors.append("One or more extracted spec IDs disagree with the locked mapping")
    if not status_alignment_ok:
        errors.append("Scorable/invalid status disagrees with the locked terminal status")
    if not score_range_ok:
        errors.append("One or more scores are outside the permitted 1-5 range")
    if not totals_ok:
        errors.append("One or more totals do not equal the five dimension scores")
    if not invalid_blanks_ok:
        errors.append("One or more invalid observations contains a score or total")

    rater_counts = Counter(row["rater_id"] for row in joined)
    rater_scorable = Counter(row["rater_id"] for row in joined if row["scorable"])
    expected_counts = {"AUTHOR": 486, "PRACTITIONER-01": 162, "PRACTITIONER-02": 162}
    expected_scorable = {"AUTHOR": 401, "PRACTITIONER-01": 132, "PRACTITIONER-02": 132}
    if dict(rater_counts) != expected_counts:
        errors.append(f"Unexpected assignment counts by rater: {dict(rater_counts)}")
    if dict(rater_scorable) != expected_scorable:
        errors.append(f"Unexpected scorable counts by rater: {dict(rater_scorable)}")

    if errors:
        raise ValueError("Rating validation failed:\n- " + "\n- ".join(errors))

    checks = {
        "assignment_count": len(joined),
        "scorable_assignment_count": scorable,
        "structural_failure_assignment_count": invalid,
        "unique_rater_blind_item_keys": True,
        "locked_key_set_exact_match": True,
        "spec_id_mapping_exact_match": True,
        "terminal_status_alignment": True,
        "scores_are_integers_1_to_5": True,
        "all_totals_recalculate": True,
        "invalid_observations_have_blank_scores": True,
        "assignment_counts_by_rater": expected_counts,
        "scorable_counts_by_rater": expected_scorable,
    }
    return joined, checks


def flatten(rows: list[dict[str, Any]]) -> pd.DataFrame:
    flattened: list[dict[str, Any]] = []
    for row in rows:
        record = {
            "rater_id": row["rater_id"],
            "packet_position": row["packet_position"],
            "blind_item_id": row["blind_item_id"],
            "work_id": row["work_id"],
            "spec_id": row["spec_id"],
            "condition": row["condition"],
            "model_id": row["model_id"],
            "model_label": MODEL_LABELS[row["model_id"]],
            "run": row["run"],
            "anchor_run": row["anchor_run"],
            "terminal_status": row["terminal_status"],
            "scorable": bool(row["scorable"]),
            "total_score": row["total_score"],
            "candidate_depth": row["candidate_depth"],
            "consensus_depth": row["consensus_depth"],
            "depth_exact": row["depth_exact"],
            "depth_distance": row["depth_distance"],
            "functional_test_count": row["functional_test_count"],
            "smoke_test_count": row["smoke_test_count"],
            "regression_test_count": row["regression_test_count"],
            "integration_test_count": row["integration_test_count"],
            "exploratory_test_count": row["exploratory_test_count"],
            "clarification_flag_count": row["clarification_flag_count"],
        }
        for dimension in DIMENSIONS:
            record[dimension] = None if row["scores"] is None else row["scores"][dimension]
        flattened.append(record)
    return pd.DataFrame(flattened)


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


def contrast_result(
    frame: pd.DataFrame,
    value_column: str,
    label: str,
    first: str,
    second: str,
    rng: np.random.Generator,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    pivot = frame.pivot(index="spec_id", columns="condition", values=value_column)
    paired = pivot[[first, second]].dropna().sort_index()
    differences = (paired[first] - paired[second]).to_numpy(dtype=float)
    n = len(differences)
    samples = differences[rng.integers(0, n, size=(BOOTSTRAP_REPLICATES, n))].mean(axis=1)
    ci = np.percentile(samples, [2.5, 97.5])
    if np.all(differences == 0):
        statistic, p_value = 0.0, 1.0
    else:
        test = stats.wilcoxon(differences, alternative="two-sided", method="auto")
        statistic, p_value = float(test.statistic), float(test.pvalue)
    result: dict[str, Any] = {
        "contrast": label,
        "first": first,
        "second": second,
        "n_specifications": n,
        "first_mean": float(paired[first].mean()),
        "second_mean": float(paired[second].mean()),
        "paired_mean_difference": float(differences.mean()),
        "paired_median_difference": float(np.median(differences)),
        "bootstrap_95_ci_mean_difference": [float(ci[0]), float(ci[1])],
        "wilcoxon_statistic": statistic,
        "wilcoxon_p_value": p_value,
        "rank_biserial": float(rank_biserial(differences)),
        "positive_ties_negative": {
            "positive": int((differences > 0).sum()),
            "ties": int((differences == 0).sum()),
            "negative": int((differences < 0).sum()),
        },
        "specification_differences": {
            spec_id: float(value)
            for spec_id, value in zip(paired.index.tolist(), differences, strict=True)
        },
    }
    if extra:
        result.update(extra)
    return result


def apply_holm(results: list[dict[str, Any]]) -> None:
    adjusted = holm_adjust([item["wilcoxon_p_value"] for item in results])
    for item, value in zip(results, adjusted, strict=True):
        item["holm_adjusted_p_value"] = value


def work_means(practitioners: pd.DataFrame) -> pd.DataFrame:
    aggregations = {"total_score": "mean", **{dimension: "mean" for dimension in DIMENSIONS}}
    return (
        practitioners.groupby(
            ["work_id", "spec_id", "condition", "model_id", "model_label"],
            as_index=False,
        )
        .agg(aggregations)
        .sort_values(["spec_id", "condition", "model_id"])
    )


def specification_means(work: pd.DataFrame, value_column: str) -> pd.DataFrame:
    return (
        work.groupby(["spec_id", "condition"], as_index=False)[value_column]
        .mean()
        .sort_values(["spec_id", "condition"])
    )


def common_model_means(work: pd.DataFrame, first: str, second: str, value: str) -> tuple[pd.DataFrame, dict[str, int]]:
    records: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for spec_id, group in work.groupby("spec_id"):
        first_models = set(group.loc[group["condition"] == first, "model_id"])
        second_models = set(group.loc[group["condition"] == second, "model_id"])
        common = first_models & second_models
        counts[str(spec_id)] = len(common)
        for condition in (first, second):
            selected = group[(group["condition"] == condition) & group["model_id"].isin(common)]
            records.append(
                {"spec_id": spec_id, "condition": condition, value: float(selected[value].mean())}
            )
    return pd.DataFrame(records), counts


def fixed_model_means(work: pd.DataFrame, models: set[str], value: str) -> pd.DataFrame:
    selected = work[work["model_id"].isin(models)]
    return specification_means(selected, value)


def fully_observed_means(work: pd.DataFrame, first: str, second: str, value: str) -> pd.DataFrame:
    model_count = len(MODEL_LABELS)
    records: list[dict[str, Any]] = []
    for spec_id, group in work.groupby("spec_id"):
        counts = group.groupby("condition")["model_id"].nunique()
        if counts.get(first, 0) == model_count and counts.get(second, 0) == model_count:
            for condition in (first, second):
                records.append(
                    {
                        "spec_id": spec_id,
                        "condition": condition,
                        value: float(group.loc[group["condition"] == condition, value].mean()),
                    }
                )
    return pd.DataFrame(records)


def icc_absolute(matrix: np.ndarray) -> tuple[float, float]:
    n, k = matrix.shape
    grand = matrix.mean()
    row_means = matrix.mean(axis=1)
    column_means = matrix.mean(axis=0)
    ss_rows = k * np.square(row_means - grand).sum()
    ss_columns = n * np.square(column_means - grand).sum()
    residual = matrix - row_means[:, None] - column_means[None, :] + grand
    ss_error = np.square(residual).sum()
    ms_rows = ss_rows / (n - 1)
    ms_columns = ss_columns / (k - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))
    single = (ms_rows - ms_error) / (
        ms_rows + (k - 1) * ms_error + k * (ms_columns - ms_error) / n
    )
    average = (ms_rows - ms_error) / (ms_rows + (ms_columns - ms_error) / n)
    return float(single), float(average)


def ordinal_alpha(matrix: np.ndarray) -> float:
    flat = matrix.ravel()
    categories = sorted(set(int(value) for value in flat))
    frequencies = {category: int((flat == category).sum()) for category in categories}
    total = len(flat)

    def distance(first: int, second: int) -> float:
        if first == second:
            return 0.0
        low, high = sorted((first, second))
        mass = sum(
            frequencies[category] for category in categories if low <= category <= high
        ) - (frequencies[low] + frequencies[high]) / 2
        return float(mass * mass)

    observed = float(np.mean([distance(int(a), int(b)) for a, b in matrix]))
    expected = sum(
        frequencies[a] * frequencies[b] * distance(a, b)
        for a in categories
        for b in categories
    ) / (total * (total - 1))
    return 1.0 if expected == 0 else float(1 - observed / expected)


def reliability(practitioners: pd.DataFrame) -> dict[str, Any]:
    pivot = practitioners.pivot(index="work_id", columns="rater_id", values="total_score").dropna()
    pivot = pivot[["PRACTITIONER-01", "PRACTITIONER-02"]].sort_index()
    matrix = pivot.to_numpy(dtype=float)
    single, average = icc_absolute(matrix)
    rng = np.random.default_rng(ANALYSIS_SEED + 1)
    icc_samples: list[tuple[float, float]] = []
    for _ in range(RELIABILITY_BOOTSTRAP_REPLICATES):
        sampled = matrix[rng.integers(0, len(matrix), len(matrix))]
        values = icc_absolute(sampled)
        if np.isfinite(values).all():
            icc_samples.append(values)
    icc_array = np.asarray(icc_samples)

    alpha_results: dict[str, Any] = {}
    for dimension_index, dimension in enumerate(DIMENSIONS):
        dimension_pivot = practitioners.pivot(
            index="work_id", columns="rater_id", values=dimension
        ).dropna()
        dimension_matrix = dimension_pivot[
            ["PRACTITIONER-01", "PRACTITIONER-02"]
        ].sort_index().to_numpy(dtype=int)
        alpha = ordinal_alpha(dimension_matrix)
        alpha_rng = np.random.default_rng(ANALYSIS_SEED + 10 + dimension_index)
        bootstrap: list[float] = []
        for _ in range(RELIABILITY_BOOTSTRAP_REPLICATES):
            sampled = dimension_matrix[
                alpha_rng.integers(0, len(dimension_matrix), len(dimension_matrix))
            ]
            value = ordinal_alpha(sampled)
            if np.isfinite(value):
                bootstrap.append(value)
        alpha_results[dimension] = {
            "alpha": alpha,
            "bootstrap_95_ci": np.percentile(bootstrap, [2.5, 97.5]).tolist(),
            "bootstrap_successful_replicates": len(bootstrap),
        }

    exact: dict[str, Any] = {}
    for value_column in ["total_score", *DIMENSIONS]:
        item = practitioners.pivot(
            index="work_id", columns="rater_id", values=value_column
        ).dropna()
        differences = np.abs(
            item["PRACTITIONER-01"].to_numpy(dtype=float)
            - item["PRACTITIONER-02"].to_numpy(dtype=float)
        )
        exact[value_column] = {
            "exact": int((differences == 0).sum()),
            "n": len(differences),
            "rate": float((differences == 0).mean()),
            "mean_absolute_difference": float(differences.mean()),
            "maximum_absolute_difference": float(differences.max()),
        }

    return {
        "targets": len(matrix),
        "raters": 2,
        "icc_two_way_random_absolute_single": single,
        "icc_two_way_random_absolute_single_95_ci": np.percentile(
            icc_array[:, 0], [2.5, 97.5]
        ).tolist(),
        "icc_two_way_random_absolute_average_of_two": average,
        "icc_two_way_random_absolute_average_95_ci": np.percentile(
            icc_array[:, 1], [2.5, 97.5]
        ).tolist(),
        "icc_bootstrap_successful_replicates": len(icc_samples),
        "ordinal_krippendorff_alpha": alpha_results,
        "exact_agreement": exact,
    }


def mixed_effects(practitioners: pd.DataFrame) -> dict[str, Any]:
    formula = (
        "total_score ~ C(condition, Treatment(reference='naive')) * "
        "C(model_label, Treatment(reference='GPT-4o'))"
    )
    model = smf.mixedlm(
        formula,
        practitioners,
        groups=practitioners["spec_id"],
        re_formula="1",
        vc_formula={"rater": "0 + C(rater_id)"},
    )
    attempts: list[dict[str, Any]] = []
    fitted_models: list[Any] = []
    all_warning_messages: list[str] = []
    for method in ("lbfgs", "powell", "cg"):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                fitted = model.fit(reml=False, method=method, maxiter=2_000, disp=False)
                fitted_models.append(fitted)
                messages = list(dict.fromkeys(str(item.message) for item in caught))
                all_warning_messages.extend(messages)
                attempts.append(
                    {
                        "method": method,
                        "converged": bool(fitted.converged),
                        "log_likelihood": float(fitted.llf),
                        "warnings": messages,
                    }
                )
            except Exception as exc:  # pragma: no cover - depends on optimizer
                messages = list(dict.fromkeys(str(item.message) for item in caught))
                messages.append(f"{type(exc).__name__}: {exc}")
                all_warning_messages.extend(messages)
                attempts.append(
                    {
                        "method": method,
                        "converged": False,
                        "log_likelihood": None,
                        "warnings": messages,
                    }
                )
    converged = [item for item in fitted_models if item.converged]
    selected = max(converged or fitted_models, key=lambda item: float(item.llf))
    selected_method = next(
        item["method"]
        for item in attempts
        if item["log_likelihood"] is not None
        and math.isclose(item["log_likelihood"], float(selected.llf), rel_tol=0, abs_tol=1e-8)
    )
    fixed: dict[str, Any] = {}
    confidence = selected.conf_int()
    for name, estimate in selected.fe_params.items():
        fixed[str(name)] = {
            "estimate": float(estimate),
            "standard_error": float(selected.bse_fe[name]),
            "p_value": float(selected.pvalues[name]),
            "confidence_interval_95": [
                float(confidence.loc[name, 0]),
                float(confidence.loc[name, 1]),
            ],
        }
    rater_variance = float(selected.vcomp[0]) if len(selected.vcomp) else None
    return {
        "n_ratings": len(practitioners),
        "n_specifications": int(practitioners["spec_id"].nunique()),
        "n_raters": int(practitioners["rater_id"].nunique()),
        "converged": bool(selected.converged),
        "log_likelihood": float(selected.llf),
        "aic": float(selected.aic),
        "bic": float(selected.bic),
        "fixed_effects": fixed,
        "specification_random_intercept_variance": float(selected.cov_re.iloc[0, 0]),
        "rater_variance_component": rater_variance,
        "residual_variance": float(selected.scale),
        "warnings": list(dict.fromkeys(all_warning_messages)),
        "optimizer_attempts": attempts,
        "selected_optimizer": selected_method,
    }


def structural_validity(author: pd.DataFrame) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for (condition, model_id), group in author.groupby(["condition", "model_id"]):
        valid = int(group["scorable"].sum())
        output.append(
            {
                "condition": condition,
                "model_id": model_id,
                "n": len(group),
                "valid": valid,
                "invalid": len(group) - valid,
                "valid_rate": valid / len(group),
            }
        )
    return output


def anchor_depth(author: pd.DataFrame) -> list[dict[str, Any]]:
    anchor = author[(author["run"] == author["anchor_run"]) & author["scorable"]]
    output: list[dict[str, Any]] = []
    for (condition, model_id), group in anchor.groupby(["condition", "model_id"]):
        output.append(
            {
                "condition": condition,
                "model_id": model_id,
                "scorable": len(group),
                "exact": int(group["depth_exact"].sum()),
                "exact_rate": float(group["depth_exact"].mean()),
                "mean_distance": float(group["depth_distance"].mean()),
            }
        )
    return output


def descriptive_counts(author: pd.DataFrame) -> list[dict[str, Any]]:
    anchor = author[(author["run"] == author["anchor_run"]) & author["scorable"]]
    fields = [
        "functional_test_count",
        "smoke_test_count",
        "regression_test_count",
        "integration_test_count",
        "exploratory_test_count",
        "clarification_flag_count",
    ]
    output: list[dict[str, Any]] = []
    for condition, group in anchor.groupby("condition"):
        item: dict[str, Any] = {"condition": condition, "scorable_outputs": len(group)}
        for field in fields:
            item[field] = {
                "mean": float(group[field].mean()),
                "median": float(group[field].median()),
            }
        output.append(item)
    return output


def run_stability(author: pd.DataFrame) -> dict[str, Any]:
    grouped = list(author.groupby(["spec_id", "condition", "model_id"]))
    valid_counts = Counter(int(group["scorable"].sum()) for _, group in grouped)
    score_sds: list[float] = []
    score_ranges: list[float] = []
    complete_depth = 0
    complete_depth_unanimous = 0
    evaluable_depth = 0
    evaluable_depth_unanimous = 0
    for _, group in grouped:
        valid = group[group["scorable"]].sort_values("run")
        if len(valid) >= 2:
            values = valid["total_score"].to_numpy(dtype=float)
            score_sds.append(float(values.std(ddof=1)))
            score_ranges.append(float(values.max() - values.min()))
            depths = valid["candidate_depth"].tolist()
            evaluable_depth += 1
            evaluable_depth_unanimous += int(len(set(depths)) == 1)
        if len(valid) == 3:
            complete_depth += 1
            complete_depth_unanimous += int(valid["candidate_depth"].nunique() == 1)

    pairwise: list[dict[str, Any]] = []
    for first, second in ((1, 2), (1, 3), (2, 3)):
        subset = author[author["scorable"] & author["run"].isin([first, second])]
        pivot = subset.pivot_table(
            index=["spec_id", "condition", "model_id"],
            columns="run",
            values="candidate_depth",
            aggfunc="first",
        ).dropna()
        exact = int((pivot[first] == pivot[second]).sum())
        pairwise.append(
            {
                "runs": [first, second],
                "evaluable_pairs": len(pivot),
                "exact_agreement": exact,
                "exact_agreement_rate": exact / len(pivot),
            }
        )
    return {
        "model_condition_specification_cells": len(grouped),
        "valid_run_count_distribution": {
            str(value): valid_counts.get(value, 0) for value in range(4)
        },
        "cells_with_at_least_two_scores": len(score_sds),
        "mean_within_cell_sd": float(np.mean(score_sds)),
        "median_within_cell_sd": float(np.median(score_sds)),
        "mean_within_cell_range": float(np.mean(score_ranges)),
        "median_within_cell_range": float(np.median(score_ranges)),
        "three_valid_run_cells": complete_depth,
        "three_run_depth_unanimous_cells": complete_depth_unanimous,
        "three_run_depth_unanimous_rate": complete_depth_unanimous / complete_depth,
        "evaluable_depth_cells_at_least_two_runs": evaluable_depth,
        "evaluable_depth_unanimous_rate": evaluable_depth_unanimous / evaluable_depth,
        "pairwise_depth_agreement": pairwise,
    }


def analyze(rows: list[dict[str, Any]], locked_results: dict[str, Any]) -> dict[str, Any]:
    data = flatten(rows)
    practitioners = data[
        data["rater_id"].str.startswith("PRACTITIONER") & data["scorable"]
    ].copy()
    author = data[data["rater_id"] == "AUTHOR"].copy()
    work = work_means(practitioners)
    rng = np.random.default_rng(ANALYSIS_SEED)

    primary_frame = specification_means(work, "total_score")
    primary = [
        contrast_result(primary_frame, "total_score", label, first, second, rng)
        for label, first, second in CONTRASTS
    ]
    apply_holm(primary)

    common_results: list[dict[str, Any]] = []
    for label, first, second in CONTRASTS:
        frame, counts = common_model_means(work, first, second, "total_score")
        common_results.append(
            contrast_result(
                frame,
                "total_score",
                label,
                first,
                second,
                rng,
                {"common_model_count_by_specification": counts},
            )
        )
    apply_holm(common_results)

    complete_models = {
        "openai/gpt-4o-2024-11-20",
        "meta-llama/llama-3.3-70b-instruct",
    }
    complete_frame = fixed_model_means(work, complete_models, "total_score")
    complete_results = [
        contrast_result(complete_frame, "total_score", label, first, second, rng)
        for label, first, second in CONTRASTS
    ]
    apply_holm(complete_results)

    fully_observed_results: list[dict[str, Any]] = []
    for label, first, second in CONTRASTS:
        frame = fully_observed_means(work, first, second, "total_score")
        fully_observed_results.append(
            contrast_result(frame, "total_score", label, first, second, rng)
        )
    apply_holm(fully_observed_results)

    rater_results: dict[str, list[dict[str, Any]]] = {}
    for rater_id in ("PRACTITIONER-01", "PRACTITIONER-02"):
        frame = specification_means(practitioners[practitioners["rater_id"] == rater_id], "total_score")
        items = [
            contrast_result(frame, "total_score", label, first, second, rng)
            for label, first, second in CONTRASTS
        ]
        apply_holm(items)
        rater_results[rater_id] = items

    model_results: list[dict[str, Any]] = []
    for model_id, model_label in MODEL_LABELS.items():
        frame = specification_means(work[work["model_id"] == model_id], "total_score")
        for label, first, second in CONTRASTS:
            model_results.append(
                contrast_result(
                    frame,
                    "total_score",
                    label,
                    first,
                    second,
                    rng,
                    {"model_id": model_id, "model_label": model_label},
                )
            )
    apply_holm(model_results)

    dimension_results: list[dict[str, Any]] = []
    for dimension in DIMENSIONS:
        frame = specification_means(work, dimension)
        for label, first, second in CONTRASTS:
            dimension_results.append(
                contrast_result(
                    frame,
                    dimension,
                    label,
                    first,
                    second,
                    rng,
                    {"dimension": dimension},
                )
            )
    apply_holm(dimension_results)

    distributions: dict[str, Any] = {}
    for condition in ("naive", "generic_structured_qa", "atsr"):
        group = practitioners[practitioners["condition"] == condition]
        distributions[condition] = {}
        for dimension in DIMENSIONS:
            values = group[dimension].to_numpy(dtype=int)
            distributions[condition][dimension] = {
                "n_ratings": len(values),
                "mean": float(values.mean()),
                "median": float(np.median(values)),
                "score_counts": {
                    str(score): int((values == score).sum()) for score in range(1, 6)
                },
            }

    author_all_run_means: list[dict[str, Any]] = []
    for condition, group in author[author["scorable"]].groupby("condition"):
        author_all_run_means.append(
            {
                "condition": condition,
                "total_score": float(group["total_score"].mean()),
                **{dimension: float(group[dimension].mean()) for dimension in DIMENSIONS},
            }
        )

    author_anchor = author[
        author["scorable"] & (author["run"] == author["anchor_run"])
    ]
    author_anchor_frame = specification_means(author_anchor, "total_score")
    author_anchor_results = [
        contrast_result(author_anchor_frame, "total_score", label, first, second, rng)
        for label, first, second in CONTRASTS
    ]
    apply_holm(author_anchor_results)

    output = {
        "protocol_id": PROTOCOL_ID,
        "analysis_date": ANALYSIS_DATE,
        "rating_set_status": "operative_original",
        "analysis_seed": ANALYSIS_SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "reliability_bootstrap_replicates": RELIABILITY_BOOTSTRAP_REPLICATES,
        "library_versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "statsmodels": statsmodels.__version__,
            "krippendorff": "custom_ordinal_implementation",
        },
        "missing_data_treatment": (
            "Persistent invalid JSON retained as missing; no score imputation. "
            "Specification-condition means average available scorable model outputs."
        ),
        "rating_records": {
            "all_assignments": len(rows),
            "scorable": int(data["scorable"].sum()),
            "structural_failure_assignments": int((~data["scorable"]).sum()),
        },
        "primary_and_overall_contrasts": primary,
        "missingness_sensitivities": {
            "common_models_within_each_specification_pair": common_results,
            "complete_GPT4o_and_Llama_models_only": complete_results,
            "fully_observed_three_model_specification_pairs": fully_observed_results,
        },
        "rater_specific_contrasts": rater_results,
        "model_specific_contrasts": model_results,
        "dimension_contrasts": dimension_results,
        "dimension_distributions": distributions,
        "mixed_effects_sensitivity": mixed_effects(practitioners),
        "reliability": reliability(practitioners),
        "structural_validity": structural_validity(author),
        "anchor_depth_accuracy_by_condition_model": anchor_depth(author),
        "depth_reference_sensitivity": locked_results["depth_reference_sensitivity"],
        "descriptive_output_counts": descriptive_counts(author),
        "author_all_run_condition_means": author_all_run_means,
        "author_anchor_contrasts": author_anchor_results,
        "run_stability": run_stability(author),
    }
    return json_value(output)


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def report_text(results: dict[str, Any]) -> str:
    primary = results["primary_and_overall_contrasts"][0]
    reliability_result = results["reliability"]
    sensitivity = results["missingness_sensitivities"]
    mixed = results["mixed_effects_sensitivity"]
    lines = [
        f"# Operative ratings analysis — {PROTOCOL_ID}",
        "",
        f"**Analysis date:** {ANALYSIS_DATE}  ",
        "**Status:** Reproducible analysis using the author-designated operative/original ratings",
        "",
        "## Validation",
        "",
        "All 810 assignments matched the locked blind-item map. The dataset contains 665 complete, scorable ratings and 145 retained invalid-JSON assignments. Every score is an integer from 1 to 5, every total equals the five dimension scores, and invalid observations contain no scores.",
        "",
        "The rating HTML did not contain the rationale column. Rationale is therefore recorded as unavailable rather than copied from the superseded preliminary rating set.",
        "",
        "## Primary result",
        "",
        (
            f"Across {primary['n_specifications']} paired specification-level means, "
            f"ATSR scored {fmt(primary['first_mean'])}/25 and GSQ scored "
            f"{fmt(primary['second_mean'])}/25. The paired mean difference was "
            f"{fmt(primary['paired_mean_difference'])} points (specification-bootstrap "
            f"95% CI {fmt(primary['bootstrap_95_ci_mean_difference'][0])} to "
            f"{fmt(primary['bootstrap_95_ci_mean_difference'][1])}); the paired median "
            f"difference was {fmt(primary['paired_median_difference'])}. Wilcoxon "
            f"W={fmt(primary['wilcoxon_statistic'])}, unadjusted "
            f"p={primary['wilcoxon_p_value']:.4g}, Holm-adjusted "
            f"p={primary['holm_adjusted_p_value']:.4g}, and matched-pairs "
            f"rank-biserial effect={primary['rank_biserial']:.3f}."
        ),
        "",
        (
            f"ATSR was higher on {primary['positive_ties_negative']['positive']} "
            f"specifications, tied on {primary['positive_ties_negative']['ties']}, "
            f"and lower on {primary['positive_ties_negative']['negative']}."
        ),
        "",
        "Persistent invalid JSON was retained as missing with no imputation. Specification-condition means average the available scorable model outputs. Structural validity therefore remains a separate outcome.",
        "",
        "## Overall condition contrasts",
        "",
        "| Contrast | n specs | Mean difference | Bootstrap 95% CI | Median difference | Wilcoxon p | Holm p | Rank-biserial |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in results["primary_and_overall_contrasts"]:
        lines.append(
            f"| {item['contrast']} | {item['n_specifications']} | "
            f"{fmt(item['paired_mean_difference'])} | "
            f"{fmt(item['bootstrap_95_ci_mean_difference'][0])} to "
            f"{fmt(item['bootstrap_95_ci_mean_difference'][1])} | "
            f"{fmt(item['paired_median_difference'])} | "
            f"{item['wilcoxon_p_value']:.4g} | {item['holm_adjusted_p_value']:.4g} | "
            f"{item['rank_biserial']:.3f} |"
        )

    lines += ["", "## Missingness sensitivities", ""]
    for label, key in (
        ("Common models within each specification pair", "common_models_within_each_specification_pair"),
        ("GPT-4o and Llama only", "complete_GPT4o_and_Llama_models_only"),
        ("Fully observed three-model specification pairs", "fully_observed_three_model_specification_pairs"),
    ):
        item = sensitivity[key][0]
        lines.append(
            f"- **{label}:** ATSR minus GSQ = {fmt(item['paired_mean_difference'])} "
            f"points (95% CI {fmt(item['bootstrap_95_ci_mean_difference'][0])} to "
            f"{fmt(item['bootstrap_95_ci_mean_difference'][1])}; "
            f"n={item['n_specifications']}; p={item['wilcoxon_p_value']:.4g})."
        )

    lines += [
        "",
        "## Inter-rater reliability",
        "",
        (
            "The total-score two-way random-effects absolute-agreement "
            f"ICC(2,1) was {reliability_result['icc_two_way_random_absolute_single']:.3f} "
            f"(bootstrap 95% CI {reliability_result['icc_two_way_random_absolute_single_95_ci'][0]:.3f} "
            f"to {reliability_result['icc_two_way_random_absolute_single_95_ci'][1]:.3f}). "
            f"ICC(2,2) was {reliability_result['icc_two_way_random_absolute_average_of_two']:.3f} "
            f"(95% CI {reliability_result['icc_two_way_random_absolute_average_95_ci'][0]:.3f} "
            f"to {reliability_result['icc_two_way_random_absolute_average_95_ci'][1]:.3f})."
        ),
        "",
    ]
    exact = reliability_result["exact_agreement"]["total_score"]
    lines.append(
        f"The practitioners assigned the same total score to {exact['exact']}/{exact['n']} "
        f"outputs ({100 * exact['rate']:.1f}%). Their mean absolute total-score "
        f"difference was {exact['mean_absolute_difference']:.2f}."
    )
    lines += [
        "",
        "| Dimension | Ordinal Krippendorff alpha | Bootstrap 95% CI |",
        "|---|---:|---:|",
    ]
    for dimension in DIMENSIONS:
        item = reliability_result["ordinal_krippendorff_alpha"][dimension]
        lines.append(
            f"| {dimension.replace('_', ' ').title()} | {item['alpha']:.3f} | "
            f"{item['bootstrap_95_ci'][0]:.3f} to {item['bootstrap_95_ci'][1]:.3f} |"
        )

    lines += [
        "",
        "## Run stability",
        "",
    ]
    stability = results["run_stability"]
    lines.append(
        f"Of {stability['model_condition_specification_cells']} model-condition-specification "
        f"cells, {stability['three_valid_run_cells']} had all three valid author-rated runs. "
        f"Across {stability['cells_with_at_least_two_scores']} cells with at least two valid "
        f"scores, the mean within-cell SD was {stability['mean_within_cell_sd']:.2f} points "
        f"and the mean range was {stability['mean_within_cell_range']:.2f} points. Exact "
        f"depth was unanimous in {stability['three_run_depth_unanimous_cells']}/"
        f"{stability['three_valid_run_cells']} complete three-run cells "
        f"({100 * stability['three_run_depth_unanimous_rate']:.1f}%)."
    )

    lines += [
        "",
        "## Mixed-effects sensitivity",
        "",
        (
            f"The mixed-effects model used {mixed['n_ratings']} practitioner ratings, with "
            f"specification and rater random intercepts. Converged: "
            f"{'yes' if mixed['converged'] else 'no'}. Model warnings, optimizer attempts, "
            "and full coefficients are preserved in `analysis-results.json`; interpret this "
            "small, crossed design as a sensitivity analysis rather than the primary result."
        ),
        "",
        "## Reproducibility notes",
        "",
        "- The specification is the principal sampling unit; ratings, dimensions, models, and runs are repeated measurements.",
        "- The two practitioner ratings were averaged before the primary comparison.",
        f"- The percentile bootstrap resampled specifications with replacement using seed {ANALYSIS_SEED}.",
        "- Invalid observations were retained as structural failures and never assigned invented scores.",
        "- Differential invalidity, especially for Claude, can change which models contribute to a specification-condition mean. Structural validity must accompany quality-score comparisons.",
        "- The dataset remains small, single-domain, and synthetic/anonymized from one enterprise QA context.",
        "- The previous rating files remain preserved only as a superseded audit trail and are not used in these results.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(
    output_dir: Path,
    rows: list[dict[str, Any]],
    results: dict[str, Any],
    checks: dict[str, Any],
    input_paths: dict[str, Path],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    long_path = output_dir / "ratings-long.jsonl"
    with long_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n")

    csv_path = output_dir / "ratings-unblinded.csv"
    columns = [
        "rater_id",
        "blind_item_id",
        "spec_id",
        "condition",
        "model_id",
        "run",
        "anchor_run",
        "terminal_status",
        "scorable",
        *DIMENSIONS,
        "total_score",
        "rationale",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            scores = row["scores"] or {}
            writer.writerow(
                {
                    "rater_id": row["rater_id"],
                    "blind_item_id": row["blind_item_id"],
                    "spec_id": row["spec_id"],
                    "condition": row["condition"],
                    "model_id": row["model_id"],
                    "run": row["run"],
                    "anchor_run": row["anchor_run"],
                    "terminal_status": row["terminal_status"],
                    "scorable": row["scorable"],
                    **{dimension: scores.get(dimension, "") for dimension in DIMENSIONS},
                    "total_score": "" if row["total_score"] is None else row["total_score"],
                    "rationale": "",
                }
            )

    results_path = output_dir / "analysis-results.json"
    results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    report_path = output_dir / "analysis-report.md"
    report_path.write_text(report_text(results), encoding="utf-8")

    output_hashes = {
        path.name: sha256(path)
        for path in (long_path, csv_path, results_path, report_path)
    }
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "analysis_date": ANALYSIS_DATE,
        "rating_set_status": "operative_original",
        "provenance_note": (
            "The author designated the renewed HTML-extracted ratings as the operative/original "
            "rating set. The earlier locked rating set was used only for blind-item metadata and "
            "remains preserved as a superseded audit trail."
        ),
        "rationale_availability": (
            "Unavailable in Ratings.html; rationale fields are null/blank and were not copied "
            "from the superseded ratings."
        ),
        "input_hashes": {name: sha256(path) for name, path in input_paths.items()},
        "validation_checks": checks,
        "output_hashes": output_hashes,
        "analysis_command": (
            ".codex-tmp/operative-analysis-venv/bin/python "
            "research/analyze_operative_ratings.py --ratings <ratings-extracted.csv> "
            "--locked-long <ratings-long.jsonl> --locked-results <analysis-results.json> "
            "--extraction-manifest <extraction-manifest.json> --output-dir <new-directory>"
        ),
    }
    (output_dir / "analysis-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    args = parse_args()
    extracted = load_csv(args.ratings)
    locked = load_jsonl(args.locked_long)
    locked_results = json.loads(args.locked_results.read_text(encoding="utf-8"))
    extraction_manifest = json.loads(args.extraction_manifest.read_text(encoding="utf-8"))
    expected_extracted_hash = extraction_manifest["ratings_sha256"]
    if sha256(args.ratings) != expected_extracted_hash:
        raise ValueError("Extracted ratings hash does not match the extraction manifest")

    joined, checks = validate_and_join(extracted, locked)
    results = analyze(joined, locked_results)
    write_outputs(
        args.output_dir,
        joined,
        results,
        checks,
        {
            "ratings_extracted": args.ratings,
            "locked_long_metadata_source": args.locked_long,
            "locked_results_for_unchanged_depth_diagnostic": args.locked_results,
            "extraction_manifest": args.extraction_manifest,
            "analysis_script": Path(__file__).resolve(),
        },
    )
    print(json.dumps({"output_dir": str(args.output_dir), "validation_checks": checks}, indent=2))


if __name__ == "__main__":
    main()
