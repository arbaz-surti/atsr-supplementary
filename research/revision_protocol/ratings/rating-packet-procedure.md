# Study-output rating-packet procedure

**Protocol:** `ATSR-SREP-R2-v1.0`  
**Prepared:** 2026-09-14  
**State:** Three completed packets received, validated, and hash-locked; controlled
score import and first-pass statistical analysis complete

## Release gate

Do not distribute a packet until the coded practitioner-qualification records,
applicable ethics arrangement, and prospective consent records have been confirmed.
These records must reflect what actually occurred and must not be backdated.

Completed workbooks were received on 2026-09-14. The author confirmed the same day
that the administrative records were in place before distribution; this chronology
statement is preserved in `administrative-chronology-confirmation.md`. The underlying
private documents are not stored or independently verified in this repository.

## Frozen inputs

| Input | SHA-256 |
|---|---|
| `outputs/b3-evaluation-kit/consensus-adjudication-completed.xlsx` | `6362cb097a3bb8fe2dff7cae672a14918765b80294fc81c0ffd49e266a7c2d04` |
| `research/revision_protocol/ratings/rubric-v1-final.md` | `dcf39358be89355afc013cdccf55888ca5a96b02862e763c5c39a9acb07b2355` |
| `outputs/b3-evaluation-kit/rubric-calibration-reconciliation-completed.xlsx` | `96f453642bcd0cce05b0d29dfc681f186754c8759038a53aa21ed00650d80bf6` |

## Issued packet set

| Rater | Workbook | Rows | Scorable | Structural failures | SHA-256 |
|---|---|---:|---:|---:|---|
| AUTHOR | `outputs/b3-rating-packets/rating-packet-author.xlsx` | 486 | 401 | 85 | `05a67c677d85f8f9a0b003bbdda54f99af0dcadb17914520f05aa9061293e55c` |
| PRACTITIONER-01 | `outputs/b3-rating-packets/rating-packet-practitioner-01.xlsx` | 162 | 132 | 30 | `a3f01a9bdb30601894de1349a79b513bc42aad5f5a31c582203f3b393539835b` |
| PRACTITIONER-02 | `outputs/b3-rating-packets/rating-packet-practitioner-02.xlsx` | 162 | 132 | 30 | `67f6782550de35f68f750287982421df1e5ad711e1ea122eb66c209db5582ada` |

The author packet contains the full randomized 486-observation queue. Each
practitioner packet contains the same preregistered 162-observation anchor set—one
run for every model × condition × specification cell—but uses a rater-specific order
and different opaque item IDs.

## Deterministic selection and blinding

- Anchor run: calculate SHA-256 over the literal string
  `model_id|condition|spec_id|20260913`, with `|` delimiters and no added
  whitespace; interpret the first eight hexadecimal digits as an integer, take
  modulo 3, and add 1.
- Presentation order: ascending SHA-256 over
  `protocol_id|rater_id|work_id|rating-order|20260913`.
- Blind item ID: `RATE-` plus the first 12 uppercase hexadecimal digits of SHA-256
  over `protocol_id|rater_id|work_id|blind-id|20260913`.
- The packets withhold model, provider, experimental condition, run number, and
  original work ID. The private lookup is
  `research/revision_protocol/blind/rating-item-map.jsonl`, SHA-256
  `bb231db1935af724be78ad152d4b9a72084aa5479d1f0e9a7dffdb3a42c3ca9d`.
  Do not distribute this lookup to raters.
- The packet manifest is
  `research/revision_protocol/blind/rating-packet-manifest.json`, SHA-256
  `4d99b6f9f3b1728b765b885c3b5b44f7b89f6c89d343442cb7c8256d07af7f52`.

## Rater workflow

1. Give each person only the workbook bearing their coded rater ID.
2. Ask the rater to read `Read First`, the frozen consensus reference, and the final
   rubric embedded in the workbook before scoring.
3. For every row marked `Scorable`, enter integer scores from 1 to 5 for all five
   dimensions. Do not discuss ratings with another rater before return.
4. Enter a rationale whenever any dimension receives 1, 2, or 5. The workbook shows
   `Complete` only after the required entries are present.
5. Do not score rows marked `Not scorable — terminal invalid JSON`. Their blank
   scores are retained structural failures, not missing human work.
6. Return the completed workbook without renaming sheets, changing source text,
   sorting rows, or adding/removing rows.

## Return, validation, and lock

For each returned workbook:

1. Archive the received file unchanged under a clearly identified completed name and
   record its SHA-256 before analysis.
2. Confirm the coded rater ID; exact blind-item ID set and order; expected counts;
   unchanged specification, candidate, and status text; preserved formulas; and
   valid XLSX archive structure.
3. Confirm every scorable row has five integer scores in the 1–5 range, all required
   rationales are present, every scorable status is `Complete`, every structural
   failure remains unscored, and there are no spreadsheet formula errors.
4. Do not open the private item map for score analysis until all three completed
   packets have been received, validated, and hash-locked.
5. After that lock, join ratings to model, condition, specification, and run only via
   the private mapping. Preserve rater-level data and structural failures; do not
   impute content scores for invalid outputs.

## Completed returns

| Rater | Archived workbook | SHA-256 | Validation |
|---|---|---|---|
| AUTHOR | `outputs/b3-rating-packets/completed/rating-packet-author-completed.xlsx` | `cafc66709a9f1ad18df779876f14993c1975031a9a48ac16efac02ca849124ec` | PASS: 401/401 scorable rows complete; 85/85 structural failures untouched |
| PRACTITIONER-01 | `outputs/b3-rating-packets/completed/rating-packet-practitioner-01-completed.xlsx` | `fbbc79e39c47c8999a2e756065603b4d7666103bcff235020f418adddbb2bfd2` | PASS: 132/132 scorable rows complete; 30/30 structural failures untouched |
| PRACTITIONER-02 | `outputs/b3-rating-packets/completed/rating-packet-practitioner-02-completed.xlsx` | `fab778e4a4f95f1a70860f8b043bfb264ceec25eb2a139f84a8aa60f5dae3dd2` | PASS: 132/132 scorable rows complete; 30/30 structural failures untouched |

The machine-readable validation record is
`research/revision_protocol/ratings/rating-return-validation.json`. No rating was
unblinded or compared during return validation.

## Verification completed at preparation

- All three workbooks reopened successfully and passed XLSX ZIP-integrity checks.
- All 810 blind IDs are unique; the two practitioner packets contain the same anchor
  work IDs in different orders and with different blind IDs.
- Score-entry cells are blank; status formulas correctly distinguish incomplete,
  rationale-required, complete, and not-scorable rows.
- A workbook-content scan found no model, provider, condition, run, or original work
  identifiers in the distributed files.
- All 12 worksheet previews were visually inspected after the final layout change.
- The generation archive audit passes with 486 terminal observations, 401 valid
  outputs, 85 retained invalid-JSON observations, and zero provider mismatches.
