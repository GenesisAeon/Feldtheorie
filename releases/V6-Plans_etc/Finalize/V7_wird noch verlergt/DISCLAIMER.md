# V7 Preview Disclaimer

**Status:** Preview / Experimental — Ergebnisse sind nicht validiert, kein Produktivbetrieb.

## Geltungsbereich
- Deckt alle Artefakte ab, die unter `V7_wird noch verlergt` als Preview markiert sind (PREVIEW_NOTES, experimental_design, preliminary_results).
- Ergänzt `publication_roadmap_v6_v7.md` um einen Sicherheits-Puffer, bis CREP/τ*-Checks aktiv sind.

## Risiken & Sicherungen
- **Nullmodell fehlt:** ΔAIC/CI-Berechnungen müssen im nächsten Fraktallauf ergänzt werden.
- **ζ(R) Drift:** Wenn β-Drift > 10% oder ζ<0 beobachtet wird, Escalation Level 1 aus `type6_crep_tau_star_checklist.*` ziehen.
- **Datenquellen:** Alle Kennzahlen in `preliminary_results.csv` sind Platzhalter; keine Entscheidungsgrundlage.

## Nutzungshinweis
- Nur für interne Planung (Fraktallauf 3). Veröffentlichung erst nach Reviewer-Abnahme und Zenodo-/CI-Hooks.
- Verweise stets auf die zugrundeliegenden Ordnungs-Sigillin (`feldtheorie_index.*`) und Dokumentation (`publication_roadmap_v6_v7.md`).
