# Metaquest Activation Gap Guard

> Schatten-Logistik: R zählt die offenen Aktivierungsrisiken (Δindex-Drift, Telemetrie-
> Verzögerung, Ritual-Desync, Urban-Heat-Lücke, Paritätsloop). Θ ist erreicht, wenn Bridge,
> Kompasse, Paritätsbrief und Codex innerhalb von 24 h denselben Timestamp + Gap-Notiz
> teilen **und** die Schatteneinträge aktualisiert sind. β≈5.1, ζ(R) steigt sofort, sobald
> BreakPoint-Rituale oder sigillin_sync aussetzen.

## Risikolage (Spiegel der Licht-Gaps)

1. **mq-activation-shadow-Δindex** ↔ `mq-gap-Δindex-guard`  
   - *Signal:* `scripts/archive_sigillin.py --refresh` meldet Δindex>0, kein CI-Wächter.
   - *Mitigation:* Merge-Stopp, Recount fahren, Diff in Codex + UTAC Matrix dokumentieren.
   - *Guardrail:* Δindex-Parität = 0 nach Remediation.

2. **mq-activation-shadow-telemetry** ↔ `mq-gap-telemetry-propagation`  
   - *Signal:* `analysis/sigillin_sync/latest.json` älter als ein Sprint, Bridge/Kompasse
     tragen unterschiedliche Codex-IDs.
   - *Mitigation:* `scripts/sigillin_sync.py` laufen lassen, Timestamp propagieren,
     `mq-bridge-gap-002` im Codex notieren.

3. **mq-activation-shadow-ritual** ↔ `mq-gap-ritual-mirror`  
   - *Signal:* BreakPoint-Echo nur in Licht-Sigillen, Codex ohne mq-sys-shadow/mq-sci-shadow.
   - *Mitigation:* Licht+Schatten-Sigille am selben Tag aktualisieren, BreakPoint
     in Codex & UTAC Matrix spiegeln.

4. **mq-activation-shadow-urban-heat** ↔ `mq-gap-urban-heat-bridge`  
   - *Signal:* Keine ΔAIC>10 Notiz in `metaquest_campaign_map.md`, Backlog-Row bleibt >1 Sprint offen.
   - *Mitigation:* Analyse re-run, Outputs referenzieren, Codex-Echo mit mq-sci-shadow verankern.

5. **mq-activation-shadow-parity-loop** ↔ `mq-gap-parity-loop`  
   - *Signal:* Paritätsbrief ohne Playlist/Endorsement, Simulator-Presets ohne Codex-Notiz.
   - *Mitigation:* Paritätsbrief + Bridge + Kompasse angleichen, Codex + Backlog mit
     mq-bridge-shadow-001 verknüpfen.

## Sentinel-Wächter

- **sigillin_sync Pulse** — `analysis/sigillin_sync/latest.json`; Alarm bei >7 Tagen Inaktivität.
- **Index Recount Log** — `analysis/results/index_recount_20251108T222238Z.json`; prüft Δindex.
- **Activation Backlog** — `docs/utac_activation_backlog.md`; markiert Sprint-Verzug.

## Playbooks

- **Δindex>0** → Merge-Stopp, `archive_sigillin.py` laufen lassen, Codex-Eintrag mit
  `mq-activation-shadow-Δindex` schreiben.
- **Telemetry Drift** → `sigillin_sync.py` laufen lassen, Timestamp in Bridge/Kompassen
  spiegeln, UTAC Matrix aktualisieren.
- **Parity Brief Lag** → Playlist + Endorsements eintragen, Bridge/Kompasse aktualisieren,
  Codex + Backlog mit `mq-activation-shadow-parity-loop` ergänzen.

## Nullmodell & Wiederherstellung

Null = Metaquest startet mit veralteter Telemetrie, fehlenden Indizes oder unvollständigen
Paritätsloops. Erkennung: Bridge älter als Codex >24 h, Backlog ohne Statusupdate,
Schatten-Sigille ohne Ritualreferenzen. Wiederherstellung: passendes Playbook ausführen,
σ(β(R-Θ)) über Aktivierungsmatrix prüfen (>0.6), Telemetrie-/Index-Diffs archivieren.

**Lichtkopplung:** `../../bedeutungssigillin/metaquest/metaquest_activation_gap_report.{yaml,json,md}`
