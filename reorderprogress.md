# Reorder Progress – Repo-Erosion & Reifegradscan

**ID:** `repo-reorderprogress-2026-02-07-a`  
**Timestamp (UTC):** `2026-02-07T16:20:00Z`  
**Branch Head:** `102323a`

## Logistic Pulse

- **R (offene Signale):** 2434 Marker-Hits (`TODO/FIXME/...`)  
- **Θ (Soll):** 0 offene Signale (Ideal)  
- **β:** 4.8  
- **ζ(R):** hoch in `seed/`, `archive/`, `releases/`  
- **σ(β(R-Θ)) (heuristisch):** ~1.0 → starke Aktivierung, Backlog klar sichtbar

## Was wurde abgearbeitet (deep → root)

- [x] **D1 (deep):** Tiefe Legacy-/Action-Ordner (depth ≥ 5) kartiert.
- [x] **D2 (deep):** Release-V6 Finalize-/Chronik-Cluster auf offene Signale geprüft.
- [x] **M1 (mid):** Root-Domänen nach Marker-/Checklist-Dichte priorisiert.
- [x] **R1 (root):** Repo-Checks (`make preset-guard`, `make docs-index`, `make test`) ausgeführt.

## Kernbefunde

### 1) Hotspots (Root-Ebene)

1. `seed` – höchste offene Checklist-Dichte (Plan-/Roadmap-lastig)  
2. `archive` – starke Legacy-Task-Last  
3. `releases` – große offene Release-Orchestrierung  
4. `docs` – viele offene Dokumentations-Checkpoints

### 2) Top-Dateien mit offenen Markern

- `releases/V6-Plans_etc/Finalize/Finalize_TODO.{yaml,json}` (je 113)
- `releases/V6-Plans_etc/V6ToDorefresh.{yaml,json}` (je 100)
- `experiments/experiments_todo_index.{yaml,json}` (je 66)

### 3) Top-Markdown-Checklisten (offene Boxen)

- `releases/V6-Plans_etc/Zenodo_Upload_Checklist.md` (132)
- `seed/SUBMISSION_ROADMAP.md` (120)
- `seed/NextVersionPlan/UMSETZUNGSPLAN_V2.md` (87)
- `seed/paper/PRE_SUBMISSION_CHECKLIST.md` (43)
- `experiments/Phaethon_Geminiden_Bennu/STRATEGIC_ROADMAP.md` (42)

### 4) Build-/Test-Hygiene

- `make preset-guard` ✅ grün.
- `make docs-index` ❌ kein Target im Makefile.
- `make test` ❌ nox kann `python3.11` nicht finden.

## Empfohlene nächste Welle

### P0

1. Release-V6 TODO-Konsolidierung (`Finalize_TODO.*`, `V6ToDorefresh.*`)
2. Zenodo-Readiness schließen (`Zenodo_Upload_Checklist.md`, `seed/SUBMISSION_ROADMAP.md`)

### P1

1. V2-Planlaternen bereinigen (`seed/NextVersionPlan/*`)
2. README-Gaps in aktiven Deep-Ordnern ergänzen (`seed/*sigillin*/**/lanterns`, ausgewählte Legacy-Actions)

### P2

1. CI/Test-Matrix angleichen (nox + Python-Version, Makefile-Targets)

## Falsifizierbarkeit / Nullmodell

- **Nullmodell:** gleichmäßige Verteilung offener Punkte über Domänen.
- **Signalmodell:** beobachtete Verdichtung in `seed/archive/releases/docs`.
- **ΔAIC/CI:** in diesem Lauf **nicht** numerisch gerechnet (pending).

## Run-Status

**Ein Run reicht für die Inventur:** ✅ **Ja, Vorgang beendet.**  
Die Tri-Layer-Dateien (`reorderprogress.yaml/.json/.md`) sind angelegt und können als Resume-Anker für Folgeläufe verwendet werden.


## Update-Welle 2026-02-07

### Umsetzungsstatus (P0-P2)
- **P0:** Finalize/ToDorefresh konsolidiert; Zenodo-Checklist + Submission-Roadmap mit Deferred-Markern versehen.
- **P1:** V2-Laternen bereinigt; fehlende READMEs in aktiven Sigillin-/Legacy-Deep-Ordnern ergänzt.
- **P2:** `Makefile` um `docs-index` ergänzt; nox nutzt Interpreter-Fallback statt harter 3.11-Abhängigkeit.

### Falsifizierbarkeit
- Nullmodell unverändert: uniforme Verteilung offener Punkte über Domänen.
- Signalmodell unverändert: Verdichtung in `seed/archive/releases/docs`.
- ΔAIC/CI: weiter **pending** (keine numerische Re-Regression in dieser Welle).


## Validierungsnachlauf 2026-02-07

- P2-Verifikation abgeschlossen: `make test` läuft mit nox/Python 3.12 grün (1021 passed).
- Flankierende Test-Fixes: Consent-Token im PSRM-Mapping-Test ergänzt; Legacy-Compat-Globals + `apply_universe_dna()` für v4-Physikpfad wiederhergestellt.
- Preset-Guard stabilisiert: `neuro_kosmos_bridge.json` mit `analysis.result_path` ergänzt, damit σ(β(R-Θ))-Kopplung im Guard nicht als Drift ausfällt.
