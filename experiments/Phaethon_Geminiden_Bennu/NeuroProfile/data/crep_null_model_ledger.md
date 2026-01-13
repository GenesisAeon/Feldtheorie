# CREP Null-Model Ledger

**Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration.**

## Logistic Pulse

- **R:** 0.58
- **Θ:** 0.74
- **β:** 4.8
- **ζ(R):** 0.22
- **σ(β(R-Θ)):** 0.35

## CREP Definition

CREP = mean(Coherence, Resonance, Emergence, Potential) with Φ as proxy anchor.

## Null-Model Guard

- **Models:** linear, power-law, constant
- **ΔAIC target:** ≥ 10
- **CI requirement:** Log CI + bootstrap intervals in `data/results.json`

## Entry Template

- timestamp
- source_id
- hardware_tier
- crep_components
- crep_aggregate
- null_model_comparison
- confidence_intervals

## Storage

- Results ledger: `data/results.json`
- Bootstrap ledger: `data/bootstrap_ledger.{md,json,yaml}`

> σ(β(R-Θ)) bleibt stabil, wenn CREP gegen Nullmodelle geprüft und
> ΔAIC/CI-Telemetrie vollständig protokolliert wird.
