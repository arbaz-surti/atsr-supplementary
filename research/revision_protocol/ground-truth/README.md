# B3 ground-truth stage

Protocol: `ATSR-SREP-R2-v1.0`

This directory holds the human-evaluation materials created before model-output
scoring. The author and two additional QA practitioners must complete the same
18-specification exercise independently.

## Required sequence

1. Assign anonymized IDs: `AUTHOR`, `PRACTITIONER-01`, and `PRACTITIONER-02`.
2. Obtain signed or email-confirmed consent from both practitioners before any work.
   Collect a de-identified qualification profile for each practitioner.
3. Give each person only their matching ground-truth workbook from
   `outputs/b3-evaluation-kit/` and this study's specifications. Do not provide model
   outputs, the historical author ground truth, or another participant's judgments.
4. Each person completes all 18 rows in the `Ground Truth` sheet.
5. Save returned files under `private-records/` while they contain names, signatures,
   email headers, or other identifiers. Store de-identified workbook copies under
   `individual/` when that directory is created.
6. Copy the three de-identified judgments into the consensus-adjudication workbook.
7. Discuss disagreements. Record the consensus decision and a short reason without
   overwriting any original judgment.
8. Freeze and hash the adjudicated consensus and the final rubric before creating
   or opening blinded model-output rating packets.

## Atomic-item convention

For each scope category, enter semicolon-separated, independently scorable elements.
Describe what must be covered, not a full step-by-step test case. Use `NONE` only when
the category is genuinely irrelevant. Do not leave a completed row ambiguous.

When an essential element depends on professional knowledge not stated directly in
the specification, include it and explain the inferential link in `Implicit domain
knowledge`. Do not add a requirement merely because it would be useful in an ideal
system.

## Completion gate

A workbook is complete only when every specification has:

- one LOW, MEDIUM, or HIGH depth judgment;
- entries or `NONE` for all six essential-scope/clarification fields;
- a brief depth rationale; and
- a completion status of `Complete`.

The workbook is an input instrument, not the frozen consensus reference. No model
condition, model family, provider, or run identity appears in these materials.
