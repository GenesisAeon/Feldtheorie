# LR4 – Ridge und Evaluation (Bericht)

**Stand:** 2026-10-08, Branch `lantern-reconstruction`. Teil 1 ist `027fc0c`: Code, Tests und die Gate-Definition, festgelegt **vor** dem Lauf. Teil 2 enthält das Gate-Ergebnis und die Dokumentation.

Es gab keine Forschungsrechnung, keinen Freeze, keinen Merge und keinen Push. Originalmodule und M0–M12 sind unverändert.

## Gebaut

| Modul | Inhalt |
|---|---|
| `training.py` | **Ridge in geschlossener Form mit NumPy** (LR0-O1: kein scikit-learn). Zielfunktion (Plan 8): (1/N)‖XₛW + 1bᵀ − U‖² + λ‖W‖². Der **Interzept b ist unbestraft**. Gelöst wird über die SVD der zentrierten, standardisierten Trainingsmerkmale: W = Q·diag(s/(s² + Nλ))·Pᵀ·U_c und b = Ū − X̄ₛW. Das ist stabil für jedes λ > 0, auch bei konstanten oder kollinearen Spalten, und eine SVD reicht für das ganze Raster. Die **Standardisierung** stammt nur aus dem Training (Mittelwert, Populations-SD mit ddof 0); eine Spalte mit SD exakt 0 bekommt die Skala 1. *(Nach `REVIEW_LR4` R1: Exakt konstante Spalten werden jetzt über ihre Werte erkannt; siehe Nachtrag.)* **λ-Raster** 1e-4 … 100. **Auswahl:** kleinster Validierungs-MSE der *projizierten* Vorhersagen, bei exaktem Gleichstand das größere λ. Die Funktion `fit_ridge` hat **kein Testargument**. |
| `decoders.py` | `RidgeDecoder` mit Merkmalsdefinition, Skalierung, Gewichten, Interzept, λ, Raster, Validierungs-MSE, Herkunft und Softwareversionen. `predict(model, X)` sieht **nur** die Merkmale. Gespeichert wird als NPZ mit rein numerischen Arrays (geladen mit `allow_pickle=False`) plus striktem JSON. Jedes Array hat eine kanonische Identität (Name, dtype mit Byteorder, Shape, Bytes in C-Ordnung). Beim Laden wird außerdem geprüft, dass das gespeicherte λ genau die Wahl der Auswahlregel ist. *(Nach `REVIEW_LR4` erweitert: vollständige Metadatenprüfung, Bindung an die Zelle, unveränderliche Arrays; siehe Nachtrag.)* |
| `evaluate.py` | Test-Scoring eines fertigen Decoders. Importiert **keine** Fit-Funktion (Plan 11, per AST geprüft). |
| `metrics.py` | Projektion auf [−1, 1]; Verlust je Episode und Nullvergleich. S und G werden **getrennt** geführt, G darf negativ sein. A ist ein fester Rastermittelwert (Trapez auf log(1 + τ), K21). **Kontextinferenz:** genau ein Wert je Kontext-ID, df = Kontexte − 1. Dazu t-Intervalle (punktweise, nicht simultan), ein entarteter Fall bei identischen Werten, H-B1/H-B2 einseitig mit Holm über zwei Tests, Bonferroni-Intervalle (Quantil 0,9875), Permutations-p = (1 + b)/(1 + B) und der Leak-Alarm über genau 12 Zellen (Holm, Grenze 0,01). |
| `runner.py` | Entwicklungspipeline für einen Kontext. Sie verweigert jede Studien-ID außer `development_study_id`. Pro Split und Bedingung wird **eine** RK4-Trajektorie berechnet. **Merkmale kommen nur über `observation.observe()`** (Vorgabe aus Astras Nachprüfung). Je Zelle folgt Fit auf train, λ auf val, Scoring auf test, und A aus den sieben G-Werten. |
| `episodes.simulate` | Optionales `dt`, **nur** für die Konvergenzprüfung. Ohne Angabe gilt das Protokoll-dt, und der Standardpfad ist unverändert. |

## Unabhängig geprüft (Kontrollwerte vor dem Code von Hand hergeleitet)

| Kontrolle | Herleitung | Ergebnis |
|---|---|---|
| Ridge in 1D | X = (1, 3), U = (0, 4): Xₛ = (−1, 1), w = 2/(1 + λ), b = 2 (mit `Fraction`) | exakt bis 1e-15 |
| Ridge allgemein | mit konstanter und kollinearer Spalte, über alle 7 λ: Vergleich mit erweiterten kleinsten Quadraten (unbestrafte Interzeptspalte) und mit den Normalgleichungen samt Interzeptblock; der Gradient der Zielfunktion ist 0; jede Störung erhöht die Zielfunktion | ≤ 1e-8 |
| Interzept unbestraft | U + 5 verschiebt b um genau 5, W bleibt gleich, auch bei λ = 100 | exakt bis 1e-12 |
| λ-Konvention (Plan-Mutant 13) | Verdoppelte Zeilen ändern W nicht. Die ungemittelte Form (scikit-learn) entspricht alpha = N·λ; alpha = λ weicht ab. | bestätigt |
| K19 | Ziele 0,1/0,2, Nullvorhersage: S = 0,925, G = 0 | ✓ |
| K20 | Holm (0,03; 0,04) → (0,06; 0,06) | ✓ |
| K21 | geschlossene Form: w₀ = ln 1,5/(2 ln 11); w₁…w₄ = ln 2/(2 ln 11); w₅ = ln(11/4)/(2 ln 11); w₆ = ln(11/6)/(2 ln 11). Für konstantes G ist A = G; für G = z ist A = ln(11)/2. | ≤ 1e-15, gleich den Referenzwerten |
| K22 | Vorhersage 1 bei kleinen Zielen: G = −2,1, zulässig | ✓ |
| t-Quantile | t₀,₉₇₅;₁₉ = 2,093024054…; t₀,₉₈₇₅;₁₉ gegen eine eigene Simpson-Integration der t-Dichte; einseitiges p bei df = 2 in geschlossener Form | ≤ 1e-10 |

**Abnahme laut Plan § 14:**
- analytische Scores: perfekte Vorhersage ergibt S = 1 und G = 3·mean(u²), Nullvorhersage ergibt G = 0;
- keine Episoden als Pseudoreplikate (Plan-Mutant 15): Episodenarrays werden abgewiesen;
- Artefakt-Roundtrip mit bitgleichen Vorhersagen; die getesteten Manipulationen an Arrays und am λ werden erkannt. **Korrektur nach `REVIEW_LR4`:** Das war kein vollständiger Manipulationsschutz. Ungültige Metadaten wie n_train = −5 oder die Referenz −1 wurden akzeptiert. Siehe den Nachtrag unten.

**Zusätzlich geprüft:**
- Eine fehlende Rasterzelle ist ein Fehler, nicht null (Plan-Mutant 16).
- Negatives G bleibt erhalten (Plan-Mutant 14).
- Die Standardisierung kommt nur aus dem Training (Plan-Mutant 11).
- Plan-Mutant 12 betrifft die MLP-Initialisierung und gilt für Ridge nicht. Sein Gegenstück, keine Testdaten im Fit, ist getestet.

## Decoder-Konvergenzgate (Plan 10.2, offen seit AE-01)

Die Definition wurde **vor** dem Lauf festgelegt und committet (`protocol/decoder_convergence_gate.json`, Commit `027fc0c`). Die Zusammenfassung ist per SHA an diese Datei gebunden.

**Panel:** Entwicklungsstudie 2026100803, Kontexte 0 und 1, je 1000/250/1000 Episoden, alle vier Bedingungen, Aufgaben A und B, sieben Zeitpunkte. Die komplette Pipeline lief je dt einmal.

| Vergleich mit dt = 0,005 | max \|ΔG\| (112 Zellen) | max \|ΔA\| (16 Kurven) | max \|ΔS\| | λ-Wechsel | max. Zustandsabstand |
|---|---|---|---|---|---|
| **dt = 0,02 (Protokoll)** | **8,7·10⁻¹⁰** | **2,5·10⁻¹⁰** | 8,7·10⁻¹⁰ | 0 | 2,4·10⁻¹⁰ rad |
| dt = 0,01 | 5,1·10⁻¹¹ | 1,5·10⁻¹¹ | 5,1·10⁻¹¹ | 0 | 1,4·10⁻¹¹ rad |

**Gate (≤ 0,01): bestanden**, mit rund sieben Größenordnungen Abstand. Ich habe die Maxima unabhängig aus der Volldatei nachgerechnet; jedes A stimmt mit den geschlossenen K21-Gewichten überein (< 1e-15).

**Pipeline-Gate aus Plan 10:**
- **Aufgabe A bei t = 0:** Das mittlere G0 über die Entwicklungskontexte liegt bei **0,962 > 0,90**, bestanden. Bei t = 0 sind alle Bedingungen identisch.
- **Aufgabe B bei t = 0:** G0 = −5,2·10⁻⁴ und −4,3·10⁻⁴. Das ist erwartet zielfrei; strukturell ist es durch LR3 getestet.

**Laufzeit** der vollen Entwicklungspipeline (4 Bedingungen, 2250 Episoden, 56 Ridge-Fits) bei dt = 0,02: 247 s bzw. 274 s je Kontext. Kontext 0 lief zeitweise parallel zu den Mutationstests. Die Hochrechnung auf 20 Kontexte, also etwa 85 Minuten für den A/B-Ridge-Teil, ist **nur eine Schätzung**. Die Messung gehört zum LR5-Benchmark.

**Verwendung der Werte:** Die G-Kurven beider Entwicklungskontexte liegen in der Volldatei. Sie sind **Entwicklungswerte** und dienen nicht der Wahl von Protokollwerten. Die Kontexte 0 und 1 der Entwicklungsstudie sind keine Forschungskontexte, und aus den Werten folgt keine Forschungsaussage. Sie werden, wie Aeons Pilot, als bekannte Entwicklungsinformation deklariert.

## Gezielte Mutation (ad hoc; die vollständige Mutationskampagne gehört zu LR5)

**29/30 erkannt.**
- **1 äquivalent:** Das erneute Zentrieren von Xₛ im Solver entfällt. Xₛ ist durch die Standardisierung bereits zentriert (Spaltenmittel ≤ 2·10⁻¹³). Der Mutant weicht über 50 Zufallsprobleme × 7 λ um höchstens 1,7·10⁻¹⁴ ab.
- **2 echte Testlücken, im ersten Lauf überlebt und geschlossen:**
  - Validierung ohne Projektion: In den Testdaten verließ keine Vorhersage [−1, 1]. Jetzt gibt es Daten mit herausragenden Rohvorhersagen.
  - Leak-Alarm ohne Holm: Es fehlte der Fall mit rohem p ≤ 0,01 und adjustiertem p > 0,01.

  Dazu kam ein echter bestrafter-Interzept-Mutant (b geschrumpft); er wird erkannt.
- **Während der Testentwicklung gefunden:** `np.std` dreier identischer Werte ist ≈ 1e-17 statt 0. Der entartete Fall wäre dadurch übersehen worden, mit riesigem t. Jetzt sind SD und SE bei identischen Kontextwerten exakt 0.

**Tests:** 268/268, davon 35 in `tests/test_lr4.py`. Die Erwartung in `test_lr2_rk4.py` wurde vom LR3-Stand „open until LR4“ auf das LR4-Ergebnis umgestellt.

**Belege** (Volldatei, Laufprotokoll, Mutationsskript und -protokoll, Äquivalenz- und Nachrechenskript): `D:/mandala/mandala-memory-results/lantern/lr4/`.

## Nachtrag nach `REVIEW_LR4` (Astra; geprüft `027fc0c` / `18a89c3`)

**Bestätigt:**
- 268/268 Tests;
- die Konvergenzwerte aus der Volldatei nachgerechnet (112 Zellen und 16 Kurven je Vergleich);
- Ridge-Formel, `observe()`-Pfad, Trennung der Splits und ein Evaluator ohne Fit-Import.

**Zuerst reproduziert** (am Stand `18a89c3`, mit eigenem Skript; Astras Reviewordner blieb unverändert):
- **R1:** `np.full((1000, 1), 0.1)` ergab die Skala **1,3877787807814457·10⁻¹⁷** statt 1. Dasselbe passiert bei n = 3 und n = 7, nicht bei n = 10. Auch der Mittelwert weicht um 1,4·10⁻¹⁷ ab.
- **R2:** n_train = −5, Referenz −1 und context_id 999 im JSON wurden geladen.
- **Zusatz:** `W.setflags(write=True)` gelang, danach änderte sich `predict`.

| Befund | Korrektur |
|---|---|
| **R1** konstante Trainingsspalte | Exakt konstante Spalten werden **über ihre Werte** erkannt (`np.all(x == x[0])`), nicht über die berechnete SD und ohne Epsilon-Schwelle. Sie erhalten Mittelwert = ihr Wert und Skala = 1 und standardisieren damit exakt zu 0. Variable Spalten, auch fast konstante (SD ≈ 3·10⁻¹⁴), werden **bitgleich wie vorher** behandelt. |
| **R2** Metadaten | `check_decoder` prüft bei der Konstruktion **und** beim Laden: <br>• n_train und n_val als echte positive Ganzzahlen; <br>• die Merkmalsdefinition mit genau den Schlüsseln task/nodes/reference/order; <br>• Knoten als eindeutige Ganzzahlen in [0, 34), 33 für A bzw. 8 für B; <br>• die Referenz in [0, 34) und außerhalb der Knoten; <br>• bei A die feste Reihenfolge; die Reihenfolge-Angabe gleich `FEATURE_ORDER`; Dimension = 2 × Knotenzahl; <br>• das λ-Raster positiv und eindeutig, die Validierungs-MSE in [0, 4]; <br>• Herkunft und Software nur mit JSON-Skalaren; <br>• λ im JSON als Zahl (`true` ist kein λ = 1). <br>Neu ist **`check_decoder_for(model, ctx, task, **zelle)`**: Es bindet das Modell an die Beobachtungsdefinition des erwarteten Kontexts (Knotenfolge, Referenz) und an Studie, Kontext, Fingerabdruck, Konfiguration und Zelle. Der Runner ruft es vor jedem Scoring auf. |
| **Zusatz** (laut Review LR5, schon jetzt mitgenommen) | Wie beim LR1-Fix liegen die Modellarrays auf **unveränderlichen Byte-Puffern**; `setflags(write=True)` wird abgewiesen. Merkmalsdefinition, Herkunft und Software sind tief eingefroren (`MappingProxyType`). |

**Ehrliche Grenze:** Eine *andere*, syntaktisch gültige context_id (999) kann der Loader allein aus dem JSON **nicht** als falsch erkennen. Die Array-Prüfsummen liegen neben den Arrays und authentifizieren die Metadatei nicht. Abgewiesen wird so ein Modell erst von `check_decoder_for` gegen die *erwartete* Zelle. Eine in sich stimmige Fälschung erkennt erst die externe Manifestidentität aus LR5. `save()` ist ausdrücklich ein Entwicklungshelfer: Es überschreibt Dateien und schreibt kein Manifest.

**Bleibt R1 ohne Wirkung auf das Konvergenzgate?**
- Unter den 4592 Trainingsmerkmalsspalten des Gate-Panels (2 Kontexte × 4 Bedingungen × 2 Aufgaben × 7 Zeiten) ist **keine** exakt konstant; die kleinste SD ist 1,1·10⁻³.
- Für variable Spalten ist die Standardisierung bitgleich.
- Eine Alt-gegen-neu-Pipeline (`18a89c3` gegen den Fix) über 2 Kontexte, 4 Bedingungen, A/B und 200/60/200 Episoden liefert für alle 16 Kurven **exakt** dieselben G-, S-, A- und λ-Werte.

Das bestandene Gate bleibt damit gültig; ein neuer langer Lauf ist nicht nötig. Die Änderung der Standardisierungsregel steht vor dem Freeze dokumentiert (`decoders.STANDARDISATION`).

**Danach:**
- Gezielte Mutation der neuen Wächter: **23/23** werden von `test_lr4_review.py` erkannt. Im ersten Lauf waren es 22/23: `true` als λ fiel nur zufällig über die Auswahlregel auf, weil das Testmodell λ = 100 hatte. Das war eine echte Testlücke; jetzt gibt es einen Fall mit λ = 1,0.
- Im eigenen Test korrigiert: Der Vergleichswert für die SD einer herausgeschnittenen Spalte hatte eine andere Summationsreihenfolge als die Regel.

**Tests:** 295/295 (bisher 268, dazu 27 in `tests/test_lr4_review.py`).

**Belege:** `D:/mandala/mandala-memory-results/lantern/lr4_review/`.

## Offen

- **LR5:** Schemas und DAG der Artefakte, deterministisches Resume, Budgetmessung, CI-Jobs, die vollständige Mutationskampagne mit den 18 Plan-Mutanten (Mutant 6 ist bis LR9 `not_applicable`). **Verbindlich aus `REVIEW_LR4`:**
  - Modellintegrität mit Hashprüfung vor und nach der Auswertung;
  - exklusive und atomare Speicherung ohne Überschreiben;
  - ein vollständiges Manifest mit externer Modell- und Herkunftsidentität samt erwarteter Zelle;
  - eine Ergebnisfreigabe, die das genaue Kontext- und Zellenraster sowie alle Kontrollalarme prüft. Die generischen Statistikfunktionen sind noch kein Forschungsgate.
- **LR5/LR6:** Kontrollkurven mit permutierten Trainingszielen; die 12 Leak-Alarm-Zellen mit 9999 Permutationen (die Funktionen sind fertig, aber noch nicht im Lauf); das optionale MLP; der Freeze-Kandidat mit Masterseeds und Kontextliste.
- Astras Nachprüfung dieses Fixes.
