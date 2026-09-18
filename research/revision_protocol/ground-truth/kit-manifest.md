# B3 evaluation-kit manifest

**Created:** 2026-09-14  
**Protocol:** ATSR-SREP-R2-v1.0  
**Stage:** Ground truth, consensus, calibration, final rubric, and all three completed
study-output rating returns are validated and hash-locked. Ratings are imported through
the private map and the first-pass statistical analysis is complete. The author confirmed
that qualification, ethics-arrangement, and consent records were in place before packet
distribution; the underlying private records are not stored in this repository.

## Distribution workbooks

| File | Intended user | SHA-256 |
|---|---|---|
| `outputs/b3-evaluation-kit/author-ground-truth.xlsx` | Author | `22e5e6c35f3dab583ea3aafadd013ae1ac818155f1a5fcaefdb83a30aac2d565` |
| `outputs/b3-evaluation-kit/practitioner-01-ground-truth.xlsx` | Practitioner 01 | `b01f4294a2c48ec059aeef3234fd4420e994baf5742207b63ff2c2b4c3e3d7d7` |
| `outputs/b3-evaluation-kit/practitioner-02-ground-truth.xlsx` | Practitioner 02 | `ecd928736e6b417b069a629796400093e2e2dec0d533f28ca656e93847acb6d5` |
| `outputs/b3-evaluation-kit/consensus-adjudication.xlsx` | Three-person adjudication | `2b5a954abb4e34d0aef0a41b2d2a02302fe0132e6fe1733c649e6c28867843a3` |

Prepared adjudication copy:

| File | Purpose | SHA-256 |
|---|---|---|
| `outputs/b3-evaluation-kit/consensus-adjudication-populated.xlsx` | Source comparison and human consensus entry | `1895695300fd7d68d42b83391abe031df580217a9153c54e04027d6ecce54078` |

Completed consensus reference:

| File | Purpose | SHA-256 |
|---|---|---|
| `outputs/b3-evaluation-kit/consensus-adjudication-completed.xlsx` | Frozen consensus ground truth | `6362cb097a3bb8fe2dff7cae672a14918765b80294fc81c0ffd49e266a7c2d04` |

Neutral rubric-calibration kit:

| File | Purpose | SHA-256 |
|---|---|---|
| `outputs/b3-evaluation-kit/rubric-calibration-author.xlsx` | Independent AUTHOR calibration | `b76a8c56fe24bc0efe4c27bd2b2c50b655b73e00d1a1b9b144e4e5149c82c260` |
| `outputs/b3-evaluation-kit/rubric-calibration-practitioner-01.xlsx` | Independent PRACTITIONER-01 calibration | `2bfdec814e942c8d478aa1c6bba46882ba3f403a126d89b0826002f889df2a56` |
| `outputs/b3-evaluation-kit/rubric-calibration-practitioner-02.xlsx` | Independent PRACTITIONER-02 calibration | `7f92f9ad9b65c4850d513344767a2fb5a1a337f34880fa72fcd2199588f9ffbb` |
| `outputs/b3-evaluation-kit/rubric-calibration-reconciliation.xlsx` | Post-return comparison and rubric freeze record | `6b617b44a73e929272dfee8cb952c39691d249d798e2be558ffb1b3e0123f4e0` |

Returned neutral calibration workbooks:

| File | Rater | SHA-256 | Validation |
|---|---|---|---|
| `outputs/b3-evaluation-kit/rubric-calibration-author-completed.xlsx` | AUTHOR | `77332300d67ac0a9047c2c7d02740a2bdb5859c7c91b1050e1ea77acb4942593` | 25/25 valid scores and rationales; all rows complete; source text/formulas preserved; zero formula errors |
| `outputs/b3-evaluation-kit/rubric-calibration-practitioner-01-completed.xlsx` | PRACTITIONER-01 | `fd5cd4f0026d326f7362bac54b54006d3098175ace6cb771014168fe3975663b` | 25/25 valid scores and rationales; all rows complete; source text/formulas preserved; zero formula errors |
| `outputs/b3-evaluation-kit/rubric-calibration-practitioner-02-completed.xlsx` | PRACTITIONER-02 | `722f283659811d05cd123e1b128cdf65920e5a6f6dd0d14dae7eadeb3cb5ad0a` | 25/25 valid scores and rationales; all rows complete; source text/formulas preserved; zero formula errors |

Prepared reconciliation copy:

| File | Purpose | SHA-256 | Validation |
|---|---|---|---|
| `outputs/b3-evaluation-kit/rubric-calibration-reconciliation-populated.xlsx` | Three source-score columns populated by opaque item ID for human reconciliation | `75e864e2833a4b8c27b73ef731c6b390b1d4b87e36763f3ad4ab7c0f1233ce15` | 75/75 source scores present and matched to their locked returns; 25/25 rows unanimous; 25/25 match the draft intended score; human decision fields remain blank; zero formula errors |

Completed calibration and frozen rubric:

| File | Purpose | SHA-256 | Validation |
|---|---|---|---|
| `outputs/b3-evaluation-kit/rubric-calibration-reconciliation-completed.xlsx` | Frozen calibration decisions and rubric freeze record | `96f453642bcd0cce05b0d29dfc681f186754c8759038a53aa21ed00650d80bf6` | 25/25 rows complete and affirmed; no wording changes; final rubric hash recorded; `Ready to freeze`; zero formula errors; ZIP integrity passed |
| `research/revision_protocol/ratings/rubric-v1-final.md` | Frozen study-output scoring rubric | `dcf39358be89355afc013cdccf55888ca5a96b02862e763c5c39a9acb07b2355` | Protocol, Final status, and 2026-09-14 freeze date recorded; calibrated anchor wording retained |

Blinded study-output rating packets:

| File | Rater and coverage | SHA-256 | Validation |
|---|---|---|---|
| `outputs/b3-rating-packets/rating-packet-author.xlsx` | AUTHOR; all 486 observations | `05a67c677d85f8f9a0b003bbdda54f99af0dcadb17914520f05aa9061293e55c` | 401 scorable and 85 retained structural failures; blank rating inputs; randomized and blinded |
| `outputs/b3-rating-packets/rating-packet-practitioner-01.xlsx` | PRACTITIONER-01; 162 anchor observations | `a3f01a9bdb30601894de1349a79b513bc42aad5f5a31c582203f3b393539835b` | 132 scorable and 30 retained structural failures; blank rating inputs; rater-specific order and blind IDs |
| `outputs/b3-rating-packets/rating-packet-practitioner-02.xlsx` | PRACTITIONER-02; same 162 anchor observations | `67f6782550de35f68f750287982421df1e5ad711e1ea122eb66c209db5582ada` | 132 scorable and 30 retained structural failures; blank rating inputs; order and blind IDs differ from Practitioner 01 |
| `research/revision_protocol/blind/rating-item-map.jsonl` | Private 810-row identity map; do not distribute | `bb231db1935af724be78ad152d4b9a72084aa5479d1f0e9a7dffdb3a42c3ca9d` | Covers every issued blind item; all blind IDs unique |
| `research/revision_protocol/blind/rating-packet-manifest.json` | Machine-readable packet manifest | `4d99b6f9f3b1728b765b885c3b5b44f7b89f6c89d343442cb7c8256d07af7f52` | Counts, deterministic selection rules, hashes, and verification results recorded |

Completed study-output rating returns:

| File | Rater and coverage | SHA-256 | Validation |
|---|---|---|---|
| `outputs/b3-rating-packets/completed/rating-packet-author-completed.xlsx` | AUTHOR; 486 observations | `cafc66709a9f1ad18df779876f14993c1975031a9a48ac16efac02ca849124ec` | PASS; 401/401 scorable rows complete; 85 structural failures untouched |
| `outputs/b3-rating-packets/completed/rating-packet-practitioner-01-completed.xlsx` | PRACTITIONER-01; 162 anchor observations | `fbbc79e39c47c8999a2e756065603b4d7666103bcff235020f418adddbb2bfd2` | PASS; 132/132 scorable rows complete; 30 structural failures untouched |
| `outputs/b3-rating-packets/completed/rating-packet-practitioner-02-completed.xlsx` | PRACTITIONER-02; 162 anchor observations | `fab778e4a4f95f1a70860f8b043bfb264ceec25eb2a139f84a8aa60f5dae3dd2` | PASS; 132/132 scorable rows complete; 30 structural failures untouched |
| `research/revision_protocol/ratings/rating-return-validation.json` | Machine-readable independent return validation | `9bcb51666a3c97bff8f93014e231024386d8a4c711f6143e1ef86f4abb0eb44c` | All packet checks passed; no unblinding or cross-rater comparison performed; author chronology confirmation linked |

Controlled rating import and first-pass analysis:

| File | Purpose | SHA-256 | Status |
|---|---|---|---|
| `research/revision_analysis/ATSR-SREP-R2-v1.0/ratings-long.jsonl` | Locked 810-assignment long-form dataset | `85eb851bb61dcafeb85be453b10e8174f4811202dfbd22d9f6f7b8384d26ed6a` | 665 scorable rating records; 145 structural-failure assignments retained with null scores |
| `research/revision_analysis/ATSR-SREP-R2-v1.0/rating-import-manifest.json` | Import sources, hashes, and count checks | `7218643468e6cc4633589f206c756d60fe7b8cec1863b4f950ba237e13caea93` | PASS |
| `research/revision_analysis/ATSR-SREP-R2-v1.0/analysis-results.json` | Machine-readable preregistered analyses and labeled sensitivities | `4cec4dc52932ef9400ed6d8f5dde5ab718e9e5d6aebdee498ff68001cac3c6e6` | Deterministic rerun passed; manuscript interpretation pending |
| `research/revision_analysis/ATSR-SREP-R2-v1.0/analysis-report.md` | Narrative first-pass results | `af08853ef1d4e876f97a2fed050dec443650b330c3a8366c06a1dceda72441a4` | Review required before manuscript insertion |
| `research/revision_protocol/ratings/administrative-chronology-confirmation.md` | Author chronology statement | `68166306359bdcd2b110f371b7ac498246a3a7f3dfe97166921c50989146fd0b` | Author confirms records preceded distribution; private records not independently verified here |

All three independent workbooks contain the same 18 specification records and differ
only in the anonymized rater ID. They deliberately exclude the dataset's historical
`ground_truth_scope` field and all model, condition, provider, run, output, and score
information.

## Returned independent judgments

### Author

- Received and archived: 2026-09-14.
- Raw submitted TSV:
  `research/revision_protocol/ground-truth/submissions/author-ground-truth-2026-09-14.tsv`
- Raw TSV SHA-256:
  `f30edb2d528ee35a57ae4c7ff2334ff6819e961851e6f2a746828d8634c4a18a`
- Completed workbook: `outputs/b3-evaluation-kit/author-ground-truth-completed.xlsx`
- Completed workbook SHA-256:
  `47f1dbf7d515d8810fe0accf2238c82840cbb5e3891a030aadb9df7c2866dbe6`
- Validation: all 18 expected Spec IDs were present once, in frozen order; all ten
  required judgment fields were populated; all depth labels were valid; the saved
  workbook reopened with 18 `Complete` rows and zero formula errors.
- Descriptive depth distribution: 15 `HIGH`, 3 `MEDIUM`, 0 `LOW`. This remains an
  independent input; it was not compared with practitioner judgments before all
  three workbooks were returned and locked.

### Practitioner 01

- Received and archived: 2026-09-14.
- Raw submitted Markdown table:
  `research/revision_protocol/ground-truth/submissions/practitioner-01-ground-truth-2026-09-14.md`
- Raw Markdown SHA-256:
  `3617a0651f95d7b8dedc49d24962ddb650c1d32adf101b534696393ad159026d`
- Completed workbook:
  `outputs/b3-evaluation-kit/practitioner-01-ground-truth-completed.xlsx`
- Completed workbook SHA-256:
  `326d8ee30ca224c6411143b1eb5391ecf477693d36fbf473ad6c9e26f3d514d2`
- Import normalization removed Markdown table syntax, bold markers around Spec IDs,
  and inline code markers while preserving the submitted lexical content. The raw
  submission is retained unchanged.
- Validation: all 18 expected Spec IDs were present once, in frozen order; all ten
  required judgment fields were populated; all depth labels were valid; the saved
  workbook reopened with 18 `Complete` rows and zero formula errors.
- Descriptive depth distribution: 15 `HIGH`, 3 `MEDIUM`, 0 `LOW`. No cross-rater
  comparison or interpretation was performed at import; formal comparison remains
  deferred to adjudication.

### Practitioner 02

- Received and archived: 2026-09-14.
- Raw submitted Markdown table:
  `research/revision_protocol/ground-truth/submissions/practitioner-02-ground-truth-2026-09-14.md`
- Raw Markdown SHA-256:
  `a67ebec7061a09401f978b6cc0ea2d8a7d93b98cff721b48d0e4187fb18ffbcb`
- Completed workbook:
  `outputs/b3-evaluation-kit/practitioner-02-ground-truth-completed.xlsx`
- Completed workbook SHA-256:
  `049568d4b3eac38a637c5c25a9f139bc7e3c024944826ef7873a64781d25e26d`
- Import normalization removed Markdown table syntax and bold markers around Spec IDs
  while preserving the submitted lexical content. The raw submission is retained
  unchanged.
- Validation: all 18 expected Spec IDs were present once, in frozen order; all ten
  required judgment fields were populated; all depth labels were valid; the saved
  workbook reopened with 18 `Complete` rows and zero formula errors.
- Descriptive depth distribution: 11 `HIGH`, 7 `MEDIUM`, 0 `LOW`. Cross-rater
  comparison and consensus decisions remain deferred to the formal adjudication
  stage.

All three independent inputs are now immutable source records for adjudication. Do
not edit or overwrite the completed workbooks or raw submissions.

The prepared adjudication copy contains all three source judgments without altering
their wording. It shows exact agreement on 14 of 18 depth judgments; SPEC-03, SPEC-09,
SPEC-13, and SPEC-18 required depth discussion. All 108 scope rows agree on category
applicability, while 107 contain independently worded or differently granular atomic
elements. See `adjudication-preparation.md`.

The completed consensus reference was returned on 2026-09-14 and archived without
workbook re-export or content changes. All 18 depth rows and 108 scope rows have
`Complete` status. The consensus depth distribution is 15 `HIGH`, 3 `MEDIUM`, and 0
`LOW`; evidence-basis classifications are 32 `Explicit`, 36 `Implicit`, and 40
`Mixed`. All decision rows use the coded adjudicator entry `QA1/QA2/QA3` and decision
date 2026-09-14. Source columns match the prepared adjudication workbook exactly.

## Supporting documents

- `README.md`: ground-truth procedure and completion gate.
- `participant-consent-template.md`: prospective information and consent record.
- `rater-profile-template.md`: coded, non-identifying practitioner-qualification
  record.
- `../ratings/rubric-v1-final.md`: frozen, calibrated five-dimension 1–5 scoring
  rubric for study outputs.
- `../ratings/calibration-examples-v1-draft.md`: non-study examples for aligning the
  score anchors before the freeze.
- `../ratings/calibration-procedure.md`: independent distribution, reconciliation,
  affirmation, and final-rubric freeze gate.
- `../ratings/rating-packet-procedure.md`: packet selection, blinding, distribution,
  return validation, and score-import controls.
- `build_ground_truth_workbooks.mjs`: reproducible workbook builder.
- `import_author_ground_truth.mjs`: validates, archives, and imports returned author
  or practitioner judgments from tab-separated or Markdown-table submissions.
- `adjudication-preparation.md`: prepared-workbook hash, disagreement map, and human
  adjudication record and completion controls.

## Source controls

- Specification source: `supplementary/data/specifications.json`
- Specification SHA-256:
  `48d94cce163cf21efa712939bd4334b0a89260434aafe0d83a00cbd2dd3856f0`
- The builder refuses to run if the source hash or expected 18-record count changes.

## Verification performed

- All four XLSX archives passed ZIP integrity checks.
- Every worksheet was rendered and visually inspected.
- Formula scans found no spreadsheet error values.
- A saved rater workbook was reopened and a representative row was completed in
  memory; the row status changed to `Complete`, the workbook count changed to 1, and
  rows remaining changed to 17.
- The saved adjudication workbook was reopened and representative depth and scope rows
  were completed in memory; both status fields and both summary counters changed to 1.
- Exported XLSX XML contains the intended LOW/MEDIUM/HIGH validation lists.
- A content scan found no model identifiers, condition identifiers, or historical
  ground-truth content in the four workbooks.
- The completed consensus reference has 18 complete depth rows and 108 complete scope
  rows, valid consensus depth labels, preserved status formulas, and zero formula-error
  matches. Its source columns match the prepared adjudication copy exactly.
- The completed consensus file passed ZIP integrity testing, and its archived SHA-256
  matches the downloaded source byte-for-byte.
- The four neutral calibration workbooks passed reopen, formula-error, formula-state,
  ZIP-integrity, and visual checks. The three independent copies have the same 25
  opaque item IDs in different orders, contain no intended scores, and remain blank
  for human scoring.
- The three study-output rating packets passed reopen, formula-state, ZIP-integrity,
  identifier-leak, and visual checks. Their 810 blind IDs are unique; practitioner
  packets contain the same deterministic anchor set in different orders and with
  different blind IDs. Structural failures remain unscored.
- All three completed returns passed identity, immutable-source, score-range,
  rationale, total, status-formula, structural-failure, formula-error, and XLSX
  integrity checks. Received and archived hashes match byte-for-byte. No score
  unblinding or cross-rater comparison occurred during validation.

## Ethics-policy basis checked on 2026-09-14

Scientific Reports states that human-participant research must identify the applicable
ethics committee arrangement, confirm compliance with relevant guidelines, and state
that informed consent was obtained. It may request consent documentation. Its
submission guidance also requires removal of participant names and personally
identifying information from manuscript and supplementary materials.

- https://www.nature.com/srep/journal-policies/editorial-policies
- https://www.nature.com/srep/author-instructions/submission-guidelines

The consent form does not itself determine whether formal ethics approval is required.
The study must retain the journal's written direction about the author's independent-
researcher arrangement.
