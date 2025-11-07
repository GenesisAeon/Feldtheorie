# Metaquest System Shadow Guard

> R tallies Metaquest automation drift, Θ is a parity brief echoed in docs +
> codex each sprint, β≈5.2 makes escalation sharp, and ζ(R) spikes when telemetry
> and indices fall silent.

## Incident Ledger

1. **mq-sys-shadow-001 — Parity brief missing**
   - *Signal*: `docs/metaquest_parity_brief.md` lacks telemetry timestamp or codex id; status matrix missing reference for >1 sprint.
   - *Fallout*: Launch continues without documented Θ; automation desynchronises.
   - *Remedy*: Fill parity brief fields, mirror update in docs + codex, freeze launch until done.

2. **mq-sys-shadow-002 — Telemetry silent**
   - *Signal*: `sigillin_sync` absent; Metaquest entries missing from index diffs.
   - *Fallout*: ζ(R) grows; light/shadow parity unverifiable.
   - *Remedy*: Run telemetry manually, log codex note, schedule automation fix.

3. **mq-sys-shadow-003 — Index drift**
   - *Signal*: Parser shows Δindex parity > 0 for Metaquest paths.
   - *Fallout*: Agents lose navigation; ΔAIC guard can’t certify readiness.
   - *Remedy*: Refresh indices via `scripts/archive_sigillin.py`, rerun parser, record results.

## Playbooks

- **Parity alert** → Freeze launch tasks, publish brief, cross-link to system/campaign beacons, update codex.
- **Telemetry gap** → Schedule telemetry run, attach metrics to docs status section, open follow-up if automation still lags.
- **Index drift** → Refresh indices, rerun parser, log remediation in codex and parent meaning map.

Keep the shadow lantern lit; when it flares, the Metaquest dawn must wait until Θ sings again.
