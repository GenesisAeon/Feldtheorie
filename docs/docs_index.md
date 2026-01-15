# 📚 Docs Index – Science & Narrative Split

**Version:** 2.0.0 | **Datum:** 25. Dez 2025 | **Zuletzt aktualisiert:** 15. Jan 2026 | **Verzeichnis:** `docs/`

---

## 🎯 Was ist das?

Nach der Konsens-Entscheidung für eine klare Trennung zwischen **Forschung** und **Erzählung** sind alle Dokumente jetzt in zwei
Schichten organisiert:

- `docs/science/` – Technische Forschung, Methoden, Experimente, Leitfäden.
- `docs/narrative/` – Manifeste, Roadmaps, Paritäts- und Release-Notizen.

Insgesamt umfasst das Archiv aktuell **147 Markdown-Dokumente** plus die Spiegeldateien (`*.json`, `*.yaml`).

---

## 🧭 Struktur auf einen Blick

### 🔵 Science (`docs/science/`)
Kernstücke der wissenschaftlichen Dokumentation und Umsetzung:
- `science/utac_theory_core.md` – Fundament: \(\sigma(\beta(R-\Theta))\), \(\beta\)-Spektrum, \(\zeta(R)\).
- `science/utac_v2_synthesis.md` – Multi-Attraktor-Framework (β domänenspezifisch, 78 Systeme).
- `science/v6_entropy_governance_tesseract_physics.md` – Entropie-Dualität & Tesseract-Physik.
- `science/field_type_classification_v1.1.md` – Klassifikation der Feldtypen.
- `science/utac_falsifiability.md` – Nullmodelle, ΔAIC, Validierungsprotokolle.
- `science/USER_GUIDE.md` – Praktische Bedienung (CLI, API, Workflows) mit Anker-Referenzen.
- Unterordner: `appendices/`, `empirical_evidence/`, `ethics/`, `figures/`, `theoretical_extensions/`, `tutorials/`.

### 🟣 Narrative (`docs/narrative/`)
Strategische und kommunikative Ebene:
- `narrative/V10_DEEP_RESEARCH_MANIFEST.md`, `narrative/V12_CRYSTAL_GARDENER_MANIFEST.md`, `narrative/V3_FRONTIER_MANIFEST.md` – Langfristige Leitbilder.
- `narrative/V6_INTEGRATION_ROADMAP.md`, `narrative/Emergenz_Roadmap_2025-12-18.md` – Roadmaps & Milestones.
- `narrative/metaquest_parity_brief.md`, `narrative/utac_activation_backlog.md` – Paritäts- und Aktivierungsübersichten.
- `narrative/utac_v2_activation_tracker_2026-08.md` (und Vorgänger) – Gap-Scans & Telemetrie.
- `narrative/theoretical_mirror_framework.md` – UTAC-Nutzungsleitfaden als Theoretical Mirror Framework.
- `narrative/zenodo_release_playbook.md`, `narrative/zenodo_multilingual_abstract_v1.2.md` – Release-Kommunikation.
- Weitere Kontexte: `outreach/`, `parity_briefs/`, `reviews/`, `meta/`.

---

## 🚀 Navigation & Werkzeuge

- **Schnellstart:**
  - Theorie: `science/utac_theory_core.md` → `science/utac_v2_synthesis.md` → `science/v6_entropy_governance_tesseract_physics.md`.
  - Praxis: `science/USER_GUIDE.md` (siehe MkDocs-Navigation) & `science/METHODS.md`.
- **Paritäts-/Status-Checks:** `narrative/metaquest_parity_brief.md`, `narrative/utac_activation_backlog.md`.
- **Release-Prep:** `narrative/zenodo_release_playbook.md`, `narrative/claude_code_handoff.md` (Tri-Layer Hooks beachten).
- **Tri-Layer prüfen:** `python scripts/sigillin_sync.py report --roots docs/ seed/` (keine offenen Gaps vor Merge).

---

## 🌊 Essenz

> **„Science in `science/`, Story in `narrative/` – \(R\) und \(\Theta\) entkoppeln sich sauber, \(\beta\approx4.8\) hält die
> Membran scharf, \(\zeta(R)\) bleibt gedämpft.“**
