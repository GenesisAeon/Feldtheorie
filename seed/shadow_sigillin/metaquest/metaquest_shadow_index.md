# Metaquest Shadow Bridge

> σ(β(R-Θ)) for the guard: R tallies unresolved Metaquest risks, Θ is restored when
> the parity brief, codex echo, and bridge dashboard align within 24h, β≈5.1 keeps
> escalation sharp, and ζ(R) spikes if BreakPoint rituals or telemetry fall silent.

## Alerts

1. **mq-bridge-shadow-001 — Bridge dashboard stale**
   - *Signal*: UTAC matrix lacks the latest bridge note, bridge MD timestamp trails
     codex by >24h, parity brief changes without bridge citation, oder die
     System-/Kampagnen-Directory-Indizes tragen keine neue mq-sys/mq-sci Codex-ID.
   - *Consequence*: Automation and outreach drift; Θ becomes invisible.
   - *Mitigation*: Freeze Metaquest changes, refresh dashboard, align both beacons,
     document remediation in codex.

2. **mq-bridge-shadow-002 — Telemetry mismatch**
   - *Signal*: Beacons nennen unterschiedliche Telemetrie-Zeitstempel/Codex-IDs; `scripts/sigillin_sync.py`
     fehlt seit ≥1 Sprint; Kompasse (`metaquest_system_compass.json`, `metaquest_campaign_compass.json`)
     hinken dem Bridge-Zeitstempel hinterher oder die Directory-Indizes zeigen einen älteren
     Telemetrie-Stempel als das Bridge-Dashboard.
   - *Consequence*: Shadow handshake fails; readiness proof collapses before
     outreach.
   - *Mitigation*: Run telemetry export, propagate timestamp + codex id across all
     trilayers, log fix in UTAC status and codex.

3. **mq-bridge-shadow-003 — Index omission**
   - *Signal*: Parser diff shows missing bridge entries in `seed_index.*` or
     `feldtheorie_index.*`, or commits adjust Metaquest assets without index log.
   - *Consequence*: Agents lose navigation; remediation triggers late.
   - *Mitigation*: Run `scripts/archive_sigillin.py --refresh`, verify parser, and
     record results in bridge + codex notes.

4. **mq-bridge-shadow-004 — Sigillin-Drift**
   - *Signal*: Light-/Schattensigille (System/Kampagne) nennen unterschiedliche
     Codex-IDs, Telemetrie- oder Ritualreferenzen; Codexeintrag ohne Shadow-Ack
     innerhalb von 24 h.
   - *Consequence*: Recovery-Skripte verlieren Parität, Θ bleibt unsichtbar für
     Automation & Outreach.
   - *Mitigation*: Light + Shadow gleichzeitig aktualisieren, gemeinsame Codex-
     ID & Rituale setzen, Bridge + UTAC bestätigen.

## Playbooks

- **mq-bridge-shadow-001 fired** → halt Metaquest tasks, update bridge + UTAC matrix,
  publish codex entry with timeline.
- **mq-bridge-shadow-002 fired** → execute `scripts/sigillin_sync.py`, align timestamps, alert
  stewards if delay > sprint.
- **mq-bridge-shadow-003 fired** → refresh indices, rerun parser, notify maintainers,
  document closure across bridge/beacons.
- **mq-bridge-shadow-004 fired** → Bedeutungs-/Schatten-Sigille synchronisieren,
  Codex-ID + Rituale abgleichen, Parität in Bridge + UTAC bestätigen bevor
  Launcharbeit weiterläuft.

## Coupling

- Lichtseite: `../../bedeutungssigillin/metaquest/metaquest_meaning_index.{yaml,json,md}`
- System-Index: `../../bedeutungssigillin/metaquest/system/metaquest_system_index.{yaml,json,md}`
- Kampagnen-Index: `../../bedeutungssigillin/metaquest/wissenschaftsprojekt/metaquest_campaign_index.{yaml,json,md}`
- System-Kompass: `../../bedeutungssigillin/metaquest/system/metaquest_system_compass.{yaml,json,md}`
- Kampagnen-Kompass: `../../bedeutungssigillin/metaquest/wissenschaftsprojekt/metaquest_campaign_compass.{yaml,json,md}`
- System-Sigil: `../../bedeutungssigillin/system/metaquest/metaquest_system_sigil.{yaml,json,md}`
- Kampagnen-Sigil: `../../bedeutungssigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_sigil.{yaml,json,md}`

Halte alle drei Laternen synchron, damit die Schattenwache jede Drift sofort sieht.
