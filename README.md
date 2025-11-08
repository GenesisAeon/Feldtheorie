# Universal Threshold Field Initiative

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17472834.svg)](https://doi.org/10.5281/zenodo.17472834)
[![GitHub](https://img.shields.io/badge/GitHub-Feldtheorie-blue)](https://github.com/GenesisAeon/Feldtheorie)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.1.0-green.svg)](RELEASE_NOTES_v1.1.0.md)

## What's New in v1.1.0 🎉

**Enhanced System Typology**: β-heterogeneity (2.50-16.28) is now explained through a field type classification based on coupling strength, dimensionality, and coherence. Five field types identified with characteristic β-ranges. Field type explains 68% of β-variance via ANOVA (η²=0.68, p=0.0025).

**Key Achievement**: Transformed apparent limitation (β-heterogeneity) into diagnostic framework that reveals system architecture. Meta-regression of continuous covariates is exploratory (R²=0.33, not yet significant).

**Documentation**: See [`RELEASE_NOTES_v1.1.0.md`](RELEASE_NOTES_v1.1.0.md) and [`docs/field_type_classification_v1.1.md`](docs/field_type_classification_v1.1.md)

---

The Universal Threshold Field (UTF) programme studies how the logistic quartet
\((R, \Theta, \beta, \zeta(R))\) captures switch-like transitions across
astrophysics, biology, cognition, climate, and synthetic intelligence.  We fit
\(\sigma(\beta(R-\Theta))\) to curated datasets, quantify goodness of fit, and
contrast the logistic response with smooth null models (linear, power-law,
exponential).  Documentation, analysis scripts, and simulator presets are
coordinated so that each claim traces back to data, code, and reproducible
statistics.

## Emergenz & Metaquest Resonance

`seed/Emergenz.txt` distils why UTF treats emergence as a recursive
storyteller: subsystems tighten or loosen their coupling so that the global
membrane keeps \(R\) close to its guard \(\Theta\), while attraction and
repulsion rules modulate the effective steepness \(\beta\).  In practice this
means every repository surface must mirror three layers:

- **Formal:** the logistic derivations in `docs/utac_status_alignment_v1.2.md`
  explain how σ(β(R−Θ)) stays falsifiable against linear and power-law nulls.
- **Empirical:** telemetry ledgers (e.g. `analysis/results/*`,
  `docs/utac_activation_backlog.*`) show which lanterns already supply ΔAIC ≥ 10
  evidence and where ζ(R) still needs damping through BreakPoint rituals.
- **Poetic:** launch directives like `seed/Manuskriptfinalisierung und
  Kampagnenstart.pdf` and `seed/Finalize_Publish.txt` keep the symbolic
  lexicon—membranes, dawn choruses, laternen—aligned with governance pledges.

This resonance guide helps every new contribution stay isomorphic to the system
it documents: formulas echo subsystem structure, codex entries log the
telemetry, and the narrative membrane keeps UTAC’s release cadence coherent.

### Zenodo v1.2 Release Cadence

The logistic quartet \((R, \Theta, \beta, \zeta(R))\) now leans toward the
release gate: formal artefacts (`docs/utac_status_alignment_v1.2.md`), empirical
ledgers (`analysis/results/universal_beta_summary.json`), and poetic pledges
(`seed/Finalize_Publish.txt`) have to resonate before the archive is sealed.

- **Multilingual Abstract:** `docs/zenodo_multilingual_abstract_v1.2.md` mirrors
  the release narrative in EN/DE/ES so that Zenodo metadata remains in parity
  with README and codex hooks.
- **Release Playbook:** `docs/zenodo_release_playbook.md` lists the ΔAIC guards,
  CI rituals, and codex checkpoints that must fire before `release-gap-002`
  clears.
- **Telemetry Hook:** `docs/utac_activation_backlog.*` tracks
  `zenodo-v12-resonance` (β≈4.92), ensuring README/CITATION updates arrive in
  lock-step with the Zenodo upload.

When \(R>\Theta\) across these surfaces, run the playbook, log the codex entry,
and ship the repository bundle via `ZENODO_UPLOAD_GUIDE.md`.

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

## Field Type Classification (v1.1)

β is not a universal constant, but a **diagnostic parameter** revealing system architecture:

| Field Type | β Range | Examples | Key Properties |
|------------|---------|----------|----------------|
| **Strongly Coupled** | 3.5-5.0 | Neural networks, AMOC, honeybees | High coupling, fast collective response |
| **High-Dimensional** | 3.0-4.5 | LLMs, evolutionary systems | Many degrees of freedom, depth-dependent |
| **Weakly Coupled** | 2.0-3.5 | Neural plasticity, ecosystems | Local interactions, gradual transitions |
| **Physically Constrained** | 4.5-6.0+ | Black holes, earthquakes, ice sheets | Hard physical limits, abrupt transitions |
| **Meta-Adaptive** | Variable | Climate cascades, markets, consciousness | Adaptive thresholds, dynamic feedback |

**ANOVA Result**: Field type classification explains **68% of β-variance** (η²=0.68, F=10.9, p=0.0025, n=15 systems).
**Meta-Regression (exploratory)**: Continuous covariates show R²=0.33 (not yet significant, p=0.53) — further covariate refinement needed in future work.

**Try it**:
```bash
python analysis/beta_drivers_meta_regression.py  # Run meta-regression
python simulation/threshold_sandbox.py            # Explore parameter space
```

---

## Repository layout
| Directory | Description |
|-----------|-------------|
| `analysis/` | CLI scripts for logistic fitting, ΔAIC computation, β-bootstrapping, **meta-regression** (v1.1), and JSON ledgers. |
| `data/` | Domain datasets with harmonised metadata + **derived/** for β-estimates and system covariates (v1.1). |
| `docs/` | Tri-layer documentation + **field type classification v1.1** linking β to system architecture. |
| `models/` | Numerical solvers that expose impedance terms \(\zeta(R)\) and membrane dynamics. |
| `paper/` | Manuscript sources incorporating the statistical diagnostics required for publication. |
| `simulation/` | Interactive experiments + **threshold sandbox** (v1.1) for parameter space exploration. |
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

`METHODS.md`, `METRICS.md`, `ETHICS.md`, and `LIMITATIONS.md` provide concise
references for reviewers who require the statistical, metric, governance, and
methodological constraint context.

## Continuous integration
`.github/workflows/ci.yml` runs linting (`ruff`, `black --check`), tests,
optional type checks, and coverage reports on every push and pull request.  The
workflow installs dependencies from `requirements.txt` to mirror the quick-start
recipe.

## Citation
If you cite this repository, please use `CITATION.cff`.  It encodes the authorship
structure, the DOI `10.5281/zenodo.17472834`, and the current release tag (v1.1.0).

For v1.1 field type classification, cite:
> Römer, J. et al. (2025). *Universal Threshold Field Model v1.1.0: Enhanced System Typology*.
> DOI: 10.5281/zenodo.17472834
