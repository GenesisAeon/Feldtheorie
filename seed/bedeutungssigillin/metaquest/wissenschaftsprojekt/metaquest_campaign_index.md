# Metaquest Campaign Directory Index

> σ(β(R-Θ)) für die Kampagnenlaterne: **R** bündelt Manuskript-Cadenz, Outreach-Assets
> und das Endorsement-Ledger. **Θ** leuchtet, wenn `seed/Manuskriptfinalisierung und
> Kampagnenstart.pdf` und `docs/utac_status_alignment_v1.2.md` dieselbe Paritäts-ID im
> Codex teilen. **β ≈ 4.8** hält die Aktivierung steil, während **ζ(R)** durch
> BreakPoint-Rituale, ArchivSucheUTAC und den Paritätsbrief gedämpft bleibt.

Dieses Verzeichnis bündelt alle Kampagnen-Laternen, damit Story, Governance und
Simulator-Demos synchron in die Metaquest-Launchphase gleiten.

## Parent & Shadow Links
- **Bridge Index**: `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.yaml`
- **Campaign Map**: `seed/bedeutungssigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_map.yaml`
- **Campaign Sigil**: `seed/bedeutungssigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_sigil.yaml`
- **Shadow Index**: `seed/shadow_sigillin/metaquest/wissenschaftsprojekt/metaquest_campaign_shadow_index.yaml`

## Lanterns
1. **Metaquest Campaign Map** (`seed/bedeutungssigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_map.{yaml,json,md}`)
   - *Fokus*: Manuskript-, Outreach- und Endorsement-Cadenz.
   - *Paritäts-Anker*: `seed/Manuskriptfinalisierung und Kampagnenstart.pdf`, `docs/utac_status_alignment_v1.2.md#metaquest-handshake`.
   - *Evidenz*: `seed/Finalize_Publish.txt`, `seed/BreakPointAnalyse/WayToGo.txt`.
2. **Metaquest Campaign Compass** (`seed/bedeutungssigillin/metaquest/wissenschaftsprojekt/metaquest_campaign_compass.{yaml,json,md}`)
   - *Fokus*: Sprint-Playlist, Governance, Codex-Hooks.
   - *Paritäts-Anker*: `docs/metaquest_parity_brief.md`, `seed/codexfeedback.md`.
   - *Evidenz*: `seed/bedeutungssigillin/metaquest/wissenschaftsprojekt/metaquest_campaign_compass.md`.
3. **Metaquest Campaign Sigil** (`seed/bedeutungssigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_sigil.{yaml,json,md}`)
   - *Fokus*: Bedeutungs-Schicht für Kampagnenresonanz → Parität + Governance.
   - *Paritäts-Anker*: `seed/bedeutungssigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_sigil.md`, `seed/bedeutungssigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_map.yaml`.
   - *Evidenz*: `seed/shadow_sigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_shadow.yaml`.
4. **Metaquest Parity Brief** (`docs/metaquest_parity_brief.md`)
   - *Fokus*: mq-parity-001…004 für Telemetrie, Playlist, Endorsements, Codex.
   - *Paritäts-Anker*: `docs/utac_status_alignment_v1.2.md#metaquest-handshake`, `seed/codexfeedback.yaml`.
   - *Evidenz*: `seed/Finalize_Publish.txt`.
5. **ArchivSucheUTAC Resonance Ledger** (`seed/ArchivSucheUTAC/`)
   - *Fokus*: Archiv- und Resonanz-Linie vor jeder Veröffentlichung.
   - *Paritäts-Anker*: `docs/utac_status_alignment_v1.2.md#activation-gaps`, `ZENODO_DESCRIPTION_v1.1.md`.
   - *Evidenz*: `seed/BreakPointAnalyse/ReaktionWayToGo.txt`.

## Activation Hooks
- **Manuscript checkpoint reached** → Kampagnenkarte + Sigil updaten, Codex-Entry mit mq-sci-Verweis anlegen, Bridge-Dashboard synchronisieren.
  - *Guard*: Kein Codex-Verweis innerhalb 24 h → `mq-sci-shadow-001`.
- **Outreach asset or endorsement logged** → Kompass, Paritätsbrief und ArchivSuche-Ledger aktualisieren; Codex informieren.
  - *Guard*: Fehlender Archiv-Link → `mq-sci-shadow-002`.

## Nullmodell
Ohne diesen Index löst sich die Kampagnenmembran: Paritätsbrief, Archivlinie und Codex verlieren
die Kopplung, Endorsements und Outreach geraten asynchron.

**Erkennung & Gegenmaßnahmen**
- *Signal*: Paritätsbrief-Timestamp neuer als Kompass-Metadaten.
  - *Aktion*: Kompass + Index aktualisieren, Codex-Nachtrag mit mq-sci-Vektoren.
- *Signal*: Outreach/Press-Dokument ohne ArchivSuche-Referenz.
  - *Aktion*: Asset + Codex nachrüsten, bevor Veröffentlichung erfolgt.
