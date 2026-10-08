# LR0 – Lokaler Bestand (Bericht)

Trilayer: [`lr0_status.json`](lr0_status.json) (maßgeblich), [`lr0_status.yaml`](lr0_status.yaml) (Strukturzwilling), dieser Bericht (Erzählung). Rohdaten: [`lr0_inventory.json`](lr0_inventory.json), [`local_source_audit.json`](local_source_audit.json), [`local_control_results.json`](local_control_results.json).

**Grundlage:** [Implementierungsplan Version 2.0](../reference/review_package_2026-10-07/LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md) und [Fachreview](../reference/review_package_2026-10-07/LANTERN_FACHREVIEW.md).
- Die Ablage ist eine unveränderte Referenzkopie des Prüfpakets; alle `SHA256SUMS` sind geprüft.
- Die Originale im Planordner `D:/mandala/mandala-memory-results/lantern-reconstruction-plan/` und die sechs historischen Eingaben bleiben unverändert.

## Arbeitsort

| | |
|---|---|
| Worktree | `D:/mandala/.worktrees/feldtheorie-lantern-reconstruction` |
| Branch | `lantern-reconstruction` |
| Ausgangscommit | `d1c56267ae81e90f9ebd7d5d195fea818b5f3930` (Feldtheorie main, lokal, absichtlich nicht gepusht; gleich `repo_head` des Quelleninventars) |
| Bereich | `experiments/lantern_reconstruction/` |

## Quellen und Orakel

- **Elf Quellen** des Quelleninventars:
  - Git-Blobs und rohe Bytes in main stimmen 11/11 mit dem Inventar überein.
  - Nach LF-Normierung sind alle Dateien in main und im Worktree identisch mit ihren Blobs.
  - Roh unterscheiden sie sich (CRLF, `core.autocrlf=true`). Das erwartet auch das Inventar; Roh- und Blob-Hashes bleiben getrennt.
  - Ankerzeilen: 9/9 gefunden.
- **Registry:** 34 eindeutige IDs, sortiert identisch mit dem Inventar. Die YAML-Reihenfolge ist nicht sortiert, deshalb ist eine kanonische Permutation nötig (LR1). In LR0 wurde keine Matrix berechnet.
- **Orakel,** unverändert aus der Referenzkopie ausgeführt:
  - Analytische Kontrollen: **22/22**, höchstens 5,6·10⁻¹⁷ relative Abweichung zu den gespeicherten Werten.
  - Quellaudit gegen diesen Worktree:
    - 34 Knoten und 561 Kanten (vollständiger Graph);
    - 187 Kanten bei `kappa` begrenzt, 9 Endgewichte genau 1;
    - Matrixnachbau gegen die ausgewählten Quellmethoden: 2,2·10⁻¹⁶;
    - Phasenschritt nach 200 Schritten: 4,2·10⁻¹⁷ rad;
    - der Nullrausch-Pfad verbraucht den globalen RNG.

    Alle Strukturgrößen sind exakt gleich den gespeicherten Werten, die Eigenwerte bis auf 1,3·10⁻¹⁵.
  - **Grenze:** Geprüft sind ausgewählte Quellmethoden und analytische Kontrollen, **nicht** der vollständige Lader, die Import-Isolation oder eine Gedächtnisaussage. Das ist LR1.

## Lokale Regeln

- Feldtheorie hat keine `CLAUDE.md`. Die Root-`AGENTS.md` beschreibt sich selbst als `narrative/docs`-Charta; sie bleibt unverändert.
- **Angewendet:**
  - Trilayer: JSON maßgeblich, YAML-Zwilling, Markdown;
  - Falsifizierbarkeit über Nullmodelle und explizite Kontrollen;
  - Tests für neue Funktionen;
  - dokumentierte Seeds und Umgebung.
- **pytest und CI:** `testpaths = ["tests"]`, und die CI ruft nur `pytest` auf. Lantern-Tests brauchen deshalb eigene, explizite Aufrufe (F10). Die Fehlermaskierung in `validation.yml` (`|| echo`) darf nicht übernommen werden.

## Bestand und Sicherung

- **Main-Checkout:** keine Änderungen an versionierten Dateien.
  - 24 unversionierte Datendateien aus August 2026 (fremd): Sie sind **kopiert, nicht verschoben** nach `D:/mandala/backups/feldtheorie-untracked-2026-10-08/` (Manifest mit Prüfsummen, alle gleich, 673 KB). Die Originale bleiben unberührt.
  - Drei verschachtelte Worktrees.
- **Unangetastet:**
  - der Studienansicht-Worktree `feldtheorie-mandala-memory` (Branch `mandala-memory`, `e49f2b1`, sauber; meine unabhängige Prüfung steht als eigener Auftrag aus);
  - `feldtheorie-archaeology` und `feldtheorie-coverage-fix` (beide sauber);
  - der gesperrte Worktree `review-g01-g02-independent` mit einer offenen Änderung (fremd).

## Abweichungen und offene Punkte

| ID | Art | Inhalt |
|---|---|---|
| LR0-D1 | erwartet | rohe Bytes ≠ Blob wegen CRLF; LF-normiert identisch |
| LR0-D2 | Umgebung | Python 3.11.9, NumPy 2.2.6, SciPy 1.15.3 (innerhalb der Repo-Grenzen) statt Astras 3.12/2.3.5/1.17; Ergebnisse bis 1,4·10⁻¹⁵ gleich |
| LR0-O1 | **Entscheidung vor LR4** | scikit-learn ist in der Laborumgebung **nicht installiert**. Möglichkeiten: eine eigene Lantern-Umgebung auf D: innerhalb der `pyproject`-Grenzen oder Ridge in geschlossener Form mit NumPy, ohne neue Abhängigkeit. |
| LR0-O2 | LR5 | explizite CI-Jobs für Lantern-Tests; keine Fehlermaskierung |

In LR0 gab es keinen Projektimport, keine Simulation, keinen Decoder, keine Forschungsrechnung, keinen Freeze, keinen Merge und keinen Push. Die Originalmodule und M0–M12 sind unverändert.
