# Erratum 1 zur M9-Herleitung

**Bezug:** [`M9_HERLEITUNG.md`](M9_HERLEITUNG.md) in der eingefrorenen Fassung. Ihr SHA-256 ist in `protocol/m9_frozen_predictions.json` festgehalten.

**Anlass:** unabhängige Prüfung `D:/mandala/mandala-memory-results/astra-m8-m9-review/REVIEW.md` (Stand `e8b1f10`), Befunde R3 und R4.

Die Herleitung selbst bleibt **unverändert**, damit sie als eingefrorene Referenz nachprüfbar bleibt; die Korrekturen stehen nur hier. Betroffen sind zwei **Erklärungen**, nicht die Rechnungen:
- `predict.py`, die eingefrorenen Vorhersagen und die M9-Ergebnisse sind korrekt und unverändert.
- Beide Gegenbeispiele sind mit dem Kern und mit `predict.py` wörtlich nachgerechnet. Ihre Regressionstests stehen in [`tests/test_m9_erratum.py`](../tests/test_m9_erratum.py).

## R3: Ein Vorzeichenwechsel braucht μ_D < 0, nicht λ_D < 0

**Ursprünglich (Abschnitt 3, S2):**
> Ab c > (N−n)/N wird λ_D negativ (anti-modular), und die Spur wechselt das Vorzeichen.

**Richtig:**
- Ab c > (N−n)/N ist der **Kopplungseigenwert** λ_D negativ. Die Kopplung wirkt dann dem Modul-Unterschied entgegen (anti-modular) und drückt μ_D unter 1 − ℓ.
- Der **Zeitschrittfaktor** ist μ_D = 1 − ℓ + ℓλ_D. Wegen des Trägheitsanteils 1 − ℓ bleibt er oft positiv.
- Im linearen Modus wechselt die Spur ihr Vorzeichen von Schritt zu Schritt **genau dann, wenn μ_D < 0**, also λ_D < −(1−ℓ)/ℓ.

**Gegenbeispiel (Astra):** N = 12, M = 3, c = 0,8, γ = 0,8, ℓ = 0,5, a = 0,6, Eingänge 0/4.
- Es gilt λ_D = −0,16, aber μ_D = +0,42.
- Der Modulkontrast (Mittel M1 − Mittel M2 von x_A − x_B) bleibt positiv: 0,1342624; 0,0563928; 0,0236859; 0,0099484; 0,0041785.
- Unser Kern ergibt exakt dieselben Werte.

**Positivkontrolle:** N = 12, M = 3, c = 1, γ = 0,95, ℓ = 1. Dann ist μ_D = λ_D = −0,475, und der Kontrast wechselt bei jedem Schritt das Vorzeichen.

## R4: Unter der Schwelle bei d = 0 heißt nicht „keine Erinnerung“

**Ursprünglich (Abschnitt 4, Sonderfälle):**
> „keine“: schon Bayes(0) < p\*.

**Richtig:**
- **D ist „keine“ genau dann, wenn bei keiner geprüften Pause d = 0…64 die Schwelle erreicht wird.** Die Definition D = max{d : Bayes(d) ≥ p\*} war schon richtig, und so ist sie auch implementiert. Falsch war nur die Erläuterung des Sonderfalls.
- Bei einem **einzelnen Ableseknoten** kann die Information erst später ankommen: Sie breitet sich über die Kopplung aus.
- Die **Ersterreichungs-Variante** (first_passage = erste Pause unter p\* minus 1) ist eine eigene Größe. Bei Bayes(0) < p\* ist sie undefiniert („None“) und sagt dann über spätere Pausen nichts aus.

**Gegenbeispiel (Astra):** N = 12, M = 3, c = 0,25, γ = 0,8, ℓ = 0,5, a = 0,6, σ = 0,01, Eingänge 0/4, Ableseknoten 1.
- Die ideale Trefferquote verläuft 0,5 → 0,879704 → 0,911444 → … und ergibt D = 5, obwohl Bayes(0) < 0,75.
- Unser Kern ergibt D = 5 (first_passage = None, nicht monoton); `predict.py` sagt D ∈ [5, 5] voraus.

**Folge für die M9-Prüfung:** keine. Alle 10 Prüfkombinationen mit vorhergesagtem „–“ bleiben im Kern bei **allen** d = 0…64 unter p\*; die Auswertung prüft D über die ganze Kurve. In der Roadmap war „–“ als „schon bei d = 0 unter p\*“ erklärt; das ist dort berichtigt.

## Weitere Präzisierungen aus derselben Prüfung

1. **Schranke und Gleitkomma:**
   - Die Fehlerschranke E(d) ist ein analytisches Argument.
   - Ihre Auswertung in Gleitkomma mit Sicherheitszuschlägen (1e‑9 relativ, 1e‑18 absolut, Vergleichstoleranz 1e‑12) ist **keine zertifizierte Intervallarithmetik**.
   - Es wurde kein Bandverstoß gefunden. Eine rechnerische Zertifizierung ist damit nicht gezeigt.
2. **Decoder-Band:**
   - Die 28 bestandenen Decoder-Prüfungen bestätigen das vorab festgelegte Toleranzkriterium (Zuschlag 0,01 plus 4 SE je Prüfung).
   - Sie liefern **kein** kalibriertes gemeinsames Konfidenzniveau über alle Prüfungen.
3. **„Modul von B löschen verlängert die Erinnerung“ (M8):**
   - Nach dem Löschen wird A gegen ein Nullsignal unterschieden, und der Unterschied enthält den langsamen Gleichtakt-Anteil.
   - Die längere ideale Unterscheidbarkeit heißt **nicht**, dass der gelöschte B-Zustand wiederhergestellt wird. Die Aufgabe hat sich verändert.
4. **Reihenfolge:** Die Commit-Folge belegt die **versionierte** Reihenfolge (Herleitung → Register → Einfrieren `359a4cf` → Auswertung). Dass es keinerlei unversionierte Vorabrechnungen gab, belegt sie nicht. Die einzige bekannte Vorabrechnung ist der Scan vor M8; er ist im Register erfasst.
