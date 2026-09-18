# ATSR Expanded Evaluation Protocol

**Protocol ID:** ATSR-SREP-R2-v1.0  
**Frozen:** 2026-09-13  
**Purpose:** Scientific Reports reviewer revision  
**Status:** Design frozen; no revision experiment outputs generated yet

## 1. Objective

The expanded evaluation tests whether ATSR offers measurable value beyond both an
unstructured prompt and a credible generic structured QA prompt, whether condition
differences persist across model families, how stable outputs are across repeated
runs, and whether conclusions remain similar under blinded independent evaluation.

The protocol addresses four limitations of the reviewed experiment: a weak baseline,
one model, one run, and predominantly author-conducted evaluation.

## 2. Research questions

- **RQ1 — Stronger-baseline comparison:** Does ATSR improve practitioner-rated test
  scope quality relative to a generic structured QA prompt?
- **RQ2 — Naive-baseline comparison:** How do ATSR and the generic structured QA
  prompt compare with the original naive prompt?
- **RQ3 — Model robustness:** Are condition differences directionally consistent
  across OpenAI, Anthropic, and open-weight Meta model families?
- **RQ4 — Run stability:** How much do assigned depth, structural validity, and
  practitioner-rated quality vary across three independent runs?
- **RQ5 — Evaluator robustness:** How consistent are ratings among the author and two
  additional QA practitioners when model and condition identity are hidden?

The primary comparison is ATSR versus the generic structured QA condition. All other
contrasts are secondary and will be identified as such.

## 3. Fixed dataset

The experiment retains all 18 specifications in
`supplementary/data/specifications.json`, SHA-256
`48d94cce163cf21efa712939bd4334b0a89260434aafe0d83a00cbd2dd3856f0`.

No specifications will be added for this revision. Adding retrospectively authored
cross-domain synthetic cases would change the construct and would not provide genuine
external validation. Credibility will instead be strengthened through complete
multi-model, repeated-run, and independent-rater coverage of the existing paired
dataset. The manuscript will explicitly retain the small, single-domain dataset as a
limitation and frame generalizability as preliminary.

Ground-truth fields are never included in model messages.

## 4. Prompt conditions

All prompts and the shared user-message builder are frozen in `prompts.py`.

1. **Naive:** reproduces the original minimal QA role and common JSON schema. It
   contains no reasoning process or calibration guidance.
2. **Generic Structured QA (GSQ):** a credible one-pass comparator using generally
   applicable risk-based QA planning guidance. It requests direct, adjacent,
   regression, integration, exploratory, depth, effort, and missing-information
   analysis. It does not contain ATSR's restaurant/POS domain framing or its
   deterministic change-type-to-depth calibration taxonomy.
3. **ATSR:** the reviewed framework reasoning instructions, including enterprise/POS framing,
   eight reasoning dimensions, material clarification rules, specificity guidance,
   and LOW/MEDIUM/HIGH change-type calibration. Its historical verbose schema block
   is replaced by the same concise schema block used in the comparator conditions.

The same specification fields, user-message builder, byte-identical output schema,
API settings, and JSON-only requirement apply to all conditions. The complete
historical ATSR prompt is also archived in `prompts.py` and checked against the
reviewed implementation, but it is not used for new production calls. Standardizing
the schema prevents descriptive field wording from acting as a condition-level
confound.

## 5. Models and provider control

Three model families will be evaluated through OpenRouter:

| Family | OpenRouter model ID | Pinned provider | Reason |
|---|---|---|---|
| OpenAI | `openai/gpt-4o-2024-11-20` | OpenAI | Versioned GPT-4o snapshot closest to the reviewed model family |
| Anthropic | `anthropic/claude-sonnet-4.6` | Anthropic | Independent proprietary model family |
| Meta | `meta-llama/llama-3.3-70b-instruct` | DeepInfra, FP8 | Open-weight instruction model served through a fixed endpoint |

Availability and supported parameters were checked through OpenRouter's model and
endpoint APIs on 2026-09-13. Provider fallback will be disabled and required
parameters enforced. The returned provider, model identifier, response identifier,
usage, latency, and timestamp will be stored for every attempt.

The unversioned historical `openai/gpt-4o` outputs remain part of the reviewed-study
record but will not be mixed into the confirmatory expanded comparison. All three
conditions will be regenerated contemporaneously on every included model.

## 6. Generation design

- Full factorial design: 18 specifications × 3 conditions × 3 models × 3 runs.
- Expected valid or retained failed outputs: **486**.
- Temperature: 0.2.
- Maximum output: 2,000 tokens.
- `top_p`: provider default, omitted.
- Seed: omitted because it is not supported consistently across all pinned providers.
- Response format: JSON object.
- No tools, retrieval, web access, conversation history, or cross-specification
  context.

The 486-call queue will be randomized once using seed `20260913`. Each output will
carry immutable identifiers for protocol, model, provider, condition, specification,
run, request attempt, and prompt hashes.

### Failure handling

- Transport, timeout, and rate-limit failures: up to three attempts with recorded
  exponential backoff.
- Syntactically invalid JSON: retain the original attempt and permit one explicitly
  labeled repair retry using the same messages and parameters.
- Schema-invalid content: retain and flag; do not manually repair content.
- Persistent failures: retain as missing/invalid observations. Do not selectively
  regenerate until a desirable response appears.

Every attempt, including failures and retries, is archived.

## 7. Ground truth and rubric preparation

Before raters see any generated output:

1. The author and two additional QA practitioners independently review all 18
   specifications.
2. Each records a coverage-depth judgment and the essential functional, smoke,
   regression, integration, exploratory, and clarification elements.
3. Disagreements are discussed and an adjudicated consensus reference is frozen,
   while all original judgments remain archived.
4. The rubric is expanded to contain explicit anchors for scores 1 through 5 on every
   dimension, including treatment of information requiring implicit domain knowledge.
5. The consensus reference and rubric are hashed before output scoring begins.

The original author-established ground truth remains available for a sensitivity
analysis; it is not silently overwritten.

Each additional participant must provide informed consent before participating.
Only anonymized rater identifiers and permitted evaluation data will be released.

## 8. Blinded rating design

The author will score all 486 outputs in randomized order to measure run-level
variation. Output identifiers shown during scoring will not disclose model, provider,
condition, or run.

Two additional QA practitioners will each score 162 outputs: one preregistered anchor
run for every specification × condition × model cell. The anchor is selected before
outputs are inspected using:

```text
1 + (first 8 hex digits of SHA-256(
  model_id | condition | spec_id | 20260913
) interpreted as an integer modulo 3)
```

Thus the independent subset covers all 18 specifications, all three prompt
conditions, and all three model families without selecting the best-looking run.

Raters receive outputs in separately randomized orders, do not see one another's
ratings, and do not receive model or condition mappings until ratings are locked.
Formatting will be normalized without changing substantive content. Any normalization
operation will be deterministic, logged, and applied to every condition.

The earlier six-specification rater exercise remains historical and will not be pooled
with the new blinded ratings because its selection, instructions, and exposure controls
differ.

## 9. Outcomes

### Primary outcome

Per-output total rubric score (5–25), with the primary ATSR-versus-GSQ comparison
based on the two independent raters' anchor-run scores. Rater scores will be averaged
for the primary analysis while rater-specific results remain reported.

### Secondary outcomes

- Five dimension scores (1–5).
- Exact coverage-depth agreement with consensus ground truth.
- Distance from consensus depth (0, 1, or 2 levels).
- JSON and schema validity rates.
- Clarification-flag count and test-item counts, reported descriptively rather than as
  quality proxies.
- Author-scored total and dimension results across all three runs.
- Within-cell run variability and unanimous depth rate.
- Sensitivity against the original author ground truth and author ratings.

Effort-estimate accuracy is not claimed because the dataset contains no observed
testing-effort outcome.

## 10. Statistical analysis

The specification is the principal independent sampling unit. Dimensions, runs,
models, and raters are repeated measurements—not independent sample-size inflation.

### Confirmatory analysis

1. Average the two independent anchor-run ratings for each output.
2. For each specification and condition, average across the three models.
3. Compare ATSR with GSQ using the 18 paired specification-level means.
4. Report the paired mean and median difference, a specification-clustered bootstrap
   95% confidence interval, Wilcoxon signed-rank test, and matched-pairs
   rank-biserial effect size.

The threshold is two-sided α = 0.05. Statistical significance will not substitute for
effect magnitude or uncertainty.

### Secondary analyses

- ATSR versus naive and GSQ versus naive use the same paired procedure.
- The three overall condition contrasts use Holm correction.
- Model-specific condition contrasts are exploratory, report confidence intervals and
  Holm-adjusted p-values, and are not used to claim universal model robustness.
- A mixed-effects sensitivity model will use total score as the outcome, condition,
  model, and their interaction as fixed effects, and specification and rater as random
  intercepts. Its assumptions and convergence diagnostics will be reported.
- Dimension-specific analyses are exploratory ordinal outcomes; report distributions,
  paired effects, and multiplicity-adjusted uncertainty without treating 90 dimension
  cells as independent observations.
- Run stability is summarized by within-cell standard deviation/range of author total
  scores, exact depth unanimity, and pairwise depth agreement across the three runs.
- Inter-rater reliability on anchor outputs is reported using two-way random-effects
  absolute-agreement ICC for total scores and ordinal Krippendorff alpha by dimension,
  with bootstrap confidence intervals where feasible.

No post-hoc exclusion of specifications, raters, models, conditions, or runs is
permitted. Any sensitivity analysis must retain a clear label and the primary analysis.

## 11. Workload and cost

- Generation: 486 calls.
- Author rating: 486 outputs × five dimensions.
- Independent rating: 162 outputs per rater × two raters.
- Consensus ground truth: 18 specifications × three initial judges.

Existing output lengths average roughly 500–550 tokens. Using a conservative 1,200
input and 1,000 output tokens per call and OpenRouter prices observed on 2026-09-13,
estimated generation cost is approximately USD 5.20 before retries. Actual usage and
cost will be recorded from API response metadata. Human-rating time, not API cost, is
the dominant resource requirement.

## 12. Reproducibility and directory contract

Planned artifacts:

```text
research/revision_protocol/
  protocol.md
  protocol.json
  prompts.py
  prompt-manifest.json
  model-availability-2026-09-13.json
  ground-truth/
  raw/
  normalized/
  blind/
  ratings/
  analysis/
```

Raw API responses are immutable. Derived files must identify their source hashes and
generating script. Secrets must never be written into request logs or the replication
package.

## 13. Interpretation boundaries fixed in advance

- This design can test robustness across three named model configurations, not all
  LLMs.
- Retaining one domain and 18 specifications means cross-domain generalizability
  remains untested.
- The GSQ comparison tests ATSR against one credible structured alternative; it does
  not prove that ATSR is optimal among all prompt designs.
- Human rubric scores measure practitioner-assessed recommendation quality, not defect
  prevention, effort saved, or production outcomes.
- Hosted model and endpoint behavior is time-dependent even when identifiers and
  providers are recorded.
- Null or unfavorable results will be reported and claims revised accordingly.

## 14. Amendment rule

After the first production API call, this protocol and its prompt/config files must
not be edited in place. Any change requires:

1. a new protocol version;
2. a dated amendment explaining the reason;
3. new hashes; and
4. regeneration of every condition affected by the change.
