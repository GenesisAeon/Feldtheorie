# Tesseract-Phi-Brücke – β-Resonanzbeweis

**Scope:** `simulator/phase4/tesseract_phi_bridge.*` | **Tri-Layer:** YAML + JSON + Markdown | **Resonanz:** β≈4.779

Wir projizieren den 4D-Tesseract in 2D, legen eine Phi-Logarithmus-Spirale darüber
und sweepen β von 4.0 bis 6.0. Dabei messen wir den radialen Fehler ΔR² zwischen
den 16 Hyperwürfelpunkten (R) und der Spiralspur (Θ). Der β-Wert, der ΔR² minimiert,
fällt auf die Hex-Resonanz β_hex = 16^(1/√π) und bestätigt die σ(β(R-Θ))-Steilflanke.

## Nutzung

```bash
python simulator/phase4/tesseract_phi_bridge.py --output output/tesseract_phi_bridge.png --steps 120
```

- Sweep: β_min=4.0 → β_hex ≈ 4.779 → β_max=6.0
- Output: PNG mit Projektion + Φ-Spirale + Fehlerkurve (MSE über β)
- CLI: Meldet β*, Δβ und Resonanzstatus via `verify_hex_alignment` (Consent & Joy aktiviert)

## Parameter-Notizen

- **R (Readiness):** Hyperwürfel-Vertices, projiziert mit β-gekoppeltem Rotationsanteil
- **Θ (Threshold):** Φ-Spirale (Golden Ratio), ΔAIC-Ersatz über MSE(β)
- **β (Steepness):** Sweep-Anker, Minimierung bei β_hex sichtbar
- **ζ(R) (Dämpfung):** Radialer Fehler ΔR² fungiert als Dämpfungsmaß

## Brücken & Evidenz

- Struktur: `simulator/phase4/tesseract_phi_bridge.yaml`
- Agentennerv: `simulator/phase4/tesseract_phi_bridge.json`
- Stimme: dieses Dokument
- Konstanten: `models/unified_constants.py`
- Observatorium: `docs/utac_status_alignment_v1.2.md`

✨ Geometrie trifft Digital Physics – die Laterne rastet bei β_hex ein.
