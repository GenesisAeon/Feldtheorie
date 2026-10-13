# LR7 Lantern-Rekonstruktion: Ergebnisbericht des Forschungslaufs

**Stand:** 2026-10-13, Version 2. Verfasst von der Claude-Haupt-Session.

**Version 2** setzt die Korrekturen R1–R7 aus Astras Review ASTRA-2026-10-12-04 um. Durchgeführt hat es Codex-Astra lokal (Review-Repo `astra-reviews` `f50dee1`). Geändert ist nur der Wortlaut. Rohdaten, Kennzahlen und Hypothesenergebnis sind unverändert. Version 1: `ERGEBNISBERICHT_LR7_v1_vor_review.md`.

**Review-Ergebnis:**
- Identität geprüft: alle 29 Code-Hashes, 1960 Zellordner.
- 294 Zellen aus den vorab gewählten Kontexten 0, 9 und 19 nachgerechnet, größte Differenz 0.
- Die Hauptstatistik über alle 20 Kontexte ist unabhängig nachgerechnet und stimmt innerhalb 2e-13.
- Kein Anlass für eine Wiederholung.

## Identität

| | |
|---|---|
| Lauf | `runs/lr7-research-20261012T124802Z` (Art `research`) |
| Studie | 1431972670, eingefroren auf `5ccad90`; Startwerkzeug `99ec950` |
| Start / Ende | 2026-10-12 12:48 / 14:50 UTC; Rechnen 7356 s, Freigabe 187 s |
| Laufidentität | `2e61024776cd1cad870df1e01536ef1df6e96c0c9234e56076e67332027639ae` |
| `release_report.json` | SHA-256 `1ec33ae8c70ebde942df14b86ecdd526ba8614ff4b1f64b871377b052eea342c` |
| `run.json` | SHA-256 `71a28ee0b3711558fcfcc7171dd1573da32d419126d11f24e30b73e82e5f8603` |
| `events.jsonl` | SHA-256 `6032e0550069328e7728d469b8f0ab6286aee86102e0f0a624c6c48bf55c3dd2` |
| Umgebung | Lab-venv: Python 3.11.9, NumPy 2.2.6, SciPy 1.15.3 |

Direkt vor dem Start war die Bereitschaftsprüfung grün: Der Code entsprach dem Freeze-Kandidaten, es gab keine Softwareprobleme, und die Probe ohne Wirkung war erfolgreich. Gestartet hat Johann nach Astras Vorstartreview (ASTRA-2026-10-12-01: kein Einwand).

## Freigabe-Gate (vom Werkzeug ausgewertet, vorab festgelegte Regeln)

| Feld | Ergebnis |
|---|---|
| technisch vollständig | **ja**: 1960 von 1960 Zellen verifiziert, keine Probleme |
| Zeitlücken | keine vom Laufprotokoll gemeldete Zeitlücke (0 `clock_gap`-Ereignisse); einen Ruhezustand des Betriebssystems belegt das allein nicht (R7) |
| Konvergenz-Gate | **bestanden**: max \|ΔG\| = 8,7·10⁻¹⁰, max \|ΔA\| = 2,5·10⁻¹⁰, bei einer Grenze von 0,01 |
| Strukturprüfungen | reset und zero_impulse in allen 20 Kontexten erfüllt |
| Pipeline-Gate A bei G₀ | 0,9773 in allen vier Bedingungen |
| Kontroll-Alarme | **keiner**. 12 Zellen (permuted_targets, reset, zero_impulse × Aufgabe A/B × Pause τ = 1 und τ = 5), Holm über 12 Zellen, α = 0,01. Kleinstes Holm-p: 0,156. |
| wissenschaftlich interpretierbar | **ja**, keine `scientific_blocks` |
| Hypothesenstatus | `evaluated` |

**Lesehilfe:**
- **G** ist der Rekonstruktionsgewinn gegenüber der Nullvorhersage: G = 3·Mittel(u² − (Vorhersage − u)²).
  - G = 0 bedeutet den gleichen empirischen quadratischen Fehler wie die Vorhersage „0“.
  - 1 ist die theoretische Normierung im Erwartungswert der Zielverteilung, **keine** exakte Obergrenze einer endlichen Stichprobe (R2). In Kontext 0 ergibt eine perfekte Rekonstruktion empirisch G = 1,004.
  - Die Kennzahl S = 1 − 3·MSE wäre bei perfekter Rekonstruktion exakt 1.
- **A** ist G, über das Zeitgitter des Protokolls gewichtet gemittelt: sieben Pausen von τ = 0 bis 10, Trapez auf log(1+τ).
- **Intervalle (R6):**
  - Die deskriptiven 95-%-Intervalle sind punktweise t-Intervalle über 20 Kontexte (df = 19), modellbasiert und **einzeln** zu lesen.
  - Anders die beiden Bonferroni-Intervalle (97,5 %) zu H-B1/H-B2: Unter den t-Modellannahmen liefern sie für genau diese Zweierfamilie eine gemeinsame Abdeckung von mindestens 95 %. Für andere Tabellenwerte oder Zeitpunkte gilt das nicht.
  - Der generische Intervalltext im eingefrorenen Freigabebericht bleibt unverändert.

## Aufgabe A: Spurerhalt (alle Knoten beobachtbar)

Diese Aufgabe ist laut Plan §9 eine **Schätzung ohne Erfolgsschwelle**; es gibt keinen Test.

| Bedingung | Mittel A | 95-%-Intervall |
|---|---:|---|
| ungekoppelt (Referenz) | 0,977 | [0,969; 0,985] |
| Lantern | 0,517 | [0,480; 0,553] |
| Differenz Lantern − ungekoppelt (gepaart) | **−0,461** | [−0,498; −0,423] |

In **allen 20 Kontexten** liegt Lantern unter der ungekoppelten Referenz. Die Spanne bei Lantern reicht von 0,41 bis 0,67, die der Referenz von 0,93 bis 1,00.

**Lesart (korrigiert nach R1):**
- Über das festgelegte Zeitgitter beträgt der gewichtete Rekonstruktionsgewinn mit Lantern-Kopplung im Mittel 0,517, ohne Kopplung 0,977. Das Verhältnis der Mittelwerte ist 0,529.
- „Ungefähr halbiert“ bezieht sich **nur** auf diesen aggregierten Gewinn. Es betrifft weder die Informationsmenge noch die Haltedauer noch jede einzelne Pause.
- Das positive Zeitmittel belegt **weder eine dauerhafte Spur noch eine bestimmte Gedächtnisdauer**. Es kann vollständig von frühen Pausen getragen sein. In Kontext 0 etwa ist A = 0,428, aber bei τ = 10 ist G = −0,0014, also auf Nullniveau.
- Version 1 enthielt hier den Satz „Ein Teil bleibt dauerhaft lesbar“. Diese Überdeutung ist zurückgenommen.

## Aufgabe B: verteilte Auslesbarkeit (nur unbeschriebene Knoten)

| Bedingung | Mittel A | 95-%-Intervall |
|---|---:|---|
| Lantern | −0,0010 | [−0,0015; −0,0005] |
| Stärke-Surrogat | −0,0008 | [−0,0013; −0,0003] |
| gleichmäßige Gesamtkopplung | −0,0012 | [−0,0017; −0,0007] |
| ungekoppelt | −0,0012 | [−0,0017; −0,0007] |

Vorab festgelegte Hypothesen (Plan §9; einseitige t-Tests gegen die Marge 0,05; Holm über genau diese zwei; Familien-α 0,05):

| Hypothese (Forschungsalternative) | Mittel | Holm-p | Bestätigungskriterium erfüllt |
|---|---:|---:|---|
| H-B1: E[A_Lantern] > 0,05 | −0,0010 | 1,0 | **nein** |
| H-B2: E[A_Lantern − A_Surrogat] > 0,05 | −0,0002 | 1,0 | **nein** |

Bonferroni-Intervalle (97,5 %): H-B1 [−0,0016; −0,0004], H-B2 [−0,0005; +0,0001].

Die Zeilen H-B1 und H-B2 sind die positiven Forschungsalternativen (R4). Ihre Nullhypothesen (Effekt ≤ 0,05) werden **nicht verworfen**. p = 1 ist keine Wahrscheinlichkeit dafür, dass eine Nullhypothese wahr ist.

**Lesart (korrigiert nach R5):**
- Mit dieser Kodierung und diesen Ridge-Auslesern wurde **kein** vorab geforderter Gewinn über 0,05 nachgewiesen. Ebenso wurde kein Vorteil über 0,05 gegenüber dem Stärke-Surrogat nachgewiesen.
- Die vier geschätzten Gewinne liegen nahe null, leicht darunter.
- Das ist **kein** Beleg für Gleichheit oder Äquivalenz der Bedingungen. Es ist auch kein Beleg für die Abwesenheit jeder gespeicherten Information und kein Ergebnis für andere Dekoder. Version 1 enthielt hier den Satz „Lantern unterscheidet sich weder vom Surrogat noch von der Referenz“; er ist zurückgenommen.
- Vorab erlaubte Aussage (aus dem Freigabebericht): *„the pre-specified evidence was not reached; this is no general impossibility proof“*. Die vorab festgelegte Evidenz wurde also nicht erreicht. Das ist kein allgemeiner Unmöglichkeitsbeweis.

## Aussagegrenzen

- Alles gilt für **dieses rekonstruierte Modell**, die eingefrorene Studie (20 Kontexte, Schreibamplitude 0,35, sieben Pausen von τ = 0 bis 10), die festgelegten Ridge-Dekoder und das Zeitgitter. Nichts davon ist eine Aussage über andere Netze, andere Dekoder oder biologische Systeme.
- Das negative Ergebnis in Aufgabe B schließt verteilte Auslesbarkeit mit anderen Lesern oder Kodierungen nicht aus.
- Das Ergebnis in Aufgabe A ist eine Schätzung. Ob 0,52 „gut“ oder „schlecht“ ist, legte das Protokoll bewusst nicht fest.
- Keine Kontroll-Alarme heißt: Kein Leck und keine Zielabhängigkeit wurden erkannt. Das ist kein Unabhängigkeitsbeweis; so steht es in der Regel selbst.
- Die negativen G-Werte in Aufgabe B liegen in der Größenordnung von 10⁻³. Sie bedeuten „minimal schlechter als die Nullvorhersage“. Eine Deutung als Effekt war nicht vorab festgelegt, und ich gebe ihnen keine.

- **Betrieb (R7):** Rechnen 7356 s und Freigabe 187 s ergeben rund 2,10 h. Das liegt im Betriebsfenster von 2,5 h, aber über der älteren Hochrechnung von knapp 2 h.
- **Prüftiefe des Reviews:** eine Stichprobe von 294 Zellen. Die 9999 Permutationen der Kontrollzellen wurden nicht unabhängig neu erzeugt, und es wurden keine Zustände neu simuliert.

## Nächste Schritte

1. ✅ Review durch Astra (ASTRA-2026-10-12-04, lokal ausgeführt von Codex-Astra) abgeschlossen; R1–R7 in dieser Version umgesetzt. Ein gezielter Dokumentationsabgleich dieser Punkte genügt.
2. Erst nach Astras Review und Johanns Entscheidung: Ergebnis-Commit im Branch `lantern-reconstruction` (Bericht, ohne Rohdaten), danach eventuell ein Push.
3. Der Lauf-Ordner bleibt unverändert. Hier wird nichts nachträglich umgerechnet.
