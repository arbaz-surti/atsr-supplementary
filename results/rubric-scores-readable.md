# ATSR Evaluation — Rubric Scores
**Model:** GPT-4o | **Total Specs:** 18 | **Overall Score:** 380/450 (84.4%)

## Scoring Key
| Score | Meaning |
|---|---|
| 5 | Excellent |
| 4 | Good |
| 3 | Adequate |
| 2 | Weak |
| 1 | Poor |

**Dimensions:**
- **C** = Completeness — are all relevant test types covered?
- **S** = Specificity — are test descriptions concrete and actionable?
- **R** = Risk Calibration — is the coverage depth (LOW/MEDIUM/HIGH) correct?
- **I** = Integration Awareness — are cross-system touchpoints identified?
- **F** = Clarification Flag Quality — are the flagged gaps useful and actionable?

---

## Results Table

| Spec | Title | C | S | R | I | F | Total /25 |
|---|---|---|---|---|---|---|---|
| SPEC-01 | Online Ordering Portal Menu Sync Bug | 5 | 4 | 5 | 4 | 4 | **22** |
| SPEC-02 | Payment Firmware Patch — Quick Chip Reconnection | 5 | 5 | 5 | 3 | 3 | **21** |
| SPEC-03 | New Wi-Fi 7 Access Point Hardware Rollout | 5 | 4 | 5 | 4 | 4 | **22** |
| SPEC-04 | New Catering Voucher Tender Key on POS | 4 | 3 | 5 | 3 | 4 | **19** |
| SPEC-05 | New Extra-Large Beverage Size Menu Addition | 5 | 5 | 5 | 4 | 4 | **23** |
| SPEC-06 | Menu Item Availability App Time Window Enhancement | 5 | 5 | 5 | 4 | 4 | **23** |
| SPEC-08 | Role-Based Access Control — Void on Empty Check | 5 | 5 | 5 | 4 | 3 | **22** |
| SPEC-09 | Delivery Markup Percentage Config Change | 4 | 4 | 5 | 4 | 5 | **22** |
| SPEC-10 | SSL Certificate Renewal for Loyalty Platform | 4 | 4 | 5 | 4 | 3 | **20** |
| SPEC-11 | Mobile App Advance Order Price Lock Behavior | 4 | 4 | 4 | 4 | 3 | **19** |
| SPEC-12 | Financial Report Layout Change — Section Reordering | 5 | 4 | 5 | 3 | 3 | **20** |
| SPEC-13 | POS Hierarchy Zone Addition — Non-Traditional Locations | 5 | 4 | 5 | 4 | 3 | **21** |
| SPEC-14 | Digital Ordering App Upgrade — Device/OS Matrix Testing | 5 | 5 | 5 | 4 | 5 | **24** |
| SPEC-15 | Gift Card Cancel Messaging Bug Fix | 3 | 5 | 5 | 3 | 2 | **18** |
| SPEC-16 | BIN Range Regression — Existing Coupons Unaffected | 3 | 3 | 4 | 3 | 3 | **16** |
| SPEC-17 | Antivirus Exclusion Script Deployment | 5 | 4 | 5 | 4 | 4 | **22** |
| SPEC-18 | POS Crew Notification Feature Enablement | 5 | 5 | 5 | 5 | 5 | **25** |
| SPEC-19 | Secondary DNS Provider Change — Broad System Regression | 5 | 3 | 5 | 5 | 3 | **21** |

---

## Dimension Averages

| Dimension | Total /90 | Average /5 | % |
|---|---|---|---|
| Risk Calibration | 88 | 4.89 | 97.8% |
| Completeness | 82 | 4.56 | 91.1% |
| Specificity | 76 | 4.22 | 84.4% |
| Integration Awareness | 69 | 3.83 | 76.7% |
| Clarification Flag Quality | 65 | 3.61 | 72.2% |
| **Overall** | **380** | **4.22** | **84.4%** |

---

## Notable Results

| | Spec | Score | Why |
|---|---|---|---|
| Highest | SPEC-18 (POS Crew Notification) | 25/25 | Perfect across all dimensions — new feature with clear scope, strong integration reasoning, all 3 flags would materially change test design |
| Second highest | SPEC-14 (Digital Ordering App Upgrade) | 24/25 | All 4 device/OS combinations covered, critical flag on pending release notes |
| Lowest | SPEC-16 (BIN Range Regression) | 16/25 | Missed BIN range boundary/conflict testing — the most important test — and missed deployment pipeline consideration |
| Second lowest | SPEC-15 (Gift Card Messaging Fix) | 18/25 | Very specific on the bug itself but thin across regression, integration, and flags |

---

## Coverage Depth Distribution

| Depth | Specs | Correct? |
|---|---|---|
| LOW | SPEC-02, SPEC-09, SPEC-10, SPEC-15 | All correct ✓ |
| MEDIUM | SPEC-01, SPEC-03, SPEC-06, SPEC-08, SPEC-12, SPEC-13, SPEC-16, SPEC-17 | All correct ✓ (SPEC-16 debatable) |
| HIGH | SPEC-04, SPEC-05, SPEC-11, SPEC-14, SPEC-18, SPEC-19 | All correct ✓ (SPEC-11 debatable) |

---

## Key Findings Summary

1. **Risk calibration is near-perfect (97.8%)** — ATSR reliably determines how deeply to test based on change type alone
2. **Completeness is very high (91.1%)** — rarely misses a test dimension entirely
3. **Weakest dimension: Clarification Flag Quality (72.2%)** — flags become generic when specs are sparse, showing quality correlates with input richness
4. **SPEC-16 outlier** — implicit risks (BIN range conflicts) were missed because the spec didn't state them explicitly; requires domain knowledge to infer
5. **Added value beyond specs** — ATSR surfaced test ideas not in the ground truth in 7 of 18 specs (DST edge case, Wi-Fi handoff, audit logging, mobile app integration, cert import failure, simultaneous clock-ins, network failover)
