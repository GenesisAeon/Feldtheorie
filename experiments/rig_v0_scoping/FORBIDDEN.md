# FORBIDDEN — read before touching RIG v0

Read this before writing a line of code or a paragraph of analysis in
`experiments/rig_v0_scoping/`. It exists because chat-window context does
not survive session boundaries, and this project has repeatedly had to
re-fight the same drift (Johann's own account, since UTAC v1.0.0: AI
collaborators repeatedly promoting a fitted number to a universal
constant).

## Read-only (do not recalibrate, do not treat as validated by this work)

- φ, φ^(1/3), σ_Φ = 1/16
- v_RIG = c/(α⁻¹·φ) ≈ 1352 km/s
- 13.5 MHz

These stay exactly as documented in `theory/afet.py` and
`docs/science/v_rig_literature_convergence_2026-08.md`. RIG v0 (this
directory) does not test them, does not confirm them, and a passing H1/H2
result here is not evidence for them. See that whitepaper's own
distinction: the structural *shape* (relational band) has independent
support; the specific *numbers* do not.

## Already falsified — do not reintroduce

- v_RIG written as "1.352 km/s" (decimal-separator bug, was a real
  factor-1000 error in `theory/afet.py`'s `AFETConstants.V_RIG` — fixed
  2026-08-28/29, guarded by `tools/afet_constant_guard.py` in CI).
- "78 datasets, η²=0.91, statistically robust and independently
  reproducible" — traced to a document whose own ANOVA table says
  "simulated from data"; see `VALIDATION_HISTORY.md`.
- Invented `Gamma_tipping` values (0.48/0.62/0.45), a "Pressure-inverted
  UTAC" formula, a "strict GPL-3.0 template" claim, a non-existent git
  branch — all from an external AI dialogue, all disproven by direct repo
  inspection; see `coral-reef-utac`'s DISCLAIMER.md.
- "Gamma≈0.251 universal across domains" — this is AMOC's own
  domain-specific calibration value from
  `resilience-core/benchmarks/calibration.py`, not a constant (real range
  0.05-0.92 across domains).

## Process rules for this directory

1. **No new numeric invariant more than once per quarter**, and only if
   it was written down *before* the data that would test it was touched.
2. **Every "confirmation" without a held-out test is invalid.** State
   which domain was held out and untouched, or the result does not count.
3. **`RIG_v0_SCOPING.md` is frozen once committed.** A changed mind about
   estimator, data source, or metric requires a new, separately-dated
   scoping document, not an edit.
4. Widespread reuse of the Coherence/Resonance/Emergence/Persistence
   pattern across ~40+ GenesisAeon packages is not validation of that
   pattern — see `PACKAGE_REGISTRY.md`'s "Framework-categorization
   findings" section, Johann's own account, 2026-08-02.

If a future session wants to add to this list: append, do not delete
past entries, even ones that feel obvious in hindsight — that history is
the point.
