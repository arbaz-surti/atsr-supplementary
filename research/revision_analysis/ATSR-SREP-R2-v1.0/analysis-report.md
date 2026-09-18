# Expanded evaluation analysis — ATSR-SREP-R2-v1.0

**Analysis date:** 2026-09-14  
**Status:** Reproducible first-pass analysis from the three validated, hash-locked rating returns

## Primary result

Across 18 paired specification-level means, ATSR scored 17.38/25 and GSQ scored 17.61/25. The paired mean difference was -0.22 points (specification-bootstrap 95% CI -0.92 to 0.50); the paired median difference was -0.17. Wilcoxon W=60.50, unadjusted p=0.4486, Holm-adjusted p=0.4486, and matched-pairs rank-biserial effect=-0.209.

ATSR was higher on 8 specifications, tied on 1, and lower on 9.

Persistent invalid JSON was retained as missing with no imputation. Specification-condition means average the available scorable model outputs. Structural validity is therefore reported separately and must accompany quality-score comparisons.

The frozen protocol did not specify how model averaging should handle terminal invalid outputs. The available-output calculation above is therefore not sufficient by itself. Post-hoc missingness sensitivities are reported transparently below and do not replace the primary calculation.

## Overall condition contrasts

| Contrast | n specs | Mean difference | Bootstrap 95% CI | Median difference | Wilcoxon p | Holm p | Rank-biserial |
|---|---:|---:|---:|---:|---:|---:|---:|
| ATSR - GSQ | 18 | -0.22 | -0.92 to 0.50 | -0.17 | 0.4486 | 0.4486 | -0.209 |
| ATSR - Naive | 18 | -0.86 | -1.60 to -0.12 | -0.75 | 0.04499 | 0.135 | -0.538 |
| GSQ - Naive | 18 | -0.64 | -1.53 to 0.26 | -0.83 | 0.2181 | 0.4362 | -0.340 |

## Missingness sensitivities

When each specification contrast uses only models valid under both ATSR and GSQ, the paired mean difference is -0.49 points (95% CI -1.10 to 0.19; n=18 specifications). Restricting to GPT-4o and Llama, the two models with complete validity, gives -0.49 points (95% CI -1.10 to 0.19; n=18). These analyses were specified after observing the invalid-output pattern and must be labeled post hoc.

## Inter-rater reliability

The total-score two-way random-effects absolute-agreement ICC(2,1) was 0.994 (bootstrap 95% CI 0.991 to 0.997). Reliability of the mean of two raters, ICC(2,2), was 0.997 (95% CI 0.995 to 0.998).
The two practitioners assigned exactly the same total score to 113/132 outputs (85.6%); their mean absolute total-score difference was 0.14. This unusually high agreement should be reported and audited against the independence procedures.

| Dimension | Ordinal Krippendorff alpha | Bootstrap 95% CI |
|---|---:|---:|
| Completeness | 0.910 | 0.849 to 0.953 |
| Specificity | 1.000 | 1.000 to 1.000 |
| Risk Calibration | 1.000 | 1.000 to 1.000 |
| Integration Awareness | 0.996 | 0.985 to 1.000 |
| Clarification Flag Quality | 0.997 | 0.989 to 1.000 |

## Run stability

Of 162 model-condition-specification cells, 130 had all three valid author-rated runs. Across the 134 cells with at least two valid scores, the mean within-cell SD was 1.06 points and the mean range was 1.97 points. Exact depth was unanimous in 120/130 complete three-run cells (92.3%).

## Mixed-effects sensitivity

The mixed-effects model used 264 practitioner ratings, with specification and rater random intercepts. Converged: yes. Model warnings, optimizer attempts, and full coefficients are preserved in `analysis-results.json`; interpret this small, crossed design as a sensitivity analysis rather than the primary result.

## Reproducibility and limitations

- The specification is the principal sampling unit; ratings, dimensions, models, and runs are repeated measurements.
- The two practitioner ratings were averaged before the confirmatory comparison.
- The percentile bootstrap resampled specifications with replacement using seed 20260913.
- Invalid observations were retained as structural failures and never assigned invented scores.
- Differential invalidity, especially for Claude, can change which models contribute to a specification-condition mean. Report validity with every score comparison.
- The dataset remains small, single-domain, and synthetic/anonymized from one enterprise QA context.
