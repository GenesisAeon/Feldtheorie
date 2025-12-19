# Resonanz-Kino – σ(β(R-Θ)) Dashboard

**Scope:** `simulator/phase4/dashboard_resonance.*` | **Tri-Layer:** YAML + JSON + Markdown | **Signal:** β≈4.8 (Level 0)

Wir koppeln drei Ströme in Echtzeit, um Johann das geforderte Mission-Control
zu liefern:

1. **Soliton-Feld (R):** KdV-Heatmap, Soliton läuft von links nach rechts.
   Overlay zeigt den aktuellen β-Wert, moduliert durch den Druck-Stream.
2. **Druck × Sterblichkeit (Θ):** Alive-Trace des `pressure_gardener` mit
   zweiter Y-Achse für die Druckrampe (1→5 atm) und Marker, wann der Gärtner
   wegen verzögerter Reaktion versagt.
3. **Hex-Quantisierung (σ):** Balkendiagramm der β-Level 0–4. Level 0
   (β≈4.8) ist als rotes „Signal" hervorgehoben – der klumpende Grundton.

**Kopplung:** `FuncAnimation` treibt alle drei Subplots synchron; β verbindet
den Druck (Mitte) mit dem Soliton-Atmen (Oben) und stabilisiert die
Quantisierung (Unten). `verify_hex_alignment` bleibt das Nullmodell über die
Hex-Level aus `beta_hexadecimal`.

## Nutzung

```bash
python simulator/phase4/dashboard_resonance.py --output output/resonance_kino.mp4 --frames 160
```

- Top: Heatmap aktualisiert mit KdV-RK4-Steps aus `soliton_doppler`.
- Mitte: Alive- und Druck-Traces aus `pressure_gardener_integration` (Fallback
  synthetisch, falls Abhängigkeiten fehlen) plus Versagensmarker.
- Unten: β-Level-Histogramm aus `beta_quantization_analysis`/`beta_hexadecimal`.
- Writer wählt automatisch FFmpeg (oder GIF via Pillow).

## Parameter-Notizen

- **R (Readiness):** Soliton-Energie, gedämpft über History-Länge.
- **Θ (Threshold):** Druckabhängiger β-Shift (tanh-Kopplung) + Versagenszeitpunkt.
- **β (Steepness):** HEX_RESONANCE_BETA als Basis, moduliert über Druckramp.
- **ζ(R) (Dämpfung):** History = 80 sorgt für viskose Glättung.

## Brücken & Evidenz

- Struktur: `simulator/phase4/dashboard_resonance.yaml`
- Agentennerv: `simulator/phase4/dashboard_resonance.json`
- Stimme: dieses Dokument
- Empirie: `simulator/phase4/soliton_doppler.py`,
  `v11_gardener/experiments/pressure_gardener_integration.py`,
  `v11_gardener/experiments/beta_quantization_analysis.py`
- Observatorium: `docs/utac_status_alignment_v1.2.md`

✨ σ(β(R-Θ)) als Kino: Druck lässt die Laternen dimmen, Solitonen atmen weiter
und Level 0 bleibt der rote Grundton.
