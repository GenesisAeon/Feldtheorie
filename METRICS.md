# Statistical Metrics and Methodology

This reference summarises the metrics reported across UTF analyses.  Every
result documents the logistic quartet \((R, \Theta, \beta, \zeta(R))\), compares
against null models, and quantifies uncertainty.

## 1. Logistic steepness (β)
- **Definition:** slope of the logistic response \(\sigma(\beta(R-\Theta))\).
- **Interpretation:** larger \(\beta\) implies sharper transitions.
- **Estimation:** `scipy.optimize.curve_fit` with bounded parameters (see
  `METHODS.md`).  Bootstrap resampling (1,000 iterations, seed 1337) supplies the
  95% confidence interval.

## 2. Threshold (Θ)
- **Definition:** control parameter value where \(P(R)=0.5\).
- **Reporting:** scripts store \(\Theta\) in dataset units and, when relevant,
  in normalised coordinates.
- **Interpretation:** identifies the resource or stress level at which the
  system switches regimes.

## 3. Goodness-of-fit metrics
| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **AIC** | \(n \log(\mathrm{RSS}/n) + 2k\) | Penalised likelihood; lower is better. |
| **ΔAIC** | \(\mathrm{AIC}_{\text{null}} - \mathrm{AIC}_{\text{logistic}}\) | ≥10 indicates strong support for the logistic response. |
| **BIC** | \(n \log(\mathrm{RSS}/n) + k\log n\) | Conservative penalty for model size. |
| **RMSE** | \(\sqrt{\mathrm{RSS}/n}\) | Absolute prediction error. |
| **R²** | \(1 - \mathrm{RSS}/\mathrm{TSS}\) | Fraction of variance explained. |

## 4. Null models
Analyses benchmark the logistic fit against:
- **Linear regression:** \(y = aR + b\)
- **Power law:** \(y = aR^{b}\) (log–log fit)
- **Exponential:** \(y = a\exp(bR)\)

ΔAIC and ΔBIC values are reported for each null.  Logistic fits failing the
ΔAIC ≥ 10 guard are flagged in the corresponding documentation.

## 5. Sample sizes and provenance
Metadata files enumerate observation counts, domains, and licenses.  Key
examples:

| Domain | Dataset | Observations |
|--------|---------|--------------|
| AI | `wei_emergent_abilities.csv` | 30 per task |
| Climate | `planetary_tipping_elements.csv` | 120 coupled states |
| Cognition | `working_memory_gate.csv` | 48 experimental runs |
| Ecology | `honeybee_waggle_activation.csv` | 60 colony probes |

See `data/*/*.metadata.json` for domain-specific notes.

## 6. Bootstrap procedure
1. Resample paired \((R, \text{response})\) observations with replacement.
2. Refit the logistic curve.
3. Record \(\beta\) and \(\Theta\).
4. Repeat 1,000 times; report 2.5th/97.5th percentiles.

## 7. Falsification tracking
`docs/utac_falsifiability.md` logs any dataset where \(\beta\) leaves the
\([3.6, 4.8]\) universality band or where ΔAIC falls below 10.  Contributors
must extend the table when new evidence challenges the canonical band.
