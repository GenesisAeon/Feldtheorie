# Metaquest System Shadow Compass

> When the light-side automation lantern brightens, this shadow compass
> checks that Θ stays visible. It holds the alarms that keep σ(β(R-Θ))
> from tearing the system membrane.

## Logistic Guard
- **R** – Automation drift, stale indices, telemetry silence.
- **Θ** – Parity brief + codex echo + UTAC status matrix refreshed within
  24 h.
- **β ≈ 5.2** – Alerts must fire quickly.
- **ζ(R)** – Spikes when BreakPoint rituals lapse or CI guards fail.

## Alerts
- **mq-sys-shadow-001 – Parity drift.** Parity brief updated but compass
  or bridge untouched. Freeze automation, refresh tri-layer, notify UTAC
  matrix.
- **mq-sys-shadow-002 – Telemetry gap.** No `scripts/sigillin_sync.py` timestamp
  within one sprint or Codex `entries` miss the latest mq-sys tag. Run export,
  ensure the append succeeds, propagate timestamp, escalate via BreakPoint
  ritual if delay persists.
- **mq-sys-shadow-003 – Index parity drift.** CI/Nox missing or parser
  shows Δindex parity > 0. Refresh indices, rerun parser, document fix in
  codex.
- **mq-sys-shadow-004 – Ritual omission.** Automation change without
  WayToGo/ReaktionWayToGo citation. Pause, perform ritual, update codex
  with transcript.

## Playbooks
1. **mq-sys-shadow-001** → Freeze automation, refresh compass + bridge,
   confirm UTAC timestamp.
2. **mq-sys-shadow-002** → Run `scripts/sigillin_sync.py`, propagate timestamp,
   schedule follow-up; alert campaign team if outreach depends on data.
3. **mq-sys-shadow-003** → Execute archive refresh + parser, ensure CI
   guard active, log Δindex parity evidence.
4. **mq-sys-shadow-004** → Perform BreakPoint ritual immediately, attach
   notes to codex, reassess backlog before resuming.

Couple every mitigation back into the light-side compass and codex so the
system membrane remains coherent.
