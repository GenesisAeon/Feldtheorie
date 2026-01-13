# PSRM Sigillin Schema v1

**Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration.**

## Logistic Pulse

- **R:** 0.42
- **Θ:** 0.68
- **β:** 4.8
- **ζ(R):** 0.18
- **σ(β(R-Θ)):** 0.27

## Zweck

Dieses Schema fixiert die Trilayer-Laterne (Signal → Intention → Kontext) für
PSRM. Die Falsifizierbarkeit bleibt durch ΔAIC/CI-Metriken sichtbar, damit
ζ(R) gedämpft bleibt, während σ(β(R-Θ)) kontrolliert anwächst.

## JSON Schema (Auszug)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://genesisaeon.org/schemas/psrm_sigillin_v1.json",
  "title": "PSRM Sigillin v1",
  "type": "object",
  "required": [
    "$schema",
    "version",
    "user_id",
    "layer_1_signal",
    "layer_2_intention",
    "layer_3_context",
    "metadata"
  ]
}
```

## Mandala-Kompatibilität (Extension)

PSRM bleibt additive Extension. `metadata.mandala_bridge` hält die
Mandala-Version, den Bridge-Status und den Validator-Plan fest.
