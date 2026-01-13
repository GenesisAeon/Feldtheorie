# PSRM Sigillin v1 – Mandala Extension

**Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration.**

## Logistic Pulse

- **R:** 0.58
- **Θ:** 0.74
- **β:** 4.8
- **ζ(R):** 0.22
- **σ(β(R-Θ)):** 0.35

## Zweck

Diese Extension ergänzt `psrm_sigillin_v1.*` um ein Mandala-kompatibles
`metadata.mandala_bridge`-Segment, ohne die bestehende Trilayer-Struktur zu brechen.

## Extension (Auszug)

```json
{
  "metadata": {
    "mandala_bridge": {
      "mandala_version": ">=0.8.0",
      "bridge_status": "planned",
      "validator_plan": "tests/test_neuro_profile.py::test_mandala_schema_extension_hook",
      "compatibility_notes": "PSRM bleibt additive Extension zur Mandala-Struktur."
    }
  }
}
```

> σ(β(R-Θ)) bleibt stabil, weil die Mandala-Extension als additive Laterne
> geführt wird und ζ(R) durch klare Validator-Pläne gedämpft bleibt.
