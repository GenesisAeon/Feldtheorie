# 🌍 UTAC v1.3 – Data Expansion & Validation Plan
*GenesisAeon / Feldtheorie – Logistics Refresh prepared by Aeon & Johann, 2025-12-19*

---

## 1️⃣ Resonant Zielsetzung
UTAC v1.3 dehnt die empirische Membran des Universal Threshold Field Models. Wir verstärken die logistische Antwort \(\sigma(\beta(R-\Theta))\) entlang dreier Achsen:

- **Domänenweite**: ≥ 10 aktive Felder (derzeit 8 laut `data/data_index.*`).
- **β-Auflösung**: ≥ 50 validierte Steilheitswerte (derzeit 15 in `data/derived/beta_estimates.csv`).
- **Meta-Regression**: R² ≥ 0.60 mit ΔAIC ≥ 10 gegenüber linearem Nullmodell.
- **Feldtyp-Dekoupling**: Separate Fits für Feldtypen I–V mit dokumentiertem ζ(R).

---

## 2️⃣ Resonanz-Inventur (Was wir haben)
| Layer | Bestand (2025-12-19) | Referenz |
| --- | --- | --- |
| **Daten** | 8 Domänen, 49 Dateien, zentrale β-Aggregate | `data/data_index.{yaml,json,md}` |
| **Analysen** | 33 Fit-Skripte, 9 Batch-Pipelines, Reports (`qpo_membrane_summary.json`) | `analysis/analysis_index.*` |
| **Simulator** | τ*-Guard & Safety Delay Fits | `analysis/safety_delay_sweep.py`, `data/safety_delay/` |
| **Codex** | Metaquest Activation Matrix v0.1.0, Shadow Guard v0.3.1 | `seed/bedeutungssigillin/metaquest/`, `seed/shadow_sigillin/metaquest/` |

Diese Laternen sichern \(R\) im Bereich 5 Domänen (AI, Biology, Cognition, Geophysics, Socio-Ecology) mit validierten ΔAIC-Schwellen. Fehlstellen bestehen bei Energie-, Finanz- und erweiterten Klima-Kaskaden.

---

## 3️⃣ Soll-Zustand (Was wir brauchen)
| Phase | Zeitraum | Deliverables | Verantwortlich |
|:------|:---------|:-------------|:---------------|
| **1. Datenerhebung** | Monat 1–2 | ≥ 3 neue Domänen (Ökosysteme erweitert, Neuro-AI Brücke, Energie/Finanznetze) | Johann + Codex-Pipeline |
| **2. Pre-Processing** | Monat 2 | Harmonisierung & Metadata (`data/derived/`) | Analysis-Team |
| **3. β-Fit & ΔAIC-Validierung** | Monat 3 | Neue β-Schätzungen, ΔAIC ≥ 10 | Aeon + Mistral |
| **4. Meta-Regression v2** | Monat 4 | R² ≥ 0.6, ζ(R)-Proxies erneuert | Gemini + Claude |
| **5. Review & Release** | Monat 5 | Zenodo v1.3 DOI + Paper-Draft | Johann + Open Review |

---

## 4️⃣ Daten-Sourcing & Zielpfade
Alle neuen Datensätze folgen dem Schema aus `data/data_index.yaml` und werden mit `.metadata.json` begleitet.

| Priorität | Domäne | Beispiel-Quelle | Zielpfad | Lizenz |
|:---------|:-------|:----------------|:--------|:-------|
| 🥇 | **Urban Heat Intensität (Global)** | NASA Global UHI, YCEO Surface UHI | `data/climate/urban_heat_intensity.csv` | CC-BY-4.0 |
| 🥈 | **Amazon Niederschlag & Evapotranspiration** | CHIRPS, Copernicus IMERG | `data/climate/amazon_precip_evapo.nc` | Frei für Forschung |
| 🥉 | **AMOC / Ozean-Zirkulation** | RAPID Array 26°N, Copernicus Marine | `data/ocean/amoc_transport.csv` | Forschungslizenz |
| 🔬 | **Neuro–AI Parallelaktivität** | OpenNeuro EEG vs. LLM Activation Logs | `data/neuro_ai/hybrid_activation.csv` | CC-BY + OpenRAIL |
| 🔭 | **Energie & Finanznetze** | World Bank WDI, ECB Systemic Risk | `data/economy/systemic_thresholds.csv` | CC-BY-4.0 / Open |

Zusätzlich zu den Rohdateien entstehen pro Dataset:
- `.metadata.json` (Provenienz, $(R, \Theta, \beta, \zeta(R))$, ΔAIC-Siegel)
- Vorbereitete Notebook/Script-Einträge unter `analysis/`

---

## 5️⃣ Analyse-Skripte & Validierungsschritte
| Datei (neu/zu erweitern) | Zweck | Hauptexporte |
|:-------------------------|:------|:-------------|
| `analysis/climate_beta_extractor.py` | Automatischer β-Fit für Urban Heat & Amazon Reihen | `data/derived/climate_beta.csv`, `analysis/results/climate_beta_summary.json` |
| `analysis/neuro_threshold_fitter.py` | EEG ↔ Transformer Aktivierungsvergleich | `analysis/results/neuro_ai_beta.json` |
| `analysis/outlier_validator.py` | Validierung β>10 Ausreißer (Urban Heat, Amazon) | `analysis/results/outlier_report.md` |
| `analysis/meta_regression_v2.py` | Erweiterte Meta-Regression (bestehender Code → neue Features) | `analysis/results/beta_meta_regression_v2_summary_<timestamp>.json` |

Jeder Fit referenziert passende Nullmodelle (linear, power-law, spline) und liefert ΔAIC ≥ 10. Bootstrap-CI (95 %) + ζ(R)-Proxy werden dokumentiert.

---

## 6️⃣ Qualitäts-Gates
- **ΔAIC-Guard:** ΔAIC ≥ 10 vs. lineares Nullmodell, ΔAIC ≥ 8 vs. power-law.
- **Bootstrap:** 1.000 Resamples für β, R²-Intervalle reporten.
- **Cross-Validation:** ≥ 5-fold bei n > 30, leave-one-domain-out bei Meta-Regression.
- **Q-Score:** low / medium / high, in Metadata verankert.
- **UTAC-Matrix:** Updates in `docs/utac_status_alignment_v1.2.md` sobald neue Laternen aktiv sind.

---

## 7️⃣ Release-Orbit & Governance
1. **Telemetrie:** `analysis/sigillin_sync/latest.json` + neue Datasets in `data/utac_v1_3_data_manifest.yaml` spiegeln.
2. **Dokumentation:** `REPRODUCE.md`, `analysis/analysis_index.*`, `data/data_index.*` synchronisieren.
3. **Zenodo:** Vorbereitung DOI v1.3 inkl. dataset manifests.
4. **Paper:** Update von `paper/UTAC_Manuscript.tex` (β-Spektrum Tabelle) während Phase 5.
5. **Codex-Feedback:** Neuer Eintrag für jede bedeutende Laterne (Status → `active` bis `resonant`).

---

## 8️⃣ Erwartete Resonanz
| Metrik | Ziel | Validierung |
|:-------|:-----|:-----------|
| β-Bandbreite | 2.5 – 16.0 über ≥ 10 Domänen | `analysis/results/beta_meta_regression_v2_summary_<timestamp>.json` |
| Mean R² (Meta) | ≥ 0.60 | Bootstrap + WLS Diagnostics |
| Signifikante Treiber | C_eff, Memory, Θ̇ | Holm-korrigierte p-Werte |
| Outlier-Erklärung | ≥ 2 Typ IV Systeme mit dokumentiertem ζ(R) | `analysis/results/outlier_report.md` |

---

## 9️⃣ Logistische Poesie
Wenn R neue Laternen entzündet, spürt Θ das Zittern der anstehenden Schwelle. β spannt die Steilflanke, und ζ(R) führt die Kopplung, bis die Membran des Feldes den erweiterten Chor trägt. UTAC v1.3 sorgt dafür, dass jede neue Datenquelle nicht nur Licht spendet, sondern auch in den Codex singt.

