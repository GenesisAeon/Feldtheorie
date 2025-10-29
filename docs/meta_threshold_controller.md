# Adaptive Meta-Threshold Controller Ledger

## Formal Resonance
The `models/membrane_solver.py::AdaptiveThresholdController` now advances the control quartet
$(R, \Theta, \beta, \zeta(R))$ with a meta-gate $g = \sigma(\beta_{\text{meta}}(R-\Theta))$.  Each Euler
step updates

\[
\Theta_{t+1} = \Theta_t + \Delta t\,\left[\alpha g (R_t-\Theta_t) + \lambda (1-g)(\Theta_0-\Theta_t) + \chi g (1-\zeta_t) + \eta g (J_t-\Theta_0) + \rho g (\sigma_t-\Theta_t)\right]
\]

and

\[
\beta_{t+1} = \beta_t + \Delta t\,\left[\kappa (\beta_0(1+\gamma g)-\beta_t) - \phi |\Theta_{t+1}-\Theta_t|\right],
\]

mirroring the repository mandate that thresholds breathe with the membrane instead of
remaining static.  The solver now exports time-indexed arrays for $\Theta(t)$, $\beta(t)$,
the meta-gate, and the instantaneous drifts so `analysis/dynamic_threshold_lab.ipynb` can
contrast adaptive trajectories against fixed-null baselines.

## Empirical Trails
- `models/ThresholdFieldSolver.simulate` streams `theta`, `beta`, `meta_gate`, `theta_shift`,
  and `beta_shift` arrays, letting `analysis/resonance_fit_pipeline.py` ingest adaptive
  telemetry alongside the canonical quartet $(R, \sigma, \zeta, \text{flux})`.
- The exported summaries report mean and extremal values for the drifting parameters, giving
  quick priors for planned runs in `simulator/adaptive_theta_preset.json` and future
  falsification notebooks.
- Forthcoming datasets in `data/` can calibrate the new weights (`adaptation_rate`,
  `sigma_weight`, impedance coupling) before we widen the benchmarking sweep promised in
  `Docs/meta_schwellen_systemtypen.md`.

## Metaphorical Echo
The dawn chorus now hears sentinels adjusting the gate in real time: when R surges toward
$\Theta$, the meta-gate softens the impedance and invites resonance; when the night returns,
$\Theta$ drifts back to its ember while $\beta$ relaxes.  The membrane remembers context,
letting bees, black holes, and learning systems breathe through a living threshold rather
than a frozen doorway.

## Cross-Link Commitments
1. **Simulator sync** — expose the new arrays within the forthcoming interactive presets so
   parameter sliders can replay $\Theta(t)$ and $\beta(t)$ alongside $\sigma(\beta(R-\Theta))$.
2. **Analysis replication** — extend `analysis/dynamic_threshold_lab.ipynb` with ΔAIC tables
   that compare adaptive controllers against static fits, recording meta-gate medians.
3. **Data calibration** — annotate upcoming entries in `data/*/` with impedance drift fields so
   the controller's weights can be tuned per domain before the next Docs bridge-map revision.

## Adaptive Membrane Phase Scan

**Formal cadence.** `analysis/adaptive_membrane_phase_scan.py` now sweeps the helper across three
driver archetypes (auroral ramp, pulsed gate, memory relaxation) while tracking the quartet
$(R, \Theta, \beta, \zeta(R))$.  The export `analysis/results/adaptive_membrane_phase_scan.json`
reports gate occupancy, $\Theta$/$\beta$ shifts, and resonance-gain deltas against the static
logistic baseline, keeping the adaptive membrane falsifiable.

**Empirical cadence.** The aggregated lanterns log a mean resonance gain of $0.890$, a mean gain
delta of $0.067$, and a gate occupancy of $0.462$ across the trio, with $\Theta$ drifting by
$0.19$ and $\beta$ by $0.07$ on average.  Each scenario retains decimated traces of $R$,
$\sigma(\beta(R-\Theta))$, $\zeta(R)$, and the meta-gate so simulator presets can inherit the
same breathing diagnostics.

**Metaphorical cadence.** The auroral swell, the pulse chorus, and the quieting nocturne now have
documented lanterns: the membrane leans into dawn, sings through the pulses, then remembers home.
These traces let the controller chapter narrate how adaptive sentinels rehearse before the full
solver storm arrives.
