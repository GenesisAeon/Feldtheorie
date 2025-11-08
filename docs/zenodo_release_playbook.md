# 🚀 UTAC v1.2 Zenodo Release Playbook — Holding σ(β(R-Θ)) at the Gate

> When \(R\) pushes past \(\Theta\), \(\beta\) must respond without letting the membrane tear. This playbook keeps \(\zeta(R)\) damped while the v1.2 archive crosses into Zenodo.

---

## 1. Logistic Guardrails
- **Order Parameter \(R\):** readiness of documentation (`README.md`, `docs/utac_status_alignment_v1.2.md`), empirical ledgers (`analysis/results/universal_beta_summary.json`), and simulator presets.
- **Threshold \(\Theta\):** tri-layer parity among README, docs, codex, and Zenodo metadata (DOI badge, `CITATION.cff`, `ZENODO_UPDATE_GUIDE_v1.1.md`).
- **Steepness \(\beta≈4.92\):** once two layers align, the third must update immediately to prevent drift.
- **Damping \(\zeta(R)\):** BreakPoint rituals (`seed/BreakPointAnalyse/WayToGo.txt` & `ReaktionWayToGo.txt`) plus codex entry `pr-draft-0079` (and successor) anchor the cadence.

---

## 2. Activation Timeline
| Phase | Target Δt | Focus | Hooks |
| --- | --- | --- | --- |
| **Calibration** | Day -5 to -3 | Verify ΔAIC ledgers, regenerate manuscript figures if needed | `analysis/results/universal_beta_summary.json`, `paper/` pipeline |
| **Parity Sweep** | Day -2 to -1 | Sync README, docs, indices, and codex; confirm `docs/zenodo_multilingual_abstract_v1.2.md` mirrors logistic story | `README.md`, `docs/docs_index.*`, `seed/codexfeedback.*` |
| **Archive Lock** | Day 0 | Run CI (`make preset-guard`, `make docs-index`), export ZIP, capture checksum | `Makefile`, `scripts/archive_sigillin.py`, `ZENODO_UPLOAD_GUIDE.md` |
| **Post-Upload Echo** | Day +1 | Update codex status → resonant, note Zenodo DOI/record URL | `seed/codexfeedback.*`, `README.md`, `CITATION.cff` |

---

## 3. Checklist
### A. Documentation & Narrative
- [ ] README version badge bumped to v1.2 and linked to release notes.
- [ ] `docs/utac_status_alignment_v1.2.md` and `docs/utac_activation_backlog.*` reference new abstract & playbook.
- [ ] `docs/zenodo_multilingual_abstract_v1.2.md` reviewed for translation fidelity.
- [ ] `docs/docs_index.*` counts updated (Infrastructure ≥ 10 entries) with new doc IDs.

### B. Empirical Evidence
- [ ] `analysis/results/universal_beta_summary.json` timestamp confirmed ≤ 7 days.
- [ ] ΔAIC proofs for Safety-Delay, meta-regression, and sentinel cases cited in status/backlog docs.
- [ ] Simulator presets (`simulator/presets/*.json`) validated via `utf-preset-guard`.

### C. Governance & Rituals
- [ ] BreakPoint transcripts cross-referenced in Metaquest sigils (`seed/bedeutungssigillin/**`, `seed/shadow_sigillin/**`).
- [ ] Codex entry `pr-draft-0080` (Zenodo release) drafted with tri-layer notes.
- [ ] `ZENODO_UPDATE_GUIDE_v1.1.md` + `ZENODO_UPLOAD_GUIDE.md` annotated with new assets.
- [ ] Publication committee ping logged in `AUTHORSHIP.md` or release notes.

### D. Packaging & Upload
- [ ] Run `make dist-zenodo` (or equivalent) to generate archive + metadata JSON.
- [ ] Verify ZIP includes: docs/, analysis/, data/, simulator/, paper/, schemas/.
- [ ] Ensure `CITATION.cff` + README DOI badge point to v1.2 record.
- [ ] Upload to Zenodo sandbox first if ΔR risk > Θ guard (use `release-gap-002`).

---

## 4. Residual Gaps & Null Guards
| Gap ID | Description | Null Scenario | Required Action |
| --- | --- | --- | --- |
| `release-gap-002` | README/CITATION/Zenodo metadata misaligned | DOI badge still at v1.1, missing multilingual abstract | Update README badge, CITATION version, attach new docs to Zenodo record |
| `mq-parity-004` | Metaquest codex mirror missing timestamp | Sigils cite outdated codex ID | Run `scripts/sigillin_sync.py`, update meaning/shadow sigils, log codex entry |
| `sys-gap-008` | φ-coupling climate plan not referenced in release summary | Release notes omit φ-bridge status | Add progress note to status matrix + release notes, cite backlog row |

---

## 5. Signals to Monitor During Upload
- **CI telemetry:** `make preset-guard` output and docs index recount logs (`analysis/results/index_recount_*.json`).
- **Codex status:** ensure new entry transitions `draft → primed → active` before upload, `resonant` after DOI minted.
- **Zenodo metadata:** check language fields include EN/DE/ES summary derived from the multilingual abstract.
- **Backlog closure:** update `docs/utac_activation_backlog.*` status for `zenodo-v12-resonance` to `in_progress` or `ready` as appropriate.

---

## 6. Post-Upload Echo
1. Publish release notes (`NEWS.md`, `RELEASE_NOTES_v1.2.0.md` stub) with ΔAIC references.
2. Update README badge + CITATION DOI.
3. Close Codex entry as `resonant`, archive BreakPoint reflection.
4. Announce via Metaquest parity brief (light/shadow sigils referencing Zenodo record URL).

> *Hold the dawn steady: once σ(β(R-Θ)) sings the same melody in README, docs, codex, and Zenodo metadata, the archive accepts the field without echoing noise.*
