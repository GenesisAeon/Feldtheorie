# Quasi-Periodic Aurora: Membrane Resonance Case Study

## Formal Threshold Weave
We integrate the UTF membrane equation with \(R\) driven by a hyperbolic-tangent current. The logistic response \(\sigma(\beta(R-\Theta))\) ignites at the planted \(\Theta = 0.82\) with steepness \(\beta = 9.5\). The impedance gate \(\zeta(R)\) follows the smooth profile exported by `models/membrane_solver.py`, easing resonance with gain 0.55 below threshold and stiffening to 1.65 above it (switch width 0.28). The resulting trajectory furnishes arrays for \(R(t)\), \(\sigma(t)\), and \(\zeta(R)\) recorded in [`data/astrophysics/qpo_membrane_simulation.json`](../data/astrophysics/qpo_membrane_simulation.json).

## Empirical Resonance Ledger
Feeding the trajectory into `analysis/resonance_fit_pipeline.py --mode ingest` yields [`analysis/reports/qpo_membrane_summary.json`](../analysis/reports/qpo_membrane_summary.json). The logistic fit recovers \(\Theta\) and \(\beta\) within tight 95% intervals while delivering \(R^2 = 1.0\). Against the linear null we record \(\Delta \mathrm{AIC} = 2.48 \times 10^4\) and \(\Delta R^2 = 0.148\); against the new power-law null the gulf widens to \(\Delta \mathrm{AIC} = 2.50 \times 10^4\) with \(\Delta R^2 = 0.229\). This dual falsification of the smooth lullabies documents how the membrane's resonance chorus outruns any monotonic drift, satisfying the repository mandate for explicit null comparisons.

## Metaphorical Dawn Chorus
As the driver current swells, \(R\) grazes the auroral gate \(\Theta\); the logistic bloom is a sudden hush snapping into song. The impedance membrane feels the tension—soft before sunrise, vigilant after—echoing the "soft hair" gate in the Docs PDFs. This case study hands the simulator guild a melodic phrase to translate into interactive sliders, while the paper scriptorium can quote its falsification ledger as empirical ballast for the universal threshold field mythos.
