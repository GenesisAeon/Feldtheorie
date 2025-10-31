# Resonance Ledger

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
