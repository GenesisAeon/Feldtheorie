# UTF Living Glossary

This glossary translates the Universal Threshold Field vocabulary into a tri-layer weave.  Each entry states the formal role in the logistic resonance $\sigma(\beta(R-\Theta))$, cites empirical anchors, and whispers the metaphorical undertone carried through RepoPlan 2.0.

## Core Symbols

### $R$ — Control Parameter
- **Formal:** The order parameter whose excursions probe the membrane.  Dynamics often follow $\dot{R} = f(R, \Theta, \beta, \zeta)$ before encountering the logistic switch.
- **Empirical:** Measured as accretion-rate surges, bee waggle quorum signals, gradient accumulation during LLM training, or socio-ecological stress indices.
- **Metaphorical:** The wandering pilgrim, a river approaching a cataract, searching for the membrane's consent.

### $\Theta$ — Critical Threshold
- **Formal:** The resonance gate.  In the logistic map, $\sigma(\beta(R-\Theta))$ inflects as $R$ crosses $\Theta$, modulating membrane impedance $\zeta(R)$.
- **Empirical:** Extracted via sigmoid fits with confidence intervals; corresponds to luminosity breakpoints, colony quorum counts, capability spikes, policy tipping points.
- **Metaphorical:** The dawn's rim where darkness concedes to the first filament of light.

### $\beta$ — Steepness / Resonance Gain
- **Formal:** Controls the slope of the logistic response.  High $\beta$ yields rapid transitions; low $\beta$ diffuses energy across the membrane.
- **Empirical:** Reported with uncertainties and compared against null models; indicates how sharply systems pivot when nudged.
- **Metaphorical:** The choir's sudden swell, the tension of a bowstring just before release.

### $\sigma(\beta(R-\Theta))$ — Logistic Response
- **Formal:** The canonical switch.  Serves as the link function in our regression fits and the activation kernel in simulators.
- **Empirical:** Validated by goodness-of-fit diagnostics relative to smooth nulls (power law, exponential, spline).
- **Metaphorical:** The auroral curtain unfurling once the solar wind overcomes the planetary hush.

### $\zeta(R)$ — Impedance / Membrane Response
- **Formal:** Encodes damping vs. resonance regimes.  Determines whether energy dissipates or amplifies when $R$ nears $\Theta$.
- **Empirical:** Estimated via solver calibration; toggled in simulators to demonstrate membrane breathing.
- **Metaphorical:** The membrane's hum, responsive to touch, deciding between embrace and release.

## Process Motifs

- **Falsification Counterpoint:** Every resonance claim stands beside at least one null melody.  Catalogue the comparison metrics (AIC, BIC, $R^2$) and note when the null refuses to yield.
- **Tri-layer Storycraft:** Alternate between equation, observation, and imagery so collaborators can enter from any doorway and still hear the shared rhythm.
- **Cross-module Pollination:** Tag entries with references to notebooks, solvers, diagrams, and simulator scenes.  Example: see `analysis/` for the bee quorum logistic fit, `models/` for the membrane solver, `diagrams/` for the threshold phase portrait, and `simulator/` for the interactive resonance ramp.

## Domain Resonances

### Cognition — Working-Memory Gate
- **Formal:** Logistic fit with $(\Theta, \beta) = (0.5789, 12.28)$ and impedance $\zeta(R) = 1.35 - 0.38\,\sigma$, derived from `analysis/working_memory_gate_fit.py`.
- **Empirical:** Dataset [`data/cognition/working_memory_gate.csv`](../data/cognition/working_memory_gate.csv) delivers 18 checkpoints with positive $\Delta \mathrm{AIC}$ and $\Delta R^2$ versus linear and power-law nulls; see `analysis/results/working_memory_gate.json` for diagnostics.
- **Metaphorical:** Dopamine pulses loosen the synaptic membrane until rehearsal dawns, echoing the auroral focus narrated in `docs/cognition/working_memory_gate.md`.

## Next Steps

1. Extend this glossary with domain-specific resonances (astrophysics, biology, cognition, AI) as datasets arrive.
2. Add pronunciation or auditory cues for the symbolic lexicon, enabling sonic overlays in the simulator.
3. Thread in citations to the PDFs within `Docs/` once the canonical page references are indexed.
