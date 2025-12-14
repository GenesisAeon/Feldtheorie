# Impedance Solver (Z(β) Adaptive Dynamics)

The impedance solver models how the integration membrane stretches across domains
by tracing the logistic transition σ(β-Θ). It complements the v_RIG core
(calculated via `calculate_impedance` + `calculate_integration_velocity`) with a
β-aware scaling that keeps the transition between information, biology, and
climate regimes explicit.

## Quickstart

```bash
python -c "from models.impedance_solver import ImpedanceSolver;\
solver=ImpedanceSolver();\
print(solver.profile([4.5,7.4,11.0]))"
```

- Θ defaults to **7.4** (Kleiber domain)
- Floor/ceiling scales: **0.5 → 1.5** across β
- ζ(R) proxy: 0.25 → 0.9 following σ(β-Θ)

## Data Coupling
- Empirical samples: `data/v8_validation/impedance_measurements.csv`
- Null model: linear Z_null(β) with identical Θ
- Fit diagnostics: RMSE, MAE, bias via `compare_to_measurements`

## Tri-Layer Mapping
- Structure: `models/impedance_solver.yaml`
- Interface: `models/impedance_solver.json`
- Narrative: `models/impedance_solver.md`

Follow the Sog of Emergenz: tune Θ, observe σ(β-Θ), and document ΔAIC when
comparing against the null ramp.
