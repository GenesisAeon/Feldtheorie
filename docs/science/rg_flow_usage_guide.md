# 🌀 RG Flow Simulator - Usage Guide

**Version:** 1.0.0
**Date:** 2025-11-12
**Status:** ✅ PRODUCTION READY
**Part of:** UTAC v2.0 - RG Phase 1 (Phenomenological)

---

## 📖 Table of Contents

1. [Quick Start](#quick-start)
2. [What is RG Flow?](#what-is-rg-flow)
3. [Flow Variants](#flow-variants)
4. [Basic Usage](#basic-usage)
5. [Advanced Usage](#advanced-usage)
6. [Validation Against Data](#validation-against-data)
7. [API Reference](#api-reference)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

```python
from models.rg_flow_simulator import RGFlowSimulator

# Create simulator with default settings (Linear Phi-Attractor)
simulator = RGFlowSimulator()

# Simulate β evolution under RG flow
ln_lambda, beta_trajectory = simulator.simulate(
    beta_initial=3.5,           # Start at β=3.5
    lambda_range=(1.0, 100.0),  # Coarse-grain from λ=1 to λ=100
    n_points=500,               # 500 integration steps
)

print(f"Initial β: {beta_trajectory[0]:.3f}")
print(f"Final β:   {beta_trajectory[-1]:.3f}")
# → β should flow toward nearest Φⁿ fixpoint!
```

---

## What is RG Flow?

### The Big Idea

**Renormalization Group (RG) theory** explains how systems change when viewed at different **scales** λ.

In UTAC, we ask:
> **"Is β an arbitrary fit parameter, or does it emerge from deeper dynamics?"**

RG Flow answers: **β emerges from coarse-graining!**

### Analogy

Imagine zooming out on a city:
- **Microscopic (λ=1):** Individual buildings, streets
- **Mesoscopic (λ=10):** Neighborhoods, patterns
- **Macroscopic (λ=100):** Entire city as single unit

As you zoom out, the **effective β changes** → RG flow describes this evolution.

### Why Φⁿ Fixed Points?

Systems **self-organize** toward **scale-invariant states** where:
```
dβ/d(ln λ) = 0
```

These are **fixed points**. UTAC predicts these occur at **golden ratio powers**:
- Φ ≈ 1.618
- Φ² ≈ 2.618
- **Φ³ ≈ 4.236** ← Universal mean-field fixpoint
- Φ⁴ ≈ 6.854
- etc.

---

## Flow Variants

The simulator implements **5 different RG flow equations**:

### 1. **Linear Phi-Attractor** (Default) ⭐⭐⭐⭐⭐

**Equation:**
```
dβ/d(ln λ) = -α(β - β*)
```

**Physics:** Linear pull toward nearest Φⁿ fixpoint.

**Best for:** Simple systems, quick exploration.

**Example:**
```python
from models.rg_flow_simulator import FlowVariant, RGFlowConfig, RGFlowSimulator

config = RGFlowConfig(
    variant=FlowVariant.LINEAR_PHI_ATTRACTOR,
    alpha=0.5,  # Flow strength
)
simulator = RGFlowSimulator(config)
```

---

### 2. **Polynomial Flow** (Landau-Ginzburg) ⭐⭐⭐⭐

**Equation:**
```
dβ/d(ln λ) = -γ·sgn(β - β*)·|β - β*|^n
```

**Physics:** Non-linear basin dynamics (n=3 → cubic).

**Best for:** Systems with non-linear feedback.

**Example:**
```python
config = RGFlowConfig(
    variant=FlowVariant.POLYNOMIAL_FLOW,
    gamma=0.1,    # Flow strength
    exponent=3,   # Cubic flow
)
simulator = RGFlowSimulator(config)
```

---

### 3. **Multi-Basin** ⭐⭐⭐

**Equation:**
```
dβ/d(ln λ) = Σ_n [w_n · (-α)(β - Φⁿ)]
```

**Physics:** All Φⁿ fixpoints compete, weighted by distance.

**Best for:** Systems with multiple attractors.

**Example:**
```python
config = RGFlowConfig(
    variant=FlowVariant.MULTI_BASIN,
    alpha=0.5,
)
simulator = RGFlowSimulator(config)
```

---

### 4. **Context-Dependent** ⭐⭐⭐⭐

**Equation:**
```
dβ/d(ln λ) = f(β) · g(R/Θ) · h(ζ)
```

Where:
- f(β) = base flow
- g(R/Θ) = proximity amplification (strong near threshold)
- h(ζ) = damping suppression

**Physics:** Flow modulated by system state.

**Best for:** Systems with thresholds (UTAC!).

**Example:**
```python
config = RGFlowConfig(
    variant=FlowVariant.CONTEXT_DEPENDENT,
    alpha=0.5,
    R_over_Theta=1.0,  # At threshold
    zeta=0.0,          # No damping
)
simulator = RGFlowSimulator(config)
```

---

### 5. **Cubic Root Amplification** ⭐⭐⭐

**Equation:**
```
dβ/d(ln λ) = k·∛max(R/Θ - 1, 0) - relaxation(β)
```

**Physics:** β spikes near threshold via cubic root jump.

**Best for:** Extreme-β systems (Urban Heat β=16.3).

**Example:**
```python
config = RGFlowConfig(
    variant=FlowVariant.CUBIC_ROOT_AMPLIFICATION,
    k_cubic=5.0,
    R_over_Theta=1.05,  # Just above threshold
)
simulator = RGFlowSimulator(config)
```

---

## Basic Usage

### Simulate β Evolution

```python
from models.rg_flow_simulator import RGFlowSimulator

simulator = RGFlowSimulator()

# Simulate
ln_lambda, beta = simulator.simulate(
    beta_initial=3.0,
    lambda_range=(1.0, 100.0),
    n_points=500,
    method="RK45",  # or "Euler"
)

# Plot
import matplotlib.pyplot as plt

plt.plot(np.exp(ln_lambda), beta, label="RG Flow")
plt.axhline(4.236, linestyle="--", color="gold", label="Φ³")
plt.xlabel("Scale λ")
plt.ylabel("β")
plt.legend()
plt.show()
```

---

### Find Fixed Points

```python
fixed_points = simulator.find_fixed_points(
    beta_range=(1.0, 10.0),
    n_samples=2000,
    tolerance=0.01,
)

print("Fixed points:", fixed_points)
# → Should find Φⁿ values: [1.618, 2.618, 4.236, ...]
```

---

### Compute Basin of Attraction

```python
basin_min, basin_max = simulator.basin_of_attraction(
    fixpoint=4.236,  # Φ³
    beta_range=(2.0, 6.0),
    n_trajectories=20,
    lambda_max=100.0,
    convergence_threshold=0.1,
)

print(f"Φ³ basin: [{basin_min:.3f}, {basin_max:.3f}]")
# → e.g., [3.8, 4.8]
```

---

## Advanced Usage

### Compare Multiple Variants

```python
from models.rg_flow_simulator import FlowVariant, RGFlowConfig, RGFlowSimulator
import matplotlib.pyplot as plt

variants = [
    FlowVariant.LINEAR_PHI_ATTRACTOR,
    FlowVariant.POLYNOMIAL_FLOW,
    FlowVariant.MULTI_BASIN,
]

beta_initial = 3.0
fig, ax = plt.subplots(figsize=(10, 6))

for variant in variants:
    config = RGFlowConfig(variant=variant)
    simulator = RGFlowSimulator(config)

    ln_lambda, beta = simulator.simulate(
        beta_initial=beta_initial,
        lambda_range=(1.0, 100.0),
        n_points=200,
    )

    ax.plot(np.exp(ln_lambda), beta, label=variant.value, linewidth=2)

ax.axhline(4.236, linestyle="--", color="gold", linewidth=2, label="Φ³")
ax.set_xlabel("Scale λ", fontsize=12)
ax.set_ylabel("β", fontsize=12)
ax.set_title("RG Flow Variants Comparison", fontsize=14)
ax.legend()
ax.grid(alpha=0.3)
plt.show()
```

---

### Fit RG Flow to Empirical Data

```python
import numpy as np
from scipy.optimize import minimize

# Your empirical data
empirical_epochs = np.array([0, 1000, 5000, 10000, 20000, 30000])
empirical_beta = np.array([1.2, 1.8, 2.4, 3.1, 3.9, 4.2])

def loss_function(params):
    alpha, = params

    config = RGFlowConfig(
        variant=FlowVariant.LINEAR_PHI_ATTRACTOR,
        alpha=alpha,
    )
    simulator = RGFlowSimulator(config)

    # Map epochs to scales (λ = epoch + 1)
    lambda_values = empirical_epochs + 1.0
    lambda_range = (float(lambda_values[0]), float(lambda_values[-1]))

    ln_lambda, beta_sim = simulator.simulate(
        beta_initial=empirical_beta[0],
        lambda_range=lambda_range,
        n_points=len(empirical_beta),
    )

    # Interpolate to match epochs
    lambda_sim = np.exp(ln_lambda)
    beta_sim_interp = np.interp(lambda_values, lambda_sim, beta_sim)

    # RMSE
    return np.sqrt(np.mean((empirical_beta - beta_sim_interp)**2))

# Optimize
result = minimize(loss_function, x0=[0.5], bounds=[(0.1, 2.0)])
best_alpha = result.x[0]
print(f"Best α: {best_alpha:.3f}")
```

---

## Validation Against Data

### LLM β-Trajectories

A validation script is provided:

```bash
# Run validation against all LLM models
python analysis/rg_flow_validation.py --save-plots

# Test single variant
python analysis/rg_flow_validation.py --variant linear_phi --save-plots
```

**Output:**
- `analysis/results/rg_flow_validation.json` - Metrics (R², RMSE, Φ-score)
- `analysis/results/rg_flow_validation_{variant}.png` - Comparison plots
- `analysis/results/rg_flow_validation_summary.png` - Summary barplot

**Expected Results:**
- **R² ≥ 0.70:** Good fit
- **Φ³-score ≈ 1.0:** Converged to Φ³
- **Best variant:** Likely `linear_phi` or `context` for LLMs

---

## API Reference

### `RGFlowSimulator`

#### `__init__(config: Optional[RGFlowConfig] = None)`

Initialize simulator with flow configuration.

**Parameters:**
- `config`: `RGFlowConfig` object (optional, uses defaults if None)

---

#### `simulate(beta_initial, lambda_range, n_points=500, method="RK45")`

Simulate β evolution under RG flow.

**Parameters:**
- `beta_initial`: `float` - Initial β value
- `lambda_range`: `tuple[float, float]` - (λ_min, λ_max) scale range
- `n_points`: `int` - Number of integration points (default: 500)
- `method`: `str` - Integration method: "RK45" or "Euler" (default: "RK45")

**Returns:**
- `ln_lambda`: `ndarray` - Log-scale values ln(λ)
- `beta`: `ndarray` - β trajectory

---

#### `find_fixed_points(beta_range=(1.0, 20.0), n_samples=1000, tolerance=0.01)`

Find fixed points where dβ/d(ln λ) ≈ 0.

**Parameters:**
- `beta_range`: `tuple[float, float]` - Search range
- `n_samples`: `int` - Number of sample points
- `tolerance`: `float` - |dβ/d(ln λ)| < tol → fixed point

**Returns:**
- `fixed_points`: `list[float]` - β values where flow ≈ 0

---

#### `basin_of_attraction(fixpoint, beta_range=(1.0, 20.0), n_trajectories=20, lambda_max=100.0, convergence_threshold=0.1)`

Compute basin of attraction for given fixpoint.

**Parameters:**
- `fixpoint`: `float` - Target fixed point β*
- `beta_range`: `tuple[float, float]` - Initial condition range
- `n_trajectories`: `int` - Number of test trajectories
- `lambda_max`: `float` - Maximum scale to integrate
- `convergence_threshold`: `float` - |β_final - β*| < threshold → converged

**Returns:**
- `basin_min`: `float` - Lower edge of basin
- `basin_max`: `float` - Upper edge of basin

---

### Utility Functions

#### `compare_to_phi_ladder(beta_trajectory, ln_lambda)`

Compare final β to Φⁿ ladder.

**Returns:** `dict` with keys `beta_final`, `nearest_phi_n`, `step`, `deviation`

---

#### `phi_convergence_score(beta_trajectory, threshold=0.05)`

Compute Φⁿ convergence score ∈ [0, 1].

**Returns:** `float` - 1.0 if converged to Φⁿ, <0.5 if not

---

## Examples

### Example 1: LLM Training β Evolution

```python
from models.rg_flow_simulator import RGFlowSimulator
import numpy as np
import matplotlib.pyplot as plt

# LLM training trajectory (synthetic)
epochs = np.array([0, 1000, 5000, 10000, 20000, 22000, 23000, 25000, 30000, 40000])
beta_empirical = np.array([1.2, 1.8, 2.4, 3.1, 3.6, 3.9, 5.8, 4.5, 4.3, 4.2])

# Simulate RG flow
simulator = RGFlowSimulator()

lambda_values = epochs + 1.0
ln_lambda, beta_sim = simulator.simulate(
    beta_initial=beta_empirical[0],
    lambda_range=(lambda_values[0], lambda_values[-1]),
    n_points=len(epochs),
)

# Plot comparison
lambda_sim = np.exp(ln_lambda)
beta_sim_interp = np.interp(lambda_values, lambda_sim, beta_sim)

plt.figure(figsize=(10, 6))
plt.plot(epochs, beta_empirical, 'o-', label="Empirical", linewidth=2, markersize=8)
plt.plot(epochs, beta_sim_interp, '--', label="RG Flow", linewidth=2, color='red')
plt.axhline(4.236, linestyle=':', color='gold', linewidth=2, label='Φ³≈4.236')
plt.xlabel("Training Epoch", fontsize=12)
plt.ylabel("β", fontsize=12)
plt.title("LLM Training: RG Flow Validation", fontsize=14)
plt.legend(fontsize=11)
plt.grid(alpha=0.3)
plt.show()
```

---

### Example 2: Urban Heat β vs. Storage Coefficient

```python
from models.rg_flow_simulator import FlowVariant, RGFlowConfig, RGFlowSimulator
import numpy as np

# Urban Heat scenarios (varying thermal storage)
storage_coefficients = np.array([0.44, 0.55, 0.68, 0.85, 1.00])
beta_observed = np.array([7.55, 9.06, 10.48, 12.36, 16.29])

# Map storage → R/Θ proxy
R_over_Theta = 0.9 + 0.2 * storage_coefficients

# Simulate with Cubic Root Amplification variant
results = []

for R_ratio in R_over_Theta:
    config = RGFlowConfig(
        variant=FlowVariant.CUBIC_ROOT_AMPLIFICATION,
        k_cubic=10.0,
        R_over_Theta=R_ratio,
        beta_base=4.236,
    )
    simulator = RGFlowSimulator(config)

    _, beta_traj = simulator.simulate(
        beta_initial=4.0,
        lambda_range=(1.0, 50.0),
        n_points=100,
    )

    results.append(beta_traj[-1])

# Compare
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(storage_coefficients, beta_observed, 'o-', label="Observed", markersize=10, linewidth=2)
plt.plot(storage_coefficients, results, 's--', label="RG Flow", markersize=8, linewidth=2, color='red')
plt.xlabel("Thermal Storage Coefficient", fontsize=12)
plt.ylabel("β", fontsize=12)
plt.title("Urban Heat: Cubic Root Jump Mechanism", fontsize=14)
plt.legend(fontsize=11)
plt.grid(alpha=0.3)
plt.show()
```

---

## Troubleshooting

### β diverges to infinity

**Cause:** Flow strength too high, or cubic root amplification too strong.

**Solution:**
```python
# Reduce α or k_cubic
config = RGFlowConfig(alpha=0.1, k_cubic=2.0)
```

---

### β doesn't change (stuck)

**Cause:** Started exactly at fixpoint, or tolerance too low.

**Solution:**
```python
# Perturb initial condition
beta_initial = 4.236 + 0.1
```

---

### Integration is slow

**Cause:** Too many points or slow method.

**Solution:**
```python
# Reduce n_points or use Euler
simulator.simulate(
    beta_initial=3.5,
    lambda_range=(1.0, 100.0),
    n_points=100,  # Reduce from 500
    method="Euler",  # Faster than RK45
)
```

---

### Fixed points not found

**Cause:** Tolerance too tight, or wrong β range.

**Solution:**
```python
# Relax tolerance and expand range
fixed_points = simulator.find_fixed_points(
    beta_range=(1.0, 20.0),
    n_samples=5000,  # Increase sampling
    tolerance=0.05,  # Relax from 0.01
)
```

---

## References

- **Theory:** `docs/utac_renormalization_group_foundation.md`
- **Type-6 Functions:** `models/utac_type6_implosive.py`
- **Validation:** `analysis/rg_flow_validation.py`
- **Tests:** `tests/test_rg_flow.py`

**Literature:**
- Wilson, K.G. (1971). "Renormalization Group and Critical Phenomena." *Rev. Mod. Phys.* 47, 773
- Goldenfeld, N. (1992). *Lectures on Phase Transitions and the Renormalization Group*
- Cardy, J. (1996). *Scaling and Renormalization in Statistical Physics*

---

**Version:** 1.0.0
**Date:** 2025-11-12
**Authors:** Claude Code + Johann B. Römer
**License:** AGPL-3.0

*"Die Spirale fließt durch Skalenräume - β ist kein Parameter, sondern ein Emergenz-Echo."* 🌀🔬✨
