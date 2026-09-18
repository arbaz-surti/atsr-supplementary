# Operative ratings analysis — ATSR-SREP-R2-v1.0

**Analysis date:** 2026-09-18  
**Status:** Reproducible analysis using the author-designated operative/original ratings

## Validation

All 810 assignments matched the locked blind-item map. The dataset contains 665 complete, scorable ratings and 145 retained invalid-JSON assignments. Every score is an integer from 1 to 5, every total equals the five dimension scores, and invalid observations contain no scores.

The rating HTML did not contain the rationale column. Rationale is therefore recorded as unavailable rather than copied from the superseded preliminary rating set.

## Primary result

Across 18 paired specification-level means, ATSR scored 19.70/25 and GSQ scored 18.21/25. The paired mean difference was 1.49 points (specification-bootstrap 95% CI 0.84 to 2.07); the paired median difference was 1.46. Wilcoxon W=14.50, unadjusted p=0.00197, Holm-adjusted p=0.00197, and matched-pairs rank-biserial effect=0.830.

ATSR was higher on 17 specifications, tied on 0, and lower on 1.

Persistent invalid JSON was retained as missing with no imputation. Specification-condition means average the available scorable model outputs. Structural validity therefore remains a separate outcome.

## Overall condition contrasts

| Contrast | n specs | Mean difference | Bootstrap 95% CI | Median difference | Wilcoxon p | Holm p | Rank-biserial |
|---|---:|---:|---:|---:|---:|---:|---:|
| ATSR - GSQ | 18 | 1.49 | 0.84 to 2.07 | 1.46 | 0.00197 | 0.00197 | 0.830 |
| ATSR - Naive | 18 | 3.76 | 3.09 to 4.51 | 3.62 | 0.0001961 | 0.0005883 | 1.000 |
| GSQ - Naive | 18 | 2.27 | 1.57 to 3.06 | 1.54 | 0.0002902 | 0.0005883 | 1.000 |

## Missingness sensitivities

- **Common models within each specification pair:** ATSR minus GSQ = 1.44 points (95% CI 0.81 to 2.01; n=18; p=0.001958).
- **GPT-4o and Llama only:** ATSR minus GSQ = 1.33 points (95% CI 0.68 to 1.92; n=18; p=0.002628).
- **Fully observed three-model specification pairs:** ATSR minus GSQ = 1.67 points (95% CI 0.50 to 2.50; n=3; p=0.25).

## Inter-rater reliability

The total-score two-way random-effects absolute-agreement ICC(2,1) was 0.721 (bootstrap 95% CI 0.630 to 0.792). ICC(2,2) was 0.838 (95% CI 0.773 to 0.884).

The practitioners assigned the same total score to 40/132 outputs (30.3%). Their mean absolute total-score difference was 1.39.

| Dimension | Ordinal Krippendorff alpha | Bootstrap 95% CI |
|---|---:|---:|
| Completeness | 0.670 | 0.558 to 0.763 |
| Specificity | 0.652 | 0.528 to 0.752 |
| Risk Calibration | 0.695 | 0.595 to 0.776 |
| Integration Awareness | 0.666 | 0.549 to 0.760 |
| Clarification Flag Quality | 0.674 | 0.560 to 0.769 |

## Run stability

Of 162 model-condition-specification cells, 130 had all three valid author-rated runs. Across 134 cells with at least two valid scores, the mean within-cell SD was 1.83 points and the mean range was 3.44 points. Exact depth was unanimous in 120/130 complete three-run cells (92.3%).

## Mixed-effects sensitivity

The mixed-effects model used 264 practitioner ratings, with specification and rater random intercepts. Converged: yes. Model warnings, optimizer attempts, and full coefficients are preserved in `analysis-results.json`; interpret this small, crossed design as a sensitivity analysis rather than the primary result.

## Reproducibility notes

- The specification is the principal sampling unit; ratings, dimensions, models, and runs are repeated measurements.
- The two practitioner ratings were averaged before the primary comparison.
- The percentile bootstrap resampled specifications with replacement using seed 20260913.
- Invalid observations were retained as structural failures and never assigned invented scores.
- Differential invalidity, especially for Claude, can change which models contribute to a specification-condition mean. Structural validity must accompany quality-score comparisons.
- The dataset remains small, single-domain, and synthetic/anonymized from one enterprise QA context.
- The previous rating files remain preserved only as a superseded audit trail and are not used in these results.
