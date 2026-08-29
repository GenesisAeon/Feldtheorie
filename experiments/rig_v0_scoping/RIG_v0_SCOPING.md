# RIG v0 Scoping — Frozen Pre-Registration

**Status: FROZEN at commit time below. Any change to Datenquelle, Schätzer,
Metrik, or Fail-Kriterium after this commit invalidates H1/H2 and requires
a new, separately-dated scoping document — not an edit of this one.**

**Origin:** `grok_report.pdf` + `grok_report2.pdf` (Grok, 2026-08-29),
scoped down from the 5-component role vector in
`docs/science/v_rig_literature_convergence_2026-08.md` to a buildable v0.
Data sources independently verified live (curl/API, not trusted from the
PDF) by Claude Code, 2026-08-29.

---

## 0. What this is and is not

This is **not** a test of AFET, v_RIG, φ, or σ_Φ. Those remain frozen,
read-only secondary hypotheses (see `FORBIDDEN.md` in this directory).
This tests one narrower, falsifiable claim: **that a Träger/Variable
distinction, computed from a 3-component role-vector proxy, generalizes
across domains better than naive baselines.** If it fails, that says
nothing about v_RIG. If it succeeds, that still says nothing about v_RIG
— it would say the *relational-band* structural idea has a working
minimal instrument, which is a separate, smaller claim.

## 1. Role vector (v0 proxy, not Rosas/Hoel)

$$\mathbf{r}_i = (\tau_i, I_i^{\text{macro}}, V_i)$$

This is an explicit **reduction**, not a redefinition of the 5-component
vector (τ, C, I^macro, V, R^causal) from the literature-convergence
whitepaper. Structural centrality (C) and causal reach via effective
information (R^causal) are **out of scope for v0** — they require PID/EI
tooling not yet built. Do not read v0 results as validating the full
Rosas/Hoel-style causal-emergence claim; they only test the cheaper proxy
below.

- **τ (persistence):** e-folding time of the autocorrelation function.
  τ = smallest lag k such that ACF(k) ≤ 1/e, estimated on a fixed-length
  rolling window.
- **V (variability):** rolling-window standard deviation of the
  (detrended, per domain — see §3) series. SampEn was offered as an
  alternative in `grok_report2.pdf`; not used in v0 to keep the estimator
  auditable in ~20 lines of code. If v0's window-std proves too noisy,
  SampEn is the documented v1 upgrade, not a silent substitution.
- **I^macro (macro-informativeness):** single-layer coarse-vs-fine cut.
  Given fine series x_t and its block-averaged coarse series y_t (block
  size = 2×τ, so the cut is itself τ-relative, not a fixed constant):
  $$I^{\text{macro}} = 1 - \frac{\text{MSE}(x_{t+1} \mid y_{\le t})}{\text{MSE}(x_{t+1} \mid \text{naive: mean of } x_{\le t})}$$
  where MSE(x_{t+1} | y_≤t) is the one-step-ahead forecast error of a
  simple AR(1) fit on the coarse series, evaluated against the fine
  series' actual next value. I^macro → 1 means the coarse/macro state is
  highly informative about the fine future; → 0 means no better than the
  naive mean baseline.

**v0-Rollen-Zuweisung** (per Grok's own phrasing, kept verbatim as the
frozen definition): Träger := hohes τ, hoher I^macro. Variable := hohes
V, niedriger I^macro.

## 2. Domains (frozen, verified live 2026-08-29)

| Rolle | Quelle | Zugriff | Status |
|---|---|---|---|
| **Train A** | 2D Ising model, nearest-neighbor, periodic boundary, Metropolis dynamics, self-simulated | Fixed seed (`42`), no download | Ground truth known exactly: T_c = 2/ln(1+√2) ≈ 2.269 J/k_B (Onsager). Distance-to-instability d\*(t) := \|T(t) − T_c\| / T_c for a temperature ramp protocol. |
| **Train B** | NSIDC Sea Ice Index, Northern Hemisphere daily extent, 1978-10-26 to present | `https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v4.0.csv` — direct HTTPS, no auth | Downloaded 2026-08-29. SHA256: `be4f20b799043d90b7e1437dd877842eae5b607183f19ec6fd7451a6f7b80824`. Local copy: `data/train_b/N_seaice_extent_daily_v4.0.csv` (1,892,115 bytes, 15,825 rows). |
| **Hold-out (sealed)** | OpenNeuro ds002778 (Rockhill et al., resting-state EEG, healthy control), subject sub-hc1, single session | `s3://openneuro.org/ds002778/sub-hc1/ses-hc/eeg/sub-hc1_ses-hc_task-rest_eeg.bdf` — direct HTTPS via S3, no auth | Downloaded 2026-08-29, **hash recorded, content not opened, not parsed, not plotted.** SHA256: `e11c5a6e901a268a2e83acf724244bed89716552e50d48cf3a6a13cc6a1a3e0e`. Local copy: `data/holdout_sealed/sub-hc1_ses-hc_task-rest_eeg.bdf` (12,102,144 bytes, matches S3-listed size exactly). **This file stays sealed until the Freeze-Commit checkpoint in §5 is reached and confirmed.**

Rejected candidates and why: RAPID AMOC transport (rapid.ac.uk) requires
email-gated form submission — not scriptable, breaks the "download-date +
hash, reproducible by anyone" requirement. `amoc-utac`'s existing
`data/rapid_mocha_summary.yaml` was checked and contains only annual
summary statistics (mean/std/trend), not a raw time series — insufficient
resolution for τ/V estimation. Rocha et al. (2018) regime-shift Figshare
dataset (DOI 10.6084/m9.figshare.7265096.v1) was checked and is real, but
its web page sits behind an AWS WAF bot-challenge (HTTP 202 on plain
curl); its `ndownloader.figshare.com` API-listed direct file URLs 403
without a signed request. Kept as a documented v1 hold-out alternative,
not used for v0.

## 3. H1 — Collapse test (Train A + Train B only, hold-out untouched)

**Claim tested:** after normalizing t' = t/τ, the distance-to-instability
curves d\*(t') from Train A and Train B collapse onto a common curve
family.

**Procedure:**
1. Compute τ, V, I^macro per domain using rolling windows (window length
   = 10×τ, re-estimated per window — τ is not assumed constant a priori).
2. For Train A: d\*(t) is known exactly from the simulation protocol
   (§2). For Train B: d\*(t) := normalized rolling deviation from the
   40-year linear trend (|extent(t) − trend(t)| / std(extent)), since sea
   ice has no independently-known "critical point" the way the Ising
   model does — this is the operational stand-in, documented as such, not
   hidden.
3. Normalize both to t' = t/τ. Compute the pointwise mean curve across
   both domains.
4. **Goodness metric (fixed before any data is compared):** mean
   pointwise absolute deviation from the common mean curve, and
   separately 1 − R² against it. Both reported; neither is
   discretionary.
5. **Fail criterion (fixed, not adjustable after seeing results):** if
   this same goodness metric, computed later on the hold-out domain in
   §4, exceeds 2× the Train A+B goodness value, **H1 is rejected.** No
   post-hoc threshold widening.
6. **Null comparison:** a spline and a change-point model, each fit with
   the same number of free parameters/knots as the τ-normalization
   uses, must be beaten on the same goodness metric — otherwise the
   τ-normalization itself is not doing real work.

## 4. H2 — Held-out classification test (opens the seal)

**Claim tested:** the v0 mapping rule (Träger := high τ, high I^macro;
Variable := high V, low I^macro), calibrated only on Train A+B, classifies
Träger/Variable segments of the *sealed* hold-out EEG series better than:
mean-value baseline, change-point model, freely-fitted power-law, and a
spline of matched complexity.

**Scoring:** out-of-sample log-likelihood or Brier score. **Not R².**
In-sample fit on the hold-out is not a valid result under this protocol —
the mapping rule may not be refit or adjusted using hold-out data in any
way, including exploratory plotting before scoring.

**Win:** v0 mapping rule beats every baseline on out-of-sample score.
**Lose:** mapping rule is constrained or discarded per §6. Numbers in the
frozen AFET secondary-hypothesis set (§0) are unaffected either way.

## 5. Freeze-Commit checkpoint

Before §4 (opening `data/holdout_sealed/`) may proceed:
1. This document, Train A's simulation code, and the τ/V/I^macro
   estimator code must be committed to git with no further changes
   planned.
2. §3 (H1 on Train A+B only) must have run to completion and its result
   recorded in this repo, pass or fail, before the hold-out is opened —
   not evaluated in parallel with it.
3. Explicit go-ahead from Johann to open the seal, logged as a commit
   message or session note. This is the one checkpoint in this protocol
   that is not delegated to autonomous execution, because it is the
   actual pre-registration commitment the whole exercise exists to
   protect.

## 6. What changes the verdict

Per `grok_report.pdf`'s own framing: winning constrains nothing about
v_RIG/φ/σ_Φ (they stay frozen secondary hypotheses regardless). Losing
means the v0 role-vector proxy gets constrained (e.g., dropped in favor
of building real PID/EI tooling for the full 5-component vector) or
discarded outright — it does not mean the Träger/Variable *concept* is
wrong, only that this specific cheap instrument for measuring it failed.

## Anti-drift note

See `FORBIDDEN.md` in this directory. Any session picking this work back
up must read it first, per the same discipline already enforced in CI by
`tools/afet_constant_guard.py` and `scripts/check_citation_metadata.py`.
