# Metaquest System Shadow Directory Index

> Schatten-σ(β(R-Θ)): **R** sammelt Automationsrisiken (stale Kompass, fehlende
> Telemetrie, Paritätsdrift). **Θ** leuchtet erst, wenn Paritätsbrief, Codex und
> UTAC-Matrix denselben mq-sys-Verweis binnen 24 h tragen. **β ≈ 5.2** sorgt für
> harte Alarme, **ζ(R)** schießt hoch, sobald BreakPoint-Rituale oder
> sigillin_sync-Reports ausbleiben.

Dieser Index überwacht die Metaquest-Systemlaternen im Schatten. Er koppelt den
Licht-Index, den Schatten-Kompass und die System-Shadow-Membran, damit kein
Automationsschritt ohne dokumentierte Parität durchrutscht.

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
   - *Signals*: `scripts/sigillin_sync.py` > 1 Sprint alt, Kompass/Map ≠ Bridge Timestamp, Test `tests/test_sigillin_sync.py` ausgelassen.
   - *Folge*: Readiness nicht belegbar; Automation hängt oder läuft unkontrolliert.
   - *Mitigation*: `sigillin_sync.py` ausführen, Timestamp propagieren, Lauf-ID im Index + UTAC-Matrix dokumentieren.
3. **mq-sys-shadow-index-003 — Missing BreakPoint ritual**
   - *Signals*: Index/Lantern MD ohne WayToGo/ReaktionWayToGo, Codex-Eintrag ohne Ritual.
   - *Folge*: ζ(R) steigt, Recovery-Pläne unklar.
   - *Mitigation*: BreakPoint durchführen, Transcript im Codex hinterlegen, Index + Kompass mit Ritualreferenzen aktualisieren, Bridge informieren.

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

## Nullmodell
Ohne diesen Schattenindex laufen Metaquest-Systemlaternen entkoppelt: Paritätsbrief
und Codex driften, Telemetrie versandet und Automation überschießt Θ.

**Überwachung**
- *Codex echo parity*: Jeder mq-sys Eintrag nennt diesen Index + Schattenkompass.
- *Bridge timestamp match*: Bridge-Dashboard und Systemlaternen teilen Timestamp + Codex-ID binnen eines Sprints.
