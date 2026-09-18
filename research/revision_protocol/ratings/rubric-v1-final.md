# Expanded output-scoring rubric

**Protocol:** ATSR-SREP-R2-v1.0  
**Status:** Final and frozen  
**Freeze date:** 2026-09-14  
**Calibration outcome:** All three raters independently assigned the intended score
to all 25 neutral examples, then jointly affirmed all 25 decisions. No wording changes
were required.  
**Scale:** Five integer scores from 1 to 5. Half-points are not permitted.

## General scoring rules

Score the recommendation shown, using the frozen consensus ground truth and the
feature specification. Do not infer model, condition, provider, or run identity. Judge
each dimension separately; a weakness may affect more than one dimension only when it
genuinely meets each dimension's definition.

- Compare coverage with the consensus essential elements. Extra useful content may
  improve a score, but volume alone does not.
- Do not reward confident wording, formatting, or item count by itself.
- Do not penalize Specificity merely because an essential test is absent; absence is
  primarily a Completeness issue. If an included test is too vague to execute, that is
  a Specificity issue.
- An element requiring implicit domain knowledge counts as essential only when the
  frozen consensus reference marks it essential and records the inferential link.
- Unsupported assumptions or invented system behavior do not earn credit. They may
  reduce Specificity, Integration Awareness, or Clarification Flag Quality when they
  make the recommendation misleading.
- Use the lower score when a recommendation straddles two anchors and the higher
  anchor's requirements are not fully met. Explain all scores of 1, 2, or 5 and any
  judgment that depends on implicit domain knowledge.

## 1. Completeness

Does the recommendation cover the test types and essential test concerns warranted by
the change?

| Score | Anchor |
|---|---|
| 5 | Covers every critical and important consensus element across all relevant test types. No material gap remains. |
| 4 | Covers every critical element and nearly all important elements. At most one minor or narrowly bounded gap remains. |
| 3 | Covers the core changed behavior and the main test type, but misses one important secondary area or several minor elements. The plan remains usable with supplementation. |
| 2 | Misses a critical element or multiple important areas. The plan would create a meaningful coverage risk without substantial additions. |
| 1 | Misses the core changed behavior or most relevant test types. The proposed scope is fundamentally inadequate or largely unrelated. |

Implicit elements are treated exactly like explicit elements after they are frozen in
the consensus reference. Their omission affects Completeness, not Specificity, unless
the output also includes a vague version of the same test.

## 2. Specificity

Are the tests that are present concrete and actionable for a QA practitioner?

| Score | Anchor |
|---|---|
| 5 | Nearly every material item identifies a concrete behavior or scenario, relevant context or boundary, and an observable expected result. A practitioner could translate the scope into tests with minimal interpretation. |
| 4 | The recommendation is actionable overall. Most material items contain concrete scenarios and outcomes, with only minor vagueness or a few generic supporting items. |
| 3 | The core items are understandable, but concrete inputs, boundaries, system states, or expected results are inconsistently supplied. Moderate interpretation is needed. |
| 2 | Most items are category labels or generic directives such as “test edge cases” or “verify integration.” Significant interpretation is needed before execution. |
| 1 | The content is predominantly boilerplate, tautological, internally incoherent, or too vague to guide test design. |

Judge the quality of included content. Do not lower this score solely because another
test is missing; score that omission under Completeness.

## 3. Risk Calibration

Is the recommended LOW, MEDIUM, or HIGH coverage depth appropriate, and does the
justification reflect the change's risk and breadth?

| Score | Anchor |
|---|---|
| 5 | The depth exactly matches consensus and the justification accurately connects change type, impact, breadth, and material failure risks. |
| 4 | The depth exactly matches consensus and the justification is sound but incomplete or somewhat generic. |
| 3 | The depth differs by one level but is reasonably defensible from ambiguity recorded in the consensus, or the depth matches but the justification is materially weak or partly contradictory. |
| 2 | The depth differs by one level without a sound case, or it matches only superficially while the justification materially misreads the risk. |
| 1 | The depth differs by two levels, is absent/invalid, or is plainly incompatible with the scale and the change's risk. |

Record exact depth agreement and ordinal distance separately from this rubric score.
The rubric score includes justification quality and must not replace the categorical
depth outcome.

## 4. Integration Awareness

Does the recommendation identify and test relevant cross-system, component, data-flow,
and downstream dependencies?

| Score | Anchor |
|---|---|
| 5 | Identifies every critical and important consensus integration boundary and states how behavior or data should be checked across each one. If no external integration is relevant, it correctly limits the scope and addresses the material internal boundary. |
| 4 | Covers every critical boundary and most important dependencies, with at most one minor touchpoint or consequence omitted. |
| 3 | Covers the main end-to-end path but misses an important secondary dependency, failure path, or downstream effect. |
| 2 | Mentions integration only at a surface level, tests one side of the boundary, or misses a critical dependency. |
| 1 | Integration considerations are absent, substantially incorrect, or replaced by invented systems that obscure the actual boundary. |

Do not require an external system when the consensus establishes that none is
relevant. In that case, accurate restraint can receive a high score.

## 5. Clarification Flag Quality

Do the questions identify material unknowns whose answers could change the test scope,
depth, environment, data, or expected result?

| Score | Anchor |
|---|---|
| 5 | Captures all material consensus ambiguities with targeted, actionable questions and no distracting boilerplate. If no material ambiguity exists, explicitly or appropriately supplies no flags. |
| 4 | Captures the most important ambiguities. One minor question is missing, vague, or low-value. |
| 3 | Includes at least one useful question but mixes it with generic items, or misses another important ambiguity. Answers would improve only part of the plan. |
| 2 | Questions are mostly generic, already answered by the specification, or low-impact; or a material ambiguity is left unflagged. |
| 1 | Provides no useful question despite a critical ambiguity, or the flags are wholly irrelevant, fabricated, or boilerplate. |

Absence of flags is not automatically poor. Compare it with the frozen consensus
clarification needs.

## Calibration and freeze record

The three raters calibrated only on the neutral examples outside the 486 study
outputs. All 25 independent scores were unanimous and matched the draft intended
anchors. On 2026-09-14, the raters jointly affirmed all decisions and confirmed that
no wording changes were required. This file is the frozen rubric for study-output
scoring. Any later change requires a versioned amendment and a new hash.
