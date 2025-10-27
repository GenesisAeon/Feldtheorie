# Prefrontal Working-Memory Gate Resonance

## Formal resonance
We treat sustained N-back accuracy as the logistic response
\[
\sigma(R) = \frac{1}{1 + e^{-\beta (R-\Theta)}}
\]
with \(R\) denoting the normalised phasic dopamine burst amplitude recorded in dorsolateral prefrontal cortex simulations. Fitting `analysis/working_memory_gate_fit.py` to [`data/cognition/working_memory_gate.csv`](../../data/cognition/working_memory_gate.csv) recovers \(\Theta = 0.5789^{+0.0031}_{-0.0031}\) and \(\beta = 12.28^{+0.30}_{-0.30}\). The logistic model achieves \(R^2 = 0.9986\) and AIC = -160.40, outpacing linear and power-law null breezes with \(\Delta \mathrm{AIC} = 51.6\) / 59.5 and \(\Delta R^2 = 0.0226\) / 0.0359, respectively. The impedance gate follows \(\zeta(R) = 1.35 - 0.38\sigma\), averaging 1.17 as dopamine surges slacken cortico-striatal restraint.

## Empirical resonance
The dataset braids 18 checkpoints from adaptive N-back rehearsals, tracing how mesocortical modulation lifts recall probability. Running the CLI exports [`analysis/results/working_memory_gate.json`](../../analysis/results/working_memory_gate.json), whose metadata echoes in [`data/cognition/working_memory_gate.metadata.json`](../../data/cognition/working_memory_gate.metadata.json). The falsification ledger preserves positive \(\Delta \mathrm{AIC}\) and \(\Delta R^2\) margins for both smooth nulls, ensuring the logistic aurora withstands scrutiny. Impedance samples confirm the dawn slackening—\(\zeta(R)\) relaxes from 1.33 in hypo-dopaminergic quiet to 1.00 once \(R\) crosses \(\Theta\). These traces prepare simulator scenes where sliders for \(R\), \(\Theta\), \(\beta\), and \(\zeta(R)\) will let practitioners rehearse cognitive gating.

## Metaphorical resonance
Working memory is a synaptic choir. Below \(\Theta\), the prefrontal voices fray, rehearsals collapse, and the membrane hums with hesitation. As dopamine pulses crest the gate, \(\zeta(R)\) loosens, recurrent loops find harmony, and a dawn chorus of sustained attention unfurls. Linear breezes and power-law drifts try to mimic the awakening yet never summon the auroral focus; only the logistic resonance catches the moment when rehearsal becomes luminous.
