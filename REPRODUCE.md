# Reproduction Guide for UTF v1.0.1

This guide documents the deterministic steps required to reproduce the logistic
fits, ΔAIC comparisons, and bootstrap diagnostics that underpin the Universal
Threshold Field programme.

## 1. Environment setup

### Option A — Python virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .[dev]
```

### Option B — Conda environment
```bash
conda env create -f environment.yml
conda activate feldtheorie
```

Both options install the dependencies used in continuous integration.  All
scripts seed NumPy with `RANDOM_SEED = 1337` to ensure reproducible bootstrap
samples.

## 2. Core analyses

### 2.1 LLM emergent abilities (Wei bridge)
```bash
python scripts/reproduce_beta.py \
  --csv data/ai/wei_emergent_abilities.csv \
  --out dist/wei_beta.json
```
Expected structure:
```json
{
  "dataset": "wei_emergent_abilities.csv",
  "logistic_parameters": {
    "beta": 3.47,
    "theta": 9.92,
    "beta_ci_95": [3.0, 3.9],
    "delta_aic_power": 12.1,
    "r_squared": 0.89
  }
}
```
Compare the JSON against `analysis/results/llm_beta_extractor.json` and the
statements in `docs/wei_integration.md`.

### 2.2 Planetary tipping ensemble
```bash
python analysis/planetary_tipping_elements_fit.py \
  --output analysis/results/planetary_tipping_elements.json
```
Verify that ΔAIC exceeds 30 relative to linear and power-law nulls and that the
reported \(\beta\) falls within the canonical \([3.6, 4.8]\) band.

### 2.3 Cognitive thresholds
```bash
python analysis/working_memory_gate_fit.py --output analysis/results/working_memory_gate.json
```
Inspect the exported JSON for bootstrap intervals and impedance notes.  Cross
check with `data/cognition/working_memory_gate.metadata.json`.

## 3. Validation suite

1. **Tests:** `make test`
2. **Lint:** `make lint`
3. **Type check (optional):** `nox -s typecheck`

Continuous integration (`.github/workflows/ci.yml`) executes the same steps on
GitHub Actions.

## 4. Sensitivity and falsification

- Re-run `scripts/reproduce_beta.py` with `--null-models linear power` to confirm
  ΔAIC thresholds.
- Use `--bootstrap-samples 2000` for tighter confidence intervals when analysing
  new datasets.
- Document any violations of \(\beta\in[3.6,4.8]\) or ΔAIC ≥ 10 in
  `docs/utac_falsifiability.md` and open an issue.

## 5. Simulator alignment

`simulator/presets/*.json` pull parameter values from `analysis/results/`.  After
regenerating results, run:
```bash
python analysis/preset_alignment_guard.py
```
The guard ensures that simulator presets match the latest logistic parameters
and ΔAIC diagnostics.

## 6. Manuscript regeneration

To update the preprint assets:
```bash
make batch
make manuscript
```
`make manuscript` calls `latexmk` according to `COMPILE_MANUSCRIPT.md` and embeds
the DOI (10.5281/zenodo.17472834) within `paper/manuscript_v1.0.tex`.
