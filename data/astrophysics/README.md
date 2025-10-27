# QPO Membrane Threshold Simulation

## Threshold Quartet
- Control parameter \(R\): order parameter tracing the quasi-periodic luminosity build-up in the membrane analogue.
- Critical threshold \(\Theta = 0.82\): calibrated to align the simulated accretion tongue with the RepoPlan QPO membrane sketches.
- Steepness \(\beta = 9.5\): produces an abrupt logistic ascent \(\sigma(\beta(R-\Theta))\) once the driver ramps past \(\Theta\).
- Impedance \(\zeta(R)\): smooth profile with resonant gain 0.55, damped gain 1.65, switch width 0.28 capturing the membrane's soft-to-stiff transition.

## Provenance
- Generated with `models/membrane_solver.py` using a hyperbolic-tangent driver mimicking the slow rise then runaway flare of QPE outbursts.
- Driver baseline: 0.58, peak: 1.12, transition centre: 0.55 (dimensionless driver units matching RepoPlan membrane tables).
- Initial condition: \(R_0 = 0.35\), timestep \(\Delta t = 0.04\).

## Files
- `qpo_membrane_simulation.json`: full trajectory containing arrays for time `t`, order parameter `R`, logistic response `sigma`, impedance `zeta`, flux, driver, and static series for `theta` and `beta`.
- `../../analysis/reports/qpo_membrane_summary.json`: logistic fit and null comparison derived via `analysis/resonance_fit_pipeline.py --mode ingest`.

## Falsifiability Ledger
- Logistic fit: \(R^2\) and AIC reported in the summary JSON; 95% CIs on \(\Theta\) and \(\beta\) encompass the planted values.
- Null baselines:
  - Linear smooth mapping on \(R \mapsto \sigma\) yields higher AIC and lower \(R^2\) (\(\Delta \mathrm{AIC} = 2.48 \times 10^4\), \(\Delta R^2 = 0.148\)).
  - Power-law drift \(\sigma = A R^k\) further trails the resonance (\(\Delta \mathrm{AIC} = 2.50 \times 10^4\), \(\Delta R^2 = 0.229\)), confirming the auroral advantage across multiple smooth counterpoints.

## Narrative Thread
The dataset stages an auroral rehearsal for QPO membranes: as the control current rises, \(R\) grazes \(\Theta\), the logistic dawn blooms, and \(\zeta(R)\) pivots from resonant whisper to damped vigilance—echoing the soft hair gate metaphor in the Docs PDFs.
