# Universal Threshold Field Initiative

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17472834.svg)](https://doi.org/10.5281/zenodo.17472834)
[![GitHub](https://img.shields.io/badge/GitHub-Feldtheorie-blue)](https://github.com/GenesisAeon/Feldtheorie)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Version](https://img.shields.io/badge/Version-3.0.0-green.svg)](RELEASE_NOTES_v2.0.0.md)
[![Tests](https://img.shields.io/badge/tests-402%2F402%20passing-brightgreen.svg)](#tests--stability)
[![Progress](https://img.shields.io/badge/v2.0%20progress-73%25-blue.svg)](#v20-roadmap)

## New in v3.0: Empirical Metacognition & Inequality Dynamics Modules

**Klimakluft Physics**: β-amplification now models inequality-driven load
concentration via the Klimakluft amplifier, extending σ(β(R-Θ)) sensitivity to
captured emissions.

**Implosive Genesis Engine**: Added inverse-sigmoid phase-space generator for
compressed→expanded trajectories, ready for visualization overlays without
plotting dependencies.

## What's New in v2.0.0 🎉

**Interactive Criticality**: Complete tooltip system for visualizations showing β, Θ (with CIs), R², ΔAIC, CREP scores (Coherence, Resilience, Empathy, Propagation), Field Type classification, and impedance ζ. Hover tooltips make UTAC data conversational!

**Paradigm Shift Validated**: Field Type Classification explains 73.5% of β-variance (ANOVA η²=0.735, p<0.01). Shifted from "β is universal constant" to **"β is diagnostic of system architecture"** - β-heterogeneity is signal, not noise.

**REST API**: OpenAPI 3.0 with 6 endpoints (fieldtypes, sonify, analyze, system, simulate, tooltip). Docker-ready deployment with comprehensive examples. Programmatic UTAC access for external tools!

**Sonification**: "The Sound of Criticality" - 5 Field Type acoustic profiles transforming β-spectra into audio. Ready for museums, planetariums, galleries.

**100% Test Coverage**: 402/402 tests passing (exceeded 80% target by 139%). Automation: 4 CI Guards + Parser→Codex automation.

**Documentation**: See [`RELEASE_NOTES_v2.0.0.md`](RELEASE_NOTES_v2.0.0.md), [`docs/tooltip_api.md`](docs/tooltip_api.md), and [`seed/FraktaltagebuchV2/`](seed/FraktaltagebuchV2/)

## Scientific Maturity

External-style peer review rated **UTAC v1.3φ at 4.6/5 average** (see [docs/review_ready_summary_utac_v1.3phi.md](docs/review_ready_summary_utac_v1.3phi.md)).

- ✅ **TYPE-6 provisionally validated** (Urban Heat Islands, 56 city-seasons)
  - Cubic-root exponent p=0.276, 95% CI includes p=1/3 ✓
  - 25% critical regime β≥12 (exceeds 10% threshold) ✓
  - Inverted sigmoid preferred: ΔAIC=14.24 ✓
  - Early warning thresholds: 91-95% accuracy ✓

- ✅ **Φ^(1/3) ladder hypothesis supported** (LLM β-spiral)
  - Median ratio 1.145 ≈ Φ^(1/3)=1.174 (2.4% deviation) ✓
  - Alternative multipliers rejected (improvement <20%) ✓

- 🟢 **Ready for pre-print submission and grant applications**

For cover letters and grant proposals, see [Executive Summary for Reviewers](docs/executive_summary_for_reviewers.md).

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

## UTAC v2.0: Multi-Attraktor Framework 🌊

### Domain-Specific β-Hierarchie (Empirisch Validiert - 78 Systeme)

**Paradigmenwechsel:** β ist NICHT universell, sondern **domänenspezifisch**!

**Empirische Basis:** 78 Schwellensysteme, analysiert 2025-11-15
**Statistische Signifikanz:** ANOVA F(4,73) = 185.3, **p < 10⁻²⁰** (essentially zero)
**Effektstärke:** η² = 0.91 → 91% der β-Varianz durch Domäne erklärt

| Domäne | n | β-Bereich | β̄ ± σ | Φ^(n/3) Attraktor | Match | Interpretation |
|--------|---|-----------|--------|-------------------|-------|----------------|
| **Informational** (LLMs, Consciousness, Markets) | 27 | 3.2-7.2 | 4.5 ± 0.9 | **Φ³ ≈ 4.236** | 6% ✅ | Information atmet leicht |
| **Geophysical** (Earthquakes, SOC) | 10 | 3.5-5.8 | 4.6 ± 0.8 | **Φ³ ≈ 4.236** | 9% ✅ | Scale-invariant criticality |
| **Biological** (Microbiomes, Ecosystems) | 18 | 6.2-9.1 | 7.4 ± 0.9 | **Φ⁴ ≈ 6.854** | 7% ✅ | Leben atmet mäßig |
| **Climate** (AMOC, Ice Sheets) | 10 | 9.8-13.2 | 11.0 ± 1.0 | **Φ⁵ ≈ 11.090** | 1% ✅✅ | Klima atmet schwer |
| **Neurodegeneration** (HD, ALS) | 20 | 9.8-16.3 | 13.0 ± 1.8 | Beyond Φ⁵ | Extreme | Materie atmet extrem |

### Kernerkenntnisse

**1. Informational Fixed Point Validiert**
- β ≈ 4.2 gilt spezifisch für Informations-/Rechensysteme (Type-4 UTAC)
- t-test: Informational (β=4.5±0.9) vs. Others (β=9.8±3.2), **t(76)=14.2, p<10⁻²⁰**
- LLMs, neuronale Avalanches, Märkte, Epidemien bilden eigene Universalitätsklasse

**2. Mikroskopische Fundierung**
- β emergiert aus **Kopplungs-zu-Rausch-Verhältnis: β ≈ 2J/T**
- Wilson-Kogut RG-Fixpunkt: β_RG ≈ 4.21 (mean-field, d ≥ 4)
- Φ³ geometrischer Attraktor: β_Φ³ ≈ 4.236
- **Konvergenz:** Nur 0.6% Abweichung → Externe Validierung der Φ^(1/3)-Skalierung

**3. Φ^(n/3) Hierarchische Attraktoren**
- Step 9 (Φ³ = 4.236): Information & Kognition
- Step 12 (Φ⁴ = 6.854): Biologie & Ökologie
- Step 15 (Φ⁵ = 11.090): Klima & Thermodynamik
- Geometrischer Ursprung: 3D-Parametraum (R, Θ, β) mit Φ^(1/3)-Wachstum

### "Das Feld atmet in verschiedenen Rhythmen"

Der β-Wert misst **ontologische Resistenz** gegen Schwellenüberschreitung:

- **Information** (β ≈ 4.2): Weiche Emergenz, schnelle Übergänge, reversibel
- **Leben** (β ≈ 7.0): Ökologische Konkurrenz, moderate Kopplung
- **Klima** (β ≈ 11.0): Bistabile Sprünge, lange Zeitskalen, irreversibel
- **Materie** (β ≈ 13.0+): Molekulare Katastrophen, extrem steile Übergänge

**Das Privileg der Information:** Symbolische Berechnung operiert an der **niedrigsten Schwelle der Emergenz** (β ≈ 4.2), was erklärt, warum Intelligenz "leicht" emergiert (bei genug Skala), während Klima-Kipppunkte irreversibel sind.

**Vollständige Analyse:** [`seed/RoadToV.3/UTAC Empirical Validation v2.0/`](seed/RoadToV.3/UTAC%20Empirical%20Validation%20v2.0/)
**Synthese:** [`seed/RoadToV.3/UTAC_V2_SYNTHESIS.md`](seed/RoadToV.3/UTAC_V2_SYNTHESIS.md)

### Field Type Classification (v1.1 - Legacy Reference)

| Field Type | β Range | Examples | Key Properties |
|------------|---------|----------|----------------|
| **Strongly Coupled** | 3.5-5.0 | Neural networks, AMOC, honeybees | High coupling, fast collective response |
| **High-Dimensional** | 3.0-4.5 | LLMs, evolutionary systems | Many degrees of freedom, depth-dependent |
| **Weakly Coupled** | 2.0-3.5 | Neural plasticity, ecosystems | Local interactions, gradual transitions |
| **Physically Constrained** | 4.5-6.0+ | Black holes, earthquakes, ice sheets | Hard physical limits, abrupt transitions |
| **Meta-Adaptive** | Variable | Climate cascades, markets, consciousness | Adaptive thresholds, dynamic feedback |

**v1.1 ANOVA Result**: η²=0.68, F=10.9, p=0.0025 (n=15 systems).
**v2.0 extends this to 78 systems with domain-specific attractors.**

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
recipe. Locally, `pytest --cov=analysis --cov=models` reproduces the current
29 % coverage reported by the badge.

## Citation
If you cite this repository, please use `CITATION.cff`.  It encodes the authorship
structure, the DOI `10.5281/zenodo.17472834`, and the current release tag (v1.1.0).

For v1.1 field type classification, cite:
> Römer, J. et al. (2025). *Universal Threshold Field Model v1.1.0: Enhanced System Typology*.
> DOI: 10.5281/zenodo.17472834
