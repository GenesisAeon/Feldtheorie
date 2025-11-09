# Metaquest System Bridge Shadow Map

> When the bridge lantern brightens, this shadow map watches the same σ(β(R-Θ))
> flank for cracks. It keeps Metaquest automation honest by naming the failure
> modes that would let R outrun Θ.

## Logistic Guard
- **R – Drift Load.** Missing telemetry exports, stale readiness audits, orphaned
  simulator presets, or uncoupled indices.
- **Θ – 24 h Parity Rule.** Bridge, compass, UTAC matrix, and codex must echo the
  same mq-sys timestamp/codex id within one day.
- **β ≈ 5.1.** Alerts fire sharply because bridge automation is steep.
- **ζ(R).** Spikes whenever BreakPoint rituals lapse or shadow remediation is not
  logged before release freeze.

## Shadow Alerts

1. **mq-sys-shadow-bridge-001 — Telemetry Silence.**
   - *Signal:* `analysis/sigillin_sync/latest.json` older than one sprint or
     missing from bridge map.
   - *Action:* Freeze automation, run `scripts/sigillin_sync.py`, propagate
     timestamp to bridge map, compass, and meaning index, cite codex id.
2. **mq-sys-shadow-bridge-002 — Readiness Drift.**
   - *Signal:* `analysis/v2_readiness_audit.py` not re-run after manifest/preset
     change; logistic Θ/β omitted from bridge map.
   - *Action:* Execute audit, archive tri-layer outputs, update UTAC matrix and
     codex with ΔAIC proof, notify campaign lane.
3. **mq-sys-shadow-bridge-003 — Simulator Desync.**
   - *Signal:* `simulator/presets/coherence_formula.json` missing, outdated, or
     not imported in `simulator/src/presets.ts`; preset not listed in
     `docs/resonance-bridge-map.md`.
   - *Action:* Restore preset, rerun preset alignment guard, refresh indices,
     append codex note with mq-bridge-shadow reference.
4. **mq-sys-shadow-bridge-004 — Shadow Echo Missing.**
   - *Signal:* Bridge map updated without corresponding shadow map entry or
     codex remediation log.
   - *Action:* Update this map, cite recovery hooks, cross-link to UTAC matrix,
     and document ritual completion.

## Recovery Hooks
- **Telemetry Reset Ritual.** Run `scripts/sigillin_sync.py`, archive report,
  repeat BreakPoint steps, update bridge + compass + codex, confirm UTAC matrix
  mirrors timestamp.
- **Readiness Audit Cycle.** Re-run audit, regenerate
  `analysis/reports/utac_v2_readiness.*`, add ΔAIC summary to bridge/shadow maps,
  file codex entry with mq-sys-shadow-bridge-002.
- **Simulator Alignment Loop.** Restore preset JSON, import in
  `simulator/src/presets.ts`, rerun `analysis/preset_alignment_guard.py`, update
  `docs/resonance-bridge-map.md`, log codex reference.
- **Codex Echo Seal.** Every remediation writes mq-sys-shadow id, timestamp, and
  pointer to `docs/utac_status_alignment_v1.2.md` to maintain traceability.

## Null Model
Metaquest automation advances while telemetry, readiness, or simulator hooks go
quiet. Bridge map glows, but the shadow stays blank. Indices drift, ΔAIC proof is
lost, and ζ(R) surges without recovery steps. Keep this map in lockstep with the
light-side bridge to preserve resonance.
