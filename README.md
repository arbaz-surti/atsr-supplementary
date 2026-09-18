# ATSR Supplementary Materials and Reproducibility Archive

Supplementary materials, code, data, and analysis outputs for:

> **AI-Assisted Test Scope Recommendation for Manual QA: A Framework and Evaluation**
> Arbaz Surti (independent researcher). Manuscript under revision at *Scientific Reports*
> (Springer Nature), 2026.

**Archive version:** 2.0.0 (2026-09-18) — expanded evaluation under the frozen protocol
`ATSR-SREP-R2-v1.0`. Version 1.0.0 (March 2026) covered the original single-model,
single-run evaluation; its files are retained unchanged under `original-evaluation/`
(see `CHANGELOG.md`).

**Persistent identifier:** Zenodo DOI `10.5281/zenodo.22839182` for version 2.0.0
(https://doi.org/10.5281/zenodo.22839182); concept DOI `10.5281/zenodo.22839181` resolves to the
latest version. The GitHub repository (`https://github.com/arbaz-surti/atsr-supplementary`)
is the development copy; the Zenodo record is the citable, versioned snapshot.

---

## 1. What the archive contains

The expanded evaluation compared three prompt conditions (`naive`,
`generic_structured_qa` = GSQ, `atsr`) across three model families
(`openai/gpt-4o-2024-11-20`, `anthropic/claude-sonnet-4.6`,
`meta-llama/llama-3.3-70b-instruct`, all via OpenRouter, temperature 0.2) with three
runs per model × condition × specification on the frozen 18-specification dataset:
486 generation cells, 401 valid schema-conforming outputs, and 85 retained invalid-JSON
outputs. Outputs were rated by the author (all 486) and by two independent QA
practitioners (one pre-registered anchor run per cell, 162 each) on a five-dimension
1–5 rubric, blind to model and condition, after a three-person consensus ground truth
and a rubric calibration exercise. Every number in the manuscript's Results is produced
by `research/analyze_operative_ratings.py` from the files in this archive.

Directory layout preserves the project-relative paths recorded in the frozen protocol
and its lock file (`research/revision_protocol/protocol-lock.json`), so every script
runs unmodified from the archive root:

| Path | Contents |
|---|---|
| `supplementary/data/specifications.json` | The frozen 18-specification dataset (SHA-256 `48d94cce…3856f0`, recorded in `protocol.json` and `protocol-lock.json`). `specifications.md` is the human-readable rendering. Specifications are synthetic/anonymised derivations of enterprise restaurant-technology QA tickets; company, brand, and vendor names are replaced. |
| `atsr_tool.py`, `baseline_tool.py` | The historical (v1) ATSR and naïve-baseline implementations. Kept at the root because `validate_protocol.py` imports them to verify that the frozen prompts preserve the historical system prompts byte-for-byte. |
| `research/revision_protocol/` | The frozen protocol (`protocol.md`, `protocol.json`), the lock file with SHA-256 hashes of every frozen input, the three condition prompts and shared user-message builder (`prompts.py`, `prompt-manifest.json`), the model-availability check of 2026-09-13, and `validate_protocol.py`. |
| `research/revision_protocol/ground-truth/` | Ground-truth procedure: kit manifest with hashes of every workbook issued and returned, adjudication preparation notes, participant consent and rater-profile *templates*, the workbook build/import scripts, and the three raw independent ground-truth submissions (`submissions/`, de-identified). |
| `research/revision_protocol/ratings/` | The rubric (`rubric-v1-draft.md` → `rubric-v1-final.md`, frozen 2026-09-14), the calibration procedure and examples, the blinded rating-packet procedure, the rating-return validation record, and the author's chronology confirmation. |
| `research/revision_protocol/blind/` | `rating-item-map.jsonl` (the 810-row blind-item → output identity map, withheld from raters during the study and released here for unblinding) and `rating-packet-manifest.json`. |
| `outputs/b3-evaluation-kit/` | Ground-truth and rubric-calibration workbooks: blank kits as issued, completed returns from the author and both practitioners, and the completed three-person consensus adjudication and calibration reconciliation workbooks. |
| `outputs/b3-rating-packets/` | The three blinded output-rating packets as issued (blank) and the first-pass completed returns (superseded; see §3). |
| `research/revision_outputs/ATSR-SREP-R2-v1.0/` | Generation records: `queue-manifest.json` (deterministic randomised queue, frozen-input hashes), `attempts.jsonl` (every request payload and response body for all 584 attempts, including transport failures and invalid-JSON repair attempts; API keys are never written), `outputs.jsonl` (486 terminal outputs incl. invalid ones), `run-summary.json`, `generation-audit.json`. |
| `research/revision_analysis/ATSR-SREP-R2-v1.0-renewed-ratings-2026-09-17/` | `ratings-extracted.csv`: the operative rating returns (810 assignments), extracted from the raters' HTML exports; `extraction-manifest.json` records the SHA-256 of each source export and the extraction checks. |
| `research/revision_analysis/ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18/` | **The operative analysis** reported in the manuscript: `ratings-long.jsonl` and `ratings-unblinded.csv` (665 scorable ratings + 145 retained structural failures, unblinded), `analysis-results.json` (all statistics), `analysis-report.md`, `analysis-manifest.json` (input/output hashes and the exact command). |
| `research/revision_analysis/ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18-results-checks/` | `results-checks.json`: secondary cross-checks used in the Results section (naïve contrasts, structural-failure finish reasons, post-hoc depth analyses). |
| `research/revision_analysis/ATSR-SREP-R2-v1.0/` | The **superseded first-pass** rating analysis (see §3). Retained as an audit trail; also required as an input by `analyze_operative_ratings.py` for blind-item metadata and one carried-over diagnostic. |
| `research/*.py` | All executable code for the expanded evaluation (§2). |
| `submission/figures/` | Manuscript Figures 2 and 3 as generated TikZ/pgfplots sources and rendered PDFs, plus `figure-data.json` (the exact values plotted, with source hashes). |
| `original-evaluation/` | Version 1.0.0 material: the March 2026 single-model outputs, rubric scores, and six-specification inter-rater sheet. Superseded by the expanded evaluation; retained for the record and for the "earlier version" comparisons in the manuscript. |

### Not included (and why)

- **Participant identities, consent records, and the identity-to-code mapping.** Held
  privately by the author under the consent terms; raters appear only as `AUTHOR`,
  `PRACTITIONER-01`, `PRACTITIONER-02`. Spreadsheet metadata has been checked for
  author fields and e-mail addresses (none present).
- **API credentials.** The runner reads `OPENROUTER_API_KEY` from a local `.env` file
  that is git-ignored and never written into any record.
- **The raters' original HTML rating exports.** Their SHA-256 hashes are recorded in
  `extraction-manifest.json`; the archived form of the same data is
  `ratings-extracted.csv`.
- **Later ATSR development work.** A separate, in-progress refinement effort that
  post-dates the frozen protocol is not part of this manuscript and is not included;
  nothing in this archive was changed by it.

---

## 2. Reproducing the reported results

Requirements: Python 3.14 (3.12+ should work) and the pinned packages in
`requirements.txt`. No API access is needed to reproduce the analysis; only re-running
generation (§2.5) calls OpenRouter.

```bash
git clone https://github.com/arbaz-surti/atsr-supplementary.git   # or unzip the Zenodo archive
cd atsr-supplementary
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONDONTWRITEBYTECODE=1
```

### 2.1 Verify archive integrity

```bash
python3 verify_manifest.py            # every file in MANIFEST-SHA256.txt matches
python3 research/revision_protocol/validate_protocol.py
```

`validate_protocol.py` re-hashes every frozen input against `protocol-lock.json`,
checks the dataset, the factorial design (3 × 3 × 3 × 18 = 486), that the frozen
prompts preserve the historical system prompts, and that all three conditions share a
byte-identical output-schema suffix.

### 2.2 Verify the generation archive

```bash
python3 research/audit_revision_generation.py
```

Recomputes the queue/attempt/terminal counts, terminal statuses by condition and
model, provider consistency, token usage and cost, and the SHA-256 of the three
generation files, and rewrites `generation-audit.json` (identical to the archived
copy; `verify_manifest.py` checks its recorded hashes). Expected: `PASS`, 486 queue
items, 584 attempts, 401 valid / 85 invalid-JSON terminal outputs.

### 2.3 Reproduce the operative analysis (all manuscript statistics)

```bash
L=research/revision_analysis
python3 research/analyze_operative_ratings.py \
  --ratings              $L/ATSR-SREP-R2-v1.0-renewed-ratings-2026-09-17/ratings-extracted.csv \
  --locked-long          $L/ATSR-SREP-R2-v1.0/ratings-long.jsonl \
  --locked-results       $L/ATSR-SREP-R2-v1.0/analysis-results.json \
  --extraction-manifest  $L/ATSR-SREP-R2-v1.0-renewed-ratings-2026-09-17/extraction-manifest.json \
  --output-dir           /tmp/atsr-repro
```

Then compare with the archived outputs:

```bash
for f in analysis-results.json analysis-report.md ratings-long.jsonl ratings-unblinded.csv; do
  cmp -s $L/ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18/$f /tmp/atsr-repro/$f && echo "MATCH $f" || echo "DIFF $f"
done
```

All four files reproduce byte-for-byte (verified 2026-09-18 from a clean copy with a
fresh virtual environment). The bootstrap uses seed 20260913. Headline values:
ATSR − GSQ = +1.49/25 (specification-bootstrap 95% CI 0.84 to 2.07; Wilcoxon
p = 0.00197; n = 18 paired specifications); ICC(2,1) = 0.721 (95% CI 0.630 to 0.792).

### 2.4 Reproduce the secondary checks and figure sources

```bash
python3 research/results_supplementary_checks.py     # rewrites …-results-checks/results-checks.json (identical)
python3 research/generate_revision_figures.py        # rewrites submission/figures/fig2-*.tex, fig3-*.tex, figure-data.json (identical)
python3 research/generate_revision_figures.py --render   # additionally compiles the PDFs (needs `tectonic`)
```

### 2.5 Re-running generation (optional; costs money and produces new outputs)

The runner is dry-run only unless `--execute` and the exact protocol ID are both
supplied. A dry run validates the frozen protocol, rebuilds the deterministic queue
(hash `bf97bf96…7391c`) and checks a sample payload without any network call:

```bash
python3 research/test_revision_generation.py
python3 research/run_revision_generation.py
```

To generate afresh, put `OPENROUTER_API_KEY=…` in a `.env` file at the archive root and
run with `--execute` as documented in `research/revision_outputs/README.md`. Model
availability and provider routing on OpenRouter change over time; new outputs will not
be identical to the archived ones and must not be mixed with them.

### 2.6 Ground-truth and rating workbooks

The `.mjs` scripts in `research/revision_protocol/ground-truth/` document exactly how
the workbooks were built and imported, but depend on a non-public spreadsheet library
and are provided for transparency rather than re-execution. All workbooks they
produced, and all completed returns, are included; their SHA-256 hashes are listed in
`kit-manifest.md` and `rating-return-validation.json`; `verify_manifest.py` re-checks
every hash recorded in `kit-manifest.md` against the archived file.

---

## 3. Two rating passes — which one is operative

The blinded output-rating packets were completed twice. After the first pass the three
raters revisited their understanding of the rubric anchors and re-rated the same 810
blinded assignments; the author designated the renewed set as the study's
operative/original ratings before any renewed statistic was examined. Both passes are
archived:

| Pass | Files | Status |
|---|---|---|
| First pass | `outputs/b3-rating-packets/completed/*.xlsx` → `research/revision_analysis/ATSR-SREP-R2-v1.0/` | **Superseded.** Preliminary audit trail only. Its numbers and rater rationales are not used in the manuscript. |
| Renewed pass | `…/ATSR-SREP-R2-v1.0-renewed-ratings-2026-09-17/ratings-extracted.csv` → `…/ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18/` | **Operative.** Every manuscript value derives from this analysis. |

The renewed exports did not expose the free-text rationale column; the operative
`ratings-long.jsonl` therefore carries `rationale: null` throughout, and the manuscript's
worked-example scoring explanation is labelled as a post-analysis illustration rather
than a contemporaneous rater rationale.

---

## 4. Licence

- **Code** (`*.py`, `*.mjs`): MIT Licence — see `LICENSE-CODE`.
- **Data, prompts, protocol documents, workbooks, model outputs, ratings, figures, and
  documentation**: Creative Commons Attribution 4.0 International (CC BY 4.0) — see
  `LICENSE-DATA`.

Model outputs were generated by third-party models accessed through OpenRouter and are
redistributed here for research reproducibility.

## 5. Citation

See `CITATION.cff`. Please cite the manuscript and the Zenodo archive DOI.

## 6. Contact

Arbaz Surti — arbaz.m.surti@gmail.com
