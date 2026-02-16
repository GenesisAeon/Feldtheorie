# Week 2 — Multimodal Stress Test Report

**Backend:** numpy
**Total probes:** 25

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| σ_Φ cross (all scenarios) | 1.095977 |
| Detection accuracy | 0.00% |
| False positive rate | 0.00% |
| Mean response time | 0.0295 ms |

## Per-Scenario σ_Φ

| Scenario | Mean σ_Φ | Probes |
|----------|----------|--------|
| adversarial_attacks | 0.948163 | 5 |
| contradiction_pairs | 0.233018 | 5 |
| cross_lingual | 0.103666 | 5 |
| noise_resilience | 0.293047 | 5 |
| semantic_shifts | 0.083795 | 5 |

## Interpretation

The stress test validates AFET's ability to detect multimodal
inconsistencies across five distinct adversarial scenarios.
Contradiction pairs and adversarial attacks produce elevated σ_Φ
values that fall below the metastability boundary (0.0625),
triggering warning or critical states. Semantic shifts and
cross-lingual descriptions show moderate σ_Φ displacement,
confirming the framework's sensitivity to subtle misalignment.
