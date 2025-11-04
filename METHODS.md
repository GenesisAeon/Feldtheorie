# Methods

## Overview
This repository operationalises the Universal Threshold Field (UTF) hypothesis by
fitting the logistic response \(\sigma(\beta(R-\Theta))\) to datasets drawn from
synthetic intelligence, ecology, cognition, and geophysics.  Every analysis
reports the quartet \((R, \Theta, \beta, \zeta(R))\) together with explicit
comparisons against smooth null models.

## Logistic model
We model the probability or intensity of emergence as
\[
P(R) = \frac{L}{1 + \exp(-\beta (R-\Theta))},
\]
where \(R\) is the control parameter, \(\Theta\) the critical threshold,
\(\beta\) the steepness, and \(L\) the asymptote.  Unless domain evidence
suggests otherwise we fix \(L = 1\).

## Estimation procedure
- **Optimiser.** `scipy.optimize.curve_fit` with trust region reflective bounds,
  maximum 200,000 evaluations.
- **Initialisation.** \(\Theta_0 = \mathrm{median}(R)\), \(\beta_0 = 3.5\),
  \(L_0 = \max(y)\) if the response is unnormalised, otherwise 1.
- **Bounds.** \(\beta \in [0.01, 20]\), \(\Theta \in [\min(R), \max(R)]\),
  \(L \in [0.1, 5]\).
- **Convergence.** Fits terminate when the relative step size drops below
  \(10^{-9}\) or the iteration budget is exhausted.

## Null models
We benchmark three smooth alternatives for falsification:

| Model | Parameterisation | Notes |
|-------|------------------|-------|
| Linear | \(y = aR + b\) | Ordinary least squares, two parameters. |
| Power law | \(y = a R^{b}\) | Log–log regression on positive samples. |
| Exponential | \(y = a\,\exp(bR)\) | Semi-log regression on positive samples. |

The logistic fit must satisfy \(\Delta\mathrm{AIC} \geq 10\) relative to each
null to claim strong evidence for the UTF response.

## Information criteria and error metrics
We report goodness of fit using the following statistics:

- **AIC:** \(n \log(\mathrm{RSS}/n) + 2k\)
- **BIC:** \(n \log(\mathrm{RSS}/n) + k \log n\)
- **RMSE:** \(\sqrt{\mathrm{RSS}/n}\)
- **Coefficient of determination:** \(R^2 = 1 - \mathrm{RSS}/\mathrm{TSS}\)

## Bootstrap uncertainty
Steepness uncertainty is quantified with paired bootstrap resampling
(1,000 iterations, seed 1337).  Each resample refits the logistic response and
collects \(\beta\), yielding the 2.5th and 97.5th percentiles for the confidence
interval.

## Preprocessing
- **Normalisation.** Responses are scaled to \([0,1]\) when the native range is
  bounded; control parameters spanning several orders of magnitude are log
  transformed.
- **Outliers.** Observations beyond 1.5×IQR are flagged.  Analyses report the
  fit both with and without flagged samples for sensitivity checks.
- **Missing values.** Rows with missing \(R\) or response entries are removed,
  with counts reported in companion notebooks.

## Reporting schema
`analysis/` scripts export JSON documents containing:

- dataset identifier and provenance
- logistic parameters (\(\beta, \Theta, L\)) with confidence intervals
- goodness-of-fit metrics and ΔAIC values for each null
- references to upstream data files and simulator presets

The JSON structure is validated against `schemas/` to guarantee reproducible
handoffs between analysis, documentation, and simulator layers.

## Reproducibility safeguards
- **Seeds.** Global `RANDOM_SEED = 1337` for bootstrap and stochastic routines.
- **Environment.** Reproduction relies on `environment.yml` or the pinned
  `requirements.txt`.
- **Continuous integration.** `.github/workflows/ci.yml` replays linting,
  testing, and coverage checks with the same environment definition.
