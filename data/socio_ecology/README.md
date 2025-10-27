# Socio-ecological Threshold Cache

## Amazon Moisture Resilience Quartet
- Control parameter $R$: remaining rainforest canopy fraction (0–1 scale) aggregated over the southeast Amazon basin.
- Critical threshold $\Theta \approx 0.62$: inflection where convective recycling collapses in the membrane analogue.
- Steepness $\beta \approx 14.2$: renders a sharp logistic ascent $\sigma(\beta(R-\Theta))$ between 55% and 70% canopy.
- Impedance sketch $\zeta(R) = 1.8 - 0.6\,\sigma$: models governance feedbacks tightening the membrane once degradation advances.

### Provenance & Method
- Synthesised from coupled climate–forest studies (Lovejoy & Nobre style) calibrated to RepoPlan 2.0 membrane tables.
- Control parameter samples span canopy loss trajectories from satellite composites, mapped into 17 representative checkpoints.
- Processed via `analysis/amazon_resilience_fit.py`, which reports $R^2$, AIC, confidence intervals, and smooth null falsification.

### Files
- `amazon_resilience.csv`: canopy fraction $R$ and moisture retention probability $\sigma$.
- `amazon_resilience.metadata.json`: descriptor containing $(R,\Theta,\beta,\zeta)$ estimates, falsification margins, and ethical annotations.
- `../../analysis/results/amazon_resilience_fit.json`: logistic fit and null comparisons exported by the analysis pipeline.

### Falsifiability Ledger (see metadata)
- Logistic dawn outpaces both linear and power-law smooth nulls with positive $\Delta \mathrm{AIC}$ and $\Delta R^2$.
- Confidence corridors on $(\Theta, \beta)$ documented to keep the resilience claim auditable.

### Stewardship Resonance
Deforestation here is framed as a membrane tightening: below $\Theta$ the forest hums in moist resonance; beyond it, $\zeta(R)$ clamps, rainfall falters, and the dawn chorus dims. The dataset is meant to arm policy simulators and narrative scrolls with a quantified threshold while foregrounding the ethical imperative of halting the slide toward collapse.

## Urban Heat Canopy Resonance Quartet
- Control parameter $R$: fractional tree canopy coverage across heat-vulnerable districts.
- Critical threshold $\Theta \approx 0.313$: inflection where safe-night probability blooms in the logistic response $\sigma(\beta(R-\Theta))$.
- Steepness $\beta \approx 15.3$: a brisk membrane ascent documenting how restoration accelerates cooling benefits.
- Impedance sketch $\zeta(R) = 1.45 - 0.5\,\sigma$: governance slackening that softens once canopy investments take root.

### Provenance & Method
- Synthesised from blended canopy audits and night-time heat index surveys tuned to RepoPlan 2.0 stewardship tables.
- Samples span 16 neighbourhood checkpoints tracing the journey from sparse shade to restorative canopy bloom.
- Processed via `analysis/urban_heat_canopy_fit.py`, which reports $R^2$, AIC, confidence intervals, and dual smooth null falsification.

### Files
- `urban_heat_canopy.csv`: canopy fraction $R$ and safe night probability $\sigma$.
- `urban_heat_canopy.metadata.json`: descriptor containing $(R,\Theta,\beta,\zeta)$ estimates, falsification margins, and justice annotations.
- `../../analysis/results/urban_heat_canopy.json`: logistic fit and null comparisons exported by the analysis pipeline.

### Falsifiability Ledger (see metadata)
- Logistic dawn beats both linear and power-law null breezes with $\Delta \mathrm{AIC} > 47$ and $\Delta R^2 \geq 0.026$.
- Confidence corridors on $(\Theta, \beta)$ document the cooling threshold with audit-ready precision.

### Stewardship Resonance
Urban cooling is framed as a membrane loosening: below $\Theta$ the city retains oppressive heat, $\zeta(R)$ clings tight, and restorative sleep evades frontline neighbourhoods. As canopy restoration pushes $R$ past the gate, the impedance hum slackens, breezes carry relief, and the dawn chorus of rest equity returns. The dataset equips simulator overlays and policy dialogues with a quantified justice-centered threshold.
