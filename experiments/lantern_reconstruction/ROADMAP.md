# Lantern-Rekonstruktion: Roadmap

Grundlage: [Implementierungsplan Version 2.0, § 14](reference/review_package_2026-10-07/LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md).

| Paket | Inhalt | Status |
|---|---|---|
| LR0 | Lokaler Bestand: Worktree, Regeln, Hashvergleich der elf Quellen, Inventar, Sicherung | ✅ erledigt, siehe [Bericht](lr0/LR0_BERICHT.md); wartet auf Prüfung |
| LR1 | Snapshot und Import: separater Legacy-Prozess, kanonische Matrix, Importmanifest | ✅ erledigt, siehe [Bericht](lr1/LR1_BERICHT.md); wartet auf Prüfung |
| LR2 | Numerischer Kern: gebatchte Dynamik, lineares H(t), Orakel | ✅ erledigt, siehe [Bericht](lr2/LR2_BERICHT.md). ODE-Gate: Euler nicht bestanden (bleibt dokumentiert), **RK4 bestanden** (Planänderung AE-01); Decoderteil offen bis LR4; wartet auf Prüfung |
| LR3 | Aufgaben A/B und Referenzen: Beobachtungen, Ströme, Surrogate | ✅ erledigt, siehe [Bericht](lr3/LR3_BERICHT.md); wartet auf Prüfung |
| LR4 | Ridge und Evaluation | offen; vorher Entscheidung LR0-O1 (scikit-learn) |
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
