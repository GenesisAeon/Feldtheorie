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

## Offen

- **Entscheidung vor dem Freeze:** die LR5-A1-Freigaberegel. Der Vorschlag lautet, dass beide Alarme sperren.
- **LR6:** Entwicklungsabnahme und Freeze-Kandidat. Dazu gehören Masterseeds und Kontextliste, das optionale MLP (oder dessen ausdrücklicher Verzicht), vollständig entschiedene Protokollwerte und ein voller Entwicklungslauf mit allen Kontrollkurven auf der Entwicklungsstudie.
- **CI auf GitHub** erst, wenn der Branch gepusht werden darf.
- Astras Prüfung von LR5.
