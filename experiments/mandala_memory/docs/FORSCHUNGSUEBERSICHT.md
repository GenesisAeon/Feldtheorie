# Mandala-Gedächtnislabor: Forschungsübersicht M0–M11

Dies ist ein Einstieg neben der langen [Roadmap](../ROADMAP.md). Die Übersicht fasst nur zusammen, was dort und in den verlinkten Dokumenten bereits belegt ist; sie enthält keine neuen Rechnungen. Alle Aussagen gelten für eine **synthetische Modellstudie**: kleine Netze, feste Parameter, keine biologische und keine allgemeine KI-Aussage, keine Gewinnerbehauptung.

## Das Modell in einem Satz

Ein Netz aus 12 Knoten, x_{k+1} = (1−ℓ)·x_k + ℓ·tanh(A·x_k + B·u_k), bekommt einen kurzen Reiz A oder B. Nach einer Pause von d Schritten wird mit Messrauschen (σ = 0,02) abgelesen, welcher Reiz es war. Verglichen wird ein **modulares** Netz (3 Module, Kopplung c = 1/4) mit einem gleich budgetierten **uniformen** Netz. Die Gewichtssumme pro Zeile ist in beiden γ = 0,8.

Zwei Arten von Leistung ziehen sich durch alle Pakete:
- die **Bayes-Grenze**: wie gut der Reiz bestenfalls aus dem Zustand ablesbar ist;
- **trainierte Decoder**: wie gut ein konkretes, gelerntes Ausleseverfahren das tatsächlich schafft.

## Fragen und Antworten

| Paket | Frage | Antwort (Kurzfassung) | Art des Belegs |
|---|---|---|---|
| **M0–M2** | Rechnen Kern, Zufallsströme und Decoder korrekt? | Ja. Die Kontrollen K1–K9 wurden unabhängig nachgerechnet, mit exakten Brüchen. Der Kern ist bitgleich mit SCF `simulate_trial`. | exakte Kontrollen, Tests |
| **M3–M4** | Verbessert eine episodische Hebb-Anpassung das Erinnern bei d = 8? | **Nicht nachweisbar**: gepaarte Differenz −0,001, 95 %-Bootstrap [−0,0025; +0,0005]. Beschreibend erinnert sich das modulare Netz länger als das uniforme (d = 4: 0,93 gegen 0,65). | vorab festgelegter Kontrast, 20 Seeds |
| **M5** | Trägt die Feldtheorie-Membran einen Reiz über eine Pause? | Beschreibend ja, im adaptiven Parameterzustand (θ und β); die Spur zerfällt bis d ≈ 32. Es ist eine andere Aufgabe als im Netz, also kein Vergleich. | Pilot, beschreibend |
| **M6, M8** | Kann man das Mandala erleben, ohne den Benchmark zu berühren? | Ja: eine lokale Ansicht (nur 127.0.0.1) und ein Regler-Labor, beide explorativ und protokolliert. Benchmarkdaten bleiben unberührt. | Dienst, Tests |
| **M9** | Lässt sich die Gedächtnisdauer **vorhersagen**? | Ja, für die Modellfamilie F. Herleitung der Moden und eine beweisbare Fehlerschranke. Eingefrorene Vorhersagen an 24 ungesehenen Kombinationen: 24/24 Bänder, 23/23 Punktvorhersagen von D, 28/28 Decoder-Prüfungen. Die naive q-Regel lag in allen 14 Fällen mit Erinnerung daneben. | `analytic_argument` + eingefrorene Vorhersage |
| **M10** | Wie stören Ablenkungen kurz vor dem Ablesen? | **H-N bestätigt:** Ablenkung in den Eingangsmodulen kostet das modulare Netz 0,024 an Bayes-Leistung, das uniforme nicht. **H-F+ nicht bestätigt:** ferne Ablenkung, kein Unterschied über 0,01. Trainierte Decoder verlieren viel mehr als die Bayes-Grenze (NM 0,30, LDA 0,16). | eingefrorenes Protokoll, einmaliger Lauf |
| **M11** | Wie viel dieser Ablese-Lücke schließt ein besseres Ausleseverfahren, bei unverändertem Mandala? | **C-Modell bestätigt:** Ein kleines MLP ist bei n = 1000 um 0,022 besser als LDA. **C-Daten nicht bestätigt:** Mehr Daten bringen LDA nur +0,0017. Beschreibend schließt das MLP bei n = 16000 rund 84 % der LDA-Lücke. | eingefrorenes Protokoll; zwei Versuche, der zweite vollständig |

## Was sich daraus ergibt

1. **Die Erinnerung steckt im Modul-Unterschied** (M9). Der Reizunterschied hat aus Symmetriegründen keinen Gleichtaktanteil. Deshalb ist die Kontraktionsrate q nur eine obere Grenze und keine Erinnerungsrate. Er klingt mit μ_D ab:
   - μ_D liegt nahe 1, wenn die Module gut abgeschottet sind (kleines c);
   - dann hält sich die Spur länger.
   - Das erklärt den Vorsprung des modularen Netzes aus M4.
2. **Dieselbe Struktur macht störbar** (M10): Ablenkung, die in die Eingangsmodule fällt, trifft im modularen Netz genau den tragenden Modus. Im uniformen Netz liegen die Ablenkorte symmetrisch zum Reizpaar.
3. **Vorhandene Information ist nicht automatisch ablesbare Information** (M10, M11).
   - Unter Ablenkung bleibt die Bayes-Leistung im Hauptfall hoch (0,912), lineare Decoder fallen aber ab.
   - Ein nichtlineares Lernverfahren holt bei genug Daten den größten Teil zurück.
   - Ob ein Netz „vergisst“ oder nur „schwerer abzulesen ist“, hängt also vom Ablesenden ab.

## Grenzen, die für alles gelten

- **Geltungsbereich:** zwei feste 12-Knoten-Netze, ein Parametersatz pro Studie. M9 deckt eine definierte Modellfamilie ab, mit einer Stichprobe von 24 Prüfkombinationen; allgemein gilt nur die bewiesene Schranke.
- **Unsicherheiten:** Seeds sind synthetische Wiederholungen. Intervalle beschreiben Rechen- und Stichprobenunsicherheit unter genau diesem Modell, keine Population von Netzen.
- **„Nicht bestätigt“ heißt nicht „kein Effekt“:** Es heißt „unter der vorab festgelegten Relevanzschwelle“ (M4, M10 H-F+, M11 C-Daten).
- **M11 im Besonderen:**
  - Die beste *gefundene* lineare Regel ist keine bewiesene Grenze aller linearen Regeln.
  - Das MLP ist ein Beispiel für nichtlineares Auslesen, kein bestes Verfahren.
  - Bisher wurde es nur unter **passenden** Trainings- und Testbedingungen gemessen.

## Eingefrorene Belege

| Paket | Eingefroren | Ergebnis und Prüfungen |
|---|---|---|
| M0–M4 | [Startkonfiguration](../protocol/startkonfiguration.json), [Manifest](../M0_MANIFEST.json) | `D:/mandala/mandala-memory-results/research/research-e19650a0a0.json` (+ Auswertung v2 nach Review R1/R2) |
| M9 | [Herleitung](M9_HERLEITUNG.md) (hashgeschützt), [Vorhersagen](../protocol/m9_frozen_predictions.json) (SHA-256 `1e872cec…`, Stand `6f8a812`), [Erratum 1](M9_ERRATUM_1.md) | `D:/mandala/mandala-memory-results/m9/m9-evaluation--8d353dbc88.json` |
| M10 | [Plan](M10_PLAN_ABLENKUNG.md), [Protokoll](../protocol/m10_protokoll.json), [Freeze-Datensatz](../protocol/m10_freeze.json), Tag `m10-freeze` (7b31300) | `D:/mandala/mandala-memory-results/m10/research/m10-research-20261003T230058-47d41706.json`; Integrationsbericht `m10/INTEGRATION_M10.md` |
| M11 | [Plan](M11_PLAN_AUSLESE.md), [Protokoll](../protocol/m11_protokoll.json), [Referenzen](../protocol/m11_references.json), [Freeze-Datensatz](../protocol/m11_freeze.json), Tag `m11-freeze` (1a5423f), [Ergebnis](M11_ERGEBNIS.md) | Versuch 2: `D:/mandala/mandala-memory-results/m11/research/m11-research-20261005T114106-e996e301.json` (+ `.evaluation.json`); Versuch 1 (abgebrochen, gesperrt), Abbruchbericht und Nachtrag im selben Ordner; `m11/INTEGRATION_M11.md` |

Unabhängige Reviews von Astra liegen in den `astra-*`-Ordnern unter `D:/mandala/mandala-memory-results/`. Jeder Befund wurde vor seiner Korrektur reproduziert und mit einem eigenen Regressionstest abgesichert (Details in der Roadmap).

## Mögliche nächste Frage (noch nicht geplant)

**Robustheit des gelernten Auslesens:** Funktioniert das in M11 trainierte MLP auch bei leicht veränderter Ablenkungsstärke oder verändertem Messrauschen, ohne neu trainiert zu werden? Und wie verhält sich LDA dabei im Vergleich? Für diese Frage gäbe es zuerst einen eigenen Plan mit vorab festgelegten Verschiebungen und Kontrasten, wie in M10 und M11.
