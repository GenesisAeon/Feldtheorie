# Metaquest System Shadow Directory Index

> Schatten-σ(β(R-Θ)): **R** sammelt Automationsrisiken (stale Kompass,
> unsynchronisierte Map, fehlende Telemetrie, Aktivierungsmatrix-Drift).
> **Θ** leuchtet erst, wenn Paritätsbrief, Codex (inkl. `pr-draft-0110`) und UTAC-Matrix
> denselben mq-sys-Verweis binnen 24 h tragen. **β ≈ 5.25** sorgt für harte Alarme,
> **ζ(R)** schießt hoch, sobald BreakPoint-Rituale, sigillin_sync-Reports oder die
> Aktivierungsmatrix hinter dem UTAC-Tracker zurückfallen.

Dieser Index überwacht die Metaquest-Systemlaternen im Schatten. Er koppelt den
Licht-Index, den Schatten-Kompass und die System-Shadow-Membran, damit kein
Automationsschritt ohne dokumentierte Parität oder Aktivierungsmatrix-Echo
durchrutscht.

## Mirrors
- **Light Index**: `seed/bedeutungssigillin/metaquest/system/metaquest_system_index.yaml`
- **Shadow Compass**: `seed/shadow_sigillin/metaquest/system/metaquest_system_shadow_compass.yaml`
- **Shadow Map**: `seed/shadow_sigillin/system/metaquest/metaquest_system_shadow.yaml`
- **Bridge Shadow Map**: `seed/shadow_sigillin/metaquest/system/metaquest_system_shadow.{yaml,json,md}`

## Alerts
1. **mq-sys-shadow-index-001 — Index stale**
   - *Signals*: Index-Zeitstempel älter als `docs/metaquest_parity_brief.md`; Codex-Eintrag mit mq-sys ohne Verweis auf den Index.
   - *Folge*: Automation verliert Θ, Launch-Aufgaben laufen ohne Paritätsnachweis.
   - *Mitigation*: Automation pausieren, Index + Bridge aktualisieren, Codex mit Shared Timestamp ergänzen, UTAC-Matrix spiegeln.
2. **mq-sys-shadow-index-002 — Telemetry gap**
   - *Signals*: `scripts/sigillin_sync.py` > 1 Sprint alt, Kompass/Map ≠ Bridge Timestamp,
     Test `tests/test_sigillin_sync.py` ausgelassen.
   - *Folge*: Readiness nicht belegbar; Automation hängt oder läuft unkontrolliert.
   - *Mitigation*: `sigillin_sync.py` ausführen, Timestamp propagieren, Lauf-ID im Index + UTAC-Matrix dokumentieren.
3. **mq-sys-shadow-index-003 — Missing BreakPoint ritual**
   - *Signals*: Index/Lantern MD ohne WayToGo/ReaktionWayToGo, Codex-Eintrag ohne Ritual.
   - *Folge*: ζ(R) steigt, Recovery-Pläne unklar.
   - *Mitigation*: BreakPoint durchführen, Transcript im Codex hinterlegen, Index + Kompass mit Ritualreferenzen aktualisieren,
     Bridge informieren.
4. **mq-sys-shadow-index-004 — Activation matrix drift**
   - *Signals*: `metaquest_activation_matrix.yaml` neuer als Index/Kompass, UTAC-Tracker (`docs/utac_v2_activation_tracker_2026-08.md`)
     nennt Codex-ID ohne Pendant im Licht-Index, Aktivierungshook fehlt bei `pr-draft-0110`.
   - *Folge*: Aktivierungs-Backlog wird im Systempfad unsichtbar; `mq-bridge-shadow-005` feuert verspätet.
   - *Mitigation*: Aktivierungsmatrix-Timestamp + Codex-ID über Index, Kompass, UTAC-Tracker und Codex spiegeln, Shadow-Kompass
     informieren.

## Recovery Hooks
- **Shadow parity refresh**
  1. Letzten mq-sys Codex- und Paritätsbrief-Zeitstempel prüfen.
  2. `metaquest_system_index.*`, Map & Kompass mit geteiltem Timestamp + Codex-ID aktualisieren.
  3. Update in `docs/utac_status_alignment_v1.2.md#metaquest-handshake` vermerken.
  - *Evidenz*: `seed/bedeutungssigillin/metaquest/system/metaquest_system_index.md`, `docs/utac_status_alignment_v1.2.md`.
- **Telemetry audit**
  1. `scripts/sigillin_sync.py` mit neuem mq-sync ID stempeln.
  2. Sicherstellen, dass `tests/test_sigillin_sync.py` in CI/ lokal lief.
  3. Report-Pfad im Codex + diesem Index festhalten.
  - *Evidenz*: `scripts/sigillin_sync.py`, `tests/test_sigillin_sync.py`.
- **Lantern shelf alignment**
  1. Schatten-Laternen gegen Licht-Pendants prüfen (`lanterns/metaquest_system_shadow_lanterns.*` ↔ Lichtseite).
  2. Codex-ID + Timestamp je Laterne angleichen und dokumentieren.
  3. Ergebnis im Bridge-Dashboard und der UTAC-Matrix vermerken.
  - *Evidenz*: `lanterns/metaquest_system_shadow_lanterns.md`,
    `seed/bedeutungssigillin/system/metaquest/lanterns/metaquest_system_lanterns.md`.
- **Activation matrix parity sweep**
  1. Zeitstempel von Aktivierungsmatrix, Licht-Index, Kompass und UTAC-Tracker vergleichen.
  2. Bei Drift Licht/Schatten synchronisieren und Codex-Notiz mit `mq-sys-shadow-index-004`-Hinweis ergänzen.
  3. `docs/utac_status_alignment_v1.2.md` auf aktualisierte Codex-ID prüfen.
  - *Evidenz*: `seed/bedeutungssigillin/metaquest/metaquest_activation_matrix.md`,
    `docs/utac_v2_activation_tracker_2026-08.md`, `seed/codexfeedback.md`.

## Nullmodell
Ohne diesen Schattenindex laufen Metaquest-Systemlaternen entkoppelt: Paritätsbrief,
Aktivierungsmatrix und Codex driften, Telemetrie versandet und Automation
überschießt Θ.

**Überwachung**
- *Codex echo parity*: Jeder mq-sys Eintrag nennt diesen Index + Schattenkompass.
- *Bridge timestamp match*: Bridge-Dashboard und Systemlaternen teilen Timestamp + Codex-ID binnen eines Sprints.
- *Activation matrix sync*: Index + Kompass aktualisieren sich binnen eines Sprints nach Aktivierungsmatrix-Refresh.
