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
| M1 | Episodenoperator, linearer/Null-Referenzkern; K1–K9, SCF-Parität, Reset/Fortsetzung | ⬜ |
| M2 | Splits, Decoder, Rauschströme; Trennung, gepaarte Tests, Determinismus | ⬜ |
| M3 | Eingefrorenes/adaptives Netz, Ablationen; Gewichte nur im Training; Smoke + Ressourcen | ⬜ |
| M4 | SCF-Auswertung, Forschungsrunde (nach Hochrechnung) | ⬜ |
| M5 | Feldtheorie-Membranpilot (separat) | ⬜ |
| M6 | Lokale Mandala-Ansicht (unified-mandala `experiments/memory_lab/`) | ⬜ |
| M7 | Reproduzierbare Übergabe, Reviewpaket | ⬜ |

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
