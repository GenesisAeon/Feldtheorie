# M10 – Erinnerung unter Ablenkung: Versuchsplan, Fassung 2 (Entwurf zur Prüfung)

**Status:** reviewbarer **Plan**. Noch kein Protokoll eingefroren, keine M10-Forschungsrechnung, kein Ausbau der Oberfläche.

**Aufträge:**
- `D:/mandala/AnschlussPromtAstra.txt`, Teil 2;
- Review `D:/mandala/mandala-memory-results/integration-2026-10-03/ASTRA_REVIEW_M10_PLAN.md`, Punkte R5–R7. R8 betrifft die Testorganisation und ist in der README unter „Teststufen“ umgesetzt.

**Grundlage:** das integrierte Labor M0–M9:
- Feldtheorie `main` = `061adba`
- Herleitung [`M9_HERLEITUNG.md`](M9_HERLEITUNG.md) und Erratum [`M9_ERRATUM_1.md`](M9_ERRATUM_1.md)

**Leitfrage:** Bleibt die Identität eines ursprünglichen Reizes A oder B lesbar, wenn in der bisherigen Ruhephase weitere, von A/B unabhängige Reize auftreten? Wie unterscheiden sich ein modulares und ein gleich budgetiertes uniformes Netz?

Der Plan trennt drei Arten von Aussagen:
- **[E]** bestehende Erkenntnis;
- **[H]** neue Hypothese;
- **[O]** offene Entscheidung.

## Änderungen gegenüber Fassung 1 (Review R5–R7)

| Punkt | Fassung 1 | Fassung 2 |
|---|---|---|
| **R5** Theorie und Decoder | A2/A3 sollten an trainierten Decodern sichtbar werden | **Zwei getrennte Messebenen.** Die **Bayes-Ebene B** rechnet mit der *expliziten* Likelihood der Klassenverteilungen; das sind exakt Mischungen aus 27 Normalverteilungen, auch im tanh-Netz (Abschnitt 6). Ihre einzige Unsicherheit ist Monte-Carlo-Unsicherheit. Die **Decoder-Ebene D** (Nearest-Mean, LDA) wird daneben berichtet und prüft keine Bayes-Aussage. A1 wird als Zustandsidentität geprüft, A2 über die Projektion auf V₋, A3 als analytisches Resultat mit einer festgelegten numerischen Prüfung. H-N ist für tanh ausdrücklich nur Hypothese. |
| **R6** Ablesezeit | primär d = 6 (modular) gegen d = 3 (uniform) | **primär d = 4 für beide Netze**, W = 3 direkt davor. Der Vergleich bei ähnlicher Ausgangsleistung (d = 6/3) bleibt **beschreibend**. Keine Auswahl anhand von M10-Ergebnissen. |
| **R7** Inferenz | „Holm-korrigiert“, „optional Sign-Flip“, H-F zugleich beschreibend und TOST | **Vollständig festgelegt** (Abschnitt 7): Nur H-N und H-F+ sind bestätigend, auf Ebene B, einseitig, mit Mindesteffekt, Holm über 2, und Prüfgrößen aus Monte-Carlo-Standardfehlern. H-F, Decoder-Ebene und Zielkonflikt bleiben **rein beschreibend**. Kein Sign-Flip-Test. |

---

## 1. Bestehende Erkenntnisse [E]

| # | Erkenntnis | Quelle |
|---|---|---|
| E1 | Ohne Ablenkung steckt die Reizidentität im Modul-Unterschieds-Modus μ_D (modular) bzw. im Binnenmodus μ_I (uniform). q ist nur obere Grenze. | M9 (24/24, 23/23) |
| E2 | Analytische Grundwerte ohne Ablenkung (σ = 0,02, a = 0,6, Bayes):<br>• **modular**: d = 3: 0,981; **d = 4: 0,935**; d = 6: 0,801<br>• **uniform** (M = 1, gleiches γ = 0,8 und ℓ = 0,5): d = 3: 0,828; **d = 4: 0,670**; d = 6: 0,538 | `predict.py`, keine Kernrechnung |
| E3 | Involution P mit P e_0 = e_4, P A Pᵀ = A, also x_B = P x_A.<br>• modular: Knoten 8–11 fest, 1 ↔ 5, 2 ↔ 6, 3 ↔ 7<br>• uniform: alle Knoten außer 0, 4 fest | M9, Abschnitt 5 |
| E4 | Hebb-Anpassung brachte keinen nachweisbaren Gewinn (d = 8). | M4 |

## 2. Ablauf einer Episode (unverändert, Pause primär d = 4)

```
x_0 = 0
Schritt 0:            Zielreiz u_0 = e_s, s ∈ {A, B} (Knoten 0 bzw. 4), a = 0,6
Schritte 1 … d−3:     Ruhe (bei d = 4: Schritt 1)
Schritte d−2 … d:     Ablenkfenster W = 3; je Schritt unabhängig mit p = 0,5 ein Puls
                      an Kanal X oder Y (je ½), sonst 0
Ablesung:             x_(d+1);  y = x_(d+1) + ε,  ε ~ N(0, σ² I),  σ = 0,02
```

- **Kanäle:** Ablenkpulse gehen über eigene Eingangsspalten mit Amplitude a_X.
- **Unabhängigkeit:** Die Ablenkfolge wird **unabhängig** von der Zielklasse gezogen.
- **Muster:** Es gibt 3³ = **27 Fenstermuster** π mit bekannten Wahrscheinlichkeiten P(π): (1/2)^(#leer) · (1/4)^(#Pulse).
- **Fester Rest:** ℓ = 0,5, tanh, kein Prozessrauschen.

## 3. Netze (fest, ohne Hebb)

| Netz | Konstruktion |
|---|---|
| modular | `budget_adjacency(12, 3, γ = 4/5, c = 1/4)` (eingefrorenes Benchmark-Netz) |
| uniform | `budget_adjacency(12, 1, γ = 4/5)`: gleiche Zeilensumme γ, gleiches q, gleiche Gesamtsumme |

**Für beide Netze identisch:**
- N, ℓ, tanh, Zielknoten 0/4, Ablenkknoten, Amplituden;
- W, p, σ, Pausen;
- Decoder, Episodenzahlen, Seeds.

**Lineare Zwillinge** (identity) jeder Bedingung dienen nur zur Prüfung von A2/A3.

## 4. Ablenkbedingungen

| Kürzel | Orte X / Y | a_X | Zweck |
|---|---|---|---|
| **K0** | – | – | Kontrolle |
| **F** | 8 / 10 | 0,6 | in beiden Netzen P-fest ⇒ linear störungsfrei (A2) |
| **N** | 1 / 5 | 0,6 | modular nicht P-fest (1 ↔ 5), uniform P-fest |
| **F+** | 8 / 10 | 1,8 | P-fest, aber tanh-Sättigung (nur nichtlinearer Störweg) |

## 5. Zwei Leistungen, getrennt gemessen

- **Bewahren:** Zielklasse s ∈ {A, B} aus y.
- **Aktualisieren:** Kanal des **letzten** Pulses im Fenster (X/Y) aus derselben Beobachtung. Episoden ohne Puls (P = 1/8) sind ausgeschlossen.

Beide Leistungen werden auf **beiden** Ebenen B und D berichtet. Ein **Zielkonflikt** wird in dieser Runde **nicht bestätigend** geprüft; er wird nur beschrieben, und nur wenn beide Leistungen in derselben Bedingung gemessen sind.

## 6. Theorie, Messebenen und ihre Prüfung

### 6.1 Was die Klassenverteilungen sind

Für ein festes Netz, eine Pause d, eine Zielklasse s und ein Fenstermuster π ist der Ablesezustand **deterministisch**: z(s, π). Damit ist

  p(y | s) = Σ_π P(π) · N(y; z(s, π), σ² I)

**exakt** eine Mischung aus 27 Normalverteilungen, im tanh- wie im linearen Netz. Die alte Formel Φ(‖Δx‖/2σ) gilt nur für K0, also ohne Mischung.

### 6.2 Ebene B: Bayes-Leistung mit expliziter Likelihood

Die Bayes-Trefferquote ist acc_B = E_y[ max_s P(s | y) ] mit P(s | y) ∝ ½ p(y | s). Sie wird so bestimmt:
1. Alle z(s, π) werden mit dem getesteten Kern berechnet: 2 × 27 deterministische Läufe je Netz, Bedingung und Pause.
2. Gezogen wird y aus ½ p(y|A) + ½ p(y|B); gemittelt wird max_s P(s|y). Das ist ein erwartungstreuer Schätzer mit geringerer Varianz als das Zählen von Treffern.
3. **Umfang:** n_MC = 2 000 000 Ziehungen je Netz × Bedingung × Pause, eigener Strom `m10-bayes`. Der Monte-Carlo-Standardfehler SE_MC wird aus der Stichprobe geschätzt und berichtet (erwartet ≤ 3·10⁻⁴).
4. **K0:** analytisch, acc_B = Φ(‖z(A) − z(B)‖ / 2σ), ohne Monte-Carlo.

Diese Ebene beschreibt die **Information im Zustand** unter dem bekannten Modell, unabhängig von einem Lernverfahren.

### 6.3 Ebene D: trainierte Decoder

- **Decoder:** Nearest-Mean ohne Standardisierung (primär innerhalb von D) und LDA mit Ledoit-Wolf-Schrumpfung, nur aus Trainingsdaten.
- **Daten:** 20 Seeds, je 1000 Trainings- und 2000 Testepisoden je Zielklasse, Netz, Bedingung und Pause.
- **Rolle:** Ebene D beschreibt, **wie viel ein realistisch trainierter Decoder davon abliest**. Ein Ergebnis auf Ebene D bestätigt oder widerlegt **keine** Aussage über Ebene B. Insbesondere garantiert A3 keine Monotonie für einen neu trainierten, suboptimalen Decoder.

### 6.4 Analytische Aussagen und wie sie geprüft werden

| # | Aussage | Status | Prüfung (vorab festgelegt) |
|---|---|---|---|
| **A1** | Für P-feste Ablenkorte und **dasselbe** Muster gilt x_B(k) = P x_A(k) für alle k, auch nichtlinear. | bewiesen (Symmetrie, Abschnitt 5 der Herleitung) | **Zustandsidentität im Kern:** Für jedes Netz, jedes P-feste π und jedes k gilt max\|x_B(k) − P x_A(k)\| ≤ 1e‑14 · max\|x\|. Die Toleranz deckt nur andere Summationsreihenfolge ab. Gilt für F und F+ in beiden Netzen und für N im uniformen Netz; N modular ist die Negativkontrolle (dort **nicht** erfüllt). |
| **A2** | Linear und P-fest: Die Ablenkantwort r(π) liegt in V₊, der Klassenunterschied in V₋. Die V₋-Projektion von y ist suffizient und von π unabhängig, also acc_B(Bedingung) = acc_B(K0). | bewiesen | (a) **Strukturell:** ‖P₋ r(π)‖ ≤ 1e‑13 für alle 27 π, mit P₋ = (I − P)/2.<br>(b) **Numerisch (Ebene B):** \|acc_B(Bed.) − acc_B(K0)\| ≤ 4·SE_MC.<br>Beides im linearen Zwilling. |
| **A3** | Linear, beliebige Orte: acc_B(Bedingung) ≤ acc_B(K0). Beweis: Beobachtung = Beobachtung ohne Ablenkung + davon unabhängiges Signal; Datenverarbeitungs-Ungleichung. | bewiesen, **nur linear** | Geführt als **analytisches Resultat**. Numerische Gegenprobe auf Ebene B im linearen Zwilling: acc_B(Bed.) ≤ acc_B(K0) + 4·SE_MC. Ein Verstoß wäre ein Rechen- oder Implementierungsfehler und wird berichtet, nicht repariert. |
| A4 | Linear, N modular: Die Ablenkantwort hat einen V₋-Anteil, die Trefferquote sinkt typischerweise. | Richtung aus A3 (≤); Höhe nur numerisch | Ebene B im linearen Zwilling, beschreibend |
| A5 | tanh: A2 und A3 gelten nicht mehr; die Ablenkung moduliert die lokale Verstärkung. | – | nur Ebene B/D, beschreibend bzw. H-N/H-F+ |

**Prüfung der Prüfwerkzeuge vor dem Einfrieren**, an Entwicklungseinstellungen mit anderen Ablenkknoten, Amplituden und Seeds:
- **Ebene-B-Schätzer:** Er trifft bei einem 1-Muster-Fall (keine Mischung) die geschlossene Formel Φ(‖Δ‖/2σ) innerhalb von 4·SE_MC.
- **Zwei-Muster-Fall:** Er trifft eine unabhängige Quadraturrechnung in einer Dimension.
- **A1/A2-Prüfungen:** Sie schlagen bei absichtlich nicht P-festen Orten an.

## 7. Hypothesen und vollständig festgelegtes Inferenzverfahren [H]

**Messgröße der Interferenz** (Ebene B) je Netz n, Bedingung b, primäre Pause d = 4:

  I_n(b) = acc_B,n(K0) − acc_B,n(b)

**Bestätigende Familie** (genau 2 Hypothesen; einseitig; Mindesteffekt δ = 0,01):

| | Nullhypothese H₀ | Alternative H₁ | Begründung (heuristisch, kein Satz) |
|---|---|---|---|
| **H-N** | Δ_N := I_mod(N) − I_uni(N) ≤ 0,01 | Δ_N > 0,01 | Für das uniforme Netz sind 1/5 P-fest (linear störungsfrei, A2), für das modulare nicht (A4). Für tanh folgt das **nicht** als Satz aus A2/A4. |
| **H-F+** | Δ_F+ := I_uni(F+) − I_mod(F+) ≤ 0,01 | Δ_F+ > 0,01 | Sättigung aus dem unbeteiligten Modul erreicht die Eingangsmodule im modularen Netz (c = 1/4) gedämpft, im uniformen direkt. |

**Prüfgröße:**
- **Schätzer:** Δ̂ aus den Ebene-B-Schätzern. Die K0-Terme sind analytisch, die beiden Bedingungsterme kommen aus unabhängigen Monte-Carlo-Strömen.
- **Standardfehler:** SE(Δ̂) = √(SE₁² + SE₂²).
- **Teststatistik:** Z = (Δ̂ − 0,01) / SE(Δ̂), mit p = 1 − Φ(Z).
- **Voraussetzung:** Der Schätzer ist beschränkt (Werte in [½, 1]). Bei n_MC = 2·10⁶ ist die Normalapproximation des Monte-Carlo-Mittels (zentraler Grenzwertsatz) gerechtfertigt.
- **Was die Unsicherheit bedeutet:** Sie ist **reine Monte-Carlo-Unsicherheit** über eine deterministische Größe des festen Modells. Es ist keine Aussage über eine Population von Netzen oder Seeds.

**Holm (α = 0,05, Familie {H-N, H-F+}):**
- Ordne p₍₁₎ ≤ p₍₂₎.
- Verwirf H₍₁₎, wenn p₍₁₎ ≤ 0,025; nur dann verwirf zusätzlich H₍₂₎, wenn p₍₂₎ ≤ 0,05.
- **Berichtet werden:** Punktschätzer, Holm-adjustierte p-Werte und **unadjustierte** zweiseitige 95-%-MC-Intervalle, als solche benannt.

**Entscheidung:**
- „bestätigt“ bei verworfener H₀;
- sonst „nicht bestätigt“, ausdrücklich nicht „widerlegt“, außer das unadjustierte 95-%-Intervall liegt ganz unter 0. Dann gilt „Richtung widerspricht der Hypothese“.

**Rein beschreibend** (kein Test, keine Adjustierung, Intervalle als unadjustiert benannt):
- **H-F:** \|I_n(F)\| bei a_X = 0,6 in beiden tanh-Netzen. Die TOST-Variante aus Fassung 1 entfällt.
- **Ebene D:**
  - Interferenz je Decoder als Mittel der gepaarten Seed-Differenzen;
  - 95-%-Bootstrap über ganze Seeds (2000 Wiederholungen, eigener Bootstrap-Seed). Die Seeds sind Monte-Carlo-Wiederholungen bei festen Netzen, keine Population.
  - **Kein Sign-Flip-Test.**
- **Aktualisieren und Zielkonflikt:** beide Ebenen, beschreibend.
- **Normierte Interferenz:** I_n / (acc_B,n(K0) − ½), wegen der verschiedenen Ausgangsleistungen bei d = 4 (0,935 gegen 0,670; Decke und Boden offen berichtet).
- **Sekundäre Pausen:**
  - angeglichener Vergleich d = 6 (modular) gegen d = 3 (uniform); er vermischt Struktur und Alter der Erinnerung;
  - gemeinsame Pausen d ∈ {3, 6}.
- **Lineare Zwillinge:** A2/A3-Prüfungen (Abschnitt 6.4) und A4.

## 8. Daten, Seeds, Trennung, Ausschluss

- **Ebene B:**
  - kein Lernen, also keine Trainings-/Testtrennung;
  - Monte-Carlo-Strom `m10-bayes`, je Netz × Bedingung × Pause ein eigener benannter Teilstrom;
  - die Zustände z(s, π) kommen aus dem Kern und sind zufallsfrei.
- **Ebene D:** 20 Forschungs-Seeds und 3 Smoke-Seeds, eigene Listen, Modus `m10`.
  - **Ströme:** Ablenkmuster und Rauschen kommen aus disjunkten benannten Strömen je Rolle (`decoder_train`, `test`), Bedingung, Pause und Kanal.
  - **IDs:** Episoden-IDs sind disjunkt; geprüft mit SCF `check_split`.
  - **Gleiche Muster sind kein Leck:** Gleiche *Muster* in Training und Test sind bei 27 Mustern erwartbar. Sie sind von der Zielklasse unabhängig, und der Decoder sieht nur y.
  - **Paarung:** Innerhalb eines Splits teilen sich je eine A- und eine B-Episode dasselbe Muster. Über Netze hinweg sind Muster und ε je Seed gleich.
  - **Verboten:** gemeinsame Episoden oder Zufallsströme über die Split-Grenze sowie Paarkennzeichen für den Decoder.

**Ausschlussregeln** (vorab, ohne Ersatz):
1. Ein Fehler in einem Teillauf (Seed oder Monte-Carlo-Teilstrom) wird protokolliert. Das Protokoll ist dann unvollständig, und es gibt **keine** bestätigende Aussage (Freigaberegel wie `inference_release`).
2. Aktualisieren: Episoden bzw. Muster ohne Puls sind ausgeschlossen; ihre Zahl bzw. Masse wird berichtet.
3. Nicht-endliche Werte führen zum Abbruch mit Status, ohne stille Korrektur.
4. Keine Änderung an Bedingungen, Pausen, Decodern, n_MC, δ oder α nach dem Einfrieren.

## 9. Ressourcenrahmen

| Größe | Rahmen |
|---|---|
| Ebene B | 2 Netze × (4 + 4 lineare) Bedingungen × 3 Pausen × 2·10⁶ Ziehungen; je Ziehung 54 Normaldichten in 12 Dimensionen, in Blöcken vektorisiert. Ziel < 5 min. |
| Ebene D | 20 Seeds × 2 Netze × 8 Bedingungen × 3 Pausen × 6000 Episoden (≤ 7 Schritte, vektorisiert). Ziel < 5 min. |
| Gesamt | harte Grenze 20 min CPU, < 1 GiB RAM, Ergebnisse < 100 MB (nur Kennzahlen und Rohwerte je Seed/Teilstrom) |
| Ablage | `D:/mandala/mandala-memory-results/m10/`, exklusiv geschrieben, C: verboten; BLAS 2 Threads |

## 10. Einfrieren vor der Forschungsrechnung

1. **Plan-Review** dieser Fassung; offene Punkte entscheiden (Abschnitt 12).
2. **Protokoll:** `protocol/m10_protokoll.json` plus YAML- und MD-Zwilling. Es enthält alle Parameter, Seeds und Ströme, n_MC, δ, α, die Holm-Familie, die Prüfregeln A1–A3 mit Toleranzen, die beschreibenden Größen, die Ausschlussregeln und die Ressourcengrenzen.
3. **Code und Tests:** nur an Entwicklungseinstellungen, darunter die Werkzeugprüfungen aus Abschnitt 6.4 und Negativkontrollen:
   - klassenabhängige Ablenkung ⇒ Leckprüfung schlägt an;
   - Teststrom im Training ⇒ Trennungsprüfung schlägt an;
   - nicht P-feste Orte ⇒ A1-/A2-Prüfung schlägt an.
4. **Einfrier-Commit:** Protokoll, Auswertungscode und SHA-256 im Evaluator (wie M9b/M9c). Danach der Smoke-Lauf, nur für Laufzeit und Format.
5. **Forschungsrechnung** einmal, dann Auswertung. Abweichungen werden berichtet, nicht repariert.

## 11. Grenzen

- **Synthetische Modellstudie:** zwei feste 12-Knoten-Netze, ein Parametersatz. Keine biologische und keine allgemeine KI-Aussage.
- **Ebene B setzt das bekannte Modell voraus:** Die Muster-Zustände z(s, π) sind bekannt. Sie misst Information im Zustand, nicht Lernbarkeit.
- **Ebene D ist decoderabhängig.** Keiner der Decoder ist bei Mischverteilungen allgemein Bayes-optimal.
- **Ablenkung nur als Pulse an zwei Kanälen in kurzem Fenster.** Andere Ablenkarten sind nicht abgedeckt.
- **Verschiedene Ausgangsleistung bei d = 4** (0,935 gegen 0,670). Sie begrenzt die mögliche Interferenz im uniformen Netz nach oben (Boden ½). Deshalb wird zusätzlich normiert beschrieben.
- **Gleiche Budgets, aber verschiedene Spektren.** Das ist der Gegenstand der Frage.

## 12. Entscheidungen

| # | Frage | Stand |
|---|---|---|
| O1 | Fenster | **entschieden:** W = 3 direkt vor der Ablesung |
| O2 | Rate | **entschieden:** p = 0,5 |
| O3 | Amplitude F+ | **entschieden:** 1,8 |
| O4 | Aktualisierungsaufgabe | **entschieden:** Kanal des letzten Pulses |
| O5 | H-F | **entschieden:** rein beschreibend (kein TOST) |
| O6 | Pausen | **entschieden:** primär d = 4 für beide; beschreibend d = 6/3 angeglichen sowie d ∈ {3, 6} |
| O7 | Decoder | **entschieden:** Ebene D mit Nearest-Mean und LDA (Ledoit-Wolf), beschreibend |
| O8 | Bestätigende Familie | **entschieden:** H-N, H-F+ auf Ebene B, einseitig, δ = 0,01, Holm α = 0,05 |
| O9 | **neu, offen:** Mindesteffekt δ | Vorschlag 0,01 (ein Prozentpunkt Bayes-Trefferquote). Bitte bestätigen oder ändern; muss vor dem Einfrieren feststehen. |
| O10 | **neu, offen:** n_MC | Vorschlag 2·10⁶ (SE_MC ≤ 3·10⁻⁴, klein gegen δ). Bitte bestätigen. |
| O11 | **neu, offen:** Ebene D bestätigend? | Vorschlag: nein (beschreibend). Eine bestätigende Decoder-Replikation bräuchte eine eigene, vorab definierte Familie. |
