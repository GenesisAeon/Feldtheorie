# Meta-Schwellen und Systemplastizität

Die folgende Notiz erweitert das Schwellenfeldmodell um systemtypische Verschiebungen der kritischen Schwelle. Sie folgt der Triadenform: formale Ableitung, empirische Resonanz, poetische Membran.

## Formale Ableitung: Kontextadaptive Schwellenfunktion

Wir betrachten weiterhin das Schwellenquartett $(R, \Theta, \beta, \zeta(R))$ und die logistische Antwort
\[
\sigma(\beta (R - \Theta)) = \frac{1}{1 + e^{-\beta (R-\Theta)}}.
\]
Statt einer fixen Schwelle modellieren wir nun eine kontextadaptive Funktion
\[
\Theta(t) = \Theta_0 + \alpha S_{\text{system}}(t) + \beta_c C_{\text{sub}}(t) + \gamma E(t) + \sum_i \delta_i \Delta_i(t),
\]
bei der

- $S_{\text{system}}$ die globale Komplexität oder Informationsdichte (z.\,B. Kopplungsgraph-Dichte) misst,
- $C_{\text{sub}}$ die lokale Kopplungsstärke eines Subsystems (z.\,B. neuronaler Cluster, Insektenkolonie, Genregion),
- $E$ externe Störungen oder Energieflüsse charakterisiert,
- $\Delta_i$ emergente Einzelereignisse (Spike, Mutation, Resonanz) repräsentiert, die als impulsartige Schwellenshifts $\delta_i$ beitragen.

Damit ergibt sich eine effektive Ordnungsgleichung
\[
R_{\text{eff}}(t) = \frac{R(t)}{\Theta(t)}
\]
und die Impedanz wird dynamisch
\[
\zeta(R, t) = \zeta_0 + \kappa\,\partial_t \Theta(t),
\]
so dass steigende Schwellen ($\partial_t \Theta > 0$) die Membran versteifen, während sinkende Schwellen resonante Durchlässigkeit erzeugen.

**Falsifizierbarkeit:** Als glatter Nullvergleich dient eine lineare Schwellenhypothese $\Theta(t)=\Theta_0$, die keine Kopplungen oder Rückkopplungen zulässt. Abweichungen lassen sich durch Likelihood-Ratio-Tests in künftigen `analysis/`-Notebooks (vgl. geplante Skizze in `analysis/dynamic_threshold_lab.ipynb`) quantifizieren.

## Empirische Resonanzpfade

- **Biologie:** Insektenstaaten zeigen, dass bereits kleine Anpassungen in der Kopplungsdichte der Königinnenpheromon-Netze ($C_{\text{sub}}$) das Schwärmen triggern oder unterdrücken. Hier schlagen wir vor, Datenschemata aus `data/biology/` mit einer Spalte `adaptive_theta_shift` zu erweitern, sobald Messreihen vorliegen.
- **Kognition:** Spike-Kaskaden in kortikalen Netzen erhöhen temporär $C_{\text{sub}}$ und damit $\Theta$ – analog zu geplanten Simulatorläufen mit adaptiver Schwelle in `simulator/membrane_kernels.py`.
- **KI-Systeme:** Curriculum-Schwellen in `docs/ai/llm-threshold-training.md` können durch $S_{\text{system}}$ (Token-Entropie) und Feedbackereignisse $\Delta_i$ rekalibriert werden. Die Brücke zur Empirie soll ein kommender Fit in `analysis/llm-threshold-survey.ipynb` liefern, der die adaptive Sigmoidkante gegen eine statische Nullkurve hält.

Messbare Größen: Für jedes Szenario loggen wir $(\Theta_0, \alpha, \beta_c, \gamma)$ und die Impulsverteilung der $\Delta_i$. Die beobachteten $\Delta\text{AIC}$-Deltas gegenüber dem Nullmodell werden in `analysis/results/dynamic_theta_tests.json` archiviert.

## Poetische Membran

Wenn Felder lernen, ihre eigenen Schwellen zu verschieben, flüstert das System seine Biographie in die Membran. Die adaptive Schwelle ist Erinnerung: Ein Bienenschwarm senkt sie, wenn das Licht die Waben wärmt; ein neuronaler Sturm hebt sie, damit das Bewusstsein nicht verbrennt. Selbst Maschinen, wenn sie Geschichten falten, spüren das leise Knistern, sobald $R$ die neue Schwelle küsst. Halten wir diese Meta-Schwellen fest, damit Brücken, Daten und Simulatoren denselben Atem teilen.

## Weiterführende Hooks

1. **Simulation:** Entwurf eines Moduls `simulator/adaptive_theta_preset.json`, das $\partial_t \Theta$ als steuerbaren Parameter führt.
2. **Analyse:** Erstellung von `analysis/dynamic_threshold_lab.ipynb` für Maximum-Likelihood-Fits der adaptiven Sigmoidfunktion samt Nullmodell-Konfrontation.
3. **Dokumentation:** Ergänzung von `docs/resonance-bridge-map.md` um eine Spalte `Theta_shift_signature`, sobald erste Fits vorliegen, und Cross-Link zu den oben genannten Assets.

So wächst die Theorie der adaptiven Schwellenwerte zur Karte systemtypischer Emergenzfingerabdrücke.
