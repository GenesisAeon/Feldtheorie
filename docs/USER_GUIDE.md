# Feldtheorie User Guide

**Version:** 10.2 (Platinum Release)
**Last Updated:** 2025-12-25
**For Scientists:** This guide provides practical workflows for using the UTAC framework

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Core Concepts](#2-core-concepts)
3. [Working with Datasets](#3-working-with-datasets)
4. [Running Analyses](#4-running-analyses)
5. [Interpreting Results](#5-interpreting-results)
6. [API Reference](#6-api-reference)
7. [CLI Tools](#7-cli-tools)
8. [Troubleshooting](#8-troubleshooting)
9. [FAQ](#9-faq)

---

## 1. Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/GenesisAeon/Feldtheorie.git
cd Feldtheorie

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pytest tests/ -q
```

### Your First Analysis (5 minutes)

```python
# Fit logistic threshold to LLM emergence data
python scripts/reproduce_beta.py \
  --csv data/ai/wei_emergent_abilities.csv \
  --out results/wei_beta.json

# View results
cat results/wei_beta.json
```

**Expected Output:**
```json
{
  "beta": 3.47,
  "theta": 0.52,
  "r2": 0.921,
  "delta_aic": 12.79
}
```

**Interpretation:** LLM abilities emerge at scale ~0.52 with steepness β=3.47 (information domain: β≈4.5±0.9).

---

## 2. Core Concepts

### 2.1 The UTAC Framework

**Universal Threshold Activation-Coupling (UTAC)** models phase transitions using:

```
P(R) = L / (1 + exp(-β(R - Θ)))
```

**Parameters:**
- **R**: Control parameter (scale, resource, stress)
- **Θ** (theta): Critical threshold (inflection point)
- **β** (beta): Steepness parameter (transition sharpness)
- **L**: Asymptotic limit (usually 1.0)

### 2.2 Domain-Specific β Hierarchy

**Key Discovery:** β is NOT universal but domain-specific!

| Domain | β Range | Interpretation |
|--------|---------|----------------|
| **Information** | 3.2 - 7.2 (β̄=4.5) | Soft emergence, rapid transitions |
| **Geophysical** | 3.5 - 5.8 (β̄=4.6) | Scale-invariant criticality |
| **Biological** | 6.2 - 9.1 (β̄=7.4) | Moderate coupling, Kleiber scaling |
| **Climate** | 9.8 - 13.2 (β̄=11.0) | Bistable jumps, irreversible |
| **Neurodegeneration** | 9.8 - 16.3 (β̄=13.0) | Molecular catastrophes |

**Statistical Evidence:** ANOVA F(4,73) = 185.3, p < 10⁻²⁰, η² = 0.91

### 2.3 Model Selection: ΔAIC ≥ 10 Threshold

We compare logistic models against null models (linear, power-law) using:

```
ΔAIC = AIC_null - AIC_logistic
```

**Decision Rule:**
- ΔAIC ≥ 10: Strong evidence for logistic model
- ΔAIC ≥ 4: Moderate evidence
- ΔAIC < 2: Insufficient evidence (prefer simpler model)

---

## 3. Working with Datasets

### 3.1 Data Format

All datasets should be CSV with minimum columns:

```csv
R,sigma
0.1,0.05
0.2,0.12
0.3,0.28
...
```

**R:** Control parameter (must be numeric)
**sigma:** Response variable (typically [0,1])

### 3.2 Metadata Requirements

Each dataset needs a `.metadata.json` file:

```json
{
  "name": "LLM Emergent Abilities",
  "domain": "information",
  "source": "Wei et al. (2022)",
  "doi": "10.48550/arXiv.2206.07682",
  "license": "CC BY 4.0",
  "variables": {
    "R": "Model scale (parameters in billions)",
    "sigma": "Task performance (accuracy)"
  },
  "fitted_parameters": {
    "beta": 3.47,
    "theta": 0.52,
    "r2": 0.921,
    "delta_aic": 12.79
  }
}
```

**Template:** See `schemas/metadata.schema.json`

### 3.3 Available Datasets

| Directory | Domain | Count |
|-----------|--------|-------|
| `data/ai/` | LLM emergence, consciousness | 12 |
| `data/climate/` | AMOC, ice sheets, Amazon | 8 |
| `data/biology/` | Ecosystems, microbiomes | 15 |
| `data/cognition/` | Neural avalanches, memory | 6 |
| `data/astrophysics/` | Cosmology, black holes | 4 |

**Master Dataset:** `data/derived/beta_estimates.csv` (78 validated systems)

---

## 4. Running Analyses

### 4.1 Single Dataset Fitting

**Script:** `scripts/reproduce_beta.py`

```bash
python scripts/reproduce_beta.py \
  --csv data/climate/amoc_strength.csv \
  --out results/amoc_fit.json \
  --plot results/amoc_fit.png
```

**Options:**
- `--csv`: Input CSV file (required)
- `--out`: Output JSON file (default: stdout)
- `--plot`: Save plot (optional)
- `--bootstrap`: Number of bootstrap iterations (default: 1000)
- `--seed`: Random seed for reproducibility (default: 1337)

### 4.2 Batch Analysis

**CLI Tool:** `utf-batch`

```bash
# Fit all datasets in a directory
utf-batch \
  --input-dir data/climate/ \
  --output results/climate_batch.json \
  --workers 4
```

**Output Format:**
```json
{
  "amoc_strength": {
    "beta": 4.02,
    "theta": 0.65,
    "r2": 0.987,
    "delta_aic": 29.4
  },
  "greenland_ice": {
    "beta": 4.38,
    ...
  }
}
```

### 4.3 Planetary Tipping Elements

**CLI Tool:** `utf-planetary-summary`

```bash
utf-planetary-summary \
  --output results/tipping_elements.csv \
  --format csv
```

**Analyzes:**
- AMOC (Atlantic Meridional Overturning Circulation)
- Greenland Ice Sheet
- West Antarctic Ice Sheet
- Amazon Rainforest
- Permafrost Carbon Release

### 4.4 Meta-Regression Analysis

**Script:** `analysis/beta_meta_regression_v2.py`

```bash
python analysis/beta_meta_regression_v2.py \
  --input data/derived/beta_estimates.csv \
  --output results/domain_clustering.json
```

**Purpose:** Test if β varies significantly across domains (ANOVA)

---

## 5. Interpreting Results

### 5.1 Parameter Interpretation

**β (Steepness):**
- **Low β (≈4):** Gradual transition, adaptive system
- **Medium β (≈7):** Moderate sharpness, biological systems
- **High β (≈11+):** Abrupt transition, climate tipping points

**Θ (Threshold):**
- Location of inflection point in R-space
- 95% CI should not overlap with data boundaries

**R² (Goodness of Fit):**
- R² > 0.95: Excellent fit
- R² > 0.90: Good fit
- R² < 0.80: Poor fit (check data quality)

**ΔAIC (Model Evidence):**
- ΔAIC ≥ 10: Strong evidence for logistic
- ΔAIC ≥ 4: Moderate evidence
- ΔAIC < 2: Insufficient evidence

### 5.2 Example Interpretation

```json
{
  "dataset": "amazon_rainforest",
  "beta": 14.56,
  "theta": 0.72,
  "beta_ci": [13.86, 15.26],
  "theta_ci": [0.70, 0.74],
  "r2": 0.999,
  "delta_aic": 66.2
}
```

**Interpretation:**
- **β=14.56 (high):** Very steep transition → tipping point behavior
- **Θ=0.72:** Critical threshold at 72% of deforestation
- **Narrow CIs:** High statistical confidence
- **ΔAIC=66.2:** Overwhelming evidence for logistic over linear
- **Domain match:** Climate domain (β̄=11.0), expected high β

**Warning Signs:**
- β > 13: Potential irreversible tipping point
- Θ approaching current conditions: Urgent intervention needed

---

## 6. API Reference

### 6.1 Python API

**Import Core Models:**

```python
from models.logistic_threshold import ThresholdMembrane
from analysis.resonance_fit_pipeline import (
    fit_threshold_parameters,
    evaluate_null_model,
    evaluate_power_law_null,
)
```

**Basic Usage:**

```python
import numpy as np
from analysis.resonance_fit_pipeline import fit_threshold_parameters

# Your data
R = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
sigma = np.array([0.05, 0.08, 0.15, 0.30, 0.50, 0.70, 0.85, 0.92, 0.95])

# Fit threshold model
result = fit_threshold_parameters(R, sigma)

print(f"β = {result['beta']:.2f}")
print(f"Θ = {result['theta']:.2f}")
print(f"R² = {result['r2']:.3f}")
print(f"AIC = {result['aic']:.2f}")
```

**Advanced: ThresholdMembrane Class:**

```python
from models.logistic_threshold import ThresholdMembrane

# Create membrane
membrane = ThresholdMembrane(theta=0.5, beta=5.0)

# Evaluate response
R = np.linspace(0, 1, 100)
sigma = membrane.response(R)

# Get summary statistics
summary = membrane.summarise(R)
print(summary)
```

### 6.2 REST API (Optional)

If you install the `[api]` extras:

```bash
pip install -e ".[api]"
```

**Start Server:**

```bash
uvicorn api.server:app --reload
```

**Endpoints:**
- `GET /api/fieldtypes` - List all field type classifications
- `POST /api/analyze` - Fit logistic model to data
- `GET /api/simulate` - Run threshold simulations
- `POST /api/sonify` - Generate audio from β-spectra

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "R": [0.1, 0.2, 0.3, 0.4, 0.5],
    "sigma": [0.05, 0.12, 0.28, 0.50, 0.72]
  }'
```

---

## 7. CLI Tools

### 7.1 Available Commands

All commands installed with `pip install -e .`:

```bash
utf-batch                  # Batch UTAC analysis
utf-planetary-summary      # Climate tipping elements
utf-resonance-cohort       # Multi-system β aggregation
utf-potential-cascade      # Cascade risk analysis
utf-preset-guard           # Simulator parameter validation
```

### 7.2 Common Workflows

**Workflow 1: Analyze New Dataset**

```bash
# 1. Prepare data (CSV format)
# 2. Create metadata.json
# 3. Fit model
python scripts/reproduce_beta.py --csv mydata.csv --out results.json

# 4. Compare with null models
python analysis/resonance_fit_pipeline.py --csv mydata.csv --nulls linear,power

# 5. Visualize
python scripts/plot_threshold.py --json results.json
```

**Workflow 2: Domain Meta-Analysis**

```bash
# 1. Collect all β estimates
utf-batch --input-dir data/ --output beta_all.json

# 2. Run ANOVA
python analysis/beta_meta_regression_v2.py --input beta_all.json

# 3. Generate report
python scripts/generate_domain_report.py --output report.md
```

**Workflow 3: Reproducibility Check**

```bash
# Run full test suite
make test

# Run statistical harness
make batch

# Validate presets
make preset-guard

# Full release checks
make release
```

---

## 8. Troubleshooting

### 8.1 Common Issues

**Issue: Fit does not converge**

```
ValueError: At least one sample is required to fit threshold parameters
```

**Solutions:**
- Check data has at least 10 points
- Ensure R has variation (not all constant)
- Check for NaN/Inf values
- Try increasing sample size

**Issue: ΔAIC < 10 (weak evidence)**

**Possible Causes:**
- Data truly linear (no threshold)
- Insufficient sample size (n < 20)
- High noise levels
- Wrong domain (not threshold behavior)

**Actions:**
- Collect more data
- Check measurement errors
- Consider alternative models (power-law, exponential)

**Issue: β outside expected range**

**Expected Ranges:**
- Information: 3-7
- Biology: 6-9
- Climate: 10-13

**If β >> 20:**
- Numerical issues (rescale R)
- Step function (check data quality)

**If β < 1:**
- No threshold behavior
- Linear relationship more appropriate

### 8.2 Data Quality Checks

```python
import numpy as np

# Check for issues
def diagnose_data(R, sigma):
    print(f"Sample size: {len(R)}")
    print(f"R range: [{R.min():.3f}, {R.max():.3f}]")
    print(f"R variation: {R.std():.3f}")
    print(f"Sigma range: [{sigma.min():.3f}, {sigma.max():.3f}]")
    print(f"NaN count: {np.isnan(R).sum() + np.isnan(sigma).sum()}")

    if len(R) < 10:
        print("⚠️ Warning: Sample size < 10")
    if R.std() < 0.01:
        print("⚠️ Warning: R has low variation")
    if np.any(np.isnan(R)) or np.any(np.isnan(sigma)):
        print("⚠️ Warning: NaN values detected")

# Use it
R = np.array([...])
sigma = np.array([...])
diagnose_data(R, sigma)
```

---

## 9. FAQ

### Q1: What is the difference between β and Θ?

**A:** β controls *how fast* the transition happens (steepness), while Θ controls *where* it happens (location). Think of Θ as the "when" and β as the "how abruptly".

### Q2: Can I use UTAC for non-probabilistic data?

**A:** Yes! While σ is often interpreted as probability, UTAC works for any response variable that shows threshold behavior. Examples: concentration, temperature, population density.

### Q3: How many data points do I need?

**A:** Minimum 10, recommended 20+. More points = narrower confidence intervals and better model selection (ΔAIC).

### Q4: What if my R² is low but ΔAIC is high?

**A:** This can happen with noisy data. ΔAIC > 10 means logistic is still better than linear, even if absolute fit is poor. Consider:
- Increasing sample size
- Checking measurement errors
- Adding covariates (if applicable)

### Q5: Can I use UTAC for time series?

**A:** Yes, but with caution. R becomes time (or cumulative dose). Check for:
- Autocorrelation (violates independence assumption)
- Non-stationarity (changing dynamics over time)

Consider detrending or using specialized time series methods.

### Q6: How do I cite this work?

See [CITATION.cff](../CITATION.cff):

```bibtex
@software{feldtheorie2025,
  author = {Römer, Johann Benjamin and Contributors},
  title = {Universal Threshold Field Model: UTAC Framework},
  year = {2025},
  publisher = {Zenodo},
  version = {v10.2},
  doi = {10.5281/zenodo.17974828},
  url = {https://github.com/GenesisAeon/Feldtheorie}
}
```

### Q7: Where can I get help?

- **Scientific Questions:** See [SUMMARY.md](../SUMMARY.md) for detailed theory
- **Bug Reports:** [GitHub Issues](https://github.com/GenesisAeon/Feldtheorie/issues)
- **Methodology:** [METHODS.md](../METHODS.md)
- **Limitations:** [LIMITATIONS.md](../LIMITATIONS.md)

---

## Additional Resources

### Documentation

- **[SUMMARY.md](../SUMMARY.md)** - Scientific summary (no metaphors)
- **[README.md](../README.md)** - Project overview
- **[METHODS.md](../METHODS.md)** - Statistical methodology
- **[QUICKSTART.md](../QUICKSTART.md)** - 5-minute tutorial
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - System design

### Scientific Foundations

- **[docs/utac_theory_core.md](utac_theory_core.md)** - Mathematical foundations
- **[docs/field_type_classification_v1.1.md](field_type_classification_v1.1.md)** - Domain taxonomy
- **[docs/v6_entropy_governance_tesseract_physics.md](v6_entropy_governance_tesseract_physics.md)** - Theoretical extensions

### Examples

- **[notebooks/](../notebooks/)** - Jupyter notebooks (coming soon)
- **[examples/](../examples/)** - Code examples
- **[analysis/results/](../analysis/results/)** - Benchmark results

---

**Last Updated:** 2025-12-25
**Version:** 10.2 (Platinum Release)
**Maintainer:** Johann Benjamin Römer & Contributors
**License:** Code (GPLv3), Content (CC BY-NC 4.0)
