# Integration M12 in Feldtheorie main (lokal, 2026-10-05)

## Merges und Marken

- **Merges:**
  - `813e91f6` (`--no-ff`) mit Branch-Stand `d850a0e6`: M12 nach der Ergebnisprüfung.
  - `4499e7d8`: Integrationsbefund, siehe unten.
  - Der Ordner `experiments/mandala_memory` und `.gitattributes` sind auf main baumgleich mit dem Branch.
- **Marken:**
  - Sicherung `backup/main-vor-m12-2026-10-05` auf `4cb353ba`;
  - geprüfter Stand `reviewed/mandala-memory-d850a0e`;
  - Freezes `m12-freeze` (`f3a5bc2`) und `m12-models` (`e8e53a8`).
- **Nicht gepusht.** Fremde, unversionierte Dateien in der Hauptarbeitskopie blieben unberührt.

## Ablauf M12 (je Phase genau ein Versuch, ohne Abbruch)

Plan → Implementierung → Review-Fixes → Protokoll-Freeze → Referenzen → Smoke → Training → Modell-Freeze → Robustheitsauswertung → Ergebnisprüfung.

| Schritt | Stand |
|---|---|
| Plan, Fassungen 1 und 2 | `2a07ae4`, `d1acc4a` |
| Implementierung | `ba5dabc` |
| Review-Fixes R5–R8 | `15edfbd` |
| Protokoll-Freeze | `f3a5bc2` |
| Referenzen | `331f422` |
| Smoke | ohne Commit |
| Training | 2343 s |
| Modell-Freeze | `e8e53a8` |
| Robustheitsauswertung | `093d34f`, Lauf `m12-research-20261005T170243-972cca01` |
| Ergebnisdoku | `84e9d72`, präzisiert in `d850a0e` |

**Ergebnis:** R-a (+0,104) und R-σ (+0,043) bestätigt. Details: `experiments/mandala_memory/docs/M12_ERGEBNIS.md`.

## Integrationsbefund und Korrektur

- **Befund:** Nach dem ersten Merge meldete die Freeze-Prüfung auf main, dass Modelldateien vom Modell-Freeze abweichen.
- **Ursache:**
  - `core.autocrlf=true` hatte beim Auschecken in main die 21 JSON-Dateien im Modellordner (20 Seed-Metadaten und das Manifest) auf CRLF umgewandelt.
  - Der Modell-Freeze bindet rohe Bytes, die Binärregel deckte aber nur die NPZ ab.
  - Nach LF-Normierung waren alle 21 identisch; die NPZ waren unberührt.
  - Der Worktree war davon nicht betroffen, weil dort nie neu ausgecheckt wurde. Training und Auswertung liefen also auf den unveränderten Dateien.
- **Korrektur (`71bb31f`, gemergt in `4499e7d8`):**
  - `.gitattributes` ergänzt um `experiments/mandala_memory/protocol/m12_models/*.json -text`.
  - Kein eingefrorener Code, keine Daten und keine Ergebnisse geändert.
  - Die 21 JSON wurden in main gelöscht und aus dem Commit neu ausgecheckt (versioniert, inhaltlich identisch).
- **Neue Tests:**
  - Die echten Forschungsmodelle laden in der jeweiligen Arbeitskopie mit rohen Datei-Hashes.
  - Frisches Auschecken mit `core.autocrlf=true` in einem Wegwerf-Repo: Mit der Regel kommen alle Bytes unverändert zurück, ohne sie werden die JSON umgewandelt.

## Prüfungen nach der Integration (auf main)

- Protokoll-Freeze gültig.
- Alle 20 Modelle laden mit vollständiger Herkunfts- und Hashprüfung; die NPZ-Blobs sind byte-gleich mit den Dateien.
- Neuauswertung: freigegeben, kein Alarm, **identisch** mit der gespeicherten Auswertung. Die Ergebnis-Prüfsumme passt zum Abschlussdatensatz.
- Pflichtlauf auf main **396/396**.
- Linux (Branch, gleicher Baum): ohne SCF 194 bestanden, mit SCF 378 bestanden.
- Die Mutationsprüfung wurde nach den Review-Fixes nicht wiederholt; Stand 126/126 bei `15edfbd`. Seitdem gab es nur die Freeze-Konstante, Tests, Dokumentation und `.gitattributes`.
