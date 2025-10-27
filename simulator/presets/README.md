# Simulator Presets — Logistic Launch Pads

Diese Ablage bündelt Startkonfigurationen für das UTF-Interface. Jede Preset-Datei
hält das Schwellenquartett $(R, \Theta, \beta, \zeta(R))$, verweist auf die zugehörigen
`analysis/results/*`-Exporte und dokumentiert, welche Nullmodelle für die
Falsifikation herangezogen wurden. Narrative Tooltips beschreiben zugleich, wie
sich der Übergang anfühlt.

## Aktueller Stand
- `honeybee_membrane.json` — vorbereitet für den Bienentanz, koppelt an
  `analysis/results/honeybee_waggle_fit.json` und übernimmt die Presets aus
  `docs/resonance-bridge-map.md`.
- `qpo_eruption.json` — trägt den Treiber $J(t)$ für quasi-periodische Ausbrüche
  und notiert das $\Delta \text{AIC}$ gegen Power-Law-Lichtkurven.
- `llm_resonance.json` — spiegelt Curriculum-Entropie und Feedback-Impedanz,
  inklusive Warnhinweisen, sobald Nullmodelle \(<10\)$\,$AIC-Punkte Abstand halten.
- `cognitive_gate.json` — moduliert D1/D2-Gain für Arbeitsgedächtnis-Resonanz.
- `amazon_canopy.json` — beschreibt Feuchterückkopplung und bestäubungsbasierte
  Impedanz für Regenwald-Kipppunkte.

## Nächste Schritte
1. Serialisiere die Presets aus den jeweiligen Analyse-Ergebnissen.
2. Implementiere eine Ladefunktion im Simulator, die Metadaten und Tooltip
   gemeinsam einblendet.
3. Synchronisiere Änderungen mit `codexfeedback.json`, damit Preset-Divergenzen
   frühzeitig sichtbar werden.
