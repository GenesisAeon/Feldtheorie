# Simulator Presets — Logistic Launch Pads

Diese Ablage bündelt Startkonfigurationen für das UTF-Interface. Jede Preset-Datei
hält das Schwellenquartett $(R, \Theta, \beta, \zeta(R))$, verweist auf die zugehörigen
`analysis/results/*`-Exporte und dokumentiert, welche Nullmodelle für die
Falsifikation herangezogen wurden. Narrative Tooltips beschreiben zugleich, wie
sich der Übergang anfühlt.

## Aktueller Stand
- `honeybee_membrane.json` — Bienenschwarm-Gate mit $\zeta(R)=1.25-0.35\,\sigma$;
  bindet `analysis/results/honeybee_waggle_fit.json` samt ΔAIC gegen das Potenzgesetz.
- `qpo_eruption.json` — Soft-Hair-Impedanz ($\Delta \text{AIC}>2.5\times 10^4$)
  für `analysis/reports/qpo_membrane_summary.json`.
- `llm_resonance.json` — Curriculum-Gating aus `analysis/results/llm_emergent_skill.json`
  inklusive ΔAIC=48.8.
- `cognitive_gate.json` — D1/D2-Schwellenschaltung (`analysis/results/working_memory_gate.json`).
- `amazon_canopy.json` — Regenwald-Kipppunkt (`analysis/results/amazon_resilience_fit.json`).
- `lenski_citplus.json` — Evolutionsmembran der LTEE (`analysis/results/lenski_citplus_fit.json`, ΔAIC≈42 gegen linear).

Alle Dateien führen Formal-/Empirie-/Poetik-Felder und deklarieren geschlossene vs. offene
Impedanz, damit das Frontend $\zeta(R)$ direkt modulieren kann.

## Nächste Schritte
1. Erweitere bei Bedarf weitere Domänen um denselben JSON-Kanon.
2. Synchronisiere Loader-Anpassungen im Simulator mit `codexfeedback.json`, damit
   Divergenzen früh auffallen.
3. Ergänze Tests, die Preset-IDs gegen `docs/resonance-bridge-map.md` spiegeln.
