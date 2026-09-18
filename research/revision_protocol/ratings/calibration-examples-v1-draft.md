# Neutral rubric-calibration examples

**Protocol:** ATSR-SREP-R2-v1.0  
**Status:** Draft. These examples are not part of the 18-specification study dataset
and are not among the 486 generated outputs.

Use these examples only to align interpretation of the rubric before study-output
scoring. Each rater should first assign scores independently, then compare the scores
with the intended anchors below. Discuss disagreements and change the final rubric or
examples only before the rubric freeze.

## Neutral specification

A document portal is increasing its maximum upload size from 10 MB to 25 MB. It accepts
PDF and DOCX files. Uploaded files pass through antivirus scanning and are then stored
in a cloud object store. The user sees a success or failure message. No acceptance
criteria specify boundary behavior, timeouts, or what should happen when antivirus
scanning is unavailable.

Assume the calibration panel agrees that MEDIUM depth is appropriate. Essential scope
includes the 10/25 MB boundaries, both file types, unchanged rejection above the
limit, upload success/failure messaging, antivirus handoff and failure behavior,
storage persistence, regression below 10 MB, and clarification of timeout and scanner-
unavailable behavior.

## Completeness examples

| Intended score | Example and rationale |
|---|---|
| 5 | Covers both formats, all size boundaries, success/failure messages, scanner and storage paths, failure handling, regression below 10 MB, and both material clarification needs. No essential gap remains. |
| 4 | Covers all critical paths but omits one minor regression check, such as a representative file well below 10 MB. |
| 3 | Covers valid uploads and the 25 MB boundary but omits scanner-unavailable behavior and one secondary regression area. The core is usable with supplementation. |
| 2 | Tests only successful 25 MB PDF upload and a file above 25 MB. Critical DOCX and antivirus/storage behavior are absent. |
| 1 | Says only to “test document upload thoroughly” without identifying the changed limit or the core success and rejection behaviors. |

## Specificity examples

| Intended score | Example and rationale |
|---|---|
| 5 | “Upload 24.99 MB, 25.00 MB, and 25.01 MB PDF and DOCX files; verify the first two reach scanning and storage and the last is rejected with the documented size-limit message.” Concrete data, states, boundaries, and outcomes are present. |
| 4 | Gives the exact boundary values, both formats, and expected accept/reject results but does not specify how storage success will be observed. |
| 3 | Says to test just below, at, and above 25 MB for both formats and verify correct behavior. The scenarios are clear, but expected messages and observable downstream outcomes need interpretation. |
| 2 | Says to test “valid, invalid, and edge-case files” and “verify integrations.” Substantial interpretation is required. |
| 1 | Says only “perform functional, regression, and integration testing.” It is a category template rather than an actionable scope. |

## Risk Calibration examples

| Intended score | Example and rationale |
|---|---|
| 5 | Recommends MEDIUM and explains that a bounded configuration change affects validation plus two downstream services and failure handling. |
| 4 | Recommends MEDIUM with a sound but generic explanation that the change affects upload validation and connected services. |
| 3 | Recommends HIGH because of malware and storage risk. The one-level increase is defensible, but broader regression is not clearly warranted. |
| 2 | Recommends LOW because “only one number changed,” ignoring the scanner and storage path. The one-level decrease lacks a sound risk case. |
| 1 | Recommends no depth or an invalid value, or treats the change as requiring no testing despite its downstream path. |

## Integration Awareness examples

| Intended score | Example and rationale |
|---|---|
| 5 | Tests portal-to-scanner handoff, scanner result return, portal-to-object-store persistence, failures at each boundary, and the user-visible final state. |
| 4 | Covers scanner and object-store boundaries and user-visible results but omits one secondary timeout or retry consequence. |
| 3 | Covers the normal scanner-to-storage path but omits scanner outage/failure propagation. |
| 2 | Says only to verify that “the upload integrates with backend services,” without testing either side of a concrete boundary. |
| 1 | Omits the scanner and storage path or invents an unrelated payment service as the primary integration. |

## Clarification Flag Quality examples

| Intended score | Example and rationale |
|---|---|
| 5 | Asks for the exact timeout/retry behavior and the required user/system outcome when antivirus scanning is unavailable. Both answers materially change testing. |
| 4 | Asks both material questions, but one is worded broadly and needs a small follow-up. |
| 3 | Asks what happens when scanning fails but omits timeout/retry behavior and adds one low-value generic question. |
| 2 | Asks who owns the feature and whether documentation exists. These questions add little to test design while material ambiguity remains. |
| 1 | Supplies no flags despite the unresolved scanner failure behavior, or asks wholly irrelevant questions. |

## Calibration record

Record the meeting date, participants' coded IDs, disputed anchors, agreed wording
changes, and final rubric filename in a separate calibration log. Do not include any
of the 486 study outputs in that discussion.

