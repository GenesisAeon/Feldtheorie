# LR1 – Snapshot und Import (Bericht)

Trilayer: [`lr1_status.json`](lr1_status.json) (maßgeblich), [`lr1_status.yaml`](lr1_status.yaml), dieser Bericht. Artefakt: [`artifacts/registry_snapshot_v2/`](../artifacts/registry_snapshot_v2/); es ersetzt v1, siehe den Nachtrag unten.

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

**Tests:** 52/52 (nach dem Nachtrag) (`python -m pytest experiments/lantern_reconstruction/tests`).

**Ad-hoc-Mutationsprüfung** (ursprünglicher Stand `2a60c2b`): 11/11 erkannt, darunter Planmutant 1; nach dem Nachtrag effektiv 25/25. Die vollständige Prüfung mit den 18 Planmutanten folgt in LR5.

## Offen

- **LR5:** vollständiges Mutationswerkzeug.
- **LR4:** Ridge-Entscheidung. Eine NumPy-Lösung ist zulässig, wenn Regularisierung, Interzept und numerische Stabilität unabhängig geprüft werden.
- **Archiv:** Die offiziellen Probe-Rohdaten liegen unter `D:/mandala/mandala-memory-results/lantern/lr1/probe_official/`.

In LR1 gab es keine Dynamik, keine Episoden, keinen Decoder und keine Forschungsrechnung. Originalmodule und M0–M12 sind unverändert; es gab keinen Freeze, keinen Merge und keinen Push.

## Nachtrag nach `REVIEW_LR1` (Astra, Stand 2a60c2b)

Alle drei Gegenproben habe ich **zuerst unverändert reproduziert**:
- `g = 100`, leere Quellenangabe und Identitäts-Permutation wurden **mit dem originalen Array-Pin** akzeptiert;
- `beta[0] = 999` mit angepassten internen Hashes ging beim Standardaufruf durch;
- das Write-Flag ließ sich wieder einschalten, `C[0,1] = 123` war möglich, und der Hash blieb gleich.

Die Originalmatrix war nicht betroffen; es ging um die zugesicherten Prüf- und Schutzmechanismen.

| Befund | Korrektur |
|---|---|
| **R1** ungeprüfte Manifestwerte | Alle operativen Strukturwerte werden aus den geprüften Arrays **nachgerechnet** und mit dem Manifest verglichen: Knotensummen samt argmin/argmax, g, Eigenwerte und Kantenzahlen. Mit Repository kommt die `kappa`-Begrenzungszahl aus der unabhängigen Formel. Die Permutation wird gegen die aufgezeichnete YAML-Reihenfolge und die Registry geprüft. Die Quellen müssen genau die elf gepinnten Dateien sein, mit Blob = LF = Basis; Rohhashes bleiben nur informativ, weil sie vom Checkout abhängen. Das **ganze Manifest** ist über einen eigenen Manifest-Pin verankert. JSON wird streng geladen (keine doppelten Schlüssel, kein NaN). Die vertrauenswürdige API liefert nur nachgerechnete Werte; die Probe-Angaben stehen getrennt als `recorded_probe` (durch den Pin authentifiziert, nicht neu ausgeführt). |
| **R2** Knotenparameter | Beim Laden werden **alle** Knotenarrays und Metadaten gegen die Registry geprüft. Beide Pins sind **Pflichtargumente** ohne Vorgabe. Der Forschungseinstieg ist `load_verified_snapshot()` mit den Pins aus `SNAPSHOT_PIN` im geprüften Code. Der ungeprüfte Entwicklungs-Leser `read_snapshot_unverified()` ist getrennt und als UNVERIFIED gekennzeichnet. |
| **R3** Unveränderlichkeit | Die Arrays liegen auf **unveränderlichem Bytespeicher**; das Write-Flag lässt sich nicht wieder setzen. Alle Mappings, auch verschachtelte, sind schreibgeschützte Ansichten in einer eingefrorenen Dataclass. `working_copy()` liefert unabhängige Kopien für die Dynamik, `verify()` rechnet den kanonischen Hash nach und erkennt auch eine bewusste Umgehung. |
| **Importmanifest** | vollständige Modulliste (708) mit Ursprungsdatei und Roh-SHA-256; Repo-Dateien zusätzlich mit LF- und Blob-Hash; Paketversionen |

**Snapshot v2:**
- Kanonischer Hash `2d6a2a64…`, Manifest-Pin `5b7aa962…`.
- Die Zahlenwerte sind gleich v1. Der Schemaname geht in den kanonischen Hash ein, deshalb ist der Wert neu.
- v1 ist aus dem Baum entfernt und bleibt in der Git-Historie (`2a60c2b`).

**Gegenprobe danach:**
- Astras Manipulationen werden mit den Original-Pins abgewiesen (Manifest-Pin).
- Selbst mit vom Angreifer neu berechneten Pins werden sie abgewiesen: über die Permutation bzw. weil `beta` von der Registry abweicht.
- Das Write-Flag wird verweigert.

**Tests:** 52/52.

**Ad-hoc-Mutation:** 25 Mutanten, davon 14 neu für R1–R3. Im ersten Lauf wurden 24 erkannt. Überlebt hat `container_check_off`; das war eine echte Testlücke, denn ein inhaltsgleich neu verpacktes NPZ war ungetestet. Der neue Test erkennt ihn nachweislich, damit sind effektiv **25/25** erkannt.
