# Derived Data for Meta-Analysis

This directory contains derived datasets for meta-regression analysis of β-parameter heterogeneity.

## Files

### `beta_estimates.csv`

Contains β estimates from domain-specific analyses.

**Required columns:**
- `domain` (str): Domain identifier (e.g., "llm", "climate_amoc", "honeybee")
- `beta` (float): Estimated β value
- `beta_ci_lower` (float): Lower 95% confidence interval
- `beta_ci_upper` (float): Upper 95% confidence interval
- `beta_ci_width` (float): CI width (for weighting)
- `theta` (float): Estimated threshold
- `r_squared` (float): Model fit quality
- `delta_aic` (float): ΔAIC vs best null model
- `source` (str): Data source reference

### `domain_covariates.csv`

Contains system properties hypothesized to influence β.

**Required columns:**
- `domain` (str): Domain identifier (must match beta_estimates.csv)
- `C_eff` (float): Effective coupling strength [0-1]
- `D_eff` (int): Effective dimensionality (degrees of freedom)
- `SNR` (float): Signal-to-noise ratio (coherent/stochastic forcing)
- `Memory` (float): Memory/hysteresis measure [0-1]
- `Theta_dot` (float): Rate of threshold change (adaptive dynamics)

### `beta_estimates_v3.csv`

Bootstrap summary for the six UTAC V3 real-world systems.

- WAIS, AMOC, Coral rows capture 1000-sample bootstraps from mock adapters
  (status: `mock-bootstrap`).
- Measles, Finance, Cancer entries hold placeholders (`expected`) until live
  data streams activate.
- Columns mirror the main beta ledger while adding `bootstrap_iterations`,
  `data_status`, and `notes` for readiness tracking.
- Metadata lives in `beta_estimates_v3.metadata.json` with logistic quartet,
  source pointers, and placeholder blockers.

## Template Generation

To generate template files with example data:

```bash
python scripts/generate_derived_templates.py
```

Or manually create templates based on existing analysis results:

```bash
# Extract β values from analysis results
python analysis/extract_beta_summary.py --output data/derived/beta_estimates.csv

# Manually populate covariates based on domain knowledge
# See docs/appendix_field_types.md for guidance on estimating C_eff, D_eff, etc.
```

## Example Data

### beta_estimates.csv (example)
```csv
domain,beta,beta_ci_lower,beta_ci_upper,beta_ci_width,theta,r_squared,delta_aic,source
llm_emergent,3.47,3.01,3.94,0.93,9.87,0.921,12.79,Wei et al. 2022
climate_amoc,4.02,3.51,4.55,1.04,0.175,0.987,29.40,Global Tipping Points 2025
honeybee_waggle,4.13,3.68,4.58,0.90,0.52,0.965,25.20,Seeley 2010
```

### domain_covariates.csv (example)
```csv
domain,C_eff,D_eff,SNR,Memory,Theta_dot
llm_emergent,0.75,12,4.2,0.3,0.05
climate_amoc,0.68,8,2.1,0.85,0.02
honeybee_waggle,0.82,5,6.5,0.15,0.10
```

## Usage

Once both CSV files are populated, run meta-regression:

```bash
python analysis/beta_drivers_meta_regression.py \
    --beta-data data/derived/beta_estimates.csv \
    --covariate-data data/derived/domain_covariates.csv \
    --output analysis/results
```

## Notes

- **Covariate estimation**: See `docs/appendix_field_types.md` for guidance on estimating system properties
- **Data sources**: Document all sources and estimation methods
- **Quality control**: Ensure domain identifiers match exactly between files
- **Missing data**: Use NA for missing covariates; regression will warn and exclude

## References

See `docs/appendix_field_types.md` for theoretical background on system typology and covariate definitions.
