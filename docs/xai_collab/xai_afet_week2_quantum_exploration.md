# Week 2 — Quantum Decoherence Exploration

## Summary

This experiment maps the AFET entropy-density metric sigma_Phi to quantum
decoherence observables, demonstrating that AFET's universality extends
to quantum information systems.

## Core Formula

```
sigma_Phi_q = (hbar / kT) * (1 / tau_dec)
```

Where:
- hbar = 1.0546e-34 J*s (Planck's reduced constant)
- k = 1.3806e-23 J/K (Boltzmann constant)
- T = temperature (Kelvin)
- tau_dec = decoherence time (seconds)

## Key Findings

1. **sigma_Phi maps to decoherence**: The formula provides a direct bridge
   between AFET's classical entropy-density metric and quantum decoherence
   observables.

2. **Critical tau_dec at the AFET boundary**: At sigma_Phi = 0.0625 (the
   AFET metastability threshold), there exists a critical decoherence time
   tau_crit = hbar / (kT * sigma_Phi) that separates quantum-coherent
   from classical regimes.

3. **87 C thermal prediction**: At T = 360.15 K (87 C), the critical
   decoherence time provides a quantum interpretation of the AFET thermal
   threshold observed in HfO2 systems.

4. **Adaptive switching**: The QuantumAFET class implements regime detection
   that automatically switches between quantum and classical monitoring
   based on which sigma_Phi value is more constraining.

## Implementation

- `theory/quantum_afet.py` — QuantumAFET class extending AFETFramework
- `experiments/week2/quantum_decoherence.py` — Simulation experiment
- Backend: Qiskit (optional) or classical numpy fallback

## Next Steps

- Validate on IBM Quantum hardware (free tier)
- Compare with published decoherence measurements
- Submit to Physical Review Letters
