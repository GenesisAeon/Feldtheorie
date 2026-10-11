# Nachbericht zu Astras Vorstartreview `LANTERN_LR7_VORSTARTREVIEW_2822141` (2026-10-11)

**Ausgang:** Lantern `2822141`, Review-Paket `b05c8c8`. Astras Urteil: Der Freeze und der wissenschaftliche Kern sind bestätigt. Es gibt noch kein Start-GO, weil zwei Betriebsfehler im Startwerkzeug offen sind (LR7-F1, LR7-F2).
**Geändert:** nur `tools/lr7_research_run.py`, `tests/test_lr6.py`, `lr6/BETRIEB.md`, `lr7/LR7_VORSTART.md` und dieser Ordner.
**Nicht geändert:** Produktionsmodule, `protocol/`, Kandidat, Forschungsseed, CI-Workflow. Es lief keine Forschungsrechnung.

## 1. Reproduktion am Stand `2822141`

- **Beilage:** Die ZIP ist entpackt, alle 9 Prüfsummen (`SHA256SUMS.txt`) stimmen.
- **Review-Paket:** Der lokale Klon `D:\mandala\review-repo\mandala-memory-reviews` steht exakt auf `b05c8c88…` und hat keine Änderungen.
- **Astras 13 Proben** (`test_prestart_review.py`), gelaufen mit der Lab-venv, Python 3.11.9 / NumPy 2.2.6 / SciPy 1.15.3: **12 bestanden, 1 fehlgeschlagen.**
  - Die bestandenen umfassen die bewusste Reproduktion von **F1**: `ResumeRefused: run status is complete`, kein Bericht, Log unverändert.
  - Ebenso die von **F2**: Ein Smoke-Lauf der Entwicklungsstudie 2026100803 wird mit `--confirm-study 1` bis zum ersten Arbeitsschritt angenommen.
  - Die eine fehlgeschlagene Probe ist `test_actual_foreign_environment_is_refused`. Sie setzt Astras fremde Umgebung (Python 3.12.14) voraus. In der eingefrorenen Umgebung hier ist `research_start_allowed = true`, also das korrekte Gegenstück.
  - Beleg: `claude_repro_probes_2822141.json`.

## 2. Reparatur (nur das Werkzeug)

**LR7-F2: Zielprüfung `verify_target()`.** Sie läuft vor jeder Wirkung, also vor `keep_awake`, vor einem neuen Ereignis und vor Ausführung oder Bericht. Die Schritte:
1. Freeze über `runs.frozen_candidate()` und `runs.research_grid()`;
2. eine angegebene `--confirm-study` muss gleich der eingefrorenen Studie sein, ein falscher Wert wird nie ignoriert;
3. `runs.load_run()`, ein unlesbares oder verändertes Manifest wird abgewiesen;
4. `kind == "research"`;
5. Studie gleich dem Freeze;
6. gesamtes Raster gleich `research_grid(candidate)`;
7. `runs.check_resumable()` für Code, Konfiguration, Snapshot und Software.

`--resume <Laufordner>` bleibt als Kurzform erhalten, weil die Zielprüfung aus dem Manifest erfolgt.

**LR7-F1: Der Zustand bestimmt die Aktion** (Astras Reparaturvertrag, Tabelle §3):

| Zustand | Aktion |
|---|---|
| neu, `interrupted`, `incomplete` | `runs.execute`, danach Bericht |
| `running` | Abweisung mit Verweis auf `runs.recover()`; das Werkzeug entfernt keine Sperren |
| `complete`, Bericht fehlt | **nur** `release.write_release_report` (exklusiver Schreiber); kein `execute`, kein Training; `complete` bleibt |
| `complete`, Bericht vorhanden | read-only `release.release_report` (enthält keine Zeitstempel) und kanonischer JSON-Vergleich; bei Gleichheit Anzeige, bei Abweichung Halt mit unveränderter Datei; nie Überschreiben, nie Neurechnen |
| `failed_integrity`, `numerically_invalid` | Abweisung, kein automatischer Ersatzlauf |
| Bericht vorhanden, Status nicht `complete` | Abweisung; von Hand prüfen |

**Abschnitt 6 (Empfehlung, getrennt von F1/F2):** `--start` wird abgewiesen, wenn unter dem Laufordner schon ein Forschungsmanifest dieser Studie und dieses Rasters liegt oder ein unlesbares Manifest. Die Meldung nennt Lauf, Zustand und ob ein Bericht vorliegt.
- Die Prüfung ist **nicht atomar**; zwei gleichzeitige Aufrufe könnten beide passieren. Gleichzeitige Rechnung derselben Studie verhindert weiterhin die bestehende Studiensperre.
- Ein Ersatz nach endgültigem Fehler braucht eine dokumentierte Entscheidung.

## 3. Regressionstests

**17 Tests `test_lr7_*`** stehen in der **bestehenden** `tests/test_lr6.py`. Damit bleiben Astras 13-Dateien-Vertrag und der Workflow unverändert.
- Grundlage ist die synthetische Freeze-Fixture der Datei mit 2 Kontexten.
- `runs.execute` und, wo angegeben, der Berichtschreiber sind durch Rekorder ersetzt. **Es wird nichts numerisch gerechnet.**
- Der echte exklusive Schreiber wird beim Import festgehalten, damit Fixtures ihn nicht verdecken.

| Fall (Astra §5) | Test |
|---|---|
| keine Argumente | `test_lr7_dry_run_creates_and_runs_nothing` |
| Start ohne oder mit falscher ID | `test_lr7_start_without_or_with_wrong_confirmation_refused_before_creation` (2 Varianten) |
| Start und Resume | `test_lr7_start_and_resume_exclude_each_other` |
| richtiger Erststart | `test_lr7_valid_start_order_create_execute_report` (Reihenfolge awake → execute → report → awake aus) |
| Entwicklungslauf als Resume-Ziel | `test_lr7_f2_development_run_refused_as_resume_target` (Log unverändert, keine Wirkung) |
| falsche explizite Bestätigung bei Resume | `test_lr7_f2_wrong_explicit_confirmation_refused_on_resume` (die richtige wird angenommen) |
| abweichendes Raster bzw. abweichende Software | `test_lr7_f2_research_manifest_with_other_grid_or_software_refused` |
| Rechenabbruch | `test_lr7_execution_failure_releases_keep_awake` |
| `complete` ohne Bericht | `test_lr7_f1_complete_without_report_writes_report_only` (kein execute, genau ein Bericht) |
| `complete` mit Bericht | `test_lr7_f1_complete_with_report_never_overwritten_nor_recomputed` (auch ein manipulierter Bericht bleibt unverändert, Halt) |
| Fehler bei der Berichtserzeugung | `test_lr7_f1_report_failure_can_be_finished_later` (Zellen unverändert, zweiter Versuch schließt ab) |
| endgültiger Fehlerzustand | `test_lr7_final_states_refused_without_new_attempt` (2 Varianten) |
| zusätzlich: `running` | `test_lr7_running_refers_to_recover_and_removes_no_lock` |
| zusätzlich: Bericht ohne `complete` | `test_lr7_report_present_but_run_not_complete_refused` |
| zusätzlich: Abschnitt 6 | `test_lr7_section6_second_first_start_refused` |

**Gegenprobe am alten Werkzeug** (Stand `2822141` vorübergehend eingesetzt, danach bytegleich wiederhergestellt):
- **11 der 17 Tests schlagen fehl**, nämlich F1, F2, die Endzustände und Abschnitt 6.
- Die 6 übrigen prüfen Verhalten, das Astra bereits als korrekt bestätigt hat: Probelauf, Startabweisungen, `--start` mit `--resume`, `keep_awake` im `finally` und den gültigen Erststart.
- Ehrlicher Hinweis: Im ersten Versuch fiel auch „gültiger Erststart“ am alten Stand durch. Ursache war ein unvollständiger Testrekorder (Feld `scientific_blocks` fehlte), kein Altfehler. Der Rekorder ist korrigiert.

Am neuen Werkzeug: **17/17**.

## 4. Freeze unberührt

| | vor der Änderung | nach der Änderung |
|---|---|---|
| Kandidat (SHA-256, LF) | `68fac7fa0ddc43a2133af417c4fb8ccf64717ab52fe31ca02af7aa259b79b690` | identisch |
| Produktionsidentität | `670d9352e7fb6f7291318cbd36f0b2df2a17cdbd1cd84acf1e404cf16681ea2c` | identisch |

Belege: `identity_before.txt`, `identity_after.txt`. `code_identity` umfasst nur `*.py` des Labors und `protocol/*`; `tools/` und `tests/` gehören nicht dazu.

## 5. Abschluss-Grünlauf

Volle Lantern-Suite (Lab-venv, Python 3.11.9 / NumPy 2.2.6 / SciPy 1.15.3, Freeze vorhanden): **483 passed** (vorher 466; +17 LR7-Tests), 1074 s. Der CI-Zuordnungstest (13 Testdateien) besteht unverändert.

## 6. Offen

- Astras kurze Vorstart-Nachprüfung dieses Stands.
- Danach entscheidet **Johann** gesondert über den echten Start. Am Starttag wird die Bereitschaft erneut geprüft (`tools/lr7_readiness.py`, Probelauf).
