# Lantern-Rekonstruktion: Roadmap

Grundlage: [Implementierungsplan Version 2.0, § 14](reference/review_package_2026-10-07/LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md).

| Paket | Inhalt | Status |
|---|---|---|
| LR0 | Lokaler Bestand: Worktree, Regeln, Hashvergleich der elf Quellen, Inventar, Sicherung | ✅ erledigt, siehe [Bericht](lr0/LR0_BERICHT.md); wartet auf Prüfung |
| LR1 | Snapshot und Import: separater Legacy-Prozess, kanonische Matrix, Importmanifest | ✅ erledigt, siehe [Bericht](lr1/LR1_BERICHT.md); wartet auf Prüfung |
| LR2 | Numerischer Kern: gebatchte Dynamik, lineares H(t), Orakel | ✅ erledigt, siehe [Bericht](lr2/LR2_BERICHT.md). ODE-Gate: Euler nicht bestanden (bleibt dokumentiert), **RK4 bestanden** (Planänderung AE-01); Decoderteil in LR4 bestanden; wartet auf Prüfung |
| LR3 | Aufgaben A/B und Referenzen: Beobachtungen, Ströme, Surrogate | ✅ erledigt, siehe [Bericht](lr3/LR3_BERICHT.md); Fixes nach Astras Nachprüfung, von ihr nachgeprüft (`6680618`) |
| LR4 | Ridge und Evaluation | ✅ erledigt, siehe [Bericht](lr4/LR4_BERICHT.md). Ridge per NumPy (LR0-O1); Decoder-Konvergenzgate bestanden; wartet auf Prüfung |
| LR5 | Laufverwaltung und CI | offen |
| LR6 | Entwicklungsabnahme und Freeze-Kandidat | offen |
| LR7–LR9 | Forschungsrunde, Bericht, Folgestudien | erst nach der LR6-Freigabe |

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
- **Verbindlich für LR5** (aus `REVIEW_LR4`): Modellintegrität mit Hashprüfung vor und nach der Auswertung; exklusive, atomare Speicherung ohne Überschreiben; externes Manifest mit Modell- und Herkunftsidentität samt erwarteter Zelle; eine Ergebnisfreigabe, die das genaue Raster und alle Kontrollalarme prüft.
