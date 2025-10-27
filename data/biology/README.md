# Biology Resonance Cache

## Dataset: Honeybee Waggle Activation Threshold

**Control parameter** \(R\): nectar sucrose concentration (degrees Brix) sampled from 18–31.

**Logistic response** \(\sigma(\beta(R-\Theta))\): probability that a forager recruits nestmates via the waggle dance.

**Threshold quartet**: \(\Theta = 26.58^{+0.75}_{-0.75}\) Brix, \(\beta = 0.67^{+0.13}_{-0.13}\), impedance sketch \(\zeta(R) = 1.25 - 0.35\sigma\).

### Formal strand
- Logistic regression on the logit domain using `analysis/honeybee_waggle_fit.py`.
- Confidence intervals from the Fisher information approximation; \(R^2 = 0.969\), AIC = -73.55.
- Falsification: logistic model beats linear and power-law nulls (ΔAIC > 18, ΔR^2 > 0.08).

### Empirical strand
- Synthetic calibration echoing nectar threshold measurements reported in the honeybee foraging literature.
- Data stored in `honeybee_waggle_activation.csv`; regeneration via the analysis CLI exports `analysis/results/honeybee_waggle_fit.json`.
- Metadata recorded in `honeybee_waggle_activation.metadata.json` for downstream simulators and docs.

### Metaphorical strand
- Nectar sweetness slackens the membrane until waggle songs blaze across the comb, a dawn chorus crossing \(\Theta\).
- The impedance sketch hums from 1.25 (quiescent night) toward 0.88 (radiant resonance) as the hive consents to dance.
- Null models whisper but fail to drown the aurora; the logistic signal glows unmistakably.

## Cross-links
- Analysis: `analysis/honeybee_waggle_fit.py`
- Narrative: `docs/biology/honeybee_waggle.md`
- Simulator hooks: expose \(R\), \(\Theta\), \(\beta\), and \(\zeta(R)\) sliders in forthcoming UI panels.
