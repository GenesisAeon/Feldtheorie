# Bio-Emergenz Verifikation: Cit⁺-Schwelle im Lenski-LTEE

## Formale Resonanz
- **Quartett:** Aus `analysis/lenski_citplus_fit.py` ergibt sich \(\Theta = 32.77^{+0.08}_{-0.08}\) in Tausend Generationen (\(3.28\times10^4\) Generationen), \(\beta = 5.08^{+0.42}_{-0.42}\) im skalierten Raum bzw. \(\beta = 4.25^{+0.35}_{-0.35}\) als normalisierte Steilheit. Die Antwort folgt \(\sigma(\beta(R-\Theta))\) mit \(R\) als Generation/1000.
- **Fit-Güte:** Logistiche Regression liefert \(R^2 = 0.990\), AIC = \(-85.87\). Lineare und Potenz-Nulle weichen um \(\Delta\mathrm{AIC} = 42.1\) bzw. \(32.7\) und \(\Delta R^2 = 0.196\) bzw. \(0.095\) zurück.
- **Universalitätsprüfung:** Die normalisierte Steilheit \(\beta=4.25\) liegt innerhalb des universal postulierten Bandes (\(\beta\approx4.1\pm0.9\)), womit das Kapitel "Einleitung: Motivation und Universalitätsidee" eine empirische Stütze erhält.

## Empirische Spur
- **Datengrundlage:** `data/biology/lenski_citplus.csv` digitalisiert den Cit⁺-Anteil der Ara-3-LTEE-Population nach Blount et al. (2008, Nature 455). Das Begleit-Metadatum `lenski_citplus.metadata.json` dokumentiert Skalierung, Quartett und Falsifikationsmargen.
- **Reproduzierbarkeit:** Die CLI `analysis/lenski_citplus_fit.py --data data/biology/lenski_citplus.csv` erzeugt `analysis/results/lenski_citplus_fit.json`, das alle Kennzahlen für Docs/ und Simulatoren bereitstellt.
- **Falsifikation:** Beide glatten Nullmodelle scheitern (positives \(\Delta\mathrm{AIC}\), \(\Delta R^2\ge0\)), womit die Schwellenbehauptung die Repository-Mandate erfüllt.

## Metaphorische Dawn-Chorus
- Dreißigtausend Generationen lang blieb das mikrobielle Feld still – \(\zeta(R)\) dicht gespannt. Erst als \(R\) den Schwellenkamm \(\Theta\) erreichte, schlug die Cit⁺-Membran auf und die Population leuchtete wie eine aurorale Mutation.
- Die lineare Brise und der Potenzhauch versuchten, den Gesang zu imitieren, doch nur die logistiche Kaskade konnte den punktierten Gleichgewichtssprung der Bio-Emergenz erfassen.

## Bedeutung für das Bio-Emergenz-Kapitel
- Der verifizierte \(\beta\)-Wert liefert eine quantitative Brücke zur These, dass Evolution als semantisch-biophysikalischer Phasenübergang fungiert.
- Die Kombination aus datengetreuer Schwellenbestimmung und expliziter Nullfalsifikation stärkt die narrativen Bögen der neuen Docs/-PDFs und bietet Kennzahlen für weitere Modelle (`models/` und `simulator/`).
