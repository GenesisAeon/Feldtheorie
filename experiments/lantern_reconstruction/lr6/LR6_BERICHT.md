# LR6 – Entwicklungsabnahme und Freeze-Kandidat (Bericht)

**Stand:** 2026-10-09, Branch `lantern-reconstruction`.

**Grundlage:** Astras Abschluss des Recovery-Gates (`astra-lr5-93f4b95-review/REVIEW.md`, GO für LR6) und der Plan, § 12, § 14 und § 19.5.

Es gab **keinen Freeze, keinen Forschungslauf, keinen Merge und keinen Push öffentlicher Repositories.** Der Freeze-Kandidat wird separat geprüft.

| Commit | Inhalt |
|---|---|
| `99e6480` | Forschungsmodus nur mit Freeze; Studienauswertung im Freigabe-Gate |
| `f9ea14d` | Betriebshandbuch `lr6/BETRIEB.md` |
| `5905dcd` | Kontrollalarm-Protokoll v2, nach der Untersuchung der ersten Abnahme |
| dieser Commit | zweite Entwicklungsabnahme, Freeze-Kandidat, Bericht |

## 1. Ausführbarkeit des Kandidaten (`99e6480`)

- **Forschungslauf nur mit Freeze.** Er entsteht ausschließlich über `runs.create_research_run(runs_root, run_id)`; diese Funktion nimmt keinen weiteren Parameter.
  - Er verlangt `protocol/freeze.json` mit Schema `lantern-freeze-v1`, Status `frozen` und `approved_by`.
  - Diese Datei muss den SHA-256 der LF-normierten Kandidatendatei und die Code-Identität binden; letztere muss gleich dem aktuellen Code sein (die Freeze-Datei selbst ausgenommen).
  - Alle Parameter stammen aus dem Kandidaten. Die Forschungsstudie darf weder die Entwicklungsstudie sein noch im Aeon-Ausschlussbereich liegen.
  - `execute()` prüft den Freeze vor jedem Fortsetzen erneut.
  - In diesem Repository gibt es **keine** `freeze.json`; jeder Forschungslauf wird verweigert (Test).
- **Studienauswertung** (`release.hypothesis_section` / `study_evaluation`, Plan § 9). Sie greift nur bei einem *interpretierbaren* Forschungslauf.
  - **Aufgabe A** ist eine Schätzung ohne Erfolgsschwelle: Mittelwert, SD und punktweise 95-%-t-Intervalle von A_lantern, A_uncoupled und deren gepaarter Differenz.
  - **Aufgabe B** prüft H-B1 und H-B2 einseitig, mit Holm über genau diese zwei Tests und Bonferroni-Intervallen.
  - Dazu kommt die **zulässige Aussage** nach der Ergebnistabelle des Plans.
  - Bei Entwicklungs-, Smoke- und blockierten Forschungsläufen steht `not_evaluated` mit Begründung.

## 2. Entwicklungsabnahme und Untersuchung

**Erster Abnahmelauf** `lr6-acceptance-20261009T151633Z` (Entwicklungsstudie, Kontexte 0–3, 1000/250/1000, alle Bedingungen und drei Kontrollkurven):
- technisch vollständig, 392/392 Zellen, 1382 s;
- wissenschaftlich **gesperrt**: Beide LR5-A1-Alarme schlugen an, **nur** in `permuted_targets|A|1.0` (G = +0,0048, Holm-p = 0,0012).

**Untersuchung** (`results/lantern/lr6_acceptance_investigation/UNTERSUCHUNG.md`):
- Ein Decoder mit permutierten Labels ist eine zufällige Abbildung von Merkmalen, die u kodieren. Seine Vorhersagen **können** daher von den Testzielen abhängen; im Diagnosefall war das nachgewiesen. (Eine konstante Abbildung wäre ein Gegenbeispiel zu „zwangsläufig“, so stand es zuerst hier; korrigiert nach Astras Review `29af52f`.) Der Test mit festen Vorhersagen war für diese Zellen der unpassende Vergleich; den Konstruktionsfehler habe ich in LR5 gemacht.
- Ein schwacher Zusatzkanal war die λ-Wahl auf echten Validierungszielen.
- Reset und Nullimpuls blieben unauffällig. Die Untersuchung hat einen unpassenden Nullvergleich nachgewiesen und **keinen zusätzlichen Befund eines Pipeline-Lecks** ergeben. Aus unauffälligen Kontrollen folgt kein allgemeiner Beweis, dass es kein Leck gibt.

**Entscheidung Johann** (Variante „Passende Nullverteilung“) führte zum **Protokoll v2** (`5905dcd`, `protocol/control_alarms.json`):
- Bei `permuted_targets` werden Trainings- **und** Validierungsziele permutiert.
- Die vier Alarmzellen bekommen eine **Neufit-Nullverteilung**: B = 9999 vollständige Neufits mit neuen Permutationen, exakt `fit_ridge` plus Scoring (Abweichung < 1e-12), vektorisiert 5,9 s je Zelle und Kontext. Sie wird im Lauf als `null.npz` gespeichert, an den Datensatz gebunden und beim Lesen und Fortsetzen geprüft.
- Auf synthetischen Daten reproduziert: Die alte Nullverteilung schlägt beim labelfreien Decoder an (Seeds 4 und 9), die neue nicht. Ein echtes Leck erkennt die neue weiterhin (p = 1/(B + 1)).

**Zweiter Abnahmelauf** `lr6-acceptance-20261009T165010Z` (`5905dcd`):

| Prüfung | Ergebnis |
|---|---|
| Status / Zellen | `complete`, 392/392 verifiziert, keine Uhrenlücke |
| technisch vollständig | **ja** |
| wissenschaftlich interpretierbar | **ja**, keine Sperre |
| LR5-A1-Alarme | **beide still**; alle 12 Zellen mit G < 0, kleinster Holm-p **0,6492** (≈ 0,65; zuerst zu scharf als „≥ 0,65“ gerundet) (`permuted_targets|A|1.0`: G = −0,0006, p = 0,53) |
| Strukturprüfungen (Reset/Nullimpuls) | bestanden und nachgerechnet |
| Pipeline-Gate A, G0 | 0,978 > 0,90 |
| Konvergenzgate | gebunden, bestanden |
| Hypothese | `not_evaluated` (Entwicklungslauf) |
| Laufzeit | Ausführung 1341 s für 4 Kontexte, Freigabebericht 33 s; Artefakte 42 MB |

Die G-Werte beider Läufe sind **Entwicklungswerte** und dienen nicht der Wahl von Protokollwerten. Im Kandidaten sind sie als bekannte Information deklariert.

## 3. Freeze-Kandidat (`lr6/freeze_candidate.json` + YAML)

Erzeugt mit `tools/lr6_freeze_candidate.py`. Alle Werte stammen aus Code und Protokoll, nichts ist abgetippt. Die Datei wurde exklusiv geschrieben und wird nie ersetzt.

| Bestandteil | Inhalt |
|---|---|
| Code | Code-Identität aller Produktionsmodule und Protokolldateien (gleich `5905dcd`, sauber); Python 3.11.9, NumPy 2.2.6, SciPy 1.15.3 |
| Quellen | Snapshot-Pins (kanonisch, Manifest), `config_sha256`, Plan v2.0 + AE-01 |
| **Masterseed** | **1431972670**, mit `secrets.randbelow(2**32)` in **einem** Versuch gezogen; neu gezogen worden wäre nur im Ausschlussbereich oder bei Gleichheit mit der Entwicklungsstudie; nie nach einem Ergebnis gewählt |
| Raster | Kontexte 0–19, 1000/250/1000, 4 Bedingungen, Aufgaben A/B, 7 Zeiten, 3 Kontrollkurven; 1960 Zellen; RK4, dt 0,02; 20 000 Surrogatvorschläge |
| Decoder | Ridge (Zielfunktion, Standardisierung, λ-Raster, Auswahl, Projektion) |
| **MLP** | **Vorschlag: Verzicht.** Ridge ist primär und blockiert nicht auf dem MLP; das MLP ist weder implementiert noch validiert; Plan § 13 nennt es als Erstes zu streichen. Ein späteres MLP bräuchte eine eigene Protokollversion. |
| Ströme | Schlüssel, Rollen, Splits, Grenze 2³², Decoder-Zusätze 1–4 |
| Inferenz | Kontext als Einheit, K21-Raster, Aufgabe A als Schätzung, H-B1/H-B2 mit Holm/Bonferroni, zulässige Aussagen |
| Kontrollregeln | Kontrollalarm-Protokoll v2 vollständig, B = 9999, Strukturprüfung, Pipeline- und Konvergenzgate; Freigaberegel befürwortet |
| Budget | Gemessen 1341 s für 4 Kontexte. **Hochgerechnet 6705 s ≈ 1,86 h** für 20 Kontexte (Entwurfsbudget 2 h, Reserve rund 7 %, rechnerabhängig). Artefakte rund 210 MB. |
| Bekannte Information | Aeons Pilot (ausgeschlossene Seeds); Entwicklungsstudie 2026100803: Kontexte 0/1 (Konvergenzgate) und 0–3 (beide Abnahmeläufe) gesehen |
| Offene Befunde | GitHub-CI nie gelaufen, Python 3.12 lokal nicht verfügbar; verwaiste Verwaltungssperren werden absichtlich von Hand behandelt; Forschungslauf strikt an die Software des Freezes gebunden |

Der Kandidat ist an den Code gebunden. Ein Test schlägt fehl, sobald ein Produktionsmodul oder eine Protokolldatei sich ändert; ein veralteter Kandidat kann also nie still anderen Code abdecken.

## 4. Prüfungen

- **Tests:** 425 (bisher 393, dazu 26 in `tests/test_lr6.py` und 6 in `tests/test_lr5_runs.py` zur Neufit-Nullverteilung). Die volle Suite lief am Code-Stand `5905dcd` mit 422/422; danach kamen nur die drei Kandidatentests hinzu, die mit `test_lr6.py` (26/26) bestanden haben.
- **Mutationskampagne:** 68 ausgeführt, 66 erkannt, 2 äquivalent (L2, R4b), 0 offene Überlebende.
  - LR6: 8/8, S7 erst nach einem neuen Test.
  - Kontrollprotokoll v2: 6/6, V4–V6 erst nach neuen Tests.
- **CI-Workflow:** um `test_lr6.py` erweitert (13 Testdateien, durch einen Test erzwungen).

## Offen

- **Eigene Prüfung des Freeze-Kandidaten** durch Astra.
- **Entscheidungen von Johann und Astra:** MLP-Verzicht (Vorschlag); die Budgetreserve von rund 7 %; der Freeze selbst (`protocol/freeze.json` als eigener, dokumentierter Schritt).
- Danach LR7 (Forschungsrunde) nur nach einer **separaten Prüfung vor dem Forschungsstart**.
