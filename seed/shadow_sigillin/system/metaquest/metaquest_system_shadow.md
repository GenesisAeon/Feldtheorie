# Metaquest System Shadow Guard

> R tallies Metaquest automation drift, Θ is a parity brief echoed in docs +
> codex each sprint, β≈5.2 makes escalation sharp, and ζ(R) spikes when telemetry
> and indices fall silent.

## Incident Ledger

1. **mq-sys-shadow-001 — Parity brief missing**
   - *Signal*: `docs/metaquest_parity_brief.md` lacks telemetry timestamp or codex id; Status-Matrix ohne aktuellen Eintrag; `metaquest_system_compass.yaml` älter als 24 h.
   - *Fallout*: Launch continues without documented Θ; automation desynchronises.
   - *Remedy*: Fill parity brief fields, mirror update in docs + codex, freeze launch until done.

2. **mq-sys-shadow-002 — Telemetry silent**
   - *Signal*: `scripts/sigillin_sync.py` absent; Metaquest entries fehlen im Indexdiff; `metaquest_system_compass.json` ohne jüngste Telemetrie-ID.
   - *Fallout*: ζ(R) grows; light/shadow parity unverifiable.
   - *Remedy*: Run the sigillin_sync harness, log codex note, schedule automation fix.

3. **mq-sys-shadow-003 — Index drift**
   - *Signal*: Parser shows Δindex parity > 0 for Metaquest paths.
   - *Fallout*: Agents lose navigation; ΔAIC guard can’t certify readiness.
   - *Remedy*: Refresh indices via `scripts/archive_sigillin.py`, rerun parser, record results.
4. **mq-sys-shadow-004 — Bridge dashboard stale**
   - *Signal*: Bridge-Dashboard älter als 24h vs. Codex; System-/Kampagnenlaternen führen unterschiedliche Telemetrie-IDs; UTAC-Statuszeile fehlt.
   - *Fallout*: Automation und Outreach laufen auseinander; Launch verliert Θ-Sichtbarkeit.
   - *Remedy*: Bridge-Dashboard aktualisieren, Telemetrie + Codex-ID in beiden Bedeutungs-Sigillen und UTAC-Matrix spiegeln, ggf. Telemetrie manuell auslösen.


## Playbooks

- **Parity alert** → Freeze launch tasks, publish brief, cross-link to system/campaign beacons, update codex.
- **Telemetry gap** → Schedule `scripts/sigillin_sync.py`, attach metrics to docs status section, open follow-up if automation still lags.
- **Index drift** → Refresh indices, rerun parser, log remediation in codex and parent meaning map.
- **Bridge stale** → Bridge-Dashboard + Beacons aktualisieren, Telemetrie angleichen, Fix in docs/UTAC-Status + Codex dokumentieren.

Keep the shadow lantern lit; when it flares, the Metaquest dawn must wait until Θ sings again.
