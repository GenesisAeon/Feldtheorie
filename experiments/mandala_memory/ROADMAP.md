# Mandala-Gedächtnislabor: Roadmap (M0–M7)

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
- Die adaptive Membran speichert die Reizamplitude in θ. Die Spur zerfällt über die Pause, weil θ unter R = 0 gegen etwa 0,10 läuft.
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




