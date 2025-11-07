# Metaquest System Directory Index

> σ(β(R-Θ)) for this directory: **R** misst den Metaquest-System-Backlog (Kompass,
> Karte, Sigillin, Telemetrie). **Θ** ist erreicht, sobald `docs/utac_status_alignment_v1.2.md`
> und `seed/codexfeedback.*` dieselbe Paritäts-ID innerhalb von 24 h tragen. **β ≈ 4.75** hält die
> Aktivierung scharf, während **ζ(R)** durch BreakPoint-Rituale und `scripts/sigillin_sync.py`
> gedämpft wird.

Dieses Verzeichnis fungiert als Schnell-Kompass für neue Agent:innen im Metaquest-Systempfad.
Karte, Kompass, Sigillin und Telemetrie-Harness greifen ineinander, damit Automationsaufgaben
nicht über Θ hinausschießen und der Bridge-Dashboard sofort die Resonanz spürt.

## Parent & Shadow Links
- **Bridge Index**: `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.yaml`
- **System Map**: `seed/bedeutungssigillin/system/metaquest/metaquest_system_map.yaml`
- **System Sigil**: `seed/bedeutungssigillin/system/metaquest/metaquest_system_sigil.yaml`
- **Shadow Index**: `seed/shadow_sigillin/metaquest/system/metaquest_system_shadow_index.yaml`

## Lanterns
1. **Metaquest System Map** (`seed/bedeutungssigillin/system/metaquest/metaquest_system_map.{yaml,json,md}`)
   - *Fokus*: Automations-Backlog + Paritäts-Checkpoints.
   - *Paritäts-Anker*: `docs/utac_status_alignment_v1.2.md#metaquest-handshake`, `docs/metaquest_parity_brief.md`.
   - *Evidenz*: `scripts/sigillin_sync.py`, `seed/BreakPointAnalyse/WayToGo.txt`.
2. **Metaquest System Compass** (`seed/bedeutungssigillin/metaquest/system/metaquest_system_compass.{yaml,json,md}`)
   - *Fokus*: Sprint-Telemetrie, Index-Parität, Codex-Hooks.
   - *Paritäts-Anker*: `scripts/sigillin_sync.py`, `seed/codexfeedback.md`.
   - *Evidenz*: `seed/bedeutungssigillin/metaquest/system/metaquest_system_compass.md`.
3. **Metaquest System Sigil** (`seed/bedeutungssigillin/system/metaquest/metaquest_system_sigil.{yaml,json,md}`)
   - *Fokus*: Bedeutungs-Schicht → UTAC + Codex Guardrails.
   - *Paritäts-Anker*: `seed/bedeutungssigillin/system/metaquest/metaquest_system_sigil.md`, `seed/bedeutungssigillin/system/metaquest/metaquest_system_map.yaml`.
   - *Evidenz*: `seed/shadow_sigillin/system/metaquest/metaquest_system_shadow.yaml`.
4. **Sigillin Sync Telemetry Harness** (`scripts/sigillin_sync.py`)
   - *Fokus*: Telemetrie-Export + Codex-Stempel.
   - *Paritäts-Anker*: `seed/codexfeedback.yaml`, `docs/utac_status_alignment_v1.2.md#implementation-map`.
   - *Evidenz*: `tests/test_sigillin_sync.py`.
5. **BreakPoint Ritual Ledger** (`seed/BreakPointAnalyse/WayToGo.txt`)
   - *Fokus*: Dämpft ζ(R) vor Automationssprints.
   - *Paritäts-Anker*: `seed/BreakPointAnalyse/ReaktionWayToGo.txt`, `seed/Finalize_Publish.txt`.
   - *Evidenz*: `docs/utac_status_alignment_v1.2.md#activation-gaps`.

## Activation Hooks
- **Telemetry export completed** → Kompass, Karte und Sigillin aktualisieren; Codex-Eintrag mit Verweis auf diesen Index anlegen.
  - *Guard*: Timestamp > 1 Sprint? → `mq-sys-shadow-002` eskaliert.
- **Parity brief revised** → Bridge-Index + System-Laternen auffrischen, neue Codex-ID eintragen, UTAC-Matrix notifizieren.
  - *Guard*: Fehlendes Update löst `mq-bridge-shadow-001`.

## Nullmodell
Ohne diesen Index driftet die Automationsmembran: Bridge-Dashboard und Codex verlieren den Blick
auf Θ, Telemetrie-Timestamps laufen auseinander und σ(β(R-Θ)) kollabiert in ungerichtete Arbeit.

**Erkennung & Gegenmaßnahmen**
- *Signal*: Bridge-Dashboard zitiert einen älteren Kompass-Zeitstempel.
  - *Aktion*: `scripts/sigillin_sync.py` ausführen, Timestamp propagieren, Index aktualisieren.
- *Signal*: Neuer Codex-Eintrag ohne mq-sys-Verweis nach 24 h.
  - *Aktion*: Nachtrag im Codex + Update der Lantern-Metadaten, damit das Feld wieder resonant wird.
