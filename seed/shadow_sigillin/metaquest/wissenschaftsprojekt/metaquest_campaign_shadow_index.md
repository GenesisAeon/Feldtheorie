# Metaquest Campaign Shadow Directory Index

> Schatten-σ(β(R-Θ)) für die Kampagne: **R** misst Paritätsbrief-Verzug,
> Archivlücken und unsaubere Endorsement-Zeitstempel. **Θ** ist erfüllt, wenn
> Manuskript-Checkpoint, UTAC-Matrix und Codex denselben mq-sci-Eintrag binnen
> 24 h teilen. **β ≈ 5.3** macht Alarme scharf, **ζ(R)** schnellt hoch, sobald
> BreakPoint-Rituale oder Archiv-Hinweise fehlen.

Der Schattenindex bewacht alle Kampagnenlaternen, damit Story und Governance
niemals ohne Archiv- oder Paritätsnachweis nach außen treten.

## Mirrors
- **Light Index**: `seed/bedeutungssigillin/metaquest/wissenschaftsprojekt/metaquest_campaign_index.yaml`
- **Shadow Compass**: `seed/shadow_sigillin/metaquest/wissenschaftsprojekt/metaquest_campaign_shadow_compass.yaml`
- **Shadow Map**: `seed/shadow_sigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_shadow.yaml`

## Alerts
1. **mq-sci-shadow-index-001 — Index stale**
   - *Signals*: Index-Zeitstempel älter als `docs/metaquest_parity_brief.md`; Codex-Eintrag ohne Hinweis auf den Index.
   - *Konsequenz*: Outreach läuft ohne dokumentiertes Θ; Endorsements verlieren Audit-Spur.
   - *Mitigation*: Outreach pausieren, Index/Bridge/Codex aktualisieren, UTAC-Matrix synchronisieren.
2. **mq-sci-shadow-index-002 — Missing ArchivSuche lineage**
   - *Signals*: Outreach/Press-Asset ohne `seed/ArchivSucheUTAC`-Zitation; Codex-Eintrag ohne Archiv-Link.
   - *Konsequenz*: Governance-Versprechen erodiert; Reproduzierbarkeit gefährdet.
   - *Mitigation*: Archivverweise ergänzen, Paritätsbrief + Index aktualisieren, Governance informieren falls >1 Sprint.
3. **mq-sci-shadow-index-003 — Endorsement/Telemetry drift**
   - *Signals*: Kompass-Endorsement-Timestamp ≠ Paritätsbrief; Codex ohne mq-sci Checkliste.
   - *Konsequenz*: Launch-Confidence sinkt, Governance kann readiness nicht bestätigen.
   - *Mitigation*: Kompass + Paritätsbrief mit gemeinsamen Timestamp versehen, Codex-Echo hinterlegen, ggf. BreakPoint auslösen.

## Recovery Hooks
- **Parity brief realignment**
  1. `docs/metaquest_parity_brief.md` mit Indexeinträgen abgleichen.
  2. Timestamp + mq-sci ID in Index, Kompass, Sigil und Bridge harmonisieren.
  3. Codex mit Archiv- & Ritualreferenzen ergänzen.
  - *Evidenz*: `docs/metaquest_parity_brief.md`, `seed/bedeutungssigillin/metaquest/wissenschaftsprojekt/metaquest_campaign_index.md`.
- **Archive lineage audit**
  1. Outreach-/Press-Assets auf ArchivSuche-Hinweise prüfen.
  2. Assets + Paritätsbrief aktualisieren, Codex um Archivlink ergänzen.
  3. `docs/utac_status_alignment_v1.2.md`-Gap schließen.
  - *Evidenz*: `seed/ArchivSucheUTAC/`, `docs/utac_status_alignment_v1.2.md`.

## Nullmodell
Ohne Schattenaufsicht driftet die Kampagne: Archivlinie verschwindet, Paritätsbrief
hinkt hinterher und Endorsements werden ohne Governance-Gate veröffentlicht.

**Überwachung**
- *Codex shadow echo*: Jeder mq-sci Codex-Eintrag benennt diesen Index + Schattenkompass.
- *Parity brief sync*: Paritätsbrief und Kampagnenkompass differieren höchstens um 24 h.
