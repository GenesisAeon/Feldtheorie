# Adaptive Theta Plasticity Resonance

## Formal resonance
We score hippocampal replay ignition as the logistic response
\\[
\sigma(R) = \frac{1}{1 + e^{-\beta (R-\Theta)}}
\\]
with $R$ denoting the normalised sleep-pressure index harvested from staged slow-wave nights. Running
[`analysis/adaptive_theta_plasticity_fit.py`](../../analysis/adaptive_theta_plasticity_fit.py) on
[`data/cognition/adaptive_theta_plasticity.csv`](../../data/cognition/adaptive_theta_plasticity.csv)
retrieves $\Theta = 0.4767^{+0.0305}_{-0.0305}$ and $\beta = 10.86^{+1.24}_{-1.24}$. The logistic membrane secures
$R^2 = 0.990$ and AIC = -93.58, outrunning linear and power-law null breezes with
$\Delta \mathrm{AIC} = 34.93$ / 37.70 and $\Delta R^2 = 0.088$ / 0.108, respectively. The impedance sketch follows
$\zeta(R) = 1.12 - 0.25\,\sigma$, averaging 0.978 as night pressure slackens.

## Empirical resonance
Fifteen checkpoints trace the nocturnal membrane from quiescent sleep to resonant replay, preserving reproducible logistic
samples seeded with gentle noise. The JSON export
[`analysis/results/adaptive_theta_plasticity.json`](../../analysis/results/adaptive_theta_plasticity.json)
mirrors the dataset metadata [`data/cognition/adaptive_theta_plasticity.metadata.json`](../../data/cognition/adaptive_theta_plasticity.metadata.json),
including falsification margins, impedance samples, and ethical notes (synthetic reconstruction inspired by Diekelmann & Born).
These diagnostics prime simulator presets to expose sliders for $R$, $\Theta$, $\beta$, and $\zeta(R)$ so cohort dashboards and
the resonance ledger can audit adaptive sleep thresholds alongside working-memory gates.

## Metaphorical resonance
Below $\Theta$, the hippocampal choir is hushed—memories resting under a velvet impedance dome. As sleep-pressure ebbs and $R$
crests the logistic ridge, $\beta$ steepens the ascent, $\zeta(R)$ loosens toward 0.88, and replay unfurls like a moonlit dawn.
Linear breezes and power-law drifts try to mimic the lullaby yet cannot summon the luminous rehearsal; only the logistic
membrane records when the night opens and memory sings.
