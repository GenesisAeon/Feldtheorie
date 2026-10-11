# LR7 – Unterlagen zum Vorstartreview

**Stand:** 2026-10-09. **Es läuft noch kein Forschungslauf.** Gestartet wird erst nach diesem gesonderten Vorstartreview.

## 1. Freeze

Johann hat am 2026-10-09 entschieden: den geprüften Kandidaten **unverändert** einfrieren; der MLP-Verzicht gilt verbindlich für diese Studie; mindestens 2,5 h Betriebsfenster, die Laufzeitschätzung ist keine Garantie.

- **Commit `5ccad90`** enthält ausschließlich `protocol/freeze.json`:
  - Schema `lantern-freeze-v1`, Status `frozen`, `approved_by` Johann;
  - Kandidat `lr6/freeze_candidate.json`, LF-SHA-256 `68fac7fa0ddc43a2133af417c4fb8ccf64717ab52fe31ca02af7aa259b79b690`, unverändert wie in Astras Nachreview `987d9fc`;
  - Code-Identität `670d9352e7fb6f7291318cbd36f0b2df2a17cdbd1cd84acf1e404cf16681ea2c` (Git `d1cb936`, sauber).
- **Studie:** Forschungsstudie **1431972670**, 20 Kontexte, 1960 Zellen.
- **Software:** Python 3.11.9, NumPy 2.2.6, SciPy 1.15.3.
- **Verbindliche Festlegungen** (im Freeze-Datensatz):
  - MLP-Verzicht; Aussagen nur zur untersuchten Ridge-Auslesbarkeit.
  - Betriebsfenster mindestens 9000 s.
  - Die Laufzeit ist nur eine Hochrechnung.
  - Kontexte, Seed, Statistik und Kontrollregeln sind fest. Kein Kontext wird nach Sichtung gestrichen.
- **Bewusst ohne YAML-Zwilling:** `code_identity()` nimmt nur `protocol/freeze.json` aus; eine `freeze.yaml` würde die eingefrorene Identität ändern.
- Ab jetzt gibt es keine Änderung an Produktionsmodulen oder Protokolldateien. Die Werkzeuge in `tools/` und die Berichte gehören nicht zur Identität.

## 2. Bereitschaftsprüfung in der eingefrorenen Umgebung

`tools/lr7_readiness.py` (Ausgang 0) und die erweiterte, nur lesende Prüfung `readiness_frozen_environment.py` liefern:

| Prüfung | Ergebnis |
|---|---|
| Freeze vorhanden und gültig | ja; `research_start_allowed: true`, keine Ablehnung |
| Code = eingefrorene Identität | ja |
| Software exakt eingefroren | ja (3.11.9 / 2.2.6 / 1.15.3), keine Abweichung |
| Registry-Snapshot | voll verifiziert **einschließlich** der Prüfung gegen die ursprüngliche Git-Historie; gleich dem Kandidaten |
| Freier Platz D: | etwa 238 GB, das 1132-Fache der hochgerechneten 210 MB |
| RAM | 25,7 GB gesamt, 8,8 GB frei (Entwurfsbudget 1 GB) |
| Stromversorgung | Netzbetrieb |
| Verwaiste Sperren | keine |
| Vorhandene Forschungsläufe | keine (nur die drei Entwicklungsabnahmen) |
| Volle Testsuite mit vorhandenem Freeze | **466/466** (871 s); kein Forschungslauf und keine Sperre dabei entstanden |

Belege: `readiness_frozen_environment.json` und `dry_run.txt`.

## 3. Start: `tools/lr7_research_run.py`

Dies ist der einzige Startweg. Es ist ein neues Werkzeug, nicht Teil der Code-Identität, und **zur Prüfung in diesem Review**.

- **Ohne Argumente: Probelauf.** Er zeigt Bereitschaft und Plan (Studie, 20 Kontexte, 1960 Zellen, Hochrechnung 6820 s Ausführung plus 151 s Freigabe, Fenster 9000 s) und legt nichts an. Geprüft: Ausgang 0, kein Laufordner.
- **Start:** `--start --confirm-study 1431972670`.
  - Ohne oder mit falscher Studien-ID wird verweigert, bevor etwas angelegt wird. Geprüft mit `1` und ohne ID; kein Laufordner entstanden.
  - Danach `runs.create_research_run` (ohne Parameter, alles aus dem Kandidaten), Lauf-ID `lr7-research-<UTC>`, dann `runs.execute` und `release.write_release_report`.
  - `execute` prüft Freeze, Code und Software vor jedem Start erneut.
- **Fortsetzen / Abschließen:** `--resume <Laufordner>` (optional `--confirm-study 1431972670`), nach `runs.recover()` gemäß `lr6/BETRIEB.md`.
  - **Zielprüfung vor jeder Wirkung** (Vorstartreview LR7-F2, Fix in diesem Stand). Vor `keep_awake`, vor neuen Ereignissen und vor Ausführung oder Bericht wird geprüft:
    - gültiger Freeze;
    - intaktes Manifest;
    - Lauftyp `research`;
    - Studie und gesamtes Raster gleich dem Freeze;
    - unveränderte Code-, Snapshot- und Softwarebindung (`check_resumable`);
    - eine angegebene `--confirm-study` muss stimmen. Ein falscher Wert wird nie ignoriert.
  - Entwicklungs- und Smoke-Läufe werden abgewiesen.
  - **Zustand bestimmt die Aktion** (LR7-F1):
    - neu, `interrupted` oder `incomplete`: rechnen, dann Bericht;
    - `running`: abweisen, auf `runs.recover()` verweisen; das Werkzeug entfernt keine Sperren;
    - `complete` ohne Bericht: **nur** den Bericht erzeugen;
    - `complete` mit Bericht: lesend nachrechnen und vergleichen, nie überschreiben;
    - `failed_integrity` oder `numerically_invalid`: abweisen, kein automatischer Ersatzlauf.
  - Ein fehlender Bericht verlangt weder einen neuen Forschungsseed noch einen neuen Lauf.
- **Zweiter Erststart** (Vorstartreview Abschnitt 6): `--start` wird abgewiesen, wenn unter dem Laufordner schon ein Forschungsmanifest dieser Studie und dieses Rasters liegt, oder ein unlesbares Manifest. Die Meldung nennt Lauf und Zustand.
  - Die Prüfung ist **nicht atomar**. Gleichzeitige Rechnung derselben Studie verhindert weiterhin die bestehende Studiensperre.
  - Ein Ersatz nach endgültigem technischem Fehler braucht eine dokumentierte Entscheidung.
- Der Ruhezustand wird nur für den eigenen Prozess verhindert. Nichts wird gelöscht oder überschrieben.
- Die Ausgabe auf der Konsole ist rein technisch. Die wissenschaftliche Auswertung steht nur in `release_report.json`; Hypothesen werden nur bei einem interpretierbaren Forschungslauf ausgewertet.

## 4. Ablauf am Starttag (Vorschlag zur Prüfung)

1. Netzteil anschließen; ein Zeitfenster von mindestens 2,5 h freihalten.
2. `tools/lr7_readiness.py` muss mit 0 enden; danach den Probelauf.
3. Start mit `--start --confirm-study 1431972670`. Überwachung über `events.jsonl` (`cell_completed`, `clock_gap`).
4. Bei einem Abbruch: `runs.recover()`, danach `--resume`. Verwaiste Verwaltungssperren werden von Hand behandelt (`lr6/BETRIEB.md`).
5. Freigabebericht: drei getrennte Felder. Die Hypothesen werden nur ausgewertet, wenn der Lauf interpretierbar ist.
6. Ergebnisbericht und Review-Paket. Keine Aussage über die Ridge-Auslesbarkeit, die dokumentierte Dynamik und die strukturelle Referenz hinaus.

## 5. Offene Punkte für das Review

- **Das Startwerkzeug selbst:** ~~kein eigener Test~~ → behoben nach dem Vorstartreview `LANTERN_LR7_VORSTARTREVIEW_2822141`.
  - 17 Regressionstests (`test_lr7_*`) stehen in der **bestehenden** `tests/test_lr6.py`. Der 13-Dateien-Vertrag und der CI-Workflow bleiben unverändert.
  - Am Stand `2822141` schlagen 11 davon fehl. Die 6 übrigen prüfen Verhalten, das schon korrekt war.
  - Nachbericht: `lr7/review_2822141/NACHBERICHT.md`.
- **Laufzeit:** Die Hochrechnung aus vier Kontexten ist linear und keine Obergrenze. Ein Problem wird nach Protokoll fortgesetzt oder offen berichtet.
- **Nicht geprüft:** Der GitHub-CI-Workflow ist nie gelaufen. Ein echter Python-3.12-Lauf fehlt; er ist für den Forschungslauf irrelevant, weil 3.11.9 eingefroren ist.
