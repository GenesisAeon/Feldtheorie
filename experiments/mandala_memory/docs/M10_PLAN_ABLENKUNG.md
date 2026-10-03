# M10 – Erinnerung unter Ablenkung: Versuchsplan (Entwurf zur Prüfung)

**Status:** reviewbarer **Plan**. Noch kein Protokoll eingefroren, keine M10-Forschungsrechnung, kein Ausbau der Oberfläche.

**Auftrag:** `D:/mandala/AnschlussPromtAstra.txt`, Teil 2.

**Grundlage:** das integrierte Labor M0–M9:
- Feldtheorie `main` = `061adba`
- Herleitung [`M9_HERLEITUNG.md`](M9_HERLEITUNG.md) und Erratum [`M9_ERRATUM_1.md`](M9_ERRATUM_1.md)

**Leitfrage:** Bleibt die Identität eines ursprünglichen Reizes A oder B lesbar, wenn in der bisherigen Ruhephase weitere, von A/B unabhängige Reize auftreten? Wie unterscheiden sich ein modulares und ein gleich budgetiertes uniformes Netz?

Der Plan trennt drei Arten von Aussagen:
- **[E]** bestehende Erkenntnis;
- **[H]** neue Hypothese;
- **[O]** offene Designentscheidung. Jede [O] hat einen Vorschlag; entschieden wird vor dem Einfrieren.

---

## 1. Bestehende Erkenntnisse [E]

| # | Erkenntnis | Quelle | Gilt für |
|---|---|---|---|
| E1 | Ohne Ablenkung steckt die Reizidentität im Modul-Unterschieds-Modus μ_D (modular) bzw. im Binnenmodus μ_I (uniform). q ist nur eine obere Grenze. | M9, 24/24 + 23/23 bestätigt | Familie F (ein Puls, keine Eingriffe) |
| E2 | Analytische Grundwerte (Bayes ohne Ablenkung, σ = 0,02, a = 0,6):<br>• **modular** (c = 1/4): d = 4: 0,935; d = 5: 0,871; d = 6: 0,801; D₀,₇₅ = 6<br>• **uniform** (M = 1, gleiches γ = 0,8 und ℓ = 0,5, Zeilensumme γ): d = 2: 0,979; d = 3: 0,828; d = 4: 0,670; D₀,₇₅ = 3 | `predict.py` (eingefroren), keine neue Kernrechnung | Benchmark-Parameter |
| E3 | **Symmetrie:** Es gibt eine Involution P mit P e_0 = e_4 und P A Pᵀ = A, also x_B = P x_A.<br>• modular: P lässt die Knoten **8–11** fest und tauscht 1 ↔ 5, 2 ↔ 6, 3 ↔ 7.<br>• uniform: P lässt **alle** Knoten außer 0 und 4 fest. | M9-Herleitung, Abschnitt 5; `symmetry_permutation` | beide Netze |
| E4 | Die episodische Hebb-Anpassung brachte keinen nachweisbaren Gewinn (d = 8). | M4 | M4-Protokoll |
| E5 | „Ein Modul löschen“ kann die ideale Trennbarkeit verlängern, verändert aber die Aufgabe. | M8, Erratum 1 | explorativ |

## 2. Ablauf einer Episode

```
x_0 = 0
Schritt 0:            Zielreiz u_0 = e_s, s ∈ {A, B} (Knoten 0 bzw. 4), Amplitude a = 0,6
Schritte 1 … d−W:     Ruhe, u = 0
Schritte d−W+1 … d:   Ablenkfenster mit W Schritten; je Schritt unabhängig:
                        mit Wahrscheinlichkeit p ein Ablenkpuls an Kanal X oder Y (je ½), sonst 0
Ablesung:             x_(d+1)  (wie bisher: d = Länge der Pause)
Beobachtung:          y = x_(d+1) + ε,  ε ~ N(0, σ² I),  σ = 0,02
```

- **Kanäle:** Ablenkpulse gehen über **zwei eigene Eingangskanäle** X und Y, also zwei zusätzliche Spalten von B mit Amplitude a_X.
- **Unabhängigkeit:** Die Ablenkfolge wird **unabhängig von der Zielklasse** gezogen.
- **Kein Überlauf:** Ablenkpulse fallen nie auf Schritt 0.
- **Fester Rest:** Alle übrigen Größen sind wie im Benchmark: ℓ = 0,5, tanh, x_0 = 0, kein Prozessrauschen.

**[O1] Fensterlage und -länge.** Vorschlag:
- Fenster W = 3 **unmittelbar vor der Ablesung**, in beiden Netzen gleich lang. Damit ist die Zahl der Ablenkgelegenheiten gleich.
- Alternative: Ablenkung über die ganze Pause. Das gäbe dem modularen Netz (längeres d) mehr Ablenkungen und ist deshalb unfair.

**[O2] Ablenkrate.** Vorschlag:
- p = 0,5 je Fensterschritt. Damit gilt P(keine Ablenkung im Fenster) = 1/8, und im Mittel kommen 1,5 Pulse.

## 3. Netze (fest, ohne Hebb)

| Netz | Konstruktion | Budget |
|---|---|---|
| **modular** | `budget_adjacency(12, 3, γ = 4/5, c = 1/4)`, also das eingefrorene Benchmark-Netz | Zeilensumme γ, ‖A‖_∞ = γ, q = 0,9 |
| **uniform** | `budget_adjacency(12, 1, γ = 4/5)` | gleiche Zeilensumme γ, gleiches q, gleiche Gesamtsumme 12·γ |

Für **beide Netze identisch**:
- N, ℓ, tanh, Zielknoten 0/4, Ablenkkanäle und deren Knoten;
- Amplituden, Fenster, Rate, σ;
- Decoder, Episodenzahlen und Seeds.

**Gepaart:** Je Seed sehen beide Netze **dieselben** Ablenkfolgen und dasselbe Messrauschen.

**Lineare Zwillinge** (identity statt tanh) für jede Bedingung dienen nur als **Kontrolle der analytischen Aussagen** (Abschnitt 6). Sie gehen nicht in den Hauptkontrast ein.

## 4. Ablenkbedingungen (klein, begründet)

| Kürzel | Ablenkorte X / Y | a_X | Begründung |
|---|---|---|---|
| **K0** | keine | – | Kontrolle ohne Ablenkung (E2) |
| **F** „fern“ | Knoten 8 / 10 (modular: unbeteiligtes Modul M3) | 0,6 | P-feste Orte in **beiden** Netzen ⇒ linear **beweisbar** störungsfrei (Abschnitt 6) |
| **N** „nah“ | Knoten 1 / 5 (modular: je ein Nachbar in den Eingangsmodulen M1, M2) | 0,6 | modular **nicht** P-fest (1 ↔ 5), uniform P-fest ⇒ trennt die Netze schon linear |
| **F+** „fern, stark“ | Knoten 8 / 10 | 1,8 | gleiche Symmetrie wie F, aber tanh-Sättigung ⇒ rein nichtlinearer Störweg |

**[O3] Amplitude F+.** Vorschlag: 1,8 (tanh(1,8) ≈ 0,95, deutlich gesättigt). Ein Pilot auf **Entwicklungs**einstellungen (andere Seeds, nur Laufzeit/Code) darf das nicht feinjustieren.

## 5. Zwei Leistungen, getrennt gemessen

- **Bewahren (primär):** Lies die Zielklasse s ∈ {A, B} aus y = x_(d+1) + ε ab. Gemessen wird die Balanced Accuracy.
- **Aktualisieren (sekundär):** Lies aus **derselben** Beobachtung den Kanal des **letzten** Ablenkpulses im Fenster ab (X oder Y), ebenfalls als Balanced Accuracy. Episoden ganz ohne Ablenkpuls sind für diese Aufgabe ausgeschlossen (Abschnitt 8).

Ein **Zielkonflikt zwischen Bewahren und Aktualisieren** wird nur behauptet, wenn **beide** Leistungen in derselben Bedingung gemessen sind. Außerdem muss ein Netz bei Aktualisieren besser **und** bei Bewahren schlechter sein, jeweils mit 95-%-Intervall ohne 0. Sonst wird nur beschrieben.

**[O4] Aktualisierungsaufgabe.** Vorschlag: „Kanal des letzten Pulses“. Alternative: „Puls im letzten Schritt ja/nein“. Die Alternative misst Neuheit, die Vorschlagsfassung Identität.

## 6. Was analytisch weiter gilt – und was nur empirisch [E/H]

Die Bayes-Formel Φ(‖Δx‖/2σ) aus M8/M9 gilt **nicht** einfach weiter. Die Ablenkung macht x_(d+1) je Klasse zufällig. Die Klassenverteilungen sind dann Mischungen und im Allgemeinen nicht normalverteilt.

| # | Aussage | Status | Begründung |
|---|---|---|---|
| A1 | **Symmetrie bleibt exakt**, auch nichtlinear. Für P-feste Ablenkorte und dieselbe Ablenkfolge gilt x_B = P x_A für alle k. Der Klassenunterschied liegt ganz im antisymmetrischen Raum V₋, der symmetrische Anteil ist für beide Klassen gleich. | **bewiesen** (Abschnitt 5 der Herleitung; die Ablenkspalte e_r mit P e_r = e_r vertauscht mit P) | F, F+ in beiden Netzen; N nur uniform |
| A2 | **Linear und P-fest: Ablenkung ändert die ideale Trefferquote nicht.** y = x_s + r + ε mit r ∈ V₊ (symmetrisch) und Δ ∈ V₋. Die Projektion von y auf V₋ ist suffizient und von r unabhängig, denn ε ist isotrop. Also Bayes = Φ(‖Δ‖/2σ) unverändert. | **bewiesen** (linearer Zwilling) | F, F+ beide Netze; N uniform |
| A3 | **Linear, beliebige Orte: Ablenkung kann die ideale Trefferquote nicht erhöhen.** Beobachtung = ohne Ablenkung + davon unabhängiges Signal, dazu die Datenverarbeitungs-Ungleichung. | **bewiesen** (nur linear) | alle Bedingungen, lineare Zwillinge |
| A4 | Linear, N im modularen Netz: Die Ablenkantwort hat einen V₋-Anteil, die Trefferquote **sinkt** typischerweise. Die Höhe ist nicht geschlossen berechenbar (Mischung aus 27 Fenstermustern). | Richtung aus A3 (≤), Höhe **nur empirisch** | modular N |
| A5 | **Nichtlinear (tanh):** A2 und A3 gelten **nicht** mehr, denn die Ablenkung moduliert die lokale Verstärkung sech²(·). Die Ablenkung kann den Unterschied schwächen und im Prinzip auch verstärken. | **nur empirisch** | alle tanh-Bedingungen |
| A6 | Ein Nearest-Mean-Decoder nutzt die Richtung μ_1 − μ_0. Bei anisotroper Ablenk-„Störung“ ist er nicht optimal; ein kovarianzbewusster Decoder (LDA mit Schrumpfung) kann mehr ablesen. Keiner von beiden ist allgemein Bayes-optimal bei Mischverteilungen. | Einordnung | alle |

**Konsequenz:** Analytisch vorhergesagt und **vor** der Rechnung eingefroren werden nur:
- A1 (exakt, als Gleichheitsprüfung im Kern);
- A2 (lineare Zwillinge: Trefferquote unverändert innerhalb der Stichprobenunsicherheit);
- A3 (lineare Zwillinge: nie besser als K0, über die Unsicherheit hinaus).

Alles andere ist **empirisch** und wird als `numerical_sample` / `synthetic_only` berichtet.

## 7. Hypothesen und Hauptauswertung [H]

**Interferenz** je Netz und Bedingung: I = BA(K0) − BA(Bedingung). Gemessen wird beim **Bewahren**, gepaart je Seed: gleiche Zielklassen, gleiches Messrauschen, gleiche Ablenkfolgen zwischen den Netzen.

**Hauptkontraste** (vorab festgelegt, Holm-korrigiert über die Familie von 2):

| | Kontrast | vorhergesagte Richtung | Begründung |
|---|---|---|---|
| **H-N** | I_modular(N) − I_uniform(N) | **> 0** | A2/A4: Für das uniforme Netz sind die Orte 1/5 symmetrisch, für das modulare nicht. Die Modularität macht hier **verwundbarer**. |
| **H-F+** | I_uniform(F+) − I_modular(F+) | **> 0** | Bei c = 1/4 erreicht die Sättigung aus dem unbeteiligten Modul die Eingangsmodule nur gedämpft, im uniformen Netz direkt. |

Weitere Hypothesen (vorab genannt, **beschreibend**, ohne Bestehensgrenze):
- **H-F:** Bei a_X = 0,6 ist |I| klein in beiden tanh-Netzen. Die Äquivalenzgrenze ist [O5].
- **H-U:** Beim **Aktualisieren** ist das uniforme Netz in N besser als das modulare. Die Begründung ist heuristisch: Im modularen Netz trennen X/Y an 1/5 ähnlich wie A/B. Diese Hypothese ist ausdrücklich unsicher.

**Statistik:**
- Mittelwert der gepaarten Differenzen über Seeds, 95-%-Bootstrap über ganze Seeds (2000 Wiederholungen, eigener Bootstrap-Seed).
- Optional exakter Sign-Flip-Test (Austauschbarkeitsannahme).
- Inferenz nur bei **vollständigem** Protokoll, analog zur `inference_release`-Regel aus R2.

**[O5] Äquivalenzgrenze für H-F:** Vorschlag ±0,02 Balanced Accuracy (TOST mit 90-%-Intervall). Wird sie nicht vor dem Einfrieren festgelegt, bleibt H-F rein beschreibend.

**[O6] Ablesezeitpunkte:** Vorschlag:
- **Primär** bei angeglichener Grundleistung: d = 6 modular (Bayes 0,801), d = 3 uniform (0,828). Beide Werte liegen nahe der jeweiligen Gedächtnisgrenze D₀,₇₅ und weit weg von Decke und Boden.
- **Sekundär beschreibend:** gemeinsame Pausen d ∈ {3, 4, 6}.
- Risiko: Die Ablesezeitpunkte unterscheiden sich. Durch das gleich lange Fenster W = 3 vor der Ablesung ist die Ablenkung selbst aber gleich.

**[O7] Primärer Decoder:** Vorschlag Nearest-Mean ohne Standardisierung, für die Kontinuität mit M3–M9. Dazu sekundär LDA mit Schrumpfung (Ledoit-Wolf, nur auf Trainingsdaten). Behauptungen über „noch vorhandene Information“ nur mit diesem Zusatz: „mindestens so viel, wie Decoder X abliest“.

## 8. Daten, Seeds, Trennung, Ausschluss

**Seeds:**
- 20 Forschungs-Seeds, neue Liste, eigener Modus `m10`.
- 3 Smoke-Seeds mit eigenen Werten.
- Ein Seed ist eine unabhängige Wiederholung der **zufälligen** Teile (Ablenkfolgen, Messrauschen). Die Netze sind fest; Seeds machen deterministische Dynamik nicht unabhängiger (Hinweis aus M9).

**Episodenumfang** je Seed × Netz × Bedingung × Pause:
- 1000 Trainings- und 2000 Testepisoden je Zielklasse;
- für LDA zusätzlich 500 Validierungsepisoden, nur zur Wahl der Schrumpfung, falls nicht Ledoit-Wolf.

**Trennung Training/Test:**
- Ablenkfolgen und Rauschen kommen aus **disjunkten benannten Strömen**: Rolle `decoder_train` bzw. `test`, Bedingung, Pause, Kanal.
- Episoden-IDs sind disjunkt; geprüft wird mit SCF `check_split`.
- **Hinweis:** Bei W = 3 gibt es nur 27 Fenstermuster. Gleiche *Muster* kommen in Training und Test zufällig vor. Das ist kein Leck, denn sie sind von der Zielklasse unabhängig und werden unabhängig gezogen. Der Decoder sieht **nur** y, nie die Ablenkfolge.

**Paarung** (präzisiert Vergleiche, liefert dem Decoder nichts):
- **Innerhalb eines Splits:** Je ein A- und ein B-Episode teilen dieselbe Ablenkfolge. Damit ist die Balance exakt.
- **Über Netze und Bedingungen:** gleiche Ablenkfolgen und gleiches ε je Seed.

Nicht erlaubt:
- dem Decoder ein Paarkennzeichen oder die Ablenkfolge zu geben;
- Test-Ablenkfolgen aus Trainingsströmen zu nehmen.

**Ausschlussregeln** (vorab, ohne Ersatz-Seeds):
1. Ein fehlgeschlagener Seed wird protokolliert. Das Protokoll ist dann unvollständig, und es gibt **keine** Inferenz.
2. Aktualisierungsaufgabe: Episoden ohne Ablenkpuls im Fenster werden ausgeschlossen (erwartet 1/8). Ihre Zahl wird je Bedingung berichtet.
3. Nicht-endliche Werte führen zum Abbruch mit Status. Es gibt keine stille Korrektur.
4. Keine datenabhängigen Änderungen an Bedingungen, Pausen oder Decodern nach dem Einfrieren.

## 9. Ressourcenrahmen (Vorschlag)

| Größe | Rahmen |
|---|---|
| Episoden | 20 Seeds × 2 Netze × 4 Bedingungen (+ 4 lineare Zwillinge) × 4 Pausen × 6000 ≈ 4–8 Mio. Episoden à ≤ 7 Schritte, über Episoden vektorisiert |
| Rechenzeit | Ziel < 5 min CPU (Smoke < 30 s), harte Grenze 15 min |
| Speicher | < 1 GiB RAM; Ergebnisse < 100 MB, nur Rohwerte und Kennzahlen, keine Zustandsfolgen je Episode |
| Ablage | `D:/mandala/mandala-memory-results/m10/`, exklusiv geschrieben; C: verboten (wie Runner und M9) |
| Threads | BLAS 2 |

## 10. Einfrieren vor der Forschungsrechnung

1. **Plan-Review:** Dieser Plan wird geprüft; die [O]-Entscheidungen werden getroffen.
2. **Protokoll:** `protocol/m10_protokoll.json` plus YAML- und MD-Zwilling (Trilayer). Es enthält alle Parameter, Seeds, Ströme, Bedingungen, Pausen, Decoder, Hypothesen, Kontraste, Korrektur, Ausschlussregeln, Ressourcengrenzen und die analytischen Vorhersagen A1–A3.
3. **Code und Tests:**
   - Code: Episodengenerator, Runner, Auswertung.
   - Tests nur an **Entwicklungseinstellungen**: andere Seeds, andere Ablenkknoten und Amplituden als in Abschnitt 4.
   - Dazu Negativkontrollen: Ablenkung hängt von der Klasse ab ⇒ Leckprüfung schlägt an; Testfolgen in Trainingsströmen ⇒ Trennungsprüfung schlägt an; A1-Verletzung ⇒ erkannt.
4. **Einfrier-Commit:** Protokoll, Auswertungscode und SHA-256 im Evaluator, wie M9b/M9c. Der Smoke-Lauf läuft **nach** dem Einfrieren mit den Smoke-Seeds und dient nur Laufzeit- und Formatprüfung.
5. **Forschungsrechnung** (einmal), danach Auswertung mit `inference_release`. Abweichungen werden berichtet, nicht repariert.

## 11. Grenzen

- **Synthetische Modellstudie** an zwei festen 12-Knoten-Netzen mit einem Benchmark-Parametersatz. Keine biologische Aussage und keine allgemeine Aussage über KI-Leistung.
- **Ablenkung = Pulse an zwei Kanälen** in einem kurzen Fenster. Andere Ablenkarten (Dauerreize, Rauschen im Prozess, lernende Netze) sind nicht abgedeckt.
- **Decoderabhängig:** Für Mischverteilungen ist keiner der Decoder allgemein Bayes-optimal (A6).
- **Kein Ressourcenvergleich über das Budget hinaus:** gleiche Zeilensummen und gleiches q, aber verschiedene Spektren. Das ist der Gegenstand der Frage, kein Mangel.

## 12. Offene Entscheidungen (Zusammenfassung)

| # | Frage | Vorschlag |
|---|---|---|
| O1 | Fensterlage/-länge | W = 3 direkt vor der Ablesung, in beiden Netzen |
| O2 | Ablenkrate | p = 0,5 je Fensterschritt |
| O3 | Amplitude F+ | 1,8 |
| O4 | Aktualisierungsaufgabe | Kanal des letzten Pulses (X/Y) |
| O5 | Äquivalenzgrenze H-F | ±0,02 (TOST) oder H-F rein beschreibend |
| O6 | Ablesezeitpunkte | primär angeglichen (d = 6 / d = 3), sekundär d ∈ {3, 4, 6} |
| O7 | Primärer Decoder | Nearest-Mean, sekundär LDA (Ledoit-Wolf) |
| O8 | Hauptkontraste | H-N und H-F+ (Holm über 2); alles andere beschreibend |
