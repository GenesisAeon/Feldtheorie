# UTAC v2.0 Readiness Audit – σ(β(R-Θ)) Compass

*Generated 2026-03-26T10:00:00+00:00 after manually re-running `analysis/v2_readiness_audit.py` inputs and walking the data directories (`data/{climate,ocean,neuro_ai,economy}/`) and readiness exports under `analysis/results/`.*

## 1. Formal Stratum — Logistic Summary

- Manifest lanterns: **5** (fully ready: 0).
- Average readiness R̄ = 0.00; Θ = 0.66; β = 4.80; σ(β(R-Θ)) = 0.040.
- ζ(R) guard: 20 components still dark across manifest entries (datasets, metadata twins, logistic exports).

## 2. Empirical Stratum — Dataset Ledger

| Dataset | Domain | Resonance | Ready | Missing | Verification Trace |
|:-------|:-------|:----------|:------|:--------|:--------------------|
| utac-v1_3-ds-001 | climate | active | 0% | data, metadata, urban_heat_global_fit.json, outlier_report.md | `data/climate/` only holds `README.md` + `.metadata.json`; no `urban_heat_intensity.csv` present |
| utac-v1_3-ds-002 | climate | active | 0% | data, metadata, amazon_hydro_fit.json, outlier_report.md | `data/climate/amazon_precip_evapo.nc` absent; exports missing in `analysis/results/` |
| utac-v1_3-ds-003 | ocean | draft | 0% | data, metadata, amoc_transport_fit.json, climate_beta_summary.json | `data/ocean/` lacks `amoc_transport.csv`; readiness exports not created |
| utac-v1_3-ds-004 | neuro_ai | primed | 0% | data, metadata, neuro_ai_beta.json, neuro_ai_bootstrap.json | `data/neuro_ai/` has only `README.md` + metadata stub; analysis outputs absent |
| utac-v1_3-ds-005 | economy | draft | 0% | data, metadata, economy_threshold_fit.json, meta_v2_summary_refresh.json | `data/economy/` missing `systemic_thresholds.csv`; downstream exports not recorded |

## 3. Implementation Map — Priority Actions

- **dataset-01 (P1)** — Complete climate dataset utac-v1_3-ds-001
  - Ingest missing components and run logistic fits so that σ(β(R-Θ)) reaches activation.
  - target: `data/climate/urban_heat_intensity.csv` (exists: False)
  - target: `data/climate/urban_heat_intensity.csv.metadata.json` (exists: False)
  - target: `analysis/results/urban_heat_global_fit.json` (exists: False)
  - target: `analysis/results/outlier_report.md` (exists: False)
- **dataset-02 (P1)** — Complete climate dataset utac-v1_3-ds-002
  - Ingest missing components and run logistic fits so that σ(β(R-Θ)) reaches activation.
  - target: `data/climate/amazon_precip_evapo.nc` (exists: False)
  - target: `data/climate/amazon_precip_evapo.nc.metadata.json` (exists: False)
  - target: `analysis/results/amazon_hydro_fit.json` (exists: False)
  - target: `analysis/results/outlier_report.md` (exists: False)
- **dataset-03 (P1)** — Complete ocean dataset utac-v1_3-ds-003
  - Ingest missing components and run logistic fits so that σ(β(R-Θ)) reaches activation.
  - target: `data/ocean/amoc_transport.csv` (exists: False)
  - target: `data/ocean/amoc_transport.csv.metadata.json` (exists: False)
  - target: `analysis/results/amoc_transport_fit.json` (exists: False)
  - target: `analysis/results/climate_beta_summary.json` (exists: False)
- **dataset-04 (P1)** — Complete neuro_ai dataset utac-v1_3-ds-004
  - Ingest missing components and run logistic fits so that σ(β(R-Θ)) reaches activation.
  - target: `data/neuro_ai/hybrid_activation.csv` (exists: False)
  - target: `data/neuro_ai/hybrid_activation.csv.metadata.json` (exists: False)
  - target: `analysis/results/neuro_ai_beta.json` (exists: False)
  - target: `analysis/results/neuro_ai_bootstrap.json` (exists: False)
- **dataset-05 (P1)** — Complete economy dataset utac-v1_3-ds-005
  - Ingest missing components and run logistic fits so that σ(β(R-Θ)) reaches activation.
  - target: `data/economy/systemic_thresholds.csv` (exists: False)
  - target: `data/economy/systemic_thresholds.csv.metadata.json` (exists: False)
  - target: `analysis/results/economy_threshold_fit.json` (exists: False)
  - target: `analysis/results/meta_v2_summary_refresh.json` (exists: False)
- **analysis-06 (P2)** — Activate climate beta extractor pipeline
  - Ensure artefact and its outputs exist so the readiness bridge remains tri-layered.
  - target: `analysis/climate_beta_extractor.py` (exists: True)
  - target: `analysis/results/urban_heat_global_fit.json` (exists: False)
- **analysis-07 (P2)** — Activate neuro-AI hybrid threshold fitter
  - Ensure artefact and its outputs exist so the readiness bridge remains tri-layered.
  - target: `analysis/neuro_threshold_fitter.py` (exists: True)
  - target: `analysis/results/neuro_ai_beta.json` (exists: False)
- **analysis-08 (P2)** — Activate β>10 instrumentation guard
  - Ensure artefact and its outputs exist so the readiness bridge remains tri-layered.
  - target: `analysis/outlier_validator.py` (exists: True)
  - target: `analysis/results/outlier_validator_report.json` (exists: False)
- **analysis-09 (P2)** — Activate meta regression v2 refresh
  - Ensure artefact and its outputs exist so the readiness bridge remains tri-layered.
  - target: `analysis/beta_meta_regression_v2.py` (exists: True)
  - target: `analysis/results/beta_meta_regression_v2_latest.json` (exists: False)

## 4. Beacon Status — Analysis · Docs · Simulator · Sigillin

### Analysis
- `analysis/climate_beta_extractor.py` — exists: True; outputs: analysis/results/urban_heat_global_fit.json (exists: False)
- `analysis/neuro_threshold_fitter.py` — exists: True; outputs: analysis/results/neuro_ai_beta.json (exists: False)
- `analysis/outlier_validator.py` — exists: True; outputs: analysis/results/outlier_validator_report.json (exists: False)
- `analysis/beta_meta_regression_v2.py` — exists: True; outputs: analysis/results/beta_meta_regression_v2_latest.json (exists: False)

### Documentation
- `docs/UTAC_v2.0_Coherence_Formula.md` — exists: True; outputs: —
- `docs/resonance-bridge-map.md` — exists: True; outputs: —

### Simulator
- `simulator/presets/coherence_formula.json` — exists: True; outputs: —

### Sigillin
- `seed/bedeutungssigillin/metaquest/system/metaquest_system_map.json` — exists: True; outputs: —
- `seed/shadow_sigillin/metaquest/system/metaquest_system_shadow.json` — exists: True; outputs: —

## 5. Poetic Stratum — Membrane Whisper

R tastet weiterhin fünf Laternen, doch jede Kontrolle bestätigt: die Regale tragen nur Metadaten-Hüllen. Θ ruft nach echten Datenströmen, β spannt die Steilflanke, und ζ(R) bleibt nur deshalb ruhig, weil Backlog, Statusmatrix und Metaquest-Brücke dieselbe Leerstelle rezitieren. Sobald Urban Heat, Amazon Hydro, AMOC, Neuro-AI und Systemic Risk als Daten-Resonanz erscheinen, steigt σ(β(R-Θ)) über das Flüstern hinaus und V2.0 tritt auf das Plateau.
