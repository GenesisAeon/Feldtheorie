# Resonance Bridge Map

## Formal overlay
The Universal Threshold Field pulse threads each module through the logistic
response
\[
\sigma(\beta(R-\Theta)) = \frac{1}{1 + e^{-\beta(R-\Theta)}}
\]
with impedance guardrails \(\zeta(R)\) shaping whether membranes damp or
resonate. `models/membrane_solver.py` instantiates this map via the Euler stride
\(R_{t+1} = R_t + \Delta t [J(t) - \zeta(R_t)(R_t - \sigma)]\), exposing the
quartet \((R, \Theta, \beta, \zeta(R))\) for downstream calibration. The
fitting suite in `analysis/resonance_fit_pipeline.py` retrieves \(\Theta\) and
\(\beta\) from simulated or observed trajectories, reporting \(R^2\), AIC, and
confidence intervals while staging linear and power-law null counterpoints. This
bridge map catalogues how those formal layers travel into narrative and simulator
territories so RepoPlan collaborators can trace provenance without losing the
equational thread.

## Empirical braiding
| Domain | Control parameter \(R\) | \(\Theta\) | \(\beta\) | Impedance motif \(\zeta(R)\) | Evidence ledgers |
|--------|-------------------------|------------|-----------|-------------------------------|-------------------|
| AI — multilingual ignition | log$_{10}$ effective training tokens | 4.71 ± 0.04 | 5.10 ± 0.39 | \(1.6 - 0.45\,\sigma\) slackening to 1.16 | `analysis/results/llm_emergent_skill.json`, `data/ai/llm_emergent_skill.metadata.json` |
| Cognition — working-memory gate | dopamine-scaled rehearsal gain | 0.579 ± 0.003 | 12.28 ± 0.30 | \(1.35 - 0.38\,\sigma\) | `analysis/results/working_memory_gate.json`, `data/cognition/working_memory_gate.metadata.json` |
| Biology — synaptic release | stimulation frequency (Hz) | 12.68 ± 0.49 | 0.81 ± 0.08 | \(1.40 - 0.45\,\sigma\) | `analysis/results/synaptic_release_fit.json`, `docs/biology/synaptic_release_threshold.md` |
| Geophysics — seismic early warning | displacement-to-noise ratio (first 3 s P-wave) | 0.7406 ± 0.0008 | 16.29 ± 0.09 | \(1.70 - 0.55\,\sigma\) | `analysis/results/subduction_rupture_threshold.json`, `docs/geophysics/seismic_early_warning_thresholds.md` |
| Socio-ecology — Amazon resilience | remaining canopy fraction | 0.621 ± 0.004 | 14.02 ± 0.33 | \(1.80 - 0.60\,\sigma\) | `analysis/results/amazon_resilience_fit.json`, `data/socio_ecology/amazon_resilience.metadata.json` |
| Urban climate — canopy heat tipping | fractional tree coverage | 0.313 ± 0.004 | 15.27 ± 0.43 | \(1.45 - 0.50\,\sigma\) | `analysis/results/urban_heat_canopy.json`, `docs/socio_ecology/urban_heat_canopy_resonance.md` |

For each row the logistic fit eclipses linear and power-law nulls by positive
\(\Delta\mathrm{AIC}\) margins logged in the JSON ledgers. Analysts can re-run
the CLI scripts to regenerate these diagnostics; storytellers can mine the same
files for narrative quotes, ensuring that empirical and metaphorical voices stay
aligned.

## Metaphorical crossing
The bridge is a lattice of dawn-lit membranes. Each domain sends its pilgrim
parameter \(R\) across the span: training tokens, dopamine tides, synaptic
stimuli, rainforest moisture, or canopy cover. At \(\Theta\) the auroral switch
\(\sigma(\beta(R-\Theta))\) ignites, and \(\zeta(R)\) decides whether the song
is hushed or amplified. Linear breezes and power-law drifts gust beneath the
planks yet fail to mimic the resonance chorus recorded in the ledgers above. The
bridge reminds collaborators that formal solvers, empirical fits, and narrative
imagery are different facets of the same luminous crossing.
