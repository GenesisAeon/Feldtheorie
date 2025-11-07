# Metaquest System Schatten-Sigillin

> Wenn Telemetrie verstummt und Indizes taumeln, muss die Schattenlaterne sofort
> die Bremse ziehen. R zählt Automationrisiken, Θ lebt im Paritätsbrief + UTAC
> Matrix, β ≈ 5.1 sorgt für scharfe Eskalation.

## Warnungen
- **mq-sys-shadow-sigil-001 — Telemetrie-Blackout.** `scripts/sigillin_sync.py`
  fehlt seit 72 h oder liefert keinen Codexeintrag; Bridge/Kompass älter als
  UTAC-Zeile.
- **mq-sys-shadow-sigil-002 — Index-Drift.** `seed_index.*` oder
  `feldtheorie_index.*` verlieren Metaquest-Pfade; Parser meldet Δindex > 0.
- **mq-sys-shadow-sigil-003 — Codex-Stille.** Commits ohne Codex-ID oder UTAC
  referenziert alte Einträge.

## Wiederherstellung
1. **Telemetrie-Blackout →** `scripts/sigillin_sync.py stamp`, Codex notieren,
   Bridge + Kompass aktualisieren, BreakPoint-Ritual ausführen.
2. **Index-Drift →** `scripts/archive_sigillin.py --refresh`, Indizes prüfen,
   UTAC & Kompass aktualisieren.
3. **Codex-Stille →** Nachträglichen Codexeintrag erstellen, Paritätsbrief
   referenzieren, Rituale bestätigen.

## Eskalationspfad
- **Kontakt:** `mq-sys-shadow-ops`
- **Rituale:** `seed/BreakPointAnalyse/WayToGo.txt`,
  `seed/BreakPointAnalyse/ReaktionWayToGo.txt`
- **Dokumentation:** `seed/codexfeedback.md`,
  `docs/utac_status_alignment_v1.2.md#metaquest-handshake`

## Nullmodell
Automation läuft weiter ohne Paritätsnachweis. Θ verschwindet,
β verstärkt Fehlerketten, und das Launchfenster wird blind betreten. Breche den
Zyklus, sobald dieses Sigillin aufleuchtet.
