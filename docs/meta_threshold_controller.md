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
