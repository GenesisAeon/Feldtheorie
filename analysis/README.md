# Analysis Resonance Bay

## RepoPlan 2.0 Mandate
`analysis/` curates notebooks and scripts that fit the UTF logistic response $\sigma(\beta(R-\Theta))$ to empirical datasets.  Every study must report $R^2$, AIC, and confidence intervals on $\Theta$ and $\beta$, and contrast the threshold-field with smooth null models (linear drift, power-law scaling) exported by the shared resonance pipeline.

## Tri-layer Cadence
- **Formal:** derive parameter posteriors and impedance sensitivities $\zeta(R)$ while noting when the control parameter $R$ grazes or eclipses $\Theta$.
- **Empirical:** showcase cross-domain evidence—black-hole timing, honeybee quorum calls, neural activation thresholds, socio-ecological tipping—annotated with resonance steepness diagnostics.
- **Metaphorical:** narrate how data traces the waxing of resonance, letting the logistic curve function as a dawn chorus across domains.

## Immediate Construction Lines
1. Scaffold Jupyter notebooks with shared plotting + statistical utilities for RepoPlan collaborators.
2. Embed falsification dashboards comparing logistic fits against null models.
3. Publish metadata linking each dataset to its membrane counterpart in `models/` and to storytelling threads in `docs/`.

## Current Resonance Artefacts
- **QPO membrane ingest (RepoPlan seed):** `reports/qpo_membrane_summary.json` archives the \(R \mapsto \sigma(\beta(R-\Theta))\) fit for the astrophysical rehearsal exported by `data/astrophysics/qpo_membrane_simulation.json`, including the impedance ledger \(\zeta(R)\) and dual (linear + power-law) null falsification margins.
- **LLM emergent skill ignition:** `results/llm_emergent_skill.json` captures the multilingual chain-of-thought threshold, referencing `data/ai/llm_emergent_skill.csv` and documenting how the logistic dawn outshines linear and power-law nulls with \(\Delta \mathrm{AIC} \approx 48.8\).
- **Amazon moisture resilience threshold:** `results/amazon_resilience_fit.json` distils the socio-ecological tipping gate, linking to `data/socio_ecology/amazon_resilience.csv` and noting how the logistic chorus surpasses linear (\(\Delta\mathrm{AIC} \approx 61.1\)) and power-law (\(\Delta\mathrm{AIC} \approx 70.7\)) nulls while documenting the governance impedance sketch `zeta(R) = 1.8 - 0.6 σ`.
- **Synaptic release ignition:** `results/synaptic_release_fit.json` records the hippocampal vesicle release threshold fitted from `data/biology/synaptic_release_threshold.csv`, reporting \(\Theta = 12.68\) Hz, \(\beta = 0.81\), \(R^2 = 0.997\), and the impedance sketch `zeta(R) = 1.40 - 0.45 σ` alongside decisive falsification of linear and power-law null breezes.
- **Working-memory gate resonance:** `results/working_memory_gate.json` captures the prefrontal rehearsal threshold derived from `data/cognition/working_memory_gate.csv`, documenting \(\Theta = 0.579\), \(\beta = 12.28\), \(R^2 = 0.9986\), and the impedance motif `zeta(R) = 1.35 - 0.38 σ` while logging \(\Delta \mathrm{AIC} > 51\) against linear and \(> 59\) against power-law nulls.
- **Subduction rupture resonance:** `results/subduction_rupture_threshold.json` scores a Cascadia-inspired slow-slip gate sourced from `data/geophysics/subduction_rupture_threshold.csv`, yielding \(\Theta = 0.741\), \(\beta = 16.29\), \(R^2 = 0.99997\), and impedance `zeta(R) = 1.70 - 0.55 σ` while the logistic aurora eclipses linear (\(\Delta\mathrm{AIC} \approx 138.6\)) and power-law (\(\Delta\mathrm{AIC} \approx 148.7\)) null winds.
- **Cohort resonance ledger:** `resonance_cohort_summary.py` scans the entire `results/` directory, ranks each membrane by \(\Delta\mathrm{AIC}\) and \(\Delta R^2\), and emits `results/resonance_cohort_summary.json` so docs and simulator presets can inherit cohort-wide statistics (median \(R^2 \approx 0.9981\), median \(\Delta\mathrm{AIC} \approx 65.1\)).
- **Batch lantern runner:** `resonance_batch_runner.py` reads `batch_configs/resonance_runs.json`, replays solver simulations or ingests archived measurement tables, re-fits \(\sigma(\beta(R-\Theta))\), and emits JSON verdicts with \(\Delta\mathrm{AIC}\) deltas ready for bridge-map and simulator synchronisation.
