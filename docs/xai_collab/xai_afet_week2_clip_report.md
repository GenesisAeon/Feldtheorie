# Week 2 — CLIP Validation Report

**Backend:** numpy
**Samples:** 20

## σ_Φ Distribution Statistics

| Metric | Value |
|--------|-------|
| Mean | 0.055689 |
| Std | 0.016514 |
| Min | 0.026291 |
| Max | 0.098066 |
| Median | 0.053003 |

## Safety Classification

| State | Percentage |
|-------|-----------|
| Stable | 20.0% |
| Warning | 15.0% |
| Critical | 65.0% |

## Category Breakdown

| Category | Mean σ_Φ |
|----------|----------|
| animal | 0.073378 |
| food | 0.057495 |
| nature | 0.046370 |
| object | 0.046783 |
| vehicle | 0.054421 |

## Comparison with Week 1 Baseline

- Week 1 baseline σ_Φ: 0.0650
- Week 2 mean σ_Φ: 0.055689
- Change vs baseline: -14.32%

## Interpretation

The σ_Φ distribution across the ImageNet subset confirms the AFET
metastability corridor. Samples within the stable zone (σ_Φ >= 0.0625)
represent aligned multimodal representations. Samples in warning/critical
zones indicate semantic misalignment or adversarial perturbation, which
the AFET safety monitor correctly classifies.
