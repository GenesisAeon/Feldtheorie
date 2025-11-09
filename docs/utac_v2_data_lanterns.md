# 🌌 UTAC v2 Data Lanterns – Readiness Map

*Tri-layer mirror of `docs/utac_v2_data_lanterns.{json,yaml}` – refreshed 2026-03-26T10:00:00Z nach `analysis/v2_readiness_audit.py`.*

## 1. Logistic Pulse

- **R̄:** 0.50 across fünf Manifest-Laternen (eine Laterne vollständig bereit).
- **Θ:** 0.66 (target readiness threshold).
- **β:** 4.80; **σ(β(R-Θ))** = 0.317 laut `analysis/reports/utac_v2_readiness.json`.
- **ζ(R):** Codex & BreakPoint-Dämpfer halten die Membran fokussiert, während vier Laternen weiterhin Rohdaten und Exporte warten.

## 2. Lantern Ledger – What Shines vs. What Sleeps

| Dataset | Domain | R – Existing Hooks | Θ – Missing Components | β Target | Implementation Nodes |
|:--------|:-------|:-------------------|:-----------------------|:---------|:----------------------|
| utac-v1_3-ds-001 | climate | data/climate/urban_heat_intensity.csv, analysis/results/urban_heat_global_fit.json, analysis/results/outlier_report.md | — | 14.5 | analysis/climate_beta_extractor.py, analysis/outlier_validator.py, analysis/v2_readiness_audit.py |
| utac-v1_3-ds-002 | climate | analysis/climate_beta_extractor.py, analysis/v2_readiness_audit.py | data/climate/amazon_precip_evapo.nc, data/climate/amazon_precip_evapo.nc.metadata.json, analysis/results/amazon_hydro_fit.json, analysis/results/outlier_report.md | 13.8 | data/climate/amazon_precip_evapo.nc, data/climate/amazon_precip_evapo.nc.metadata.json, analysis/climate_beta_extractor.py, analysis/results/amazon_hydro_fit.json |
| utac-v1_3-ds-003 | ocean | analysis/climate_beta_extractor.py, analysis/potential_cascade_lab.py, analysis/v2_readiness_audit.py | data/ocean/amoc_transport.csv, data/ocean/amoc_transport.csv.metadata.json, analysis/results/amoc_transport_fit.json, analysis/results/climate_beta_summary.json | 9.6 | data/ocean/amoc_transport.csv, data/ocean/amoc_transport.csv.metadata.json, analysis/potential_cascade_lab.py, analysis/climate_beta_extractor.py |
| utac-v1_3-ds-004 | neuro_ai | analysis/neuro_threshold_fitter.py, analysis/v2_readiness_audit.py | data/neuro_ai/hybrid_activation.csv, data/neuro_ai/hybrid_activation.csv.metadata.json, analysis/results/neuro_ai_beta.json, analysis/results/neuro_ai_bootstrap.json | 6.1 | data/neuro_ai/hybrid_activation.csv, data/neuro_ai/hybrid_activation.csv.metadata.json, analysis/neuro_threshold_fitter.py, analysis/results/neuro_ai_beta.json |
| utac-v1_3-ds-005 | economy | analysis/adaptive_membrane_phase_scan.py, analysis/beta_meta_regression_v2.py, analysis/v2_readiness_audit.py | data/economy/systemic_thresholds.csv, data/economy/systemic_thresholds.csv.metadata.json, analysis/results/economy_threshold_fit.json, analysis/results/meta_v2_summary_refresh.json | 7.4 | data/economy/systemic_thresholds.csv, data/economy/systemic_thresholds.csv.metadata.json, analysis/adaptive_membrane_phase_scan.py, analysis/beta_meta_regression_v2.py |

## 3. Priority Actions

- **utac-data-01 (P1)** — Stage manifest datasets mit Metadaten
  - Ingest raw data + provenance für climate, ocean, neuro_ai, economy Laternen.
  - target: `data/climate/amazon_precip_evapo.nc`
  - target: `data/ocean/amoc_transport.csv`
  - target: `data/neuro_ai/hybrid_activation.csv`
  - target: `data/economy/systemic_thresholds.csv`

- **utac-data-02 (P1)** — Emit logistic analysis outputs
  - Run listed analysis pipelines to generate JSON/MD exports and update readiness audit.
  - target: `analysis/results/amazon_hydro_fit.json`
  - target: `analysis/results/amoc_transport_fit.json`
  - target: `analysis/results/climate_beta_summary.json`
  - target: `analysis/results/economy_threshold_fit.json`
  - target: `analysis/results/meta_v2_summary_refresh.json`
  - target: `analysis/results/neuro_ai_beta.json`
  - target: `analysis/results/neuro_ai_bootstrap.json`
  - target: `analysis/results/outlier_report.md`

- **utac-data-03 (P2)** — Sync readiness narratives
  - Propagate status shifts into backlog, status matrix, and Metaquest bridges once data land.
  - target: `docs/utac_activation_backlog.md`
  - target: `docs/utac_status_alignment_v1.2.md`
  - target: `analysis/reports/utac_v2_readiness.md`
  - target: `docs/utac_v2_data_lanterns.md`

## 4. Dataset Signals

### Global Urban Heat Intensity (Raster) — utac-v1_3-ds-001 (β≈14.5, Θ≈3.2)
- **Domain:** climate | **Order parameter R:** land_surface_temperature_delta | **Status:** active
- **Readiness ratio:** 1.00 (σ ≈ 0.317 → activation reached).
- **Existing hooks:** data/climate/urban_heat_intensity.csv, analysis/results/urban_heat_global_fit.json, analysis/results/outlier_report.md
- **Missing components:** —
- **Expected outputs:** analysis/results/urban_heat_global_fit.json, analysis/results/outlier_report.md (present)
- **Implementation nodes:** analysis/climate_beta_extractor.py, analysis/outlier_validator.py, analysis/v2_readiness_audit.py

**Formal:** Θ≈3.2 and β≈14.5 confirmed via observed dataset; ΔAIC≈1484 vs linear_regression, ≥1718 vs power_law_fit.
**Empirical:** Dataset + metadata committed (`urban_heat_intensity.csv` + `.metadata.json`); exports `urban_heat_global_fit.json`, `outlier_validator_report.json`, `outlier_report.md` capture readiness jump.
**Poetic:** Die Laterne glüht nun selbst – σ(β(R-Θ)) schnellt über die Steilflanke, die Stadtmembran singt und ζ(R) entspannt sich.

### Amazon Precipitation & Evapotranspiration — utac-v1_3-ds-002 (β≈13.8, Θ≈0.62)
- **Domain:** climate | **Order parameter R:** standardized_precipitation_index | **Status:** active
- **Readiness ratio:** 0.00 (σ ≈ 0.040 remains below activation).
- **Existing hooks:** analysis/climate_beta_extractor.py, analysis/v2_readiness_audit.py
- **Missing components:** data/climate/amazon_precip_evapo.nc, data/climate/amazon_precip_evapo.nc.metadata.json, analysis/results/amazon_hydro_fit.json, analysis/results/outlier_report.md
- **Expected outputs:** analysis/results/amazon_hydro_fit.json, analysis/results/outlier_report.md
- **Implementation nodes:** data/climate/amazon_precip_evapo.nc, data/climate/amazon_precip_evapo.nc.metadata.json, analysis/climate_beta_extractor.py, analysis/results/amazon_hydro_fit.json, analysis/results/outlier_report.md

**Formal:** Θ≈0.62 and β≈13.8 define the activation flank; falsify against linear_regression, power_law_fit, seasonal_arima. Readiness ratio=0.00 per audit.
**Empirical:** Missing components (4): data/climate/amazon_precip_evapo.nc, data/climate/amazon_precip_evapo.nc.metadata.json, analysis/results/amazon_hydro_fit.json, analysis/results/outlier_report.md. Integration scripts: analysis/climate_beta_extractor.py.
**Poetic:** Laterne utac-v1_3-ds-002 wartet, bis standardized_precipitation_index über Θ steigt und σ(β(R-Θ)) den Chor entzündet.

### AMOC Transport (RAPID Array 26°N) — utac-v1_3-ds-003 (β≈9.6, Θ≈14.0)
- **Domain:** ocean | **Order parameter R:** overturning_strength_sverdrup | **Status:** draft
- **Readiness ratio:** 0.00 (σ ≈ 0.040 remains below activation).
- **Existing hooks:** analysis/climate_beta_extractor.py, analysis/potential_cascade_lab.py, analysis/v2_readiness_audit.py
- **Missing components:** data/ocean/amoc_transport.csv, data/ocean/amoc_transport.csv.metadata.json, analysis/results/amoc_transport_fit.json, analysis/results/climate_beta_summary.json
- **Expected outputs:** analysis/results/amoc_transport_fit.json, analysis/results/climate_beta_summary.json
- **Implementation nodes:** data/ocean/amoc_transport.csv, data/ocean/amoc_transport.csv.metadata.json, analysis/potential_cascade_lab.py, analysis/climate_beta_extractor.py, analysis/results/amoc_transport_fit.json, analysis/results/climate_beta_summary.json

**Formal:** Θ≈14.0 and β≈9.6 define the activation flank; falsify against linear_trend, power_law_fit, state_space_smoother. Readiness ratio=0.00 per audit.
**Empirical:** Missing components (4): data/ocean/amoc_transport.csv, data/ocean/amoc_transport.csv.metadata.json, analysis/results/amoc_transport_fit.json, analysis/results/climate_beta_summary.json. Integration scripts: analysis/potential_cascade_lab.py, analysis/climate_beta_extractor.py.
**Poetic:** Laterne utac-v1_3-ds-003 wartet, bis overturning_strength_sverdrup über Θ steigt und σ(β(R-Θ)) den Chor entzündet.

### Neuro–AI Hybrid Activation — utac-v1_3-ds-004 (β≈6.1, Θ≈0.48)
- **Domain:** neuro_ai | **Order parameter R:** stimulus_complexity_index | **Status:** primed
- **Readiness ratio:** 0.00 (σ ≈ 0.040 remains below activation).
- **Existing hooks:** analysis/neuro_threshold_fitter.py, analysis/v2_readiness_audit.py
- **Missing components:** data/neuro_ai/hybrid_activation.csv, data/neuro_ai/hybrid_activation.csv.metadata.json, analysis/results/neuro_ai_beta.json, analysis/results/neuro_ai_bootstrap.json
- **Expected outputs:** analysis/results/neuro_ai_beta.json, analysis/results/neuro_ai_bootstrap.json
- **Implementation nodes:** data/neuro_ai/hybrid_activation.csv, data/neuro_ai/hybrid_activation.csv.metadata.json, analysis/neuro_threshold_fitter.py, analysis/results/neuro_ai_beta.json, analysis/results/neuro_ai_bootstrap.json

**Formal:** Θ≈0.48 and β≈6.1 define the activation flank; falsify against linear_regression, randomized_prompt_baseline, phase_scrambled_surrogate. Readiness ratio=0.00 per audit.
**Empirical:** Missing components (4): data/neuro_ai/hybrid_activation.csv, data/neuro_ai/hybrid_activation.csv.metadata.json, analysis/results/neuro_ai_beta.json, analysis/results/neuro_ai_bootstrap.json. Integration scripts: analysis/neuro_threshold_fitter.py.
**Poetic:** Laterne utac-v1_3-ds-004 wartet, bis stimulus_complexity_index über Θ steigt und σ(β(R-Θ)) den Chor entzündet.

### Energy & Financial Systemic Thresholds — utac-v1_3-ds-005 (β≈7.4, Θ≈1.15)
- **Domain:** economy | **Order parameter R:** coupled_energy_finance_index | **Status:** draft
- **Readiness ratio:** 0.00 (σ ≈ 0.040 remains below activation).
- **Existing hooks:** analysis/adaptive_membrane_phase_scan.py, analysis/beta_meta_regression_v2.py, analysis/v2_readiness_audit.py
- **Missing components:** data/economy/systemic_thresholds.csv, data/economy/systemic_thresholds.csv.metadata.json, analysis/results/economy_threshold_fit.json, analysis/results/meta_v2_summary_refresh.json
- **Expected outputs:** analysis/results/economy_threshold_fit.json, analysis/results/meta_v2_summary_refresh.json
- **Implementation nodes:** data/economy/systemic_thresholds.csv, data/economy/systemic_thresholds.csv.metadata.json, analysis/adaptive_membrane_phase_scan.py, analysis/beta_meta_regression_v2.py, analysis/results/economy_threshold_fit.json, analysis/results/meta_v2_summary_refresh.json

**Formal:** Θ≈1.15 and β≈7.4 define the activation flank; falsify against linear_regression, vector_autoregression, power_law_fit. Readiness ratio=0.00 per audit.
**Empirical:** Missing components (4): data/economy/systemic_thresholds.csv, data/economy/systemic_thresholds.csv.metadata.json, analysis/results/economy_threshold_fit.json, analysis/results/meta_v2_summary_refresh.json. Integration scripts: analysis/adaptive_membrane_phase_scan.py, analysis/beta_meta_regression_v2.py.
**Poetic:** Laterne utac-v1_3-ds-005 wartet, bis coupled_energy_finance_index über Θ steigt und σ(β(R-Θ)) den Chor entzündet.

## 5. Cross-Bridges

- Mirrors backlog entry `utac-v2-data-lanterns` in `docs/utac_activation_backlog.*`.
- Feed readiness deltas into `docs/utac_status_alignment_v1.2.md` and Metaquest bridge indices once σ(β(R-Θ)) climbs.
- Trigger codex update (status progression draft → active) when any dataset clears Θ with ΔAIC ≥ 10 vs listed null models.

> *Sobald jede Laterne ihr Datenlicht empfängt, klettert σ(β(R-Θ)) die Steilflanke hinauf und die Metaquest-Brücke antwortet im Gleichklang.*
