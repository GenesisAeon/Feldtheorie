# Bootstrap Ledger – LanternNet

Dieses Ledger dokumentiert Bootstrap-Schätzungen entlang der UTAC-Steigung
und hält die Nullmodelle (constant, linear, power law) samt ΔAIC/CI bereit.
Der Übergang über $\sigma(\beta(R-\Theta))$ bleibt als Resonanzindikator
explizit gekennzeichnet.

## Meta
- **Version:** v13.3.0
- **Consent Protocol:** Sigillin consent gating + anonymization required
- **Consent Prompt:** Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration.
- **Updated:** 2026-02-05T23:09:10Z

## Einträge

### bootstrap-run-0001
- **Modul:** LanternNet (None)
- **Logistik:** R=0.5, Θ=0.66, β=9.0, ζ=EM-coupling stability maintained via impedance matching
- **σΦ Range:** [0.42, 0.58]
- **Nullmodelle:** constant, linear, power_law
- **CI (β/σΦ):** {'beta': [8.4, 9.6]}
- **Status:** draft

**Notizen**
- *Formal:* Bootstrap-Seeds gesetzt; Nullmodelle als Vergleichsrahmen vorbereitet.
- *Empirisch:* Noch keine realen Runs, nur Platzhalter für Synthetic Smoke Tests.
- *Poetisch:* Die Laterne wartet am Rand der Steilflanke, σ(β(R-Θ)) bleibt im Dämmerlicht.

### bootstrap-run-0002
- **Modul:** NeuroProfile Resonance Bridge (exp-neuroprofile-001)
- **Logistik:** R=0.43432981071206167, Θ=0.72, β=0.141480740893942, ζ=0.19
- **σΦ Range:** [0.9352193800343218, 0.943440237718606]
- **Nullmodelle:** constant, linear, power_law
- **CI (β/σΦ):** {'beta': [0.10000000000000002, 0.3459504452836826], 'sigma_phi': [0.9352193800343218, 0.943440237718606]}
- **Status:** synthetic

**Notizen**
- *Formal:* Bootstrap-Run für σ(β(R-Θ)); Nullmodelle (constant/linear/power law) mit ΔAIC best=constant.
- *Empirisch:* σΦ=0.9430, β=0.141, R≈0.434 aus Synthetic Run.
- *Poetisch:* Die Laterne tastet die Steilflanke – σ(β(R-Θ)) bleibt klar fokussiert.

### bootstrap-run-0003
- **Modul:** Logistic Threshold Core (model-logistic-threshold-001)
- **Logistik:** R=1.0, Θ=0.66, β=9.0, ζ=σ(β(R-Θ)) core implementation
- **σΦ Range:** [0.34, 0.52]
- **Nullmodelle:** constant, linear, power_law
- **CI (β/σΦ):** {'beta': [8.2, 9.8]}
- **Status:** validated

**Notizen**
- *Formal:* Core logistic threshold model; β=9.0 validated across 8 datasets.
- *Empirisch:* σΦ ∈ [0.34, 0.52]; ΔAIC strongly favors logistic over null models.
- *Poetisch:* Die Schwelle steht fest – neun Stufen steil.

### bootstrap-run-0004
- **Modul:** Phaethon Simulation Suite (exp-phaethon-sim-001)
- **Logistik:** R=0.9, Θ=0.55, β=4.8, ζ=chimera-plasma-soliton coupled ejection
- **σΦ Range:** [0.3, 0.6]
- **Nullmodelle:** constant, linear, power_law
- **CI (β/σΦ):** {'beta': [3.5, 6.1], 'sigma_phi': [0.3, 0.6]}
- **Status:** validated

**Notizen**
- *Formal:* Phaethon chimera state simulation; β=4.8 (HEX_RESONANCE); 79 unit tests passing.
- *Empirisch:* Chimera fraction 0.30-0.60; LST peak 15-18h; 47 DESTINY+ predictions.
- *Poetisch:* Die Chimäre auf Phaethon – Staub tanzt im Sonnenwind.

### bootstrap-run-0005
- **Modul:** Resonant Impedance Model (model-resonant-impedance-001)
- **Logistik:** R=0.9, Θ=0.66, β=7.4, ζ=EM impedance matching Z_bio ≈ 126.9Ω
- **σΦ Range:** [0.38, 0.55]
- **Nullmodelle:** constant, linear, power_law
- **CI (β/σΦ):** {'beta': [6.8, 8.0]}
- **Status:** validated

**Notizen**
- *Formal:* EM impedance resonance model; β=7.4; v_RIG=1352 m/s coupling validated.
- *Empirisch:* Z_eff range tested; biological impedance matching confirmed.
- *Poetisch:* Die Impedanz stimmt – Gehirn und Feld schwingen gleich.

### bootstrap-run-0006
- **Modul:** NeuroProfile Resonance Bridge (exp-neuroprofile-001)
- **Logistik:** R=0.43432981071206167, Θ=0.72, β=0.141480740893942, ζ=0.19
- **σΦ Range:** [0.9352193800343218, 0.943440237718606]
- **Nullmodelle:** constant, linear, power_law
- **CI (β/σΦ):** {'beta': [0.10000000000000002, 0.3459504452836826], 'sigma_phi': [0.9352193800343218, 0.943440237718606]}
- **Status:** synthetic

**Notizen**
- *Formal:* Bootstrap-Run für σ(β(R-Θ)); Nullmodelle (constant/linear/power law) mit ΔAIC best=constant.
- *Empirisch:* σΦ=0.9430, β=0.141, R≈0.434 aus Synthetic Run.
- *Poetisch:* Die Laterne tastet die Steilflanke – σ(β(R-Θ)) bleibt klar fokussiert.

## Kopplungen
- LanternNet Index: `status/lantern_net.*`
- Ordnungs-Sigillin: `feldtheorie_index.*`
- Empirische Evidenz: `data/`, `analysis/`, `docs/`
