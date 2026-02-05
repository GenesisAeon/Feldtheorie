# Bootstrap Ledger – LanternNet

Dieses Ledger dokumentiert Bootstrap-Schätzungen entlang der UTAC-Steigung
und hält die Nullmodelle (constant, linear, power law) samt ΔAIC/CI bereit.
Der Übergang über $\sigma(\beta(R-\Theta))$ bleibt als Resonanzindikator
explizit gekennzeichnet.

## Meta
- **Version:** v13.0.0
- **Consent Protocol:** Sigillin consent gating + anonymization required
- **Updated:** 2026-02-05T14:44:41+00:00

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

## Kopplungen
- LanternNet Index: `status/lantern_net.*`
- Ordnungs-Sigillin: `feldtheorie_index.*`
- Empirische Evidenz: `data/`, `analysis/`, `docs/`
