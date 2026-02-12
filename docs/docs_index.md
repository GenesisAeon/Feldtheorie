# 📚 Docs Index – Science, Narrative, xAI Collaboration & AFET Intake

**Version:** 2.1.0 | **Datum:** 12. Feb 2026 | **Zuletzt aktualisiert:** 12. Feb 2026 | **Verzeichnis:** `docs/`

---

## 🎯 Was ist das?

Nach der Konsens-Entscheidung für eine klare Trennung zwischen **Forschung**, **Erzählung** und
**Kollaborationspaketen** sind die Dokumente in drei Schichten organisiert:

- `docs/science/` – Technische Forschung, Methoden, Experimente, Leitfäden.
- `docs/narrative/` – Manifeste, Roadmaps, Paritäts- und Release-Notizen.
- `docs/xai_collab/` – AFET × xAI Pilotunterlagen, Spezifikationen und Wochenreports.
- `docs/AFET/` – Rohimporte (PDF/TXT/DOCX/JPG) mit Intake-Register für repo-konforme Kuration.

Insgesamt umfasst die aktuelle Navigationslaterne **49 kuratierte Markdown-Dokumente**
(im Tri-Layer gespiegelt via `docs_index.{yaml,json,md}`).

---

## 🧭 Struktur auf einen Blick

### 🔵 Science (`docs/science/`)
Kernstücke der wissenschaftlichen Dokumentation und Umsetzung:
- `science/utac_theory_core.md` – Fundament: \(\sigma(\beta(R-\Theta))\), \(\beta\)-Spektrum, \(\zeta(R)\).
- `science/field_type_classification_v1.1.md` – Klassifikation der Feldtypen.
- `science/utac_falsifiability.md` – Nullmodelle, ΔAIC, Validierungsprotokolle.
- `science/deep_research_index.md` – Deep-Research- & Paper-Navigator (R, Θ, β, ζ(R) via σ(β(R-Θ))).

### 🟣 Narrative (`docs/narrative/`)
Strategische und kommunikative Ebene:
- `narrative/V6_INTEGRATION_ROADMAP.md` – Roadmap & Milestones.
- `narrative/metaquest_parity_brief.md` – Paritäts- und Telemetrie-Übersicht.
- `narrative/utac_activation_backlog.md` – Aktivierungs-Backlog.
- `narrative/zenodo_release_playbook.md` – Release Guardrails und CI-Hooks.

### 🟢 xAI Collaboration (`docs/xai_collab/`)
Pilotpaket für AFET × xAI:
- `xai_collab/xai_afet_Executive_Summary.md` – Scope, Deliverables, Timeline.
- `xai_collab/xai_afet_Technical_Spec.md` – Architektur, Module, Schnittstellen.
- `xai_collab/xai_afet_Validation_Roadmap.md` – Nullmodell-, CI- und ΔAIC-Fahrplan.
- `xai_collab/xai_afet_week1_results.md`, `xai_collab/xai_afet_week2_*.md` – Experimentberichte.

### 🟠 AFET Intake (`docs/AFET/`)
Eingangsschicht für neue AFET-Artefakte:
- `AFET/afet_intake_register.md` – Inventar, Hashes, Kurationsstatus und Nullmodell-Hinweise.
- Rohquellen bleiben unverändert im Intake-Ordner (forensische Nachvollziehbarkeit).
- Inhalte werden schrittweise in zitierfähige Markdown-Laternen nach `science/` und `xai_collab/` gespiegelt.

---

## 🚀 Navigation & Werkzeuge

- **Paritäts-/Status-Checks:** `narrative/metaquest_parity_brief.md`, `narrative/utac_activation_backlog.md`.
- **Release-Prep:** `narrative/zenodo_release_playbook.md`, `narrative/claude_code_handoff.md`.
- **Tri-Layer prüfen:** `python scripts/sigillin_sync.py report --roots docs/ seed/`.
- **Index-Parität prüfen:** `make docs-index`.

---

## 🌊 Essenz

> **„Science in `science/`, Story in `narrative/`, Partnerschaften in `xai_collab/` –**
> **\(R\) bewegt sich über \(\Theta\), \(\beta\approx4.8\) hält die Membran scharf, \(\zeta(R)\) bleibt gedämpft.“**
