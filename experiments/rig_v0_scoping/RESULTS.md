# RIG v0 — H1 Results (Train A + Train B only, hold-out untouched)

**Date:** 2026-08-29
**Status: H1 does not currently pass its own pre-registered check (section
3, item 6). Hold-out was NOT opened.** Per `RIG_v0_SCOPING.md` section 5,
opening the hold-out requires H1 to run to completion on Train A+B first —
it has, and the result is a documented fail on the null-model comparison,
not a pass. Proceeding to H2 anyway would contradict the protocol's own
logic: if τ-normalization doesn't already beat a naive flexible curve on
the training domains, there is no principled reason to expect it to work
on the sealed domain either.

## Final numbers

| | τ | V | I^macro |
|---|---:|---:|---:|
| Train A (Ising, detrended \|M\|) | 1007 sweeps | 0.179 | −2.33 |
| Train B (NSIDC sea ice, detrended anomaly) | 67 days | 0.378 | 0.035 |

| Metric | τ-normalized collapse | Null model (spline, no τ-rescaling) |
|---|---:|---:|
| Mean abs deviation | 0.186 | **0.145** (wins) |
| 1 − R² | 0.656 | **0.546** (wins) |

**τ-normalization beats null: `False`.** The null model — a spline fit
directly to each domain's raw (unnormalized) index with the same degrees
of freedom as τ provides — collapses the two domains onto a shared curve
*better* than rescaling time by τ does. Per section 3, item 6, this means
τ-normalization is not currently doing real work in this v0 instantiation.

## Three real implementation bugs found and fixed en route (not spec changes)

All three are documented in commit history and code comments, not hidden.
None of them touched the frozen definitions in `RIG_v0_SCOPING.md` section
1, the H1 goodness metric, or the fail-threshold — each is a case of the
code not yet correctly implementing what the frozen prose already said.

1. **τ estimator's `max_lag=200` ceiling.** Both domains hit exactly
   τ=200.0 on the first run — not a real e-folding time, just the
   estimator's own arbitrary cap. Direct ACF inspection (lags out to
   1000) showed Train A's autocorrelation doesn't cross 1/e until
   ~lag 830 (genuine critical-slowing-down near T_c is physically
   expected), and Train B's ACF is non-monotonic (residual multi-year
   structure survives simple deseasonalization). Fixed: `max_lag`
   defaults to `len(x)//4` (standard rule of thumb) instead of a fixed
   constant.
2. **Train A was never detrended, only Train B was.** Section 1 already
   specifies "the (detrended, per domain) series" for V. The first
   correction only added trend removal to Train B's *d\** computation, not
   to Train A's raw `|magnetization|` series used for τ/V/ACF. The
   temperature ramp induces a large deterministic drift in magnetization
   (ordered → disordered) that dominated the ACF, making τ scale with
   simulation length (2613 at N=12000 vs. 830 at N=4000) instead of
   converging to a physical value — a tell that something was
   structurally wrong, not just noisy. Fixed: `detrend_linear()` applied
   uniformly to both domains before any estimator runs on them.
3. **I^macro was uncomputable at N_SWEEPS=4000** because the discovered
   τ (830, before the detrending fix) left too few `block_size=2τ` blocks
   (need ≥4 per spec) for Train A's series length. Raised `N_SWEEPS` from
   4000 to 12000 — a self-contained simulation-length parameter with no
   real-world data constraint, not a change to any frozen metric.
   **Train B has no equivalent fix available**: at τ=67 with
   `block_size=134`, Train B's 14,108-point record gives ~105 blocks,
   comfortably above the ≥4 threshold — this one resolved itself once
   detrending was fixed, unlike the earlier (pre-fix) τ=2316 case where
   even the full 38.6-year NSIDC record would have been insufficient.

## What this does and does not mean

**Does not mean:** anything about v_RIG, φ, σ_Φ, or 13.5 MHz — those
were never part of this test and remain exactly as documented in
`docs/science/v_rig_literature_convergence_2026-08.md`, per `FORBIDDEN.md`
in this directory.

**Does not mean:** the Träger/Variable *concept* is wrong. It means this
specific cheap v0 proxy (3-component role vector, single-layer
coarse-vs-fine cut, linear detrend + e-folding τ) does not yet
demonstrate that τ-rescaling captures real cross-domain structure better
than a generic flexible curve, on this specific domain pair.

**Does mean**, concretely: either (a) the v0 estimators need real
revision — e.g. I^macro's single-layer cut may be too crude (Train A's
strongly negative I^macro suggests the coarse AR(1) forecast is actively
worse than the naive baseline, not just uninformative), or the linear
detrend may be too weak for Train B's slower multi-year structure — or
(b) this is accepted as a genuine v0 negative result and the next step is
building the fuller Rosas/Hoel-style PID/EI machinery this v0 proxy was
explicitly scoped down from (`docs/science/v_rig_literature_convergence_2026-08.md`,
falsifiable-next-steps item 3), rather than iterating further on the cheap
proxy.

## Recommendation

Do not open `data/holdout_sealed/` yet. This is a genuine decision point,
not an autonomous-execution step — per `RIG_v0_SCOPING.md` section 5,
that was deliberate. Two honest paths forward, Johann's call:

1. **Revise v0** (new estimator definitions, e.g. a better I^macro cut or
   a nonlinear detrend for Train B) as a new, separately-dated scoping
   document — not an edit of the frozen one — then rerun H1 before ever
   touching the hold-out.
2. **Accept this as v0's answer** and archive it as a real, documented
   negative result — itself a legitimate scientific outcome, and arguably
   a better one for this project's credibility than a result massaged
   into passing.

Either way: the hold-out EEG file's hash (`RIG_v0_SCOPING.md` section 2)
is unchanged, its content still unopened.
