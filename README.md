# ATSR Supplementary Materials

Supplementary materials for:

> **AI-Assisted Test Scope Recommendation for Manual QA: A Framework and Evaluation**
> Arbaz Surti — *Software Quality Journal* (Springer), submitted 2026

---

## Repository Contents

### `data/`
- **`specifications.json`** — The 18 synthetic feature specifications used in the evaluation (JSON format). Specifications are derived from real enterprise QA tickets; all company names, brand identifiers, and vendor names have been replaced with generic equivalents.
- **`specifications.md`** — Human-readable version of the same 18 specifications.

### `results/`
- **`atsr-outputs.json`** — Raw JSON output from ATSR for all 18 specifications (GPT-4o, temperature 0.2, via OpenRouter API).
- **`baseline-outputs.json`** — Raw JSON output from the naive baseline for all 18 specifications (same model, same schema, unstructured prompt).
- **`rubric-scores.json`** — Machine-readable rubric scores (primary evaluator) for all 18 specifications across all five dimensions.
- **`rubric-scores-readable.md`** — Human-readable rubric scorecard with per-specification dimension scores and scorer notes.
- **`baseline-scores.json`** — Rubric scores for the naive baseline condition.

### `evaluation/`
- **`irr-scoring-sheet.md`** — Inter-rater reliability scoring data: dimension scores from the primary evaluator (R1) and independent reviewer (R2) for the six-specification IRR subset.

### `code/`
- **`atsr_tool.py`** — Python implementation of ATSR. Contains the full system prompt (lines 45–110), user prompt builder, and OpenRouter API integration. Requires an `OPENROUTER_API_KEY` in a `.env` file.
- **`baseline_tool.py`** — Python implementation of the naive baseline. Same API setup as `atsr_tool.py` but with an unstructured system prompt.

---

## Reproducing the Evaluation

1. Clone this repository.
2. Install dependencies: `pip install requests python-dotenv`
3. Create a `.env` file in the `code/` directory with your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your-key-here
   ```
4. Run ATSR over the specifications:
   ```bash
   cd code
   python atsr_tool.py
   ```
5. Compare outputs against the rubric in `results/rubric-scores-readable.md`.

---

## ATSR System Prompt

The core of the ATSR framework is the system prompt in `code/atsr_tool.py` (lines 45–110). It encodes:
- Eight reasoning dimensions (functional, smoke, regression, integration, exploratory scope; coverage depth; effort estimate; clarification flags)
- Coverage depth calibration rules (LOW / MEDIUM / HIGH by change type)
- Specificity and quality guidelines

---

## Licence

The evaluation dataset and scoring artefacts in this repository are made available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The code is made available under the MIT Licence.

---

## Citation

If you use these materials, please cite:

```
Surti, A. (2026). AI-Assisted Test Scope Recommendation for Manual QA: A Framework
and Evaluation. Software Quality Journal. Springer.
```
