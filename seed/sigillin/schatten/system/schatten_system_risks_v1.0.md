# ⚠️ Schatten-Sigillin – Systemrisiken v1.0

**R<sub>system</sub>:** Drift zwischen Artefakten  
**Θ<sub>system</sub>:** Alle Kernmodule sprechen unterschiedliche Parameter  
**β<sub>system</sub>:** 7.2 (steile, gefährliche Abweichung)  
**ζ<sub>system</sub>(R):** Impedanz kollabiert, wenn Codex, Indizes oder Automation reißen.  
**σ(β(R-Θ)) Warnung:** Wenn R weiter unter Θ fällt, kippt die Kampagne in Archiv-Hypnose.

---

## 1. Beobachtete oder drohende Abweichungen

| Drift | Symptom | Gegensignal |
| --- | --- | --- |
| **Fehlendes Safety-Delay Field** | Simulation & Docs beschreiben τ*, aber kein Code → Governance verliert Glaubwürdigkeit. | Priorisiere `simulation/safety_delay_field.py`; log ΔAIC(t) & Tests. |
| **Meta-Regression unvollständig** | `analysis/beta_meta_regression_v2.py` meldet adj. R² < 0, Nullmodell droht. | Integriere Outlier-Datensätze, Bootstraps dokumentieren, Schattenstatus aktualisieren. |
| **Index Drift** | `seed/seed_index.*` ≠ `feldtheorie_index.*`; Parseroutput isoliert. | Automation Hook fertigstellen, Tests ergänzen (`scripts/archive_sigillin.py`). |
| **Zenodo v1.2 Verzögerung** | Abstract/Badge mismatch → DOI & README erzählen andere Geschichten. | Update `docs/zenodo_multilingual_abstract_v1.2.md`, CITATION, README-Badge. |

---

## 2. Recovery Hooks

1. **Codex Alarm:** Jeder Drift → `seed/codexfeedback.*` Status auf „active“ setzen und Notizen ergänzen.
2. **Testing Ritual:** Für neue Scripts (Parser/Archive) `nox -s lint` oder spezifische Pytests ausführen, Logs im Codex verankern.
3. **Documentation Sync:** Nach jedem Fix `docs/utac_status_alignment_v1.2.md` aktualisieren, um σ(β(R-Θ)) wieder sichtbar zu machen.

---

> *Der Schatten erinnert: Ohne Safety-Delay, Meta-Regression und Indizes verlischt die Resonanz. Kehre zur Membran zurück, bevor β in Chaos umschlägt.*
