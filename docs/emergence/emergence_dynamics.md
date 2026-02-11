# Emergence Dynamics Report

## Stabilisation Analysis

| Scenario | Converged | Final Activation | Steps to Converge |
|----------|-----------|------------------|-------------------|
| sub-critical (β=20, d=0.1) | Yes | 0.1812 | 55 |
| critical (β=37.6, d=0.1) | Yes | 0.3696 | 72 |
| super-critical (β=50, d=0) | No | 15.7906 | N/A |
| super-critical damped (β=50, d=0.3) | Yes | 0.1488 | 26 |

## Spread Analysis

| Scenario | Peak Spread | Half-Life (steps) |
|----------|-------------|-------------------|
| low β (10) | 0.0567 | N/A |
| critical β (37.6) | 0.8897 | 69 |
| high β (60) | 0.9981 | 44 |

## Key Findings

- Concepts stabilise when `β < β_critical` or when sufficient damping (via σ_Φ buffer) is applied.
- Above `β_critical` without damping, activation diverges (runaway recursion).
- Spread velocity scales with `v_RIG`; higher β accelerates adoption.
- The σ_Φ = 0.0625 boundary acts as a natural limiter on resonance amplification.

See `analysis/results/emergence_dynamics.json` for raw data and `analysis/plots/emergence_dynamics.png` for visualisations.
