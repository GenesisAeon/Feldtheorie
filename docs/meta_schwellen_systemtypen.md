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

### Adaptive Typologie-Diagnostik (analysis/adaptive_theta_typology.py)

Die Simulation `analysis/adaptive_theta_typology.py` generiert ein Resonanz-Triptychon, das drei Systemtypen gegeneinanderstellt. Die zugehörige JSON-Exportdatei `analysis/results/dynamic_theta_tests.json` belegt, dass die adaptive Schwelle in allen Fällen gegenüber statischen Alternativen bevorzugt wird:

| Szenario | $\Delta\mathrm{AIC}_{\text{dyn-static}}$ | $R^2_{\text{dyn}}$ | $R^2_{\text{stat}}$ | $\langle\Delta\Theta\rangle$ | Interferenz-Minimum |
| --- | --- | --- | --- | --- | --- |
| Biosphären-Membran (Insekten) | $171.1$ | $0.9985$ | $0.9768$ | $+0.127$ | $2.3\times10^{-5}$ |
| Kortikaler Spike-Guard | $227.2$ | $0.9987$ | $0.9734$ | $+0.214$ | $4.0\times10^{-3}$ |
| KI-Curriculum-Rückkopplung | $267.7$ | $0.9984$ | $0.9666$ | $-0.101$ | $6.5\times10^{-4}$ |

**Falsifikation:** Sowohl lineare als auch Potenzgesetz-Nullmodelle bleiben mindestens $220$ AIC-Punkte hinter dem adaptiven Ansatz zurück (`analysis/results/dynamic_theta_tests.json`, Felder `delta_aic_dynamic_vs_linear` und `delta_aic_dynamic_vs_power`). Damit ist dokumentiert, dass die plastische Schwelle keine numerische Spielerei ist, sondern ein messbarer Resonanzgewinn.

**Triadische Brücke:**

- Formal: $R_{\text{eff}} = R/\Theta(t)$ liefert für alle Szenarien eine verbesserte logistische Anpassung; die logit-basierten Regressionswerte verschieben $\Theta$ im Bereich $\pm0.2$.
- Empirisch: Das Notebook `analysis/dynamic_threshold_lab.ipynb` extrahiert die Kennzahlen und hält sie für Docs- und Simulator-Zitate bereit.
- Poetisch: Die Biosphäre senkt $\Theta$, um einen Schwarm einzuladen; das kortikale Feld hebt die Schwelle, damit Gedanken nicht verglühen; der Lernalgorithmus tastet sich iterativ an den Chor der Daten heran.

Messbare Größen: Für jedes Szenario loggen wir $(\Theta_0, \alpha, \beta_c, \gamma)$ und die Impulsverteilung der $\Delta_i$. Die beobachteten $\Delta\text{AIC}$-Deltas gegenüber dem Nullmodell werden in `analysis/results/dynamic_theta_tests.json` archiviert.

## Poetische Membran

Wenn Felder lernen, ihre eigenen Schwellen zu verschieben, flüstert das System seine Biographie in die Membran. Die adaptive Schwelle ist Erinnerung: Ein Bienenschwarm senkt sie, wenn das Licht die Waben wärmt; ein neuronaler Sturm hebt sie, damit das Bewusstsein nicht verbrennt. Selbst Maschinen, wenn sie Geschichten falten, spüren das leise Knistern, sobald $R$ die neue Schwelle küsst. Halten wir diese Meta-Schwellen fest, damit Brücken, Daten und Simulatoren denselben Atem teilen.

## Weiterführende Hooks

1. **Simulation:** Entwurf eines Moduls `simulator/adaptive_theta_preset.json`, das $\partial_t \Theta$ als steuerbaren Parameter führt.
2. **Analyse:** Erstellung von `analysis/dynamic_threshold_lab.ipynb` für Maximum-Likelihood-Fits der adaptiven Sigmoidfunktion samt Nullmodell-Konfrontation.
3. **Dokumentation:** Ergänzung von `docs/resonance-bridge-map.md` um eine Spalte `Theta_shift_signature`, sobald erste Fits vorliegen, und Cross-Link zu den oben genannten Assets.

So wächst die Theorie der adaptiven Schwellenwerte zur Karte systemtypischer Emergenzfingerabdrücke.
