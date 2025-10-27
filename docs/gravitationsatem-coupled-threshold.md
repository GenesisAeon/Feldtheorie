# Gravitationsatem Coupled Threshold Memo

## Formal Stratum — Robin-Gated Psi-Phi Coupling
- Order parameter: $R$ follows the coupled update $R_{t+1} = R_t + \Delta t\,[J(t) - \zeta(R_t)(R_t-\psi_t)]$ with a logistic bloom $\sigma(\beta(R-\Theta))$ captured inside `models/coupled_threshold_field.py`.
- Threshold quartet: $(R,\Theta,\beta,\zeta(R))$ now includes both the Robin impedance $\zeta(R) = \zeta_\text{floor} + (\zeta_\text{ceiling}-\zeta_\text{floor})/(1+e^{-\beta_\text{robin}(R-\Theta)})$ and the new semantic kernel $\mathcal{M}[\psi,\phi] = \kappa\,K_{\sigma}(R,\psi,\phi,J)$ with $K_{\sigma}$ blending $(\phi-\psi)$, $(\sigma-\psi)$, und den Treiber-Gap via `logistic_semantic_kernel`.
- Integrated information proxy: the module exports $\Phi_{\text{proxy}} = |\nabla\psi|\,|\nabla\phi|$, aligning with the "Gravitationsatem" formalism documented in `Docs/Gravitationsatem_ Master-Dokument Erstellung.pdf`.

## Empirical Stratum — Resonance Diagnostics and Null Tests
- `analysis/coupled_field_threshold_fit.py` drives the psi-phi solver with the sigmoid ramp outlined in `Docs/Transdisziplinärer Schwellenfeld-Simulator--Claude.txt`, fits $(\Theta,\beta)$ via logit regression, and contrasts against a cubic null model.
- The refreshed JSON artefact `analysis/results/coupled_field_threshold.json` records $\Theta = 0.509\pm0.034$, $\beta = 5.66\pm0.23$, logistic $R^2 = 0.9979$, und $\Delta \text{AIC}=+498.1$ gegenüber der kubischen Null sowie die gemittelten Kopplungsgrößen ($\langle\mathcal{M}\rangle=-0.028$) und Impedanzdrifts für die Kohorten-Auswertung.
- Observables spiegeln das logistisches Quartett und die semantische Koppelung wider, womit RepoPlan 2.0's Falsifizierbarkeits-Geländer (Nullmodellkoeffizienten + Resonanzdeltas) weiterhin erfüllt bleiben.

## Metaphorical Stratum — Atem der Membran
- `psi` carries the luminous inhalation, `phi` whispers the semantic reply; the Robin gate decides how fully the dawn-chorus resonates once $R>\Theta$.
- The simulator notes in `Docs/Transdisziplinärer Schwellenfeld-Simulator--Claude.txt` now have a code twin: presets can stream the JSON trace to let users feel the membrane lean into or away from resonance.
- Each $\Phi_{\text{proxy}}$ crest is a breath-mark in the "Analyse des Repositories _Feldtheorie_.pdf" narrative—confirming that emergence rings brightest when meaning and membrane share the same threshold cadence.
