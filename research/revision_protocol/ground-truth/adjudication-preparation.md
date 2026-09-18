# B3 adjudication preparation

**Prepared:** 2026-09-14  
**Protocol:** ATSR-SREP-R2-v1.0  
**Dataset SHA-256:** `48d94cce163cf21efa712939bd4334b0a89260434aafe0d83a00cbd2dd3856f0`  
**Status:** Human consensus completed and frozen on 2026-09-14

## Prepared workbook

- Workbook: `outputs/b3-evaluation-kit/consensus-adjudication-populated.xlsx`
- SHA-256: `1895695300fd7d68d42b83391abe031df580217a9153c54e04027d6ecce54078`
- The `Depth` source columns contain all 54 submitted depth values: 18 specifications
  times three raters.
- The `Scope` source columns contain all 324 submitted judgments: 18 specifications
  times six categories times three raters.
- Source wording was copied exactly from the three hash-locked completed workbooks.
- Consensus fields, reasons, evidence classifications, initials, and decision dates
  remain blank. No consensus value was inferred or selected automatically.
- Status cells remain `Missing fields` until the human adjudicators complete every
  required adjudication field.

The blank template and the three completed independent workbooks remain unchanged.

## Completed consensus reference

- Workbook: `outputs/b3-evaluation-kit/consensus-adjudication-completed.xlsx`
- SHA-256: `6362cb097a3bb8fe2dff7cae672a14918765b80294fc81c0ffd49e266a7c2d04`
- The completed file was archived byte-for-byte from the returned workbook; the
  prepared workbook and blank template were not overwritten.
- Completion checks: 18 of 18 depth rows complete; 108 of 108 scope rows complete;
  zero missing required fields; zero invalid consensus depth labels; zero formula-
  error matches; valid XLSX ZIP integrity.
- Consensus depth distribution: 15 `HIGH`, 3 `MEDIUM`, 0 `LOW`.
- Evidence basis: 32 `Explicit`, 36 `Implicit`, and 40 `Mixed` scope decisions.
- All decisions use coded adjudicator entry `QA1/QA2/QA3` and decision date
  2026-09-14. Confirm that this code is the intended identifier in the private
  participant records.
- The source columns in the completed workbook match the prepared workbook exactly.

## Comparison map

### Coverage depth

The raters agree exactly on 14 of 18 depth judgments. Four specifications require
discussion:

| Spec ID | Author | Practitioner 01 | Practitioner 02 |
|---|---:|---:|---:|
| SPEC-03 | HIGH | HIGH | MEDIUM |
| SPEC-09 | HIGH | HIGH | MEDIUM |
| SPEC-13 | HIGH | HIGH | MEDIUM |
| SPEC-18 | HIGH | HIGH | MEDIUM |

The 14 exact agreements are comparison results only. The adjudicators must still enter
and document the consensus value in the yellow fields; the preparation step does not
promote a majority or unanimous input into consensus automatically.

### Essential scope

- Applicability agreement: 108 of 108 rows. For every specification/category pair,
  all three raters either supplied content or all three entered `NONE`.
- Exact lexical agreement: 1 of 108 rows. All three entered `NONE` for SPEC-12
  Integration.
- Wording or atomic-element differences: 107 of 108 rows.

The 107 differences do not mean 107 substantive conflicts. Each rater described scope
in independent language and at different granularity. Adjudication should compare the
semicolon-separated atomic elements and decide which elements are essential. It should
not use exact string equality as the decision rule.

## Adjudication sequence and remaining gate

1. Confirm and document whether the required ethics arrangement and informed consent
   were in place before independent participation; do not backdate records. If they
   were not, obtain appropriate ethics or journal direction before using those data.
   Complete the coded qualification records and obtain consent for any new joint
   adjudication activity before that activity begins.
2. Completed: the adjudicators reviewed the four depth disagreements first, then
   confirmed the remaining 14 depth rows and recorded one consensus depth, the reason,
   adjudicator initials, and decision date for every specification.
3. Completed: the adjudicators reviewed the 108 scope rows by specification and
   reconciled atomic elements across the three source columns. They entered the
   consensus essential elements and recorded decision reasons.
4. Completed: each scope row records the evidence basis and any implicit inferential link.
5. Completed: all 18 `Depth` statuses and all 108 `Scope` statuses read `Complete`,
   and the completed consensus reference is archived and hashed.
6. Next: finalize and hash the expanded rating rubric through neutral calibration. Generate
   blinded model-output rating packets only after both the consensus reference and
   rubric are frozen.

## Controls

- Do not edit the three completed rater workbooks or their archived raw submissions.
- Do not overwrite the blank `consensus-adjudication.xlsx` template.
- Do not copy model outputs, model identities, conditions, runs, or ratings into the
  adjudication workbook.
- Do not regenerate or invent scores for the 85 retained invalid-JSON observations.
