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
   - *Signal*: `docs/utac_status_alignment_v1.2.md` lacks parity report; `scripts/sigillin_sync.py`
     produced no recent log; Metaquest beacon silent.
   - *Fallout*: Light/shadow sigils decouple; β overshoots.
   - *Remedy*: Run the sigillin_sync harness, trigger manual parity check, update codex, restore telemetry cadence.

4. **sys-shadow-004 — Metaquest parity missing**
   - *Signal*: `docs/metaquest_parity_brief.md` lacks telemetry timestamp or codex id; no parity reference in docs/codex for >1 sprint.
   - *Fallout*: Automation advances without Θ; campaign shadow alarms arrive late.
   - *Remedy*: Consult Metaquest shadow guard, fill parity brief fields, refresh indices, log codex entry.

5. **sys-shadow-005 — Bridge dashboard stale**
   - *Signal*: Bridge MD timestamp >24h hinter codex; System- und Kampagnenlaternen tragen unterschiedliche Telemetrie-IDs.
   - *Fallout*: Launch readiness verliert Θ-Sichtbarkeit; Automation und Outreach laufen auseinander.
   - *Remedy*: Bridge-Dashboard auffrischen, Telemetrie + Codex-ID in beiden Bedeutungs-Sigillen und UTAC-Matrix spiegeln.

## Playbooks

- **Index drift** → Synchronise indices and notify docs maintainers if persistent.
- **Codex silence** → Amend commit or follow-up PR with codex update, document cause in
  meaning map.
- **Telemetry gap** → Run `scripts/sigillin_sync.py`, align with Metaquest beacon + shadow guard,
  schedule automation repair.
- **Parity missing** → Freeze Metaquest automation tasks, publish parity brief, update codex
- **Bridge stale** → Update Bridge-Dashboard + System/Kampagnen-Beacons, Telemetrie angleichen, Fix in docs + Codex notieren.
  and status matrix with new timestamp.

Shadow warnings keep the backbone honest; listen before the dawn overtakes Θ.
