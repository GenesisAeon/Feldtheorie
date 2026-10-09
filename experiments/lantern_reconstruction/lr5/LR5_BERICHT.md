# LR5 – Laufverwaltung, Freigabe-Gate und CI (Bericht)

**Stand:** 2026-10-09, Branch `lantern-reconstruction`.
- Teil 1 `dba1f1e`: LR5-A1.
- Teil 2 `fff9dd7`: Artefaktkette, Laufverwaltung, Resume, Freigabe-Gate.
- Teil 3: Trajektorien-Wiederverwendung, Budget, CI, Mutationskampagne und dieser Bericht.

Maßgeblich ist [`LANTERN_LR4_NACHREVIEW_25ba293_2026-10-08`](../../../../mandala-memory-results/lantern-reconstruction-plan/LANTERN_LR4_NACHREVIEW_25ba293_2026-10-08.md), mitsamt den verbindlichen LR5-Pflichten aus `REVIEW_LR4`.

Es gab **keinen Forschungs-Freeze und keinen Forschungslauf**, außerdem keinen Merge und keinen Push. Gelaufen sind nur Entwicklungs- und Smoke-Läufe auf der Entwicklungsstudie, dazu synthetische Kontrolldaten.

## LR5-A1: positiver Scheinerfolg und Zielabhängigkeit getrennt

**Zuerst reproduziert** (am Stand `25ba293`, eigenes Skript; Prüfsummen des Review-ZIP stimmen):
- Vorhersage 0,75 + 0,1u bei 10 Zielwerten in [−0,1; 0,1] ergibt G = **−1,6851777777777779**, b = 0, p = 0,0001, Holm über 12 Zellen 0,0012.
- Der alte reine p-Alarm hat ausgelöst.
- Von Hand hergeleitet: G = 3·(0,19·m₂ − 0,5625) mit m₂ = 0,01·11/27.

| Teil | Umsetzung |
|---|---|
| **Zwölf benannte Zellen** (`protocol/control_alarms.json`, festgelegt vor jedem Lauf) | Kontrollen `reset`, `zero_impulse`, `permuted_targets` × Aufgaben A/B × τ ∈ {1, 5}, auf der Lantern-Kopplung. Namen `{control}\|{task}\|{tau}` in fester Reihenfolge; diese Reihenfolge ist die Holm-Familie. |
| **Statistik** | Je Zelle das beobachtete mittlere G über die Kontexte. Permutationstest mit festen Vorhersagen: Testziele werden innerhalb jedes Kontexts permutiert, **B = 9999**, p = (1 + b)/(1 + B), ein eigener Strom je Zelle. |
| **Holm** | Immer über **alle 12** Zellen, nie über eine Auswahl, etwa nur die positiven Zellen. |
| **Zwei getrennte Alarme** (`metrics.control_alarms`, ersetzt `leak_alarm`) | **`positive_spurious_success`:** G > 0 **und** Holm-p ≤ 0,01; das ist der Alarm des Plans auf unerwartet positives G. **`target_dependence`:** Holm-p ≤ 0,01 bei beliebigem Vorzeichen von G. Jede Zelle liefert G und p **gemeinsam**. Fehlende, zusätzliche oder falsch benannte Zellen werden abgewiesen. |
| **Kontrolle `permuted_targets`** | Die Trainingsziele werden über den Decoder-Strom permutiert: (Studie, Kontext, train, decoder, 0, 2, Aufgabe, Zeitindex). Validierung und Test bleiben unpermutiert; die Trajektorien sind dieselben wie in der Hauptbedingung. |

**Freigaberegel: VORSCHLAG, vor dem Freeze von Johann und Astra zu entscheiden.**
- Jeder der beiden Alarme setzt `scientifically_interpretable = false` und sperrt die wissenschaftliche Freigabe bis zu einer dokumentierten Untersuchung.
- Negatives G macht eine unerwartete Zielabhängigkeit nicht harmlos.
- Auf `technically_complete` wirken die Alarme nicht.
- Das Gate wendet diesen Vorschlag an, bis eine Entscheidung ihn ersetzt (`release_rule.status = "PROPOSAL"`).

**Beim Testen gefunden:** Mit B = 999 ist das kleinste Holm-p über 12 Zellen 12/1000 = 0,012 > 0,01. Der Alarm hätte also **nie** auslösen können. `alarm_inputs` erzwingt deshalb das Protokoll-B von 9999.

**Abgedeckte Fälle:**
- Astras Gegenfall (nur Abhängigkeitsalarm);
- positives G mit kleinem p (beide Alarme);
- positives G ohne Signifikanz (kein Alarm);
- p = 0,004 in der einzigen positiven Zelle: Holm über 12 ergibt 0,048, also kein Alarm; eine Teilmenge hätte fälschlich ausgelöst;
- fehlende, zusätzliche und falsch benannte Zellen.

## Artefaktkette, Laufverwaltung, Resume, Freigabe-Gate

| Pflicht (Review) | Umsetzung |
|---|---|
| **Externe Artefaktidentität** | `run.json` wird einmal und exklusiv geschrieben. Es enthält Raster, Code-Identität (SHA-256 jedes Produktionsmoduls und jeder Protokolldatei, LF-normalisiert, plus Git-Commit), Konfiguration, Snapshot-Pins und Software; die **Laufidentität** hasht all das. Jede Zelle hat einen `record.json`, der Modellidentität, Datei-Hashes, Vorhersageidentitäten und Scores an Laufidentität und erwartete Zelle bindet (Studie, Kontext-Fingerabdruck, Bedingung, Kontrolle, Aufgabe, Zeit, dt). Die **Modellidentität** bindet Arrays und Metadaten gemeinsam. |
| **Atomar und ohne Überschreiben** | `artifacts.write_exclusive` schreibt eine temporäre Datei, ruft `fsync` auf und übernimmt sie mit `os.link` unter den Zielnamen. Existiert der Name, schlägt das fehl, auch in einer Race Condition (getestet). Der Datensatz wird zuletzt geschrieben; eine Zelle existiert nur mit ihm. Freigabeberichte entstehen einmalig. |
| **Deterministische Wiederaufnahme** | Dieselbe Lauf-ID wird nur fortgesetzt, wenn Code, Protokoll, Konfiguration, Snapshot und Raster unverändert sind; sonst kommt `ResumeRefused` mit Liste der geänderten Teile. Jede neu berechnete Zelle wird mit vorhandenem Datensatz bzw. verwaisten Dateien abgeglichen (Identitäten, nie ZIP-Bytes); eine Abweichung führt zu `failed_integrity`, das endgültig ist. **Unterbrechung plus Resume ergibt exakt den ununterbrochenen Lauf** (identische Modelle, Vorhersagen und Scores, getestet). |
| **Modellintegrität** | Die Modellidentität wird **vor und nach** der Auswertung geprüft (`evaluate_with_integrity`). Beim Lesen wird jeder Datensatz verifiziert: Dateien, Modellidentität, Zellbindung, Stichprobenzahl, Endlichkeit; G, S und λ werden **aus den verifizierten Vorhersagen exakt nachgerechnet**. |
| **Laufverwaltung** | Exklusive Sperre je Studie und Phase, unabhängig vom Zielordner. Nur-anhängendes Ereignisprotokoll mit `fsync`, UTC und monotoner Zeit; eine Uhrenlücke wird als vermutete Schlafunterbrechung protokolliert. Laufstatus mit erlaubten Übergängen; kein Score ändert einen Status. Studien-Lebenszyklus nach Plan § 12; `runs.py` führt nur `development` und `smoke` aus. |
| **Vollständiges Freigabe-Gate** (`release.py`) | Drei **getrennte** Felder: <br>• `technically_complete`: exaktes Raster, alle Datensätze verifiziert, keine Zelle außerhalb, Strukturprüfung je Kontext vorhanden **und nachgerechnet**, Status `complete`. <br>• `scientifically_interpretable`: zusätzlich Reset und Nullimpuls identisch für u und −u, keiner der beiden LR5-A1-Alarme, Konvergenzgate gebunden und bestanden, Aufgabe A mit G0 > 0,90. <br>• `hypothesis`: bei Entwicklungs- und Smoke-Läufen `not_evaluated`. <br>Fehlende Kontrollen sperren. |

**Beim Entwurf der Manipulationstests gefunden und geschlossen:**
- Ein editierter Score im Datensatz wäre durchgegangen; jetzt wird er nachgerechnet.
- Eine editierte Strukturprüfung wäre ebenfalls durchgegangen; das Gate rechnet sie jetzt deterministisch nach.

**Ein Smoke-Lauf zeigt das Gate korrekt:** 2 Kontexte, 30/12/20 Episoden, 140 Zellen. Er ist technisch vollständig, wissenschaftlich aber gesperrt, weil G0 = 0,67 bei 30 Trainingsepisoden unter 0,90 liegt. Die Hypothese ist `not_evaluated`.

## Budget (Plan § 13; `tools/lr5_budget.py` → `lr5/lr5_budget.json`)

Gemessen wurde auf diesem Rechner, jeder Messblock unter 5 Minuten. Die Werte für die volle Studie sind **Hochrechnungen**.

| Größe | Wert |
|---|---|
| Dynamik: 2250 Episoden, eine Bedingung (gemessen) | 59,2 s |
| Ridge, 14 Zellen (gemessen) | 0,16 s |
| Speichern und Scoren, 14 Zellen (gemessen) | 0,22 s; 103 kB je Zelle |
| Alarm, eine Zelle mit 20 Kontexten × 1000 Episoden, B = 9999 (gemessen) | 17,2 s |
| Spitzen-RAM des Messprozesses (gemessen) | 115 MB |
| **Produktion/Training, 1960 Zellen (hochgerechnet)** | **5987 s ≈ 1,66 h** (Entwurfsbudget 2 h) |
| Auswertung (hochgerechnet) | 238 s (Budget 30 min) |
| Artefakte (hochgerechnet) | 202 MB (Budget 1 GiB) |

**Ehrlich zum Verlauf:**
- Die **erste Messung lag über dem Budget**: 8083 s ≈ 2,25 h. Die Kontrolle `permuted_targets` integrierte dieselben Lantern-Trajektorien ein zweites Mal, entgegen Plan § 13 („Trajektorien nur einmal berechnen“).
- Seit der Korrektur ist der Trajektorien-Cache **über den Inhalt der Anfangszustände adressiert**. Gleiche Eingaben werden je Kontext nur einmal integriert; das betrifft auch Reset und Nullimpuls, die beide bei φ·1 starten. Damit sind es 5 statt 7 Simulationen je Kontext, mit bitgleichen Ergebnissen (Test).
- Die erste RAM-Messung meldete wegen fehlender 64-Bit-ctypes-Signaturen 0 Bytes und trotzdem „im Budget“. Eine fehlgeschlagene Messung heißt jetzt `None` (nicht gemessen).
- Die Reserve zur 2-h-Grenze beträgt rund 17 %. Sie ist rechnerabhängig und keine Zusage.

## CI (`.github/workflows/lantern-reconstruction.yml`)

- **Drei ausdrücklich aufgerufene Jobs:**
  - Kernkontrollen: LR2–LR4 und LR5-A1;
  - Legacy-Adapter/Import: LR0–LR1, mit vollständiger Git-Historie;
  - Smoke: Laufverwaltung und Freigabe-Gate.
- **Matrix:** Python 3.11 und 3.12, mit gepinnten Abhängigkeiten.
- **Keine Maskierung:** kein `|| echo`, kein `continue-on-error` (LR0-O2).
- **Lokal geprüft:** gültiges YAML; jede der 11 Testdateien wird genau einmal aufgerufen.
- **Nicht ausgeführt:** Der Workflow lief noch nie auf GitHub, weil der Branch nicht gepusht ist. Lokal gibt es kein Python 3.12; Belege für 3.12 stammen nur aus Astras Teilprüfung (3.12.14).

## Mutationskampagne (Plan § 15; `tools/lr5_mutation_campaign.py` → `lr5/lr5_mutation_campaign.json`)

**34 Mutanten ausgeführt, 33 erkannt, 1 äquivalent, 0 offene Überlebende.**

- **Plan-Mutanten:** Alle 16 ausführbaren werden von einem zuständigen Test erkannt: 1, 3, 4, 5, 7, 8, 9, 10, 11, 12-analog, 13, 14, 15, 16a (Kurve), 16b (Freigabe), 17, 18a (geänderter Code/Seed), 18b (fremdes Modell beim Resume).
  - **Mutant 2** (nur C permutieren) ist eine Eigenschaft eines Invarianztests; der Nachweistest wurde ausgeführt und besteht.
  - **`not_applicable`:** 6 (SDE erst in LR9) und 12 (MLP nicht implementiert); das Ridge-Gegenstück 12-analog wird erkannt.
  - Mutant 11 ist ehrlich abgebildet: Der Fit sieht den Test nie, deshalb wird Train+Val mutiert.
- **LR5-Mutanten:** 16 zu Überschreiben, Integrität, Score-Nachrechnung, Strukturprüfung, Sperre, Statusübergängen, Laufidentität, Zellbindung, Zellen außerhalb des Rasters sowie sechs zu LR5-A1.
  - **Im ersten Lauf überlebt, als echte Testlücken geschlossen:**
    - **L1:** `os.replace` statt `os.link`; jetzt gibt es einen Race-Test.
    - **L9:** Datensatz-Bindung aus; jetzt gibt es Attacken, die nur die Bindung erkennt.
  - **Äquivalent: L2.** Ohne die Vorab-Existenzprüfung weist `os.link` trotzdem ab; nichts wird überschrieben. Das bestätigt sich darin, dass auch der Race-Test unter dem Mutanten besteht.
  - Das Ergebnis des ersten Laufs bleibt als `history` im JSON.

**Tests:** 349/349 (bisher 295; LR5 kommt mit 54 Tests in `test_lr5_alarms.py` und `test_lr5_runs.py` dazu).

**Belege:** `D:/mandala/mandala-memory-results/lantern/lr5/` (Kampagnenprotokoll, Messausgaben).

## Nachtrag nach `REVIEW_LR5` (Astra, geprüft `1c24292`)

**Ergebnis der Prüfung:** 349/349 bestätigt, aber vier reproduzierte Lücken. Beide Alarme sollen sperren; das befürworten Johann und Astra.

**Zuerst reproduziert** (Kopie von Astras Skript, Arbeitsordner im Temp; ihr Reviewordner blieb unverändert; ein eigener Fixture-Lauf mit 30/12/20):
- **R1:** Status `running` ergab `ValueError: status transition running -> running`; der Lauf blieb `running`.
- **R2:** n_train = 2 und n_val = 2 mit konsistent erneuerten Prüfsummen wurden akzeptiert (`technically_complete = true`).
- **R3:** Die Versionen `0.0.changed` für Python und NumPy hielten das Fortsetzen nicht auf.
- **R4:** Eine NPZ mit nur `wrong = [123.]` wurde umbenannt und ersetzt.

Alle Werte stimmten mit Astras Werten überein, bis hin zur neuen Modellidentität.

| Befund | Korrektur |
|---|---|
| **R1** Prozessverlust | `execute()` verweigert bei `running` mit Hinweis; es gibt **kein** `running → running`. Der ausdrückliche Weg ist **`runs.recover()`**: <br>• Sie bestimmt den haltenden Prozess aus dem lauf-eigenen Ereignis `lock_acquired` (Sperrpfad, PID, Host). <br>• Sie verweigert bei fremdem Host, bei möglicherweise noch lebender oder nicht entscheidbarer PID (Windows `OpenProcess`/`GetExitCodeProcess`; eine wiederverwendete PID gilt konservativ als lebendig) und bei einer Sperre, die inzwischen jemand anderem gehört. <br>• Sie entfernt nur die tote Sperre **dieses** Prozesses und protokolliert deren Inhalt. <br>• Unter der Studiensperre setzt sie `interrupted`; danach setzt `execute()` dieselbe Laufidentität fort, alle Artefakte bleiben, jede Zelle wird erneut verifiziert. <br>Auch ein Verlust zwischen Sperre und Status wird erkannt. **Unerwartete Ausnahmen** führen fest zu `interrupted`. Eine **abgeschnittene letzte Protokollzeile** wird nur durch Anhängen abgeschlossen (Zeilenumbruch, dann ein Ereignis `log_line_truncated` mit SHA-256 und Länge des Fragments); eine unlesbare Zeile ohne diese Quittung ist ein Integritätsfehler. |
| **R2** Größen | `check_model_against_run` prüft **beim Schreiben und beim Lesen** unabhängig gegen den Lauf bzw. das Protokoll: `n_train` und `n_val` gegen die Größen des Rasters, das λ-Raster gegen `training.LAMBDA_GRID`, Python und NumPy des Modells gegen die Software des Laufs. |
| **R3** Software | `check_resumable` verlangt **strikt gleiche** Versionen von Python, NumPy und SciPy, die jetzt alle im Lauf festgehalten sind. Eine Kompatibilitätsregel gibt es nicht. |
| **R4** Teilmodell | `_adopt_orphans` prüft **jede** vorhandene Datei für sich gegen das neu berechnete Modell: JSON-Identität; NPZ-Namen, dtype und Array-Identitäten, auch ohne JSON; unlesbare oder pickle-pflichtige NPZ. Abweichung bedeutet `failed_integrity`; nichts wird umbenannt oder ersetzt. Eine **gültige** Hälfte wird kontrolliert ergänzt (nur die fehlende Datei, exklusiv). |

**Regressionen** (`tests/test_lr5_review.py`, 23 Tests, positive Referenzen zuerst):
- Astras Zustand `running` ohne Prozess: Verweigerung statt `ValueError`.
- **Echter Kindprozess**, der mitten im Lauf hart getötet wird: Es wird der Prozess getötet, der die Sperre hält. Unter Windows ist die `python.exe` des venv nur ein Starter mit dem eigentlichen Interpreter als Kindprozess; den Starter allein zu töten wäre nicht der getestete Prozessverlust. `recover()` erkennt die PID als tot, und die Fortsetzung ergibt **exakt den ununterbrochenen Lauf**.
- Abgeschnittene Protokollzeile, unquittierte unlesbare Zeile, unerwartete Ausnahme, lebende PID und fremder Host.
- R2 mit jeder Größe einzeln und mit geänderter Modellsoftware, dazu die Abweisung vor jedem Schreiben.
- R3 für Python, NumPy und SciPy einzeln, unveränderte Umgebung als Positivkontrolle.
- R4: Astras NPZ (Datei unverändert, nichts Neues geschrieben), richtige Namen mit falschen Werten, Müll-Bytes, Objekt-Arrays, gültige NPZ allein, JSON allein gültig und falsch, und Ende-zu-Ende (nur `model.npz` überlebt, Fortsetzung ergibt den ununterbrochenen Lauf).

**Mutation der neuen Wächter:** 11 Mutanten, 10 erkannt. **R4b** ist äquivalent: Liefert eine unlesbare NPZ `{}` statt eines Fehlers, stimmt `{}` nie mit den erwarteten Identitäten überein, und die Datei wird weiterhin abgewiesen; nur die Meldung ändert sich. **Gesamt: 45 ausgeführt, 43 erkannt, 2 äquivalent (L2, R4b), 0 offene Überlebende.**

**Freigaberegel:** von Johann und Astra **befürwortet**; sie wird mit dem Forschungs-Freeze verbindlich (`protocol/control_alarms.json`). Astras Präzisierungen sind übernommen:
- Eine Untersuchung ist kein automatisches Aufheben der Sperre.
- Befund, Ursache, Konsequenzen und gegebenenfalls eine neue Protokollfassung werden dokumentiert.
- Beide Namen bezeichnen denselben gerichteten Permutationstest, mit und ohne die Bedingung G > 0.
- Ein ausbleibender Alarm beweist keine Unabhängigkeit.

**Tests:** 372/372 (bisher 349, dazu 23 in `tests/test_lr5_review.py`).

**Belege:** `D:/mandala/mandala-memory-results/lantern/lr5_review/`.

## Nachtrag nach Astras Nachprüfung von `b9c405b`

**Ergebnis der Nachprüfung:**
- R2, R3 und R4 sind bestätigt geschlossen.
- Die 23 Regressionstests bestehen, einschließlich des echten Prozessabbruchs.
- Offen blieben zwei Punkte:
  - **F1:** `recover()` schrieb beim Quittieren einer abgeschnittenen Zeile ins Log, *bevor* es prüfte, ob der Besitzer noch lebt. Nach der korrekten Ablehnung war das Log verändert und, sobald der lebende Schreiber seine Zeile abschloss, nicht mehr lesbar.
  - **F2:** Der Workflow führte `test_lr5_review.py` nicht aus.

**Zuerst reproduziert** (Kopie von Astras Skript, Arbeitsordner im Temp): `owner_alive = true`, `log_changed_despite_refusal = true`, danach `TruncatedLogError`. Dabei fiel mir zusätzlich auf, dass die angehängte Zeile auf `\r\n` endete: `EventLog` schrieb im Textmodus.

| Befund | Korrektur |
|---|---|
| **F1** | `recover()` beginnt mit einer **rein lesenden Diagnose** (`_recovery_diagnosis`, `EventLog.read_tolerating_tail`). Das unvollständige Ende wird erkannt, aber nicht verändert. Status, haltender Prozess, Host, PID-Zustand und Sperrbesitz werden **vor jedem Schreiben** entschieden; jede Ablehnung lässt Log und Sperre bytegleich. Erst danach folgen: **exklusive Recovery-Sperre** (`<sperre>.recover`, `O_EXCL`; ein paralleles Recovery wird abgewiesen), **erneute Diagnose unter dieser Sperre** (abweichende Lage führt zur Ablehnung), dann die anhängende Reparatur der Zeile, das Entfernen der toten Sperre und der Statuswechsel. |
| **F2** | `test_lr5_review.py` steht im Smoke-Job. Der lokale Vollständigkeitscheck ist jetzt ein **Test** (`test_ci_workflow_runs_every_lab_test_file_exactly_once_without_masking`): Die Dateilisten aller Jobs müssen zusammen genau den 12 Testdateien des Labors entsprechen, ohne Maskierung. Der Workflow ist auf GitHub weiterhin **nie gelaufen**. |
| **Zusatz** | `EventLog` schreibt binär mit `\n`, auf jeder Plattform gleich (Test). |

**Regressionen:**
- Abgelehnte Recovery mit unvollständiger Zeile, je Fall bytegleiches Log und bytegleiche Sperre: lebender Besitzer (danach schließt der Schreiber seine Zeile ab und das Log bleibt lesbar), fremder Host, nicht entscheidbarer Prozesszustand, Sperre eines anderen Laufs, laufende zweite Recovery.
- Eine **Wettlaufsituation** zwischen Diagnose und Recovery-Sperre: Ein anderer Lauf übernimmt die Sperre, die erneute Prüfung verweigert, die fremde Sperre bleibt unberührt.
- Positivfall: toter Besitzer und unvollständige Zeile. Die Recovery gelingt, die ursprünglichen Bytes bleiben Präfix des Logs, und die Fortsetzung ergibt den ununterbrochenen Lauf.

**Mutation der neuen Wächter:**
- **Erkannt:** F1a (Reparatur vor der Besitzerprüfung, also die geprüfte alte Reihenfolge), F1b (Recovery-Sperre nicht exklusiv), F2 (Datei aus dem Workflow entfernt) und LF (Textmodus).
- **F1c** (keine erneute Prüfung unter der Sperre) überlebte zunächst, weil kein Test das Zeitfenster zwischen Diagnose und Sperre abdeckte. Diese echte Testlücke ist mit dem Wettlauftest geschlossen.
- **Gesamtkampagne:** 50 ausgeführt, 48 erkannt, 2 äquivalent (L2, R4b), 0 offene Überlebende.

**Tests:** 381/381 (bisher 372, dazu 8 in `test_lr5_review.py` und der CI-Auswahltest).

**Belege:** `D:/mandala/mandala-memory-results/lantern/lr5_followup_b9c405b/`.

## Nachtrag nach Astras Nachreview zu `9b52d95` (`LANTERN_LR5_NACHREVIEW_9b52d95_2026-10-09`)

**Ergebnis des Nachreviews:** geprüft wurde das private Paket `26ffbdf`.
- F1 (Beschädigung bei lebendem Schreiber) und F2 (CI-Auswahl) sind behoben.
- Zwei verbleibende Lücken des Recovery-Gates:
  - **N1:** Gültiges JSON am Dateiende **ohne** LF galt als sauber. Recovery hängte das nächste Ereignis direkt daran, es entstand eine unlesbare Zeile (`TruncatedLogError`), und die alte Sperre war schon entfernt.
  - **N2:** Die `.recover`-Sperre koordinierte nur Recovery-Aufrufe. Ein normaler `StudyLock`-Erwerb in einem zweiten Prozess bekam die Studiensperre zwischen dem Entfernen der alten und der neuen Übernahme; Recovery scheiterte danach mit bereits vorgenommenen Änderungen.

**Zuerst reproduziert** mit Astras Skript, unverändert gegen den lokalen Checkout von `26ffbdf` und erstmals unter Windows (Astra prüfte unter Linux):
- N1: `diagnosed_tail: null`, danach `TruncatedLogError`.
- N2: Der Konkurrent meldete `acquired: true, guard_exists: true`, Recovery scheiterte mit `LockError`, der Lauf blieb `running`.
- Die Positivkontrollen (unvollständiges Objekt; gültiges Objekt mit LF) verliefen wie bei Astra.

| Befund | Korrektur |
|---|---|
| **N1** | `EventLog.read_tolerating_tail` beurteilt **JSON-Syntax und Zeilenabschluss getrennt**. Es gibt drei Zustände: sauber (leer oder LF-abgeschlossen); `unterminated_event`, ein gültiges Ereignis ohne LF, das **in der Ereignisliste bleibt**; `incomplete`, eine unlesbare letzte Zeile, auch mit abgeschnittenem UTF-8. Striktes Lesen verlangt ein LF-abgeschlossenes Ende. `repair_tail` ergänzt erst unter der Verwaltungssperre durch Anhängen das LF und ein Ereignis (`log_line_terminated` bzw. `log_line_truncated`). |
| **N2** | Es gibt eine **gemeinsame Verwaltungssperre** (`AdminLock`, `<sperre>.admin`, `O_EXCL`, mit Token). **Jeder** normale `StudyLock`-Erwerb nimmt sie kurz um das Prüfen und Anlegen. `recover()` hält sie über die erneute Diagnose, die Reparatur, das Entfernen der toten Sperre, die neue Übernahme (`StudyLock(..., admin=...)`, ohne blockierenden Wiedereintritt, Besitz über das Token geprüft) und den Statuswechsel. Ein Konkurrent wird **sofort abgewiesen**, nicht blockiert. Eine liegengebliebene Verwaltungssperre wird nie automatisch gelöscht; ihr Inhalt (Zweck, PID, Host, Zeit) dient der Prüfung von Hand. Die bisherige `.recover`-Sperre ist ersetzt. |
| Docstring | `recover()` beschreibt jetzt die tatsächliche Reihenfolge (lesende Diagnose, dann Verwaltungssperre, dann erneute Diagnose, dann Schreiben). |

**Regressionen**, mit echten Kindprozessen wie in Astras Szenarien:
- **N1-Dateienden:** gültiges JSON ohne LF, gültiges JSON mit LF, unvollständiges Objekt, abgeschnittenes UTF-8 und leeres Ende. Der Besitzer ist jeweils ein echter, beendeter Kindprozess. Die Recovery gelingt, die alten Bytes bleiben Präfix, striktes Lesen funktioniert, und das gültige Ereignis steht weiter in der Liste. Es bleiben weder die tote Sperre noch eine Verwaltungssperre zurück.
- **N1 bei lebendem bzw. unklarem Besitzer** mit gültigem Ereignis ohne LF: Log und Sperre bleiben bytegleich.
- **N2, Recovery gegen normalen Start** als getrennte Prozesse, an zwei Synchronisationspunkten (nach dem Entfernen der toten Sperre; unmittelbar vor der neuen Übernahme): Der Start wird abgewiesen, Recovery schließt ab, danach gelingt der Start.
- **Normaler Start vor Recovery** (vor der letzten Diagnose): Recovery verweigert **vor** jeder Logänderung, und die lebende Sperre bleibt unberührt.
- **Recovery gegen Recovery** als getrennte Prozesse: Abweisung ohne Änderung, danach gelingt sie.
- Eine fremde Verwaltungssperre wird nie entfernt, und eine nicht gehaltene wird für `StudyLock` abgewiesen.

**Nachher-Beleg:** Astras vier Szenarien, ohne die Pinprüfung gegen den reparierten Code ausgeführt:
- unvollständiges Objekt, gültiges JSON ohne LF und gültiges JSON mit LF enden alle in `interrupted` und sind lesbar;
- der gleichzeitige Start wird mit „administration … in progress“ abgewiesen, Recovery endet in `interrupted`, es bleibt keine Sperre zurück.

**Mutation:** N1 (gültiges JSON ohne LF wieder als sauber), N2a (normale Starts ohne Verwaltungssperre), N2b (Verwaltungssperre nicht exklusiv) und N2c (keine erneute Diagnose unter ihr) werden **alle erkannt**. **Gesamtkampagne: 54 ausgeführt, 52 erkannt, 2 äquivalent (L2, R4b), 0 offene Überlebende.** Die Einträge F1a bis F1c beschreiben die frühere `.recover`-Fassung und bleiben als Verlauf stehen.

**Tests:** 393/393 (bisher 381, dazu 12 in `test_lr5_review.py`).

**Belege:** `D:/mandala/mandala-memory-results/lantern/lr5_nachreview_9b52d95/`.

## Offen

- **LR6:** Entwicklungsabnahme und Freeze-Kandidat. Dazu gehören Masterseeds und Kontextliste, das optionale MLP (oder dessen ausdrücklicher Verzicht), vollständig entschiedene Protokollwerte und ein voller Entwicklungslauf mit allen Kontrollkurven auf der Entwicklungsstudie.
- **CI auf GitHub** erst, wenn der Branch gepusht werden darf.
- Astras gezielte Nachprüfung von N1 und N2 (Entscheidung über das Recovery-Gate).
