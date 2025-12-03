# Hierarchical Bayesian β Meta-Regression

## 🎲 Overview

This module implements a **hierarchical Bayesian model** to explain how logistic steepness (β) varies across domains through **domain-level random effects** and **information borrowing**.

### Theoretical Framework

| Domain | Expected β | Interpretation |
|--------|-----------|----------------|
| **Climate/Cosmic** | ~11.0 | Surface-bound, holographic (S ∝ A) |
| **Biology** | ~7.4 | Body-coupled, metabolic (S ∝ A^0.75·V^0.25) |
| **Cognition** | ~4.5 | Volume-integrated (S ∝ V) |
| **AI/Symbolic** | ~1.0 | Decoupled, abstract (S ∝ N) |

---

## 🏗️ Hierarchical Structure

```
Level 3: μ_global ~ Normal(Φ³, σ_global²)
         ↓
Level 2: μ_j ~ Normal(μ_global, σ_μ²)  [Domain random effects]
         ↓
Level 1: β_ij ~ Normal(μ_j + X_ij·γ, σ_ε²)  [Individual observations]
```

### Information Borrowing

Domains with **few observations** automatically "borrow" information from:
1. **Global distribution** (centered on Φ³ ≈ 4.236)
2. **Other domains** (through hierarchical shrinkage)

This prevents overfitting and provides robust estimates even with sparse data.

---

## 📦 Installation

```bash
# Install PyMC and ArviZ (required)
pip install pymc arviz

# Or with conda
conda install -c conda-forge pymc arviz
```

---

## 🚀 Usage

### Basic Usage

```bash
python analysis/beta_meta_regression_bayes.py \
    --beta-csv data/derived/beta_estimates.csv \
    --covariates-csv data/derived/domain_covariates.csv \
    --output-dir analysis/results/bayes \
    --n-samples 2000 \
    --n-tune 1000 \
    --n-chains 4
```

### With Covariates

```bash
python analysis/beta_meta_regression_bayes.py \
    --beta-csv data/derived/beta_estimates.csv \
    --covariates-csv data/derived/domain_covariates.csv \
    --covariates coupling_efficiency dimensionality memory_factor \
    --n-samples 3000
```

### Input Format

**beta_estimates.csv** (required columns):
```csv
domain,beta
bio_kleiber,7.4
climate_tipping,11.2
cognition_cff,4.5
ai_gpt4,1.1
```

**domain_covariates.csv** (optional):
```csv
domain,coupling_efficiency,dimensionality,memory_factor
bio_kleiber,0.75,2.5,0.8
climate_tipping,0.9,2.0,0.3
```

---

## 📊 Output

### 1. Results JSON

```json
{
  "mu_global_mean": 6.2,
  "mu_global_hdi_low": 4.8,
  "mu_global_hdi_high": 7.6,
  "domain_effects": {
    "biology": {"mean": 7.3, "hdi_low": 6.5, "hdi_high": 8.1},
    "climate": {"mean": 10.9, "hdi_low": 9.2, "hdi_high": 12.6},
    "cognition": {"mean": 4.6, "hdi_low": 3.9, "hdi_high": 5.3},
    "ai_symbolic": {"mean": 1.2, "hdi_low": 0.6, "hdi_high": 1.8}
  },
  "shrinkage_factors": {
    "biology": 0.15,
    "climate": 0.08,
    "cognition": 0.22,
    "ai_symbolic": 0.65
  }
}
```

**Shrinkage interpretation:**
- **Low shrinkage (0.08)**: Domain has many observations, estimate stays close to observed mean
- **High shrinkage (0.65)**: Domain has few observations, estimate borrows heavily from global mean

### 2. Visualizations

- **`trace_plots.png`**: MCMC convergence diagnostics
- **`forest_plot_domains.png`**: Domain-level β estimates with 94% HDI
- **`ppc_plot.png`**: Posterior predictive check

### 3. NetCDF Trace

Full MCMC trace saved for further analysis with ArviZ:

```python
import arviz as az
trace = az.from_netcdf('analysis/results/bayes/bayes_trace_20251203T123000Z.nc')
az.plot_posterior(trace, var_names=['mu_global', 'mu_domain'])
```

---

## 🔬 Model Diagnostics

### MCMC Convergence

- **R-hat < 1.01**: Chains have converged
- **ESS > 400**: Sufficient effective sample size
- **Divergences = 0**: No sampling issues

### Posterior Predictive Checks

- **PPC p-value ≈ 0.5**: Model captures data distribution well
- **PPC RMSE**: Root mean squared error of predictions

---

## 🧮 Mathematical Details

### Likelihood

```
β_ij ~ Normal(μ_j + X_ij·γ, σ_ε²)
```

Where:
- `β_ij`: β estimate for observation i in domain j
- `μ_j`: Domain-specific mean
- `X_ij·γ`: Covariate effects
- `σ_ε²`: Observation noise

### Priors

```python
μ_global ~ Normal(Φ³, 3.0²)           # Global mean centered on 4.236
σ_global ~ HalfNormal(2.0)            # Global heterogeneity
μ_j ~ Normal(μ_global, σ_global²)     # Domain means
σ_j ~ HalfNormal(1.5)                 # Domain-specific variance
γ ~ Normal(0, 2.0)                    # Covariate effects
σ_ε ~ HalfNormal(1.0)                 # Observation noise
```

### Shrinkage Formula

```
Shrinkage = |μ_j_hierarchical - μ_j_observed| / |μ_j_observed - μ_global|
```

Values:
- **0**: No shrinkage (observed mean used)
- **1**: Complete shrinkage (global mean used)
- **0.5**: Partial pooling (compromise)

---

## 🎯 Key Features

✅ **Hierarchical Structure**: 3-level model (global → domain → observation)
✅ **Information Borrowing**: Automatic shrinkage for sparse domains
✅ **NUTS Sampler**: Efficient gradient-based MCMC
✅ **Posterior Predictive Checks**: Model validation built-in
✅ **VIF Checks**: Multicollinearity detection for covariates
✅ **94% HDI**: Highest Density Intervals (Bayesian confidence intervals)
✅ **ArviZ Integration**: Full diagnostic suite

---

## 📚 References

- Gelman & Hill (2007): *Data Analysis Using Regression and Multilevel Models*
- McElreath (2020): *Statistical Rethinking* (2nd ed.)
- Salvatier et al. (2016): *Probabilistic programming in Python using PyMC3*
- V6ToDorefresh.md Priority 11 (Beta-Bayes specification)
- FinalyzeVorschlägeGemini.txt:36-39 (Hierarchical model requirements)

---

## 🐛 Troubleshooting

### PyMC not installed

```bash
pip install pymc arviz
```

### Sampling issues (divergences)

Increase `target_accept`:
```python
pm.sample(..., target_accept=0.99)
```

### Slow sampling

Reduce chains or samples:
```bash
--n-chains 2 --n-samples 1000
```

### High VIF (>10)

Remove collinear covariates or use PCA for dimensionality reduction.

---

## 🔗 Integration

This module integrates with:
- **beta_meta_regression_v2.py**: Frequentist bootstrap comparison
- **CREP governance**: τ*-safety and Type-VI detection
- **Zenodo pipeline**: Reproducibility and provenance

---

**FIT-Track:** v6r-beta-bayes
**Status:** ✅ Operational (requires PyMC installation)
