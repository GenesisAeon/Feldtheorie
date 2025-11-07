# Metaquest Shadow Bridge

> σ(β(R-Θ)) for the guard: R tallies unresolved Metaquest risks, Θ is restored when
> the parity brief, codex echo, and bridge dashboard align within 24h, β≈5.1 keeps
> escalation sharp, and ζ(R) spikes if BreakPoint rituals or telemetry fall silent.

## Alerts

1. **mq-bridge-shadow-001 — Bridge dashboard stale**
   - *Signal*: UTAC matrix lacks the latest bridge note, bridge MD timestamp trails
     codex by >24h, or parity brief changes without bridge citation.
   - *Consequence*: Automation and outreach drift; Θ becomes invisible.
   - *Mitigation*: Freeze Metaquest changes, refresh dashboard, align both beacons,
     document remediation in codex.

2. **mq-bridge-shadow-002 — Telemetry mismatch**
   - *Signal*: Beacons cite different telemetry timestamps/codex ids or
     sigillin_sync report missing for a sprint.
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

## Playbooks

- **mq-bridge-shadow-001 fired** → halt Metaquest tasks, update bridge + UTAC matrix,
  publish codex entry with timeline.
- **mq-bridge-shadow-002 fired** → execute telemetry export, align timestamps, alert
  stewards if delay > sprint.
- **mq-bridge-shadow-003 fired** → refresh indices, rerun parser, notify maintainers,
  document closure across bridge/beacons.

## Coupling

Light-side reference: `../../bedeutungssigillin/metaquest/metaquest_meaning_index.{yaml,json,md}` — keep both membranes in parity.
