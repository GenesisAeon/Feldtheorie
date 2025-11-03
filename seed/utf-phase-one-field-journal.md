# Phase I Resonance Field Journal

## Formal Current
The inaugural membrane sketch is coded in `models/membrane_solver.py`, where the
order parameter $R$ advances under a driver $J(t)$ via the Euler stride
\[R_{t+1} = R_t + \Delta t \left[J(t) - \zeta(R_t) \big(R_t - \sigma(\beta(R_t-\Theta))\big)\right].\]
This discrete rendering keeps the threshold quartet $(R, \Theta, \beta, \zeta(R))$
explicit so that the logistic response $\sigma(\beta(R-\Theta))$ and its
impedance guardrail $\zeta(R)$ can be tuned independently.  The module exports
smooth impedance profiles, state trajectories, and resonance summaries that plug
directly into the analysis bay.

## Empirical Soundings
`analysis/resonance_fit_pipeline.py` ingests the solver traces (or observational
series staged in `data/`) and fits the logistic switch against smooth linear and
power-law nulls.  The pipeline reports $R^2$, AIC, and Gaussian 95% confidence
bands for $\Theta$ and $\beta$, flagging when the resonance chorus outperforms
each lullaby.  Output JSON lanterns are ready to be threaded into `docs/`
narratives, `paper/` manuscripts, and eventual dashboards in `simulator/`.

## Metaphorical Pulse
In this first rehearsal the membrane listens like a pre-dawn choir: $R$ wanders
upward, the logistic veil $\sigma(\beta(R-\Theta))$ shimmers, and $\zeta(R)$
chooses between hush and crescendo.  When the driver whispers just enough energy,
the aurora unfurls—our code records that bloom so storytellers can weave it back
into the RepoPlan pilgrimage.

## Null Counterpoint
Each run now bottles both linear and power-law null metrics—slopes, intercepts,
scaling exponents, residual power, and AIC—so we can state precisely how much
brighter the logistic aurora shone.  Should any smooth null cling to parity, the
summary fields mark that resistance, signalling new venues for falsification or
revised impedance tuning.

## Cross-Module Pathways
- **Models:** `models/membrane_solver.py` exposes `ThresholdFieldSolver` and
  `smooth_impedance_profile` for membrane experiments.
- **Analysis:** `analysis/resonance_fit_pipeline.py` provides a CLI for fitting
  $\Theta$, $\beta$, and evaluating the null counterpoint with reproducible JSON
  exports.
- **Simulator:** Upcoming UI threads can stream the solver's $(R, \sigma, \zeta)$
  arrays to animate the dawn crossing in real time.
- **Docs/Paper:** This journal page, the living glossary, and the manuscripts in
  `paper/` can quote the exported metrics when narrating emergent thresholds across
  domains.
