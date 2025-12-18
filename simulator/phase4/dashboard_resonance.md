# Resonanz-Panoptikum – σ(β(R-Θ)) Dashboard

**Scope:** `simulator/phase4/dashboard_resonance.*` | **Tri-Layer:** YAML + JSON + Markdown | **Resonanz:** β≈4.779

Wir legen die drei Felder übereinander und fahren den β-Slider von 4.0 über die
Hex-Resonanz bis 6.0. Das Dashboard zeigt:

1. **Soliton-Doppler (R-Kanal):** KdV-Heatmap mit Boundary-Atmen (ζ(R) wird über die History gedämpft).
2. **Chimera-Staat (Θ-Kanal):** Phasenpunkte auf dem Einheitskreis, Clusterbildung sichtbar.
3. **Cosmic Horizon (σ-Kanal):** Informationszugang P(R)=σ(β(R-Θ)) als Kurve, inkl. r_s-Marker.

Kopplungspflicht erfüllt: `verify_hex_alignment` dient als Nullmodell; Verweise auf
`feldtheorie_index.*` und `docs/utac_status_alignment_v1.2.md` sind hinterlegt.

## Nutzung

```bash
python simulator/phase4/dashboard_resonance.py --output output/resonance_cycle.mp4 --frames 180
```

- Slider fährt automatisch von β_min=4.0 → β_hex ≈ 4.779 → β_max=6.0.
- Log meldet den Resonanzdurchgang (Permission/Consent-Text inklusive).
- Ausgabe als MP4 oder GIF (Dateiendung wählen).

## Parameter-Notizen

- **R (Readiness):** Soliton-Energie im Heatmap-Verlauf.
- **Θ (Threshold):** 0.66 (Neuro-Kosmos Brücke) für Horizon-Sigmoid.
- **β (Steepness):** gemeinsamer Slider, ΔAIC-Nullmodell via Alignment-Check.
- **ζ(R) (Dämpfung):** History-Länge der Heatmap reguliert Glättung.

## Brücken & Evidenz

- Struktur: `simulator/phase4/dashboard_resonance.yaml`
- Agentennerv: `simulator/phase4/dashboard_resonance.json`
- Stimme: dieses Dokument
- Empirie: `simulator/phase4/soliton_doppler.py`, `simulator/phase4/chimera_states.py`, `simulator/phase4/cosmic_information_horizon.py`
- Observatorium: `docs/utac_status_alignment_v1.2.md`

✨ Lass die Laternen tanzen – Boundary-Breathing als Beweis der Reife (R=0.90).
