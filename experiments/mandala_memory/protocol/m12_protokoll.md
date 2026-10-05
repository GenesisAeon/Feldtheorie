# M12-Protokoll „Robustheit des festgehaltenen Auslesens“ (Narrativ-Zwilling)

Trilayer: `m12_protokoll.json` (maßgeblich), `m12_protokoll.yaml` (Strukturzwilling), diese Datei (Erzählung); erzeugt mit `tools/make_trilayer_twins.py`.

- **Status:** FROZEN 2026-10-05 after IMPLEMENTIERUNGSREVIEW_ba5dabc / NACHPRUEFUNG_15edfbd; reviewed code commit 15edfbd0d4f034c15af0cf8efd4cbb82270c198c; freeze record protocol/m12_freeze.json; references, models and evaluation follow as one-time phases
- **SHA-256 des JSON** (LF-normiert): `f3174a7d78d40aa548f257592208dab44e26437d35295fe2ff15c79a0b127c15`
- **Plan:** [`../docs/M12_PLAN_ROBUSTHEIT.md`](../docs/M12_PLAN_ROBUSTHEIT.md). Das Mandala ist unverändert: modular, tanh, d = 4, nahe Ablenkung.

**Training** nur in c₀ (Amplitude 0.6, σ = 0.02): n = 16000 Paare, LDA und MLP. Das MLP-Verfahren wird per Hash aus dem eingefrorenen M11-Protokoll übernommen. Forschungs-Seeds: 41201–41220.

**Testbedingungen** (eine Achse je Bedingung, gemeinsame Zufallszahlen, 100000 Testpaare je Seed):

| Bedingung | Ablenkungsamplitude | σ |
|---|---|---|
| c0 | 0.6 | 0.02 |
| a0.30 | 0.3 | 0.02 |
| a0.45 | 0.45 | 0.02 |
| a0.75 | 0.75 | 0.02 |
| a0.90 | 0.9 | 0.02 |
| s0.010 | 0.6 | 0.01 |
| s0.015 | 0.6 | 0.015 |
| s0.025 | 0.6 | 0.025 |
| s0.030 | 0.6 | 0.03 |

**Bestätigend:** Is the fixed MLP better than the fixed LDA by more than delta at the two raised endpoints? R-a bei a0.90, R-σ bei s0.030; δ = 0.01, Holm α = 0.05. Nicht getestet: Nichtunterlegenheit gegenüber c₀ und die Erhaltung der Vorteilsgröße.

**Diagnosen** D1–D4 sind statistische Gegenproben (4 SE) mit Alarmregel, keine Beweise; es gibt keine Wiederholung bis zum Bestehen. **Zerlegung**, Artefaktregeln, Phasen, Freigabe und Budget: siehe JSON.
