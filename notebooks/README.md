# Feldtheorie Jupyter Notebooks

Interactive notebooks for exploring the UTAC framework.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/GenesisAeon/Feldtheorie/HEAD?filepath=notebooks)

---

## Available Notebooks

### 1. **01_Quickstart_LLM_Analysis.ipynb** ⭐ **Start Here!**

**Time:** 5-10 minutes
**Level:** Beginner

Reproduces the β-fit for LLM emergent abilities (Wei et al. 2022).

**You'll learn:**
- Load UTAC framework data
- Fit logistic threshold model σ(β(R-Θ))
- Interpret β, Θ, ΔAIC parameters
- Visualize threshold emergence
- Compare with null models

**Expected Output:**
- β ≈ 3.5 (information domain)
- Θ ≈ 0.5 (emergence threshold)
- ΔAIC ≥ 10 (strong evidence)

---

## Quick Start

### Option A: Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install jupyter

# 2. Start Jupyter
cd notebooks
jupyter notebook

# 3. Open 01_Quickstart_LLM_Analysis.ipynb
```

### Option B: Run in Binder (No Installation!)

Click the Binder badge above to launch an interactive environment in your browser.

**Pros:**
- No local installation
- Works on any device
- Pre-configured environment

**Cons:**
- Slower than local
- Sessions expire after ~10 minutes of inactivity

---

## Notebook Structure

All notebooks follow this template:

1. **Import & Setup** - Load libraries and data
2. **Data Loading** - Read CSV from `data/`
3. **Model Fitting** - Fit UTAC threshold model
4. **Null Comparison** - Test against linear/power-law
5. **Visualization** - Plot results
6. **Interpretation** - Explain β, Θ, domain context

---

## Prerequisites

**Python:** 3.10+

**Required Packages:**
```
numpy>=1.26
scipy>=1.11
pandas>=2.1
matplotlib>=3.8
jupyter>=1.0
```

**Optional (for advanced notebooks):**
```
seaborn  # Enhanced visualizations
plotly   # Interactive plots
statsmodels  # ANOVA, meta-regression
```

---

## Datasets Used

| Notebook | Dataset | Domain | β Range |
|----------|---------|--------|---------|
| 01 | `wei_emergent_abilities.csv` | Information | 3.2-7.2 |

**Full Dataset Catalog:** [data/derived/beta_estimates.csv](../data/derived/beta_estimates.csv) (78 systems)

---

## Tips & Tricks

### Kernel Issues?

```python
# Check kernel
import sys
print(sys.executable)

# Should point to your venv/bin/python
```

### Can't import modules?

```python
# Add parent directory to path
import sys
sys.path.insert(0, '..')

# Now imports work
from analysis.resonance_fit_pipeline import fit_threshold_parameters
```

### Want to modify a notebook?

1. Save a copy: `File > Make a Copy`
2. Rename: `Untitled.ipynb` → `My_Analysis.ipynb`
3. Experiment freely!

---

## Troubleshooting

**Problem:** "Module not found: analysis"

**Solution:**
```python
import sys
sys.path.insert(0, '..')  # Add parent directory
```

**Problem:** "File not found: ../data/..."

**Solution:**
```bash
# Run from notebooks/ directory
cd notebooks
jupyter notebook
```

**Problem:** Kernel keeps dying

**Solution:**
- Check memory usage (some fits are memory-intensive)
- Restart kernel: `Kernel > Restart`
- Clear outputs: `Cell > All Output > Clear`

---

## Contributing New Notebooks

Want to add a notebook? Follow this template:

```python
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Title: Brief Description\n",
    "\n",
    "**Goal:** What you'll accomplish\n",
    "**Time:** X minutes\n",
    "**Level:** Beginner/Intermediate/Advanced"
   ]
  },
  # ... cells ...
 ]
}
```

**Checklist:**
- [ ] Clear learning objectives
- [ ] Well-commented code
- [ ] Visualizations included
- [ ] Interpretation section
- [ ] Works in Binder
- [ ] Tested end-to-end

**Submit via PR:**
1. Test locally
2. Test in Binder
3. Add to this README
4. Create PR with description

---

## Additional Resources

**Documentation:**
- [USER_GUIDE.md](../docs/USER_GUIDE.md) - Complete user guide
- [SUMMARY.md](../SUMMARY.md) - Scientific summary (no metaphors)
- [METHODS.md](../METHODS.md) - Statistical methodology
- [QUICKSTART.md](../QUICKSTART.md) - 5-minute CLI tutorial

**Code Examples:**
- [scripts/reproduce_beta.py](../scripts/reproduce_beta.py) - Command-line fitting
- [analysis/](../analysis/) - Analysis pipeline code
- [models/](../models/) - Core UTAC models

**Community:**
- [GitHub Issues](https://github.com/GenesisAeon/Feldtheorie/issues) - Bug reports
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [CODE_REVIEW.md](../CODE_REVIEW.md) - Code review standards

---

**Maintained by:** Johann Benjamin Römer & Contributors
**License:** Code (GPLv3), Content (CC BY-NC 4.0)
**Last Updated:** 2025-12-25
