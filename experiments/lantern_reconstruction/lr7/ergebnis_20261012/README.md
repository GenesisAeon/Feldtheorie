# LR7 Forschungslauf vom 2026-10-12: Ergebnis und Herkunftsnachweis

**Bericht:** [`ERGEBNISBERICHT_LR7.md`](ERGEBNISBERICHT_LR7.md), Version 2, mit den Korrekturen R1–R7 aus Astras Ergebnisreview ASTRA-2026-10-12-04.

## Kurzfassung

- **Aufgabe A, Spurerhalt** (eine Schätzung, keine Schwelle): Der über das Zeitgitter gewichtete Rekonstruktionsgewinn liegt bei Lantern im Mittel bei 0,517, ungekoppelt bei 0,977. Das belegt **weder eine dauerhafte Spur noch eine bestimmte Gedächtnisdauer**.
- **Aufgabe B, verteilte Auslesbarkeit:** Der vorab geforderte Gewinn über 0,05 wurde **nicht** nachgewiesen (H-B1/H-B2). Das ist kein Unmöglichkeitsbeweis und kein Gleichheitsbeleg.
- Alle Ergebnisse sind synthetisch und gelten nur für dieses rekonstruierte Modell, die eingefrorene Studie und die festgelegten Ridge-Dekoder.

## Dateien

| Datei | Inhalt |
|---|---|
| `ERGEBNISBERICHT_LR7.md` | Ergebnisbericht v2 (Claude, nach Astras Review) |
| `release_report.json` | Freigabebericht, vom eingefrorenen Werkzeug erzeugt; unverändert, SHA-256 `1ec33ae8…a342c` |
| `run.json` | Laufmanifest: Code-Hashes, Konfiguration, Gitter, Software; unverändert |
| `run_folder_SHA256SUMS.txt` | SHA-256 **jeder** Datei des vollständigen Laufordners (7943 Dateien) |

## Herkunft

- **Lauf:** `lr7-research-20261012T124802Z`.
  - Studie 1431972670, 1960/1960 Zellen.
  - Laufidentität `2e61024776cd1cad870df1e01536ef1df6e96c0c9234e56076e67332027639ae`.
  - Gestartet mit `tools/lr7_research_run.py` (Commit `99ec950`) auf dem Freeze `5ccad90`, nach Johanns Freigabe.
- **Seit dem Freeze unverändert:** Produktionsmodule, `protocol/`, `v9_alpha/`, `models/`.
- **Reviews** (privates Review-Repo, Branch `astra-reviews`, Commit `f50dee1`):
  - ASTRA-2026-10-12-01: Vorstart, kein Einwand.
  - ASTRA-2026-10-12-04: Ergebnis.
    - 294 Zellen aus den Kontexten 0, 9 und 19 nachgerechnet, größte Differenz 0.
    - Hauptstatistik über alle 20 Kontexte, innerhalb 2e-13.
    - Kein Wiederholungsbedarf.

## Bewusst nicht im Repo

- **Zellarchive** `cells/` (ca. 218 MB: Modelle, Vorhersagen, Records), `events.jsonl` und `structure/`. Sie liegen im vollständigen Laufordner. Ihre Integrität ist über `run_folder_SHA256SUMS.txt` prüfbar.
- **Lokale Betriebsdateien:** Start-Logs und Sperrdateien.
- **Version 1 des Berichts:** Sie ist durch v2 ersetzt. Die zurückgenommenen Aussagen sind in v2 ausdrücklich vermerkt.
