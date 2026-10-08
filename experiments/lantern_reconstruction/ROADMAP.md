# Lantern-Rekonstruktion: Roadmap

Grundlage: [Implementierungsplan Version 2.0, § 14](reference/review_package_2026-10-07/LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md).

| Paket | Inhalt | Status |
|---|---|---|
| LR0 | Lokaler Bestand: Worktree, Regeln, Hashvergleich der elf Quellen, Inventar, Sicherung | ✅ erledigt, siehe [Bericht](lr0/LR0_BERICHT.md); wartet auf Prüfung |
| LR1 | Snapshot und Import: isolierter Legacy-Worker, kanonische Matrix, Importmanifest | offen |
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
