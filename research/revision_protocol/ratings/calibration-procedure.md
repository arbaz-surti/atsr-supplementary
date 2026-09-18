# B3 neutral rubric calibration procedure

**Prepared:** 2026-09-14  
**Protocol:** ATSR-SREP-R2-v1.0  
**Status:** Calibration reconciled; final rubric frozen and hash-locked

## Purpose

Align the three raters on the five 1–5 scoring dimensions before any of the 486 study
outputs are opened for scoring. The calibration case and 25 examples are external to
the study dataset. Calibration may clarify the draft rubric but must not be tuned to
study outputs.

## Preconditions

1. Confirm the applicable ethics arrangement and whether informed consent was in place
   for earlier participation. Do not backdate any record.
2. Obtain prospective consent for this new calibration and rating activity before
   distributing a workbook.
3. Complete the coded practitioner-qualification records and confirm that `AUTHOR`,
   `PRACTITIONER-01`, and `PRACTITIONER-02` are the intended non-identifying codes.
4. Do not open or distribute the reconciliation workbook during independent scoring.

## Independent calibration workbooks

| Rater | Workbook | SHA-256 |
|---|---|---|
| AUTHOR | `outputs/b3-evaluation-kit/rubric-calibration-author.xlsx` | `b76a8c56fe24bc0efe4c27bd2b2c50b655b73e00d1a1b9b144e4e5149c82c260` |
| PRACTITIONER-01 | `outputs/b3-evaluation-kit/rubric-calibration-practitioner-01.xlsx` | `2bfdec814e942c8d478aa1c6bba46882ba3f403a126d89b0826002f889df2a56` |
| PRACTITIONER-02 | `outputs/b3-evaluation-kit/rubric-calibration-practitioner-02.xlsx` | `7f92f9ad9b65c4850d513344767a2fb5a1a337f34880fa72fcd2199588f9ffbb` |

Each workbook contains the same 25 opaque-ID items in a different deterministic order.
It includes the neutral case and draft rubric anchors but no intended calibration
scores, model identities, conditions, study specifications, or study outputs.

Each rater must enter one integer score from 1 to 5 and an anchor-based rationale for
all 25 items. Notes are optional. The workbook is complete only when all 25 status
cells read `Complete`.

Returned independent calibration files:

| Rater | Archived workbook | SHA-256 | Validation |
|---|---|---|---|
| AUTHOR | `outputs/b3-evaluation-kit/rubric-calibration-author-completed.xlsx` | `77332300d67ac0a9047c2c7d02740a2bdb5859c7c91b1050e1ea77acb4942593` | 25 valid scores; 25 rationales; all rows complete; source text and formulas preserved; zero formula errors |
| PRACTITIONER-01 | `outputs/b3-evaluation-kit/rubric-calibration-practitioner-01-completed.xlsx` | `fd5cd4f0026d326f7362bac54b54006d3098175ace6cb771014168fe3975663b` | 25 valid scores; 25 rationales; all rows complete; source text and formulas preserved; zero formula errors |
| PRACTITIONER-02 | `outputs/b3-evaluation-kit/rubric-calibration-practitioner-02-completed.xlsx` | `722f283659811d05cd123e1b128cdf65920e5a6f6dd0d14dae7eadeb3cb5ad0a` | 25 valid scores; 25 rationales; all rows complete; source text and formulas preserved; zero formula errors |

All three files were archived before comparison. Source scores were then mapped by
opaque item ID into
`outputs/b3-evaluation-kit/rubric-calibration-reconciliation-populated.xlsx`
(SHA-256
`75e864e2833a4b8c27b73ef731c6b390b1d4b87e36763f3ad4ab7c0f1233ce15`).
All 25 rows are unanimous across the three raters, and all 25 unanimous scores match
the draft intended score. On 2026-09-14, all three raters jointly affirmed the 25
decisions and confirmed that no wording changes were required.

Completed reconciliation workbook:
`outputs/b3-evaluation-kit/rubric-calibration-reconciliation-completed.xlsx`
(SHA-256
`96f453642bcd0cce05b0d29dfc681f186754c8759038a53aa21ed00650d80bf6`).

## Return and reconciliation

1. Receive all three workbooks before comparing any scores.
2. Archive each returned file unchanged and record its SHA-256 hash.
3. Copy scores into
   `outputs/b3-evaluation-kit/rubric-calibration-reconciliation.xlsx` by opaque item
   ID. Do not use row position because each rater received a different order.
4. Discuss every non-unanimous item and any unanimous item that reveals ambiguous
   anchor wording.
5. Record the final agreed score, whether wording must change, the agreed
   interpretation or exact wording change, and `YES` under `All raters affirm?`.
6. Preserve the three original scores. Calibration reconciliation does not overwrite
   independent judgments.

Reconciliation workbook SHA-256 before human entry:
`6b617b44a73e929272dfee8cb952c39691d249d798e2be558ffb1b3e0123f4e0`.

## Rubric freeze rule

The rubric can be frozen only when:

- all 25 comparison rows read `Complete`;
- all three raters affirm every final calibration decision;
- every approved wording change has been applied to a new file named
  `rubric-v1-final.md` rather than overwriting the draft;
- the final file states `Final`, the protocol ID, and the freeze date;
- its SHA-256 is recorded in the reconciliation workbook, kit manifest, results
  reference, and revision plan; and
- the `Freeze Record` status reads `Ready to freeze`.

After the hash is recorded, do not edit the final rubric in place. A later change
requires a versioned amendment. Do not create or open blinded study-output rating
packets until this freeze is complete.

Freeze completed on 2026-09-14. Final rubric:
`research/revision_protocol/ratings/rubric-v1-final.md` (SHA-256
`dcf39358be89355afc013cdccf55888ca5a96b02862e763c5c39a9acb07b2355`).
The completed reconciliation workbook records the same hash and reads
`Ready to freeze`.

## Verification performed

- All four workbooks reopened successfully and passed formula-error scans and ZIP
  integrity checks.
- The three independent workbooks contain the same 25 opaque IDs in three different
  orders and have blank score, rationale, and notes fields.
- No independent workbook contains an answer-key or intended-score sheet.
- Completion formulas were tested for complete and missing-field states.
- Reconciliation and freeze formulas were tested for complete, affirmed, and
  incomplete states.
- Every worksheet was rendered and visually inspected.
- The completed reconciliation reopened with 25 `Complete` rows, 25 affirmative
  decisions, 25 `NO` rubric-change decisions, the final rubric hash, zero formula
  errors, and valid XLSX ZIP integrity.
