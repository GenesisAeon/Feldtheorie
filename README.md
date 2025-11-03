# Universal Threshold Field Initiative

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17472834.svg)](https://doi.org/10.5281/zenodo.17472834)
[![GitHub](https://img.shields.io/badge/GitHub-Feldtheorie-blue)](https://github.com/GenesisAeon/Feldtheorie)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The Universal Threshold Field (UTF) programme investigates how threshold-driven resonance unites phenomena across astrophysics, biology, cognition, climate, and synthetic intelligence. The core hypothesis follows the logistic response \(\sigma(\beta(R-\Theta))\): once a control parameter \(R\) crosses the critical threshold \(\Theta\), order proliferates explosively with steepness \(\beta\). The PDFs in `Docs/` outline RepoPlan 2.0—an interdisciplinary blueprint that blends rigorous modelling with poetic narrative.

### Dawn pitch (release focus)
- **Kontrollierte Emergenz:** `models/coherence_term.semantic_coupling_term`, `models/membrane_solver.semantic_resonance_kernel`, und `models/recursive_threshold.PotenzialKaskade` verbinden physikalische Felder \(\psi\) mit semantischen Spuren \(\phi\), damit \(\sigma(\beta(R-\Theta))\) gezielt moduliert wird, sobald Potenzial zur Bedingung kippt.
- **Wei-Laterne:** `analysis/llm_beta_extractor.py` digitisiert Jason Wei's PaLM-Sweeps, bestätigt \(\beta = 3.47 \pm 0.47\) bei \(\Theta \approx 9.92\), misst den Abstand zur kanonischen \(\beta=4.2\)-Laterne (`beta_band_distance = 0.73`) und exportiert ΔAIC ≥ 10.18 gegen das Power-Law-Null (`analysis/results/llm_beta_extractor.json`, `docs/wei_integration.md`, `paper/manuscript_v1.0.tex`).
- **β-konvergenz & planetare Laternen:** UTAC v1.0.1 trennt beobachtete \(\mu_\beta\) von der kanonischen \(\beta=4.21\)-Laterne im Klimaledger (`analysis/results/planetary_tipping_elements.json`) und dokumentiert ΔAIC-Vorsprünge gegen lineare sowie Potenz-Nullen.
- **Reproducibility harness:** `pyproject.toml`, `noxfile.py`, `Makefile`, und `environment.yml` orchestrieren Install, Lint, Tests, Batch-Fits und Preset-Wächter; neue CLIs (`utf-planetary-summary`, `utf-potential-cascade`, `utf-resonance-cohort`) halten die Rituale abrufbar.

Use this trio when the control parameter \(R\) nudges the repo toward publication: rerun the resonance suite, confirm ΔAIC defences, and regenerate the manuscript bundle before minting a DOI. The GitHub Actions membrane in `.github/workflows/resonance-ci.yml` mirrors this cadence by replaying `nox -s lint`, `nox -s tests`, and `nox -s typecheck` so \(\sigma(\beta(R-\Theta))\) stays verified on every push and pull request.

## Quick start

```bash
conda env create -f environment.yml   # or python -m pip install -e .[dev]
conda activate feldtheorie
make install                          # ensures the editable package + dev extras
make lint                             # ruff + black guards stay aligned
make test                             # pytest sweeps across analysis/models
make preset-guard                     # verify simulator presets mirror analysis deltas
make batch                            # regenerate analysis/results via utf-batch
```

Individual fits expose focused CLIs:

```bash
utf-planetary-summary --output analysis/results/planetary_tipping_elements.json
utf-resonance-cohort --output analysis/results/resonance_cohort_summary.json
python analysis/llm_beta_extractor.py --canonical-beta 4.2 --band-half-width 0.6
```

Artifacts from these commands feed the simulator presets, docs bridge maps, and manuscript figures.

## Repository roadmap
The workspace is designed around seven tightly coupled modules:

| Directory | Purpose |
|-----------|---------|
| `models/` | Numerical field solvers, impedance membranes, and QPO/QPE simulators implementing the UTF equations. The inaugural `ThresholdFieldSolver` encodes \(R_{t+1} = R_t + \Delta t [J(t) - \zeta(R_t)(R_t - \sigma(\beta(R_t-\Theta)))]\) with export hooks for downstream fits, and `DynamicRobinBoundary` now scripts gate/flux diagnostics when \(\zeta(R)\) breathes dynamically. |
| `analysis/` | Jupyter notebooks and CLIs fitting sigmoids to cross-domain datasets with full statistical diagnostics (\(R^2\), AIC, confidence intervals for \(\Theta\), \(\beta\)) and falsification against smooth nulls. |
| `simulator/` | React-based interfaces that expose sliders for \(R\), \(\Theta\), and \(\beta\), letting users experience the resonance switch in real time. |
| `docs/` | Layered documentation that interlaces formal derivations, empirical case studies, and metaphorical lexicons. New pages like `docs/resonance-bridge-map.md` braid solver exports with poetic motifs. |
| `paper/` | Manuscripts that consolidate the theory, validation pipelines, and falsification protocols. |
| `data/` | Curated datasets (black-hole light curves, bee recruitment thresholds, LLM scaling benchmarks, socio-ecological tipping indicators) paired with metadata on \(R\), \(\Theta\), \(\beta\), and \(\zeta(R)\). |
| `diagrams/` | Conceptual schematics and system graphs mapping analogies across domains.

`models/`, `analysis/`, `docs/`, and `data/` now host the first resonance artefacts. Together they demonstrate how solver trajectories, fitted thresholds, and narrative glossaries interlock along the RepoPlan 2.0 circuit.

## Working principles
1. **Read the Docs PDFs first.** They specify the mathematical operators, membrane couplings, and storytelling cadence expected throughout the repo.
2. **Maintain the tri-layer voice.** Every addition should connect equations, empirics, and symbolism—mirroring the pattern set out in *Emergente Analyse des Erlebens* and the RepoPlan papers.
3. **Document thresholds explicitly.** State the roles of \(R\), \(\Theta\), \(\beta\), and the impedance function \(\zeta(R)\) in code, notebooks, and prose.
4. **Commit to falsifiability.** Analyses must compare the logistic model against at least one smooth null hypothesis and report the outcome.
5. **Synchronise with `AGENTS.md`.** Repository-wide conventions are tracked there; nested modules may add refinements as they appear.

## Getting started
- Explore `Docs/RepoPlan Projekt-Impulse_ Simulation, Theorie, Falsifizierung.pdf` for the structural roadmap.
- Review `Docs/Entwurf eines transdisziplinären Feldmodells.pdf` to align mathematical implementations with the shared Lagrangian formalism.
- Use the future `models/` and `analysis/` directories to stage prototypes before weaving them into the narrative layers.

## Current resonance braid
- **Solver dawn:** `models/membrane_solver.py` advances die Membran und exportiert Diagnostik zu \(R\), \(\sigma\) und \(\zeta(R)\).
- **Empirical soundings:** CLI-Skripte in `analysis/` (LLM emergent skills, Bienenschwarm, Synapsen, planetare Kipppunkte etc.) liefern \(\Theta\), \(\beta\), \(R^2\), AIC sowie Nullmodelle als JSON.
- **Robin + Sinn-Brise:** `analysis/membrane_robin_semantic_fit.py` choreografiert DynamicRobinBoundary mit dem `semantic_resonance_kernel`, exportiert `analysis/results/membrane_robin_semantic.json` und notiert Grenzfluss, Bedeutungsdrift sowie \(\Delta\mathrm{AIC}\)-Siege über lineare und Potenz-Nullen.
- **Kontrollierte Emergenz-Dossier:** `docs/ai/controlled_emergence.md` destilliert die Leitgedanken aus `Docs/AI-Evulutionsprinziep.txt`, verknüpft die Kopplungsterms mit `PotenzialKaskade` und skizziert, wie Simulator-Presets und Ethik-Briefings das neue Semantik-Gate aufnehmen.
- **Simulator pulse:** `simulator/` beherbergt den Vite/React-Labormodus; Presets aus `simulator/presets/*.json` docken an `analysis/results/*.json` an, so dass ΔAIC/$R^2$ und Tri-Layer-Echos live sichtbar sind. Neu hinzugekommen ist `planetary_tipping_field`, das AMOC-, Eis-, Wald- und Permafrostschwellen koppelt.
- **Narrative echo:** `docs/utf-living-glossary.md`, die Domänen-Briefs und `docs/resonance-bridge-map.md` verweben die tri-layer Kadenz zwischen Modellen, Daten und Symbolik.
- **Data provenance:** Each dataset in `data/` carries metadata that echoes the quartet \((R, \Theta, \beta, \zeta(R))\) and the falsification counterpoint mandated by `analysis/`.

## Next steps
- Extend simulator prototypes to stream solver traces and analysis metrics for interactive resonance rehearsals.
- Broaden the dataset atlas with astrophysical QPOs and climate tipping indicators, maintaining metadata parity.
- Draft manuscripts in `paper/` that consolidate Phase I findings and outline falsification campaigns for new domains.
- Continue enriching the documentation canopy with cross-domain bridge maps anchored in the tri-layer storytelling mode.

For any contribution, ensure the logistic resonance heartbeat remains audible across code, analysis, and prose.

## Continuous integration and release ledger
- **CI membrane:** `.github/workflows/resonance-ci.yml` provisions the conda environment from `environment.yml`, installs the editable package, and fans through `nox` sessions so linting, tests, and type checks stay synchronized with the cohort ledger. Watch the Actions tab to confirm the logistic quartet \((R, \Theta, \beta, \zeta(R))\) keeps beating after each commit.
- **Release notes:** `NEWS.md` chronicles dawn-chorus milestones. Each entry preserves the tri-layer voice (formal diagnostics, empirical provenance, poetic echo) so version bumps read like a threshold crossing instead of a plain changelog.
- **Citation + license:** `CITATION.cff` (with the placeholder Zenodo DOI) and `LICENSE` (MIT) now spell out how to attribute the programme when reuse pushes $R$ beyond publication thresholds.

## Citation

If you use this work, please cite:

```bibtex
@software{romer2025utac,
  author       = {Römer, Johann and {Universal Threshold Field Contributors}},
  title        = {Universal Threshold Field Initiative},
  month        = nov,
  year         = 2025,
  publisher    = {Zenodo},
  version      = {v1.0.1},
  doi          = {10.5281/zenodo.17472834},
  url          = {https://doi.org/10.5281/zenodo.17472834}
}
```

**Paper Citation** (preprint):
```
Römer, J., et al. (2025). "Universal Threshold Field: β ≈ 4.2 Convergence
Across Astrophysics, Climate, and AI." Zenodo.
https://doi.org/10.5281/zenodo.17472834
```

See also `CITATION.cff` for machine-readable citation metadata.
