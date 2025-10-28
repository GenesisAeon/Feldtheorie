# Bio-Emergenz Kapitel — Semantisch-biophysikalischer Phasenübergang

## Formale Resonanz
- **Quartett:** Wir kalibrieren das biologische Schwellenfeld mit \(R = \rho_{\text{Komplex}}/\mathcal{S}\), dem Verhältnis aus genomischer Komplexitätsdichte und entropischer Aktivität des epigenetischen Feldes. Der Cit⁺-Sprung im Lenski-LTEE liefert \(\Theta_{\text{Bio}} = 32.77^{+0.08}_{-0.08}\) (in Tausend Generationen) und eine normalisierte Steilheit \(\beta_{\text{Bio}} = 4.25^{+0.35}_{-0.35}\), womit sich die Antwort \(\sigma(\beta(R-\Theta))\) in das universelle Band \(\beta \approx 4.1 \pm 0.9\) einfügt.
- **Lagrange-Ergänzung:** Das gekoppelte Feld \((\phi, \psi)\) erweitert den UTF-Lagrangian um \(\mathcal{L}_{\text{bio}} = \frac{1}{2}(\partial_t \psi)^2 - V(\psi) - \zeta(R)(\psi-\sigma)^2 + \lambda_{\phi\psi}\phi\psi\). Überschreitet \(R\) die Schwelle, rotiert \(\psi\) in einen neuen Minima-Ast — Mutation oder Gensprung erscheinen als first-order-Übergang des kombinierten Feldes.
- **Nullkontrast:** Gegenüber einem glatten linearen Modell (\(\Delta\mathrm{AIC} = 42.1\)) und einer Potenzantwort (\(\Delta\mathrm{AIC} = 32.7\)) behauptet der logistische Fit die Resonanz. Damit bleibt die Bio-These falsifizierbar: fällt \(\Delta\mathrm{AIC}\) unter 10, ist das Kapitel zu revidieren.

## Empirische Resonanz
- **Analysepfad:** `analysis/lenski_citplus_fit.py` rekonstruiert die Cit⁺-Kurve und speichert alle Kennzahlen in `analysis/results/lenski_citplus_fit.json`. Die Skala \(R = \text{Generation}/1000\) verankert \(\Theta_{\text{Bio}}\) bei 32.77; \(\beta_{\text{Bio}}\) normalisiert sich mit der empirischen Streuung der Generationen.
- **Datenquellen:** `data/biology/lenski_citplus.csv` (plus Metadaten) bildet die Ara-3-Trajektorie aus Blount et al. (2008). Für die Feldspannungsmetrik \(\rho_{\text{Komplex}}\) referenzieren wir regulatorische Vernetzungskarten aus `Docs/Einleitung_ Motivation und Universalitätsidee.pdf`, Abschnitt "Biologische Schwellen".
- **Brückung:** `docs/resonance-bridge-map.md` führt die Bio-Emergenz nun als eigenen Knoten; Simulator-Presets erhalten \(\Theta_{\text{Bio}}\) und \(\beta_{\text{Bio}}\) als Startwerte für adaptive Evolutionsläufe.

## Falsifikationspfad
- **Replikation:** Wiederhole `python analysis/lenski_citplus_fit.py --data data/biology/lenski_citplus.csv --export analysis/results/lenski_citplus_fit.json` nach jeder Datenergänzung. Speichere \(R^2\), \(\Delta\mathrm{AIC}\) und Konfidenzintervalle in `analysis/results/`.
- **Null-Modelle:** Behalte lineare und Potenz-Nulle aktiv. Ein zusätzlicher Vergleich gegen ein exponentielles Wachstum wird für künftige Stressdaten empfohlen; erst wenn auch dort \(\Delta\mathrm{AIC} > 10\) bleibt, gilt der Übergang als gesichert.
- **Cohort Sync:** Melde neue Runs an `analysis/resonance_cohort_summary.py`, damit die Median-\(\beta\) im universellen Band verbleibt.

## Metaphorische Dawn-Chorus
- Dreißigtausend Generationen lang summte das Genom als stiller Chor, \(\zeta(R)\) gespannt wie ein Bogen. Erst als Umweltstress und Komplexität im Verhältnis \(R\) den Torbogen \(\Theta_{\text{Bio}}\) küssten, sprang ein neues Lied an — Cit⁺ leuchtete wie ein frisch erwachter Stern im mikrobiellen Firmament.
- Die Nullmodelle boten sanfte Brisen, doch nur die logistische Woge traf den Resonanzkamm. Evolution erscheint nicht mehr als blindes Würfeln, sondern als Membran, die auf den richtigen Druck antwortet.

## RepoPlan 2.0 Anschluss
- Verknüpft die neue PDF-Rolle "Biologische Evolution als Phasenübergang" mit laufenden Simulator-Konzepten (RepoPlan-Knoten RP2-Bio-1).
- Dokumentiert im `codexfeedback`-Ledger (Eintrag `pr-draft-0016`) die Wachsamkeit gegenüber \(\Delta\mathrm{AIC}\)-Drift und fordert Epigenetik-Datensätze für die nächste Iteration an.
