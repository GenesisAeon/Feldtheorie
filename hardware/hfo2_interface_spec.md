# HfO₂ Interface Spec (Placeholder, v0)

This specification defines a high-level AFET-compatible contract for neuromorphic
HfO₂ hardware integration pending partner co-design.

## Inputs
- `pulse_sequence`: voltage-time channel instructions.
- `sensor_feedback`: current, resistance, and temperature probes.
- `calibration_profile`: target σ_Φ corridor and β profile.

## Outputs
- `state_embedding`: latent state vector for downstream AFET modules.
- `sigma_phi_estimate`: runtime metastability estimate.
- `diagnostics`: drift, retention, and device health flags.

## Constraints
- Tick latency target: ≤5 ms.
- Thermal envelope: 0–85 °C.
- Critical stability boundary: σ_Φ < 0.055.
