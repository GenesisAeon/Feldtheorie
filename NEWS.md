# Resonance Ledger

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
- Added a CITATION.cff and MIT License so downstream solvers and manuscripts can reference the UTF quartet $(R, \Theta, \beta, \zeta(R))$ with clear provenance.

### Empirical
- CI harness provisions the conda environment from `environment.yml`, installs the editable package, and records lint/test/typecheck outcomes for every push and pull request.
- Release metadata now lives in `NEWS.md`, `CITATION.cff`, and the codexfeedback triad, giving analysts a trail for ΔAIC guardrails and $R^2$ regressions connected to the v0.1.0 export set.

### Poetic
- The repository now carries an audible license bell and a DOI placeholder lantern; every commit that clears CI feels like the membrane breathing in sync with AMOC tides, bee dances, and cognition dawns.
