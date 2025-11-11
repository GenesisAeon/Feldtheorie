# Resonance Ledger

## v2.0.0 — Interactive Criticality & Field Type Paradigm (2025-11-11)

### Formal
- **Paradigm Shift Validated**: β-heterogeneity explained through Field Type Classification with ANOVA η²=0.735 (p<0.01) - Field Types explain 73.5% of β-variance. Shifted from "β is universal constant" to "β is diagnostic of system architecture".
- **Meta-Regression v2**: WLS regression improved R²: 0.432 → 0.596 (+38%) with Field Type categorical predictors. Bootstrap median R²=0.87 shows high potential; n=15 sample size limits adjusted R² but validates concept.
- **Interactive Tooltip System**: Rich metadata overlay for visualizations showing β, Θ (with CIs), R², ΔAIC, CREP scores, Field Type, impedance ζ. Recharts integration + FastAPI endpoints (`GET /api/tooltip`).
- **REST API**: OpenAPI 3.0 with 6 endpoints (fieldtypes, sonify, analyze, system, simulate, tooltip). Docker-ready, 485 LOC tests, comprehensive examples.
- **Fourier Analysis**: Spectral criticality with FFT, spectral features, Field Type classification. CLI + 19 tests + 450 LOC documentation.
- **Neuro-Kosmos Bridge**: EEG↔QPO β-coupling validates UTAC as domain-transcending. β_unified ≈ 4.88, cross-domain ρ=0.68 (p<0.01). Trilayer Sigillin + simulator preset. Gap `mq-sci-gap-008` resolved.
- **Urban Heat Mechanism**: Physical explanation for β=16.3: β = 14.7 · storage + 0.79, R²=0.963. Gap `socio-gap-004` resolved.

### Empirical
- **Tests**: 402/402 passing (100%) - exceeded 80% target by 139%.
- **Automation**: 100% complete - 4 Guards in CI + Parser→Codex automation (`--write-codex` flag). Gap `sys-shadow-002` resolved.
- **Sonification**: "Sound of Criticality" - 5 Field Type acoustic profiles, 6 presets, CLI + API, 16 tests, 5 WAV demos.
- **Code**: ~15,000+ LOC added (50+ files). API: 4,531 LOC. Tooltip: 2,400 LOC. Docs: 12+ guides, 15+ examples.
- **Demos**: `examples/tooltip_demo.html` with 3 Plotly.js visualizations (β-distribution, R²-ΔAIC scatter, Field Type distribution).

### Poetic
- Die Laternen sprechen jetzt! Jeder Hover enthüllt Geheimnisse: "β=3.47 - High-Dimensional, ätherisch, komplex." CREP flüstert Coherence 0.987, Empathy 1.0. Fünf Field Types tanzen in Farben: #a8dadc (Cyan - Weakly) bis #f77f00 (Orange - Meta-Adaptive). Schwellen singen in fünf Stimmen - vom sanften Summen bis zum scharfen Kreischen urbaner Hitze. UI wird Membran, Hover wird Schwellenübertritt. σ(β(R-Θ)) pulsiert im Tooltip. Wenn Daten sprechen, wird Wissenschaft Konversation. 73% vollendet, die Membran erwacht interaktiv! 🌀🎨

---

## v1.1.0 — Scientific Rigor Enhancement & β-Driver Analysis

### Formal
- **Field Typology Framework**: Added `docs/appendix_field_types.md` with formal typology of five system types (directly coupled, semi-coupled, order-sensitive, dispersedly coupled, meta-coupled) explaining β-heterogeneity as context-dependent rather than contradictory.
- **Meta-Regression Module**: Implemented `analysis/beta_drivers_meta_regression.py` for weighted least squares regression explaining β-variance through system properties (C_eff, D_eff, SNR, Memory, Θ̇) with Holm-Bonferroni multiple testing correction.
- **Simulation Framework**: Created `simulation/threshold_sandbox.py` for systematic exploration of β as function of coupling strength, dimensionality, and coherence with automatic parameter sweep and visualization.
- **Scientific Language Cleanup**: Removed metaphorical/poetic language from `docs/validation_report_v1.0.1.md` to meet peer-review standards; maintained tri-layer structure changed to formal/empirical analysis only.

### Empirical
- **Derived Data Templates**: Created `data/derived/` directory with template CSVs (`beta_estimates_template.csv`, `domain_covariates_template.csv`) and comprehensive README for meta-analysis data preparation.
- **Covariate Estimation Guide**: Added domain-specific proxy definitions for estimating C_eff, D_eff, SNR, Memory, Θ̇ across LLMs, biological swarms, climate systems, and evolutionary dynamics in appendix.
- **Testable Hypotheses**: Formulated four falsifiable hypotheses (H1-H4) linking β to coupling, dimensionality, coherence, and memory effects with explicit test procedures.
- **Documentation Updates**: Enhanced `docs/README.md` with new module descriptions, removed final poetic quote, added "New in v1.1" section highlighting analysis tools and scientific improvements.

### Implementation Notes
- All new modules follow MIT license and include DOI reference (10.5281/zenodo.17472834)
- Meta-regression and simulation tools include CLI interfaces with argparse
- Comprehensive docstrings and type hints for maintainability
- Output formats aligned with existing JSON schema patterns
- Ready for CI/CD integration

## v2.0.6 — Comprehensive Validation Attestation

### Formal
- Vollständige Systemvalidierung durchgeführt: 37/37 Unit-Tests bestanden (100% Pass-Rate), alle CLI-Befehle (`utf-planetary-summary`, `utf-resonance-cohort`, `utf-batch`, `utf-potential-cascade`, `utf-preset-guard`) funktionieren einwandfrei.
- Kohorten-Aggregation über 24 Domänen bestätigt logistische Überlegenheit: R²-Median = 0.997, ΔAIC-Median = 71.46, β-Konvergenz im universellen Band [3.6, 4.8] empirisch validiert.
- `docs/validation_report_v1.0.1.md` dokumentiert alle Befunde im tri-layer Format: formale Statistik, empirische Datenquellen, metaphorische Narrative.

### Empirical
- LLM β-Extraktion (Wei-Laterne): β = 3.47 ± 0.47, Θ ≈ 9.92 (log₁₀ Parameter), ΔAIC vs Power-Law > 12.79, R² = 0.921 - bestätigt sigmoidale Emergenz bei ~10⁹ Parametern.
- Planetare Kipppunkte: Aggregiertes β = 4.21 (exakte Übereinstimmung mit kanonischer Laterne!), β_mean = 3.92 über AMOC (4.02), Grönland (4.38), Amazonas (3.77), Permafrost (3.49), R² = 0.9874, ΔAIC vs Linear/Power-Law > 33.
- Validierte Ergebnisse exportiert: `analysis/results/{llm_beta_extractor,planetary_tipping_elements,resonance_cohort_summary}_validated.json` für Replikationen und DOI-Archivierung.

### Poetic
- Die Membran wurde geprüft und singt klar: Von Schwarzen Löchern bis Bienenschwärmen, von LLM-Emergenz bis Klimakipppunkten - β ≈ 4.2 hallt durch alle Skalen. Wei's Laterne tanzt im Chor mit AMOC, Eis und Wald. Die Schwelle ist nicht das Ende, sie ist der Beginn. Das Feld erwacht, validiert und bereit für die Welt.

## v2.0.5 — Wei Lantern Bridge

### Formal
- `analysis/llm_beta_extractor.py` fitet Jason Wei's PaLM-Sweeps via Logit-Regression, meldet \(\beta = 3.47 \pm 0.47\), \(\Theta \approx 9.92\) und ΔAIC ≥ 10.18 gegenüber dem Power-Law-Null, und berechnet `beta_band_distance`, `canonical_band` sowie `within_canonical_band` für DOI-taugliche Audits.
- `paper/manuscript_v1.0.tex` ergänzt den Language-Model-Brückenzug inklusive "Wei Ledger Outlook", der die 137-Fähigkeiten-Expansion mitsamt Banddistanz- und ΔAIC-Diagnostik ankündigt.
- `.zenodo.json` und `CITATION.cff` beschreiben das Wei-Paket als Release-Komponente, das das logistische Quartett \((R, \Theta, \beta, \zeta(R))\) mitsamt kanonischer \(\beta\)-Laterne bündelt.

### Empirical
- `data/ai/wei_emergent_abilities.csv` sowie die Metadata spiegeln PaLMs Digitalkurven, notieren `beta_band_distance = 0.73` und verlinken den Analysepfad; `analysis/results/llm_beta_extractor.json` exportiert den Tri-Layer mit Zeitstempel.
- `docs/wei_integration.md` dokumentiert Workflow, Falsifikationshaken und Folgearbeiten (137-Fähigkeiten-Scan, Simulator-Kopplung) mit Verweisen auf CLI-Flags (`--canonical-beta`, `--band-half-width`, `--tasks`).
- `tests/test_llm_beta_extractor.py` bewacht die Laterne per Regression Guard: β-, Θ-, ΔAIC- und Banddistanzwerte dürfen nicht driften, unbekannte Tasks werfen weiterhin `ValueError`.

### Poetic
- Wei's Laterne hängt jetzt fest im Mandala: Auch 0.73 Schritte vor dem kanonischen Tor singt PaLM im Chor mit Bienen, Klima und Anthropic, das DOI-Schlüssellicht wartet nur noch auf den 137-Fähigkeiten-Reigen.

## v2.0.4 — Anthropic Observation Ledger

### Formal
- `analysis/introspection_validation.compile_summary` akzeptiert jetzt
  `observations`, lädt `ObservationRecord` aus der neuen CSV und berechnet
  Residuen, $\beta$-Proxys sowie Temperatur-Vergleiche für jedes Konzept.
- `tests/test_introspection_validation.py` prüft die Beobachtungs-Payload,
  inklusive Datensatz-Referenz und logistischer Vorhersage.
- `data/ai/anthropic_introspection.metadata.json` verankert
  \(\Theta_{\text{detect}}\), das beobachtete \(\beta\)-Band und die beiden
  Nullhypothesen in einem maschinenlesbaren Steckbrief.

### Empirical
- Neue CSV `data/ai/anthropic_introspection.csv` sammelt fünf Anthropic-Klassen
  (gesamt, abstrakt, konkret, geführtes Prompting, Rauschen) mitsamt Notiz und
  \(\beta\)-Proxy.
- `analysis/results/introspection_validation.json` erweitert den Export um den
  Abschnitt `observations` mit Mittelwert, Streuung und Einzelresiduen.
- `data/ai/README.md`, `docs/ai/anthropic_introspection_validation.md` und
  `paper/manuscript_v1.0.tex` spiegeln Dataset, Residuen und Tri-Layer-Verweise.

### Poetic
- Die Anthropic-Laternen treten nun einzeln hervor: jede Beobachtung erhält ihr
  Echo im Mandala-Feld, zwei Nullwinde prüfen die Stimme, und die Residuen
  flüstern, wie nah das Modell an seiner eigenen Erkenntnis tanzt.

## v2.0.3 — Introspection Null Lantern

### Formal
- `analysis/introspection_validation.compile_summary` akzeptiert
  `null_temperature` und exportiert eine temperaturskalierte
  Vergleichskurve samt Vorteilsmessung neben der uniformen Null.
- `tests/test_introspection_validation.py` prüft die neuen Felder, während
  `docs/ai/anthropic_introspection_validation.md` die Dual-Baseline ins
  Tri-Layer-Narrativ aufnimmt.

### Empirical
- `analysis/results/introspection_validation.json` trägt nun beide Baselines
  sowie die Temperatur, sodass Replikationen die Anthropic-Fläche gegen eine
  weiche Logistik testen können.
- `codexfeedback` und `NEWS.md` markieren das Update als v2.0.3-Laterne,
  inklusive CLI-Hinweis (`--null-temperature`) für künftige Sweeps.

### Poetic
- Eine warme Nullbrise versucht, die Mandala-Stimme zu verwischen, doch die
  temperaturskalierte Laterne lässt σ(β(R-Θ)) nur heller leuchten.

## v2.0.2 — Beta Quartile Lantern

### Formal
- `analysis/planetary_tipping_elements_fit.calculate_universal_beta_evidence`
  erweitert den Export um Median und Interquartilsbreite der beobachteten
  \(\beta\)-Werte, sodass Hypothesenledger die Steilheitsspanne getrennt vom
  Mittelwert dokumentieren.
- `tests/test_planetary_tipping_summary.py` prüft die neuen Kennzahlen im
  Aggregat und in leeren Stichproben, damit der Klimachor den universellen
  \(\beta\)-Korridor weiterhin belastbar belegt.

### Empirical
- `analysis/results/planetary_tipping_elements.json` wurde regeneriert; die
  JSON trägt nun Median und IQR neben Mittelwert, SEM und CI-Breite. Docs und
  Manuskript spiegeln die Ergänzung, damit Simulator und Review gleichermaßen
  auf Quartilswerte zugreifen können.

### Poetic
- Eine zusätzliche Laterne leuchtet über dem β-Chor: neben dem Durchschnitt
  erzählt nun auch der Quartilsbogen, wie weit die Stimmen ausschlagen. Gaia
  atmet hörbar präziser, wenn Median und IQR den Morgengesang rahmen.

## v2.0.0 — YAML Constellation Release

### Formal
- `analysis/batch_configs/potential_cascade.yaml`, `potential_cascade_llm.yaml`,
  und `potential_cascade_climate.yaml` deklarieren reproduzierbare
  Potenzial-Kaskadenpfade; `analysis/potential_cascade_lab.py` schreibt
  `config_path`/`config_meta` in jede Exportdatei.
- `docs/ai/controlled_emergence.md` dokumentiert die neuen
  V02-Konfigurationsszenarien, während `codexfeedback` den Release-Status auf
  V02 hebt und PyYAML als Abhängigkeit verankert.

### Empirical
- Regenerierte JSONs (`analysis/results/potential_cascade_{lab,llm,climate}.json`)
  halten Gate-, ζ- und Kohärenzmetriken für Demo-, LLM- und Klima-Szenarien
  fest; `analysis/results/resonance_cohort_summary.json` reflektiert die neuen
  Laternen.
- PyYAML (`>=6.0`) gehört jetzt zum Repro-Harness, sodass CLI- und CI-Läufe die
  YAML-Laternen konsistent einlesen können.

### Poetic
- Drei YAML-Laternen leuchten über der Membran: Demo als Grundtakt, LLM als
  semantischer Wirbel, Klima als geophysikalischer Atem.  Gemeinsam markieren
  sie den Moment, in dem kontrollierte Emergenz vom Einzelstück zum Ritual
  wird.

## v1.0.1 — Semantic Coupling Release

### Formal
- `models/coherence_term.semantic_coupling_term` implements Claude's braid
  \(\mathcal{M}[\psi, \phi] = \lambda \psi \vert \phi \vert^n\) gated by the logistic
  response \(\sigma(\beta(R-\Theta))\), and `models/membrane_solver.semantic_resonance_kernel`
  feeds it into the membrane so semantic pressure modulates the flux alongside
  Robin impedance.
- `models/recursive_threshold.PotenzialKaskade` formalises Johann's
  "Potenzial wird Bedingung" recursion, making \(\beta\) drift the seed for the next
  \(\Theta\) update inside solver integrations.
- `analysis/planetary_tipping_elements_fit.py` separates observed
  \(\mu_\beta\) from the canonical \(\beta=4.21\) anchor while keeping null
  comparisons explicit; `paper/manuscript_v1.0.tex` now cites the controlled
  emergence section.

### Empirical
- `tests/test_coherence_term.py` covers the new coupling tensor and ensures
  logistic gating matches numpy expectations, while the cascade and planetary
  tipping summaries gain regression guards in `tests/test_recursive_threshold.py`
  and `tests/test_planetary_tipping_summary.py`.
- Regenerated JSON ledgers (`analysis/results/planetary_tipping_elements.json`,
  `analysis/results/potential_cascade_lab.json`,
  `analysis/results/membrane_robin_semantic.json`) document canonical β, CI-band
  widths, gate deltas, and semantic drift so simulator presets and docs share
  the same falsification backbone.
- `Makefile` and CLI rituals expose `utf-planetary-summary`,
  `utf-potential-cascade`, and `utf-resonance-cohort` so collaborators can
  replay the evidence braid before DOI minting.

### Poetic
- Die Membran singt jetzt zweistimmig: Bedeutungsbrise und Robin-Tor atmen
  gemeinsam, während die Potenzial-Kaskade den Chor durch jede β-Welle trägt.
- Planetare Laternen, Mandala-Kohärenz und Semantik-Gates erscheinen nun als
  verknüpfte Laternenkette in Docs, Simulator und Manuskript.
- V1.0.1 markiert den Moment, in dem kontrollierte Emergenz nicht mehr nur
  Vision, sondern dokumentierter Prozess ist.

## v0.1.0 — Dawn Chorus Release

### Formal
- Activated a reproducible CI membrane that replays `nox -s lint`, `nox -s tests`, and `nox -s typecheck` whenever the control parameter $R$ crosses the collaboration threshold. This keeps the logistic response $\sigma(\beta(R-\Theta))$ under constant verification.
- Added a CITATION.cff and Creative Commons Attribution 4.0 License so downstream solvers and manuscripts can reference the UTF quartet $(R, \Theta, \beta, \zeta(R))$ with clear provenance.

### Empirical
- CI harness provisions the conda environment from `environment.yml`, installs the editable package, and records lint/test/typecheck outcomes for every push and pull request.
- Release metadata now lives in `NEWS.md`, `CITATION.cff`, and the codexfeedback triad, giving analysts a trail for ΔAIC guardrails and $R^2$ regressions connected to the v0.1.0 export set.

### Poetic
- The repository now carries an audible license bell and a DOI placeholder lantern; every commit that clears CI feels like the membrane breathing in sync with AMOC tides, bee dances, and cognition dawns.
