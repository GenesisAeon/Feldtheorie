# Mandala-GedÃ¤chtnislabor: ForschungsÃ¼bersicht M0â€“M12

Dies ist ein Einstieg neben der langen [Roadmap](../ROADMAP.md). Die Ãœbersicht fasst nur zusammen, was dort und in den verlinkten Dokumenten bereits belegt ist; sie enthÃ¤lt keine neuen Rechnungen. Alle Aussagen gelten fÃ¼r eine **synthetische Modellstudie**: kleine Netze, feste Parameter, keine biologische und keine allgemeine KI-Aussage, keine Gewinnerbehauptung.

## Das Modell in einem Satz

Ein Netz aus 12 Knoten, x_{k+1} = (1âˆ’â„“)Â·x_k + â„“Â·tanh(AÂ·x_k + BÂ·u_k), bekommt einen kurzen Reiz A oder B. Nach einer Pause von d Schritten wird mit Messrauschen (Ïƒ = 0,02) abgelesen, welcher Reiz es war. Verglichen wird ein **modulares** Netz (3 Module, Kopplung c = 1/4) mit einem gleich budgetierten **uniformen** Netz. Die Gewichtssumme pro Zeile ist in beiden Î³ = 0,8.

Zwei Arten von Leistung ziehen sich durch alle Pakete:
- die **Bayes-Grenze**: wie gut der Reiz bestenfalls aus dem Zustand ablesbar ist;
- **trainierte Decoder**: wie gut ein konkretes, gelerntes Ausleseverfahren das tatsÃ¤chlich schafft.

## Fragen und Antworten

| Paket | Frage | Antwort (Kurzfassung) | Art des Belegs |
|---|---|---|---|
| **M0â€“M2** | Rechnen Kern, ZufallsstrÃ¶me und Decoder korrekt? | Ja. Die Kontrollen K1â€“K9 wurden unabhÃ¤ngig nachgerechnet, mit exakten BrÃ¼chen. Der Kern ist bitgleich mit SCF `simulate_trial`. | exakte Kontrollen, Tests |
| **M3â€“M4** | Verbessert eine episodische Hebb-Anpassung das Erinnern bei d = 8? | **Nicht nachweisbar**: gepaarte Differenz âˆ’0,001, 95 %-Bootstrap [âˆ’0,0025; +0,0005]. Beschreibend erinnert sich das modulare Netz lÃ¤nger als das uniforme (d = 4: 0,93 gegen 0,65). | vorab festgelegter Kontrast, 20 Seeds |
| **M5** | TrÃ¤gt die Feldtheorie-Membran einen Reiz Ã¼ber eine Pause? | Beschreibend ja, im adaptiven Parameterzustand (Î¸ und Î²); die Spur zerfÃ¤llt bis d â‰ˆ 32. Es ist eine andere Aufgabe als im Netz, also kein Vergleich. | Pilot, beschreibend |
| **M6, M8** | Kann man das Mandala erleben, ohne den Benchmark zu berÃ¼hren? | Ja: eine lokale Ansicht (nur 127.0.0.1) und ein Regler-Labor, beide explorativ und protokolliert. Benchmarkdaten bleiben unberÃ¼hrt. | Dienst, Tests |
| **M9** | LÃ¤sst sich die GedÃ¤chtnisdauer **vorhersagen**? | Ja, fÃ¼r die Modellfamilie F. Herleitung der Moden und eine beweisbare Fehlerschranke. Eingefrorene Vorhersagen an 24 ungesehenen Kombinationen: 24/24 BÃ¤nder, 23/23 Punktvorhersagen von D, 28/28 Decoder-PrÃ¼fungen. Die naive q-Regel lag in allen 14 FÃ¤llen mit Erinnerung daneben. | `analytic_argument` + eingefrorene Vorhersage |
| **M10** | Wie stÃ¶ren Ablenkungen kurz vor dem Ablesen? | **H-N bestÃ¤tigt:** Ablenkung in den Eingangsmodulen kostet das modulare Netz 0,024 an Bayes-Trennbarkeit; im uniformen Netz ist innerhalb der Monte-Carlo-AuflÃ¶sung kein entsprechender Verlust erkennbar. **H-F+ nicht bestÃ¤tigt:** SchÃ¤tzung âˆ’0,0001, SE 0,00011, unadjustiertes 95 %-Intervall [âˆ’0,0003; +0,0001]. Getrennt davon verlieren trainierte Decoder zusÃ¤tzlich viel mehr als die Bayes-Grenze (NM 0,30, LDA 0,16). | eingefrorenes Protokoll, einmaliger Lauf |
| **M11** | Wie viel dieser Ablese-LÃ¼cke schlieÃŸt ein besseres Ausleseverfahren, bei unverÃ¤ndertem Mandala? | **C-Modell bestÃ¤tigt:** Ein kleines MLP ist bei n = 1000 um 0,022 besser als LDA. **C-Daten nicht bestÃ¤tigt:** Mehr Daten bringen LDA nur +0,0017. Beschreibend schlieÃŸt das MLP bei n = 16000 rund 84 % der LDA-LÃ¼cke. | eingefrorenes Protokoll; zwei Versuche, der zweite vollstÃ¤ndig |
| **M12** | Bleibt ein gelerntes Auslesen vorteilhaft, wenn sich AblenkungsstÃ¤rke oder Messrauschen Ã¤ndern und die trainierten Decoder unverÃ¤ndert bleiben? | **BestÃ¤tigt (beide Endpunkttests):** Das fixierte MLP ist an den erhÃ¶hten Endpunkten besser als die fixierte LDA: +0,104 bei Ablenkungsamplitude 0,9, +0,043 bei Ïƒ = 0,03. **Beschreibend:** Bei verÃ¤nderter AblenkungsstÃ¤rke wÃ¤chst die Bayes-LÃ¼cke des unverÃ¤nderten MLP in beide Richtungen; bei Amplitude 0,30 kehrt sich der Vorteil um (LDA um 0,036 besser). Beim Messrauschen bleibt die absolute Bayes-LÃ¼cke des MLP klein; das ist kein bestÃ¤tigender Robustheits- oder Ã„quivalenztest. | eingefrorenes Protokoll, neue fixierte Basismodelle, je Phase ein Versuch |

## Was sich daraus ergibt

1. **Moden der Erinnerung** (M9). Der Reizunterschied hat in der symmetrischen Modellfamilie keinen Gleichtaktanteil, auch im nichtlinearen Modell exakt. Deshalb ist die Kontraktionsrate q nur eine obere Grenze und keine Erinnerungsrate.
   - **Linear:** Im linearen Modell zerfÃ¤llt der Reizunterschied in Modul- und Binnenmoden, die mit Î¼_D bzw. Î¼_I abklingen.
   - **Benchmark:** Bei Reizen in unterschiedlichen Modulen trÃ¤gt dort die Modulmode die lÃ¤nger anhaltende Spur.
   - **Kleines c:** Je kleiner c, desto nÃ¤her rÃ¼ckt Î¼_D an q, im Benchmark q = 0,9; es geht nicht allgemein gegen 1.
   - **Nichtlinear:** FÃ¼r das nichtlineare Modell gilt die hergeleitete FehlerabschÃ¤tzung.
   - **Andere FÃ¤lle:** Bei Reizen im selben Modul oder anderen Ablesungen gelten die dokumentierten Grenzen, etwa nur Î¼_I oder eine unsichtbare Spur.
2. **Dieselbe Struktur macht stÃ¶rbar** (M10):
   - Ablenkung in den Eingangsmodulen senkt im modularen Netz die Bayes-Trennbarkeit messbar. Im uniformen Netz ist innerhalb der Monte-Carlo-AuflÃ¶sung kein entsprechender Verlust erkennbar.
   - Die Moden- und Symmetrieargumente haben diese Hypothese fÃ¼r das tanh-Netz **motiviert**. Bewiesen ist die StÃ¶rungsfreiheit nur fÃ¼r den linearen Zwilling; der Befund im tanh-Netz ist empirisch.
   - Der Verlust an Bayes-Trennbarkeit und der zusÃ¤tzliche Decoderverlust sind getrennte GrÃ¶ÃŸen.
3. **Vorhandene Information ist nicht automatisch ablesbare Information** (M10, M11).
   - Unter Ablenkung bleibt die Bayes-Leistung im Hauptfall hoch (0,912), lineare Decoder fallen aber ab.
   - Ein nichtlineares Lernverfahren holt bei genug Daten den grÃ¶ÃŸten Teil zurÃ¼ck.
   - Ob ein Netz â€žvergisstâ€œ oder nur â€žschwerer abzulesen istâ€œ, hÃ¤ngt also vom Ablesenden ab.
4. **Gute Ausleseleistung unter Trainingsbedingungen garantiert keinen Vorteil unter verÃ¤nderten Bedingungen** (M12).
   - **BestÃ¤tigt:** An den beiden vorab gewÃ¤hlten erhÃ¶hten Endpunkten bleibt das fixierte MLP mehr als 0,01 besser als die fixierte LDA. Ob der Ausgangsvorteil (+0,113) erhalten bleibt, wurde nicht getestet.
   - **Beschreibend, AblenkungsstÃ¤rke:** Das unverÃ¤nderte MLP verliert in beide Richtungen mehr, als die Ã„nderung der Bayes-Trennbarkeit vorgibt. Bei Amplitude 0,9 sinkt es, obwohl die Bayes-Leistung steigt. Bei Amplitude 0,30 ist die fixierte LDA besser. Eine Ursache bestimmt der Versuch nicht.
   - **Beschreibend, Messrauschen:** Die LeistungsÃ¤nderung des MLP liegt nahe bei der Ã„nderung der Bayes-Trennbarkeit. Seine absolute Bayes-LÃ¼cke bleibt klein, Ã¤ndert sich relativ aber deutlich.

## Grenzen, die fÃ¼r alles gelten

- **Geltungsbereich:** zwei feste 12-Knoten-Netze, ein Parametersatz pro Studie. M9 deckt eine definierte Modellfamilie ab, mit einer Stichprobe von 24 PrÃ¼fkombinationen; allgemein gilt nur die bewiesene Schranke.
- **Unsicherheiten:** Seeds sind synthetische Wiederholungen. Intervalle beschreiben Rechen- und Stichprobenunsicherheit unter genau diesem Modell, keine Population von Netzen.
- **â€žNicht bestÃ¤tigtâ€œ** bedeutet: Das vorab festgelegte BestÃ¤tigungskriterium wurde nicht erfÃ¼llt. Daraus folgt allein weder Wirkungslosigkeit noch ein Effekt unterhalb einer Relevanzschwelle. Weitergehende Aussagen brauchen das jeweilige Intervall:
  - **M11 C-Daten:** Das Intervall [0,0013; 0,0021] liegt unter der Schwelle von 0,01 und spricht zugleich fÃ¼r einen kleinen positiven Effekt.
  - **M10 H-F+:** Die SchÃ¤tzung ist âˆ’0,0001 mit SE 0,00011.
  - **M4:** Es zeigte keinen nachweisbaren Hebb-Gewinn; eine Relevanzschwelle war dort nicht festgelegt.
- **M11 im Besonderen:**
  - Die beste *gefundene* lineare Regel ist keine bewiesene Grenze aller linearen Regeln.
  - Das MLP ist ein Beispiel fÃ¼r nichtlineares Auslesen, kein bestes Verfahren.
  - In M11 wurde es nur unter **passenden** Trainings- und Testbedingungen gemessen; geÃ¤nderte Bedingungen untersucht M12.
- **M12 im Besonderen:**
  - Es gibt nur ein Netz, nahe Ablenkung, d = 4 und 9 Rasterpunkte. FÃ¼r Werte zwischen oder auÃŸerhalb der Punkte gilt keine Aussage.
  - Es gab keinen Vergleich mit nachtrainierten Modellen. Eine Ã„nderung der Bayes-LÃ¼cke (Î”G) wird keiner Ursache zugeschrieben.
  - Die LDA-Zerlegung bezieht sich auf die bedingungsspezifische Populations-LDA, nicht auf die beste lineare Regel.
  - BestÃ¤tigend sind nur die beiden Endpunkttests. Verlustkurven, Zerlegung, Umkehr bei Amplitude 0,30 und das Verhalten beim Rauschen sind beschreibend.
  - Die Basismodelle sind eine neue Stichprobe, keine Wiederholung von M11.

## Eingefrorene Belege

| Paket | Eingefroren | Ergebnis und PrÃ¼fungen |
|---|---|---|
| M0â€“M4 | [Startkonfiguration](../protocol/startkonfiguration.json), [Manifest](../M0_MANIFEST.json) | `D:/mandala/mandala-memory-results/research/research-e19650a0a0.json` (+ Auswertung v2 nach Review R1/R2) |
| M9 | [Herleitung](M9_HERLEITUNG.md) (hashgeschÃ¼tzt), [Vorhersagen](../protocol/m9_frozen_predictions.json) (SHA-256 `1e872cecâ€¦`; berechnet am dokumentierten Code-Stand `6f8a812`, versioniert eingefroren in Commit `359a4cf` vor jeder Kernrechnung), [Erratum 1](M9_ERRATUM_1.md) | `D:/mandala/mandala-memory-results/m9/m9-evaluation--8d353dbc88.json` |
| M10 | [Plan](M10_PLAN_ABLENKUNG.md), [Protokoll](../protocol/m10_protokoll.json), [Freeze-Datensatz](../protocol/m10_freeze.json), Tag `m10-freeze` (7b31300) | `D:/mandala/mandala-memory-results/m10/research/m10-research-20261003T230058-47d41706.json`; Integrationsbericht `m10/INTEGRATION_M10.md` |
| M11 | [Plan](M11_PLAN_AUSLESE.md), [Protokoll](../protocol/m11_protokoll.json), [Referenzen](../protocol/m11_references.json), [Freeze-Datensatz](../protocol/m11_freeze.json), Tag `m11-freeze` (1a5423f), [Ergebnis](M11_ERGEBNIS.md) | Versuch 2: `D:/mandala/mandala-memory-results/m11/research/m11-research-20261005T114106-e996e301.json` (+ `.evaluation.json`); Versuch 1 (abgebrochen, gesperrt), Abbruchbericht und Nachtrag im selben Ordner; `m11/INTEGRATION_M11.md` |
| M12 | [Plan](M12_PLAN_ROBUSTHEIT.md), [Protokoll](../protocol/m12_protokoll.json), [Protokoll-Freeze](../protocol/m12_freeze.json) (Tag `m12-freeze`, f3a5bc2), [Referenzen](../protocol/m12_references.json), [Modell-Freeze](../protocol/m12_models_freeze.json) (Tag `m12-models`, e8e53a8) mit [Modellartefakten](../protocol/m12_models/), [Ergebnis](M12_ERGEBNIS.md) | `D:/mandala/mandala-memory-results/m12/research/m12-research-20261005T170243-972cca01.json` (+ `.evaluation.json`); Integrationsbericht `m12/INTEGRATION_M12.md` (mit dem behobenen Checkout-Befund zu den Zeilenenden der Modell-JSON) |

UnabhÃ¤ngige Reviews von Astra liegen in den `astra-*`-Ordnern unter `D:/mandala/mandala-memory-results/`. Codefehler wurden Ã¼ber reproduzierbare Gegenbeispiele und gezielte Tests bearbeitet. Mathematische und sprachliche Ãœberdehnungen wurden durch HerleitungsprÃ¼fung bzw. Dokumentationskorrekturen behoben, etwa im Erratum zu M9 oder in den PrÃ¤zisierungen zu M10 und M11. Details stehen in der Roadmap.

## Von der offenen Frage zu M12

Die frÃ¼here offene Frage nach der Robustheit des gelernten Auslesens hat M12 aufgegriffen. Weil M11 keine Modellgewichte gespeichert hatte, wurden **neue Basismodelle** nach vorab festgelegtem Plan trainiert und dann mit PrÃ¼fsummen fixiert; es sind keine rekonstruierten M11-Modelle. Ergebnisse und Grenzen stehen oben und in [M12_ERGEBNIS.md](M12_ERGEBNIS.md).
