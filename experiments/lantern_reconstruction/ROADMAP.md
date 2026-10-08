# Lantern-Rekonstruktion: Roadmap

Grundlage: [Implementierungsplan Version 2.0, § 14](reference/review_package_2026-10-07/LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md).

| Paket | Inhalt | Status |
|---|---|---|
| LR0 | Lokaler Bestand: Worktree, Regeln, Hashvergleich der elf Quellen, Inventar, Sicherung | ✅ erledigt, siehe [Bericht](lr0/LR0_BERICHT.md); wartet auf Prüfung |
| LR1 | Snapshot und Import: separater Legacy-Prozess, kanonische Matrix, Importmanifest | ✅ erledigt, siehe [Bericht](lr1/LR1_BERICHT.md); wartet auf Prüfung |
| LR2 | Numerischer Kern: gebatchte Dynamik, lineares H(t), Orakel | offen |
| LR3 | Aufgaben A/B und Referenzen: Beobachtungen, Ströme, Surrogate | offen |
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
- **Snapshot:** `artifacts/registry_snapshot_v1`, kanonischer Hash `7237a784…`, IDs sortiert, alle Arrays gemeinsam permutiert. Die Matrix gleicht dem unabhängigen Nachbau bis 2,2·10⁻¹⁶.
- **Beobachtet:** Der Aufbau setzt den globalen RNG neu (über `hash()`). NumPy startet beim Import `cmd /c ver`. Der Versuchspfad importiert keinen Legacy-Code.
- **Prüfungen:** Tests 22/22, Ad-hoc-Mutation 11/11.
