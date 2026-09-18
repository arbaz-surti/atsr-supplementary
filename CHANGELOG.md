# Changelog

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
