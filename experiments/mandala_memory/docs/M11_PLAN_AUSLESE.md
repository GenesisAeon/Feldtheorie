# M11 – Die vorhandene Erinnerung besser auslesen: Versuchsplan (Entwurf zur Prüfung)

**Status:** reviewbarer **Plan**. Kein Protokoll eingefroren, keine Rechnung.

**M10 bleibt unverändert:** Netze, Bedingungen, eingefrorener Code und Ergebnisse (`m10-freeze`). M11 liest die Netze nur über die eingefrorenen M10-Funktionen.

**Leitfrage (Johann, 2026-10-04):** Wie viel der Lücke zur Bayes-Grenze lässt sich durch ein besseres Ausleseverfahren schließen, während das Mandala unverändert bleibt?

**Getrennt untersucht:**
- **Trainingsmenge:** Helfen mehr Beispiele bereits Nearest-Mean und LDA?
- **Modellklasse:** Hilft ein kleines nichtlineares Netz bei gleicher Trainingsmenge?

**Referenz:** die Bayes-Grenze.

Kennzeichnung: **[E]** bestehende Erkenntnis, **[H]** Hypothese, **[O]** offene Entscheidung (mit Vorschlag).

## 1. Ausgangslage [E]

Alle Werte aus dem freigegebenen M10-Forschungslauf, d = 4, tanh, Bewahren:

| Fall | Bayes acc_B | Nearest-Mean (20 Seeds) | LDA Ledoit-Wolf | Lücke NM | Lücke LDA |
|---|---|---|---|---|---|
| **modular, N** (nahe Ablenkung) | 0,9116 | 0,6346 (sd 0,0036) | 0,7759 (sd 0,0061) | **0,277** | **0,136** |
| uniform, F+ | 0,6696 | 0,6243 (sd 0,0226) | 0,6669 (sd 0,0069) | 0,045 | 0,003 |
| modular, K0 (Kontrolle) | 0,9352 | 0,9335 | 0,9335 | 0,002 | 0,002 |
| uniform, K0 (Kontrolle) | 0,6696 | 0,6672 | 0,6672 | 0,002 | 0,002 |

Je Klasse wurden dafür 1000 Trainingsepisoden verwendet. Die Klassenverteilungen sind exakt bekannte Mischungen aus 27 Normalverteilungen (M10, Abschnitt 6.1).

## 2. Kernidee: die Lücke vollständig zerlegen

### 2.1 Exakte Populations-Trefferquote linearer Regeln

Eine lineare Regel „Klasse B, wenn w·y + b > 0“ hat bei y = z(s, π) + ε mit ε ~ N(0, σ²I) die **exakte** Balanced Accuracy

  acc(w, b) = ½ Σ_π P(π) [ Φ(−(w·z(A,π) + b)/(σ‖w‖)) + Φ((w·z(B,π) + b)/(σ‖w‖)) ]

Die Projektion ist eine Mischung aus 27 eindimensionalen Normalverteilungen. Für **jede trainierte** lineare Regel (Nearest-Mean, LDA) wird die Trefferquote damit **ohne Test-Stichprobenrauschen** bestimmt. Eine Testmenge dient nur noch als Gegenprobe.

### 2.2 Referenzgrößen, vor der Rechnung aus dem Modell bestimmt und eingefroren

| Größe | Definition | Bestimmung |
|---|---|---|
| acc_B | Bayes-Grenze | aus M10 übernommen (Monte Carlo, SE ≤ 10⁻⁴) |
| acc_lin* | beste **lineare** Regel | numerische Maximierung von acc(w, b) aus 2.1, mit mehreren Startpunkten (LDA-, NM-Lösung, zufällige); berichtet als „beste gefundene“, eine untere Schranke für das lineare Optimum |
| acc_NM(∞) | Nearest-Mean bei unendlich vielen Daten | Regel mit den wahren Klassenmitteln μ_s = Σ_π P(π) z(s,π), exakt aus 2.1 |
| acc_LDA(∞) | LDA bei unendlich vielen Daten | wahre gepoolte Kovarianz σ²I + Σ_π P(π)(z − μ_s)(z − μ_s)ᵀ, Schrumpfung → 0; exakt aus 2.1 |

### 2.3 Zerlegung je Decoder D und Trainingsmenge n

  acc_B − acc_D(n) = [acc_B − acc_lin*] + [acc_lin* − acc_D(∞)] + [acc_D(∞) − acc_D(n)]

| Teil | Name | Bedeutung |
|---|---|---|
| acc_B − acc_lin* | **Nichtlinearitätslücke** | nur ein nichtlinearer Ausleser kann sie schließen |
| acc_lin* − acc_D(∞) | **Kriteriumslücke** | das Anpassungskriterium des linearen Decoders (Mittelwerte bzw. Gauß-Annahme) ist nicht trefferoptimal; mehr Daten helfen nicht |
| acc_D(∞) − acc_D(n) | **Schätzlücke** | mehr Daten helfen |

**So beantwortet die Zerlegung die Leitfrage:**
- Ist die Schätzlücke groß, fehlen vor allem Trainingsdaten.
- Sind Kriteriums- oder Nichtlinearitätslücke groß, wertet die Modellklasse die gespeicherte Information nicht passend aus.

Für das nichtlineare Netz gibt es keine geschlossene Grenze. Seine Lücke wird empirisch über n gemessen und an acc_B und acc_lin* eingeordnet.

## 3. Versuch

### Fest aus M10 (unverändert)

- Netze (modular c = 1/4, uniform M = 1), tanh, σ = 0,02, Fenster W = 3, p = 0,5;
- Zustände z(s, π) aus dem eingefrorenen Kern;
- Aufgabe **Bewahren** (A/B), d = 4.

### Fälle

| Fall | Rolle |
|---|---|
| **modular N** | Hauptfall: größte Lücke |
| uniform F+ | Nebenfall: decoderspezifischer Verlust nur bei Nearest-Mean |
| modular K0, uniform K0 | Kontrollen: ohne Ablenkung, Bayes-Regel linear, Lücke soll ≈ 0 sein |

### Faktor 1, Trainingsmenge

n je Klasse ∈ {250, 1000, 4000, 16000}, verschachtelt: die kleineren Mengen sind Präfixe derselben Ziehung je Seed.

### Faktor 2, Modellklasse (bei denselben Daten je Seed und n)

| Decoder | Beschreibung |
|---|---|
| Nearest-Mean | ohne Standardisierung (wie M3–M10) |
| LDA | Ledoit-Wolf (wie M10) |
| **MLP** | 12 → 32 tanh → 1 (logistisch); Adam; Gewichtsabfall fest; volles Batch; frühes Stoppen auf 20 % **aus dem Trainingsbudget n** (gleiche Datenmenge wie die anderen Decoder); Eingaben mit Trainingsstatistik standardisiert (Teil der Modellklasse); feste maximale Epochenzahl; 3 Initialisierungen je Training, die beste nach **Validierung**. Umgesetzt in numpy, keine neue Installation. |

**[O1]** MLP-Breite 32 und Hyperparameter. Vorschlag: vor dem Freeze **nur an den M10-Entwicklungsbedingungen** (Fdev/Ndev, Entwicklungs-Seeds) einstellen, dann einfrieren. Kein Nachjustieren an Forschungsdaten.

### Daten

- 20 neue Seeds, eigener Modus `m11`.
- Trainingsmuster und Rauschen kommen aus benannten Strömen (Seed, Rolle, n-Präfix); gepaart wie in M10 (jedes Muster einmal für A und B).
- **Bewertung:**
  - lineare Decoder exakt nach 2.1, Gegenprobe auf der Testmenge;
  - MLP auf einer Testmenge von 100 000 Episoden je Klasse aus einem eigenen Strom (Standardfehler ≈ 0,001).
- Der Decoder sieht nur y.

## 4. Hypothesen und Auswertung [H]

### Primäre Kennzahlen (Hauptfall)

- G_D(n) = acc_B − acc_D(n) für D ∈ {NM, LDA, MLP} und alle n;
- dazu die drei Lückenteile aus 2.3 für Nearest-Mean und LDA;
- und der geschlossene Anteil (acc_D(n) − acc_LDA(1000)) / (acc_B − acc_LDA(1000)).

Alles mit 95-%-Bootstrap über ganze Seeds.

### Bestätigende Kontraste (Vorschlag **[O2]**; Hauptfall, einseitig, δ = 0,01, Holm α = 0,05)

| | Frage | Kontrast |
|---|---|---|
| **C-Daten** | Helfen mehr Beispiele dem besten linearen Decoder? | acc_LDA(16000) − acc_LDA(1000) > δ |
| **C-Modell** | Hilft ein nichtlineares Netz bei gleicher Menge? | acc_MLP(1000) − acc_LDA(1000) > δ |

- **Prüfgröße:** gepaarte Seed-Differenzen; einseitiger t-Test auf (Mittel − δ) mit 19 Freiheitsgraden.
- **Annahme:** näherungsweise normal verteilte Seed-Differenzen; berichtet zusammen mit Bootstrap-Intervallen.
- **Wortregeln wie M10:** „bestätigt“ oder „nicht bestätigt“; „Richtung widerspricht“ nur, wenn das 95-%-Intervall ganz unter 0 liegt.

### Vorhersagen aus den Referenzen (vor dem Lauf eingefroren, deterministische Prüfung wie in M9)

- **V1:** Trainierte Nearest-Mean- und LDA-Regeln nähern sich mit wachsendem n ihren exakten Grenzwerten acc_D(∞) an. Bei n = 16000 liegt der Mittelwert über Seeds innerhalb einer vorab festgelegten Toleranz unter acc_D(∞), Vorschlag 0,01.
- **V2:** Ist acc_LDA(∞) ≈ acc_LDA(1000), also die Schätzlücke < δ, sagt das voraus, dass C-Daten **nicht** bestätigt wird. Das ist direkt aus den eingefrorenen Referenzen lesbar.
- **V3:** Ist acc_B − acc_lin* > δ, gibt es Raum für C-Modell. Ob das MLP ihn bei n = 1000 nutzt, ist die **empirische** Frage.

### Beschreibend

- alle n, Nebenfall und Kontrollen;
- MLP-Lernkurve;
- Testmengen-Gegenprobe der exakten Formel.

**Kontrolle K0:** Dort ist die Bayes-Regel linear. Erwartet wird acc_lin* ≈ acc_B, und kein Decoder sollte bei großem n mehr als δ unter acc_B liegen. Eine Abweichung ist ein Diagnosebefund.

## 5. Kontrollen und Prüfwerkzeuge (vor dem Freeze)

- Die exakte Formel 2.1 wird an einem 1-Komponenten-Fall gegen Φ(‖Δ‖/2σ) geprüft und an Mischungen gegen eine große Monte-Carlo-Testmenge (Entwicklungsbedingungen).
- Die Grenzwert-Regeln (NM/LDA mit wahren Momenten) werden gegen trainierte Regeln bei sehr großem n verglichen (Entwicklungsbedingungen).
- MLP-Implementierung:
  - Gradientenprüfung (finite Differenzen);
  - auf K0 (zwei Normalverteilungen) erreicht sie bei großem n die Bayes-Grenze bis auf eine kleine Toleranz;
  - deterministisch je Seed.
- Freigabe-Gate wie M10 (erwartetes Raster aus dem Protokoll, exakte n, Ströme, Kontrollen); Zeitgrenze kooperativ; exklusive Ablage auf D:.

## 6. Ressourcen (Schätzung, per Laufzeitcheck an Entwicklungsbedingungen zu bestätigen)

| Teil | Umfang | Schätzung |
|---|---|---|
| Lineare Decoder | 20 Seeds × 4 n × 4 Fälle, exakte Bewertung | Sekunden |
| MLP | 20 × 4 × 4 = 320 Trainings × 3 Initialisierungen, bis 32 000 Beispiele, kleines Netz, volles Batch | Ziel < 15 min, harte Grenze 30 min |
| Referenzen | acc_lin* als numerische Optimierung über 13 Parameter, mehrere Starts, je Fall | < 1 min |

RAM < 1 GiB.

## 7. Einfrieren

Wie M10:
1. Plan-Review und Entscheidungen [O];
2. Protokoll mit YAML- und MD-Zwilling, **einschließlich der eingefrorenen Referenzgrößen aus 2.2**;
3. Code und Tests nur an Entwicklungsbedingungen;
4. Freeze-Datensatz mit Protokoll-Hash, geprüftem Code-Commit und Code-Prüfsummen;
5. Smoke-Lauf, dann ein einmaliger Forschungslauf;
6. Auswertung über das Gate.

## 8. Grenzen

- **Synthetische Modellstudie:** dieselben zwei 12-Knoten-Netze und M10-Bedingungen; eine nichtlineare Modellklasse (kleines MLP) mit festen Hyperparametern. Andere Architekturen sind nicht abgedeckt.
- **acc_lin* ist die beste gefundene lineare Regel**, eine untere Schranke des linearen Optimums. Die Nichtlinearitätslücke ist damit höchstens überschätzt.
- **MLP-Ergebnisse sind empirisch.** Die exakte Bewertung gilt nur für lineare Regeln.
- **Keine biologische oder allgemeine KI-Aussage.** Es geht um das Auslesen **dieses** Zustands.

## 9. Offene Entscheidungen

| # | Frage | Vorschlag |
|---|---|---|
| O1 | MLP-Architektur und Hyperparameter | 12 → 32 → 1 tanh, an Entwicklungsbedingungen festgelegt |
| O2 | Bestätigende Familie | C-Daten und C-Modell, δ = 0,01, Holm |
| O3 | Toleranz für V1 | 0,01 |
| O4 | Trainingsmengen | {250, 1000, 4000, 16000} je Klasse |
| O5 | Nebenfälle | uniform F+ beschreibend; weitere Pausen erst in einer späteren Runde |
