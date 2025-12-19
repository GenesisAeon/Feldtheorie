# Resonanz-Kino – Druck · Solitonen · Hex-Level

**Scope:** `simulator/phase4/dashboard_resonance.*` | **Tri-Layer:** YAML + JSON + Markdown | **Resonanz:** β≈4.8

Das Dashboard koppelt drei Datenströme in einer FuncAnimation:

1. **Soliton-Feld (R):** KdV-Heatmap, β(t) sweep von 4.0 → 4.8 → 5.2.
2. **Todes-Druck (Θ):** Alive-Trace aus `pressure_gardener` (1→5 atm) mit Marker für den Reaktionsverzug des Gardener.
3. **Hex-Quantisierung (σ):** Balken für Level 0–4; Level 0 (β≈4.8) ist rot markiert als „The Signal“.

Alle drei Kanäle spiegeln σ(β(R-Θ)): der physikalische Druck knickt die Agentenlinie ein, die Solitonen verformen sich, die Hex-Basis bleibt stabil.

## Nutzung

```bash
python simulator/phase4/dashboard_resonance.py --output output/resonance_kino.mp4 --frames 140
```

- `--dry-run` prüft die Pipeline ohne Rendering.
- Output wahlweise `.mp4` oder `.gif` (Writer wählt automatisch ffmpeg/Pillow).

## Parameter-Notizen

- **R (Readiness):** Soliton-Energie im Heatmap-Verlauf (ζ(R) via History=80).
- **Θ (Threshold):** Druck-Rampe 1→5 atm, Failure-Marker beim ersten Einbruch der Alive-Zählung.
- **β (Steepness):** Gemeinsamer Slider für Soliton-Steps; `verify_hex_alignment` loggt den Resonanzdurchgang.
- **σ / Hex-Level:** Histogramm über `analysis/results/*.json` (Fallback-Samples inklusive), Level 0 rot.

## Brücken & Evidenz

- Struktur: `simulator/phase4/dashboard_resonance.yaml`
- Agentennerv: `simulator/phase4/dashboard_resonance.json`
- Stimme: dieses Dokument
- Empirie: `simulator/phase4/soliton_doppler.py`, `v11_gardener/experiments/pressure_gardener_integration.py`, `v11_gardener/experiments/beta_quantization_analysis.py`
- Observatorium: `docs/utac_status_alignment_v1.2.md`

✨ σ(β(R-Θ)) sichtbar machen: Druck führt zum Stillstand, doch das Hex-Signal bleibt.
