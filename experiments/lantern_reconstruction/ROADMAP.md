# Lantern-Rekonstruktion: Roadmap

Grundlage: [Implementierungsplan Version 2.0, § 14](reference/review_package_2026-10-07/LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md).

| Paket | Inhalt | Status |
|---|---|---|
| LR0 | Lokaler Bestand: Worktree, Regeln, Hashvergleich der elf Quellen, Inventar, Sicherung | ✅ erledigt, siehe [Bericht](lr0/LR0_BERICHT.md); wartet auf Prüfung |
| LR1 | Snapshot und Import: separater Legacy-Prozess, kanonische Matrix, Importmanifest | ✅ erledigt, siehe [Bericht](lr1/LR1_BERICHT.md); wartet auf Prüfung |
| LR2 | Numerischer Kern: gebatchte Dynamik, lineares H(t), Orakel | ✅ erledigt, siehe [Bericht](lr2/LR2_BERICHT.md). ODE-Gate: Euler nicht bestanden (bleibt dokumentiert), **RK4 bestanden** (Planänderung AE-01); Decoderteil in LR4 bestanden; wartet auf Prüfung |
| LR3 | Aufgaben A/B und Referenzen: Beobachtungen, Ströme, Surrogate | ✅ erledigt, siehe [Bericht](lr3/LR3_BERICHT.md); Fixes nach Astras Nachprüfung, von ihr nachgeprüft (`6680618`) |
| LR4 | Ridge und Evaluation | ✅ erledigt, siehe [Bericht](lr4/LR4_BERICHT.md). Ridge per NumPy (LR0-O1); Decoder-Konvergenzgate bestanden; R1/R2 nach `REVIEW_LR4` geschlossen und von Astra nachgeprüft (`25ba293`, GO für LR5) |
| LR5 | Laufverwaltung und CI | ✅ erledigt, siehe [Bericht](lr5/LR5_BERICHT.md). LR5-A1, Artefaktkette, Resume, Freigabe-Gate, Budget, CI-Workflow, Mutationskampagne; wartet auf Prüfung. Freigaberegel LR5-A1 vor dem Freeze zu entscheiden |
| LR6 | Entwicklungsabnahme und Freeze-Kandidat | ✅ erledigt, siehe [Bericht](lr6/LR6_BERICHT.md). Entwicklungsabnahme sauber (nach Kontrollprotokoll v2); Freeze-Kandidat `lr6/freeze_candidate.json`; wartet auf Prüfung und Freeze-Entscheidung |
| LR7 | Forschungsrunde und Ergebnisbericht | ✅ Lauf 2026-10-12 abgeschlossen; Bericht v2 nach Astras Review: [lr7/ergebnis_20261012](lr7/ergebnis_20261012/README.md) |
| LR8–LR9 | Folgestudien | offen; jede neue Studie braucht ein neues Protokoll und Johanns Freigabe |

## LR0 (2026-10-08)

- **Arbeitsort:** Worktree `D:/mandala/.worktrees/feldtheorie-lantern-reconstruction`, Branch `lantern-reconstruction`, Ausgangscommit `d1c56267ae81e90f9ebd7d5d195fea818b5f3930`.
- **Quellen:** Die elf Quellen stimmen mit dem Inventar überein (Blob, roh in main, LF-normiert).
- **Orakel:** Kontrollen 22/22; Quellaudit gleich den gespeicherten Werten.
- **Sicherung:** 24 fremde unversionierte Dateien kopiert, mit Manifest.
- **Offen:** scikit-learn fehlt (LR0-O1); explizite CI-Jobs (LR0-O2).

## LR1 (2026-10-08)

- **Vollständiger Original-Lader** in einem separaten Prozess (`PYTHONHASHSEED=0`, ohne Bytecode, Audit nur als Beobachtung).
- **Snapshot:** zunächst `artifacts/registry_snapshot_v1`, ersetzt durch **v2** (kanonischer Hash `2d6a2a64…`, Manifest-Pin `5b7aa962…`). IDs sortiert, alle Arrays gemeinsam permutiert. Die Matrix gleicht dem unabhängigen Nachbau bis 2,2·10⁻¹⁶.
- **Beobachtet:** Der Aufbau setzt den globalen RNG neu (über `hash()`). NumPy startet beim Import `cmd /c ver`. Der Versuchspfad importiert keinen Legacy-Code.
- **Nachtrag nach `REVIEW_LR1`:** R1 (Manifestwerte nachgerechnet und gepinnt), R2 (alle Knotenparameter gegen die Registry, Pflicht-Pins) und R3 (unveränderlicher Speicher) sind geschlossen. Dazu das vollständige Importmanifest.
- **Prüfungen:** Tests 52/52, Ad-hoc-Mutation effektiv 25/25 (ein Überlebender war eine echte Testlücke und ist geschlossen).

## LR2 (2026-10-08)

- **Kern:** gebatchte Euler-Dynamik in Differenzform ohne Zufallsquelle; lineares H(t) mit rauschgewichteten Singulärwerten.
- **Originaläquivalenz:** 1,6·10⁻¹⁴ über 100 Fälle; der echte Originalkern lief dafür in einem separaten Prozess.
- **Offenes Gate LR2-G1:** Die ODE-Genauigkeit ≤ 0,005 rad ist über das vorab festgelegte Panel **nicht bestanden** (0,117 bei dt = 0,02). Im Studienregime liegt der Fehler bei 1,6·10⁻³. Entscheidung vor LR6.
- **Beobachtet:** `v9_alpha.models` braucht pandas, deshalb lief der Originalkern über den Dateipfad. Der Originalkern ignoriert negative Kopplungen und Asymmetrie.
- **Prüfungen:** Tests 77/77, Ad-hoc-Mutation 12/12.
- **Planänderung AE-01** (Johann/Astra): Die Studie integriert mit **RK4**, dt = 0,02. Auf dem unveränderten Panel liegt der Fehler bei 3,2·10⁻⁷ (vierte Ordnung). Euler bleibt unverändert, sein Fehlschlag dokumentiert. RK4 ist für die geforderte Genauigkeit etwa 6-mal günstiger. Tests 93/93, RK4-Mutation 6/6. Die Decoderkennzahl (≤ 0,01) bleibt bis LR4 offen.

## LR3 (2026-10-08)

- **Module:** benannte Ströme, Kontexte, Schreiben mit Kontrollen, getrennte Sichten A (66 Merkmale) und B (16 Merkmale, unbeschriebene Referenz), Vergleichsnetze, Episoden mit RK4. Die Parameter stehen in `protocol/study_defaults.json`.
- **Abnahmen:** Referenzknoten-Leak negativ getestet; Reset und Nullimpuls gleich für alle u; Surrogatinvarianten. Dazu die harten Gates aus § 10.
- **Prüfungen:** Tests 165/165; Ad-hoc-Mutation 13/14 erkannt, 1 äquivalent, 2 echte Testlücken geschlossen.
- **Nachtrag nach `REVIEW_LR3`:** strikte Stromschlüssel und Episoden-IDs; Batch an Studie, Kontext und Konfiguration gebunden; Chunk geprüft; Surrogatbericht erhalten; unveränderliche Konfiguration. Tests 182/182, Mutation der neuen Verträge 13/13.
- **Nachtrag nach Astras Nachprüfung** (`LANTERN_LR3_NACHREVIEW_2026-10-08`, Stand `d43427d`): Die ursprünglichen Gegenfälle sind bestätigt behoben. Die neuen Befunde F1, F2, E1 und E2 wurden zuerst reproduziert und dann geschlossen:
  - Beobachtungsspezifikation vollständig gegen den Kontext geprüft, mit neuem Einstieg `observe()` für LR4;
  - Messarrays mit exakter Form, endlich, ohne Broadcasting;
  - Leseknoten als echte Ganzzahlen;
  - Stromschlüssel in [0, 2³²).

  Gültige Aufrufe sind alt gegen neu bitgleich (173 Digests). Tests 233/233, Mutation der neuen Wächter 18/18. Astras Nachprüfung (`astra-fix-6680618`): 233/233 und 44/44; keine Blocker für LR4.

## LR4 (2026-10-08)

- **Module:**
  - `training.py`: Ridge in geschlossener Form per NumPy-SVD;
  - `decoders.py`: Artefakt, `predict` nur mit Merkmalen, Roundtrip über NPZ ohne Pickle und striktes JSON;
  - `evaluate.py`: ohne Fit-Import;
  - `metrics.py`: S/G, Rastermittelwert A, Kontextinferenz, H-B1/B2 mit Holm, Leak-Alarm;
  - `runner.py`: Entwicklungspipeline, Merkmale nur über `observe()`.
- **Decoder-Konvergenzgate** (Plan 10.2, Definition vor dem Lauf festgelegt): bestanden mit |ΔG| ≤ 8,7·10⁻¹⁰ und |ΔA| ≤ 2,5·10⁻¹⁰, Grenze 0,01. Das Pipeline-Gate A bei t = 0 ist mit G0 = 0,962 > 0,90 ebenfalls bestanden.
- **Prüfungen:** Tests 268/268. Gezielte Mutation 29/30: 1 Mutant ist nachweislich äquivalent, 2 echte Testlücken sind geschlossen.
- **Nachtrag nach `REVIEW_LR4`:** Konstante Trainingsspalten werden über ihre Werte erkannt (Skala 1, R1). Die Decoder-Metadaten werden vollständig geprüft, `check_decoder_for` bindet jedes Modell an seine Zelle (R2), und die Modellarrays sind unveränderlich. Das Konvergenzgate ist nicht betroffen: Das Panel enthält keine konstante Spalte, und die Pipeline ist alt gegen neu bitgleich. Tests 295/295, Mutation 23/23.
- **Verbindlich für LR5** (aus `REVIEW_LR4`): Modellintegrität mit Hashprüfung vor und nach der Auswertung; exklusive, atomare Speicherung ohne Überschreiben; externes Manifest mit Modell- und Herkunftsidentität samt erwarteter Zelle; eine Ergebnisfreigabe, die das genaue Raster und alle Kontrollalarme prüft. → in LR5 umgesetzt.
- **Astras Nachprüfung** (`LANTERN_LR4_NACHREVIEW_25ba293`): R1/R2 im geprüften Umfang geschlossen, GO für LR5; neuer Abnahmefall LR5-A1.

## LR5 (2026-10-08/09)

- **LR5-A1:**
  - zwölf benannte Kontrollzellen (`protocol/control_alarms.json`);
  - Holm immer über alle 12;
  - getrennte Alarme `positive_spurious_success` (G > 0 und Holm-p ≤ 0,01) und `target_dependence` (jedes Vorzeichen);
  - die Kontrolle `permuted_targets`;
  - die Freigaberegel als **Vorschlag**, vor dem Freeze zu entscheiden.
- **Artefaktkette und Laufverwaltung** (`artifacts.py`, `runs.py`):
  - Lauf- und Modellidentitäten;
  - exklusive, atomare Speicherung;
  - studienweite Sperre, Ereignisprotokoll mit Schlaferkennung, Status;
  - deterministisches Resume, verweigert bei geändertem Code, Konfiguration oder Snapshot; Unterbrechung plus Resume ergibt den ununterbrochenen Lauf.
- **Freigabe-Gate** (`release.py`): technisch vollständig, wissenschaftlich interpretierbar und Hypothese als getrennte Felder; Scores und Strukturprüfung werden nachgerechnet.
- **Budget:** hochgerechnet 1,66 h Produktion bei 2 h Entwurfsbudget. Die erste Messung lag bei 2,25 h, bis die Trajektorien-Wiederverwendung nach Plan § 13 kam. Spitzen-RAM 115 MB, Artefakte 202 MB.
- **CI:** drei explizite Jobs, Python 3.11 und 3.12, ohne Maskierung; noch nicht auf GitHub gelaufen.
- **Mutationskampagne:** 34 ausgeführt, 33 erkannt, 1 äquivalent. Alle ausführbaren Plan-Mutanten werden erkannt; 6 und 12 sind `not_applicable`.
- **Nachtrag nach `REVIEW_LR5`:**
  - R1: ausdrückliches `recover()` nach Prozessverlust; es prüft die PID, entfernt die tote Sperre protokolliert und behandelt abgeschnittene Protokollzeilen.
  - R2: Trainings- und Validierungsgrößen, λ-Raster und Software an den Lauf gebunden.
  - R3: strikt gleiche Software beim Fortsetzen.
  - R4: jede verwaiste Modelldatei wird geprüft; Abweichung bedeutet Integritätsfehler, nichts wird ersetzt.

  Regression mit einem echten, hart getöteten Kindprozess. Freigaberegel befürwortet. Tests 372/372; Mutation insgesamt 45, davon 43 erkannt und 2 äquivalent.
- **Nachtrag nach Astras Nachprüfung von `b9c405b`:**
  - F1: `recover()` diagnostiziert zuerst nur lesend; eine Ablehnung lässt Log und Sperre bytegleich. Danach kommen eine exklusive Recovery-Sperre und eine erneute Prüfung, erst dann wird geschrieben.
  - F2: `test_lr5_review.py` steht im CI; die Vollständigkeit der CI-Auswahl ist jetzt ein Test.
  - Das Log ist durchgehend LF.

  Tests 381/381; Mutation 50, davon 48 erkannt und 2 äquivalent.
- **Nachtrag nach Astras Nachreview zu `9b52d95`:**
  - N1: Das Log-Ende wird nach JSON-Syntax und Zeilenabschluss getrennt beurteilt; ein gültiges Ereignis ohne LF bleibt erhalten und wird nur durch Anhängen abgeschlossen.
  - N2: Recovery und normale Starts teilen eine gemeinsame Verwaltungssperre.

  Regression mit echten Kindprozessen. Tests 393/393; Mutation 54, davon 52 erkannt und 2 äquivalent.
- **Astras Abschlussprüfung:** Das Recovery-Gate ist geschlossen; GO für LR6.

## LR6 (2026-10-09)

- **Forschungsmodus** nur über `create_research_run` mit `protocol/freeze.json`, das an den Kandidaten und die Code-Identität gebunden ist. Die **Studienauswertung** nach Plan § 9 erfolgt nur für interpretierbare Forschungsläufe. Dazu kommt das Betriebshandbuch `lr6/BETRIEB.md`.
- **Erste Entwicklungsabnahme:** Beide LR5-A1-Alarme schlugen an, nur in `permuted_targets|A|1.0`. Die Untersuchung wies einen Konstruktionsfehler dieser Kontrollzellen nach (unpassender Nullvergleich) und ergab keinen zusätzlichen Befund eines Pipeline-Lecks. Johann entschied sich für **Kontrollprotokoll v2** mit Neufit-Nullverteilung und permutierten Validierungszielen.
- **Zweite Entwicklungsabnahme:** technisch vollständig und wissenschaftlich interpretierbar; alle 12 Alarmzellen unauffällig; G0 = 0,978.
- **Freeze-Kandidat:** Masterseed 1431972670 (per `secrets`), 20 Kontexte, 1960 Zellen; MLP-Verzicht als Vorschlag; hochgerechnet 1,86 h bei 2 h Budget. Er ist an den Code `5905dcd` gebunden.
- **Prüfungen:** Tests 425; Mutation 68, davon 66 erkannt und 2 äquivalent.
- **Astras Review `29af52f`:** noch kein Freeze; R1–R4 reproduziert und behoben (`b0da0c7`):
  - Softwarebindung beim Forschungsstart;
  - Kontrollprotokoll v3 mit Gleichstandsregel;
  - Herkunft der Neufit-Null;
  - Testvertrag.

  Die dritte Abnahme stimmt mit Abnahme 2 überein: Modell-, Vorhersage- und Nullarchive sind byte-identisch, die Records wegen neuer Metadaten nicht. Der neue Kandidat übernimmt den Seed 1431972670; der alte liegt in `lr6/superseded/`. Tests 466/466; Mutation 81, davon 79 erkannt und 2 äquivalent. Bericht: `lr6/review_29af52f/NACHBERICHT.md`.
- **Astras Nachreview `987d9fc`:** R1–R3 geschlossen. Testfehler F1 (fremde Version als Literal) nachvollzogen und mit ihrem Patch behoben; `test_lr6.py` 67/67 unter 3.11.9 und unter simuliertem 3.12.14. Produktion und Kandidat unverändert. Keine weiteren Einwände gegen den formalen Freeze. Bericht: `lr6/review_987d9fc/ABSCHLUSS.md`.
- **FREEZE (`5ccad90`, Entscheidung Johann 2026-10-09):**
  - `protocol/freeze.json` bindet den unveränderten Kandidaten (`68fac7fa…`) und den Code (`670d9352…`).
  - Der MLP-Verzicht ist verbindlich; Betriebsfenster ≥ 2,5 h; die Laufzeit ist keine Garantie.

## LR7 (Vorbereitung)

- Die **Bereitschaft in der eingefrorenen Umgebung** ist geprüft und erfüllt: Software exakt, Registry voll verifiziert, Platz, RAM und Strom ausreichend, keine Sperren.
- **Startwerkzeug** `tools/lr7_research_run.py`: standardmäßig ein Probelauf; der Start verlangt `--confirm-study`.
- Unterlagen: `lr7/LR7_VORSTART.md`.
- **Offen:** das gesonderte Vorstartreview. **Kein Forschungslauf vor diesem Review.**

## LR7 Ergebnis (2026-10-12/13)

- Forschungslauf `lr7-research-20261012T124802Z`: 1960/1960 Zellen, technisch vollständig, wissenschaftlich interpretierbar, keine Kontroll-Alarme, Konvergenz-Gate bestanden.
- **Aufgabe A:** gewichteter Rekonstruktionsgewinn mit Lantern 0,517, ungekoppelt 0,977. Das ist keine Aussage über dauerhafte Spur oder Gedächtnisdauer.
- **Aufgabe B:** Der vorab geforderte Gewinn über 0,05 wurde nicht nachgewiesen (H-B1/H-B2). Das ist kein Unmöglichkeitsbeweis.
- **Astras Ergebnisreview** (ASTRA-2026-10-12-04): Zahlen reproduziert. Die Wortlautkorrekturen R1–R7 sind in Bericht v2 umgesetzt.
- **Ablage:** Bericht, Freigabebericht, Laufmanifest und Prüfsummen des vollständigen Laufordners liegen in [`lr7/ergebnis_20261012/`](lr7/ergebnis_20261012/README.md). Die Zellarchive bleiben außerhalb des Repos.

