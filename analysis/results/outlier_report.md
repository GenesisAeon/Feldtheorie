# β>10 Outlier Resonance Ledger — Urban Heat Activation

*Generated via `analysis/outlier_validator.py` after integrating `data/climate/urban_heat_intensity.csv` on 2026-03-26 (UTC).*  
*Logistic compass: R = land_surface_temperature_delta, Θ ≈ 3.20 K, β ≈ 14.27.*

## 1. Formal Stratum — σ(β(R-Θ)) Diagnostics

| Metric | Value |
| --- | --- |
| Sample size | 220 |
| θ̂ (95% CI) | 3.205 K (3.202, 3.207) |
| β̂ (95% CI) | 14.27 (14.20, 14.34) |
| R² | 0.99984 |
| ΔAIC vs linear | 1483.82 |
| ΔAIC vs power law | 1718.68 |
| Instrumentation flag | genuine_regime_split |

## 2. Empirical Stratum — Dataset & Null Models

- **Dataset:** `data/climate/urban_heat_intensity.csv` (land_surface_temperature_delta ↦ heat_activation_fraction) with metadata twin `data/climate/urban_heat_intensity.metadata.json`.
- **Fit export:** `analysis/results/urban_heat_global_fit.json` (observed data).  
- **Null guards:**
  - Linear regression AIC = −778.21, R² = 0.862, slope ≈ 0.91.
  - Power-law baseline AIC = −543.34, R² = 0.599.
- **Validator summary:** `analysis/results/outlier_validator_report.json` marks β>10 resonance as a genuine split; ΔAIC guard (≥10) comfortably cleared.

## 3. Poetic Stratum — Membrane Resonance

> Sobald ΔT die 3.2 K-Schwelle küsst, schnellt σ(β(R-Θ)) senkrecht nach oben.  
> Die Stadtmembran glüht nicht aus Instrumentenrauschen, sondern aus echter, scharfer Dawn-Steigung — β≈14 zieht die Steilflanke wie einen Lichtpfeil durch die Metropole.

## 4. Next Rituals

1. Re-run `analysis/outlier_validator.py` after ingesting the remaining UTAC v1.3 datasets to keep the ledger coherent.  
2. Reflect the observed readiness lift in `docs/utac_v2_activation_tracker_2026-03.*` and `docs/utac_activation_backlog.*`.  
3. Update Codex entry `pr-draft-0096` with the new σ(β(R-Θ)) activation evidence.
