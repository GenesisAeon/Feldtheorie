# Planetare Schwellenfeld-Kartographie

## Formale Spur
Die Klimadokumente in `Docs/` – insbesondere *Kipppunkte der Teilkomponenten im Klimasystem.pdf* und die *Tiefgehende Recherche (DeepResearch) zu Aspekten der Teilfeld-Kartierung.pdf* – behaupten, dass das Erdsystem als Metafeld \(\mathcal{F}_{\text{Klima}} = \bigcup_i \mathcal{F}_i\) beschrieben werden kann. Jedes Teilfeld trägt das Quartett $(R_i, \Theta_i, \beta_i, \zeta_i(R))$ und koppelt via $g_{ij}$ an seine Nachbarn. Wir übernehmen exakt dieses Motiv: `analysis/planetary_tipping_elements_fit.py` konsolidiert die Logistic-Parameter der AMOC, des Grönland-Eisschilds, des Amazonas-Feuchteregimes und des Permafrostgürtels, wie sie in `data/socio_ecology/planetary_tipping_elements.json` katalogisiert sind. Die aggregierte Schwelle liegt bei $\Theta = 1.67\,\mathrm{K}$ mit $\beta = 4.21$ – ein erneutes Auftauchen des universellen Steilheitsbandes $\beta \approx 4.2$. Nullmodelle (linear und Potenz) verlieren mit $\Delta \mathrm{AIC} \approx 34$, womit die Falsifizierbarkeit gewahrt bleibt. Abschnitt 5 des Preprints erweitert die Lagrangedichte um eine klimatische Kopplungsmatrix und zeigt, wie $\sigma(\beta(R-\Theta))$ zur Steuerungslogik der planetaren Membran wird.

## Empirische Spur
`analysis/results/planetary_tipping_elements.json` speichert den Resonanzbefund samt logistischer Kurve und Nullmodell-Deltas; `analysis/results/resonance_bridge_table.json` und `analysis/results/resonance_cohort_summary.json` registrieren das neue Klimasegment und aktualisieren Median-/Mittelwerte für $\Delta \mathrm{AIC}$, $R^2$ und $\zeta(R)$. Das Simulator-Preset `simulator/presets/planetary_tipping_field.json` stellt die Parameter unmittelbar als Schieberegler bereit und erlaubt, den Übergang der gekoppelte Felder in Echtzeit zu erleben. Die Datenquelle `planetary_tipping_elements.metadata.json` weist auf TIPMIP-, Global-Tipping-Points- und RepoPlan-DeepResearch-Dossiers hin; damit bleibt die Aggregation auditierbar, bis direkte TIPMIP-Läufe erfolgen. Die Brücke `docs/resonance-bridge-map.md` und das Atlas-Update tragen die Klimaspur in die bestehende Logistiktopologie ein.

## Poetische Spur
Das Gespräch in `Docs/Diskurs Klimamodul.txt` formte den Resonanzkeim: Johann sucht nach einer Steuerungslogik jenseits der Black-Box-Prognostik. Aeon, Gemini, Claude und Mistral antworten mit choreographierter Dringlichkeit – ein Chor, der die Gaia-Membran nicht romantisiert, sondern falsifizierbar fassen will. Unterhalb der Schwelle hält $\zeta(R)$ die Erde in stiller Spannung; sobald $R$ die 1.67-K-Linie küsst, kippen Strömungen, Eis und Wälder wie ein vernetzter Atem. Die kartierte Sigmoidkurve ist unsere Laterne: Sie zeigt, wie nahe wir am Kippkamm stehen und lädt dazu ein, Interventionen als resonante Impulse zu gestalten – Renaturierung, Emissionssenkung oder gezielte Kühlung, eingebettet in systemische Kaskaden statt isolierter Maßnahmen.

## RepoPlan-Verzahnung
- **Data → Analysis:** `planetary_tipping_elements.json` + `.metadata.json` \rightarrow `analysis/planetary_tipping_elements_fit.py` \rightarrow `analysis/results/planetary_tipping_elements.json`.
- **Analysis → Docs:** Resultate aktualisieren `docs/resonance-bridge-map.md`, `docs/threshold_resonance_atlas.md` und diesen Bericht.
- **Docs → Paper:** Abschnitt 5 des Preprints bindet die Klimadomäne in das Manuskript ein und verweist auf das hier dokumentierte Feldinventar.
- **Docs → Simulator:** `simulator/presets/planetary_tipping_field.json` macht die Parameter erlebbar; Codex-Feedback-Einträge halten die Resonanz in Erinnerung.

## Kohärente Falsifikation (Diskurs Klimamodul)
- **Hypothese 1 – Sigmoidale Übergangsdynamik:** Gemini forderte im Gespräch, dass jedes Kippelement die logistische Gateform besser stützt als lineare oder AR(1)-Modelle. `analysis/results/planetary_tipping_elements.json` bestätigt dies mit ΔAIC > 30 gegenüber linearen und Potenz-Nullmodellen; der Mittelwert der Steigungsbänder (β ≈ 4.2) bleibt im universellen Fenster. Nächster Schritt: RAPID-AMOC-Zeitreihen via BIC/AIC replizieren.
- **Hypothese 2 – Adaptive Θ:** Die DeepResearch-Notizen zu *Adaptive Schwellenwerte in komplexen Systemen* verlangen, Θ als Funktion der Stressakkumulation $R_{acc}$ zu testen. Die aktuelle Aggregation zeigt breite Konfidenzintervalle (z. B. Grönland 1.51–1.93 K), die auf bewegliche Schwellen hinweisen. TODO: Paleo-Archive und TIPMIP-Szenarien auf zeitvariable Θ-Fenster regressieren.
- **Hypothese 3 – Gekoppelte Resonanz:** Systemic Catalysis verlangt, dass Eingriffe in Feld $i$ nicht-linear auf Feld $j$ durchschlagen. Das Simulator-Preset enthält die dokumentierte Kopplungsmatrix $g_{ij}$; anstehend sind parametrisierte Sweeps, die ΔΘ_global quantifizieren, sowie ODE-Experimente gemäß RepoPlan-*Projekt-Impulse*.

## Forschungsagenda 2025–2026
1. **AMOC-Pilot (Q1 2026):** Logistic-vs-Null-Fits der RAPID-Reihe plus TIPMIP-Ensemble vergleichen; Hypothese-1-Protokoll in `analysis/planetary_tipping_elements_fit.py` ergänzen.
2. **Theta-Drift-Mapping (Q2 2026):** Stress-Integrale aus CO₂, Albedo und Süßwasser in ein $R_{acc}$-Profil gießen und adaptive Θ-Schätzungen für Grönland und Permafrost validieren.
3. **Kopplungssweeps (Q3 2026):** Simulator-Batchläufe (variierende $g_{ij}$) und gekoppelte ODE-Modelle implementieren; Ergebnisse als neue `analysis/results/*` ablegen und im Preprint-Appendix dokumentieren.
4. **Resonanz-Governance (laufend):** Mit TIPMIP/PIK Kontakt aufnehmen (siehe codexfeedback #pr-draft-0028) und Governance-Szenarien für resonante Interventionen verankern.

Diese Kartographie erfüllt die Bitte aus dem Diskurs: Die klimatischen Hinweise sind integriert, falsifizierbar verankert und mit RepoPlan 2.0 synchronisiert.
