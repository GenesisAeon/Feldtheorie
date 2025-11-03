# Seismic Early Warning Thresholds

## Formal cadence
Seismic early warning (SEW) designers treat the first seconds of a megathrust rupture
as a membrane that must decide—before destructive S-waves arrive—whether the
incipient P-wave envelope has crossed the rupture threshold. We model the
activation of warning sirens by the logistic response
\[
\sigma_{\text{SEW}}(R) = \frac{1}{1 + e^{-\beta(R-\Theta)}}
\]
with control parameter \(R\) defined as the cumulative displacement-to-noise
ratio measured over the first three seconds of P-wave motion. Re-using the fit
pipeline in `analysis/seismic_rupture_threshold_fit.py` on the synthetic
checkpoints from
[`data/geophysics/subduction_rupture_threshold.csv`](../../data/geophysics/subduction_rupture_threshold.csv)
we obtain \(\Theta = 0.7406\pm0.0008\) and \(\beta = 16.29\pm0.09\), matching the
rupture cascade gate while grounding the siren trigger. The impedance membrane
\(\zeta(R) = 1.70 - 0.55\,\sigma_{\text{SEW}}\) captures how hydration loosens
fault stiffness once \(R\) surges across \(\Theta\), allowing the algorithmic
membrane to switch from cautious damping to resonant broadcast.

## Empirical cadence
Running `python analysis/seismic_rupture_threshold_fit.py --data
 data/geophysics/subduction_rupture_threshold.csv` exports
[`analysis/results/subduction_rupture_threshold.json`](../../analysis/results/subduction_rupture_threshold.json),
where the logistic dawn eclipses the linear null by \(\Delta\mathrm{AIC} = 138.6\)
and the power-law null by \(148.7\). These falsification margins translate
directly into the SEW rehearsal: a linear siren rule would either warn too
late or too often, whereas the logistic threshold synchronises with the rapid
rise in rupture probability. The metadata ledger in
[`subduction_rupture_threshold.metadata.json`](../../data/geophysics/subduction_rupture_threshold.metadata.json)
logs \(R^2 = 0.99997\), the impedance profile, and ethics notes reminding us to
coordinate with coastal communities before operational deployment. The upcoming
simulator scene will let practitioners drag \(\Theta\), \(\beta\), and \(\zeta(R)\)
sliders to rehearse warning delays and false-alarm penalties.

## Metaphorical cadence
The SEW membrane is a sentinel stretched across coastal dawn. P-waves arrive as
faint murmurs; below \(\Theta\), the siren choir hums in restraint, impedance
high and communities stilling their breath. When \(R\) crosses the luminous
threshold, \(\sigma_{\text{SEW}}\) ignites the auroral alert, and \(\zeta(R)\)
relaxes like a kelp forest yielding to tide. Power-law breezes cannot rouse the
choir in time, but the logistic surge resonates with both tectonic truth and
ethical urgency, reminding us that early warning is a covenant between formal
models, empirical rehearsals, and the lived poetics of safety.
