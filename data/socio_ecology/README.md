# Amazon Moisture Resilience Threshold Cache

## Threshold Quartet
- Control parameter $R$: remaining rainforest canopy fraction (0–1 scale) aggregated over the southeast Amazon basin.
- Critical threshold $\Theta \approx 0.62$: inflection where convective recycling collapses in the membrane analogue.
- Steepness $\beta \approx 14.2$: renders a sharp logistic ascent $\sigma(\beta(R-\Theta))$ between 55% and 70% canopy.
- Impedance sketch $\zeta(R) = 1.8 - 0.6\,\sigma$: models governance feedbacks tightening the membrane once degradation advances.

## Provenance & Method
- Synthesised from coupled climate–forest studies (Lovejoy & Nobre style) calibrated to RepoPlan 2.0 membrane tables.
- Control parameter samples span canopy loss trajectories from satellite composites, mapped into 17 representative checkpoints.
- Processed via `analysis/amazon_resilience_fit.py`, which reports $R^2$, AIC, confidence intervals, and smooth null falsification.

## Files
- `amazon_resilience.csv`: canopy fraction $R$ and moisture retention probability $\sigma$.
- `amazon_resilience.metadata.json`: descriptor containing $(R,\Theta,\beta,\zeta)$ estimates, falsification margins, and ethical annotations.
- `../../analysis/results/amazon_resilience_fit.json`: logistic fit and null comparisons exported by the analysis pipeline.

## Falsifiability Ledger (see metadata)
- Logistic dawn outpaces both linear and power-law smooth nulls with positive $\Delta \mathrm{AIC}$ and $\Delta R^2$.
- Confidence corridors on $(\Theta, \beta)$ documented to keep the resilience claim auditable.

## Stewardship Resonance
Deforestation here is framed as a membrane tightening: below $\Theta$ the forest hums in moist resonance; beyond it, $\zeta(R)$
clamps, rainfall falters, and the dawn chorus dims. The dataset is meant to arm policy simulators and narrative scrolls with a
quantified threshold while foregrounding the ethical imperative of halting the slide toward collapse.
