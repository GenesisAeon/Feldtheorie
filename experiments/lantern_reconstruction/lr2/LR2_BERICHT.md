# LR2 – Numerischer Kern (Bericht)

Trilayer: [`lr2_status.json`](lr2_status.json) (maßgeblich), [`lr2_status.yaml`](lr2_status.yaml), dieser Bericht. Referenzdaten: [`artifacts/lr2_reference/`](../artifacts/lr2_reference/).

## Gebaut

| Modul | Inhalt |
|---|---|
| [`dynamics.py`](../dynamics.py) | gebatchte, rauschfreie Drift in Differenzform θ_j − θ_i; Euler-Schritt mit dem Original-Wrap; strenge Eingangsprüfung (negative Kopplungen werden **abgewiesen**, nicht abgeschnitten); **keine** Zufallsquelle |
| [`linear_diagnostics.py`](../linear_diagnostics.py) | L, Schreibmatrix E, Differenzoperator D_O, H(t) = D_O·e^{−gLt}·aE, R = σ²(I + 11ᵀ), weiß gemachte Singulärwerte, Fisher-Matrix (nur das lineare Modell) |
| [`legacy_probe.py`](../legacy_probe.py) | neuer Worker-Modus: der **originale** `PhaseEvolver.evolve_phases` in einem separaten Prozess |
| [`tools/lr2_make_reference.py`](../tools/lr2_make_reference.py) | deterministische Entwicklungs-Referenzdaten, exklusiv geschrieben; Datei-Hashes zusätzlich im Testcode gepinnt |

## Gates

| Gate | Ergebnis |
|---|---|
| **Originaläquivalenz** (Plan 10.1: ≥ 100 Zustände, 500 Schritte, Größen 2–34, Nullmatrix, ≤ 1e-12) | ✅ **1,6·10⁻¹⁴** über 100 Fälle; dazu ein Live-Lauf mit 3 neuen Fällen in einem frischen Legacy-Prozess |
| **ODE-Genauigkeit** (Plan 10.2: 32 Fälle, bis t = 10, dt/2, dt/4, ≤ 0,005 rad) | ❌ **nicht bestanden** über das vorab festgelegte Gesamtpanel: 0,117 (dt 0,02), 0,061 (0,01), 0,031 (0,005); erste Ordnung |
| **Analytische Orakel** | ✅ Zwei Knoten (δ(1,3) = 0,0656648863608956), freie Drift exakt, Zeitreskalierung, Ferntransfer (Maximum bei 0,6232…, Verstärkung 0,2875…, nichtlinear bei kleiner Amplitude innerhalb 0,2 %), uniformer Vollgraph mit exakt leeren unbeschriebenen Ausgängen |
| **Strukturgates** | ✅ gemeinsame Permutation, globale Rotation, Achsenrichtung der Kopplung, Eingaben unverändert, kein globaler RNG, Abweisung ungültiger Eingaben, Zeitraster 0/25/50/100/150/250/500 Schritte, kein Legacy-Import und kein `evolve_network` im Laborcode |

### Offenes Gate LR2-G1: ODE-Genauigkeit

Die Referenz ist belastbar: DOP853, unabhängig gegengeprüft mit Radau bis 10⁻⁸. Das Panel stand **vor** dem Lauf fest und bleibt unverändert.

| Fallgruppe | größter Fehler bei dt = 0,02 |
|---|---|
| Lantern-Matrix, Studien-g, Start nach Studiendesign | **1,6·10⁻³** |
| Lantern-Matrix, 5·g | 2,6·10⁻³ |
| dicht, 34 Knoten, g = 0,03 | 1,2·10⁻³ |
| uniform, 8 Knoten | 2,2·10⁻³ |
| zufällige Startphasen auf stark gekoppelten Zufallsgraphen (g·max. Zeilensumme 3,4–4,8) und zwei Knoten mit g = 2 | **bis 0,117** |

**Entscheidung vor dem Freeze (LR6), Möglichkeiten:**
1. Gate-Panel auf das Studienregime und Skalenvarianten begrenzen, begründet und von Reviewer:innen freigegeben; das Gesamtpanel wird weiter berichtet.
2. Kleineres dt für die Studie. Der Aufwand wächst etwa mit 1/dt, und dt = 0,005 besteht das Gesamtpanel immer noch nicht.
3. Ein anderes Integrationsverfahren. Es wiche vom Original-Euler ab und bräuchte ein eigenes Äquivalenzargument.

Der zweite Teil von 10.2 (Änderung der Decoderkennzahl ≤ 0,01) braucht den Decoder und folgt in LR4. Ein Test (`test_ode_gate_open_full_panel_fails_and_euler_is_first_order`) hält den **nicht bestandenen** Stand fest, damit er nicht stillschweigend als erfüllt gilt.

## Beobachtungen

- **LR2-B1:**
  - Der reguläre Paketimport `v9_alpha.models` scheitert in der Laborumgebung: `__init__` lädt `sensorium`, und das braucht **pandas**, das nicht installiert ist.
  - Der Worker protokolliert das und führt die **unveränderte** Originaldatei `phase_dynamics.py` über ihren Pfad aus. Ihr Rohhash entspricht dem Inventar.
  - Keine Umgebung wurde verändert.
- **LR2-B2:** Der Originalkern verbraucht in jedem Fall den globalen RNG, auch bei Rauschen 0. Der Laborkern hat keine Zufallsquelle.
- **LR2-B3:** Der Originalkern ignoriert `C_ij ≤ 0` stillschweigend und akzeptiert asymmetrische Matrizen. Der Laborkern weist beides ausdrücklich ab. Ein Testfall mit einer versehentlich asymmetrischen Matrix hat das bestätigt.

## Prüfungen

- **Tests:** 76/76 über alle Lantern-Tests (`python -m pytest experiments/lantern_reconstruction/tests`).
- **Ad-hoc-Mutation:** 12/12 erkannt, darunter die Planmutanten 3 (Sinusargument umgekehrt) und 4 (g doppelt angewendet). Das vollständige Werkzeug folgt in LR5.

**Nicht enthalten:**
- die Tangentengleichung entlang heterogener Trajektorien (später, Plan 5.3);
- Episoden, die Aufgaben A und B, Decoder und Forschungsrechnung.

Originalmodule und M0–M12 sind unverändert; es gab keinen Freeze, keinen Merge und keinen Push.
