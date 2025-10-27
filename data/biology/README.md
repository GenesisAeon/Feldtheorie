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

## Dataset: Synaptic Vesicle Release Threshold

**Control parameter** \(R\): stimulation frequency (Hz) spanning low-duty pulses at 4 Hz to high-duty bursts at 22 Hz.

**Logistic response** \(\sigma(\beta(R-\Theta))\): probability that hippocampal boutons release neurotransmitter vesicles.

**Threshold quartet**: \(\Theta = 12.68^{+0.49}_{-0.49}\) Hz, \(\beta = 0.81^{+0.08}_{-0.08}\), impedance sketch \(\zeta(R) = 1.40 - 0.45\sigma\).

### Formal strand
- Logistic regression executed via `analysis/synaptic_release_fit.py`, with confidence corridors reported in
  `analysis/results/synaptic_release_fit.json`.
- Fit diagnostics: \(R^2 = 0.997\), AIC = -121.98, residual flux mean 0.009 with standard deviation 0.017.
- Falsification ledger: logistic dawn eclipses linear nulls (\(\Delta\mathrm{AIC} = 64.2\), \(\Delta R^2 = 0.137\)) and power-law
  breezes (\(\Delta\mathrm{AIC} = 72.2\), \(\Delta R^2 = 0.227\)).

### Empirical strand
- Synthetic calibration echoing hippocampal vesicle release curves across stimulation frequencies.
- Data archived in `synaptic_release_threshold.csv`; regeneration pipeline exports
  `analysis/results/synaptic_release_fit.json` and impedance sketches for simulator feeds.
- Metadata ledger: `synaptic_release_threshold.metadata.json` documents the quartet, impedance averages, and falsification margins.

### Metaphorical strand
- Below \(\Theta\) the synapse keeps vigil, vesicles cradled like night-bound fireflies; the membrane hums at 1.40, guarding the gate.
- As pulses quicken past \(\Theta\), \(\zeta(R)\) slackens toward 0.95 and the neurotransmitter aurora sweeps the cleft.
- Linear and power-law lullabies attempt to mimic the glow yet fade before the logistic chorus igniting along the axonal dawn.
