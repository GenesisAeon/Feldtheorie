# Mandala-Gedächtnislabor: Roadmap (M0–M9)

**Erster Versuch:** „Reiz → Pause → Erinnerung“.

**Auftrag:**
- [`CLAUDE_START.md`](../../../../ArbeitFeldtheorie_mandala/Mandala_Gedaechtnis_Uebergabe_2026-10-03/CLAUDE_START.md)
- [`IMPLEMENTIERUNGSPLAN.md`](../../../../ArbeitFeldtheorie_mandala/Mandala_Gedaechtnis_Uebergabe_2026-10-03/IMPLEMENTIERUNGSPLAN.md)

Beide liegen im Übergabeordner unter `D:\mandala\ArbeitFeldtheorie_mandala\Mandala_Gedaechtnis_Uebergabe_2026-10-03`. Sie sind eingefroren unter [`protocol/`](protocol/), die Prüfsummen stehen in [`M0_MANIFEST.json`](M0_MANIFEST.json).

**Arbeitsbedingungen laut Auftrag:**
- alles auf D: (Arbeitskopie, Umgebung, Caches, Temp-Dateien, Ergebnisse);
- CPU zuerst;
- kein Push, keine Veröffentlichung;
- bestehende lokale Dateien bleiben erhalten;
- kleine, geprüfte Pakete;
- keine Gewinnerbehauptung als Abnahmekriterium.

## Pakete

| Paket | Inhalt | Status |
|---|---|---|
| M0 | Stände, APIs, Laufzeit, Speicherorte; Protokoll eingefroren; Kontrollen unabhängig | ✅ erledigt |
| M1 | Episodenoperator, linearer/Null-Referenzkern; K1–K9, SCF-Parität, Reset/Fortsetzung | ✅ erledigt |
| M2 | Splits, Decoder, Rauschströme; Trennung, gepaarte Tests, Determinismus | ✅ erledigt |
| M3 | Eingefrorenes/adaptives Netz, Ablationen; Gewichte nur im Training; Smoke + Ressourcen | ✅ erledigt |
| M4 | SCF-Auswertung, Forschungsrunde (nach Hochrechnung) | ✅ erledigt |
| M5 | Feldtheorie-Membranpilot (separat) | ✅ erledigt |
| M6 | Lokale Mandala-Ansicht (unified-mandala `experiments/memory_lab/`) | ✅ erledigt |
| M7 | Reproduzierbare Übergabe, Reviewpaket | ✅ erledigt |
| M8 | Regler-Labor: explorativ, protokolliert, getrennt vom Benchmark | ✅ erledigt |
| M9a | Herleitung der Moden und Fehlerschranke, unabhängige Kontrollen, geschlossenes Vorhersagemodul | ✅ erledigt |
| M9b | Zurückgehaltene Kombinationen ziehen, Vorhersagen einfrieren (Commit vor jeder Kernrechnung) | ✅ erledigt |
| M9c | Prüfung gegen Kern (deterministisch) und Decoder (statistisch), Bericht | ✅ erledigt |
| Integration | M0–M9 lokal in `main` beider Repos (Feldtheorie `061adba`, unified-mandala `1e310caa`) | ✅ erledigt |
| M10 | Erinnerung unter Ablenkung: [Plan, Fassung 2](docs/M10_PLAN_ABLENKUNG.md), [Protokoll](protocol/m10_protokoll.json) eingefroren (`m10-freeze`), Forschungslauf ausgewertet | ✅ erledigt: H-N bestätigt, H-F+ nicht bestätigt |

## M0: Bestand, Laufzeit und Kontrollen

### Ausgangsstände

| Projekt | Stand | Befund |
|---|---|---|
| Feldtheorie | `0e46ec88…` = Plan-Commit | Haupt-Checkout unverändert (25 unversionierte Dateien). Gearbeitet wird im **Git-Worktree** `D:/mandala/.worktrees/feldtheorie-mandala-memory`, Branch `mandala-memory`. |
| unified-mandala | `a7605284…` = Plan-Commit | `experiments/` existiert (ab_test, emergence_study, …); `memory_lab/` ist frei. Wird in M6 angefasst. |
| SCF | veröffentlichtes Paket `scoped-correspondence==0.42.0` | Für die genutzten Module identisch mit Git `873adb8`. Der lokale Haupt-Checkout steht noch auf `4a7ed38` mit unversionierten Übergaben und bleibt **unberührt**. |
| Übergabe | 6 Dateien | Alle Prüfsummen stimmen mit `manifest_sha256.json` überein. |

### Laufzeit

- **Umgebung:** isoliert unter `D:/mandala/.venvs/mandala-memory`, **ohne** System-Pakete.
- **Versionen:** Python 3.11.9, NumPy 2.2.6 (wie Feldtheoriess `.venv`), SciPy 1.15.3, pytest, `scoped-correspondence` 0.42.0.
- **Caches und Temp-Dateien:** `D:/mandala/.cache/mandala-memory`, `D:/mandala/.tmp/mandala-memory`.
- **Rechenlast:** BLAS-Threads werden auf 2 begrenzt.

### Befunde, die das Vorgehen bestimmen

1. **System-Python bindet altes SCF ein.** Die System-Python hat eine *editable*-Installation des **alten** lokalen SCF-Checkouts (`4a7ed38`, Metadaten 0.10.0a1). Jeder Import dort bekommt alten Code, deshalb gibt es die isolierte Umgebung.
2. **pip scheitert an SSL.** Die pip-Version der Store-Python scheitert an der SSL-Prüfung zu pypi.org. Installiert wurde mit `--use-feature=truststore` (Windows-Zertifikatsablage); global wurde nichts geändert.
3. **C: war voll.** Zum Start waren auf C: nur 605 MB frei. Eigene Wegwerf-Umgebungen aus der SCF-Release-Sitzung habe ich entfernt, jetzt sind es etwa 1,7 GB. Alle neuen Daten gehen auf D:.
4. **Episodenoperator nötig.** SCF `simulate_trial` setzt `x` auf 0 und hält `u` konstant. Der Plan hatte das vorhergesehen. Es wird nicht umgedeutet, sondern ein eigener Episodenoperator wird ergänzt (M1).
5. **Eigener Decoder nötig.** SCF `NearestMeanDecoder` standardisiert immer mit Trainingsstatistik. Das Protokoll verlangt `standardization: none` und Gleichstand → Klasse 0. Deshalb kommt in M2 ein eigener minimaler Nearest-Mean-Decoder; das ist eine dokumentierte Abweichung.
6. **Feldtheorie-Membran wie beschrieben.** `AdaptiveLogisticMembrane.propagate` aktualisiert θ/β je Schritt und liefert die Werte nach dem Update; `reset()` stellt die Basiswerte wieder her.
7. **Trilayer-Regel.** Die `AGENTS.md` von Feldtheorie verlangt YAML+JSON+MD je Artefakt. Das Protokoll liegt hier als JSON+MD vor; ein YAML-Zwilling folgt in M7.

### Bestätigte APIs

Geprüft wurde in der installierten Version 0.42.0 bzw. am Plan-Commit.

| API | Ort | Verwendung |
|---|---|---|
| `budget_adjacency(N, M, gamma, c)` | SCF `validation/modular_networks/adaptive_model.py:57` | Ausgangsgewichte A (Zeilensumme γ, Diagonale 0) |
| `edge_mask(N, mod, allow_inter)` | ebd. `:83` | feste Kantenmaske |
| `hebb_update(A, pairs, mask, eta, gamma)` | ebd. `:97` | lokale, zeitversetzte Hebb-Anpassung mit Renormierung auf γ. Prüft Maske, Aktivitäten ≥ 0 und γ ∈ (0,1). |
| `contraction_bound(ell, gamma)` | ebd. `:139` | q = 1 − ℓ + ℓγ = 0,9 |
| `simulate_trial(A, B, u, ell, steps)` | ebd. `:164` | **Paritätsreferenz** für den Episodenoperator (konstantes u, x0 = 0) |
| `input_matrix(N, inputs, amplitude)` | ebd. `:184` | B[0,0] = B[4,1] = 0,6; die Amplitude wird genau einmal angewendet |
| `balanced_accuracy`, `check_split`, `sign_flip_test` | SCF `validation/modular_networks/decoders.py:37, 134, 197` | Auswertung |
| `AdaptiveLogisticMembrane` (`propagate`, `reset`) | Feldtheorie `models/adaptive_logistic_membrane.py:49, 100, 226` | M5-Pilot |

### Kontrollen K1–K9

- Das gelieferte `kontrollen.py` ergibt frisch 9/9 und ist identisch mit `kontrollen_ergebnisse.json`. Die Ergebnisdatei wurde dabei **nicht** überschrieben.
- **Unabhängig nachgerechnet:** [`controls/independent_controls_m0.py`](controls/independent_controls_m0.py) ergibt 9/9 über andere Wege als das Original:
  - exakte Brüche;
  - `statistics.NormalDist` statt `erf`;
  - eigene Budgetmatrix;
  - Lipschitz-Argument für K8;
  - expliziter Zustandsautomat für K9.

  Zusätzlich prüft es, dass c = 1/4 von der uniformen Matrix abweicht. Ergebnisse: [`controls/independent_controls_m0_results.json`](controls/independent_controls_m0_results.json).

| ID | Bestätigt |
|---|---|
| K1 | x_(d+1) = ±2^(−d) für d ∈ {0,1,2,4,8}, exakt |
| K2 | Φ(2^(−d)/0,25): 0,99997 … 0,50623, streng fallend > 1/2 |
| K3 | Reset nach Puls ergibt beide Klassen exakt 0 → Bayes 1/2 |
| K4 | (1/8, 0) vs. (0, 1/8): gleiche Summe, verschiedene Vollbeobachtung |
| K5 | a und σ beide ×1000 → identische Accuracy |
| K6 | Tausch: eingefroren 0, neu angepasst 1, det = −1 |
| K7 | N = 12, γ = 4/5: M = 1 ≡ M = 3 mit c = 8/11 (exakt, Nebendiagonale 4/55) |
| K8 | q = 9/10, q¹⁰ = 3486784401/10¹⁰; Beispiel unter der Schranke (Verhältnis ≤ 1) |
| K9 | ganzer Lauf = gestückelt mit Zustandsübergabe ≠ gestückelt mit Reset |

### Abnahme M0

- [x] Versions- und Pfadmanifest
- [x] keine lokalen Dateien überschrieben (Worktree, eigene Umgebung, Übergabe nur gelesen)
- [x] unabhängige Kontrollwerte bestätigt
- [x] Protokoll eingefroren

## M1: Episodenoperator und Referenzkern

[`core.py`](core.py):
- **`EpisodeOperator`** mit `reset`, `step`, `run`, `snapshot`, `restore` und `observe`. Er verwendet denselben Schritt wie SCF `simulate_trial`, nimmt aber einen expliziten Anfangszustand und eine beliebige Eingangsfolge an.
- **Determinismus:** Der Operator zieht keine Zufallszahlen.
- **Snapshot:** Er kopiert x, k, A, B, ℓ und die Nichtlinearität. `restore` in ein anderes Netz wird abgewiesen.
- **`build_network`:** baut das Netz über SCFs öffentliche APIs. Die Gewichte entstehen **exakt aus Brüchen** und werden erst danach in Gleitkomma umgewandelt. Exakt gleiche Matrizen sind so auch bitgleiche Floats.
- **Weitere Funktionen:** `recall_state` mit Reset-Kontrolle und `LinearScalarKernel` für K1/K9.

**Zeitkonvention:** u_0 = e_s, danach d Nullschritte; abgelesen wird x_(d+1). Bei d = 0 wird direkt nach dem Puls gelesen.

[`tests/test_m1_core.py`](tests/test_m1_core.py): **32/32 bestanden.**

| Prüfung | Ergebnis |
|---|---|
| K1 | ±2^(−d) exakt mit Brüchen |
| K9 linear | exakt |
| K9 Netz | `snapshot`/`restore` ergibt bitgleiche Fortsetzung; ein Reset an der Nahtstelle weicht ab |
| SCF-Parität | bitgleich mit `simulate_trial` (konstantes u, x0 = 0, beide Klassen, 12 Schritte) |
| Ablesung | x_(d+1) für alle d ∈ {0,1,2,4,8,16,32}; Puls genau einmal (Identität: x1 = ℓ·0,6·e) |
| K3 | Reset nach dem Puls: beide Klassen exakt 0 |
| K7 | exakt mit Brüchen; Trajektorien von M = 1 und M = 3 (c = 8/11) bitgleich; c = 1/4 weicht ab |
| K8 | 200 Zufallspaare × 20 Schritte, Abstand in der Maximumsnorm ≤ q^k (Verhältnis ≤ 1) |
| Weitere | ungekoppeltes Leak-Modell klingt mit (1−ℓ)^d ab; Scope-Fehler werden abgewiesen; Episoden ändern A und B nie |

K2, K4, K5 und K6 betreffen Beobachtung und Decoder und werden in M2 geprüft.

**Tests ausführen** (im Worktree-Wurzelverzeichnis):
`PYTHONPATH=. D:/mandala/.venvs/mandala-memory/Scripts/python.exe -m pytest -p no:cacheprovider experiments/mandala_memory/tests`

## M2: Splits, Decoder und Rauschströme

[`data.py`](data.py):
- **Benannte Zufallsströme** über `SeedSequence((seed, Modus, crc32(Namen)…))`. Smoke, Forschung, Exploration und Test sind getrennte Modi, auch bei gleichem Seed. Der Ableitungsschlüssel wird mitgeführt.
- **`EpisodeSet`:** IDs der Form `mode:seed:role:d:class:index`, Labels und Beobachtungsrauschen. Das Rauschen ist eine Funktion der **Episode**, nicht der Netzbedingung, und damit für gepaarte Bedingungen identisch.
- **`observe_episodes`:** y = H·x_(d+1) + ε. Prozessrauschen ist 0; die Dynamik ist deterministisch.
- **`NearestMeanDecoder`:** ohne Standardisierung, Gleichstand → Klasse 0. `predict(Y)` hat keinen Label-Parameter. Bewusste Abweichung von SCF, siehe M0-Befund 5.
- **Auswertung:** `balanced_accuracy` (über SCF), Konfusionsmatrix sowie Summen- und Permutationsbeobachtung.
- **Disjunkte Splits:** geprüft über SCF `check_split`.

[`tests/test_m2_data.py`](tests/test_m2_data.py): **13/13 bestanden** (zusammen mit M1: 45/45).

| Prüfung | Ergebnis |
|---|---|
| Ströme | deterministisch; Modi, Rollen und Zwecke disjunkt |
| Episoden | reproduzierbar, ID-disjunkt; gleiche Sets werden abgewiesen; Klassen balanciert |
| Gepaartes Rauschen | beide Netzbedingungen bekommen bitgleich dasselbe ε |
| Decoder | Gleichstand → 0; keine Labels in `predict`; keine Standardisierung; Eingabefehler werden abgewiesen |
| K2 | Decoder liegt nahe Bayes Φ(a/σ) für d ∈ {0,1,2,4}. Fester Seed, n = 20 000, Toleranz 4 Standardfehler; keine exakte Zufallsgrenze. |
| K4 | Summenbeobachtung ist bei gleichem Rauschen für beide Klassen identisch; Vollbeobachtung trennt |
| K5 | Daten und Testpunkte ×1000 ergeben identische Vorhersagen |
| K6 | Permutation: eingefroren 0, neu angepasst 1, \|det\| = 1 |

**Testfehler unterwegs (nicht im Code):** In meinem eigenen Test hatte ich `(x+ε)−x == ε` exakt erwartet, was in Gleitkomma nicht gilt. Die Prüfung läuft jetzt mit 1e‑15 plus direktem Vergleich der Rausch-Arrays. Am Code war das kein Fehler.

## M3: Eingefrorenes und angepasstes Netz, Ablationen, Smoke-Lauf

### Code

- [`model.py`](model.py):
  - **Episodische Hebb-Anpassung:** 40 balancierte Episoden in zufälliger Reihenfolge (eigener Strom `adaptation`), je Puls + 4 Nullschritte.
  - Die zeitversetzten Paare einer Episode gehen in **einen** Aufruf von SCF `hebb_update` (η = 0,3, feste Maske, Renormierung auf γ).
  - Danach ist das Netz eingefroren; das Eingangsnetz bleibt unverändert.
  - Dies ist ein **neues Protokoll**, keine Wiederholung des alten ON-Benchmarks.
- [`runner.py`](runner.py):
  - Pro Seed: anpassen, dann für jedes d Decoder-Training und Test (in der Forschungsrunde zusätzlich Validierung).
  - Das Testrauschen ist über alle Bedingungen gepaart.
  - Es werden nur Rohwerte gespeichert, kein Gesamtscore.
  - Der Runner verweigert Ausgaben auf C:, bricht nach dem Smoke-Limit mit Status ab und protokolliert fehlgeschlagene Seeds.
  - Gemessen werden Laufzeit und Spitzen-RAM (Windows `PeakWorkingSetSize`).
- [`cli.py`](cli.py): setzt die BLAS-Threads auf 2 und TEMP auf D:.
- [`summarize.py`](summarize.py): rein beschreibende Tabelle.

**Startbefehl Smoke:** `PYTHONPATH=. D:/mandala/.venvs/mandala-memory/Scripts/python.exe -m experiments.mandala_memory.cli run --mode smoke`

Die Ausgabe landet in `D:/mandala/mandala-memory-results/smoke/`.

### Bedingungen

| Bedingung | Bedeutung |
|---|---|
| frozen | Netz vor der Anpassung |
| adapted | Netz nach der Anpassung, Decoder neu trainiert |
| adapted_with_frozen_decoder | Netz nach der Anpassung, Decoder auf dem Vorher-Netz eingefroren |
| uncoupled_leak | A = 0; **weniger** Kopplungsbudget, also kein budgetgleicher Modularitätstest |
| linear | Identität statt tanh |
| uniform_M1 ≡ renamed_M3_c8_11 | identisches Netz unter anderen Modulnamen |
| reset_control | x nach dem Puls auf 0 gesetzt |
| sum_observation_frozen | H = (1, …, 1), **andere Beobachtungsdimension**, also kein ressourcengleicher Vergleich |
| permutation_* | umgekehrte Sensorreihenfolge, Decoder eingefroren bzw. neu angepasst |

### Tests

[`tests/test_m3_model_runner.py`](tests/test_m3_model_runner.py): **9 neue, insgesamt 54/54.**

- Gewichte ändern sich nur im Training.
- Zeilenbudget γ und Maske bleiben erhalten; Episoden ändern A nicht.
- Die Anpassung ist je Seed deterministisch; die Reihenfolge ist balanciert.
- Uniform und umbenannt sind identisch.
- Der Runner liefert bei Wiederholung bitgleiche Ergebnisse.
- Die Sperre für C: greift.
- Ein Timeout führt zum Status „aborted“, die deklarierte Seed-Liste bleibt erhalten.
- Ein fehlgeschlagener Seed wird protokolliert.
- Spitzen-RAM wird gemessen.

**Bewusst nicht geprüft:** eine Effektrichtung.

### Smoke-Lauf

| Feld | Wert |
|---|---|
| Run-ID | `smoke-e19650a0a0` |
| Konfigurations-SHA-256 | beginnt mit `e19650a0a0` |
| Ergebnisdatei-SHA-256 | beginnt mit `1a78faaaa1eaabc6` |
| Status | complete, 3 Seeds, kein Ausfall |
| Laufzeit | **3,4 s** (Anpassung 0,11 s, Auswertung 0,45 s; der Rest ist Import und Start) |
| Spitzen-RAM | **93 MiB** |
| Ergebnisgröße | 83 KiB |
| Wiederholung | bitgleiche Rohwerte |

Alle Prüfungen sind je Seed wahr:
- eingefrorenes A unverändert;
- angepasstes A während der Tests unverändert;
- Maske eingehalten, Zeilensummen = γ.

### Smoke-Ergebnisse

Rein **beschreibend**: 3 Seeds, 40 Trainings- und 40 Testepisoden je Klasse und Verzögerung, keine Inferenz. Werte sind die mittlere Balanced Accuracy.

| d | frozen | adapted | adapted, Decoder eingefroren | Leak (A = 0) | linear | uniform ≡ umbenannt | Reset | Summe | Perm. eingefroren | Perm. neu |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 0,483 | 0,504 | 0,483 | 1,000 |
| 1 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 0,492 | 0,512 | 0,725 | 1,000 |
| 2 | 1,000 | 1,000 | 1,000 | 0,975 | 1,000 | 0,946 | 0,512 | 0,504 | 0,713 | 1,000 |
| 4 | 0,904 | 0,908 | 0,908 | 0,704 | 0,929 | 0,625 | 0,442 | 0,504 | 0,733 | 0,933 |
| 8 | 0,662 | 0,662 | 0,654 | 0,546 | 0,671 | 0,550 | 0,554 | 0,550 | 0,596 | 0,654 |
| 16 | 0,496 | 0,496 | 0,492 | 0,496 | 0,496 | 0,496 | 0,496 | 0,533 | 0,496 | 0,496 |
| 32 | 0,492 | 0,492 | 0,492 | 0,492 | 0,492 | 0,492 | 0,492 | 0,483 | 0,492 | 0,492 |

### Lesart (beschreibend, nicht inferenziell)

- **Zerfall der Spur:** Die Reizinformation ist bei d ≤ 2 vollständig lesbar und zerfällt bis d = 8. Ab d = 16 liegt die Zustandstrennung bei etwa 10⁻³ und damit unter σ = 0,02, die Werte sind Zufallsschwankungen.
- **Hebb-Anpassung kaum wirksam:** Unter diesem Protokoll ändert sie A wenig (‖ΔA‖_F ≈ 0,05). Die Kurven von eingefrorenem und angepasstem Netz sind praktisch gleich, auch beim vorab festgelegten Hauptkontrast d = 8.
- **Kopplung wirkt:** Gegenüber dem ungekoppelten Leak-Modell ist der Unterschied sichtbar (d = 4: 0,90 gegen 0,70).
- **Modulstruktur:** Das modulare Netz (c = 1/4) hält die Spur länger als das gleich budgetierte uniforme Netz (d = 4: 0,90 gegen 0,63). Modulnamen allein ändern nichts.
- **Kontrollen:**
  - Reset und Summenbeobachtung liegen auf Zufallsniveau. Die Summe ist wegen der symmetrischen Eingänge schon bei d = 0 informationslos.
  - Der eingefrorene Decoder versagt nach der Permutation, ein neu angepasster liest wieder.
- **Gepaartes Rauschen sichtbar:** Bei d = 32 haben alle Bedingungen exakt denselben Wert, weil sie dasselbe Rauschen sehen und die Zustände nahezu gleich sind.

## M4: Auswertung und Forschungsrunde

### Hochrechnung vor dem Start

- **Smoke:** Auswertung 0,45 s und Anpassung 0,11 s bei 3 Seeds × 80 Episoden je Klasse und Verzögerung.
- **Forschungsrunde:** 20 Seeds × 250 Episoden je Klasse und Verzögerung.
- **Erwartung:** etwa 0,45 × 3,1 × 6,7 + 0,11 × 6,7 ≈ 10 s, RAM etwa 100 MiB. Das liegt unter allen Grenzen (10 min, 2 GiB, 100 MiB).

### Auswertung

[`evaluate.py`](evaluate.py):

- **Vorab festgelegter Hauptkontrast:** neu trainierter Decoder, angepasst minus eingefroren, d = 8.
  - Gepaarte Differenz je Seed, also gleiche Testepisoden und gleiches Rauschen.
  - 95-%-Bootstrap des Mittelwerts über **ganze Seeds**: 2000 Wiederholungen, Seed 2026100399. Benannt als **synthetische** Unsicherheit unter genau dieser Seed- und Rauschverteilung.
  - Optional der exakte Sign-Flip-p-Wert über SCF, mit Austauschbarkeitsannahme.
- **Übrige Verzögerungen und Bedingungen:** nur beschreibend.
- **Ergebnisvokabular:** wie in SCF, `numerical_sample` / `synthetic_only`, mit Annahmen und „nicht behauptet“-Liste.

[`tests/test_m4_evaluate.py`](tests/test_m4_evaluate.py): 2 neue, insgesamt **56/56**. Geprüft werden:
- der Bootstrap ist deterministisch und umschließt den Mittelwert;
- der Hauptkontrast ist tatsächlich gepaart;
- Smoke-Ergebnisse sind als nicht inferenziell markiert;
- es entsteht striktes JSON.

### Forschungsrunde

| Feld | Wert |
|---|---|
| Run-ID | `research-e19650a0a0` |
| Status | complete, **20 Seeds**, kein Ausfall |
| Episoden je Klasse und Verzögerung | 100 Decoder-Training, 50 Validierung, 100 Test; die Anpassung nutzt eigene Episoden |
| Laufzeit / RAM | **5,9 s**, 95 MiB Spitze |
| Ergebnisdatei | 572 KB, SHA-256 beginnt mit `e30b93fb683c9ba7` |
| Auswertung | 36 KB, SHA-256 beginnt mit `63102e90ad85dcce` |
| Ablage | `D:/mandala/mandala-memory-results/research/` |

**Startbefehle:**
- `PYTHONPATH=. …/python.exe -m experiments.mandala_memory.cli run --mode research`
- `… -m experiments.mandala_memory.evaluate D:/mandala/mandala-memory-results/research/research-e19650a0a0.json --out …evaluation.json`

### Hauptkontrast (vorab festgelegt)

Bei d = 8, angepasst minus eingefroren, neu trainierter Decoder:
- **mittlere gepaarte Differenz:** −0,001;
- **95-%-Bootstrap:** [−0,0025; +0,0005];
- **Sign-Flip:** p = 11/32 (unter der Austauschbarkeitsannahme).

Unter diesem Protokoll verbessert die episodische Hebb-Anpassung das Ablesen bei d = 8 **nicht nachweisbar**. Das ist ein verwertbares Ergebnis und keine Gewinnerbehauptung.

### Beschreibende Kurven

Mittlere Balanced Accuracy über 20 Seeds:

| d | frozen | adapted | adapted, Decoder eingefroren | Leak (A = 0) | linear | uniform ≡ umbenannt | Reset | Summe | Perm. eingefroren | Perm. neu |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 0,496 | 0,497 | 0,487 | 1,000 |
| 1 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 0,495 | 0,506 | 0,735 | 1,000 |
| 2 | 0,997 | 0,997 | 0,997 | 0,990 | 0,999 | 0,977 | 0,510 | 0,497 | 0,731 | 0,998 |
| 4 | 0,931 | 0,933 | 0,933 | 0,706 | 0,950 | 0,651 | 0,499 | 0,489 | 0,721 | 0,930 |
| 8 | 0,668 | 0,667 | 0,667 | 0,499 | 0,687 | 0,496 | 0,493 | 0,496 | 0,586 | 0,661 |
| 16 | 0,506 | 0,505 | 0,505 | 0,507 | 0,508 | 0,507 | 0,507 | 0,487 | 0,508 | 0,508 |
| 32 | 0,489 | 0,489 | 0,489 | 0,489 | 0,489 | 0,489 | 0,489 | 0,492 | 0,489 | 0,489 |

### Grenzen

- **Kein Ressourcenvergleich:**
  - Das Leak-Modell hat weniger Kopplungsbudget.
  - Die Summenbeobachtung hat eine andere Dimension.
  - Das lineare Modell hat eine andere Amplitudendynamik; es ist separat berichtet und kein Sieg der Linearität.
- **Keine unabhängigen Tests:** Die Verzögerungen eines Seeds teilen dasselbe angepasste Netz.
- **Keine biologische Aussage:** Seeds sind synthetische Wiederholungen.
- **Variabilität:** Prozessrauschen ist null; Schwankungen kommen nur aus dem Messrauschen und der Reihenfolge der Anpassung.
- **Geltungsbereich:** Das Ergebnis gilt **nur** für dieses Protokoll, also η = 0,3, 40 Episoden zu je 5 Schritten und σ = 0,02. Ob andere Anpassungsregeln oder längeres Training helfen, ist eine offene Frage für eine spätere Runde.

## M5: Feldtheorie-Membranpilot

### Code

[`membrane_pilot.py`](membrane_pilot.py): Pilot mit `AdaptiveLogisticMembrane` aus Feldtheorie. Die θ/β-Semantik bleibt **unverändert**.

- **Loader:** Die Datei `models/adaptive_logistic_membrane.py` wird **per Pfad** geladen. `import models…` würde über `models/__init__.py` das ganze Modellpaket importieren (2,9 s, fremde Solver). Feldtheorie selbst wird nicht verändert.
- **Aufgabe:** Amplitudenreiz R = 0,2 (Klasse 0) gegen 0,8 (Klasse 1), danach Pause R = 0 über d Schritte, danach eine **Probe** R = 0,5 als eigener, protokollierter Eingriff.
- **Berichtet wird beides:**
  - `pre_probe_sigma`: die Antwort mit dem Zustand vor der Probe;
  - `post_probe_sigma`: die Ausgabe von `propagate`, die erst aktualisiert und dann ausgibt.
- **Vergleich:** adaptive Membran gegen eingefrorene Membran, bei der alle Plastizitäts- und Relaxationsfaktoren 0 sind.
- **Pilot-Annahmen** (nicht im Plan festgelegt): θ0 = 0,5, β0 = 6, übrige Parameter auf Standardwerten, dt = 1, σ = 0,02 auf der Probe-Ausgabe.
- **Startbefehl:** `… -m experiments.mandala_memory.cli pilot-membrane`. Die Ausgabe landet in `D:/mandala/mandala-memory-results/membrane_pilot/`.

### Tests

[`tests/test_m5_membrane.py`](tests/test_m5_membrane.py): **8 neue, insgesamt 64/64.**

- Ein langer Trace ist bitgleich mit zwei Stücken auf derselben Instanz.
- Die **Parameter sind Zustand:** Eine Wiederverwendung ohne Reset behält die Erinnerung; `reset()` entspricht einer frischen Instanz.
- Probe: bei der adaptiven Membran ist der Wert vor dem Update ≠ nach dem Update, bei der eingefrorenen gleich.
- Die eingefrorene Membran hat kein Klassengedächtnis.
- Der Loader importiert das `models`-Paket nicht.
- Die Quelle ist gleich dem Plan-Commit.

### Ergebnis

Rein beschreibend, 3 Seeds, 40 Episoden je Klasse:

| d | θ vor Probe (Klasse 0 / 1) | Probe-Ausgabe (0 / 1) | Balanced Accuracy adaptiv | eingefroren |
|---|---|---|---|---|
| 0 | 0,451 / 0,672 | 0,536 / 0,332 | 1,00 | ≈ 0,5 |
| 4 | 0,307 / 0,521 | 0,613 / 0,483 | 1,00 | ≈ 0,5 |
| 8 | 0,190 / 0,372 | 0,659 / 0,583 | ≈ 0,97 | ≈ 0,5 |
| 16 | 0,110 / 0,151 | 0,687 / 0,673 | ≈ 0,66 | ≈ 0,5 |
| 32 | 0,103 / 0,103 | 0,689 / 0,689 | ≈ 0,5 | ≈ 0,5 |

**Lesart:**
- Die adaptive Membran trägt die Reizamplitude in ihrem adaptiven Parameterzustand (θ und β) weiter. Die Spur zerfällt über die Pause, unter anderem weil θ unter R = 0 gegen etwa 0,10 läuft. *Präzisiert nach Review 2026-10-03:* Eine Zuschreibung allein an θ wäre ohne Parameter-Ablation zu stark.
- Die eingefrorene Membran zeigt ausdrücklich kein Gedächtnis: identische Ausgabe für beide Klassen.
- **Dies ist eine andere Aufgabe als im Netz-Benchmark**, also kein fairer Vergleich und kein Modellsieger.

## M6: Lokale Mandala-Ansicht

### Dienst

[`serve.py`](serve.py) ist ein lokaler Python-Dienst (Standardbibliothek).

- **Erreichbarkeit:** nur `127.0.0.1`.
- **Keine Shell-Endpunkte, keine Pfade aus dem Browser:** Die Datei-Whitelist umfasst `index.html`, `app.js` und `style.css`. Andere Pfade wie `/../serve.py` liefern 404.
- **Nur aufgezählte, begrenzte Parameter:** Netz, Reiz A/B, Pause 0–64, Eingriff „löschen nach dem Reiz“, 1–4 Läufe.
- **Herkunft der Traces:** Jeder Trace kommt aus dem getesteten Kern (`EpisodeOperator`). Es gibt **keinen zweiten Physik-Kern in JavaScript**.
- **Protokoll:**
  - Jede Anfrage bekommt eine **neue Run-ID** `explore-…` und die Kennzeichnung explorativ.
  - Sie wird unter `D:/mandala/mandala-memory-results/explore/` abgelegt, plus eine angehängte Zeile in `protocol.jsonl`.
  - Benchmark-Daten (`smoke/`, `research/`) werden nie geschrieben. Ein Test prüft das.
- **Vergleich:** Er berichtet ‖Δx‖₂ und die **Bayes-Accuracy** Φ(‖Δx‖₂ / 2σ) über alle Koordinaten. Siehe die Korrektur weiter unten.

### Ansicht

Liegt in unified-mandala, Worktree `D:/mandala/.worktrees/unified-mandala-memory-lab`, Branch `memory-lab`, Ordner `experiments/memory_lab/`: `index.html`, `app.js`, `style.css`, `FORMAT.md`, `README.md`.

- **Technik:** HTML/JS ohne Abhängigkeiten und ohne Build-Schritt.
- **Mandala:** zwölf Knoten mit Helligkeit auf fester Skala [0,1], der Zahlenwert steht immer dabei. Kantenstärke aus A; Modulring und Beschriftung M1–M3; markierte Eingänge.
- **Zeitachse:** mit den Phasen Start / Reiz / gelöscht / Pause / Ablesung, inklusive Abspielen.
- **Vergleich:** zwei Läufe nebeneinander mit identischem x₀.
- **Weitere Bereiche:** Ergebnis- und Protokollbereich, die schreibgeschützte Voreinstellung ist einsehbar.
- **Klang:** aus (nicht implementiert).
- **Kantenablation:** noch nicht eingebaut; sie ist für die nächste Runde vorgesehen.

### Tests

[`tests/test_m6_serve.py`](tests/test_m6_serve.py): **15 neue, insgesamt 79/79.**

- Ungültige Anfragen werden abgewiesen.
- Die Traces sind gleich `recall_state`.
- Der Eingriff „löschen“ ergibt null; der Start ist identisch.
- Die Bayes-Accuracy entspricht der Formel.
- Jede Anfrage bekommt eine neue Run-ID und einen Protokolleintrag.
- Echte HTTP-Anfragen: Whitelist und 404, Bindung an 127.0.0.1, HTTP 400 bei ungültigen Werten.
- Benchmark-Dateien bleiben unberührt.

### Visuelle Prüfung

Gemacht mit einem Headless-Edge-Screenshot (Profil auf D:) von `/?autostart`. Dieser Parameter startet den voreingestellten Vergleich A gegen B bei d = 8; auch das ist ein protokollierter, explorativer Lauf.

**Korrektur nach der Sichtprüfung:**
- **Vorher:** Die Ansicht urteilte über die größte Einzelkoordinate max|Δx| = 0,007 < σ und meldete „praktisch nicht unterscheidbar“. Das war **irreführend**, denn der Decoder nutzt alle 12 Koordinaten.
- **Jetzt:** Die Ansicht zeigt Φ(‖Δx‖₂ / 2σ) = **68,3 %**. Das stimmt mit der gemessenen Balanced Accuracy der Forschungsrunde bei d = 8 überein (0,668).
- Außerdem wurden die überlappenden Knotenbeschriftungen nach außen gerückt.

**Start:** `PYTHONPATH=. …/python.exe -m experiments.mandala_memory.serve --port 8765`, dann `http://127.0.0.1:8765/` öffnen.

## M7: Reproduzierbare Übergabe

### Dateien

- [`README.md`](README.md): Startbefehle, Ergebnis der ersten Runde und bekannte Grenzen.
- [`protocol/startkonfiguration.yaml`](protocol/startkonfiguration.yaml): YAML-Zwilling der eingefrorenen JSON-Konfiguration. Damit ist die Trilayer-Regel aus Feldtheories `AGENTS.md` erfüllt (M0-Befund 7). Beim Einlesen ist er inhaltlich identisch mit dem JSON.
- [`tools/mutation_check.py`](tools/mutation_check.py): gezielte Mutanten. Sie laufen auf einer **Kopie**; ein Hash belegt, dass der Arbeitsbaum unverändert bleibt.
- [`tools/make_review_package.py`](tools/make_review_package.py): baut das Reviewpaket unter `D:/mandala/mandala-memory-results/review/`. Es enthält:
  - Patches beider Repos gegen die Plan-Commits und die Commit-IDs;
  - SHA-256 jeder Experiment-, Ansichts- und Ergebnisdatei;
  - Konfiguration als JSON und YAML;
  - Rohergebnisse (Smoke, Forschung mit Auswertung, Membran-Pilot, Explore-Protokoll);
  - Ressourcen, pytest-JUnit-Bericht, Mutationsbericht und Screenshots.

### Mutationsprüfung

**15/15 erkannt.** Der erste Lauf erkannte 12/15; die drei Überlebenden habe ich einzeln untersucht:

| Mutant | Befund | Folge |
|---|---|---|
| `float_matrix_not_exact` | **Falsch konstruiert:** Er skalierte beide Matrizen gleich. | Auf den Gleitkomma-Pfad umgezielt. Dort weichen M = 1 und M = 3 (c = 8/11) um 1,4·10⁻¹⁷ ab, und K7 erkennt das. Die exakte Konstruktion ist also nötig. |
| `adapted_mask_ignored` | **Äquivalent:** Die Standardmaske erlaubt ohnehin alle Kanten außer der Diagonale. | Ersetzt durch „Diagonale erlaubt“; SCF `hebb_update` lehnt das ab. |
| `primary_not_paired` | **Echte Testlücke:** Im Testfall waren alle gepaarten Differenzen 0, die Paarung war deshalb unsichtbar. | Neuer Test mit synthetischen, je Seed verschiedenen Werten; der Mutant „verschobene Paarung“ wird jetzt erkannt. |

**Tests danach: 80/80.**

## Review-Fix `astra-review-2026-10-03` (R1, R2)

Review: `D:/mandala/mandala-memory-results/astra-review-2026-10-03/REVIEW_FUER_CLAUDE.md`, geprüft am Stand `0a931fd`.

Das Review bestätigt unabhängig:
- den Hauptbefund (−0,001; [−0,0025; +0,0005]);
- die Formel Φ(‖Δx‖₂ / 2σ);
- einen frischen Forschungslauf, der identisch mit dem Original ist.

Beide Befunde habe ich **zuerst unverändert reproduziert** (`0a931fd`, isolierter Temp-Ordner auf D:):
- **R1:** gleiche ID, gleicher Pfad; aus 2 gespeicherten Läufen wurden 0.
- **R2:** 2-Seed-Lauf „complete“ mit `inferential_claims = True`; abgebrochener Lauf „aborted“, ebenfalls `True`.

| Befund | Korrektur | Regression |
|---|---|---|
| **R1** Ergebnisdateien kollidieren | Feste **Protokoll-ID** plus eindeutige **Ausführungs-ID**; Dateiname `<protokoll>--<ausführung>.json`. Das Manifest führt angeforderte und deklarierte Seeds sowie die effektiven Optionen. Schreiben ist **atomar und exklusiv** (Temp-Datei + `os.link`, schlägt bei vorhandenem Ziel fehl). Timeout ≤ 0 und doppelte Seeds werden abgewiesen. Auch `evaluate --out` schreibt exklusiv. | Voll-, Teil- und Abbruchlauf im selben Ordner bleiben alle erhalten (2/1/0 Läufe); keine Temp-Reste; erzwungene ID-Kollision bricht ab und lässt die erste Datei unverändert; `write_exclusive`; Timeout 0 und −1; doppelte Seeds |
| **R2** Inferenz trotz unvollständigem Protokoll | `inference_release(result)` gibt Inferenz nur frei bei: Modus „research“, Status „complete“, keine Fehlschläge, eindeutige Seeds, ausgeführte und angeforderte Seeds gleich der **eingefrorenen** Protokoll-Liste, Konfiguration gleich dem eingefrorenen Protokoll. Technischer Status und Protokollvollständigkeit stehen getrennt, die Gründe maschinenlesbar. Der exakte Sign-Flip-p-Wert wird nur bei Freigabe berechnet; sonst ist das Ergebnis **nur beschreibend**. | 2 statt 20 Seeds, Duplikate, Abbruch, Fehlschlag, als „research“ umetikettierter Smoke-Lauf, geänderte Konfiguration → alle nicht freigegeben. Die Original-Vollrunde ist freigegeben und **zahlengleich**. |

### Weitere Änderungen

- **Exakter Sign-Flip schneller:** Er läuft jetzt über die Zählung exakter Summen statt über die Aufzählung aller 2²⁰ Muster. Ohne das hätten die neuen Tests 5 min statt 6 s gebraucht. Der Wert ist gleich SCF `sign_flip_test` (Kreuztest für n ≤ 12) und für das Original wieder **11/32**.
- **UI erklärt die Bayes-Zahl:** Sie ist die ideale Trennbarkeit genau dieser zwei Läufe. Nur bei gleichem Netz, gleichem Eingriff und Reiz A gegen B ist sie die Erinnerungsleistung des Netzes. Per Screenshot geprüft.
- **Membran-Formulierung präzisiert:** adaptiver Parameterzustand θ **und** β; eine Zuschreibung allein an θ wäre ohne Parameter-Ablation zu stark.
- **README:** PowerShell-Startbefehle und die neuen Regeln für Ergebnisdateien und Inferenz.

### Mutationsprüfung

**21/21 erkannt**, mit 6 neuen Mutanten für R1/R2. Einer überlebte zunächst: `r1_overwrite_instead_of_exclusive`. Die eindeutige ID verdeckte, ob der Runner selbst exklusiv schreibt. Ein neuer Test erzwingt deshalb eine Kollision.

### Ergebnis

- **Tests:** 95/95 in etwa 6 s.
- **Hauptauswertung** der unveränderten Originaldaten, neu berechnet: zahlengleich, abgelegt als neue Datei `research-e19650a0a0.evaluation.v2-after-review.json`. Die alte Auswertung bleibt unberührt.
- **Kein Push.**

## M8: Regler-Labor (explorativ)

**Auftrag (Johann, 2026-10-03):**
- „Bitte M8, danach M9. M8 bleibt explorativ, protokolliert und getrennt vom Benchmark.“
- „Erst das Mandala erlebbar machen; die bisherigen Benchmarkdaten bleiben dabei unverändert.“

### Code

- [`lab.py`](lab.py): reine Rechnung mit dem getesteten Kern (`EpisodeOperator`), kein zweiter Physik-Kern.
  - **Regler** (begrenzt und aufgezählt, sonst Ablehnung): N ∈ {6, 12, 18, 24}, M, c, γ, ℓ, Reizstärke a, σ, Schwelle p*, Eingangsknoten A/B, tanh oder linear, Löschen nach dem Reiz (alles oder ein Modul), Ablesung H (alle Knoten / Modulmittel / Summe / ein Knoten).
  - **Kantenablation** (ungerichtet), in zwei Arten:
    - `budget_loss`: Die Zeilensumme sinkt.
    - `renormalize`: Berührte Zeilen kommen zurück auf γ; Zeilen ohne verbleibende Kante bleiben 0 und werden gemeldet.
  - **Ideale Erinnerungskurve:** Bayes(d) = Φ(‖H(x_A − x_B)‖₂ / 2σ) für d = 0…64.
  - **Obere Schranke aus q:** q_eff = 1 − ℓ + ℓ·max_i Σ_j |A_ij| der *tatsächlich benutzten* Matrix, mit ‖H Δx(d)‖ ≤ κ(H)·q_eff^d·‖Δx_1‖_∞ und κ(H) = √(Σ_r (Σ_c |H_rc|)²).
  - **Gedächtnisdauer, explizit definiert:** D = letzte Pause d ∈ 0…64 mit Bayes(d) ≥ p* (Standard p* = 0,75). Dazu kommen die Ersterreichungs-Variante, Monotonie und Zensur bei d = 64.
- [`serve.py`](serve.py):
  - `POST /api/lab` → Run-ID `lab-…`. Die Datei unter `explore/` wird **exklusiv** angelegt; es folgt eine Zeile `"kind": "lab"` mit den bereinigten Reglerwerten in `protocol.jsonl`.
  - Whitelist erweitert um `lab.html` und `lab.js`.
  - Ein zu großer Body (> 20 kB) wird begrenzt gelesen und mit 400 abgewiesen, statt die Verbindung abzubrechen.
- Ansicht (unified-mandala `experiments/memory_lab/lab.html`, `lab.js`):
  - Drei Mandalas: Zustand nach Reiz A, nach Reiz B und die **Gedächtnisspur** x_A − x_B in Einheiten von σ.
  - Kanten werden per Klick entfernt.
  - Erinnerungskurve mit Benchmark-Kurve, q-Schranke, Schwelle, D und bis zu drei festgehaltenen Kurven.
  - Optional live neu rechnen.
  - Im Browser wird nur dargestellt.

### Tests

[`tests/test_m8_lab.py`](tests/test_m8_lab.py): **38 neue, insgesamt 133/133.**

| Prüfung | Ergebnis |
|---|---|
| Ablehnung | 25 ungültige Reglerwerte (Bereich, Typ, NaN, Wahrheitswert, unbekannter Schlüssel, Pfad, Selbstkante, …) und falsche Anfrageform |
| Benchmarkwerte | Ergeben bitgleich das eingefrorene Netz (A, B) und die Zustände von `recall_state`. Bayes(8) ist gleich der M6-Anzeige (0,683), q_eff = 0,9. |
| q-Schranke | Bei 60 zufälligen Reglersätzen (mit Ablation, Löschen, allen H) nie überschritten |
| Gleiches q, verschiedene Dauer | c = 0,05 / 0,25 / 0,5 haben alle q_eff = 0,9, aber D sinkt streng. Beim Benchmark liegt die Trennung bei d = 16 unter 5 % der Schranke. |
| Ablation | Budgetverlust senkt nur berührte Zeilen; Renormieren bringt sie auf γ zurück; leere Zeilen werden gemeldet, schon fehlende Kanten ebenfalls. Alle Kanten weg ≡ Leak-Modell (bitgleich). |
| Löschen | „Alles löschen“ gibt überall 0,5 und D = keine. Bei „ein Modul löschen“ ist das Modul null und der Rest gleich dem Zustand vor dem Eingriff. |
| Ablesung | Die Summe trägt bei symmetrischen Eingängen nichts. Modulmittel, Einzelknoten und κ(H) sind von Hand nachgerechnet. |
| Linear | Δx(d) = J^d Δx_1 mit J = (1−ℓ)I + ℓA (relativ 1e‑12) |
| Definition D | Synthetische Kurven: nicht monoton, sofort unter der Schwelle, zensiert. Benchmark: Bayes(6) ≥ 0,75 > Bayes(7), also D = 6. |
| Protokoll | Neue Run-ID je Berechnung, Protokollzeile `kind: lab`, kein Überschreiben (`FileExistsError`), Benchmark-Dateien und eingefrorenes Protokoll unverändert |
| HTTP | `lab.html`/`lab.js` werden ausgeliefert, `lab.py` gibt 404; 400 bei ungültigen Werten, falscher Form und zu großem Body |

**Mutationsprüfung: 28/28 erkannt**, darunter 7 neue Mutanten für M8: Schranke ohne κ(H), Renormierung übersprungen, Ablation nur in eine Richtung, falsches Modul gelöscht, D als Ersterreichung, Kurve ohne H, Überschreiben im Protokoll.

### Fehler unterwegs (in meinen Tests, nicht im Code)

1. **Vermutung bei „Modul löschen“ war falsch.** Ich hatte erwartet, dass das Löschen des Moduls von Eingang B die Erinnerung *schwächt*. Sie wird **stärker** (d = 8: 0,68 → 0,81; d = 16: 0,52 → 0,64). Der Grund:
   - Der Reiz landet nur auf Knoten 4. Nach dem Löschen ist deshalb x_B ≡ 0 und x_A − x_B = x_A.
   - x_A enthält den langsamen Gleichtaktmodus, der mit q abklingt. Ohne Eingriff steht der Reizunterschied senkrecht auf diesem Modus.
   - *Präzisiert nach Review (Erratum 1):* Die Aufgabe hat sich dadurch verändert, denn A wird jetzt gegen ein Nullsignal unterschieden. Der gelöschte B-Zustand wird **nicht** wiederhergestellt.

   Der Test prüft jetzt diesen Mechanismus.
2. **Toleranz im Linearitätstest zu streng.** Die absolute Toleranz von 1e‑18 war für Werte um 10⁻² zu eng; die Abweichung lag bei etwa 1e‑17. Jetzt wird relativ geprüft.
3. **Verbindungsabbruch bei großem Body.** Der Server antwortete, ohne den Body zu lesen, und Windows brach die Verbindung ab. Behoben im Dienst, siehe oben.

### Sichtprüfung

Headless-Edge-Screenshot von `/lab.html?autostart` (ein protokollierter, explorativer Lauf):
- Benchmark mit D = 6 und 68,3 % bei d = 8.
- Die Gedächtnisspur zeigt das Muster +0,3σ (Modul M1) / −0,3σ (M2) / 0 (M3).
- Die q-Schranke liegt weit über der Kurve.

### Explorative Vorerfahrung (für M9 als „gesehen“ zu führen)

Vor M8 habe ich mit einem Wegwerf-Skript (nicht im Repo) die ideale Kurve für einzelne Reglerwerte angesehen:
- γ ∈ {0,5; 0,95}
- ℓ ∈ {0,25; 0,9}
- c ∈ {0,05; 0,5}
- a = 1,2
- Eingänge (0, 1)
- M = 1

Diese Kombinationen und alle `lab`-Einträge in `explore/protocol.jsonl` gelten in M9 als **bereits gesehen** und sind dort keine Prüffälle.

## M9a: Herleitung, Kontrollen, Vorhersagemodul

**Auftrag:** siehe [`docs/M9_HERLEITUNG.md`](docs/M9_HERLEITUNG.md). Dort stehen Modellfamilie, Moden, Projektionen, die Definition der Gedächtnisdauer, die beweisbare Fehlerschranke und das Prüfprotokoll. Das Dokument wurde **vor** jeder Rechnung an Prüfkombinationen geschrieben.

### Kernaussagen der Herleitung

- **Reizeinkopplung** ist exakt: x_1 = ℓ·tanh(a)·e_i. Linearisiert wird nur die Pause.
- **Drei Moden** von J = (1−ℓ)I + ℓA:

  | Mode | Eigenwert von J |
  |---|---|
  | Gleichtakt | q = 1 − ℓ + ℓγ |
  | Modul-Unterschied | μ_D = 1 − ℓ + ℓγ(1 − cN/(N−n)) |
  | Binnenmodul | μ_I = 1 − ℓ − ℓγ(1−c)/(n−1) |

- **Der Reizunterschied hat keinen Gleichtakt-Anteil**, auch nichtlinear: Eine Involution P mit P A Pᵀ = A tauscht die beiden Eingänge, also gilt x_B(k) = P x_A(k). **q ist deshalb nicht die Erinnerungsrate**, nur eine obere Grenze.
- **Fehlerschranke der Linearisierung:**
  - Antisymmetrie und eine monotone Majorante (0 ≤ x_A(k) ≤ J^(k−1) x_1) ergeben E(d) = 2ℓ Σ ρ^(d−k) ‖h(A y_k)‖ mit h(z) = z − tanh z.
  - Alles ist geschlossen berechenbar und ergibt ein beweisbares Band für die ideale Trefferquote und für D.

### Unabhängige Kontrollen

[`controls/m9_hand_controls.py`](controls/m9_hand_controls.py): exakte Brüche, eigene Blockmatrix, kein SCF, kein Vorhersagemodul.

| Kontrolle | Wert |
|---|---|
| Moden Benchmark | q = 9/10, μ_D = 3/4, μ_I = 2/5 (λ_D = 1/2, λ_I = −1/5) |
| Eigenwertgleichungen + Spur | exakt für 6 Netzformen (N/M = 12/3, 12/1, 12/2, 24/6, 18/9, 6/3) |
| ‖J^d(e_0 − e_4)‖² | exakt = ½(3/4)^(2d) + (3/2)(2/5)^(2d) für d = 0…16 (direkte Matrixpotenz) |
| Gleiches Modul (0, 1) | ‖J^d(e_0 − e_1)‖² = 2(2/5)^(2d) exakt |
| Ideale Trefferquote, linear | d = 4: 0,935319; d = 8: 0,682698; d = 16: 0,518973 |
| D₀,₇₅ | **6** (Bayes(6) = 0,801 ≥ 0,75 > Bayes(7) = 0,737) |
| naive q-Regel | D_q = 25 (0,9^d ≥ 0,07105), also weit daneben |

### Vorhersagemodul

[`predict.py`](predict.py) arbeitet nur mit geschlossenen Formeln und importiert weder Kern noch Labor, Dienst oder SCF; ein Test prüft das in einem eigenen Prozess. Es liefert:
- Moden und Projektionsgewichte;
- die lineare Trennung s_lin(d) und die Schranke E(d);
- das Bayes-Band;
- D_lin, [D_lo, D_hi] und D_q.

### Tests

[`tests/test_m9_predict.py`](tests/test_m9_predict.py): **60 neue**, ausschließlich an **20 Entwicklungsfällen**. Deren Werte für c, γ, ℓ, a und σ liegen alle außerhalb des Prüfrasters von M9b.

| Prüfung | Ergebnis |
|---|---|
| Benchmark | gleich den Handkontrollen; D = 6, Band [6, 6], D_q = 25; E(8) < 1 % von s_lin(8) |
| Eigenwerte | Das Spektrum der Kernmatrix ist gleich {γ, λ_D^(M−1), λ_I^(N−M)} für alle Entwicklungsfälle. |
| Symmetrie P | Für alle Paare i ≠ j in 6 Netzformen ist P eine Involution, P(i) = j und A[P,P] = A. |
| Linearer Grenzfall | Vorhersage = Kern (relativ 1e‑10), E = 0 |
| Band | Der Kern liegt bei **allen** 20 Entwicklungsfällen und allen d im Band, auch bei a = 3, ℓ = 1 und γ = 0,95; D des Kerns liegt in [D_lo, D_hi]. |
| Struktur | Summe → 0; Modulmittel = g·μ_D^d·√2/n; Modulmittel bei gleichem Modul → 0 |
| Familie | Kombinationen außerhalb von F werden abgewiesen. |

**Fehler unterwegs (im Vorhersagemodul, durch Entwicklungstest gefunden):** Im linearen Grenzfall hatte ich g = ℓ·tanh(a) statt ℓ·a benutzt. Ohne tanh wird auch der Puls nicht gesättigt. Das ist korrigiert und als Mutant abgesichert.

**Mutationsprüfung: 32/32 erkannt**, mit 4 neuen Mutanten: falsches Modulverhältnis, Schranke weggelassen, zu kleine Rate ρ, tanh im linearen Grenzfall.

## M9b: Vorhersagen eingefroren

- **Werkzeuge:**
  - [`m9_registry.py`](m9_registry.py): Register des Gesehenen und Prüfraster, reine Daten.
  - [`m9_freeze.py`](m9_freeze.py): Ziehung, mechanische Prüfung auf „ungesehen“, exklusives Schreiben. Importiert keinen Kern; ein Test prüft das in einem eigenen Prozess.
- **Ziehung:** Seed 202610039, 24 Kombinationen, je 6 pro Messoperator (`full`, `module_means`, `node`, `sum`), davon 9 mit Eingängen im selben Modul (2 davon wegen M = 1). Das Raster für c, γ, ℓ, a und σ teilt **keinen** Wert mit den 21 gesehenen Fällen:
  - 20 Entwicklungsfälle (enthalten Benchmark und Scan vor M8);
  - 1 Labor-Eintrag in `explore/protocol.jsonl`: meine Sichtprüfung mit Benchmarkwerten.
- **Eingefroren:** [`protocol/m9_frozen_predictions.json`](protocol/m9_frozen_predictions.json)
  - SHA-256 `1e872cecaaa4ff10d796e921a289119cde32ba1fee8698cc0881e4137867de13`, geschrieben auf Stand `6f8a812`;
  - `kernel_evaluated_before_freeze: false`;
  - Prüfsummen (zeilenende-normiert) von `predict.py`, `docs/M9_HERLEITUNG.md` und `m9_registry.py`. Ändert sich eine dieser Dateien nach dem Einfrieren, schlägt `test_committed_frozen_predictions_are_intact` an.
- **Prüfregeln** sind in der Datei selbst festgehalten (`rules`), wie in der Herleitung, Abschnitt 7.

**Die eingefrorenen Vorhersagen** (p\* = 0,75; „–“ = bei **keiner** Pause d = 0…64 mindestens p\*; *berichtigt nach Erratum 1, R4:* früher stand hier „schon bei d = 0 unter p\*“):

| id | N/M | c | γ | ℓ | a | σ | Eingänge | H | q | μ_D | μ_I | D_lin | [D_lo, D_hi] | D_q |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h00 | 12/1 | – | 0.6 | 0.75 | 2.4 | 0.015 | n9/n6 (gleich) | full | 0.700 | – | 0.209 | 2 | [2, 2] | 11 |
| h01 | 12/3 | 0.100 | 0.6 | 0.3 | 1.6 | 0.01 | n0/n10 (versch.) | full | 0.880 | 0.853 | 0.646 | 16 | [16, 16] | 26 |
| h02 | 12/4 | 0.600 | 0.85 | 0.75 | 1.6 | 0.01 | n0/n1 (gleich) | full | 0.887 | 0.378 | 0.122 | 2 | [2, 2] | 35 |
| h03 | 12/3 | 0.150 | 0.85 | 0.4 | 0.9 | 0.03 | n6/n9 (versch.) | full | 0.940 | 0.863 | 0.504 | 10 | [10, 10] | 37 |
| h04 | 18/9 | 0.100 | 0.9 | 0.3 | 0.3 | 0.03 | n4/n7 (versch.) | full | 0.970 | 0.940 | 0.457 | 12 | [12, 12] | 36 |
| h05 | 12/1 | – | 0.85 | 0.4 | 1.6 | 0.015 | n3/n9 (gleich) | full | 0.940 | – | 0.569 | 5 | [5, 5] | 52 |
| h06 | 12/6 | 0.150 | 0.6 | 0.75 | 1.6 | 0.01 | n10/n8 (versch.) | module_means | 0.700 | 0.619 | -0.133 | 7 | [7, 7] | 10 |
| h07 | 18/2 | 0.350 | 0.85 | 0.4 | 0.3 | 0.015 | n7/n10 (versch.) | module_means | 0.940 | 0.702 | 0.572 | – | [–, –] | – |
| h08 | 24/12 | 0.150 | 0.6 | 0.4 | 1.6 | 0.03 | n19/n18 (gleich) | module_means | 0.840 | 0.801 | 0.396 | – | [–, –] | – |
| h09 | 24/2 | 0.150 | 0.9 | 0.4 | 1.6 | 0.015 | n8/n13 (versch.) | module_means | 0.960 | 0.852 | 0.572 | 4 | [4, 4] | 18 |
| h10 | 18/3 | 0.800 | 0.85 | 0.3 | 0.9 | 0.03 | n16/n6 (versch.) | module_means | 0.955 | 0.649 | 0.690 | 0 | [0, 0] | 4 |
| h11 | 24/6 | 0.350 | 0.9 | 0.4 | 0.9 | 0.015 | n2/n0 (gleich) | module_means | 0.960 | 0.809 | 0.522 | – | [–, –] | – |
| h12 | 12/3 | 0.800 | 0.6 | 0.3 | 1.6 | 0.01 | n5/n8 (versch.) | node n2 | 0.880 | 0.664 | 0.688 | – | [–, –] | – |
| h13 | 18/9 | 0.150 | 0.7 | 0.6 | 2.4 | 0.015 | n0/n15 (versch.) | node n15 | 0.820 | 0.749 | 0.043 | 9 | [8, 9] | 16 |
| h14 | 12/4 | 0.350 | 0.9 | 0.3 | 0.9 | 0.03 | n0/n1 (gleich) | node n1 | 0.970 | 0.844 | 0.612 | 3 | [3, 3] | 54 |
| h15 | 24/6 | 0.100 | 0.85 | 0.6 | 1.6 | 0.03 | n4/n19 (versch.) | node n19 | 0.910 | 0.849 | 0.247 | 7 | [7, 7] | 27 |
| h16 | 18/2 | 0.350 | 0.6 | 0.3 | 1.6 | 0.01 | n13/n8 (versch.) | node n8 | 0.880 | 0.754 | 0.685 | 8 | [8, 8] | 23 |
| h17 | 24/6 | 0.100 | 0.7 | 0.75 | 2.4 | 0.015 | n15/n14 (gleich) | node n14 | 0.775 | 0.712 | 0.092 | 1 | [1, 1] | 14 |
| h18 | 12/4 | 0.800 | 0.7 | 0.75 | 1.6 | 0.015 | n10/n0 (versch.) | sum | 0.775 | 0.215 | 0.198 | – | [–, –] | – |
| h19 | 18/2 | 0.100 | 0.9 | 0.4 | 1.6 | 0.03 | n6/n15 (versch.) | sum | 0.960 | 0.888 | 0.559 | – | [–, –] | – |
| h20 | 24/6 | 0.150 | 0.85 | 0.3 | 1.6 | 0.01 | n14/n15 (gleich) | sum | 0.955 | 0.909 | 0.628 | – | [–, –] | – |
| h21 | 24/2 | 0.800 | 0.7 | 0.6 | 0.9 | 0.015 | n15/n0 (versch.) | sum | 0.820 | 0.148 | 0.392 | – | [–, –] | – |
| h22 | 24/2 | 0.800 | 0.7 | 0.4 | 1.6 | 0.03 | n9/n12 (versch.) | sum | 0.880 | 0.432 | 0.595 | – | [–, –] | – |
| h23 | 12/4 | 0.150 | 0.85 | 0.75 | 0.3 | 0.015 | n2/n1 (gleich) | sum | 0.887 | 0.760 | -0.021 | – | [–, –] | – |

**Vorab, ohne Kern, lesbar:**
- 23 von 24 sind Punktvorhersagen für D. Nur h13 (a = 2,4) hat das Band [8, 9].
- 10 Kombinationen sagen „keine Erinnerung über p\*“ vorher:
  - 6× nur die Summe beobachtet, denn der Unterschied ist antisymmetrisch;
  - h08 und h11: Modulmittel bei gleichem Modul;
  - h12: beobachteter Knoten in einem unbeteiligten Modul, dort ist Δx durch die Symmetrie exakt 0;
  - h07: Modulmittel-Unterschied g·√2/n = 0,018 schon bei d = 0 unter r\* = 0,020; er klingt danach nur noch ab (|μ_D| < 1), bleibt also bei allen d darunter.
- Die naive q-Regel sagt bei **allen** 14 Kombinationen mit vorhergesagter Erinnerung eine längere Dauer voraus, meist ein Vielfaches: h05 52 statt 5, h14 54 statt 3; am knappsten h06 mit 10 statt 7.

## M9c: Prüfung der eingefrorenen Vorhersagen

### Werkzeug

[`m9_evaluate.py`](m9_evaluate.py) wurde **vor** dem ersten echten Lauf committet (`ac764e4`). Es arbeitet in dieser Reihenfolge:
1. **Integrität:** SHA-256 der eingefrorenen Datei, dazu die unveränderten Prüfsummen von `predict.py`, Herleitung und Register.
2. **Primärprüfung:** gegen den getesteten Kern (über `lab.compute`).
3. **Decoder-Prüfung:** eigener Zufallsmodus `m9`, Seeds 9000 + Index.
4. **Ablage:** exklusiv unter `D:/mandala/mandala-memory-results/m9/`.

Tests: [`tests/test_m9_evaluate.py`](tests/test_m9_evaluate.py) mit Negativkontrollen an Entwicklungsfällen:
- eine manipulierte Datei wird erkannt, ein CRLF-Checkout besteht;
- ein zu schmales Band (E = 0) bei starker Nichtlinearität wird erkannt;
- eine falsche Dauer [7, 7] statt 6 wird erkannt;
- eine falsche Decoder-Vorhersage wird erkannt;
- die m9-Ströme sind von allen früheren Modi getrennt;
- die Ablage schreibt exklusiv und verweigert C:.

**Insgesamt 207/207.**

### Ergebnis

Ergebnisdatei `D:/mandala/mandala-memory-results/m9/m9-evaluation--8d353dbc88.json`, eingefroren auf `6f8a812`, ausgewertet auf `ac764e4`.

| Prüfstufe | Ergebnis |
|---|---|
| **Primär** (deterministisch, 24 Kombinationen × 65 Pausen) | **bestanden 24/24.** Jede Kern-Kurve liegt im eingefrorenen Band, jedes Kern-D im vorhergesagten Intervall. Die größte Abweichung nutzt 67 % des Erlaubten; die Schranke ist eng, nicht nur formal erfüllt. |
| **Sekundär** (Decoder, statistisch) | **bestanden 28/28** (14 Kombinationen × d = D_lin, D_lin + 1) |
| Punktvorhersagen | 23/23 exakt getroffen; h13 (Band [8, 9]) → Kern 9 |
| **Naive q-Regel** | liegt bei **allen 14** Kombinationen mit Erinnerung daneben, immer zu lang (z. B. h05: 52 statt 5, h14: 54 statt 3) |
| Zusatzhypothese Z1 (nicht bewiesen) | gilt in 3/3 anwendbaren Fällen; bleibt eine Hypothese |
| Stärkste Nichtlinearität | 3,8 % relative Abweichung von der linearen Kurve (h17, a = 2,4, ℓ = 0,75) |

**Je Kombination** („größte Abweichung / erlaubt“ ≤ 1 heißt bestanden; 0 bei exakt verschwindender Trennung):

| id | H | D vorhergesagt | D Kern | naive q-Regel | größte Abweichung / erlaubt | max. relative Nichtlinearität |
|---|---|---|---|---|---|---|
| h00 | full | 2 | 2 | 11 | 0.213 | 0.0003 |
| h01 | full | 16 | 16 | 26 | 0.631 | 0.0005 |
| h02 | full | 2 | 2 | 35 | 0.498 | 0.0149 |
| h03 | full | 10 | 10 | 37 | 0.646 | 0.0022 |
| h04 | full | 12 | 12 | 36 | 0.598 | 0.0014 |
| h05 | full | 5 | 5 | 52 | 0.213 | 0.0003 |
| h06 | module_means | 7 | 7 | 10 | 0.512 | 0.0289 |
| h07 | module_means | – | – | – | 0.581 | 0.0000 |
| h08 | module_means | – | – | – | 0.000 | 0.0000 |
| h09 | module_means | 4 | 4 | 18 | 0.674 | 0.0008 |
| h10 | module_means | 0 | 0 | 4 | 0.406 | 0.0001 |
| h11 | module_means | – | – | – | 0.000 | 0.0000 |
| h12 | node | – | – | – | 0.000 | 0.0000 |
| h13 | node | [8, 9] | 9 | 16 | 0.267 | 0.0252 |
| h14 | node | 3 | 3 | 54 | 0.354 | 0.0014 |
| h15 | node | 7 | 7 | 27 | 0.231 | 0.0098 |
| h16 | node | 8 | 8 | 23 | 0.080 | 0.0000 |
| h17 | node | 1 | 1 | 14 | 0.289 | 0.0380 |
| h18 | sum | – | – | – | 0.000 | 0.0000 |
| h19 | sum | – | – | – | 0.000 | 0.0000 |
| h20 | sum | – | – | – | 0.000 | 0.0000 |
| h21 | sum | – | – | – | 0.000 | 0.0000 |
| h22 | sum | – | – | – | 0.000 | 0.0000 |
| h23 | sum | – | – | – | 0.000 | 0.0000 |

**Decoder** (1000 Trainings- und 4000 Testepisoden je Klasse; Prüfband = [lo − 0,01 − 4 SE, hi + 4 SE]):

| id | d | Decoder (Balanced Acc.) | Bayes-Band | Prüfband | Kern-Bayes |
|---|---|---|---|---|---|
| h00 | 2 | 0.9383 | [0.9356, 0.9360] | [0.9146, 0.9470] | 0.9358 |
| h00 | 3 | 0.6189 | [0.6245, 0.6250] | [0.5928, 0.6467] | 0.6248 |
| h01 | 16 | 0.7821 | [0.7786, 0.7790] | [0.7501, 0.7975] | 0.7787 |
| h01 | 17 | 0.7371 | [0.7437, 0.7440] | [0.7141, 0.7635] | 0.7437 |
| h02 | 2 | 0.7704 | [0.7634, 0.7732] | [0.7346, 0.7921] | 0.7701 |
| h02 | 3 | 0.5346 | [0.5330, 0.5386] | [0.5007, 0.5609] | 0.5361 |
| h03 | 10 | 0.7846 | [0.7811, 0.7824] | [0.7527, 0.8009] | 0.7814 |
| h03 | 11 | 0.7423 | [0.7486, 0.7498] | [0.7192, 0.7692] | 0.7488 |
| h04 | 12 | 0.7550 | [0.7544, 0.7553] | [0.7252, 0.7745] | 0.7546 |
| h04 | 13 | 0.7331 | [0.7412, 0.7420] | [0.7116, 0.7616] | 0.7413 |
| h05 | 5 | 0.8500 | [0.8500, 0.8504] | [0.8241, 0.8664] | 0.8502 |
| h05 | 6 | 0.7284 | [0.7223, 0.7227] | [0.6923, 0.7428] | 0.7225 |
| h06 | 7 | 0.7996 | [0.7890, 0.8156] | [0.7612, 0.8335] | 0.7957 |
| h06 | 8 | 0.6839 | [0.6904, 0.7110] | [0.6600, 0.7315] | 0.6955 |
| h09 | 4 | 0.7761 | [0.7772, 0.7774] | [0.7486, 0.7960] | 0.7773 |
| h09 | 5 | 0.7417 | [0.7421, 0.7423] | [0.7126, 0.7619] | 0.7422 |
| h10 | 0 | 0.7960 | [0.8007, 0.8007] | [0.7728, 0.8186] | 0.8007 |
| h10 | 1 | 0.7104 | [0.7081, 0.7081] | [0.6778, 0.7284] | 0.7081 |
| h13 | 9 | 0.7591 | [0.7461, 0.7880] | [0.7172, 0.8069] | 0.7619 |
| h13 | 10 | 0.7059 | [0.6900, 0.7254] | [0.6597, 0.7458] | 0.7032 |
| h14 | 3 | 0.7915 | [0.7941, 0.7948] | [0.7661, 0.8128] | 0.7946 |
| h14 | 4 | 0.6847 | [0.6923, 0.6929] | [0.6617, 0.7136] | 0.6927 |
| h15 | 7 | 0.7664 | [0.7594, 0.7761] | [0.7305, 0.7950] | 0.7659 |
| h15 | 8 | 0.7281 | [0.7247, 0.7405] | [0.6949, 0.7603] | 0.7309 |
| h16 | 8 | 0.7812 | [0.7760, 0.7760] | [0.7474, 0.7947] | 0.7760 |
| h16 | 9 | 0.7016 | [0.7023, 0.7023] | [0.6719, 0.7228] | 0.7023 |
| h17 | 1 | 0.9916 | [0.9849, 0.9914] | [0.9701, 0.9962] | 0.9894 |
| h17 | 2 | 0.5840 | [0.5715, 0.5951] | [0.5394, 0.6172] | 0.5853 |

### Lesart

**Was jetzt belegt ist**, synthetisch und nur für Familie F:

1. **Die Erinnerung steckt im Modul-Unterschieds-Modus.** Sie klingt mit μ_D = 1 − ℓ + ℓγ(1 − cN/(N−n)) ab. Binnenmodul-Unterschiede klingen mit μ_I ab, meist viel schneller. Der Gleichtaktmodus mit q kommt im Reizunterschied **gar nicht vor**: Das ist bewiesen (Symmetrie) und an 24 ungesehenen Kombinationen bestätigt.
2. **q ist keine Erinnerungsrate**, nur eine obere Grenze. Die naive q-Regel überschätzt die Dauer in jedem geprüften Fall, meist um ein Vielfaches.
3. **Abschottung hilft genau dann, wenn die Reize in verschiedenen Modulen ankommen** und das Ablesen den Modul-Unterschied sieht:
   - Liegen beide Eingänge im selben Modul, trägt nur μ_I, und die Spur ist nach wenigen Schritten weg (h02, h14, h17).
   - Werden nur Modulmittel abgelesen, sind Binnenmodul-Unterschiede unsichtbar (h08, h11).
   - Die Summe sieht nie etwas (h18–h23).

   Damit ist die Arbeitsteilung präzise: **Information innerhalb eines Moduls halten** heißt μ_D nahe 1, also kleines c. **Information zwischen Modulen austauschen** heißt großes c. Dieses c verkürzt genau diese Erinnerung. Ab c > (N−n)/N wird der Kopplungseigenwert λ_D negativ (anti-modular), und μ_D sinkt unter 1−ℓ (h10, h12). *Berichtigt nach Erratum 1, R3:* Ein Vorzeichenwechsel der Spur pro Schritt folgt daraus nicht; dafür braucht es μ_D < 0. Bei h10 und h12 ist μ_D > 0.
4. **Reizstärke und Rauschen** wirken nur logarithmisch auf die Dauer, über g/σ = ℓ·tanh(a)/σ. Die tanh-Sättigung deckelt den Reizgewinn.

**Was nicht behauptet wird:**
- nichts außerhalb von F: Kantenablation, Eingriffe nach dem Reiz, Hebb-angepasste oder ungleich große Module;
- keine biologische Aussage, kein Gewinner;
- die 24 Kombinationen sind eine Stichprobe (`numerical_sample`); allgemein gilt die Schranke (`analytic_argument`), nicht die Stichprobe;
- die Decoder-Schicht ist `numerical_sample` / `synthetic_only`.

**Einschränkung der Prüfstärke:** 10 der 24 Vorhersagen sind „keine Erinnerung über p\*“. Bei 9 davon ist die Trennung aus Symmetriegründen exakt 0, bei h07 liegt der monoton abklingende Modulmittel-Unterschied schon bei d = 0 unter der Schwelle (der Kern bestätigt für alle 10: bei keiner Pause ≥ p\*). Diese Fälle prüfen die Struktur (Messoperator, Symmetrie), aber kaum die Zahlenwerte. Die quantitative Last tragen die 14 Kombinationen mit Erinnerung.

### Mutationsprüfung

**37/37 erkannt**, mit 5 neuen Mutanten für M9b/M9c:
- Einfrieren ohne Prüfung auf „gesehen“;
- Integritätsprüfung aus;
- D nicht geprüft;
- Band ignoriert die Schranke;
- Decoder-Band offen.

Ein erster Mutant überlebte, `m9_seen_check_disabled`. Er war **äquivalent**, weil die strengere zweite Schicht denselben Fall abfängt. Die echte Lücke war, ob `build()` die Prüfung aufruft. Dafür gibt es jetzt einen neuen Test und einen umgezielten Mutanten.

## Followup-Review-Fix `astra-m8-m9-review` (R3, R4)

Die Prüfung liegt unter `D:/mandala/mandala-memory-results/astra-m8-m9-review/REVIEW.md` (Stand `e8b1f10`). Unabhängig bestätigt wurden:
- 207/207 Tests;
- eine separat programmierte Simulation: 24/24 Bänder, 23/23 Dauern;
- 28/28 Decoder-Prüfungen;
- Symmetrieargument, Fehlerrekursion und Commit-Reihenfolge.

Zu korrigieren waren **zwei Erklärungen, keine Rechnung**. Beide Gegenbeispiele habe ich zuerst unverändert mit dem Kern nachgerechnet; die Zahlen stimmen exakt.

| Befund | Korrektur | Regression (`tests/test_m9_erratum.py`) |
|---|---|---|
| **R3** „λ_D < 0 ⇒ Vorzeichenwechsel“ | Ein Wechsel pro Schritt braucht μ_D < 0. λ_D < 0 heißt nur anti-modulare Kopplung mit μ_D < 1−ℓ. | c = 0,8: λ_D = −0,16, μ_D = +0,42, Kontrast 0,1342624 … stets positiv. Positivkontrolle c = 1, ℓ = 1, γ = 0,95: μ_D = −0,475, alterniert. |
| **R4** „Bayes(0) < p\* ⇒ keine Erinnerung“ | D ist „keine“ genau dann, wenn **kein** d = 0…64 die Schwelle erreicht; first_passage ist eine eigene Größe. | Knoten n1, σ = 0,01: Bayes 0,5 → 0,879704 → 0,911444, D = 5, first_passage = None; die Vorhersage sagt [5, 5]. Alle 10 eingefrorenen „–“ bleiben bei jedem d unter p\*. |

- **Erratum:** [`docs/M9_ERRATUM_1.md`](docs/M9_ERRATUM_1.md). Die eingefrorene [`docs/M9_HERLEITUNG.md`](docs/M9_HERLEITUNG.md) bleibt **unverändert**; ihr Hash-Test ist weiter grün.
- **Im Erratum zusätzlich festgehalten:**
  - Gleitkomma-Auswertung der Schranke ≠ zertifizierte Intervallarithmetik;
  - das Decoder-Band ist kein gemeinsames Konfidenzniveau;
  - „Modul B löschen“ verändert die Aufgabe;
  - die Commit-Folge belegt die versionierte Reihenfolge.
- **Weitere berichtigte Stellen:** Erläuterung von `memory_duration` in `lab.py`, Zusammenfassung in `lab.js` („keine: bei keiner Pause 0–64 …“) und die Roadmap-Stellen zu „–“ und zum anti-modularen Bereich.

## Lokale Integration in `main` (2026-10-03)

**Auftrag:** `D:/mandala/AnschlussPromtAstra.txt`, Teil 1. Lokale Merges waren ausdrücklich autorisiert; kein Push.

**Bericht:** `D:/mandala/mandala-memory-results/integration-2026-10-03/INTEGRATIONSBERICHT.md`. Er enthält alle Prüfdaten der Integration im selben Ordner.

| Repo | Ausgangsstand `main` (Tag) | geprüfter Stand (Tag) | `main` nach Integration |
|---|---|---|---|
| Feldtheorie | `0e46ec8` (`backup/main-vor-mandala-memory-2026-10-03`) | `a1e61cd` (`reviewed/mandala-memory-a1e61cd`) | `061adba` |
| unified-mandala | `a7605284` (`backup/main-vor-memory-lab-2026-10-03`) | `515951be` (`reviewed/memory-lab-515951b`) | `1e310caa` |

Gefundene und behobene Integrationsfehler (auf diesem Branch, dann erneut gemergt):
- **Repo-weites pytest:** Die Feldtheorie-CI ruft `pytest` ohne Pfad auf. In fremder Umgebung scheiterten dadurch 111/211 Labortests. Jetzt prüft `tests/conftest.py` die Laborumgebung (Windows, D:/mandala, SCF ≥ 0.42). Fehlt sie, wird der Ordner nicht gesammelt, und der Grund wird gemeldet.
- **Trilayer** (Feldtheorie `AGENTS.md`): Die M9-Vorhersagen bekamen einen YAML- und einen MD-Zwilling. Das JSON ist unverändert; die Gleichheit prüft ein Test.
- **Getrennte Prüfablage:** `serve.py --explore-dir` lenkt die explorativen Protokolle in einen eigenen Ordner, nie auf C:.
- **Browser-Smoke-Test** `tools/browser_smoke.py`: Er klickt beide Ansichten in Headless-Edge über DevTools durch (stdlib, keine Installation). Ergebnis gegen beide `main`-Stände: 16/16.
- **Umgebung:** PyYAML 6.0.3 in der Labor-Umgebung auf D: ergänzt, für den Zwillingstest.

## Review `ASTRA_REVIEW_M10_PLAN` (R5–R8)

**Review:** `D:/mandala/mandala-memory-results/integration-2026-10-03/ASTRA_REVIEW_M10_PLAN.md`. Ergebnis: M10 vorerst nicht einfrieren; keine Forschungsrechnung, kein Push.

### R5–R7: Plan, Fassung 2

| Punkt | Umsetzung |
|---|---|
| **R5** Bayes-Aussagen ≠ trainierte Decoder | Zwei getrennte Messebenen:<br>• **Ebene B** mit expliziter Likelihood. Die Klassenverteilungen sind exakt Mischungen aus 27 Normalverteilungen, auch für tanh; Bayes-Trefferquote als E[max P(s\|y)] mit ausgewiesenem Monte-Carlo-Fehler.<br>• **Ebene D** mit trainierten Decodern, getrennt berichtet.<br>A1 wird als Zustandsidentität geprüft, A2 über die V₋-Projektion, A3 als analytisches Resultat mit festgelegter numerischer Gegenprobe. H-N ist für tanh ausdrücklich nur Hypothese. |
| **R6** Ablesezeit | primär **d = 4 für beide Netze**; d = 6/3 bei ähnlicher Ausgangsleistung nur beschreibend; normierte Interferenz zusätzlich |
| **R7** Inferenz | Nur H-N und H-F+ sind bestätigend, auf Ebene B: einseitig, Mindesteffekt δ = 0,01, Z aus Monte-Carlo-Standardfehlern, Holm α = 0,05. Berichtet werden adjustierte p-Werte und unadjustierte Intervalle, als solche benannt. H-F (kein TOST), Ebene D, Aktualisieren und Zielkonflikt bleiben beschreibend. Kein Sign-Flip-Test. |

**Neu offen:** O9 (δ), O10 (n_MC), O11 (Ebene D bestätigend?).

### R8: Teststufen statt Ordner-Ausschluss

`tests/conftest.py` deklariert je Test, was er braucht; fehlt etwas, werden nur die betroffenen Tests mit eigenem Grund übersprungen. Abhängigkeiten in `requirements-lab.txt`.

| Stufe | Tests |
|---|---|
| portabel | 101 |
| `scf` | 109 |
| `lab_integration` | 13 |
| `git_history` | 1 |

**Pflicht-Labortestlauf** `MANDALA_LAB_REQUIRED=1`: Jeder Skip und jede fehlende Voraussetzung lässt den Lauf scheitern.

**So wurde die Einteilung ermittelt, nicht geschätzt:**
- **Linux ohne SCF:** WSL-Ubuntu, Python 3.12, Linux-Wheels auf D: entpackt, nichts auf C: installiert. Die 52 Testfunktionen, die genau am fehlenden Modul scheitern, bilden die `scf`-Stufe. Alle 106 + 4 Fehlschläge sind diesem Grund zugeordnet; die 4 indirekten kamen über den Runner, der den Importfehler je Seed abfängt, und über den Nachrechen-Test (siehe unten).
- **Feste Scratch-Ordner auf D:** Tests mit festen D:-Scratch-Ordnern nutzen jetzt `tests/_paths.py`: im Labor unverändert `D:/mandala/.tmp/…`, sonst System-Temp. Unter POSIX hätte `"D:/…"` still einen relativen Ordner `D:` angelegt; die Sitzung prüft das jetzt und schlägt sonst fehl.

**Dabei gefundene echte Portabilitätsfehler (behoben):**
1. **C:-Sperre:** Sie prüfte `Path(...).drive`. Unter POSIX ist das für `"C:/x"` leer; der Runner hätte dort einen relativen Ordner `C:` beschrieben. Jetzt prüft `core.is_drive_c` die rohe Schreibweise mit Windows-Regeln vor dem Auflösen (Runner, M9-Auswertung, Dienst). Abgesichert durch einen neuen Test und den Mutanten `c_drive_guard_not_portable`.
2. **Nachrechnen der eingefrorenen Vorhersagen** verlangte Bit-Gleichheit. Unter Linux wich ein Wert in der letzten Stelle ab (0,9360274055191848 statt 0,936027405519185; libm/BLAS). Jetzt gilt: Struktur, ganze Zahlen (alle D-Werte und Intervalle), Wahrheitswerte und None exakt; Gleitkommazahlen relativ 1e‑12. Die eingefrorene **Datei** bleibt per SHA-256 bitgenau geschützt; Bit-Gleichheit gilt auf der Einfrier-Plattform.

**Ergebnisse:**

| Lauf | Ergebnis |
|---|---|
| Linux ohne SCF | 101 bestanden, 123 übersprungen (mit Gründen), kein streunender Ordner |
| Linux mit SCF 0.42 | 210 bestanden, 14 übersprungen (Labor/Historie) |
| Windows-Labor, Pflichtlauf | **224 bestanden, 0 übersprungen** |
| Pflichtmodus mit SCF 0.41 | Abbruch mit klarer Meldung (Gegenprobe) |

**Mutationsprüfung:** 38/38.

**Verbleibende Lücke (ehrlich):** Die Feldtheorie-CI installiert weder SCF noch PyYAML, und ein Workflow für die Laborstufen wurde nicht angelegt. Auf GitHub laufen deshalb nur portable Tests. Für alles Weitere ist das fehlende CI-Abdeckung; verbindlich ist der dokumentierte Pflicht-Labortestlauf.

## M10: Implementierung, Laufzeitcheck, Freeze-Vorbereitung

**Freigabe:** `ASTRA_FOLLOWUP_R5_R8.md`. Vorher wurde R5–R8 lokal integriert (Feldtheorie `main` = `15a24d85af`, Tag `reviewed/mandala-memory-485bfc0`).

**Entscheidungen:**
- O9: δ = 0,01;
- O10: n_MC = 2·10⁶ (bestätigt durch den Laufzeitcheck unten);
- O11: Ebene D beschreibend.

### Code

| Datei | Inhalt |
|---|---|
| [`m10_task.py`](m10_task.py) | 27 Fenstermuster mit exakten Wahrscheinlichkeiten (Brüche); Episodenablauf (Fenster W = 3 direkt vor x_(d+1)); Netze mit vier Eingangsspalten (A, B, X, Y); Zustände z(s, π) aus dem getesteten Kern; A1 (Zustandsidentität x_B = P x_A je Muster) und A2 strukturell (‖P₋ r(π)‖) |
| [`m10_bayes.py`](m10_bayes.py) | Ebene B: allgemeiner Schätzer E[max_c P(c\|y)] für endliche Gauß-Mischungen. Numerik: log-sum-exp, zentrierte Distanzen auf 0 abgeschnitten, Blöcke mit Mittel/M2 nach Chan, SE = √(var/n), SE = 0 wird als 0 berichtet, nicht-endlich führt zum Abbruch. Mischungen: **Bewahren** p(y\|s) = Σ_π P(π) N(z(s,π)); **Aktualisieren** p(y\|L=l) = Σ_s ½ Σ_{π: last=l} P(π)/P(last=l) N(z(s,π)) mit P(last = X) = P(last = Y) = 7/16; **K0** analytisch, Aktualisieren = N/A (`None`). |
| [`m10_decoders.py`](m10_decoders.py) | Ebene D: Episoden aus Strömen (Seed, Art, Rolle, Pause), gleich über Netze und Bedingungen (gepaart), getrennt über Rollen; jedes Muster einmal für A und einmal für B. Leckprüfung (Muster-Häufigkeiten je Klasse gleich), Trennungsprüfung (SCF `check_split` plus disjunkte Ströme), Nearest-Mean und LDA mit Ledoit-Wolf (eigene Umsetzung, vektorisiert) |
| [`m10_run.py`](m10_run.py) | Modi `dev`/`smoke`/`research`. **`research` ist gesperrt**, solange `FROZEN_PROTOCOL_SHA256` = `None` ist, und bei Abweichung des Protokolls; keine Overrides in `research`; exklusive Ablage, C: verboten |
| [`m10_evaluate.py`](m10_evaluate.py) | Diagnosen mit Alarmregel, Interferenz, bestätigende Familie (Z, SE = 0-Regel, Holm, Wortregeln), **Freigabe-Gate** (`release`: research + vollständig + eingefrorenes Protokoll + keine Overrides), Ebene D beschreibend (Bootstrap über ganze Seeds) |
| [`protocol/m10_protokoll.json`](protocol/m10_protokoll.json) | Protokoll-Kandidat mit YAML- und MD-Zwilling. Enthält Astras drei Präzisierungen: Likelihood der Aufgabe „letzter Kanal“ mit K0 = N/A; 4-SE als **Diagnosealarm** mit fester Zahl der Gegenproben (15 + 18), ohne Wiederholen bis zum Bestehen; Numerik, Ströme und Fehlerquellen getrennt benannt. |

### Für die gezielte Prüfung

| Prüfpunkt | Stelle |
|---|---|
| Mischungsgewichte | `m10_bayes.preserve_mixtures`, `update_mixtures`; Tests `test_update_mixture_conditions_on_the_last_channel`, `test_patterns_and_last_channel_probabilities` |
| Standardfehler | `m10_bayes._merge`, `bayes_accuracy_mc`; Tests gegen geschlossene Formel und 1-D-Quadratur, SE = 0 |
| Zufallsströme | `m10_run.level_b` (`stream("m10bayes", base_seed, task, net, nl, cond, d)`), `m10_decoders.make_episodes` (`stream("m10", seed, kind, role, d)`) |
| Freigabe-Gate | `m10_run.mode_settings`/`run`, `m10_evaluate.release`; Tests `test_research_is_blocked_until_frozen`, `test_release_gate` |

### Tests und Mutationen

- **Neu:** [`tests/test_m10_portable.py`](tests/test_m10_portable.py) mit 15 Testfällen (numpy) und [`tests/test_m10_kernel.py`](tests/test_m10_kernel.py) mit 15 Testfällen (Kern/SCF), zusammen 30; dazu 2 Trilayer-Fälle; **nur Entwicklungseinstellungen** (Ablenkorte 9/11 und 2/6, a = 0,9; Seeds 901–903).
- **Werkzeugprüfungen:**
  - Schätzer gegen Φ(‖Δ‖/2σ) im 1-Komponenten-Fall;
  - gegen eine 1-D-Trapez-Quadratur einer Zwei-Komponenten-Mischung;
  - zentrierte gegen direkte Distanzen.
- **Negativkontrollen:**
  - klassenabhängige Ablenkung ⇒ Leckprüfung schlägt an;
  - Teststrom aus dem Trainingsstrom ⇒ Trennungsprüfung schlägt an;
  - nicht P-feste Orte ⇒ A1 und A2 schlagen an.
- **Pflicht-Labortestlauf:** **256/256**, 0 übersprungen.
- **Linux (WSL):** ohne SCF 118 bestanden, 138 übersprungen; mit SCF 242 bestanden, 14 übersprungen.
- **Gefunden unter Linux:** Der LDA-Test benutzte `data.balanced_accuracy` (SCF) und war deshalb nicht portabel; er rechnet sie jetzt selbst.
- **Mutationsprüfung: 51/51**, mit 13 neuen M10-Mutanten:
  - Fenster verschoben, log-sum-exp ohne Verschiebung;
  - Aktualisieren ohne Bedingung auf den letzten Kanal bzw. ohne Marginalisierung über s;
  - Holm ohne Abbruch, SE = 0-Regel falsch;
  - Forschung nicht gesperrt, Gate ignoriert Overrides;
  - LDA ohne Kovarianz, A1 ohne Permutation;
  - Leck- bzw. Trennungsprüfung blind;
  - K0-Aktualisieren nicht N/A.

### Laufzeitcheck (O10)

Entwicklungseinstellungen in voller Größe: n_MC = 2·10⁶, d ∈ {3, 4, 6}, 3 Seeds mit 1000/2000 Episoden. Ergebnis in `D:/mandala/mandala-memory-results/m10/dev-runtime-check/`.

**Gemessen:**
- 48 Ebene-B-Schätzungen in 298,6 s, also 6,2 s je Schätzung:

  | | tanh | linear |
  |---|---|---|
  | Bewahren | 6,34 s | 6,42 s |
  | Aktualisieren | 6,06 s | 6,06 s |

- Ebene D 1,5 s; Zustände und Diagnosen 1,7 s; Spitzen-RAM 158 MiB.
- Größter Monte-Carlo-**Standardfehler** 1,0·10⁻⁴. Er ist eine geschätzte Streuung, keine garantierte Schranke der tatsächlichen Abweichung.

**Hochgerechnet auf den Forschungsumfang** (72 Ebene-B-Schätzungen = 2 Netze × 2 Nichtlinearitäten × 3 Bedingungen × 3 Pausen × 2 Aufgaben; 20 Seeds, 4 Bedingungen):

| Teil | Sekunden |
|---|---|
| Ebene B, Bewahren | ≈ 230 |
| Ebene B, Aktualisieren | ≈ 218 |
| (davon tanh / lineare Kontrollen) | (≈ 223 / ≈ 225) |
| Ebene D | ≈ 13 |
| Zustände, Diagnosen | ≈ 2 |
| **Gesamt** | **≈ 463 s (7,7 min)** |

- RAM etwa 160 MiB, Ergebnis etwa 1 MB.
- **Bewertung:** Die harte Protokollgrenze von 1200 s wird mit Abstand eingehalten. Das Planziel „Ebene B < 5 min“ (Plan, Abschnitt 9) wird mit ≈ 7,5 min **verfehlt**. Das ist ein Zielwert, keine Grenze. Eine Anpassung von n_MC ist nach dieser Messung nicht nötig; die Entscheidung liegt vor dem Freeze bei der Nachprüfung.

### Freeze-Vorbereitung (noch nicht ausgeführt)

1. **Nachprüfung** des Codes (Mischungsgewichte, SE, Ströme, Gate) und des Protokoll-Kandidaten.
2. **Einfrier-Commit:** *(nach Review R9–R12 präzisiert)*
   - Status im Protokoll auf „frozen“ setzen und die Zwillinge neu erzeugen;
   - `FROZEN_PROTOCOL_SHA256` in `m10_run.py` auf den LF-normierten SHA-256 des Protokolls setzen;
   - `protocol/m10_freeze.json` schreiben: Protokoll-Hash, **geprüfter Code-Commit** und SHA-256 jeder M10-Codedatei (`m10_run.CODE_FILES`);
   - Smoke **und** Research verlangen genau diesen Zustand;
   - Pflichtlauf und Mutationsprüfung.
3. **Smoke-Lauf** (`--mode smoke`, Smoke-Seeds, n_MC = 10⁵): nur Laufzeit und Format.
4. **Forschungslauf** (`--mode research`) einmal, dann `m10_evaluate`. Abweichungen werden berichtet, nicht repariert.

## Review-Fix `astra-m10-review` (R9–R12)

**Review:** `D:/mandala/mandala-memory-results/astra-m10-review/REVIEW.md` (Stand `66c5e81`). Der numerische Kern war schlüssig (Mischungsgewichte, Standardfehler, Ströme); vier Kontrolllücken mussten vor dem Freeze geschlossen werden. Astras Gegenbeispiele habe ich **zuerst unverändert reproduziert**, als Kopie ihres Skripts mit Ausgabe in meinen Temp-Ordner, ihr Ordner bleibt unberührt:
- leeres Ergebnis → `released: true`;
- falsche Leckprüfung → `status: complete`, `failures: []`;
- Smoke vor dem Freeze → Einstellungen mit Forschungsbedingungen.

| Befund | Korrektur | Regression (`tests/test_m10_controls.py`) |
|---|---|---|
| **R9** Gate prüft keine Vollständigkeit | `m10_evaluate.completeness`: Das erwartete Raster wird **nur aus dem Protokoll** abgeleitet, nie aus den Metadaten des Ergebnisses. Geprüft werden Ebene B (Netz × Nichtlinearität × Bedingung × Pause, je Aufgabe exaktes n_MC und Block, erwarteter Stromschlüssel, endliche Werte im Bereich, K0 mit Aktualisieren = N/A), Ebene D (Seed × Pause × Netz × Nichtlinearität × Bedingung, exakte n, erwartete Stromschlüssel je Rolle, Kontrollen, Aktualisieren-Zählung, endliche Werte), das Diagnoseraster sowie Pausen, n_MC und Seeds gegen das Protokoll. Fehlende, doppelte und zusätzliche Zeilen werden abgelehnt. Außerdem wird gegen den Code-Hash im Freeze-Datensatz geprüft. | Ein unabhängig gebautes, vollständiges synthetisches Forschungsergebnis wird freigegeben. **20 gezielte Verfälschungen** werden je mit ihrem Grund abgelehnt, darunter Astras leeres Ergebnis, entfernte, doppelte und zusätzliche Zeilen, doppelte Seeds, falsche n, fremde Ströme, NaN/Inf, K0-Aktualisieren, Overrides, Modus, protokollierter Fehler und veränderter Code. |
| **R10** Kontrollen ohne Konsequenz | Runner: Eine falsche Leck- oder Trennungsprüfung (`ControlFailure`) und unerwartete deterministische Diagnosen (`enforce_diagnostics`, vor Ebene B) führen zu `status: failed`. Die erwartete negative A1-Kontrolle (N bzw. Ndev im modularen Netz) zählt als „wie erwartet“. Das Gate prüft alle Kontrollen zusätzlich selbst. **Statistische 4-SE-Alarme** bleiben reine Berichte und sperren nicht. | Über den echten Runner: falsche Leckprüfung (Astras Gegenbeispiel), kaputte Trennungsprüfung, invertiertes A1, fehlschlagendes A2 ⇒ `failed`, keine Freigabe. Die erwartete Negativkontrolle lässt den Lauf vollständig. Gate: fehlgeschlagene Kontrollen in sonst vollständigen Daten ⇒ keine Freigabe. Ein A3-Alarm wird berichtet, die Freigabe bleibt. |
| **R11** Smoke vor dem Freeze | `require_frozen` gilt für Smoke **und** Research: Konstante gesetzt und gleich dem Protokoll, Freeze-Datensatz vorhanden mit gleichem Protokoll-Hash, geprüftem Code-Commit und gleichen Code-Hashes. Vor dem Freeze ist nur `dev` möglich. | Für beide Modi: nicht eingefroren, falscher Hash, fehlender Datensatz und veränderter Code werden abgelehnt; gültiger Freeze wird angenommen; Overrides sind verboten. |
| **R12** 1200 s nicht durchgesetzt | Die Grenze ist **verstrichene Zeit** (`time.monotonic`) des Laufs, 1200 s. Sie wird vor jedem Monte-Carlo-Block, jeder Zustandsberechnung und jeder Ebene-D-Einheit geprüft; die größte Überschreitung ist eine Einheit (gemessen etwa 0,16 s je Block). Bei Überschreitung gilt `aborted_timeout`, das Teilergebnis wird exklusiv gespeichert und nie freigegeben. RAM- und Dateigrößenbudget sind im Protokoll als **„geplant, nicht durchgesetzt; gemessen und berichtet“** gekennzeichnet. | Mit kontrollierter Uhr bricht der Lauf **innerhalb** der Monte-Carlo-Schleife ab, die Datei ist gespeichert, es gibt keine Freigabe, und Überschreiben ist unmöglich. Die Frist wird vor jedem Block geprüft (Überschreitung ≤ 1 Block). Die Protokollangaben sind eindeutig. |

**Ergebnisse:**

| Prüfung | Ergebnis |
|---|---|
| Astras Gegenbeispiele erneut | leeres Ergebnis ⇒ nicht freigegeben (7 Gründe); falsche Leckprüfung ⇒ `failed` mit `ControlFailure`; Smoke vor dem Freeze ⇒ verweigert |
| Pflicht-Labortestlauf | **287/287**, 0 übersprungen |
| Linux ohne SCF | 143 bestanden, 144 übersprungen |
| Linux mit SCF | 273 bestanden, 14 übersprungen |

**Mutationsprüfung:** siehe Commit-Nachricht. Neu sind 12 Mutanten zur **Durchsetzung**:
- Gate ohne Vollständigkeit, ohne Stromprüfung, ohne Duplikatprüfung, ohne Code-Hash, ohne Kontrollprüfung;
- Runner ignoriert die Leckprüfung, Diagnosen nicht durchgesetzt;
- Smoke nicht gesperrt, Code-Hash nicht geprüft;
- Monte Carlo ohne Frist, Blockschleife ohne Prüfung, Timeout als vollständig gezählt.

Die zwei alten Mutanten für Sperre und Overrides wurden auf die neuen Stellen und Tests umgezielt.

## Followup-Review-Fix `FOLLOWUP_R9_R12` (Restlücken vor dem Freeze)

**Nachprüfung:** `D:/mandala/mandala-memory-results/astra-m10-review/FOLLOWUP_R9_R12.md` (Stand `99b2c6b`). R11 ist geschlossen, und die Fehlerbehandlung im Runner bestätigt. Astras vier Gate-Gegenbeispiele habe ich zuerst **unverändert reproduziert** (alle `released: true`).

| Lücke | Korrektur in `m10_evaluate.completeness` bzw. `m10_run` |
|---|---|
| K0 mit NaN-Standardfehler | K0 verlangt einen endlichen Schätzwert in [½, 1] und **SE = 0 exakt**, denn K0 ist analytisch. |
| unvollständige Leckprüfungsfelder | Verlangt wird **genau** die Menge {`ids_disjoint`, `streams_disjoint`, `train_identical_pattern_counts`, `test_identical_pattern_counts`}, jeder Wert `is True`. Fehlende, zusätzliche oder nur „wahrheitsähnliche“ Werte werden abgelehnt. |
| ausgelassene A2-Prüfung | Symmetrie und A2-Pflicht werden aus **Protokoll, Netz und Bedingung** abgeleitet (`swap_permutation`), nicht aus dem Ergebnisfeld `p_fixed`. Verlangt werden die vollständige gemessene A1-Struktur (endliche Abweichung, Protokolltoleranz, `holds` passend zum Messwert, `p_fixed`/`A1_expected` gleich der abgeleiteten Symmetrie, `A1_as_expected`) und für jede Pflichtzeile das vollständige A2 (endlicher Messwert ≤ Protokolltoleranz). A2 an einer Nicht-Pflichtzeile ist unzulässig. |
| null Trainingsepisoden beim Aktualisieren | Die Zahl der Muster ohne Puls je (Seed, Pause, Rolle) wird **ohne Netzdynamik** aus den festen Musterströmen rekonstruiert. Trainings-, Test- und Ausschlusszahlen beider Aufgaben müssen exakt stimmen (ganze Zahlen, Bewahren ohne Ausschluss); Decoderwerte müssen endlich und in [0, 1] liegen. |
| Frist nach der letzten Einheit / in den Diagnosen | Die Frist wird jetzt auch **je Diagnose-Einheit** und **unmittelbar vor `complete`** geprüft. Die Beschreibung ist präzisiert: kooperative Prüfung, Überschreitung höchstens eine Einheit; die gemessenen etwa 0,16 s je Block sind eine Beobachtung, keine garantierte Schranke (Code-Doku und Protokoll). |

**Tests** (`tests/test_m10_controls.py`):
- **Synthetischer Referenzdatensatz:** Er hat jetzt **alle Pflichtfelder**. Die Episodenzahlen kommen aus dem echten Episodengenerator; damit ist auch belegt, dass die Rekonstruktion im Gate mit dem Generator übereinstimmt. Diagnosen haben die vollständige A1/A2-Messstruktur. Ein künstlich unvollständiger Diagnoseblock dient nicht mehr als positive Referenz.
- **16 neue Verfälschungen**, jede mit ihrem Grund abgelehnt:
  - Astras vier Fälle;
  - K0-SE ≠ 0;
  - Zusatzfeld bzw. Wert `1` statt `True` in den Kontrollen;
  - A2 mit fremder Toleranz, A2 an einer Nicht-Pflichtzeile;
  - fehlende A1-Messung, `holds` widersprüchlich zum Messwert, falsch behauptetes `p_fixed`;
  - um ein Paar verschobene Zählung;
  - Ausschluss beim Bewahren, Trefferquote > 1, n als Gleitkommazahl.
- **Frist mit kontrollierter Uhr:** Eine Überschreitung **genau in der letzten Decoder-Einheit** ergibt `aborted_timeout`, nicht `complete`. Eine Überschreitung **in den Diagnosen** bricht dort ab. Der Abbruch in der Monte-Carlo-Schleife ist weiter belegt.
- **Astras Gegenbeispiele erneut:** alle vier `released: false` mit präzisem Grund.

**Ergebnisse:**

| Prüfung | Ergebnis |
|---|---|
| Pflicht-Labortestlauf | **305/305**, 0 übersprungen |
| Linux ohne SCF | 159 bestanden, 146 übersprungen |
| Linux mit SCF | 291 bestanden, 14 übersprungen |
| Mutationsprüfung | siehe Commit-Nachricht, 6 neue Mutanten (unvollständige Kontrollmenge, K0-SE ungeprüft, Aktualisieren-n ungeprüft, A2-Pflicht aus dem Ergebnis, letzte und Diagnose-Frist entfernt) |

## M10: Freeze, Smoke, Forschungsrechnung und Ergebnis

**Freigabe:** `D:/mandala/mandala-memory-results/astra-m10-review/ABSCHLUSSPRUEFUNG_6f2acfd.md`.

### Freeze

- **Commit `7b31300`** (Tag `m10-freeze`).
- **Änderungen gegenüber dem geprüften Stand `6f2acfd2a8a153c8f48bc50194cbcf651a510758`:**
  - Protokollstatus FROZEN; Hash danach berechnet: `84d2b523d5f4c7dc9acc8e91d1986d71306e9aedbd4f99ef74c35c5b2056c345`; Zwillinge neu erzeugt.
  - `FROZEN_PROTOCOL_SHA256` im Runner, die **einzige Codeänderung**; im Diff belegt.
  - `protocol/m10_freeze.json` mit Protokoll-Hash, geprüftem Code-Commit und den Code-Prüfsummen. Die Prüfsummen wurden **nach** dem Eintragen der Konstante berechnet.
  - Tests auf den eingefrorenen Zustand umgestellt; neuer Konsistenztest.
- **Prüfung:** Pflichtlauf 306/306. Freeze-Konsistenz in frischem Prozess geprüft: Konstante = Protokoll = Datensatz, Code-Prüfsummen gleich.

### Smoke

`D:/mandala/mandala-memory-results/m10/smoke/m10-smoke-20261003T225248-8cf17955.json`:
- vollständig in 25,7 s;
- alle deterministischen Kontrollen bestanden;
- als Smoke korrekt **nicht** freigegeben (eigene Ströme und Seeds, kleineres n_MC);
- keine Parameteränderung danach.

### Forschungsrechnung (einmalig)

**Dateien:**
- Ergebnis: `D:/mandala/mandala-memory-results/m10/research/m10-research-20261003T230058-47d41706.json`
- Auswertung (exklusiv): `….evaluation.json`
- Lesefassung: `report.txt`

**Lauf:**
- Status complete, keine Fehler.
- 473 s (Grenze 1200 s): Ebene B 461 s, Ebene D 10,5 s; Spitzen-RAM 158 MiB.
- **Freigabe-Gate: freigegeben** (vollständiges Raster, eingefrorenes Protokoll und Code, keine Overrides).
- **Deterministische Kontrollen:** A1 überall wie erwartet, inklusive Negativkontrolle N/modular; A2 strukturell hält überall.
- **Statistische Diagnosen:** 15 A2- und 18 A3-Gegenproben, **kein Alarm**.

### Bestätigende Familie (Ebene B, d = 4, tanh, δ = 0,01, Holm α = 0,05)

| Hypothese | Δ̂ | SE | p (Holm) | 95 % unadjustiert | Ergebnis |
|---|---|---|---|---|---|
| **H-N:** I_modular(N) − I_uniform(N) > δ | **0,0238** | 0,00012 | < 10⁻¹⁰ | [0,0235; 0,0240] | **bestätigt** |
| **H-F+:** I_uniform(F+) − I_modular(F+) > δ | −0,0001 | 0,00011 | 1 | [−0,0003; +0,0001] | **nicht bestätigt** (nicht „widerlegt“: das Intervall enthält 0) |

**Komponenten:**

| | Interferenz I | Bayes ohne → mit Ablenkung |
|---|---|---|
| modular N | 0,0236 | 0,9352 → 0,9116 |
| uniform N | −0,0002 | 0,6696 → 0,6697 |
| modular F+ | 0,0001 | – |
| uniform F+ | −0,0001 | – |

### Beschreibend: Ebene B über alle Pausen (Interferenz I = K0 − Bedingung, Bewahren)

| Netz | d | K0 | F | N | F+ | linear N |
|---|---|---|---|---|---|---|
| modular | 3 | 0,981 | +0,000 | **+0,019** | −0,000 | +0,011 |
| modular | 4 | 0,935 | −0,000 | **+0,024** | +0,000 | +0,013 |
| modular | 6 | 0,801 | +0,000 | **+0,019** | −0,000 | +0,010 |
| uniform | 3 | 0,828 | −0,000 | +0,000 | −0,000 | −0,000 |
| uniform | 4 | 0,670 | −0,000 | −0,000 | −0,000 | +0,000 |
| uniform | 6 | 0,538 | +0,000 | −0,000 | −0,000 | +0,000 |

- **Angeglichener Vergleich** (ähnliche Ausgangsleistung, verschiedenes Alter der Erinnerung): modular d = 6: I(N) = 0,019; uniform d = 3: I(N) = 0,000.
- **Normierte Interferenz bei d = 4:** modular N 0,054, uniform N ≈ 0.
- **Aktualisieren (Bayes):** in allen Bedingungen 0,989–1,000, also fast perfekt in beiden Netzen.

### Beschreibend: Ebene D (trainierte Decoder, 20 Seeds, Mittel [95 % Bootstrap], d = 4, tanh)

| Netz, Bedingung | Interferenz Nearest-Mean | Interferenz LDA (Ledoit-Wolf) | Aktualisieren (NM / LDA) |
|---|---|---|---|
| modular N | **0,299** [0,298; 0,300] | **0,158** [0,155; 0,160] | 0,991 / 0,991 |
| modular F | 0,002 | 0,001 | 0,988 / 0,985 |
| modular F+ | 0,007 | 0,001 | 0,999 / 0,996 |
| uniform N | 0,012 | 0,000 | 0,995 / 0,992 |
| uniform F | 0,020 | 0,001 | 0,996 / 0,993 |
| uniform F+ | 0,043 | 0,000 | 1,000 / 0,999 |

### Lesart (synthetische Modellstudie; nur diese zwei Netze und Parameter)

1. **Struktur bestimmt die Störbarkeit, und anders als „Modularität schützt“ vermuten ließe:**
   - Ablenkung **in den Eingangsmodulen** (N) stört das modulare Netz messbar; die Bayes-Trefferquote sinkt um 2,4 Prozentpunkte.
   - Das gleich budgetierte uniforme Netz stört sie **gar nicht**.
   - Das ist die von der Symmetrie (A2) vorhergesagte Asymmetrie: Für das uniforme Netz sind die Orte 1/5 symmetrisch zum Reizpaar, für das modulare nicht. Der lineare Zwilling zeigt dieselbe Richtung, schwächer (A3/A4).
2. **Ferne Ablenkung (F, F+) stört auf der Bayes-Ebene in keinem Netz**, auch nicht bei starker Sättigung (a = 1,8).
   - Die Zustandsidentität A1 hält exakt.
   - Die Sättigung ändert den Reizunterschied offenbar nicht messbar.
   - H-F+ (Dämpfung vs. direkte Wirkung) ist damit **nicht bestätigt**. Der vermutete nichtlineare Störweg tritt hier nicht auf.
3. **Information im Zustand ≠ ablesbare Information:**
   - Der Bayes-Verlust bei N modular ist nur 0,024.
   - Ein trainierter Nearest-Mean-Decoder verliert aber 0,30, LDA 0,16.
   - An symmetrischen Orten erzeugt der Nearest-Mean-Decoder sogar **Scheininterferenz** (bis 0,043), die LDA und Bayes nicht zeigen. Ursache ist anisotrope, von der Zielklasse unabhängige Ablenkstreuung, die ein isotroper Decoder nicht wegrechnet.
   - Ob ein Netz „vergisst“ oder nur „schwerer abzulesen ist“, hängt also vom Ablesenden ab.
4. **Bewahren und Aktualisieren:** Die letzte Ablenkung ist in beiden Netzen fast perfekt ablesbar. Einen Zielkonflikt behaupte ich nicht; er ist vorab als beschreibend festgelegt.
5. **Grenzen:**
   - zwei feste 12-Knoten-Netze, ein Parametersatz, Pulse in einem Fenster aus 3 Schritten;
   - die Unsicherheit ist Monte-Carlo-Unsicherheit über ein deterministisches Modell, keine Population von Netzen;
   - keine biologische und keine allgemeine KI-Aussage;
   - Ebene D ist decoderabhängig und nur beschreibend.
