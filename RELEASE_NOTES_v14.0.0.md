# Feldtheorie v14.0.0 (Zenodo iteration 39)

**Date:** 2026-08-27
**Corresponds to:** `docs/NeueForschungenAFET/AFET_UTAC_Zenodo_v39.tex` (whitepaper), superseding Zenodo v38 (`10.5281/zenodo.18647936`).

This release bundles real, verified work accumulated since `v13.0.0`
(2026-06-17) — 41 commits, most of it correcting or hardening existing
claims rather than adding new ones. Nothing here is spin: two real
regressions in the CI pipeline were found and fixed, and a
long-repeated statistic in the AFET whitepaper was traced to its real
source and corrected.

## Highlights

### 1. AFET whitepaper (v39): the "78 systems, η²=0.91" correction

The headline empirical-clustering statistic repeated across every
whitepaper iteration since V6.0.0-beta — `F(4,73)=185.3, p<10⁻²⁰,
η²=0.91` — has been traced to its real source and corrected in three
places (Introduction, Conclusion, Data & Code Availability):

- The source document (`UTAC_v2.0_COMPLETE_ANALYSIS.md`, 2025-11-15)
  labels its own ANOVA table **"simulated from data"**, verbatim. Every
  later iteration dropped that qualifier when repeating the number.
- Of its 8 named per-dataset β values, **5 are real, literature-cited
  measurements** with exact-matching row counts: AMOC paleoclimate
  collapses (NGRIP ice core), Huntington's disease CAG threshold
  (ENROLL-HD), ALS TDP-43 phase separation, vaginal microbiome CST
  transitions (Gajer et al. 2012, *Science*), oral microbiome
  periodontitis (Patel et al. 2015, *Cell*).
- The whitepaper's own "Data and Code Availability" section cited a
  nonexistent file path and mischaracterized the real
  `data/derived/beta_estimates.csv` (36 rows) as a "78-system dataset"
  — also corrected.
- Full account: `VALIDATION_HISTORY.md`.

Domain-specific β clustering is now presented as a working hypothesis
motivated by real per-dataset values, not as an independently
reproduced statistical result.

### 2. New: the Aletheia κ-framing experiment (P1) — real, tested, reported honestly

A new whitepaper section documents a pre-registered LLM-behavior
experiment testing whether framing a language model's system prompt in
"photonic/field-coupled" vs. "discrete/symbolic" language produces a
measurable output difference — real Kimi K2 API calls (not mocked),
collected in two stages (n=30 pilot, then a confirmatory n=120/condition
run, with an optional-stopping guard to prevent interim-peeking bias).

**Result:** 2 of 3 pre-registered metrics meet the fixed support
threshold (output_length d=+0.849, vocab_density d=−0.620, both
p<0.0001; self_reflection d=+0.074, p=0.568, not significant) →
**supports H1** per the pre-registered criteria.

**Explicitly, deliberately NOT bridged to AFET/UTAC/CREP or to any
κ-value.** This shows LLM output is sensitive to this framing
contrast — nothing more. Full write-up with interpretation limits:
`docs/science/kappa_parameter_guide_v2.md` (now v2.2), which also
literature-checks two further predictions (P2: real, but the specific
operationalization needed reframing; P3, P4: confirmed by real,
citable studies including a 78-study meta-analysis, Fox et al. 2016 —
an unrelated, coincidental "78" to the one corrected above).

### 3. Real CI/build reliability fixes

- **mypy could not actually run at all before this** (a module-name
  collision silently broke it); fixed, and 23 real type errors it had
  been missing are now resolved.
- `guard_digital_physics.yml` had no Python/numpy setup — every prior
  run failed with a misleading "Non-Resonant Physics Detected" message
  that was actually just a missing `pip install`. Fixed, confirmed
  green.
- `coverage-check` ImportError, a pytest-cov/numpy dotted-path gotcha,
  a `v8-validation.yml` syntax bug plus 4 Windows-encoding bugs, and
  the TriLayer Drift Validator (broken YAML + real metadata/task
  drift) — all fixed and confirmed green in actual GitHub Actions runs,
  not just locally.
- 9 stale doctest examples in V8 modules corrected.

### 4. Other

- Citation year correction: Bak, Tang & Wiesenfeld 1987 (was
  incorrectly cited as 1988 in one location).
- P70 canonical GenesisAeon package number formally assigned
  (ecosystem registry sprint).
- Buried pre-V8 version snapshots (`v3/`, `v9_alpha/`, `v10_oracle/`,
  `v11_gardener/`, various `archive/` and `releases/` trees) mapped and
  ranked as reactivation candidates — none moved or reactivated, this
  is a documented candidate list only.

## What this release is not

This release does not claim the cosmological core of AFET/UTAC is
newly validated. The Hubble-tension, S₈-tension, and radio-dipole
sections are unchanged from v38 and remain at the same evidence level
(see the paper's own scorecard, Section "Falsifiable Predictions and
Scorecard"). What changed is honesty and reliability: a long-repeated
overstated statistic is corrected, a real new experiment is reported
with its actual mixed result rather than a spun one, and the CI
pipeline now actually checks what it claims to check.

## Files changed (Feldtheorie repo)

- `docs/NeueForschungenAFET/AFET_UTAC_Zenodo_v39.tex` — whitepaper
  corrections + new Aletheia section (see above). **Not yet
  recompiled to PDF in this environment (no LaTeX distribution
  available) — recompile before/alongside publishing this release.**
- `docs/science/kappa_parameter_guide_v2.md` — bumped to v2.2, P1
  tested, P2–P4 literature-checked, 78-datasets provenance note added
  and corrected.
- `scripts/experiment_kappa_framing.py` — new, real experiment script.
- `data/experimental/kappa_framing_results.csv`,
  `kappa_framing_results_study2_n120.csv` — real experimental data.
- `VALIDATION_HISTORY.md`, CI workflow fixes, citation correction — see
  commit history since `v13.0.0` for the full list.
