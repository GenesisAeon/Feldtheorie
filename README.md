# Universal Threshold Field Initiative

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17472834.svg)](https://doi.org/10.5281/zenodo.17472834)
[![GitHub](https://img.shields.io/badge/GitHub-Feldtheorie-blue)](https://github.com/GenesisAeon/Feldtheorie)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The Universal Threshold Field (UTF) programme studies how the logistic quartet
\((R, \Theta, \beta, \zeta(R))\) captures switch-like transitions across
astrophysics, biology, cognition, climate, and synthetic intelligence.  We fit
\(\sigma(\beta(R-\Theta))\) to curated datasets, quantify goodness of fit, and
contrast the logistic response with smooth null models (linear, power-law,
exponential).  Documentation, analysis scripts, and simulator presets are
coordinated so that each claim traces back to data, code, and reproducible
statistics.

## Quick start: β & ΔAIC in under 10 minutes

````md
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/reproduce_beta.py --csv data/ai/wei_emergent_abilities.csv --out dist/wei_beta.json
cat dist/wei_beta.json
```
````

- Determinism: the pipeline seeds NumPy with `RANDOM_SEED = 1337`.  Minor
  numerical drift can occur because of BLAS implementations.
- Methodology: see `METHODS.md` for fitting details and null-model definitions.
- Interpretation: ΔAIC ≥ 10 relative to each null model constitutes strong
evidence for the UTF logistic response.

## Repository layout
| Directory | Description |
|-----------|-------------|
| `analysis/` | CLI scripts and notebooks that fit the logistic model, compute ΔAIC, bootstrap \(\beta\), and export JSON ledgers. |
| `data/` | Domain datasets with harmonised metadata satisfying `schemas/metadata.schema.json`. |
| `docs/` | Tri-layer documentation linking formal derivations, empirical evidence, and interpretive notes. |
| `models/` | Numerical solvers that expose impedance terms \(\zeta(R)\) and membrane dynamics. |
| `paper/` | Manuscript sources incorporating the statistical diagnostics required for publication. |
| `simulator/` | Interactive experiments that replay fitted quartets for outreach and exploratory work. |
| `tests/` | Pytest suites ensuring regressions on fits, JSON payloads, and simulator presets. |

## Reproduction workflow
1. Install dependencies via `pip install -r requirements.txt` or `conda env create -f environment.yml`.
2. Run the statistical harness:
   ```bash
   python scripts/reproduce_beta.py --csv data/ai/wei_emergent_abilities.csv --out dist/wei_beta.json
   ```
3. Validate CI-equivalent checks locally:
   ```bash
   make lint test
   ```
4. Regenerate manuscript assets with `make batch` and consult `paper/manuscript_v1.0.tex` for DOI-linked references.

`REPRODUCE.md` contains extended instructions covering climate and cognition fits
plus simulator alignment tests.

## Data governance
Each dataset is accompanied by `<name>.metadata.json` describing variables,
logistic parameters, ΔAIC margins, licensing, and provenance.  The schema in
`schemas/metadata.schema.json` enforces required fields while permitting
domain-specific details.  When contributing new data:

- cite the canonical publication or dataset URL,
- document licensing explicitly,
- report \(\beta\), \(\Theta\), and ΔAIC for the logistic fit,
- note how impedance \(\zeta(R)\) was configured.

## Documentation cadence
UTF documentation maintains a tri-layer narrative:

1. **Formal layer.** Equations and algorithmic procedures (see `docs/utac_theory_core.md`).
2. **Empirical layer.** Dataset-specific diagnostics, bootstrap intervals, and falsification logs (`docs/utac_falsifiability.md`).
3. **Interpretive layer.** Symbolic and ethical framing linked to `ETHICS.md` and simulator notes.

`METHODS.md`, `METRICS.md`, and `ETHICS.md` provide concise references for
reviewers who require the statistical, metric, and governance context.

## Continuous integration
`.github/workflows/ci.yml` runs linting (`ruff`, `black --check`), tests,
optional type checks, and coverage reports on every push and pull request.  The
workflow installs dependencies from `requirements.txt` to mirror the quick-start
recipe.

## Citation
If you cite this repository, please use `CITATION.cff`.  It encodes the authorship
structure, the DOI `10.5281/zenodo.17472834`, and the current release tag.
