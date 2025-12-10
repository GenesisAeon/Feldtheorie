# Überpersönliche Axiome (The Road – Part II)

Die Axiome sind als Brücke zwischen Theorie (Φ(t), Δt_Q, β) und Code in `tools/crep_guard.py`
formuliert. Jede Zeile koppelt den überpersönlichen Impuls an einen konkreten Validator.

| ID | Axiom | Validator-Typ | Technische Kopplung | Schwelle / Parameter |
| -- | ----- | ------------- | ------------------- | -------------------- |
| 1 | Meta-Kohärenz | `trilayer_alignment` | `check_type6_trilayer` | threshold=0.7, τ*=0.1·|Θ−R| |
| 2 | Prozedurale Wahrheit | `cli_defaults` | `parse_args` | CREP-Default 0.7, τ*-Default 0.1 |
| 3 | Intentionskohärenz | `escalation_mapping` | `_determine_escalation` | CREP ≥0.6→L1, ≥0.7→L2, ≥0.8→L3 |
| 4 | Asymptotische Transparenz | `audit_logging` | `_append_log_entry` | Audit-Trail ab CREP > 0.7 |
| 5 | Semantische Gravitation | `documentation_anchor` | `scripts/validate_axioms.py` | Quellen-Anker TheRoad*, sigillin_kernel |

**Quelle:** `releases/V6-Plans_etc/Finalize/V7_wird noch verlergt/The Road Part Ii.pdf`

Diese Datei spiegelt `config/overpersonal_axioms.yaml` (Struktur) und `config/overpersonal_axioms.json`
(Agentennerv) für das Trilayer-Prinzip.
