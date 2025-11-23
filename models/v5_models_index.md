# 🌌 UTAC v5.0 Models Index - Structural Isomorphism Testing

**Version:** 5.0.0
**Date:** 2025-11-23
**Type:** Bedeutungs-Sigillin (Model Documentation)
**Status:** 🟢 ACTIVE

---

## Overview

UTAC v5.0 introduces two empirical models for testing **structural isomorphisms** between physical scaling laws and complex system dynamics:

1. **Cosmic Velocity Scaling** (`cosmic_alpha_phi.py`)
2. **Social Rigidity Ising Model** (`social_rigidity_ising.py`)

---

## Models

### 1. cosmic_alpha_phi.py (443 LOC)

**Purpose:** Test whether fundamental constants (α, Φ) correlate with cosmic velocities.

**Formula:**
```
v_test = c / (α⁻¹ · Φ)
```

**Key Features:**
- ✅ High-precision constants (CODATA 2018)
- ✅ Null hypothesis testing (10,000 random trials)
- ✅ Monte Carlo uncertainty propagation
- ✅ Statistical significance analysis

**Interfaces:**
- `CosmicQuantization` class
- `quick_prediction()` - One-liner for velocity
- `full_analysis()` - Complete analysis with null test

**Output:**
- Prediction: 1352.07 km/s
- Measured: 1370 ± 10 km/s
- Deviation: 1.31%
- p-value (null): 0.011

**Scientific Status:**
- ✅ Statistically significant correlation (p < 0.05)
- ❌ No theoretical mechanism
- ⚠️ Limitations: n=1 system, post-hoc selection

**Documentation:** [`docs/v5_hypothesis_isomorphism.md`](../docs/v5_hypothesis_isomorphism.md)

---

### 2. social_rigidity_ising.py (498 LOC)

**Purpose:** Test whether inequality drives social phase transitions via Ising model dynamics.

**Formula:**
```
T_social = 1 / (Gini · Load)
β_eff → ∞  (at high inequality)
```

**Model Analogy:**
- Spins σ_i → Individual opinions
- Coupling J → Social conformity
- Temperature T → Adaptability
- Magnetization M → Collective alignment

**Key Features:**
- ✅ Mean-field Ising model
- ✅ Self-consistent magnetization solver
- ✅ Phase transition detection
- ✅ Critical exponents calculation

**Interfaces:**
- `SocialIsingModel` class
- `quick_rigidity(gini, load)` - One-liner for β
- `full_analysis()` - Complete phase scan

**Output:**
- Critical Gini: 0.95
- Frozen states: 37.6% of parameter space
- Mean rigidity: 0.92 ± 0.60

**Scientific Status:**
- ✅ Theoretical model developed
- ❌ Empirical validation NOT yet performed
- ⚠️ Limitations: No calibration, simplistic mapping

**Documentation:** [`docs/v5_hypothesis_isomorphism.md`](../docs/v5_hypothesis_isomorphism.md)

---

## Integration with UTAC Framework

### Relationship to Core UTAC

Both v5.0 models extend the UTAC framework's threshold paradigm:

| Core UTAC | v5.0 Extension |
|-----------|----------------|
| σ(β(R-Θ)) | Cosmic: v ~ f(α, Φ) |
| Logistic response | Social: M(T, J, h) via mean-field |
| β-parameter (steepness) | Cosmic: α (coupling), Social: β_thermo (rigidity) |

**NOTE:** The β in `social_rigidity_ising.py` is **β_thermo = 1/T** (inverse temperature), NOT the UTAC threshold β!

### Dependencies

```python
# cosmic_alpha_phi.py
from scipy import constants, stats
import numpy as np
from dataclasses import dataclass

# social_rigidity_ising.py
from scipy.special import erf
import numpy as np
from dataclasses import dataclass
```

No internal UTAC model dependencies (standalone).

---

## AI Agent Interfaces

See: [`api/v5_agents.py`](../api/v5_agents.py)

**Available Functions:**
- `cosmic_velocity_predict(alpha, phi)`
- `cosmic_null_hypothesis_test(n_trials)`
- `social_rigidity_predict(gini, load)`
- `social_phase_transition_scan(gini_min, gini_max)`
- `v5_full_analysis()`

**MOR-Ready:**
- ✅ JSON-serializable outputs
- ✅ Batch processing support
- ✅ Stateless functions
- ✅ NumPy type handling

---

## Validation Scripts

### Monte Carlo Validation
**Script:** `scripts/validation/massive_monte_carlo.py`

- 100×100 parameter grids (20,000+ evaluations)
- Multiprocessing support
- Heatmap generation (300 DPI)
- CSV export for reproducibility

**Output:**
- `data/derived/monte_carlo_cosmic_results.csv` (944 KB)
- `data/derived/monte_carlo_social_results.csv` (1.2 MB)
- `figures/monte_carlo_cosmic_heatmaps.png` (353 KB)
- `figures/monte_carlo_social_heatmaps.png` (282 KB)

### Comparative Visualization
**Script:** `scripts/visualize_v5_duality.py`

- Side-by-side comparison of both models
- Publication-ready figures (300 DPI)
- Professional color scheme

**Output:**
- `figures/v5_duality_proof.png` (441 KB)

---

## FIT-MOR-Sigillin Compliance

**Code Review:** [`docs/v5_fit_mor_sigillin_review.md`](../docs/v5_fit_mor_sigillin_review.md)

### ✅ FIT (Fractal Implementation Tagebücher)
- Comprehensive docstrings
- All constants cited (CODATA, mathematical)
- Hypothesis framing (not proclamation)
- Null hypothesis testing explicit

### ✅ MOR (Multi-Orchestra-Research)
- Modular `full_analysis()` functions
- JSON-compatible outputs (via dataclasses)
- AI-agent ready interfaces
- Batch processing support

### ✅ Sigillin (Transparenz)
- Git version-controlled
- No mystical language
- Limitations explicitly documented
- Scientific neutrality maintained

**Verdict:** ✅ FULL COMPLIANCE

---

## Usage Examples

### Example 1: Quick Prediction

```python
from models.cosmic_alpha_phi import quick_prediction
from models.social_rigidity_ising import quick_rigidity

# Cosmic
v_cosmic = quick_prediction()
print(f"Cosmic velocity: {v_cosmic:.2f} km/s")

# Social
beta_social = quick_rigidity(gini=0.73)  # US 2024
print(f"Social rigidity: {beta_social:.2f}")
```

### Example 2: Full Analysis

```python
from models.cosmic_alpha_phi import full_analysis as cosmic_analysis
from models.social_rigidity_ising import full_analysis as social_analysis

# Run both
cosmic_results = cosmic_analysis(verbose=True)
social_results = social_analysis(verbose=True)
```

### Example 3: AI Agent API

```python
from api.v5_agents import v5_full_analysis, save_analysis_json

# Complete v5.0 analysis
results = v5_full_analysis(cosmic_trials=10000, social_gini=0.73)

# Export for other agents
save_analysis_json(results, 'v5_analysis.json')
```

---

## File Structure

```
models/
├── cosmic_alpha_phi.py          (443 LOC) ← Cosmic velocity
├── social_rigidity_ising.py     (498 LOC) ← Social Ising
├── v5_models_index.md           (this file)
└── models_index.{yaml,json,md}  (main index, update pending)

api/
├── v5_agents.py                 (430 LOC) ← AI interfaces
└── V5_AGENTS_README.md          (documentation)

scripts/
├── validation/
│   └── massive_monte_carlo.py   (validation script)
└── visualize_v5_duality.py      (comparative viz)

docs/
├── v5_hypothesis_isomorphism.md (scientific doc)
└── v5_fit_mor_sigillin_review.md (code review)

data/derived/
├── monte_carlo_cosmic_results.csv
├── monte_carlo_social_results.csv
└── v5_demo_analysis.json

figures/
├── monte_carlo_cosmic_heatmaps.png
├── monte_carlo_social_heatmaps.png
└── v5_duality_proof.png
```

---

## Next Steps

### For Empirical Validation
1. **Cosmic:** Search for additional systems with precise velocity measurements
2. **Social:** Acquire time-series data (Gini vs. adaptability metrics)
3. **Both:** Test predictions against new data

### For Theoretical Development
1. **Cosmic:** Develop mechanism for why α and Φ would couple to velocities
2. **Social:** Calibrate Ising parameters from real-world data
3. **Both:** Compare to alternative models (ΔAIC analysis)

### For Integration
1. Update main `models_index.{yaml,json,md}` with v5.0 entries
2. Add v5 models to CI/CD testing pipeline
3. Create LaTeX manuscript figures from validation outputs

---

## Keywords

`v5.0`, `structural-isomorphism`, `cosmic-velocity`, `social-phase-transitions`, `null-hypothesis`, `ising-model`, `fundamental-constants`, `empirical-testing`, `AI-agent-ready`

---

**Document Status:** 🟢 ACTIVE
**Change Policy:** Update upon empirical findings
**Git History:** Version-controlled source of truth
**Sigillin Type:** Bedeutungs-Sigillin (Model Documentation)

---

**Last Updated:** 2025-11-23
**Contributors:** Genesis Aeon, Johann Benjamin Römer, Claude (Documentation)
