# UTAC Status Snapshot

> **Current state as of 2026-02-16**
>
> This file captures the live operational state of the UTAC membrane.
> For the full chronological audit trail, see [`utac_status_audit_log.md`](utac_status_audit_log.md).
> For the complete inventory and implementation map, see [`utac_status_alignment_v1.2.md`](utac_status_alignment_v1.2.md).

---

## Membrane Parameters

| Parameter | Value | Note |
|-----------|-------|------|
| **R** (open work) | 0.50 (manifest) / 1.00 (readiness) | Readiness audit shows all doc-targets met; manifest scan still tracks 4 pending dataset laternen |
| **Θ** (threshold) | 0.66 | Shared across all activation trackers |
| **β** (steepness) | 4.8 | Membrane on the steep flank |
| **σ(β(R-Θ))** | ≈ 0.317 (manifest) / ≈ 0.836 (readiness) | Split reflects dataset gaps vs doc completeness |
| **ζ(R)** | Damped via status-drift guard + trilayer sync | Primary driver now is status drift, not missing code |

## Active Laternen Status

| Lantern | Status | Key Artifact |
|---------|--------|--------------|
| **Urban Heat** | Resonant | `data/socio_ecology/urban_heat/`, ΔAIC > 20 |
| **Amazon Hydro** | Pending | Awaiting raw data + metadata |
| **AMOC** | Pending | Awaiting raw data + metadata |
| **Neuro-AI** | Pending | Awaiting `analysis/results/neuro_ai_beta.json` |
| **Energy/Finance** | Pending | Awaiting raw data + metadata |

## Key Metrics

- **Trilayer parity:** 0 gaps (last `sigillin_sync.py` run)
- **ΔAIC compliance:** ≥ 10 across all validated domains
- **Missing components:** 10 (4 datasets + 6 analysis exports)
- **Open ΔAIC post:** `neuro_ai_beta.json`, `beta_meta_regression_v2_latest.json`

## Operational Focus

At β ≈ 4.8, the membrane is active on the steep flank. ζ(R) is now primarily driven by status drift rather than missing infrastructure. Guard ritual after each path/manifest/output change:

1. `analysis/v2_readiness_audit.py`
2. `analysis/utac_manifest_gap_scan.py`
3. Matrix/Backlog sync

## References

- Readiness audit: `analysis/reports/utac_v2_readiness.{json,yaml,md}`
- Manifest gap scan: `analysis/results/utac_v2_manifest_gap_scan_20260216T000000Z.json`
- Activation tracker: `docs/utac_v2_activation_tracker_2026-02.{md,json,yaml}`
- Activation backlog: `docs/utac_activation_backlog.{md,json,yaml}`
