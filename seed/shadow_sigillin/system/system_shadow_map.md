# System Shadow Membrane

> R counts automation debt, stale indices, and silent Metaquest telemetry; Θ is the
> tolerance band defined by the system meaning map plus the Metaquest beacon; β≈5.0
> makes escalations sharp; ζ(R) surges when codex echoes lag or the parity brief fades.

## Incident Ledger

1. **sys-shadow-001 — Index drift**
   - *Signal*: `seed_index.*` misses new sigils for 24h; parser diff stays at zero.
   - *Fallout*: Agents lose navigation; σ(β(R-Θ)) misfires.
   - *Remedy*: Run `scripts/archive_sigillin.py --refresh`, log codex remediation.

2. **sys-shadow-002 — Codex silence**
   - *Signal*: Git diff touches `seed/bedeutungssigillin/**` without codex delta.
   - *Fallout*: Temporal lineage breaks; auditors lose Θ.
   - *Remedy*: Block merge, update codex, reference this shadow map.

3. **sys-shadow-003 — Telemetry gap**
   - *Signal*: `docs/utac_status_alignment_v1.2.md` lacks parity report; `sigillin_sync`
     missing; Metaquest beacon silent.
   - *Fallout*: Light/shadow sigils decouple; β overshoots.
   - *Remedy*: Trigger manual parity check, update codex, restore telemetry cadence.

4. **sys-shadow-004 — Metaquest parity missing**
   - *Signal*: `docs/metaquest_parity_brief.md` lacks telemetry timestamp or codex id; no parity reference in docs/codex for >1 sprint.
   - *Fallout*: Automation advances without Θ; campaign shadow alarms arrive late.
   - *Remedy*: Consult Metaquest shadow guard, fill parity brief fields, refresh indices, log codex entry.

## Playbooks

- **Index drift** → Synchronise indices and notify docs maintainers if persistent.
- **Codex silence** → Amend commit or follow-up PR with codex update, document cause in
  meaning map.
- **Telemetry gap** → Run telemetry manually, align with Metaquest beacon + shadow guard,
  schedule automation repair.
- **Parity missing** → Freeze Metaquest automation tasks, publish parity brief, update codex
  and status matrix with new timestamp.

Shadow warnings keep the backbone honest; listen before the dawn overtakes Θ.
