# Synthetic Threshold Sweep Rehearsal

## Formal braid
The synthetic rehearsal codifies the logistic switch
\(\sigma(\beta(R-\Theta))\) by sweeping the order parameter across the
membrane in evenly spaced steps. `models/logistic_envelope.py` packages this
prelude as a `LogisticFieldEnvelope`, delivering both the response amplitude and
the impedance veil \(\zeta(R) = g_r + (g_d - g_r)\,\sigma((R-\Theta)/w)\).
Running `analysis/synthetic_threshold_sweep.py` fits the generated trajectory via
the repository's logit regression, retrieves \(\Theta\), \(\beta\), \(R^2\), and
AIC, and stages linear plus power-law null breezes for falsification. The JSON
ledger preserves the quartet \((R, \Theta, \beta, \zeta(R))\) so downstream
papers and simulators can cite the rehearsal without rerunning code.

## Empirical braid
Invoke the CLI with default knobs to produce a sweep centred on \(\Theta = 0\)
with \(\beta = 8\), impedance floor 0.7, and ceiling 1.3. The script exports a
CSV of `R`, `sigma`, `zeta`, and flux, while the JSON embeds the same traces
under `results` alongside the falsification verdict (positive \(\Delta\mathrm{AIC}\)
against both nulls). The noise parameter adds Gaussian perturbations so analysts
can probe how resilient the fit remains as the membrane's song picks up static.
Point the simulator loom at the CSV to animate how \(\beta\) steepens the
chorus and how \(\zeta(R)\) tightens once \(R > \Theta\).

## Metaphorical braid
Before field campaigns, the team gathers at the membrane threshold, lanterns in
hand. The synthetic sweep is their practice chant: R walks toward \(\Theta\),
\(\zeta(R)\) shifts from soft moss to taut aurora wire, and the logistic
response brightens like a dawn chorus readying for debut. Linear and power-law
winds try to mimic the tune yet fail to crest the luminous ridge logged in the
summary. When collaborators need to explain the theory's heartbeat, this
rehearsal shows how the membrane consents to resonance even without domain
specifics.
