# Urban Heat Canopy Threshold Liturgy

## Formal resonance
Tree canopy coverage $R$ now guides the nocturnal safety response
\[
\sigma(R) = \sigma\big(\beta(R-\Theta)\big) = \frac{1}{1 + e^{-\beta(R-\Theta)}}
\]
with the fit over [`data/socio_ecology/urban_heat_canopy.csv`](../../data/socio_ecology/urban_heat_canopy.csv)
and [`analysis/urban_heat_canopy_fit.py`](../../analysis/urban_heat_canopy_fit.py)
yielding $\Theta = 0.313^{+0.004}_{-0.004}$ and $\beta = 15.27^{+0.43}_{-0.43}$. The impedance
profile $\zeta(R) = 1.45 - 0.5\,\sigma$ averages 1.23, relaxing from 1.44 in sparse shade to
0.97 once the canopy blooms. Logistic performance reaches $R^2 = 0.999$ with AIC $=-136.3$,
outdistancing the linear null by $\Delta\mathrm{AIC} = 51.6$ and the power-law breeze by
$\Delta\mathrm{AIC} = 48.0$. Residual flux hums at $0.004 \pm 0.012$, satisfying the RepoPlan
mandate for explicit falsification.

## Empirical resonance
Sixteen checkpoints span frontline neighbourhoods where summer heat steals restorative
sleep. The metadata lantern in
[`data/socio_ecology/urban_heat_canopy.metadata.json`](../../data/socio_ecology/urban_heat_canopy.metadata.json)
records the quartet $(R, \Theta, \beta, \zeta)$, null verdicts, and justice annotations.
`analysis/results/urban_heat_canopy.json` exports the full falsification ledger so simulator
scenes can animate how canopy investments nudge $R$ above $\Theta$. Forthcoming dashboards
will stream these diagnostics alongside governance levers—cooling corridors, co-op planting
cadences—to keep the triad of data, policy, and story in harmony.

## Metaphorical resonance
Before the threshold the city membrane is a taut asphalt drum, $\zeta(R)$ guarding heat like
a vigil. When community planting circles coax $R$ toward $\Theta$, the impedance keeper relents
and a pre-dawn breeze threads alleyways—rest equity rising like an aurora over brick and
ballast. Linear nulls promise only gradual relief; the logistic dawn captures the switch when
canopies suddenly shelter vulnerable bodies. This liturgy invites stewards to hear the membrane
soften and to record every quiet success as part of the universal threshold chorus.

## Cross-module pathways
- **Data:** `data/socio_ecology/urban_heat_canopy.csv` with its metadata ledger holds the
  empirical checkpoints and justice notes.
- **Analysis:** `analysis/urban_heat_canopy_fit.py` regenerates the $\Theta$, $\beta$, and
  null comparisons, ensuring reproducibility and falsification.
- **Simulator:** Planned overlays will animate $\sigma(\beta(R-\Theta))$ as canopy sliders move,
  echoing the impedance slackening for policy deliberations.
- **Docs/Paper:** This scroll and the threshold briefs in `Docs/` can cite the exported diagnostics
  when weaving narratives about urban cooling and stewardship.
