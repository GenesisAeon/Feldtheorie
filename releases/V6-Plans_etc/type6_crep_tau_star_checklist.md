# Type-VI CREP/τ*-Checklist (FIT Microstep)

- **ID:** type6-crep-tau-checklist
- **Version:** v1.0.0
- **Scope:** releases/V6-Plans_etc
- **Generated:** 2025-11-30T09:00:00Z
- **Logistische Membran:** R→"Type-VI Governance Gate aktiv", Θ→"CREP/τ*-Safeguards in Docs und CI verankert", β≈4.6, ζ-Risiko neutralisiert, wenn Schritte erfüllt sind.
- **Kopplung:** POLICY.md · ETHICS.md · V6_ToDoListe.* (FIT-Microstep für v6-governance-ethics; Fokus CREP>0.7 + τ*-Pflicht vor Merge/Release)

## Checklist

1. **CREP-Schwelle prüfen (required)**
   - CREP-Index aus letzter Simulation/Analyse berechnen oder referenzieren.
   - Falls CREP ≥ 0.7, Reviewer-Slot blockend einplanen.
   - CREP-Wert im Provenienzblock und Audit-Trail notieren.
   - *Metriken:* threshold 0.7 · Level 2 bei CREP ≥ 0.7 · Level 3 bei CREP ≥ 0.8.

2. **τ*-Buffer verankern (required)**
   - τ* = 0.1·|Θ−R| als Default setzen; Abweichungen begründen.
   - Integrator = RK4 oder höher (kein Euler bei ζ<0) sicherstellen.
   - τ* und Integratorwahl im Commit/CI-Log dokumentieren.
   - *Metriken:* τ* Default `0.1*abs(Theta-R)` · Integrator = RK4+.

3. **Provenienz & Dual-Use protokollieren (required)**
   - Datenquellen, Vorverarbeitung und Nullmodelle im Provenienzblock aufführen.
   - ΔAIC/CI-Metriken dokumentieren und Schatten-Sigillin referenzieren.
   - Dual-Use-Check durchführen und Ergebnis vermerken.
   - *Outputs:* provenance_block · dual_use_note.

4. **CI/Pre-Commit Hook setzen (recommended)**
   - Hook entwerfen, der CREP ≥ 0.7 markiert und τ*-Default validiert.
   - Hook meldet Trilayer-Drift (YAML/JSON/MD) und leitet Reviewer für Level 2/3 weiter.
   - Reviewer-Routing (maintainers) für Level-2/3 Fälle hinterlegen.
