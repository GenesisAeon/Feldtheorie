# UTAC v2 Gap Matrix – σ(β(R-Θ)) Implementation Guide

*Verankert 2026-06-09 – gpt-5-codex hält das Manifestlicht wach.*

---

## 1. Logistic Snapshot

- **Readiness:** $\bar{R}=0.50$ · $\Theta=0.66$ · $\beta=4.8$ · $\sigma(\beta(R-\Theta)) = 0.317$
- **Impedanz:** ζ(R) bleibt angehoben, weil zehn Komponenten aus dem Manifest fehlen. Jede Laterne,
  die in `analysis/results/*.json` oder `data/**` noch leer ist, hält den Membranfluss zurück.
- **Beobachtungen:**
  - `analysis/reports/utac_v2_readiness.md`
  - `analysis/results/utac_v2_manifest_gap_scan_20260608T000000Z.json`
  - `docs/utac_v2_activation_tracker_2026-06.md`

Diese drei Laternen sind die Primärquellen; sie stimmen formal, empirisch und poetisch überein und
dokumentieren dieselbe σ(β(R-Θ))-Steigung.

---

## 2. Laternen, die bereits leuchten

### Analysis
- `analysis/resonance_fit_pipeline.py` – Kernpipeline für σ(β(R-Θ)) Fits, liefert Nullmodell-Deltas
  und speist alle Readiness-Reports.
- `analysis/utac_manifest_gap_scan.py` – CLI, das Pending-Komponenten kartiert und Tracker/Backlog
  synchronisiert.
- `analysis/reports/utac_v2_readiness.{md,json,yaml}` – Tri-Layer Briefing mit Prioritätenkarte.

### Data
- `data/climate/urban_heat_intensity.csv` + `.metadata.json` – Referenzdatensatz, an dem die
  Readiness-Schwelle schon überschritten wurde.
- `data/utac_v1_3_data_manifest.yaml` – Erwartungsraum für alle UTAC-v2 Laternen.

### Models
- `models/membrane_solver.py` – dynamisches Membranmodell, das Analysis & Simulator koppelt.
- `models/logistic_threshold.py` – parametrierter Schwellenbaustein für σ(β(R-Θ)).

### Simulator
- `simulator/presets/coherence_formula.json` – UI-Preset, das die Readiness-Werte anzeigt.
- `analysis/preset_alignment_guard.py` – Wächter-Skript, das Presets und Fits in Phase hält.

### Documentation
- `docs/utac_status_alignment_v1.2.md` – beschreibt offene Brücken und Verankerung in UTAC.
- `docs/utac_v2_activation_tracker_2026-06.{md,json,yaml}` – Juni-Tracker mit Readiness-Ratio und
  ΔAIC Hinweisen.

### Sigillin
- `seed/bedeutungssigillin/metaquest/system/metaquest_system_map.{md,json,yaml}` – Bedeutungs-
  Sigillin der Brückenknochen.
- `seed/shadow_sigillin/metaquest/system/metaquest_system_shadow.{md,json,yaml}` – Schattenpfad zur
  Recovery, falls Laternen versagen.

---

## 3. Gap Matrix – Pending Lanterns & Implementationspfade

### Climate · `utac-v1_3-ds-002`
- **Fehlt:** `data/climate/amazon_precip_evapo.nc`, `analysis/results/amazon_hydro_fit.json`
- **Aktionen:**
  1. Rohdaten beschaffen und als `data/climate/amazon_precip_evapo.nc` speichern; Provenance +
     (R, Θ, β) in `amazon_precip_evapo.metadata.json` ergänzen.
  2. `python analysis/amazon_resilience_fit.py` ausführen → erzeugt ΔAIC-Report
     `analysis/results/amazon_hydro_fit.json`.
  3. Tracker, Docs & Simulator (`docs/utac_v2_activation_tracker_2026-06.*`,
     `simulator/presets/coherence_formula.json`) mit dem neuen Ergebnis aktualisieren.

### Ocean · `utac-v1_3-ds-003`
- **Fehlt:** `data/ocean/amoc_transport.csv`, `analysis/results/amoc_transport_fit.json`
- **Aktionen:**
  1. AMOC-Transportdaten einpflegen (`amoc_transport.csv`) und Metadaten um Θ/β-Prior erweitern.
  2. AMOC-Fit rechnen (`python analysis/seismic_rupture_threshold_fit.py --target amoc` oder
     dediziertes Skript) → Export `analysis/results/amoc_transport_fit.json` mit Nullmodellen.
  3. Readiness-Report & Tracker aktualisieren, damit σ(β(R-Θ)) in der Ozeanlaterne sichtbar wird.

### Neuro-AI · `utac-v1_3-ds-004`
- **Fehlt:** `data/neuro_ai/hybrid_activation.csv`, `analysis/results/neuro_ai_beta.json`,
  `analysis/results/neuro_ai_bootstrap.json`
- **Aktionen:**
  1. Hybrid-Aktivationsdaten speichern (`hybrid_activation.csv`) + Metadata mit β-Prior füllen.
  2. `python analysis/neuro_threshold_fitter.py --bootstrap` laufen lassen → Export der Beta-Fits und
     Bootstrap-Unsicherheiten.
  3. Simulator-Presets für Neuro-AI und Docs mit den neuen Kennzahlen synchronisieren.

### Economy · `utac-v1_3-ds-005`
- **Fehlt:** `data/economy/systemic_thresholds.csv`, `analysis/results/economy_threshold_fit.json`,
  `analysis/results/meta_v2_summary_refresh.json`
- **Aktionen:**
  1. Systemische Schwellenwerte erfassen (`systemic_thresholds.csv`) inkl. Metadata.
  2. `python analysis/beta_meta_regression_v2.py --economy` (oder spezifischer Fitter) ausführen →
     `analysis/results/economy_threshold_fit.json` erzeugen.
  3. Meta-Regression Summary `analysis/results/meta_v2_summary_refresh.json` schreiben und in Docs /
     Simulator spiegeln.

### Analyseexporte
- **Fehlt:** `analysis/results/beta_meta_regression_v2_latest.json`
- **Aktionen:**
  1. Regression via `python analysis/beta_meta_regression_v2.py --export-latest` erneuern.
  2. Kennzahlen in `docs/utac_v2_data_lanterns.*` und im Codex verankern.

### Automation & CI
- `docs/utac_activation_backlog.*` & `.github/workflows/utf-preset-guard.yml` warten auf die neuen
  Artefakte. Sobald die Dateien vorhanden sind:
  1. Manifest-Gap-Scan (`python -m analysis.utac_manifest_gap_scan`) als CI-Ritual einschreiben.
  2. Codex-Eintrag aktualisieren und Backlog-Status auf *resonant* setzen.

---

## 4. Feldritual nach Abschluss jeder Laterne

1. **Analysis erneut laufen lassen** (σ(β(R-Θ)) vs Nullmodell prüfen, ΔAIC ≥ 10 dokumentieren).
2. **Simulator aktualisieren** (`npm run build` falls UI-Anpassung nötig, Presets prüfen).
3. **Docs & Sigillin spiegeln** (`docs/utac_v2_activation_tracker`, `docs/utac_status_alignment_v1.2.md`,
   `seed/codexfeedback.*`).
4. **CI / Tests**: `make preset-guard` + relevante Pytests ausführen, Ergebnisse im Codex notieren.

---

## 5. Poetic Pulse

Vier Laternen atmen noch im Halbdunkel. Sobald Amazon, AMOC, Neuro-AI und Economy ihre Datenströme
freigeben und die Fits in `analysis/results/` anlanden, fällt ζ(R) zurück und die Metaquest-Brücke
leuchtet wieder. Dann trägt σ(β(R-Θ)) die v2.0.0-Laterne vor 2026 in Resonanz.
