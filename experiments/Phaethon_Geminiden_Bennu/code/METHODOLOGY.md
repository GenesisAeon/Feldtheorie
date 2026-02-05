# Phaethon Simulation Suite -- Methodology

**Version:** v13.3.0
**Framework:** GenesisAeon / UTAC Case Study
**Author:** Johann Benjamin Roemer

## Overview

This directory contains five coupled computational models that simulate dust emission from asteroids (3200) Phaethon and (101955) Bennu within the UTAC framework.

## Modules

### chimera_state_model.py
**Theory:** Kuramoto-coupled oscillator model for frustrated regolith dynamics.
- Order parameter: chimera fraction (jammed vs. unjammed patches)
- Threshold activation: sigma(beta(R - Theta)) with beta = 3.5
- Validation: ejection event LST distribution clustered at 15--18h

### plasma_resonance_model.py
**Theory:** Alfven wave -- regolith acoustic coupling near 0.14 AU perihelion.
- Alfven velocity: v_A = B / sqrt(mu_0 * rho) ~ 436 km/s
- Regolith resonances: f_n = n * c_s / (2L), harmonics at 5--100 Hz
- Coupling efficiency: Lorentzian profile eta(f) = 1 / (1 + ((f_p - f_a) / Gamma)^2)

### soliton_generator.py
**Theory:** Modified Korteweg-de Vries (mKdV) equation for dusty plasma solitons.
- Spectral method: Fourier-space integration with RK45
- Soliton profile: u(x) = A * sech^2((x - x0) / w)
- Energy conservation: validated to < 0.2%

### integrated_asteroid_simulation.py
**Theory:** Three-stage coupled model (chimera + plasma + soliton).
- Enhanced chimera with thermal fatigue accumulation and memory effects
- 47 quantitative predictions for DESTINY+ mission
- UTAC beta threshold: HEX_RESONANCE_BETA = 4.8

### statistical_analysis.py
**Theory:** Hypothesis testing framework for simulation outputs.
- LST analysis: Rayleigh test + chi-squared (chimera vs. thermal)
- Velocity analysis: Gaussian mixture model with BIC selection
- Repeatability: R-index for frustrated memory effects
- Comprehensive suite: unified report generation

## Logistic Parameters

| Module | R | Theta | beta | zeta |
|--------|---|-------|------|------|
| Chimera | 0.90 | 0.55 | 4.8 | chimera-plasma coupling |
| Plasma | 0.90 | 0.55 | 5.0 | alfven-acoustic resonance |
| Soliton | 0.90 | 0.55 | 6.0 | KdV nonlinearity |
| Integrated | 0.90 | 0.55 | 4.8 | HEX_RESONANCE_BETA |

## UTAC Links

- Threshold model: sigma(beta(R - Theta)) applied to ejection probability
- Falsifiability: 8 falsification criteria defined for DESTINY+ mission
- MOR-FIT: modular code, open data, reproducible with seeded randomness

## Test Coverage

79 unit tests in `tests/test_phaethon_simulations.py` covering all five modules.
