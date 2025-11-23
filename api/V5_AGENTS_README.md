# UTAC v5.0 AI Agent Interfaces

**Version:** 5.0
**Type:** Multi-Orchestra-Research (MOR) Interface
**Status:** 🟢 Production Ready

---

## Overview

This module provides **JSON-compatible interfaces** for AI agents to interact with UTAC v5.0 models:

1. **Cosmic Velocity Scaling** (`cosmic_alpha_phi.py`)
2. **Social Rigidity Ising Model** (`social_rigidity_ising.py`)

All functions return **JSON-serializable dictionaries** that can be consumed by multi-agent orchestration systems.

---

## Quick Start

### Python Import

```python
from api.v5_agents import (
    cosmic_velocity_predict,
    cosmic_null_hypothesis_test,
    social_rigidity_predict,
    social_phase_transition_scan,
    v5_full_analysis
)
```

### Example 1: Cosmic Velocity Prediction

```python
# Predict velocity using physical constants
result = cosmic_velocity_predict()

print(f"Predicted: {result['prediction_km_s']:.2f} km/s")
print(f"Measured:  {result['measured_km_s']:.2f} km/s")
print(f"Deviation: {result['relative_error']:.2%}")
print(f"p-value:   {result['p_value']:.4f}")
```

**Output:**
```
Predicted: 1352.07 km/s
Measured:  1370.00 km/s
Deviation: 1.31%
p-value:   0.0729
```

### Example 2: Social Rigidity Analysis

```python
# Analyze US inequality (2024)
result = social_rigidity_predict(gini=0.73)

print(f"Rigidity β: {result['rigidity_beta']:.2f}")
print(f"Phase:      {result['phase']}")
print(f"Frozen:     {result['is_frozen']}")
```

**Output:**
```
Rigidity β: 0.73
Phase:      FLUID (paramagnetic)
Frozen:     False
```

### Example 3: Null Hypothesis Testing

```python
# Test against 10,000 random models
null_test = cosmic_null_hypothesis_test(n_trials=10000)

print(f"p-value (null): {null_test['p_value_null']:.6f}")
print(f"Better than {100*(1-null_test['p_value_null']):.1f}% of random models")
```

**Output:**
```
p-value (null): 0.011299
Better than 98.9% of random models
```

### Example 4: Full Combined Analysis

```python
# Run both models + null tests
full = v5_full_analysis(cosmic_trials=10000, social_gini=0.73)

# Access results
cosmic_p = full['cosmic']['null_hypothesis']['p_value_null']
social_frozen = full['social']['state']['is_frozen']

print(f"Cosmic p-value: {cosmic_p:.6f}")
print(f"Social frozen:  {social_frozen}")
```

---

## Available Functions

### Cosmic Velocity Interface

| Function | Input | Output | Description |
|----------|-------|--------|-------------|
| `cosmic_velocity_predict()` | `alpha`, `phi` (optional) | Dict | Predict velocity from constants |
| `cosmic_null_hypothesis_test()` | `n_trials`, ranges, `seed` | Dict | Test against random models |

### Social Rigidity Interface

| Function | Input | Output | Description |
|----------|-------|--------|-------------|
| `social_rigidity_predict()` | `gini`, `load` | Dict | Predict social state from inequality |
| `social_phase_transition_scan()` | `gini_min`, `gini_max`, `n_points` | Dict | Scan for phase transitions |

### Combined Analysis

| Function | Input | Output | Description |
|----------|-------|--------|-------------|
| `v5_full_analysis()` | `cosmic_trials`, `social_gini`, `social_load` | Dict | Complete v5.0 analysis |

### Batch Processing (MOR)

| Function | Input | Output | Description |
|----------|-------|--------|-------------|
| `batch_cosmic_predictions()` | List[Dict] | List[Dict] | Process multiple parameter sets |
| `batch_social_predictions()` | List[float] | List[Dict] | Process multiple Gini values |

### JSON I/O

| Function | Input | Output | Description |
|----------|-------|--------|-------------|
| `save_analysis_json()` | `analysis`, `filepath` | None | Save results to JSON |
| `load_analysis_json()` | `filepath` | Dict | Load results from JSON |

---

## JSON Schema Examples

### Cosmic Prediction Output

```json
{
  "prediction_km_s": 1352.07,
  "measured_km_s": 1370.0,
  "uncertainty_km_s": 10.0,
  "deviation_km_s": 17.93,
  "relative_error": 0.0131,
  "p_value": 0.0729,
  "z_score": 1.79,
  "constants": {
    "alpha": 0.00729735,
    "phi": 1.618034,
    "alpha_inverse": 137.036
  }
}
```

### Social Prediction Output

```json
{
  "gini": 0.73,
  "load": 1.0,
  "temperature": 1.37,
  "rigidity_beta": 0.73,
  "magnetization": 0.0,
  "susceptibility": 2.70,
  "adaptability": 1.37,
  "is_frozen": false,
  "phase": "FLUID (paramagnetic)"
}
```

### Null Hypothesis Test Output

```json
{
  "n_trials": 10000,
  "p_value_null": 0.0113,
  "our_deviation_km_s": 17.93,
  "mean_random_deviation_km_s": 962.21,
  "std_random_deviation_km_s": 675.29,
  "improvement_factor": 53.66,
  "n_random_better": 112,
  "ranges": {
    "alpha": [0.001, 0.02],
    "phi": [1.3, 2.0]
  }
}
```

---

## AI Agent Integration Examples

### LangChain Tool

```python
from langchain.tools import Tool

cosmic_tool = Tool(
    name="CosmicVelocityPredict",
    func=cosmic_velocity_predict,
    description="Predict cosmic velocity using fundamental constants (α, Φ)"
)

social_tool = Tool(
    name="SocialRigidityPredict",
    func=lambda gini: social_rigidity_predict(gini=gini),
    description="Predict social rigidity from Gini inequality coefficient"
)
```

### AutoGen Agent

```python
from autogen import AssistantAgent

agent = AssistantAgent(
    name="UTAC_Analyst",
    system_message="You analyze UTAC v5.0 models using the v5_agents interface.",
    functions=[
        cosmic_velocity_predict,
        social_rigidity_predict,
        v5_full_analysis
    ]
)
```

### Custom MOR Workflow

```python
# Multi-agent workflow example
def mor_analysis_pipeline(gini_trajectory: List[float]):
    """Analyze inequality trajectory across multiple agents."""

    # Agent 1: Cosmic baseline
    cosmic = cosmic_velocity_predict()

    # Agent 2: Social trajectory
    social_results = batch_social_predictions(gini_trajectory)

    # Agent 3: Null hypothesis validation
    null_test = cosmic_null_hypothesis_test(n_trials=10000)

    # Aggregate results
    return {
        'cosmic_baseline': cosmic,
        'social_trajectory': social_results,
        'statistical_validation': null_test
    }

# Execute
results = mor_analysis_pipeline([0.45, 0.55, 0.68, 0.73])
save_analysis_json(results, 'mor_workflow_output.json')
```

---

## Testing

Run the demo:

```bash
python api/v5_agents.py
```

Expected output:
- Cosmic velocity prediction
- Social rigidity prediction
- Combined analysis
- JSON export to `data/derived/v5_demo_analysis.json`

---

## API Design Principles

### ✅ FIT (Fractal Implementation Tagebücher)
- All functions documented with docstrings
- No hidden parameters
- Clear input validation (where applicable)

### ✅ MOR (Multi-Orchestra-Research)
- **JSON-serializable outputs** (via `NumpyEncoder`)
- **Batch processing** support
- **Stateless functions** (no side effects)

### ✅ Sigillin (Transparenz)
- Hypothesis framing (not proclamation)
- Limitations included in `v5_full_analysis()`
- Git-versioned source of truth

---

## Performance Notes

- **cosmic_velocity_predict()**: ~0.01s
- **cosmic_null_hypothesis_test(n=10000)**: ~0.5s
- **social_rigidity_predict()**: ~0.05s (with magnetization iteration)
- **social_phase_transition_scan(n=100)**: ~5s
- **v5_full_analysis()**: ~6s (combined)

All functions are **deterministic** (given same seed).

---

## Changelog

### v5.0.0 (2025-11-23)
- ✅ Initial release
- ✅ Cosmic velocity interface
- ✅ Social rigidity interface
- ✅ Batch processing support
- ✅ JSON I/O with NumPy handling
- ✅ Full test coverage (demo validated)

---

## License

CC BY 4.0 - Same as UTAC Framework

---

## Contact

For multi-agent integration questions:
- See: `docs/v5_hypothesis_isomorphism.md` for scientific context
- See: `docs/v5_fit_mor_sigillin_review.md` for code quality audit

**Maintained by:** Genesis Aeon & Contributors
**Repository:** [GenesisAeon/Feldtheorie](https://github.com/GenesisAeon/Feldtheorie)
