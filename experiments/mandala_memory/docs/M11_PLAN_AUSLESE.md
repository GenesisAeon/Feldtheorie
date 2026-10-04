# M11 – Die vorhandene Erinnerung besser auslesen: Versuchsplan, Fassung 2

**Status:** reviewbarer **Plan**. Kein Protokoll eingefroren, keine Referenzrechnung an Forschungsfällen, keine Forschungsrechnung.

**M10 bleibt unverändert:** Netze, Bedingungen, eingefrorener Code und Ergebnisse (`m10-freeze`).

**Fassung 2 berücksichtigt** `D:/mandala/mandala-memory-results/astra-m11-review/PLANREVIEW_49f94cf.md` (M11-R1 bis R4); die Übersicht steht am Ende.

**Leitfrage (Johann, 2026-10-04):** Wie viel der Lücke zur Bayes-Grenze lässt sich durch ein besseres Ausleseverfahren schließen, während das Mandala unverändert bleibt?

**Getrennt untersucht:**
- **Trainingsmenge:** Helfen mehr Beispiele Nearest-Mean und LDA?
- **Lernverfahren:** Hilft ein kleines nichtlineares Netz (einschließlich seines Trainings- und Validierungsverfahrens) bei gleicher Trainingsmenge?

**Referenz:** die Bayes-Grenze. Kennzeichnung: **[E]** Erkenntnis, **[H]** Hypothese, **[D]** beschreibende Diagnose, **[O]** Entscheidung.

## 1. Ausgangslage [E]

**Quelle der Bayes-Werte:**
- Datei: freigegebener M10-Forschungslauf `D:/mandala/mandala-memory-results/m10/research/m10-research-20261003T230058-47d41706.json`
- SHA-256 `db114706f10a335194ed5756d25470662f8780c5f9a877a8e67811c0594cb54d`
- d = 4, tanh, Aufgabe Bewahren

| Fall | acc_B (M10) | Standardfehler (Monte Carlo) | NM, 20 Seeds | LDA | Lücke NM | Lücke LDA |
|---|---|---|---|---|---|---|
| **modular, N** | 0,911582 | 8,9·10⁻⁵ (2·10⁶ Ziehungen) | 0,6346 | 0,7759 | 0,277 | 0,136 |
| uniform, F+ | 0,669634 | 7,8·10⁻⁵ | 0,6243 | 0,6669 | 0,045 | 0,003 |
| modular, K0 | 0,935176 | 0 (analytisch) | 0,9335 | 0,9335 | 0,002 | 0,002 |
| uniform, K0 | 0,669561 | 0 (analytisch) | 0,6672 | 0,6672 | 0,002 | 0,002 |

Die M10-Decoderwerte (je 1000 Trainingsepisoden je Klasse) sind **historische Schätzer**, keine M11-Referenzen. M11 zieht neue Trainings- und Testdaten. Es ist eine geplante Anschlussstudie an bekannten Fällen, keine Blindvalidierung.

## 2. Messgrößen und Referenzen

### 2.1 Exakte Populations-Trefferquote einer festen linearen Regel

Regel: Klasse B, wenn w·y + b > 0. Bei gleichen Klassenprioren und y = z(s,π) + ε mit ε ~ N(0, σ²I) gilt für **w ≠ 0**:

  acc(w, b) = ½ Σ_π P(π) [ Φ(−(w·z(A,π) + b)/(σ‖w‖)) + Φ((w·z(B,π) + b)/(σ‖w‖)) ]

**Für w = 0** ist die Regel konstant, und es gilt acc = ½. Das wird explizit so behandelt.

Die Formel liefert die Populations-Trefferquote ohne Test-Stichprobenrauschen; offen bleibt nur die numerische Auswertung von Φ. Für trainierte lineare Decoder wird sie exakt angewandt, eine Testmenge dient als Gegenprobe.

### 2.2 Referenzen

| Größe | Definition | Status |
|---|---|---|
| B | Bayes-Grenze: M10-Schätzer und sein Standardfehler (siehe 1) | übernommen, Monte-Carlo-unsicher |
| acc_NM(∞), acc_LDA(∞) | lineare Regeln aus den **wahren** Momenten der Klassenmischungen: μ_s = Σ_π P(π) z(s,π); gepoolte Kovarianz σ²I + ½ Σ_s Σ_π P(π)(z − μ_s)(z − μ_s)ᵀ; Schrumpfung 0; Schwelle in der Mitte; exakt nach 2.1 | Populationsgrenzwerte der **Lernkriterien**, keine Leistungsobergrenzen endlich trainierter Regeln |
| L_found | **numerische lineare Referenz:** beste gefundene lineare Regel (Optimierer in 2.3) | untere Schranke des unbekannten linearen Optimums L* |

### 2.3 Optimierer für L_found (vorab festgelegt, M11-R1)

- **Parametrisierung:** w = u/‖u‖ (Skalen-Mehrdeutigkeit entfernt), b frei. Ziel ist acc(w, b) aus 2.1.
- **Verfahren:** `scipy.optimize.minimize` (L-BFGS-B) auf −acc mit numerischem Gradienten; `gtol` = 1e‑10, `maxiter` = 2000.
- **Starts:**
  - die Populations-Regeln NM(∞) und LDA(∞);
  - 20 zufällige Richtungen aus einem festen Strom `m11-linref`, b jeweils in der Mitte der projizierten Klassenmittel.
- **Unverlierbare Kandidaten:** L_found = max über alle Endpunkte **und** über die unoptimierten Regeln NM(∞) und LDA(∞). Damit liegt L_found nie unter den bekannten linearen Regeln.
- **Berichtet werden:** alle Starts mit Endwert, die Spreizung der Endwerte und die Zahl der Starts innerhalb 10⁻⁴ des Besten.

### 2.4 Zerlegung: algebraisch richtig, kausal vorsichtig gelesen

  B − acc_D(n) = [B − L_found] + [L_found − acc_D(∞)] + [acc_D(∞) − acc_D(n)]

| Teil | Name | Lesart |
|---|---|---|
| B − L_found | **Abstand zur besten gefundenen linearen Regel** | **obere Schranke** der tatsächlichen Nichtlinearitätslücke B − L* (0 ≤ B − L* ≤ B − L_found), zuzüglich der Monte-Carlo-Unsicherheit von B. Kein Nachweis, dass nur nichtlineare Regeln den Abstand schließen können. Eine unvermeidbare Nichtlinearitätslücke wird nur behauptet, wenn eine belastbare obere Schranke für L* vorliegt; das ist in M11 nicht vorgesehen. |
| L_found − acc_D(∞) | **Kriteriumsabstand** | Abstand zwischen dem Populationsgrenzwert des Lernkriteriums (Mittelwerte bzw. Gauß-Annahme) und der besten gefundenen linearen Regel |
| acc_D(∞) − acc_D(n) | **Stichprobenabstand** | **vorzeichenbehaftet:** Einzelne trainierte Regeln können ihren Populationsgrenzwert übertreffen. Mehr Daten verbessern weder jeden Lauf noch zwingend monoton den Erwartungswert. |

## 3. Versuch

### Fest aus M10

- Netze (modular c = 1/4, uniform M = 1), tanh, σ = 0,02, Fenster W = 3, p = 0,5;
- Zustände aus dem eingefrorenen M10-Kern;
- d = 4, Aufgabe **Bewahren**.

### Fälle

| Fall | Rolle |
|---|---|
| **modular N** | Hauptfall |
| uniform F+ | Nebenfall |
| modular K0, uniform K0 | Kontrollen |

Keine weiteren Pausen (O5).

### Decoder

| Decoder | Beschreibung |
|---|---|
| Nearest-Mean | ohne Standardisierung |
| LDA | Ledoit-Wolf (beide wie M10) |
| **MLP** | 12 → 32 tanh → 1 (logistisch), siehe 3.2 |

### 3.1 Daten und Zufallsströme (M11-R3)

- **Seeds:** 20 Forschungs-Seeds, eigener Modus `m11`; Entwicklungs-Seeds getrennt.
- **Trainingsmengen:** **eine maximale Ziehung** je Seed und Fall mit 16 000 Paaren (Muster und Rauschen aus **getrennten** Strömen `pattern`/`noise`). n ∈ {250, 1000, 4000, 16000} sind **Präfixe** dieser Ziehung. Die Ströme hängen nicht von n ab, die Verschachtelung bleibt also erhalten.
- **Paare:** Jedes gezogene Muster wird für eine A- und eine B-Episode verwendet; ein Paar bleibt immer zusammen.
- **Testdaten für das MLP:** **je Seed ein unabhängiger Teststrom** mit 100 000 Paaren. Innerhalb eines Seeds ist er über n und Decoder gepaart (gleiche Testdaten), zwischen Seeds unabhängig.
- **Lineare Decoder:** exakt nach 2.1; Gegenprobe auf derselben Testmenge.

### 3.2 MLP-Lernverfahren (vorab festgelegte Regeln, M11-R3; Werte nach O1)

- **Budget:** Aus dem Trainingsbudget n werden **klassenstratifiziert 20 % der Paare** als Validierung abgetrennt (Paare gemeinsam). Gefittet wird auf den übrigen 80 %.
- **Standardisierung** nur mit Mittel und Streuung des Fit-Anteils.
- **Training:** Adam, volles Batch, L2-Regularisierung, frühes Stoppen nach Validierungs-Log-Loss mit fester Geduld und fester maximaler Epochenzahl.
- **Initialisierungen:** 3 aus dem Strom (Seed, `mlp-init`, n, k); gewählt wird die mit dem kleinsten **Validierungs**-Log-Loss. Die Regel ist für alle Fälle gleich.
- **Keine Anpassung** an Forschungsresultaten.

### 3.3 Unsicherheiten (getrennt behandelt, M11-R3)

| Quelle | Behandlung |
|---|---|
| **Trainingsziehung je Seed** | Seed-Ebene: gepaarte Seed-Differenzen, Bootstrap über ganze Seeds (2000 Wiederholungen, eigener Seed) |
| **MLP-Testschwankung** | steckt je Seed im MLP-Wert (100 000 Paare, SE ≈ 0,001) und wird über die Seed-Streuung mit erfasst; Testströme sind über Seeds unabhängig |
| **Bayes-Standardfehler** (übernommen) | gemeinsam für alle Seeds, im Seed-Bootstrap **nicht** enthalten. Bei absoluten Lücken und geschlossenen Anteilen wird er **separat ausgewiesen**, nicht verrechnet. Für C-Daten und C-Modell hebt sich B heraus. |

## 4. Hypothesen und Diagnosen

### Bestätigende Kontraste (Hauptfall modular N; einseitig; δ = 0,01; Holm α = 0,05)

| | Frage | Kontrast |
|---|---|---|
| **C-Daten** | Helfen mehr Beispiele **LDA**? | acc_LDA(16000) − acc_LDA(1000) > δ |
| **C-Modell** | Ist das **MLP-Lernverfahren** (Netz, Optimierung, Validierung) bei 1000 Beispielen besser als LDA? | acc_MLP(1000) − acc_LDA(1000) > δ |

**Testverfahren:**
- **Daten:** gepaarte Seed-Differenzen (gleiche Trainingsziehung je Seed).
- **Statistik:** einseitiger t-Test auf (Mittel − δ) mit 19 Freiheitsgraden.
- **Annahmen:** Die näherungsweise Normalverteilung der Seed-Differenzen ist eine **Annahme**, keine bewiesene Kalibrierung. Bootstrap-Intervalle werden daneben berichtet.
- **Nullvarianz-Regel:** Bei Seed-Streuung 0 gilt p = 0, wenn die mittlere Differenz > δ ist, sonst p = 1.
- **Holm:** über beide Kontraste; berichtet werden die adjustierten p-Werte.
- **Wortregeln wie M10:** „bestätigt“ oder „nicht bestätigt“; „Richtung widerspricht“ nur, wenn das unadjustierte 95-%-Intervall ganz unter 0 liegt.

**Was C-Modell bedeutet (M11-R2):** Ein bestätigtes C-Modell zeigt, dass **dieses Lernverfahren** besser abliest als LDA. Es belegt **nicht**, dass Nichtlinearität notwendig ist; ein MLP kann LDA auch dann übertreffen, wenn das lineare Optimum B bereits erreicht.

### Erwartungen und beschreibende Diagnosen (keine deterministischen Vorhersagen, M11-R2)

- **[D] Konvergenz:** |Mittel über Seeds von acc_D(16000) − acc_D(∞)| ≤ 0,01 für NM und LDA, berichtet mit Bootstrap-Intervall. Das ist eine empirische Konvergenzdiagnose ohne einseitige Forderung.
- **[H qualitativ] Erwartung aus M10:** Mehr Daten werden LDA wenig helfen, weil die M10-Werte bei n = 1000 bereits stabil wirken (sd 0,006). Das ist eine qualitative Erwartung auf Basis historischer Schätzer und keine Prüfung.
- **[D]** Zerlegung nach 2.4 für NM und LDA bei allen n, mit den Lesarten aus 2.4.
- **[D] Geschlossener Anteil** = (Mittel acc_D(n) − Mittel acc_LDA(1000)) / (B − Mittel acc_LDA(1000)), als **Quotient der Seed-Mittel**.
  - Intervall aus einem gemeinsamen gepaarten Bootstrap über Seeds; der Bayes-SE wird separat genannt.
  - Ist der Nenner ≤ 0,01, wird der Anteil nicht berichtet (N/A).
- **[D] Kontrollen K0:** Hier ist die Bayes-Regel linear. Erwartet wird L_found ≈ B, und bei großem n soll kein Decoder um mehr als δ unter B liegen. Eine Abweichung ist ein Diagnosebefund.
- **[D] MLP-Lernkurve** über n.

## 5. Reihenfolge (M11-R4)

1. **Plan festlegen** (diese Fassung nach Review): Referenzverfahren und Optimierer (2.2/2.3), Auswahlregeln des MLP (3.2), Hypothesen und Tests (4).
2. **Code und Tests** an **Entwicklungsbedingungen** (M10-Entwicklungsorte Fdev/Ndev, Entwicklungs-Seeds); dort auch die MLP-Hyperparameter festlegen (O1); Laufzeitcheck. Danach **Implementierungsreview**.
3. **Referenzverfahren und Studienentscheidungen versionieren** (Commit), **dann erst** die Referenzen an den Forschungsfällen **einmal berechnen**: acc_NM(∞), acc_LDA(∞) und L_found mit allen Starts. Dokumentiert als **modellbasierte Referenzphase**. Danach werden **keine** Hypothesen, Hyperparameter, Fälle oder Trainingsmengen mehr anhand dieser Werte gewählt oder geändert.
4. **Einfrieren:** Referenzartefakte, endgültiges Protokoll (mit YAML- und MD-Zwilling) und Code mit Freeze-Datensatz (Protokoll-Hash, geprüfter Code-Commit, Code-Prüfsummen). Danach Smoke-Lauf und eine einmalige Trainings- und Auswertungsrunde über ein Freigabe-Gate wie in M10.

## 6. Kontrollen und Prüfwerkzeuge (Schritt 2)

- **Formel 2.1:**
  - gegen Φ(‖Δ‖/2σ) im 1-Komponenten-Fall;
  - gegen eine große Monte-Carlo-Testmenge an Mischungen;
  - w = 0 ergibt ½.
- **Populationsregeln:** gegen trainierte Regeln bei sehr großem n (Entwicklungsbedingungen).
- **Optimierer:** Er findet an einem konstruierten Fall mit bekanntem linearem Optimum das Optimum. L_found ist nie kleiner als NM(∞) und LDA(∞).
- **MLP:**
  - Gradientenprüfung mit finiten Differenzen;
  - deterministisch je Seed;
  - Standardisierung nur aus dem Fit-Anteil;
  - Validierung klassenstratifiziert, Paare zusammen;
  - an K0-Entwicklungsfällen nahe B bei großem n.
- **Daten:** Präfixe verschachtelt (die Ziehung für n = 250 ist Präfix der für 16 000); Testströme je Seed unabhängig, Trainings- und Teststrom disjunkt.
- **Gate:** Raster aus dem Protokoll, exakte n, Ströme, Kontrollen, kooperative Zeitgrenze, exklusive Ablage auf D:.

## 7. Ressourcen (im Laufzeitcheck zu bestätigen, M11-R4)

| Teil | Umfang |
|---|---|
| MLP | 20 Seeds × 4 n × 4 Fälle × 3 Initialisierungen = **960 MLP-Trainings**, bis 25 600 Fit-Beispiele, Bewertung der 320 ausgewählten Modelle auf je 200 000 Testepisoden |
| Lineare Decoder | 320 Fits, exakte Bewertung |
| Referenzen | 4 Fälle × 22 Starts L-BFGS-B über 13 Parameter |

- **Ziel:** < 15 min, harte Grenze 30 min (kooperativ geprüft); RAM < 1 GiB.
- Liegt der Laufzeitcheck darüber, wird **vor** dem Freeze entschieden, nicht während der Forschungsrunde.

## 8. Grenzen

- **Synthetische Modellstudie** mit zwei festen Netzen und bekannten M10-Fällen.
- **Ein nichtlineares Lernverfahren**, feste Hyperparameter.
- **L_found** ist eine untere Schranke des linearen Optimums; B − L_found ist eine obere Schranke der Nichtlinearitätslücke.
- **Exakt bewertet** werden nur lineare Regeln; MLP-Werte sind empirisch.
- **Keine biologische oder allgemeine KI-Aussage.**

## 9. Entscheidungen

| # | Frage | Stand |
|---|---|---|
| O1 | MLP | 12 → 32 → 1 tanh als Ausgangspunkt. Epochen, Lernrate, L2, Geduld werden **nur an Entwicklungsbedingungen** festgelegt und vor der Referenzphase versioniert. |
| O2 | Bestätigend | C-Daten (LDA) und C-Modell (MLP-Verfahren gegen LDA), δ = 0,01, Holm |
| O3 | Konvergenztoleranz | 0,01, **beschreibend**, kein Bestehensversprechen |
| O4 | Trainingsmengen | 250 / 1000 / 4000 / 16000 je Klasse |
| O5 | Fälle | Hauptfall, Nebenfall uniform F+, K0-Kontrollen; keine weiteren Pausen |

## Änderungen gegenüber Fassung 1 (Review M11-R1 bis R4)

| Punkt | Änderung |
|---|---|
| R1 | L_found als **numerische lineare Referenz** (untere Schranke von L*); B − L_found als **obere Schranke** der Nichtlinearitätslücke; w = 0 ⇒ ½; Optimierer vorab festgelegt (Parametrisierung, Starts, Abbruch, unverlierbare Kandidaten NM(∞)/LDA(∞)) |
| R2 | Stichprobenabstand vorzeichenbehaftet; V1 als beschreibende Konvergenzdiagnose; V2 als qualitative Erwartung aus M10, nicht deterministisch geprüft; V3 entfällt. C-Daten heißt „Helfen mehr Beispiele LDA?“; C-Modell vergleicht das MLP-Lernverfahren mit LDA, nicht isoliert die Modellklasse. |
| R3 | eine maximale Ziehung je Seed mit n-Präfixen und getrennten Muster- und Rauschströmen; MLP-Validierung stratifiziert mit Paaren zusammen; Standardisierung nur aus dem Fit-Anteil; feste Initialisierungs- und Auswahlregel; Teststrom je Seed unabhängig; t-Annahme benannt; Nullvarianz-Regel und Holm-adjustierte p; Bayes-SE separat; geschlossener Anteil als Quotient der Mittel mit N/A-Regel |
| R4 | ausdrückliche Reihenfolge: Verfahren festlegen → Entwicklung und Implementierungsreview → Verfahren versionieren → Referenzen einmal berechnen (modellbasierte Referenzphase, keine Auswahl danach) → Freeze → Smoke → einmalige Runde; M10-Bayes-Werte mit Datei, SHA, Fall und SE referenziert |
