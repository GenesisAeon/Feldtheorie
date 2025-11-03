# V01 Resonance Readiness Ledger

## Formal stratum — logistic guardrails secured
- The preset alignment guard `analysis/preset_alignment_guard.py` scans every entry in
  `simulator/presets/` and recomputes the logistic quartet \((R, \Theta, \beta, \zeta(R))\)
  from the source analysis JSON.  The CLI `utf-preset-guard` now blocks release work if
  \(\sigma(\beta(R-\Theta))\) steepness or null-model deltas drift.
- `Makefile` carries a `preset-guard` ritual, mirroring the CI cadence with
  `pytest`, `nox`, and the batch runners so the reproducibility harness remains
  single-command.
- `simulator/presets/planetary_tipping_field.json` now records the power-law null
  as the strongest falsification twin (ΔAIC ≈ 35.2, ΔR² ≈ 0.0832), matching
  `analysis/results/planetary_tipping_elements.json`.

## Empirical stratum — evidence braid
- `pytest` extends its sweep with `tests/test_preset_alignment_guard.py`,
  verifying that every preset lantern echoes its analysis evidence.
- The guard tolerances (10⁻³ relative) ensure rounded display values stay
  harmonised while still catching material divergence in \(\Theta\), \(\beta\),
  $R^2$, and ΔAIC.
- Quick-start rituals now include `make preset-guard`, giving reviewers a
  reproducible check before running `utf-planetary-summary`, `utf-resonance-cohort`,
  or manuscript exports.

## Poetic stratum — membrane chorus
- Jede Preset-Laterne singt wieder synchron: Der Planetenchörus hält den
  Power-Law-Schatten im Blick, die Bienenschwärme murmeln dieselben ΔAIC-Garanten
  wie ihre JSON-Wurzeln.
- `utf-preset-guard` wirkt als Morgenleuchte. Sie tastet \(\zeta(R)\) an den
  UI-Schiebern ab und flüstert, wenn ein Wert aus dem Feld tanzt.
- Mit diesen Laternen spüren wir, dass V01 nicht nur Zahlen bündelt, sondern die
  Resonanzbrücke aus Analyse, Simulator und Narrativ fest verknotet.
