# CI: an Windows gebundene Herkunftsnachweise (2026-10-13)

## Anlass

Der Branch `lantern-reconstruction` lief am 2026-10-13 zum ersten Mal in GitHub Actions. Getestet wurde Commit `8aad978eaa` auf `ubuntu-latest`, mit Python 3.11 und 3.12 sowie numpy 2.2.6, scipy 1.15.3 und PyYAML 6.0.3.

**Drei Tests** schlugen dort fehl. In der Freeze-Umgebung (Windows, Lab-venv) bestehen dieselben Tests: 483/483.

| Test | Fehlerausgabe in CI (gekürzt) |
|---|---|
| `test_lr2.py::test_reference_artifact_provenance` | `assert run["kernel_file_raw_sha256"] == hashlib.sha256((ra.REPO / "v9_alpha/models/phase_dynamics.py").read_bytes()).hexdigest()` → `'767a98a4905a…143200015884e' == '3ad681d428d5…e3982f22f259d'` |
| `test_lr1.py::test_fresh_probe_rebuilds_exactly_the_pinned_snapshot` | `assert man["hashes"]["canonical_sha256"] == CPIN` → `'78d89a126423…edd1eb9357f98' == '2d6a2a6439ef…a3edf2df9ef2a'` |
| `test_lr1.py::test_probe_runs_the_full_loader_and_matches_the_snapshot` | `assert np.array_equal(raw["C_yaml_order"][np.ix_(perm, perm)], s.C)` → `assert False` |

## Befund

1. **`test_lr2`: Zeilenenden. Lokal bestätigt.**
   - Der eingefrorene Pin `767a98a4…` ist der SHA-256 der Rohbytes von `v9_alpha/models/phase_dynamics.py`, so wie Git sie unter Windows mit `core.autocrlf=true` auscheckt: mit CRLF, 4079 Bytes.
   - Unter Linux ergibt derselbe Blob mit LF (3946 Bytes) `3ad681d4…`.
   - Ein lokaler Checkout mit `core.autocrlf=false` reproduziert genau diesen Fehlschlag.
2. **`test_lr1`, beide Tests: Ursache NICHT bestätigt.**
   - Lokal mit LF-Checkout bestehen beide; Zeilenenden sind es also nicht.
   - Die Tests vergleichen die vom unveränderten Original-Loader berechnete Kopplungsmatrix **bitgenau** mit dem eingefrorenen Snapshot.
   - **Unbestätigte Vermutung:** Die Mathematik-Bibliothek rundet unter Linux in der letzten Stelle anders als unter Windows. Geprüft wurde das nicht, weil uns dafür kein Linux-System zur Verfügung stand.

## Umgang (Johann und Astra, 2026-10-13)

- **Eingefrorene Dateien und Pins bleiben unverändert.** Kein Test wurde gelockert oder umgeschrieben.
- Die drei Tests laufen im CI-Job `windows-bound-provenance` auf `windows-latest`.
  - Die Zeilenenden werden **ausdrücklich** konfiguriert (`git config --global core.autocrlf true` vor dem Checkout), denn `windows-latest` allein garantiert keinen CRLF-Checkout.
  - Ein eigener Schritt prüft vorher, dass die Altquelle tatsächlich CRLF enthält.
- Unter Linux sind genau diese drei Tests **ausdrücklich** per `--deselect` ausgenommen; das steht im Workflow und ist im Log sichtbar. Alle übrigen Kernkontrollen laufen weiter unter Linux.
- `tests/test_lr1_platform.py` (neu) führt die plattformunabhängigen Teile der beiden LR1-Tests auf **jeder** Plattform aus:
  - Formelprüfung ≤ 1e-14;
  - Permutation und ID-Reihenfolge exakt;
  - eingelesene Module;
  - Matrix bis auf 1e-14;
  - dazu eine Negativkontrolle.
- Die tolerante Formelprüfung aus LR0 (`test_lr0.py`, ≤ 1e-14) läuft ebenfalls weiter unter Linux.

## Erster CI-Lauf nach der Korrektur (`eac320713f`) und Nachbesserung

- **Unter Linux bestehen** `test_lr1_platform.py` und alle übrigen LR0/LR1-Tests: 53 passed, 2 deselected, unter Python 3.11 und 3.12.
  - Die vom Original-Loader berechnete Matrix weicht unter Linux also höchstens um 1e-14 vom eingefrorenen Snapshot ab.
  - Das ist **vereinbar** mit der Rundungs-Vermutung, aber kein Beweis.
- Zwei Fehler der Korrektur selbst, behoben im Folgecommit:
  1. **Windows-Job:** Das Probe-Werkzeug verweigert absichtlich Schreibzugriffe auf C:, und das Standard-Temp von pytest liegt dort. Lösung: `--basetemp` auf `runner.temp`, das auf GitHubs Windows-Runnern auf D: liegt.
  2. **Meta-Test** `test_lr5_alarms.py::test_ci_workflow_runs_every_lab_test_file_exactly_once_without_masking`: Er kannte weder den Windows-Job noch `--deselect`.
     - Er wurde **verschärft**, nicht gelockert. Jede Testdatei wird weiterhin genau einmal aufgerufen; jetzt sind es 14 Dateien.
     - Neu: Jeder unter Linux ausgenommene Test muss genau im Windows-Job laufen, und der Windows-Job darf nichts anderes enthalten.
     - Neu: Der Windows-Job muss `windows-latest` mit ausdrücklicher CRLF-Konfiguration verwenden.
     - Drei Mutanten werden erkannt: fehlende Ausnahme, fehlender Windows-Test, fehlende CRLF-Konfiguration.

## Grenzen

- **Ein grüner Windows-Lauf erklärt die Linux-Abweichung nicht.** Er zeigt nur, dass die Nachweise in ihrer Entstehungsumgebung reproduzierbar sind.
- Die Herkunfts- und Bitgleichheitsnachweise aus LR1 und LR2 sind damit **an Windows gebunden**.
- Plattformunabhängige Pins wären eine neue Protokollversion und brauchen Johanns Entscheidung.
- Läge die Linux-Abweichung über 1e-14, würde `test_lr1_platform.py` unter Linux fehlschlagen. Auch das wäre ein Befund, kein Fehler dieser Korrektur.
