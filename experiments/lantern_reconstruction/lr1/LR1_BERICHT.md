# LR1 – Snapshot und Import (Bericht)

Trilayer: [`lr1_status.json`](lr1_status.json) (maßgeblich), [`lr1_status.yaml`](lr1_status.yaml), dieser Bericht. Artefakt: [`artifacts/registry_snapshot_v1/`](../artifacts/registry_snapshot_v1/).

## Was gebaut wurde

| Modul | Aufgabe |
|---|---|
| [`legacy_probe.py`](../legacy_probe.py) | lädt den **vollständigen** Original-Lader `LanternNetwork` einmal in einem **separaten Prozess**, protokolliert beobachtete Ereignisse und den globalen RNG-Zustand und exportiert in YAML-Reihenfolge |
| [`registry_adapter.py`](../registry_adapter.py) | importiert **nie** Legacy-Code; prüft die Quellen, sortiert kanonisch, vergleicht mit einem unabhängigen Formelnachbau und lädt den Snapshot streng |
| [`tools/lr1_make_snapshot.py`](../tools/lr1_make_snapshot.py) | Probe → Snapshot, exklusiv geschrieben |

**Prozess:**
- `PYTHONHASHSEED=0`, kein Bytecode, kein User-Site, kein `PYTHONPATH`.
- Arbeitsordner und Temp-Dateien auf D:, Zeitlimit 300 s.
- Der Import dauert 1,1 s, der Aufbau 0,14 s; geladen werden 708 Module.

## Ergebnisse

**Kanonischer Export:**
- Die IDs werden ausdrücklich aus der (unsortierten) YAML-Reihenfolge in die lexikographische Reihenfolge überführt.
- Die Matrix und alle Knotenarrays werden **gemeinsam** permutiert; die Permutation ist gespeichert.
- `theta` heißt `theta_threshold`, weil es der Schwellenwert ist und nie eine Phase.

**Formelvergleich:** Der eigene Nachbau aus den YAML-Werten liest die Konstanten aus `unified_constants.py`, ohne sie zu importieren. Die größte Abweichung ist in **beiden** Reihenfolgen 2,2·10⁻¹⁶ (Toleranz 10⁻¹⁴).

**Struktur** (gleich Plan § 4):
- 561 positive Kanten, 187 bei `kappa` begrenzt, 9 Endgewichte genau 1;
- Knotensummen 0,8286…–25,087 (seed-morph-compute-001 bzw. seed-wolfmessing-001);
- g = 0,0398616…, λ₂ = 0,034030…, λ_max = 1,038686.

**Reproduzierbarkeit:** Der kanonische Hash `7237a784…` ist über unabhängige Probe-Läufe und für `PYTHONHASHSEED` 0 und 1 identisch.

**`coupling_targets`:** Sie werden geladen (68 Einträge), aber für die Matrix nicht verwendet. Ohne sie bleibt die Matrix bitgleich (getestet).

## Hashbegriffe, getrennt

| Begriff | Bedeutung |
|---|---|
| `raw_sha256` | Bytes der Arbeitskopie (hier CRLF) |
| `lf_sha256` | CRLF→LF, nur für deklarierte Textquellen; muss dem Blob gleichen |
| `blob_sha256` | Git-Blob an HEAD; muss der geprüften Basis (Quelleninventar) gleichen |
| `container_sha256` | genau diese NPZ-Bytes; ein gleiches Array, neu gespeichert, kann abweichen |
| `canonical_sha256` | Schema, IDs, Metadaten, Form, `<f8` und C-Order-Daten; unabhängig vom Container (getestet) |

## Beobachtungen (Audithook)

Der Audithook ist eine **Beobachtung**. Er blockiert nichts, setzt keine Isolation durch und beweist keine Abwesenheit.

- **Beim Import:** ein Unterprozess `cmd.exe /c ver`. Verursacher ist `numpy/testing/_private/utils.py:92` (`platform.machine()` → `platform.win32_ver()`), also ein Nebeneffekt von NumPy unter Windows, nicht Lantern-Code. Dazu gehört der einzige beobachtete Schreib-Open, nämlich auf `nul`.
- **Beim Aufbau und bei der Extraktion:** keine Schreibzugriffe und keine Prozess- oder Netzereignisse. Netzereignisse wurden in keiner Phase beobachtet.
- **Globaler RNG:**
  - Der Import verbraucht ihn **nicht**, der Aufbau **schon**: `_initialize_collective_field` setzt den Seed über `hash(domain+type)` (`lantern_bridge.py:516`).
  - Der Zustand hängt von `PYTHONHASHSEED` ab, die Matrix nicht.
  - Der spätere Versuchspfad lädt nur den Snapshot. `registry_adapter` lädt in einem frischen Prozess kein `v9_alpha` und kein `models` und lässt den globalen RNG unverändert (getestet).
- **Umfang des Imports:** Das breite `models/__init__.py` zieht 11 weitere Modellmodule nach. `v9_alpha/models` wird vom Lader nicht importiert.

## Abweisungen (alle getestet)

- **Fehlende oder falsche Quellen:**
  - fehlende Quelldatei;
  - Blob weicht von der Basis ab;
  - fehlende Registry für die Probe.
- **Falsche Reihenfolge:**
  - sortierte IDs mit Matrix in YAML-Reihenfolge (Planmutant 1), obwohl die Hashes passend nachgerechnet wurden;
  - unsortierte IDs;
  - Probe-IDs nicht in YAML-Reihenfolge;
  - Knotenarray nicht gemeinsam permutiert.
- **Manipulierte Artefakte:**
  - Byte-Kippen (Containerhash);
  - Wertänderung bei korrigiertem Container (kanonischer Hash);
  - Wertänderung mit beiden Hashes korrigiert (Formelvergleich);
  - Abweichung vom gepinnten Hash;
  - Zusatzdatei im Artefaktordner.
- **Ungültige Werte:**
  - float32, NaN, asymmetrische Matrix, Diagonale ≠ 0, falsche Form;
  - Pickle-Objekte;
  - Bool als Parameter;
  - doppelte ID.
- **Überschreiben:** Bestehende Probe- oder Snapshot-Ausgaben werden nie überschrieben.

**Tests:** 22/22 (`python -m pytest experiments/lantern_reconstruction/tests`).

**Ad-hoc-Mutationsprüfung:** 11/11 erkannt, darunter Planmutant 1. Die vollständige Prüfung mit den 18 Planmutanten folgt in LR5.

## Offen

- **LR5:** vollständiges Mutationswerkzeug.
- **LR4:** Ridge-Entscheidung. Eine NumPy-Lösung ist zulässig, wenn Regularisierung, Interzept und numerische Stabilität unabhängig geprüft werden.
- **Archiv:** Die offiziellen Probe-Rohdaten liegen unter `D:/mandala/mandala-memory-results/lantern/lr1/probe_official/`.

In LR1 gab es keine Dynamik, keine Episoden, keinen Decoder und keine Forschungsrechnung. Originalmodule und M0–M12 sind unverändert; es gab keinen Freeze, keinen Merge und keinen Push.
