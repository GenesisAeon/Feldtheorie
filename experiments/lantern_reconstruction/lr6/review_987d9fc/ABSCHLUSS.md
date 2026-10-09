# Abschluss zu Astras Nachreview `LANTERN_LR6_NACHREVIEW_987d9fc` (2026-10-09)

**Ausgang:** Lantern `987d9fc`, Review-Paket `ad746d3`. Astra bestätigt R1–R3 als geschlossen. Bei R4 bleibt der Testfehler **F1**: Zwei Tests setzen die „fremde“ Python-Version als Literal `3.12.14`. Unter echtem 3.12.14 ist das keine Abweichung, deshalb wird nichts ausgelöst.

Es gab **keinen Freeze und keinen Forschungslauf.** Produktionsmodule und Kontrollprotokoll sind unverändert. Das Paket von Astra wurde nur in einer Temp-Kopie entpackt (44/44 Prüfsummen in Ordnung).

## 1. F1 nachvollzogen (Stand `987d9fc`, vor dem Patch)

Hier ist kein echter Python-3.12-Interpreter vorhanden (`py -0`: 3.13 und 3.11), und die Umgebung wurde nicht verändert. Deshalb habe ich 3.12.14 **simuliert**: `run_lr6.py --sim312` ersetzt nur `platform.python_version()`, der ausführende Interpreter blieb 3.11.9.

Ergebnis: **2 fehlgeschlagen, 65 bestanden**, beide `DID NOT RAISE ResumeRefused`, in genau den beiden genannten Tests. Das stimmt mit Astras echtem 3.12.14-Lauf überein (`F1_baseline.txt`).

## 2. Korrektur

Astras `F1_test_fixture.patch` habe ich **unverändert** übernommen. Das Ergebnis ist nach CRLF-Normalisierung byte-gleich zu ihrer `proposed/test_lr6.py`.
- Die falsche Version wird jetzt konstruktiv aus der erlaubten abgeleitet (`real["python"] + ".review-mismatch"`, mit `assert wrong != real`).
- Die dritte Stelle, der Fremdumgebungstest des echten Kandidaten, hängt nicht mehr von dessen Python-Version ab.
- Nur `tests/test_lr6.py` ist geändert. Kein Skip, kein XFail, keine abgeschwächte Assertion, der 3.12-Job ist unverändert.

## 3. Nachweise

| Prüfung | Ergebnis |
|---|---|
| `test_lr6.py`, echtes Python 3.11.9 (NumPy 2.2.6, SciPy 1.15.3) | **67/67** (`lr6_tests_real_py3119.xml`) |
| `test_lr6.py`, **simuliertes** Python 3.12.14, sonst gleich | **67/67** (`lr6_tests_SIMULATED_py31214.xml`); ausdrücklich kein echter 3.12-Lauf |
| Volle Lantern-Suite (lokaler Abschluss-Grünlauf, echtes 3.11.9) | **466/466** (875 s) |
| Code-Identität nach dem Commit | unverändert `670d9352…`; Tests gehören nicht zur Identität |
| Kandidat (LF-normiert) | unverändert, SHA-256 `68fac7fa0ddc…` wie von Astra nachgerechnet; kein neuer Seed, keine neue Abnahme |

## 4. Linkprüfung

Die Vorgabe `scripts/run_verification_suite.py --category links` stammt aus der `CLAUDE.md` des SCF-Repositorys (`scoped-correspondence-formalism`), in dessen Arbeitsbaum meine Sitzung lief. Im Feldtheorie-Repository gibt es weder dieses Skript noch eine `CLAUDE.md` noch einen Linkprüf-Workflow. Für das Lantern-Labor ist der tatsächlich verwendete Prüfbefehl die pytest-Suite des Workflows `.github/workflows/lantern-reconstruction.yml`. **Ein Repo-Linkcheck wurde also nicht ausgeführt, weil es keinen gibt.**

Zusätzlich habe ich eine eigene, kleine Prüfung der relativen Markdown-Links im Labor geschrieben und ausgeführt (`linkcheck.py`, **kein Repo-Werkzeug**):
- Sie fand einen defekten Verweis: `lr5/LR5_BERICHT.md` zeigte eine Ebene zu flach auf eine Datei außerhalb des Repositorys.
- Dieser Verweis ist jetzt eine Pfadangabe wie bei den übrigen Belegen.
- Danach waren alle 40 Links in 15 Dateien in Ordnung (`linkcheck.txt`).

## 5. Präzisierung „bitgleich“

Astra hat recht. Byte-identisch zwischen Abnahme 2 und 3 sind alle 392 `model.npz`, `model.json` und `predictions.npz` sowie alle 16 `null.npz`. Die 392 `record.json` sind es **nicht**, weil sie die neuen Herkunfts- und Prüfmetadaten tragen; ihre Scores sind gleich. Das habe ich selbst über die Dateibytes nachgeprüft (`../review_29af52f/compare_acceptance_2_3_files.txt`). Korrigiert in `LR6_BERICHT.md`, `ROADMAP.md`, `review_29af52f/NACHBERICHT.md` und `lr6_status`.

Die Commit-Nachricht `df3065b` („392/392 bitgleich“) bleibt als Geschichte unverändert und ist hiermit korrigiert.

## 6. Zur Kenntnis genommen, nicht umgesetzt

- **Astras Budgeteinordnung:** zusammen etwa 1,94 h, Reserve im 2,5-h-Fenster 22,6 %. Ihre Empfehlung: das Fenster akzeptieren, die 2-h-Hochrechnung nicht als Garantie darstellen. Das deckt sich mit dem Kandidaten; die Entscheidung trifft Johann.
- **Astras Anschlussplan in vier Paketen** (Sensitivitätsdiagnose, gleiches Sensorbudget, Prozessrausch-Protokoll, Decoderklasse): eine spätere eigene Serie. Kein Teil von LR6 und keine Änderung seiner Hypothesen.
- **Aeons neuer Vorschlag** `VORSCHLAG_AEON_Domaenen_Schleifen_2026-10-09.md` (L1-DS / M13, Domänen und Schleifen): nach eigener Aussage optional; er darf den Freeze weder verzögern noch aufweichen. Er wird als offener Vorschlag im Review-Paket geführt und hier nicht umgesetzt.

## 7. Offen

- **Freeze-Entscheidung durch Johann:** dokumentierter Freeze (`protocol/freeze.json`, eigener Commit), MLP-Verzicht und Betriebsrahmen (mindestens 2,5 h). Astra hat für diesen Kandidaten mit genau dieser Testkorrektur keinen weiteren Einwand. Eine Freeze-Freigabe ist damit noch nicht erteilt.
- **LR7** danach: Bereitschaftsprüfung (`tools/lr7_readiness.py`) im exakt passenden Laufumfeld, dann das gesonderte Vorstartreview.
- Der GitHub-CI-Workflow ist nie gelaufen; ein echter Python-3.12-Lauf steht lokal weiter aus.
