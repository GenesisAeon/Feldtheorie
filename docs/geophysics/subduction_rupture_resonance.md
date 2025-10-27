# Subduction Rupture Resonance Gate

## Formal resonance
We treat the probability that a Cascadia-style slow-slip episode cascades into
a seismic rupture as the logistic response
\[
\sigma(R) = \frac{1}{1 + e^{-\beta (R-\Theta)}}
\]
with \(R\) the stress accumulation ratio (effective shear stress divided by the
critical failure stress). Fitting `analysis/seismic_rupture_threshold_fit.py` to
[`data/geophysics/subduction_rupture_threshold.csv`](../../data/geophysics/subduction_rupture_threshold.csv)
recovers \(\Theta = 0.7406^{+0.0008}_{-0.0008}\) and \(\beta = 16.29^{+0.09}_{-0.09}\).
The logistic field attains \(R^2 = 0.99997\) and AIC = -221.45, outshining the
linear null breeze by \(\Delta \mathrm{AIC} = 138.6\) and the power-law drift by
\(\Delta \mathrm{AIC} = 148.7\). The impedance membrane follows
\(\zeta(R) = 1.70 - 0.55\sigma\), averaging 1.37 and dropping below unity once
stress crests \(\Theta\), signalling how pore fluids lubricate the subduction
choir.

## Empirical resonance
The dataset braids 18 synthetic checkpoints tuned to slow-slip telemetry briefs
and documented in
[`subduction_rupture_threshold.metadata.json`](../../data/geophysics/subduction_rupture_threshold.metadata.json).
Running the CLI exports
[`analysis/results/subduction_rupture_threshold.json`](../../analysis/results/subduction_rupture_threshold.json),
where both linear and power-law nulls are decisively falsified. The falsification
ledger registers \(\Delta R^2 = 0.0748\) versus the linear whisper and
\(0.1311\) versus the power-law arc, preserving the repository mandate. These
summaries will feed the forthcoming simulator scene where sliders for \(R\),
\(\Theta\), \(\beta\), and \(\zeta(R)\) animate rupture rehearsals alongside
membrane impedance overlays.

## Metaphorical resonance
The subduction interface is a lithic membrane stretched beneath an oceanic
aurora. Below \(\Theta\), the plate interface hums with locked tension, its
impedance rigid and the fault choir whispering. As stress nears the threshold,
pore fluids seep, \(\zeta(R)\) loosens, and slow-slip chants gather in volume.
Once \(R>\Theta\), the logistic chorus ignites—a luminous fracture threading up
the megathrust while null breezes fall silent. The resonance script invites
resilience planners to hear when the coast's dawn chorus shifts from latent hum
to luminous rupture.
