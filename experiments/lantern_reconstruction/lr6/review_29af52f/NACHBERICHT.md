# Nachbericht zu Astras Review `LANTERN_LR6_REVIEW_29af52f` (2026-10-09)

**Ausgang:** Lantern `29af52f`, Review-Paket `0091f96`. Urteil des Reviews: noch nicht einfrieren, vier Befunde R1–R4.
**Stand jetzt:** Code `b0da0c7`, alter Kandidat abgelöst `df3065b`, neuer Kandidat im darauf folgenden Commit.

Es gab **keinen Freeze und keinen Forschungslauf**. Es wurden keine Forschungs-Kontexte gerechnet. Das Paket von Astra wurde nur in einer Temp-Kopie entpackt (46/46 Prüfsummen in Ordnung).

## 1. Gegenproben vor jeder Änderung (Stand `29af52f`)

| Befund | Gegenprobe | Ergebnis am Ausgangsstand |
|---|---|---|
| R1 | eigenes Skript `repro_r1_r4_baseline.py`; Software auf 3.12.14 simuliert, synthetischer Freeze in Temp | Lauf angelegt, Manifest mit Python 3.12.14, `check_resumable` akzeptiert |
| R2 | Astras `reproduce_lr6_review.py` unverändert | beobachtet −0,011351993312996786, Null −0,011351993312996828 (Differenz 4,16·10⁻¹⁷); b = 0, p = 0,0001, Holm 0,0012, Abhängigkeitsalarm **an** |
| R3 | dasselbe Skript | fremde Null samt gültigem Datensatzblock aus Kontext 1 in Kontext 0: **akzeptiert** |
| R4 | Kandidatentest unter simuliertem Python 3.12.14 | Assertion `c['software'] == runs.software()` falsch |

Belege: `baseline_astra_script_RESULTS.json`, `baseline_repro_r1_r4_output.json`.

## 2. Korrekturen (`b0da0c7`)

**R2 – Gleichstände (Kontrollalarm-Protokoll v3).**
- *Gleichstandsregel:* Ein Nullwert zählt als ≥ beobachtet, wenn er ≥ beobachtet − 10⁻¹⁰ ist. Gleichstände zählen also zum oberen Schwanz; das kann p nur erhöhen.
  - Die Regel gilt für beide Nullverteilungen: die Neufit-Null und die Null mit festen Vorhersagen (`metrics.upper_tail_count`).
  - Die Toleranz ist absolut, weil G null sein kann.
- *Gleicher Auswertungspfad:* Der beobachtete Gewinn jeder Neufit-Alarmzelle wird zusätzlich mit demselben vektorisierten Code wie die Nullziehungen berechnet, mit den eigenen Permutationen der Zelle (`training.refit_gains`, gemeinsamer Kern `_RefitCore`).
  - Weicht er vom aufgezeichneten Wert (fit_ridge plus Scoring) um mehr als 10⁻¹² ab, wird die Zelle abgewiesen.
  - Beide Werte und die Abweichung werden gespeichert.
- *Begründung des Epsilons, aus der Fehlergröße und vor jedem Forschungslauf:*
  - G ist beschränkt (−12 ≤ G ≤ 3).
  - Die geprüfte Pfadabweichung ist ≤ 10⁻¹²; gemessen auf Entwicklungsdaten ≤ 7,5·10⁻¹⁸ (`numerics_development.json`).
  - Die Streuung echter Nullwerte liegt bei SD 3,8·10⁻⁵ bis 2,5·10⁻³.
  - In Abnahme 2 lag in keiner der zwölf Zellen ein Nullwert innerhalb von 10⁻¹⁰; der kleinste Abstand war 1,3·10⁻⁹.
- *Abnahmeprüfungen:*
  - Astras Fall ergibt p = 1 und keinen Alarm.
  - Exakte Gleichstände (positiv, negativ, null) zählen.
  - Werte außerhalb der Toleranz werden auf beiden Seiten richtig behandelt.
  - Chunkgrößen 1, 7, 50 und 128 liefern bitgleiche Ergebnisse, ebenso die expliziten Permutationen.
  - Die unabhängige Normalgleichungs-Referenz stimmt (< 10⁻¹²).
  - Ein eingespeister Lernkanal löst beide Alarme weiterhin aus (p = 1/(B+1)).
  - Konstante Merkmale bleiben zulässig.
  - Die Null mit festen Vorhersagen gibt bei konstanten Vorhersagen p = 1.

**R1 – Softwarebindung.**
- `frozen_candidate()` verlangt exakt Python, NumPy und SciPy des Kandidaten (`runs.software_problems`).
- Das wird geprüft, bevor ein Laufordner entsteht, und vor jedem Start oder Fortsetzen erneut.
- Ein fehlender, unvollständiger oder nicht-textueller Block wird abgewiesen.
- Ein in falscher Umgebung angelegtes Manifest lässt sich weder in dieser noch in der eingefrorenen Umgebung starten. Zusammen erzwingen `check_resumable` (aktuell = Manifest) und `frozen_candidate` (aktuell = Freeze), dass Manifest und Freeze gleich sind.
- Abnahmeprüfungen:
  - Python, NumPy und SciPy einzeln abweichend: jeweils abgewiesen, ohne Laufordner.
  - Sechs defekte Softwareblöcke: abgewiesen.
  - Erneute Prüfung vor dem Start.
  - Der Fall des falsch angelegten Manifests.

**R4 – Testvertrag.**
- Die allgemeinen Tests prüfen das Schema der Softwareangaben, nicht die Gleichheit mit diesem Rechner.
- Freeze- und Nicht-Freeze-Fälle laufen über isolierte Fixtures (`FREEZE_FILE` umgebogen) und hängen nicht vom Checkout ab.
- Der echte Kandidat mit einem synthetischen Freeze-Fixture:
  - In fremder Umgebung (3.12.14) lehnt er ab; das ist ein bestandener Negativtest.
  - In seiner eigenen Umgebung nimmt er an.
- Die rechnerabhängige Bereitschaftsprüfung ist getrennt: `runs.research_readiness()` und `tools/lr7_readiness.py`. Sie benennt jede Abweichung und endet nur mit 0, wenn der Start erlaubt wäre.
- Kein Test ist maskiert oder übersprungen; der 3.12-CI-Job ist unverändert.

**R3 – Herkunftsbindung der Neufit-Null (Record-Schema v2).**
- `record['null'].provenance` enthält: Laufidentität, Studie, Kontext und Fingerabdruck, Bedingung, Kontrolle, Aufgabe, Zeit und Zeitindex, B, Stromschlüssel, Algorithmus, Protokollschema, Modellidentität und Identität der Testziele.
- `verify_record` vergleicht diese Angaben mit Werten, die aus Lauf, erwarteter Zelle, Kontext und dem verifizierten Modell und Vorhersagen dieser Zelle gebildet werden, **nie aus dem Null-Datensatz selbst**.
- Die Refit-Pfad-Prüfung muss zum aufgezeichneten Score passen.
- Die Identitäten aller sechs Eingabearrays werden gespeichert und beim Fortsetzen mit den neu berechneten verglichen.
- Abnahmeprüfungen:
  - Das Original wird angenommen.
  - Null-Datei plus gültiger Block aus einem anderen Kontext, einem anderen Zeitpunkt oder einem anderen Lauf wird abgewiesen. Im Lauf-Fall sind die Nullarrays sogar bitgleich; nur die Herkunft unterscheidet sie.
  - Der Freigabebericht sperrt in diesen Fällen.
  - Ein bearbeiteter Block (Herkunft entfernt, Abweichung, beobachteter Wert, fehlende Eingabe) wird abgewiesen.
  - Geänderte Eingabeidentität beim Fortsetzen führt zu einem Integritätsfehler.
- Orphan- und Wiederaufnahmetests bleiben unverändert grün.
- Alte Abnahmeartefakte (Record-Schema v1) wurden nicht verändert. Mit dem neuen Code sind sie als alte Belege lesbar, aber nicht mehr verifizierbar; das ist gewollt.

**Redaktion** (LR6-Bericht, Roadmap, Protokoll v2-Text, Runner-Docstring; Nachtrag in der Untersuchung, deren ursprünglicher Text als Beleg stehen bleibt):
- „zwangsläufig“ → „können abhängen; im Diagnosefall nachgewiesen“.
- „Kein Pipeline-Leck“ → „unpassender Nullvergleich nachgewiesen, kein zusätzlicher Befund eines Pipeline-Lecks; kein allgemeiner Abwesenheitsbeweis“.
- Kleinster Holm-p **0,6492** (aus `release_report.json` nachgeprüft: `permuted_targets|B|1.0`, b = 540).
- Zeitfenster von mindestens 2,5 h im Betriebshandbuch.

## 3. Wirkung auf die Entwicklungsabnahme

Dritte Entwicklungsabnahme `lr6-acceptance-20261009T192821Z` am reparierten Code (Code-Identität = die des neuen Kandidaten; Git-Feld des Laufs `29af52f`, *dirty*, weil sie vor dem Commit lief):

| Prüfung | Ergebnis |
|---|---|
| Status / Zellen | `complete`, 392/392, keine Uhrenlücke |
| technisch vollständig / interpretierbar | ja / ja |
| Alarme | beide still; die zwölf Alarmzellen sind **identisch** zu Abnahme 2 (G, p, Holm-p), kleinster Holm-p 0,6492 |
| Bitgleichheit mit Abnahme 2 | alle 392 Scores und Modellidentitäten, alle 16 Nullarrays |
| Refit-Pfad-Abweichung | höchstens 7,5·10⁻¹⁸ (16 Zellen) |
| G0 Aufgabe A | 0,978 |
| Laufzeit | Ausführung 1364 s (Abnahme 2: 1341 s), Freigabebericht 30 s |

Die numerische Regel ändert an den Entwicklungsbelegen also nichts.

## 4. Neuer Kandidat (`lr6/freeze_candidate.json`)

- **Ablösung:** Er ersetzt den Kandidaten von `29af52f`. Der alte liegt unverändert in `lr6/superseded/freeze_candidate_29af52f.json`; Hash und Code-Identität sind im neuen gebunden.
- **Masterseed 1431972670 übernommen:** nicht neu gezogen, mit Verweis auf die ursprüngliche einmalige Ziehung per `secrets`.
- **Code:** Code-Identität `670d9352…`, Git `df3065b`, sauber; Software Python 3.11.9, NumPy 2.2.6, SciPy 1.15.3.
- **Ströme:** Decoder-Zusätze 1–4 vollständig.
- **MLP:** **Verzicht**, von Astra befürwortet; bindend erst mit der Freeze-Freigabe. Aussagen sind auf die untersuchte Ridge-Auslesbarkeit beschränkt.
- **Bekannte Information:** alle drei Abnahmeläufe namentlich. Präzisiert: Numerische Studienparameter wurden nicht nach Forschungsresultaten gewählt; der Kontrolltest wurde nach dokumentierten Entwicklungsdiagnosen revidiert (v2, v3).
- **Reichweite:** Positive Ergebnisse betreffen Dynamik, Messabbildung, Ridge-Auslesbarkeit und Referenz; keine Übertragung. Ein negatives Ergebnis heißt: die vorgegebene Evidenz wurde nicht erreicht.
- **Budget:**
  - hochgerechnet **6820 s ≈ 1,89 h** Ausführung plus etwa 151 s Freigabe;
  - Reserve gegen 7200 s nur **380 s (5,3 %)**, knapper als zuvor (6,9 %), weil Abnahme 3 23 s länger lief;
  - Betriebsfenster mindestens 9000 s (2,5 h).
  - Das ist eine lineare Hochrechnung, keine Obergrenze.

## 5. Prüfungen

- **Volle Lantern-Suite: 466/466** am Kandidatenstand. Vorher 425; dazu kommen 41 Tests in `test_lr6.py`.
- **Gezielte Mutanten:**
  - 13 neue (T1–T6, P1–P2, N1–N5), alle erkannt, jeweils vom zuständigen Regressionstest. V3 und V5 wurden auf den geänderten Zielzeilen erneut ausgeführt; beide erkannt.
  - Die beiden an die Code-Identität gebundenen Kandidatentests werden bei Mutanten abgewählt, weil sie sonst jeden Mutanten trivial töten würden.
  - Gesamt: **81 ausgeführt, 79 erkannt, 2 äquivalent (L2, R4b), 0 Überlebende.**
- **Astras Gegenprobenskript nach der Reparatur:**
  - Angepasst sind nur der Code-Pin, `null_meta` und der Importpfad (`reproduce_lr6_review_ADAPTED_b0da0c7.py`).
  - R2: p = 1, kein Alarm. R3: abgewiesen („provenance differs in context_fingerprint, context_id, model_identity, stream, test_targets“).
  - Den R1-Fall kann dieses Skript hier nicht zeigen, weil dieser Rechner die eingefrorene Umgebung hat. Die Regressionstests decken ihn ab.

## 6. Offen

- **Astras gezielte Nachprüfung** dieses Standes.
- Danach die **Freeze-Entscheidung** (Johann/Astra, `protocol/freeze.json` als eigener Commit). Dazu gehört die Frage, ob die Reserve von 5,3 % mit dem 2,5-h-Fenster akzeptiert wird.
- **LR7** nur nach dem gesonderten Vorstartreview.
- Der GitHub-CI-Workflow ist nie gelaufen; Python 3.12 ist lokal nicht verfügbar.
