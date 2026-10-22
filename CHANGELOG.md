# Changelog

## 2.1.0 — 2026-10-22

Two post-hoc analyses added during the October 2026 review round at *Scientific
Reports*. Both read the locked operative analysis (and, for the second, the generation
records) read-only; no existing file changed, no output was regenerated, and no rating
changed. Neither analysis was pre-specified in `ATSR-SREP-R2-v1.0`.

Added
- `research/round3_depth_baseline.py` and
  `research/revision_analysis/ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18-round3-depth-baseline/depth-baseline.json`:
  always-HIGH majority-class depth baseline, balanced accuracy, Cohen's κ (unweighted
  and linear-weighted), and specification-bootstrap intervals.
- `research/round3_structural_failures.py` and
  `research/revision_analysis/ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18-round3-structural-failures/structural-failures.json`:
  impact of the Claude Sonnet 4.6 structural failures on the primary ATSR − GSQ
  comparison (bounds, tipping point, completion-token descriptives).

Changed
- README (version, file table, Section 2.4 commands), `CITATION.cff`, `.zenodo.json`,
  `LICENSE-DATA` attribution, `MANIFEST-SHA256.txt`.

## Unreleased (post-2.0.0 metadata only)

- Recorded the Zenodo DOI minted for release v2.0.0 (`10.5281/zenodo.22839182`;
  concept DOI `10.5281/zenodo.22839181`) in `CITATION.cff`, `LICENSE-DATA`, and
  `README.md`; regenerated `MANIFEST-SHA256.txt`. No study files changed.

## 2.0.0 — 2026-09-18

Expanded evaluation under the frozen protocol `ATSR-SREP-R2-v1.0`, prepared for the
revision of the manuscript at *Scientific Reports*.

Added
- Frozen protocol, lock file, prompts, model-availability record, and validator
  (`research/revision_protocol/`).
- Complete generation archive: 584 attempts / 486 terminal outputs across three
  conditions × three model families × three runs (`research/revision_outputs/`).
- Ground-truth procedure, kit manifest, raw independent submissions, consensus
  adjudication, rubric v1 (draft and final), calibration procedure and returns,
  blinded rating-packet procedure and packets (`research/revision_protocol/…`,
  `outputs/`).
- Operative ratings (810 assignments; 665 scorable) and the operative analysis with
  all statistics, plus the superseded first-pass analysis as an audit trail
  (`research/revision_analysis/`).
- Analysis, checks, extraction, and figure-generation scripts (`research/*.py`);
  manuscript Figures 2–3 sources and PDFs (`submission/figures/`).
- `verify_manifest.py`, `MANIFEST-SHA256.txt`, `requirements.txt`, `CITATION.cff`,
  `.zenodo.json`, `LICENSE-CODE`, `LICENSE-DATA`.

Changed
- Version 1.0.0 files moved unchanged to `original-evaluation/` (results, evaluation
  sheet); `atsr_tool.py` and `baseline_tool.py` moved to the archive root, where the
  protocol validator imports them; the dataset moved to `supplementary/data/`, the
  path recorded in the frozen protocol.
- `original-evaluation/results/baseline-scores.json`: aggregate fields corrected on
  2026-09-13 to match the row-level scores that were always the primary record (Risk
  Calibration 64/90; grand total 306/450 = 68.0%). Row-level scores unchanged.
- README rewritten for the expanded evaluation.

## 1.0.0 — 2026-03-22

Original single-model (GPT-4o), single-run evaluation of ATSR against a naïve baseline
on 18 specifications, with author scoring and a six-specification independent rescoring.
