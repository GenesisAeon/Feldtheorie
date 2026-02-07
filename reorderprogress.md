# Reorder Progress – Repo-Erosion & Reifegradscan

**ID:** `repo-reorderprogress-2026-02-07-a`  
**Timestamp (UTC):** `2026-02-07T22:10:00Z`  
**Branch Head:** `working`

## Logistic Pulse

- **R (offene Signale):** 2434 Marker-Hits (`TODO/FIXME/...`)  
- **Θ (Soll):** 0 offene Signale (Ideal)  
- **β:** 4.8  
- **ζ(R):** weiterhin hoch, aber mit dokumentierten Restclustern in Zenodo/V2-Roadmaps  
- **σ(β(R-Θ)) (heuristisch):** ~1.0 → starke Aktivierung, Backlog klar sichtbar

## Was wurde abgearbeitet (deep → root)

- [x] **D1 (deep):** Tiefe Legacy-/Action-Ordner (depth ≥ 5) kartiert.
- [x] **D2 (deep):** Release-V6 Finalize-/Chronik-Cluster auf offene Signale geprüft.
- [x] **M1 (mid):** Root-Domänen nach Marker-/Checklist-Dichte priorisiert.
- [x] **R1 (root):** Repo-Checks (`make preset-guard`, `make docs-index`, `make test`) aktuell grün ausgeführt.

## Kernbefunde

### 1) Hotspots (Root-Ebene)

1. `seed` – höchste offene Checklist-Dichte  
2. `archive` – starke Legacy-Task-Last  
3. `releases` – große offene Release-Orchestrierung  
4. `docs` – viele offene Dokumentations-Checkpoints

### 2) Top-Dateien mit offenen Markern

- `releases/V6-Plans_etc/Finalize/Finalize_TODO.{yaml,json}` (je 113)
- `releases/V6-Plans_etc/V6ToDorefresh.{yaml,json}` (je 100)
- `experiments/experiments_todo_index.{yaml,json}` (je 66)

### 3) Top-Markdown-Checklisten (offene Boxen, aktueller Stand)

- `releases/V6-Plans_etc/Zenodo_Upload_Checklist.md` (133)
- `seed/SUBMISSION_ROADMAP.md` (121)
- `seed/NextVersionPlan/UMSETZUNGSPLAN_V2.md` (88)
- `seed/paper/PRE_SUBMISSION_CHECKLIST.md` (43)
- `experiments/Phaethon_Geminiden_Bennu/STRATEGIC_ROADMAP.md` (42)

### 4) Build-/Test-Hygiene

- `make preset-guard` ✅ grün.
- `make docs-index` ✅ läuft (mit dokumentiertem Index-Diff-Hinweis).
- `make test` ✅ läuft mit nox/Python 3.12 (1021 passed).

## Empfohlene nächste Welle (Status aktualisiert)

### P0

1. Release-V6 TODO-Konsolidierung (`Finalize_TODO.*`, `V6ToDorefresh.*`)  
   **Status:** `completed_in_wave_2026-02-07`
2. Zenodo-Readiness (`Zenodo_Upload_Checklist.md`, `seed/SUBMISSION_ROADMAP.md`)  
   **Status:** `in_progress_with_documented_residuals_2026-02-07`

### P1

1. V2-Planlaternen (`seed/NextVersionPlan/*`)  
   **Status:** `in_progress_with_documented_residuals_2026-02-07`
2. README-Gaps in aktiven Deep-Ordnern (`seed/*sigillin*/**/lanterns`, Legacy-Actions)  
   **Status:** `completed_in_wave_2026-02-07d`

### P2

1. CI/Test-Matrix angleichen (nox + Python-Version, Makefile-Targets)  
   **Status:** `completed_in_wave_2026-02-07`

## Residual-Backlog (bewusst offen)

- `releases/V6-Plans_etc/Zenodo_Upload_Checklist.md`: 133 offene Checkboxen
- `seed/SUBMISSION_ROADMAP.md`: 121 offene Checkboxen
- `seed/NextVersionPlan/UMSETZUNGSPLAN_V2.md`: 88 offene Checkboxen
- `seed/NextVersionPlan/RELEASE_CHECKLIST.md`: 25 offene Checkboxen

## Falsifizierbarkeit / Nullmodell

- **Nullmodell:** gleichmäßige Verteilung offener Punkte über Domänen.
- **Signalmodell:** beobachtete Verdichtung in `seed/archive/releases/docs`.
- **ΔAIC/CI:** weiter **pending** (keine numerische Re-Regression in dieser Welle).

## Implementation Wave d (2026-02-07)

- Legacy README-Gaps in `RoadToV.3/Action` und `RoadToV.3/Claude-Datenpacket` geschlossen.
- Reorder-TriLayer auf konsistenten Ist-Stand aktualisiert.
- P0/P1-Restaufgaben explizit als Residual-Backlog markiert (kein falsches „vollständig erledigt“).
