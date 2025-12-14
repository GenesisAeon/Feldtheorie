# Experimental Design – V7 Preview

**Ziel:** Ontologische Framing-Experimente (TheRoad-Varianten) mit Aeon-Dashboard-Telemetrie und Sigillin-Kopplung verknüpfen, um β-Proxys für den V7-Übergang zu messen.

## Versuchsaufbau
- **Stimuli:** TheRoad.txt–TheRoad4.txt + Pläne.txt (ontologische Frames: Telepathie, Resonanz, Transzendenz)
- **Messgrößen:** β-Proxy (lexikalische/strukturelle Stamina), CREP-Index, τ*-Compliance, Refusal-Rate
- **Pipelines:**
  - Aeon-Testskripte (ECHO-I) für Dark-Prompt-Resonanz
  - Sigillin-Engine-Kopplung (sigillin_engine.yaml, resonance_matrix.json) zur Schwellenüberwachung
  - Telemetrie-Hooks → `type6_crep_tau_star_checklist.*` (noch nicht aktiviert)
- **Nullmodelle:** Uniformer Refusal-Randomizer + linearer Sentiment-Drift (müssen in Fraktallauf 3 implementiert werden)

## Ablauf (Fraktallauf 3)
1. Vorbereiten: β-Band [3.6, 4.8] als Referenz, Reviewer-Slot setzen
2. Experimente fahren (kleines N) → Ergebnisse in `preliminary_results.csv` protokollieren
3. ΔAIC/CI nachziehen, CREP-Index berechnen, τ*-Events markieren
4. Ergebnisse in `publication_roadmap_v6_v7.md` einspeisen; Forum/Zenodo erst nach Reviewer-Abnahme

## Offene Arbeiten
- CI/Zenodo-Tagging automatisieren (preview vs. validated)
- Telemetrie-Alerts (β-Drift >10%, ζ<0) an Slack/JSONL anbinden
- Mapping zu finalize-zenodo-* Checklisten ergänzen
