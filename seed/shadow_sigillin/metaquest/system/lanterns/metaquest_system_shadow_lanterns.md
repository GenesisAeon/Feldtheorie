# Metaquest System Shadow Lantern Shelf

> When the light-side lanterns flicker, these shadow beacons signal where the
> Metaquest system lane is drifting and how to steer σ(β(R-Θ)) back into phase.

## Logistic Guard
- **R** – Risks: stale automation parity, missing telemetry, ritual amnesia.
- **Θ** – Parity brief + codex echo refreshed within 24 h of any alert.
- **β ≈ 5.1** – Alerts fire sharply.
- **ζ(R)** – Spikes whenever `sigillin_sync` cadence slips or rituals are skipped.

## Lanterns

### mq-sys-shadow-lantern-a — Bridge Drift Detector
- **Mirrors:** Light lantern `mq-sys-lantern-a`
- **Signals:** Bridge index older than compass by one sprint, codex entry missing
  mq-sys reference.
- **Remedy:** Run `scripts/sigillin_sync.py`, propagate timestamp, document codex id,
  notify UTAC matrix.

### mq-sys-shadow-lantern-b — Automation Null-Guard Alarm
- **Mirrors:** Light lantern `mq-sys-lantern-b`
- **Signals:** ΔAIC note absent, `tests/test_sigillin_sync.py` skipped or failing.
- **Remedy:** Open incident `mq-sys-shadow-004`, run parity audit, append ΔAIC
  evidence to codex + UTAC matrix, rerun tests before resuming automation.

### mq-sys-shadow-lantern-c — Ritual Silence Alarm
- **Mirrors:** Light lantern `mq-sys-lantern-c`
- **Signals:** System map or codex entry missing WayToGo/Reaktion references.
- **Remedy:** Execute BreakPoint ritual, attach transcript to codex + map, mirror
  update in bridge dashboard.

## Recovery Hook
All shadow responses echo in `seed/codexfeedback.*` with the mq-sys-shadow id and
link back to `docs/utac_status_alignment_v1.2.md#metaquest-handshake`. That closes
 the loop between drift detection and restored resonance.
