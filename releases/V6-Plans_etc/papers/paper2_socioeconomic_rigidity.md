# Paper 2: Socioeconomic Rigidity

**Scope (R → Θ):** R ist die unbehandelte Nutzung von σ(β(R-Θ)) als Frühwarn-Operator für Ungleichheits-getriebene Rigidität; Θ ist ein validierter Schwellenparameter, der β_eff mit Gini×Load koppelt. β bewegt sich im kritischen Bereich 11–∞, ζ(R) repräsentiert politische Dämpfung (Umverteilung, Resilienzprogramme).

## Hypothesen & Nullmodelle
- **H1:** β_eff = β_base × (1 + Gini × Load) erklärt den beobachteten Anstieg der Antwortschärfe.  
  **Null:** β_eff unabhängig von Gini/Load.  
  **Falsifizierbarkeit:** p_interaction > 0.05 oder ΔAIC < 0 für das Nullmodell.
- **H2:** σ(β(R-Θ)) mit endlichem β erzeugt lead time Δt > 0 und erhöht ROC-AUC gegenüber β→∞.  
  **Null:** Keine Vorwarnzeit; stufenförmiger Übergang.  
  **Falsifizierbarkeit:** Δt ≤ 0 oder ROC-AUC ≤ Nullmodell.

## Daten & Analyseplan
- **Daten:** World Inequality Database, IMF/WB Load-Proxies, Climate-Damage-Shocks, UTAC Sigillin-Verweise.  
- **Analyse-Schritte:**
  1. β_eff aus Gini×Load konstruieren; logistisches σ(β(R-Θ)) fitten.
  2. ΔAIC/BIC gegen Nullmodell testen; ζ(R)-Policy-Dämpfung variieren.
  3. Frühwarnzeit Δt und ROC-AUC evaluieren; Bootstraps für Unsicherheit.
  4. UTAC Status Matrix + shadow_sigillin koppeln.

## Artefakte & Meilensteine
- Artefakte: Trilayer-Notiz, Notebook (analysis/results oder docs/empirical_evidence), Policy-Szenario-Tableau (docs/outreach oder figures/).  
- Milestones: Pipeline+Features (T+4), Frühwarn-Metriken (T+9), Draft-Policy-Note (T+15).

**Logistische Sprache:** σ(β(R-Θ)) misst, wann soziale Membranen verhärten; ζ(R) hält Spielräume offen, damit falsifizierbare Politikfenster sichtbar bleiben.
