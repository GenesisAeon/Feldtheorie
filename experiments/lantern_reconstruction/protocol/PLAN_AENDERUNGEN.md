# Dokumentierte Planänderungen vor dem Freeze

Trilayer: [`plan_changes.json`](plan_changes.json) (maßgeblich), [`plan_changes.yaml`](plan_changes.yaml), diese Erzählung. Die Plandatei selbst ([Version 2.0](../reference/review_package_2026-10-07/LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md)) bleibt unverändert.

## AE-01 – Lantern-Differentialgleichung mit geprüftem RK4-Verfahren (2026-10-08)

**Entscheidung:** Johann und Astra; umgesetzt von Claude.

**Geändert:** Die Studie integriert die rauschfreie Lantern-Differentialgleichung mit dem klassischen **Runge-Kutta-Verfahren vierter Ordnung** (`dynamics.integrate_rk4`), bei dt = 0,02. Gleichung und geprüfte Drift sind dieselben wie im Euler-Pfad.

**Bisher:** Euler mit dt = 0,02, nur nach einem Konvergenznachweis (Plan § 6 und § 10).

**Grund:** Euler hat das ODE-Gate (≤ 0,005 rad) über das vorab festgelegte 32-Fälle-Panel **nicht bestanden**. Dieser Fehlschlag bleibt dokumentiert und durch einen Test festgehalten. RK4 besteht auf dem **unveränderten** Panel deutlich:

| Verfahren | dt = 0,02 | dt = 0,01 | dt = 0,005 | Ordnung |
|---|---|---|---|---|
| Euler | 0,1165 | 0,0606 | 0,0309 | 1 |
| RK4 | **3,2·10⁻⁷** | 2,1·10⁻⁸ | 1,4·10⁻⁹ | 4 |

**Euler-Pfad:** Er bleibt unverändert, ebenso sein Originaläquivalenztest (1,6·10⁻¹⁴). RK4 muss die diskreten Schritte des Original-Euler **nicht** nachbilden.

**Laufzeit** (256 Episoden, t = 10, dieser Rechner):

| Verfahren | dt | Laufzeit | Fehler |
|---|---|---|---|
| Euler | 0,02 | 2,5 s | 0,117 |
| Euler | 0,005 | 10,0 s | 0,031 |
| Euler | 0,00125 | 39,2 s | ≈ 0,007, besteht noch nicht |
| RK4 | 0,02 | 9,2 s | 3,2·10⁻⁷ |

RK4 kostet pro Schritt etwa das 3,7-Fache. Für die geforderte Genauigkeit ist es aber geschätzt etwa 6-mal günstiger als ein hinreichend kleiner Euler-Schritt.

**Prüfungen für RK4:**
- unverändertes Panel und die Lehrbuchformel des Schritts;
- Zwei-Knoten-Lösung mit vierter Ordnung, freie Drift, Zeitreskalierung, Ferntransfer und uniformer Vollgraph;
- Permutation und Rotation, unveränderte Eingaben, kein globaler RNG;
- Batch-Unabhängigkeit, auch für Euler;
- Abweisung ungültiger Eingaben.

**Offen:** Die Prüfung der **Decoderkennzahländerung ≤ 0,01** (zweiter Teil von Plan 10.2) bleibt bis LR4 offen. Ein bestandenes Zustandsgate schließt sie nicht automatisch.
