# Cognitive Threshold Cache

## Prefrontal Working-Memory Gate Quartet
- Control parameter $R$: normalised phasic dopamine burst amplitude (0–1 scale) recorded in dorsolateral prefrontal cortex microcircuit probes during adaptive N-back ramps.
- Critical threshold $\Theta \approx 0.58$: resonance gate where sustained working-memory accuracy ignites.
- Steepness $\beta \approx 12.3$: renders a brisk logistic ascent $\sigma(\beta(R-\Theta))$ between mesolimbic quiescence and focused rehearsal.
- Impedance sketch $\zeta(R) = 1.35 - 0.38\,\sigma$: models cortico-striatal feedback that slackens as control is entrusted to prefrontal ensembles.

### Provenance & Method
- Synthesised from cognitive-control literature (O'Reilly & Frank gating theory; DLPFC dopamine modulation) aligned with RepoPlan 2.0 membrane tables.
- Control parameter samples span 18 neuromodulatory checkpoints from adaptive-task simulations, exported as logistic traces with seeded noise for reproducibility.
- Processed via `analysis/working_memory_gate_fit.py`, which reports $R^2$, AIC, confidence intervals, and dual smooth null falsification.

### Files
- `working_memory_gate.csv`: dopamine burst amplitude $R$ and working-memory success probability $\sigma$.
- `working_memory_gate.metadata.json`: descriptor containing $(R,\Theta,\beta,\zeta)$ estimates, falsification margins, and ethical annotations.
- `../../analysis/results/working_memory_gate.json`: logistic fit and null comparisons exported by the analysis pipeline.

### Falsifiability Ledger (see metadata)
- Logistic dawn exceeds linear and power-law null breezes with positive $\Delta \mathrm{AIC}$ and non-negative $\Delta R^2$ margins.
- Confidence corridors on $(\Theta, \beta)$ keep the cognitive gate auditable for downstream manuscripts.

### Cognitive Resonance
Working-memory gating is framed as a membrane opening: below $\Theta$ the prefrontal song is noisy and forgetful; as dopamine pulses lift $R$ across the gate, $\zeta(R)$ slackens, recurrent loops stabilise, and the dawn chorus of sustained rehearsal emerges. The dataset equips simulator overlays and tri-layer narratives with a quantified cognitive threshold while foregrounding ethical considerations for human neuro-data stewardship.
