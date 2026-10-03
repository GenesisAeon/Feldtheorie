# Mandala-Gedächtnislabor: „Reiz → Pause → Erinnerung“

Kleines, reproduzierbares CPU-Experiment. Es fragt: Welche Information über einen vergangenen Reiz bleibt nach einer reizfreien Pause aus dem Zustand eines kleinen modularen Netzes lesbar, und wie verändern Kopplung und Anpassung das?

- **Feldtheorie** liefert Modell und Protokoll.
- **SCF** (`scoped-correspondence==0.42.0`) liefert geprüfte Bausteine: Budgetmatrix, Hebb-Regel, Split- und Auswerteprüfungen.
- **unified-mandala** (`experiments/memory_lab/`) zeigt Zustände und Eingriffe.

Die Arbeitsschritte M0–M9 und alle Befunde stehen in [ROADMAP.md](ROADMAP.md), das eingefrorene Protokoll unter [protocol/](protocol/).

## Startbefehle

Alle Befehle im Wurzelverzeichnis von `D:/mandala/.worktrees/feldtheorie-mandala-memory` ausführen. Mit `PY` ist die Umgebung `D:/mandala/.venvs/mandala-memory/Scripts/python.exe` gemeint.

| Zweck | Befehl | Dauer / Ablage |
|---|---|---|
| Tests, Pflicht-Labortestlauf (224) | `MANDALA_LAB_REQUIRED=1` setzen, dann | `PYTHONPATH=. PY -m pytest -p no:cacheprovider experiments/mandala_memory/tests` | ≈ 10 s |
| Smoke-Lauf | `PYTHONPATH=. PY -m experiments.mandala_memory.cli run --mode smoke` | ≈ 4 s → `D:/mandala/mandala-memory-results/smoke/` |
| Forschungsrunde | `PYTHONPATH=. PY -m experiments.mandala_memory.cli run --mode research` | ≈ 6 s |
| Auswertung | `PYTHONPATH=. PY -m experiments.mandala_memory.evaluate <research.json> --out <evaluation.json>` | |
| Beschreibende Tabelle | `PYTHONPATH=. PY -m experiments.mandala_memory.summarize <result.json> --markdown` | |
| Membran-Pilot | `PYTHONPATH=. PY -m experiments.mandala_memory.cli pilot-membrane` | |
| Ansicht | `PYTHONPATH=. PY -m experiments.mandala_memory.serve --port 8765`, dann `http://127.0.0.1:8765/` öffnen | |
| Regler-Labor (M8, explorativ) | derselbe Dienst, dann `http://127.0.0.1:8765/lab.html` öffnen | → `D:/mandala/mandala-memory-results/explore/lab-*.json` |
| M9: Vorhersagen einfrieren (einmalig, schon geschehen) | `PYTHONPATH=. PY -m experiments.mandala_memory.m9_freeze` | schreibt exklusiv `protocol/m9_frozen_predictions.json` |
| M9: Prüfung | `PYTHONPATH=. PY -m experiments.mandala_memory.m9_evaluate` | ≈ 5 s → `D:/mandala/mandala-memory-results/m9/` |
| M9: Handkontrollen | `PY experiments/mandala_memory/controls/m9_hand_controls.py` | exakte Brüche |
| Mutationsprüfung | `PY experiments/mandala_memory/tools/mutation_check.py` | |
| Reviewpaket | `PY experiments/mandala_memory/tools/make_review_package.py` | → `D:/mandala/mandala-memory-results/review/` |

### PowerShell

Die Befehle oben sind für Bash geschrieben. In PowerShell im Worktree-Wurzelverzeichnis zuerst einmalig je Sitzung:

```powershell
Set-Location D:\mandala\.worktrees\feldtheorie-mandala-memory
$env:PYTHONPATH = "."
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:OPENBLAS_NUM_THREADS = "2"
$env:TMP = "D:\mandala\.tmp\mandala-memory"; $env:TEMP = $env:TMP
$PY = "D:\mandala\.venvs\mandala-memory\Scripts\python.exe"
```

Danach:

```powershell
& $PY -m pytest -p no:cacheprovider experiments/mandala_memory/tests
& $PY -m experiments.mandala_memory.cli run --mode smoke
& $PY -m experiments.mandala_memory.cli run --mode research
& $PY -m experiments.mandala_memory.evaluate D:\mandala\mandala-memory-results\research\<datei>.json --out D:\mandala\mandala-memory-results\research\<datei>.evaluation.json
& $PY -m experiments.mandala_memory.serve --port 8765      # dann http://127.0.0.1:8765/ bzw. /lab.html öffnen
& $PY -m experiments.mandala_memory.m9_evaluate
& $PY experiments/mandala_memory/tools/mutation_check.py
& $PY experiments/mandala_memory/tools/make_review_package.py
```

**Ergebnisdateien:** Jeder Lauf schreibt eine **neue** Datei `<protokoll-id>--<ausführungs-id>.json`. Vorhandene Dateien werden nie überschrieben (Review R1). Die Originaldatei der ersten Forschungsrunde (`research-e19650a0a0.json`, aus der Zeit vor dieser Korrektur) bleibt unverändert.

**Inferenz** ist nur freigegeben, wenn der vorab festgelegte Forschungsumfang vollständig erreicht ist (Review R2): alle 20 Protokoll-Seeds, Status „complete“, keine Fehlschläge, Konfiguration identisch mit dem eingefrorenen Protokoll. Sonst bleibt das Ergebnis beschreibend; die Gründe stehen in `inference_release.reasons`.

## Teststufen und Pflicht-Labortestlauf (Review R8)

Jeder Test erklärt in [`tests/conftest.py`](tests/conftest.py), was er braucht. Fehlt etwas, werden **nur die betroffenen** Tests übersprungen, jeweils mit eigenem Grund. Die Abhängigkeiten stehen in [`requirements-lab.txt`](requirements-lab.txt).

| Stufe | braucht | Tests | geprüft |
|---|---|---|---|
| portabel | numpy, pytest, PyYAML | 101 (Mathematik, Vorhersage, Freeze/Hash, Trilayer, Ablesungs- und Dauerdefinitionen, Runner-Regeln) | Linux (WSL, Python 3.12) und Windows |
| `scf` | + scoped-correspondence 0.42 | 109 (Netzkonstruktion, Kern gegen Vorhersage, SCF-Paritäten) | Linux und Windows |
| `lab_integration` | Windows-Laborablage auf `D:/mandala` (Originalergebnisse, Ansicht im unified-mandala-Worktree, Benchmarkdateien) | 13 | nur Windows-Labor |
| `git_history` | Feldtheorie-Historie mit Plan-Commit `0e46ec8` | 1 | Windows-Labor (unter WSL ist die Worktree-Historie nicht lesbar) |

- **Pflicht-Labortestlauf:** `MANDALA_LAB_REQUIRED=1` setzen, dann `pytest experiments/mandala_memory/tests`. Fehlt eine Voraussetzung, bricht der Lauf mit Fehler ab. Jeder übersprungene Test lässt den Lauf scheitern. Erwartet: **224 bestanden, 0 übersprungen.**
- **Ohne die Variable** gilt ein Lauf mit übersprungenen Stufen **nicht** als Labortestlauf. Die Sitzung meldet dann ausdrücklich: „this is NOT a lab test run“.
- **CI-Abdeckung (ehrlich):** Die bestehende Feldtheorie-CI installiert weder SCF noch PyYAML; ein Workflow für die Laborstufen wurde **nicht** angelegt. Auf GitHub laufen deshalb nach jetzigem Stand nur die portablen Tests ohne Trilayer-Test. Für `scf`, `lab_integration` und `git_history` ist das **fehlende CI-Abdeckung**, keine bestandene Labor-CI. Verbindlich bleibt der Pflicht-Labortestlauf.
- **Schutz:** Unter POSIX schlägt die Sitzung fehl, wenn ein Test versehentlich einen relativen Ordner `D:` oder `C:` anlegt. Die C:-Sperre der Schreibwege prüft die Schreibweise plattformunabhängig.

## Ergebnis der ersten Runde

Synthetisch, nur dieses Protokoll:

- **Hauptkontrast** (vorab festgelegt: d = 8, neu trainierter Decoder, angepasst minus eingefroren, 20 Seeds): mittlere gepaarte Differenz −0,001, 95-%-Bootstrap über Seeds [−0,0025; +0,0005]. Die episodische Hebb-Anpassung bringt hier **keinen nachweisbaren Gewinn**.
- **Beschreibend:**
  - Die Reizspur ist bis d = 2 vollständig lesbar und zerfällt bis d = 8 auf etwa 0,67.
  - Kopplung hilft gegenüber A = 0 (d = 4: 0,93 gegen 0,71).
  - Das modulare Netz (c = 1/4) hält die Spur länger als das gleich budgetierte uniforme (0,93 gegen 0,65).
  - Reset, Summenbeobachtung und eingefrorener Decoder nach der Permutation verhalten sich wie die Kontrollen K3, K4 und K6 erwarten lassen.
- **Membran-Pilot** (separate Aufgabe, kein Vergleich): Die adaptive Membran trägt die Reizamplitude in ihrem **adaptiven Parameterzustand** (θ und β) weiter, lesbar bis etwa d = 8–16. Die eingefrorene Membran zeigt kein Gedächtnis. Welcher der beiden Parameter wie viel beiträgt, ist ohne eigene Parameter-Ablation nicht belegt.

## Ergebnis der zweiten Runde (M9): Warum das Mandala erinnert

Die Herleitung steht in [docs/M9_HERLEITUNG.md](docs/M9_HERLEITUNG.md) (eingefroren; zwei Erklärungen berichtigt in [docs/M9_ERRATUM_1.md](docs/M9_ERRATUM_1.md)), die Prüfung im Abschnitt M9c der [ROADMAP](ROADMAP.md). Alles ist synthetisch und gilt nur für die Familie F: gleich große Module, Budgetmatrix, ein Puls, keine Eingriffe.

- **Wo die Erinnerung steckt:** im **Modul-Unterschieds-Modus** mit μ_D = 1 − ℓ + ℓγ(1 − cN/(N−n)). Unterschiede innerhalb eines Moduls verschwinden mit μ_I, meist viel schneller.
- **q ist keine Erinnerungsrate:** Der Kontraktionsfaktor q gehört zum Gleichtaktmodus. Der Reizunterschied steht darauf senkrecht; das ist bewiesen, auch nichtlinear.
- **Vorhersagen eingefroren und bestätigt:** 24 nie zuvor angesehene Parameterkombinationen wurden **vor** jeder Rechnung mit dem Kern eingefroren.
  - Alle 24 Kern-Kurven liegen über 65 Pausen im beweisbaren Band.
  - 23/23 Punktvorhersagen der Gedächtnisdauer (letzte Pause mit ≥ 75 % idealer Trefferquote) treffen exakt.
  - 28/28 Decoder-Prüfungen bestehen.
- **Die naive q-Regel versagt:** Sie sagt in allen 14 Fällen mit Erinnerung eine zu lange Dauer voraus, meist ein Vielfaches.
- **Abschottung (kleines c) hilft nur unter drei Bedingungen:** Die Reize kommen in **verschiedenen** Modulen an, das Ablesen sieht den Modul-Unterschied, und Austausch zwischen Modulen ist nicht gefragt. Wer Information zwischen Modulen austauschen will (großes c), verkürzt genau diese Erinnerung.

## Bekannte Grenzen

- **Rein synthetisch.** Seeds sind Wiederholungen, keine biologischen Präparate. Die Unsicherheit gilt nur für diese Seed- und Rauschverteilung.
- **Variabilität:** Die Dynamik ist deterministisch, Prozessrauschen ist null; Schwankungen kommen nur aus Messrauschen σ = 0,02 und der Reihenfolge der Anpassung.
- **Enger Geltungsbereich:** Das Ergebnis gilt für η = 0,3, 40 Episoden zu je 5 Schritten und den Nearest-Mean-Decoder ohne Standardisierung. Andere Lernregeln, längeres Training oder Online-Lernen im Test sind nicht untersucht.
- **Keine ressourcengleichen Vergleiche:** Leak-Modell (weniger Budget), Summenbeobachtung (andere Dimension) und lineares Modell (andere Amplitudendynamik) dienen nur als Kontrollen.
- **Keine unabhängigen Tests:** Die Verzögerungen eines Seeds teilen ein angepasstes Netz.
- **Membran-Pilot:** Die Anfangswerte θ0 = 0,5 und β0 = 6 sind Annahmen dieses Pilots.
- **Ansicht:** Klang fehlt noch. Der Screenshot-Test ersetzt keinen Bedientest durch einen Menschen.
- **M9:** Die Aussagen gelten für Familie F. Für Ablation, Eingriffe nach dem Reiz und angepasste Netze gibt es nur die q-Schranke aus M8, keine Vorhersage.
- **Regler-Labor (M8):** rein explorativ. Seine Kurven sind ideale Trefferquoten (Bayes) und keine Decoder-Messungen. Was dort auffällt, ist eine Beobachtung und erst nach einer vorab festgelegten Prüfung (M9) eine Aussage.
- **Abweichungen vom SCF-Standard:** Statt SCFs immer standardisierendem `NearestMeanDecoder` gibt es einen eigenen Decoder. Statt `simulate_trial` gibt es einen eigenen Episodenoperator, der bitgleich zu `simulate_trial` ist.
- **Tests:** Die Feldtheorie-weite Test-Suite wurde nicht ausgeführt; berührt wurden nur neue Ordner. Die `pytest.ini` von Feldtheorie erzeugt eine harmlose Warnung (`asyncio_default_fixture_loop_scope`).
- **Kein Push**, keine Veröffentlichung: Alles liegt lokal in Git-Worktrees.
