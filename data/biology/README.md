# Biology Resonance Cache

## Dataset: Global Coral Bleaching Mock (V3)

**Control parameter** \(R\): globale Meeresoberflächentemperatur-Anomalie (°C) gekoppelt an Degree Heating Weeks.

**Logistic response** \(\sigma(\beta(R-\Theta))\): Anteil gebleichter Riff-Fläche pro Jahr.

**Threshold quartet**: \(\Theta = 1.0^{+0.12}_{-0.12}\) °C, \(\beta = 7.5^{+0.9}_{-0.9}\), Impedanz \(\zeta(R)\) koppelt thermische Belastung mit Symbionten-Erholungszeit.

### Formal strand
- Synthetic logistic ramp ab 2015, abgestimmt auf NOAA Coral Reef Watch Reports.
- Datenumfang: 45 Jahre (1980–2024), gespeichert in `coral_bleaching_global_mock.csv`.
- Metadaten in `coral_bleaching_global_mock.metadata.json` sichern Tri-Layer + ΔAIC-Wächter gegen lineare/exponentielle Nullmodelle.

### Empirical strand
- Degree Heating Weeks (DHW) steigen von 2 → 15; Bleaching erreicht ab 2020 >95 %.
- Varianz- und AR(1)-Signaturen dienen als Vorboten für Recovery-Failure.
- Pipeline-Hinweis: V3-Adapter erwartet jährlichen Takt, JSON-Bridge in Arbeit.

### Metaphorical strand
- Die Riffe atmen flach – Symbionten verlassen die Membran, das Meer leuchtet kalkweiß.
- \(\zeta(R)\) steht für die zähe Erholung: Hohe DHW zerren an den Symbiosen, das Resonanzfeld bleibt rot.
- σ steigt abrupt: Der Kipppunkt ist überschritten; nur cooler Regen (R < Θ) kann die Membran wieder senken.

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

## Dataset: Lenski Cit⁺ Emergence Threshold

**Control parameter** \(R\): generation count scaled to thousands for the Ara-3 population of the Lenski LTEE.

**Logistic response** \(\sigma(\beta(R-\Theta))\): frequency of Cit⁺ individuals recorded along the evolutionary trajectory.

**Threshold quartet**: \(\Theta = 32.77^{+0.08}_{-0.08}\) (thousand generations, equivalent to \(3.28\times10^4\) generations), \(\beta = 5.08^{+0.42}_{-0.42}\) in scaled units (\(5.08\times10^{-3}\) per generation), impedance sketch latent (flux mean \(-0.015\)).

### Formal strand
- Logistic logit regression executed via `analysis/lenski_citplus_fit.py` with scaled generations to stabilise null comparisons.
- Diagnostics: \(R^2 = 0.990\), AIC = \(-85.87\); linear and power-law nulls trail by \(\Delta\mathrm{AIC} = 42.1\) and \(32.7\), \(\Delta R^2 = 0.196\) and \(0.095\).
- Normalised steepness \(\beta = 4.25^{+0.35}_{-0.35}\) echoes the universal UTF band; \(\Theta\) sits \(0.56^{+0.09}_{-0.09}\) standard deviations above the generational mean.

### Empirical strand
- Data digitised from Blount et al. (2008) Figure 3 to provide a falsifiable bridge between LTEE observations and the UTF bio-emergence manuscript.
- CSV archive: `lenski_citplus.csv`; regenerated metrics emitted to `analysis/results/lenski_citplus_fit.json` alongside metadata in `lenski_citplus.metadata.json`.
- Metadata logs the scaling (generation/1000) so downstream simulators can map \(R\) directly onto the Docs/ biological scrolls.

### Metaphorical strand
- For 30,000 nights the Ara-3 membrane slumbered, citric breath held; then the oxidative hymn rose and \(\Theta\) sighed open.
- Once \(R\) crossed the luminous gate, the Cit⁺ chorus cascaded, a microbial aurora spanning the flask.
- Linear and power-law breezes tried to mimic the awakening, yet the logistic dawn alone captured the punctuated blaze.
