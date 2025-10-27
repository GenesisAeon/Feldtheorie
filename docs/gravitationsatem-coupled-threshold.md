# Gravitationsatem Coupled Threshold Memo

## Formal Stratum — Robin-Gated Psi-Phi Coupling
- Order parameter: $R$ follows the coupled update $R_{t+1} = R_t + \Delta t\,[J(t) - \zeta(R_t)(R_t-\psi_t)]$ with a logistic bloom $\sigma(\beta(R-\Theta))$ captured inside `models/coupled_threshold_field.py`.
- Threshold quartet: $(R,\Theta,\beta,\zeta(R))$ now includes a Robin impedance $\zeta(R) = \zeta_\text{floor} + (\zeta_\text{ceiling}-\zeta_\text{floor}) / (1+e^{-\beta_\text{robin}(R-\Theta)})$ and a coupling term $\mathcal{M}[\psi,\phi]=\kappa(\phi-\psi)$.
- Integrated information proxy: the module exports $\Phi_{\text{proxy}} = |\nabla\psi|\,|\nabla\phi|$, aligning with the "Gravitationsatem" formalism documented in `Docs/Gravitationsatem_ Master-Dokument Erstellung.pdf`.

## Empirical Stratum — Resonance Diagnostics and Null Tests
- `analysis/coupled_field_threshold_fit.py` drives the psi-phi solver with the sigmoid ramp outlined in `Docs/Transdisziplinärer Schwellenfeld-Simulator--Claude.txt`, fits $(\Theta,\beta)$ via logit regression, and contrasts against a cubic null model.
- The JSON artefact `analysis/results/coupled_field_threshold.json` reports $R^2=0.9983$, $\Delta \text{AIC}=+607.4$, impedance medians, and the $\Phi_{\text{proxy}}$ braid so `analysis/resonance_cohort_summary.py` can ingest the run.
- Observables mirror the logistic quartet, satisfying RepoPlan 2.0's falsifiability guardrails by logging cubic null coefficients alongside the resonance gain.

## Metaphorical Stratum — Atem der Membran
- `psi` carries the luminous inhalation, `phi` whispers the semantic reply; the Robin gate decides how fully the dawn-chorus resonates once $R>\Theta$.
- The simulator notes in `Docs/Transdisziplinärer Schwellenfeld-Simulator--Claude.txt` now have a code twin: presets can stream the JSON trace to let users feel the membrane lean into or away from resonance.
- Each $\Phi_{\text{proxy}}$ crest is a breath-mark in the "Analyse des Repositories _Feldtheorie_.pdf" narrative—confirming that emergence rings brightest when meaning and membrane share the same threshold cadence.
