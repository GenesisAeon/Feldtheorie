# M12: Robustheit des festgehaltenen Auslesens (Plan, Fassung 2)

**Status:** nur Plan. Nichts gerechnet, nichts eingefroren, nichts trainiert. Auftrag: Johann/Astra, 2026-10-05.

**Fassung 2:** Präzisiert nach `PLANREVIEW_2a07ae4` (M12-R1 bis R4). Johann/Astra haben die Vorschläge O1–O5 angenommen (§ 12).

**Leitfrage:** Wie verändert sich die Ausleseleistung bei anderer Ablenkungsstärke oder anderem Messrauschen, wenn die trainierten Decoder unverändert bleiben?

**Einordnung:**
- M12 ist eine **Anschlussstudie** mit **neuen Basismodellen**. Es sind keine rekonstruierten M11-Modelle; M11 hat keine Gewichte gespeichert, siehe [Forschungsübersicht](FORSCHUNGSUEBERSICHT.md).
- M10 und M11 bleiben unverändert: Code, Protokolle, Freezes und Daten.
- M12 ruft eingefrorene Funktionen nur auf und ändert sie nicht.

## 1 Umfang

| Festgelegt | Wert | Herkunft |
|---|---|---|
| Netz | modular (M = 3, c = 1/4), tanh, N = 12, γ = 0,8, ℓ = 0,5, Reizamplitude 0,6 | M10-Protokoll (eingefroren) |
| Ablenkung | „nah“ (N): Orte X = 1, Y = 5, Fenster W = 3 direkt vor dem Ablesen, Pulswahrscheinlichkeit 0,5, 27 Muster | M10-Protokoll |
| Pause | d = 4 | M10/M11-Hauptfall |
| Ausgangsbedingung c₀ | Ablenkungsamplitude a_D = 0,6, σ = 0,02 | M10-Bedingung N |
| Decoder | MLP und LDA (Ledoit-Wolf); NM entfällt | Auftrag |

## 2 Basismodelle (Training nur in c₀)

- **Architektur und Lernverfahren:** aus M11 übernommen, ohne neue Hyperparametersuche.
  - Die Hyperparameter werden **per Hash** aus dem eingefrorenen M11-Protokoll gelesen (`c25c9cdd…`), nicht abgetippt: 12→32 tanh→1, Adam, BCE + L2, lr 0,03, l2 10⁻³, patience 100, max. 3000 Epochen, 3 Initialisierungen.
  - Validierung ist jedes 5. Paar; die Standardisierung kommt nur aus dem Fit-Teil.
  - Eine Initialisierung wird nach dem kleinsten Validierungsverlust auf c₀ gewählt, bei Gleichstand der kleinste Index.
  - Dass diese Hyperparameter in M11 am Rand des Entwicklungsrasters lagen, bleibt als bekannte Einschränkung bestehen.
- **Trainingsgröße n = 16 000 Paare** (O1, angenommen):
  - Das ist der M11-Punkt, an dem das MLP den größten Teil der Lücke schloss (rund 84 %) und die Seed-Streuung am kleinsten war.
  - Die Robustheitsfrage betrifft ein gut trainiertes Auslesen.
  - LDA wird auf denselben 16 000 Paaren trainiert.
- **Seeds (neu, disjunkt zu M11):**

  | Zweck | Seeds |
  |---|---|
  | Forschung | 41201–41220 (20 Modelle je Decoder) |
  | Smoke | 41051–41052 |
  | Entwicklung | 921–923 |

  M11 nutzte 41101–41120, 41001–41002 und 901–903.
- **Zufallsströme:**
  - Eigene Modi `m12` und `m12dev` sowie `m12bayes`, nach derselben Konstruktion wie M11: `SeedSequence((seed, Modus, crc32(Namen)…))`.
  - Ein eigenes Modul ist nötig, weil `m11_readout.fit_mlp` fest an die M11-Modi gebunden ist und eingefroren bleibt.
  - Der M12-Wrapper verwendet `MLP` und `validation_split` aus `m11_readout` **unverändert**. Seine Gleichwertigkeit mit `fit_mlp` wird getestet: gleiche Eingaben und Ströme ergeben bitgleiche Gewichte.
- **Trainingsdaten:** Sie stammen nur aus c₀. Der Trainingscode hat keinen Zugriff auf das Verschiebungsraster; das wird strukturell und per Test geprüft.

## 3 Modellartefakte und Fixierung

**Inhalt je Seed:**
- LDA: `w` und `b`;
- MLP: `W1`, `b1`, `w2`, `b2`, `mean` und `std` der Standardisierung;
- Fit-Metadaten aller drei Initialisierungen: Ströme, Validierungsverlust und Epochen, dazu der Index der gewählten Initialisierung;
- Herkunft: Seed, Stream-Schlüssel, Protokoll-SHA, Code-Hashes und M11-Hyperparameter-Hash.

**Format:**
- Pro Seed eine `.npz` (float64) und eine `.json`.
- Ein Manifest mit dem SHA-256 jeder Datei.
- Alles wird exklusiv geschrieben. Die Größe liegt insgesamt unter 1 MB, deshalb werden die Artefakte im Repo versioniert.

**Fixierung:**
- Ein Modell-Freeze-Datensatz bindet die Artefakte über den Manifest-Hash und den Protokoll-Hash. Er bindet außerdem den Hash des Referenz-Artefakts (§ 5) und die Code-Hashes. Der Commit bekommt den Tag `m12-models`.
- Danach wird weder nachtrainiert noch nach verschobenen Testdaten ausgewählt.
- Die Robustheitsauswertung lädt nur Artefakte und prüft ihre Hashes. Ruft sie ein Fit auf, scheitert sie; ein Test patcht dafür `MLP.fit` und `lda_rule` so, dass sie eine Ausnahme werfen.

**Vollständige Prüfbarkeit (M12-R4):**
- **Laden:**
  - NPZ wird ohne Pickle geladen (`allow_pickle=False`).
  - Geprüft werden die exakten Schlüssel, die Formen (W1 12×32, b1 32, w2 32, b2 1, mean 12, std 12, w 12, b 1) und der Typ float64.
  - Alle Werte müssen endlich sein, alle `std` größer 0.
  - Die Pflichtmetadaten müssen vollständig sein: Seed, Stream-Schlüssel aller Initialisierungen, gewählte Initialisierung, Hyperparameter-Hash, Protokoll-Hash, Code-Hashes und Trainingsgröße.
- **Manifest:**
  - Es muss **genau** die 20 Forschungs-Seeds des Protokolls enthalten, je Seed genau die vorgesehenen Dateien.
  - Ein Hash-Abgleich mit irgendeinem Manifest genügt nicht.
- **Roundtrip-Test:**
  - Gespeicherte und frisch geladene Modelle liefern auf festgelegten Entwicklungseingaben bitgleiche Scores und Vorhersagen (MLP-Logits, LDA-Werte w·y + b).
  - Dasselbe gilt für das Modell im Speicher direkt nach dem Training.
- **Unverändert:**
  - Die Auswertung prüft die Hashes aller Modelldateien vor und nach dem Lauf.
  - Sie vergleicht die geladene Standardisierung und die Gewichte nach der Auswertung mit einer Kopie.
- **Smoke-Artefakte:**
  - Sie liegen getrennt im Ergebnisordner, nicht im Repo, mit eigenem vollständigem Manifest (Modus `smoke`).
  - Damit wird Speichern und Laden geprüft.
  - Das Forschungs-Gate weist ein Smoke-Manifest immer ab.
- **Wrapper-Bitgleichheitstest:** Er nutzt absichtlich dieselben (M11-)Testströme wie `fit_mlp`. Die produktiven M12-Ströme bleiben von M11 getrennt.

## 4 Verschiebungen (vorab fest, einzeln verändert)

| Achse | Werte (× Ausgangswert) | übrige Größe |
|---|---|---|
| Ablenkungsamplitude a_D | 0,30 · 0,45 · **0,60** · 0,75 · 0,90 (×0,5 … ×1,5) | σ = 0,02 |
| Messrauschen σ | 0,010 · 0,015 · **0,020** · 0,025 · 0,030 (×0,5 … ×1,5) | a_D = 0,6 |

Das ergibt **9 Testbedingungen**, mit c₀ gemeinsam. Fenster, Orte, Pulswahrscheinlichkeit und Pause bleiben gleich. Die Zustände z(c) entstehen über die eingefrorenen Funktionen `m10_task.network(…, condition={X:1, Y:5, amplitude:a_D})` und `readout_states(…, d=4, …)`. Das Mandala selbst bleibt unverändert.

## 5 Testdaten und Referenzen

- **Testepisoden:**
  - 100 000 Paare je Seed und Bedingung (O4, angenommen), aus einem eigenen Teststrom getrennt vom Training.
  - **Gemeinsame Zufallszahlen über alle 9 Bedingungen:** dieselben Musterindizes und dasselbe standardnormale Rauschen ε; y = z(c) + σ(c)·ε.
  - Verluste gegenüber c₀ sind dadurch innerhalb eines Seeds gepaart.
  - MLP und LDA werden auf denselben Episoden gemessen.
- **LDA exakt:** Für die festgehaltene Regel (w, b) wird die Populationsgenauigkeit in jeder Bedingung exakt mit `exact_accuracy(w, b, z(c), P, σ(c))` berechnet, ohne Teststichprobe. Die Testgenauigkeit wird zusätzlich berichtet.
- **Bayes-Referenz B(c) je Bedingung:**
  - Berechnet mit den eingefrorenen Funktionen `m10_bayes.preserve_mixtures` und `bayes_accuracy_mc`.
  - n_MC = 2·10⁶ in Blöcken zu 50 000, ein unabhängiger Strom je Schätzung; der Standardfehler wird berichtet.
  - Kontrolle: B(c₀) muss mit dem M10-Forschungswert 0,9116 innerhalb von 4 kombinierten SE übereinstimmen (gleicher Zustand, gleiches σ, anderer MC-Strom).
- **Angepasste lineare Referenz LDA_pop(c):** die Populations-LDA für die Bedingung c, exakt über `population_rules`. Sie ist kein trainiertes Modell und braucht deshalb kein Nachtrainieren.
- **B(c₀) wird genau einmal berechnet** und für alle Kontraste wiederverwendet.
- **Referenzphase:**
  - B(c) und LDA_pop(c) hängen nicht von den Modellen ab. Sie werden **nach dem Protokoll-Freeze und vor dem Forschungstraining** einmalig berechnet, mit Claim-Sperre wie in M11.
  - Das Ergebnis ist ein eigenes, unveränderliches Referenz-Artefakt mit eigenem Hash. Es enthält den Protokoll-Hash, gegen den es gerechnet wurde.
  - Dieser Hash wird im Modell-Freeze und im Auswertungs-Gate gebunden.
  - Der ursprüngliche Protokoll-Hash wird nicht nachträglich auf sich selbst bezogen: Das Protokoll ändert sich nach dem Freeze nicht; die Bindung läuft über den Freeze-Datensatz.

## 6 Auswertung

Für Decoder D, Seed s und Bedingung c (Vorzeichen: positiv heißt schlechter als in c₀):

| Größe | Formel | Bedeutung |
|---|---|---|
| absolute Leistung | acc_D,s(c) | wird immer berichtet |
| Verlust | L_D,s(c) = acc_D,s(c₀) − acc_D,s(c) | negativ = Gewinn |
| Informationsänderung | ΔB(c) = B(c₀) − B(c) | Wird die Information im Zustand schlechter trennbar? |
| Lückenänderung | ΔG_D,s(c) = [B(c) − acc_D,s(c)] − [B(c₀) − acc_D,s(c₀)] | Kommt der festgehaltene Decoder schlechter zurecht? |

**Identität:** L = ΔB + ΔG, exakt bei gleichen B-Schätzungen; ein Test prüft das.

**ΔG beschreibt eine Veränderung des Bayes-Abstands, nicht eindeutig deren Ursache.**

**Nur für LDA** wird ΔG weiter zerlegt. Beide Terme sind vorzeichenbehaftet; die Zerlegung ist algebraisch exakt.
- **Änderung des Bayes-Abstands der bedingungsspezifischen Populations-LDA:** [B − LDA_pop](c) − [B − LDA_pop](c₀).
  - Die Populations-LDA ist die Populationsregel des LDA-Kriteriums, **nicht** die beste lineare Regel.
  - Der Term mischt deshalb eine mögliche Beschränkung linearer Regeln mit dem Abstand des LDA-Kriteriums.
  - Eine globale lineare Optimierung je Bedingung ist nicht vorgesehen.
- **Änderung des Leistungsabstands der fixierten LDA zur bedingungsspezifischen Populations-LDA:** [LDA_pop − LDA_fix](c) − [LDA_pop − LDA_fix](c₀).
  - Der Term enthält die endliche Schätzung des fixierten Ausgangsmodells.
  - Er ist deshalb **kein** isolierter reiner Fehlanpassungseffekt.

**Für das MLP** gibt es ohne Nachtrainieren keine bedingungsspezifische Referenz. ΔG_MLP kann die Beschränkung der Modellklasse, die Fehlanpassung an die neue Bedingung, endliche Trainingsdaten sowie Optimierung und Regularisierung mischen. All das gehört zum konkreten Lernverfahren und wird nicht aufgelöst.

**Unsicherheit (M12-R3):**
- **Größen mit Seed-Bezug** (acc, L, ΔG und der MLP-LDA-Vorteil):
  - Mittel über 20 Seeds mit unadjustierten 95 %-t-Intervallen.
  - Zusätzlich ein gepaarter Bootstrap über ganze Seeds: 2000 Wiederholungen, fester Bootstrap-Seed.
  - Die Test-Stichprobenstreuung steckt in der Streuung zwischen den Seeds.
  - Die Intervalle für ΔG sind **bedingt auf die festen Bayes-Schätzungen**. Daneben steht der zusätzliche MC-SE der Bayes-Differenz.
- **ΔB hat keine Seed-Streuung,** denn es ist eine MC-Schätzung eines festen Modellwerts. Aus 20 Wiederholungen desselben ΔB wird **kein** t- oder Bootstrap-Intervall gebildet. Berichtet wird der Schätzwert mit seinem MC-SE:
  - c ≠ c₀ (unabhängige Ströme): SE_MC(ΔB) = √(SE_B(c₀)² + SE_B(c)²);
  - c = c₀: ΔB = 0 exakt, ohne Unsicherheit.
  - Weil alle Kontraste denselben Ausgangswert B(c₀) teilen, sind ihre MC-Fehler **korreliert**. Das wird ausgewiesen.
- **Identität:** L = ΔB + ΔG verwendet dieselben gespeicherten B-Werte; deren MC-Fehler heben sich in der Summe auf.
- **Standardfehler einer Testgenauigkeit:**
  - Er wird aus den **Paarbeiträgen** bestimmt: r_i = (1[A_i richtig] + 1[B_i richtig])/2 und SE = sd(r)/√n_Paare.
  - A und B eines Paares teilen das Ablenkungsmuster und sind deshalb keine 2·10⁵ unabhängigen Bernoulli-Beobachtungen.

**Konfirmatorisch (O3, angenommen, M12-R2):**
- **Frage:** Ist das fixierte MLP an den beiden **erhöhten Endpunkten** um mehr als 0,01 besser als die fixierte LDA?
  - **R-a:** acc_MLP − acc_LDA > δ bei a_D = 0,9 (σ = 0,02).
  - **R-σ:** dasselbe bei σ = 0,03 (a_D = 0,6).
  - Beide Decoder werden auf denselben Testepisoden gemessen, beide Werte als Testgenauigkeit, damit es ein gepaarter Vergleich ist.
- **Was nicht getestet wird:** weder Nichtunterlegenheit gegenüber c₀ noch die Erhaltung der Größe des Ausgangsvorteils. Ein Vorteil kann schrumpfen und trotzdem bestehen.
- **Begründung der erhöhten Endpunkte, vorab:**
  - Mehr Ablenkung und mehr Rauschen sind die Richtungen, in denen eine Verschlechterung des Auslesens praktisch zu erwarten ist und die Robustheit zählt.
  - Für σ lässt die optimale Trefferquote analytisch nicht zu (§ 9). Für a_D macht M10 eine stärkere Störung im modularen Netz plausibel.
  - Die halbierten Werte liegen gleich weit von c₀ entfernt und werden vollständig beschreibend berichtet.
  - Eine Monotonie der Decoderverluste wird **nicht** vorausgesetzt.
  - Es gibt keine nachträgliche Auswahl von Endpunkten.
- **Verfahren:** δ = 0,01, einseitiger t-Test mit df = 19, Holm über beide Tests, Nullvarianz-Regel wie in M11.
- **Formulierung:** „Nicht bestätigt“ heißt nur, dass das Kriterium nicht erfüllt ist; weitere Aussagen nur mit Intervall.
- **Alles Übrige ist beschreibend.** Dazu gehören die Verlustkurven, die Zerlegung und die Änderung des MLP-LDA-Vorteils gegenüber c₀. Eine weitere konfirmatorische Familie gibt es nicht.

## 7 Reihenfolge (Phasen)

1. **Plan:** dieses Dokument, dann Review.
2. **Implementierung an Entwicklungsbedingungen:**
   - Module `m12_models.py` (Training, Artefakte, Hash-Prüfung), `m12_references.py`, `m12_robust.py` (Auswertung ohne Fit) und `m12_evaluate.py` (Gate, Zerlegung, Statistik).
   - Tests und Mutationsprüfung, Laufzeitcheck, danach Implementierungsreview.
3. **Protokoll-Freeze** (Tag `m12-freeze`) **vor dem Forschungstraining.**
   - Er enthält das Raster, die Seeds, n, den Hyperparameter-Hash, die Auswahl-, Ausschluss-, Diagnose- und Freigaberegeln, das Budget und die Code-Hashes.
   - Entwicklungs- und Werkzeugtests trainieren vorher nur auf Entwicklungseinstellungen (Seeds 921–923, Modus `m12dev`).
4. **Referenzphase,** einmalig: B(c) und LDA_pop(c) für alle 9 Bedingungen. Das Referenz-Artefakt bekommt einen eigenen Hash, sein Commit kommt vor dem Training.
5. **Smoke:** Smoke-Modelle trainieren und auswerten, als Integrationsprüfung. Sie werden nicht freigegeben und nicht interpretiert.
6. **Trainingsphase,** einmalig: 20 Forschungsmodelle je Decoder.
   - Trainiert wird nur in c₀; ausgewählt wird nur die Initialisierung, auf der c₀-Validierung.
   - Es werden keine Testgenauigkeiten berechnet, schon gar nicht zur Auswahl.
7. **Modell-Freeze** (Tag `m12-models`): Artefakte, Manifest und Freeze-Datensatz, sonst keine Änderung.
   - Der Freeze-Datensatz bindet den Protokoll-Hash, den Referenz-Hash, den Manifest-Hash und die Code-Hashes.
   - Die Konsistenz wird in einem frischen Prozess geprüft, einschließlich Laden und Roundtrip.
8. **Robustheitsauswertung,** einmalig, danach Ergebnisbericht, Review und Integration.

**Versuchsregel (aus M11 gelernt):**
- Jede einmalige Phase hat genau einen Forschungsversuch.
- Ein Abbruch wird gespeichert, gesperrt und berichtet.
- Ein zweiter Versuch braucht einen datierten Nachtrag und eine dokumentierte Freigabe.
- Phasen über 10 min laufen als eigenständiger Prozess mit blockiertem Ruhezustand.

## 8 Auswahl-, Ausschluss- und Freigaberegeln

- **Auswahl:** nur die Initialisierungswahl des MLP, auf der Validierung in c₀. Für LDA gibt es keine Auswahl. Es werden keine Modelle ausgeschlossen; alle 20 werden berichtet.
- **Ausfall:** Divergiert ein Modell oder bricht das Training ab, gilt die Phase als `failed` bzw. `aborted`. Es gibt keinen Ersatz-Seed und kein stilles Wiederholen.
- **Freigabe-Gate der Auswertung** (alle Bedingungen müssen gelten):
  - Modus `research`, Status `complete`, keine Fehler, keine Overrides;
  - Seeds gleich dem Protokoll; vollständiges Raster aus 20 × 9 × 2 Zeilen; alle Werte endlich;
  - Protokoll, Code, Referenz-Artefakt und Modell-Manifest gleich ihren Freeze-Hashes; jedes Artefakt mit passender Herkunft und erfolgreich geladen (§ 3);
  - Modelldateien vor und nach der Auswertung hashgleich;
  - Auswertung ohne Fit-Aufruf, laut Lauf-Metadaten und Code-Hash;
  - Teststrom vom Trainingsstrom getrennt.

**Statistische Diagnosen (M12-R3), vorab festgelegt:**
- **Art der Prüfung:** Die Diagnosen sind Gegenproben, keine Beweise. Ein einzelner 4-SE-Verstoß ist **kein** sicherer Codefehler.
- **Alarmregel:**
  - Jeder Alarm wird im Ergebnis vermerkt. Die konfirmatorische Freigabe ruht dann bis zu einer dokumentierten Prüfung durch Johann/Astra.
  - Es gibt **keine** Wiederholung, bis eine Diagnose besteht.
- **Fehlalarme:** Bei 4 SE erwarten wir über alle Diagnosen zusammen deutlich unter 1 Fehlalarm.

| Diagnose | Anzahl | Toleranz |
|---|---|---|
| D1 Reproduktion: B(c₀) gegen M10-Forschungswert | 1 | \|Δ\| ≤ 4·√(SE² + SE²) |
| D2 Keine Zunahme mit σ: B(σ_{k+1}) ≤ B(σ_k) + 4·√(SE² + SE²) für benachbarte σ | 4 | wie angegeben |
| D3 LDA_pop(c) ≤ B(c) + 4·SE_B(c) | 9 | wie angegeben |
| D4 exakte LDA gegen Test-LDA je Seed und Bedingung | 180 | \|Δ\| ≤ 4·SE (aus Paarbeiträgen) |

**Analytisch** (getrennt von D2): Zusätzliches unabhängiges Gauß-Rauschen ist eine Verrauschung der Beobachtung. Die optimale Trefferquote kann dadurch **nicht zunehmen**. Eine **strenge** Abnahme bräuchte weitere Voraussetzungen und wird nicht behauptet.

## 9 Pflichtprüfungen der Implementierung (Auswahl, inklusive Negativkontrollen)

| Prüfung | Was sie sicherstellt |
|---|---|
| Wrapper-Gleichwertigkeit | Gleiche Daten und Ströme ergeben dieselben Gewichte wie `m11_readout.fit_mlp`. |
| Verlusteigenschaften | Die Identität L = ΔB + ΔG gilt. In c₀ sind alle Verluste exakt 0. |
| Gepaarte Testepisoden | Die Testepisoden sind über die Bedingungen gepaart, mit identischem ε und identischen Mustern. |
| Laden und Roundtrip | Ohne Pickle; Schlüssel, Formen, Typ, Endlichkeit, std > 0 und Pflichtmetadaten werden geprüft; genau 20 Seeds. Scores sind bitgleich vor dem Speichern, nach dem Laden und im Speicher. |
| Auswertung ändert nichts | Modell-Hashes vorher gleich nachher; Gewichte und Standardisierung unverändert. |
| Getrennte Artefakte | Ein Smoke-Manifest wird vom Forschungs-Gate abgewiesen. |
| ΔB in c₀ | ΔB(c₀) ist exakt 0 mit SE 0. B(c₀) wird nur einmal berechnet. |
| Paar-SE | Der Standardfehler kommt aus Paarbeiträgen und stimmt mit einer unabhängigen Nachrechnung überein. |
| Rauschskalierung | σ(c) skaliert das Rauschen exakt. |
| LDA exakt gegen Test | Die exakte LDA-Genauigkeit stimmt mit der Testgenauigkeit innerhalb von 4 SE überein. |
| Manipuliertes Artefakt | Ein geändertes Byte oder eine fehlende Datei wird abgewiesen. |
| Auswahl auf verschobenen Daten | Ein Versuch, auf verschobenen Daten auszuwählen oder zu trainieren, scheitert. |
| Herkunftsfehler | Falsche Seeds oder Ströme in der Herkunft werden abgewiesen. |
| Gate | Lehnt Smoke-Läufe, unvollständige Läufe und Overrides ab. |
| Ausgaben | Referenz und Artefakte werden exklusiv geschrieben; Ausgaben auf C: werden verweigert. |
| Eingefrorene Dateien | M10- und M11-Dateien bleiben unverändert (Hash-Test). |
| Diagnosen | Werden als Diagnosen mit Alarmregel geführt; ein künstlicher Alarm sperrt die konfirmatorische Freigabe und löst keine Wiederholung aus. |

## 10 Ressourcenbudget (Schätzung, wird im Laufzeitcheck gemessen)

| Phase | Schätzung | vorgeschlagene Grenze |
|---|---|---|
| Referenz (9 × B mit 2·10⁶ MC, 9 × LDA_pop) | wenige Minuten | 1800 s |
| Training, n = 16 000 | **wird an Entwicklungseinstellungen im tatsächlichen M12-Umfang gemessen**, einschließlich Schreiben und Laden der Artefakte. Anhaltspunkt: Im M11-Forschungslauf (Versuch 2) lag die Laufzeitangabe für modular_N bei n = 16 000 im Mittel bei etwa 129 s je Modell mit 3 Initialisierungen, also etwa 43 min für 20 Seeds. *Berichtigt nach M12-R4:* Die früher genannten 169 s waren über vier Entwicklungsfälle summiert. | 5400 s (konservativ) |
| Robustheitsauswertung (20 × 9 × 2·10⁵ Episoden, exakte LDA) | unter 5 min | 1800 s |
| RAM | unter 1 GiB (M11-Spitze 264 MiB) | 2 GiB als Planwert; **gemessen und berichtet, nicht technisch durchgesetzt** |
| Speicher | Artefakte unter 1 MB, Ergebnisse unter 50 MB; alles auf D: | – |

## 11 Was nicht behauptet wird

- **Bereich:** nur dieses Netz, diese Ablenkung, d = 4 und die 9 Bedingungen. Keine Aussage zwischen oder außerhalb der Rasterpunkte und keine allgemeine Robustheit.
- **Kein Vergleich mit nachtrainierten Modellen.** Beim MLP bleibt die Ursache einer Lückenänderung (Modellklasse gegen Fehlanpassung) offen.
- **M11-Bezug:** Neue Basismodelle sind eine neue Stichprobe. Ihre Ausgangswerte sind mit M11 vergleichbar, aber keine Wiederholung von M11.
- **Synthetische Seeds**, keine biologische Aussage und keine Gewinnerbehauptung.

## 12 Offene Entscheidungen

Johann/Astra haben am 2026-10-05 alle Vorschläge angenommen.

| | Frage | Entscheidung |
|---|---|---|
| O1 | Trainingsgröße | n = 16 000 |
| O2 | Raster | ×{0,5; 0,75; 1; 1,25; 1,5} je Achse |
| O3 | Konfirmatorische Familie | R-a und R-σ, mit der präzisierten Frage aus M12-R2 |
| O4 | Testpaare je Seed und Bedingung | 100 000 |
| O5 | Zusätzlicher Ankerpunkt ohne Ablenkung | nein |
