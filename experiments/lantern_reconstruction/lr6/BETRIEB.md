# Lantern-Labor: Betriebshandbuch (LR6)

Dieses Handbuch beschreibt, wie Läufe gestartet, überwacht, nach Abbrüchen fortgesetzt und freigegeben werden. Es gehört zum Freeze-Kandidaten. **Ein Forschungslauf ist erst nach einem dokumentierten Freeze erlaubt.**

## Lauftypen

| Typ | Einstieg | Studie | Parameter |
|---|---|---|---|
| `smoke` / `development` | `runs.create_run(...)` + `runs.execute(...)` | Entwicklungsstudie 2026100803 | frei wählbar (Kontexte, Größen) |
| `research` | **nur** `runs.create_research_run(...)` + `runs.execute(...)` | Masterseed aus dem Kandidaten | **ausschließlich** aus `lr6/freeze_candidate.json` |

Ein Forschungslauf verlangt `protocol/freeze.json`:
- Status `frozen` und die Namen der Freigebenden;
- den SHA-256 der LF-normierten Kandidatendatei;
- dieselbe Code-Identität wie der aktuelle Code (die Freeze-Datei selbst ausgenommen).

Fehlt etwas davon oder weicht es ab, wird der Lauf verweigert, auch beim Fortsetzen.

## Freeze (Ablauf, nicht durch den Code)

1. Den Kandidaten unabhängig prüfen; der Prüfbericht liegt im Review-Repo.
2. Johann und Astra geben frei. Dabei wird `protocol/freeze.json` geschrieben, mit Schema `lantern-freeze-v1`, Status `frozen`, `approved_by`, `candidate_sha256` und `code_identity`. Das ist ein eigener, dokumentierter Commit.
3. Ab dann keine Änderung an Produktionsmodulen oder Protokolldateien. Jede Änderung ändert die Code-Identität und sperrt den Forschungslauf. Eine neue Studienversion braucht einen neuen Kandidaten.

## Einen Lauf durchführen

1. Netzteil anschließen. Das Werkzeug verhindert den Ruhezustand nur für den eigenen Prozess (`SetThreadExecutionState`), ohne dauerhafte Systemänderung.
2. Starten: Entwicklungsabnahme über `tools/lr6_development_acceptance.py`, Forschung (erst nach dem Freeze) über ein entsprechendes LR7-Werkzeug.
3. **Überwachen:** `events.jsonl` im Laufordner, nur anhängend. `cell_completed` zeigt den Fortschritt, `clock_gap` eine vermutete Schlafunterbrechung. Den Status liefert `runs.status(run_dir)`.
4. **Freigabebericht:** `release.write_release_report(run_dir)` erzeugt `release_report.json` einmalig mit drei getrennten Feldern.

## Nach einem Abbruch

| Lage | Vorgehen |
|---|---|
| Status `interrupted` oder `incomplete` | `runs.execute(run_dir)` setzt denselben Lauf fort. Code, Protokoll, Konfiguration, Snapshot, Software und Raster müssen unverändert sein, sonst `ResumeRefused`. |
| Status `running`, aber der Prozess ist weg (Absturz, Stromausfall, Abschuss) | `runs.recover(run_dir)`. Prüft nur lesend Host, PID und Sperrbesitz. Ist der Prozess sicher tot, repariert es unter der Verwaltungssperre das Log-Ende nur anhängend, entfernt die tote Studiensperre (protokolliert) und setzt `interrupted`. Danach `runs.execute`. |
| `recover` verweigert mit „may still be active“ | Der Prozess lebt möglicherweise (auch eine wiederverwendete PID gilt als lebendig). **Nicht** eingreifen, sondern prüfen und den Prozess gegebenenfalls ordentlich beenden. |
| `recover` verweigert wegen eines anderen Hosts | Recovery nur auf dem Rechner, der den Lauf hielt. |
| Status `failed_integrity` oder `numerically_invalid` | Endgültig. Der Lauf wird nicht fortgesetzt, nichts wird überschrieben. Ursache dokumentieren; ein neuer Lauf bekommt eine neue Lauf-ID. |
| `TruncatedLogError` beim Lesen | Das Log-Ende ist unvollständig. Nur `runs.recover` repariert es, und zwar nur bei totem Besitzer. |

## Verwaiste Verwaltungssperre `<studiensperre>.admin` (immer manuell)

Die Verwaltungssperre wird **nie automatisch entfernt**. Sie bleibt liegen, wenn ein Prozess mitten in einer Sperrverwaltung verloren geht, also in den Millisekunden um das Anlegen einer Studiensperre oder während einer Recovery. Neue Starts und Recoveries melden dann `LockError: administration of … in progress` mit dem Inhalt der Sperre: Zweck, PID, Host, Zeit, Token.

Vorgehen:
1. Den Inhalt der `.admin`-Datei lesen und notieren (Zweck, PID, Host).
2. Auf **diesem** Host prüfen, ob die PID noch läuft (`Get-Process -Id <pid>`) und ob sie zu einem Lantern-Lauf gehört.
3. Nur wenn kein solcher Prozess läuft: die `.admin`-Datei von Hand löschen und den Vorgang mit Inhalt und Zeitpunkt in einer Notiz neben dem Lauf festhalten.
4. Danach `runs.recover` bzw. `runs.execute` wie oben.

Eine **Studiensperre** (`study-<id>-<phase>.lock`) wird ebenfalls nicht von Hand gelöscht, solange ein Lauf `running` ist; dafür ist `runs.recover` da. Für eine Studiensperre ohne laufenden Lauf gilt dasselbe Vorgehen wie oben.

## Review-Paket

Zu jeder Übergabe an ein Review wird das private Paket aktualisiert: `D:/mandala/review-repo/REVIEW_ROUTINE.md` und `publish_review_repo.py --publish`. Öffentliche Repositories werden nicht gepusht.
