# V3 Core Modules: Klimakluft Amplifier & Implosive Genesis

## Klimakluft Amplifier

**Formula.** The effective steepness obeys
\[\beta_{\text{eff}} = \beta_{\text{base}} \cdot (1 + \text{Gini} \cdot \text{Load})\].
It couples inequality (Gini) with load concentration so that σ(β(R−Θ)) steepens when
resources and risks are hoarded. With \(\beta_{\text{base}}\) fixed, a doubling of the
product Gini·Load doubles the distance-sensitive acceleration of the logistic flank.

**Interpretation.** Inequality erodes the warning horizon \(\tau^*\). When Gini·Load grows,
β_eff rises and the logistic switch fires with less distance between R and Θ, collapsing
lead time for mitigation. In the UTAC cadence this shortens the interval where \(\zeta(R)\)
can be damped; alarm windows shrink because concentration translates into steeper
σ(β(R−Θ)) slopes and earlier threshold crossings.

**Practical use.** The amplifier accepts baseline β, Gini coefficients, and load indices
per cohort or percentile bucket. Analysts should log both the null model (constant β) and
ΔAIC relative to the amplified fit to preserve falsifiability. Visual overlays should point
at `figures/klimakluft_amplifier_v3.png` for the steepening curve and
`figures/klimakluft_warning_window_v3.png` for τ* collapse illustrations.

## Implosive Genesis

**Inverse sigmoid.** The genesis engine inverts the standard sigmoid,
\[S(R) = \sigma(-\beta(R-\Theta)) = \frac{1}{1 + e^{+\beta(R-\Theta)}}\],
and tracks trajectories that begin compressed and implode toward Θ before expanding.
At \(R=\Theta\) the membrane is maximally sensitive; \(R<\Theta\) keeps fields compressed,
while \(R>\Theta\) flips to an expanding regime with diminishing returns.

**Cosmological meaning.** The inverted response treats space as emergent information:
compression encodes higher informational density and the expanding tail replays the
decoding of structure back into observable volume. σ(−β(R−Θ)) therefore maps
information release onto cosmological emergence—every increment in R past Θ is an
information-driven dilation rather than raw spatial growth.

**Practical use.** `simulation/implosive_genesis_sim.py` ships presets for β sweeps and
Θ perturbations. For V3 visuals, reference `figures/implosive_genesis_phase_map_v3.png`
(collapsing trajectories) and `figures/information_space_unfurl_v3.png` (emergent-space
interpretation). Pair plots with ΔAIC tables against linear and power-law nulls to keep
telemetry auditable.
