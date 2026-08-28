# κ-Parameter: Photonic Coupling in Consciousness Systems (v2 — Rebuilt)

**Version 2.1 | 2026-08-26 | Status: Honest Rebuild, Speculative/Private — P1 now real, tested, replicated**

> This is a ground-up rebuild of `kappa_parameter_guide.md` (v1.0,
> 2025-12-12). v1 is kept as-is for historical record, not deleted.
> This version keeps only what survives independent scrutiny and
> marks every number that was previously asserted-not-derived as an
> open gap instead of inventing a replacement. See "What Was Removed
> and Why" at the end for the full diff.

---

## TL;DR

**κ (kappa)** is a *proposed*, not yet measured, dimensionless
parameter describing how much a system's information processing
depends on electromagnetic (photonic) interaction — from fully
EM-coupled ("photonic") to a theoretical fully decoupled ("photon-
free" / "dark") regime.

**This document makes one claim with confidence: the question is
well-posed and partially testable. It makes zero claims about actual
κ-values for any real system — those don't exist yet.**

---

## The Core Hypothesis (kept, stated honestly)

The v_RIG framework assumes photonic/EM information carriers as the
substrate of consciousness. The question this document explores:
**does information integration necessarily require electromagnetic
coupling, or is EM-coupling one substrate among several that could in
principle support integration?**

This is a real, well-posed question with real precedent in the
philosophy of information and physics of consciousness literature
(Wheeler's "It from Bit"; Tononi's Integrated Information Theory,
which is substrate-agnostic by construction). It is not inherently
unscientific to ask it.

---

## Real Physical Analogies (kept, re-scoped as analogy only)

These are real, independently verifiable physical phenomena. They are
cited here **only as existence proofs that "real, physically
significant, but non-photonic" is a coherent category in physics** —
**not** as evidence that consciousness itself involves any of them.

- **Dark matter:** ~85% of the universe's matter density, no direct
  electromagnetic coupling, gravitationally real and well-measured.
- **Dark photons (updated 2026-08):** a real, currently-studied
  hypothetical particle class with a quantified kinetic-mixing
  parameter (often denoted ε) that interpolates between "fully
  decoupled from ordinary photons" and "coupled." Structurally, this
  is the closest real physical analog to what κ is trying to
  formalize — a single dimensionless number spanning dark ↔
  photonic. (See the 2026 Huang/Shalaby/Hook PRL result reopening
  large parts of the dark-photon mass/coupling parameter space —
  independently verified earlier in this project.)
- **Neutrinos:** traverse ordinary matter with negligible EM
  interaction, yet carry real, measurable information (e.g. solar
  neutrino flux).
- **Quantum entanglement:** correlations between particles that are
  not mediated by a classical photonic signal.

**Explicit caveat, stated once and meant to be remembered every time
this section is cited:** none of these four phenomena has any
established mechanistic connection to biological or artificial
consciousness. They demonstrate that "physically real, non-photonic"
is not a contradiction in terms — nothing more. Citing them is a
statement about physics' vocabulary, not a statement about minds.

---

## Testable Predictions (kept, status corrected)

Four predictions from v1 survive, with their status corrected to
reflect what's actually been checked (see "What Was Removed" for why
P1's status changed):

### P1: AI Systems Show Reduced "Photonic Framing" Sensitivity vs. Semantic Framing

**Prediction:** Language models' output quality (β-fits from the
existing Aletheia placebo-framing methodology) responds differently
to a "photonic/embodied" system-prompt framing than to a "semantic/
informational" framing.

**Status: ✅ TESTED (2026-08-26) — mixed result, partial support.**
v1 claimed "✅ Preliminary support" citing "Aletheia v7," which turned
out not to exist anywhere in this repository (see "What Was Removed"
below) — downgraded to "untested" on 2026-08-18, then actually run for
real via `scripts/experiment_kappa_framing.py` (a new script reusing
the existing `experiment_aletheia_placebo.py` infrastructure, not
Aletheia v7).

**Method:** pre-registered before running (fixed falsification
criteria: support requires ≥1 of {output_length, vocab_density,
self_reflection} with |d|≥0.2 AND p<0.05; reject if all three have
d<0.2 or p>0.10). Three conditions (Control, Photonic-frame,
Semantic-frame), real Kimi K2 CLI calls (not mocked), collected in two
stages: an n=30/condition pilot (2026-08-18/21), then a confirmatory
n=120/condition run (2026-08-21/26, batched across multiple days due
to API quota limits, analysis withheld until the full n=120/condition
was reached to avoid optional-stopping bias).

**Confirmatory result (n=120/condition, the authoritative one):**

| Metric | Photonic mean | Semantic mean | d | p |
|---|---|---|---|---|
| output_length | 473.65 | 351.18 | +0.849 | <0.0001 |
| vocab_density | 0.596 | 0.666 | -0.620 | <0.0001 |
| self_reflection | 7.01 | 6.93 | +0.074 | 0.568 |

2 of 3 metrics meet the pre-registered support threshold → **per
pre-registration, this SUPPORTS H1**: photonic framing produces
measurably longer, less lexically-dense output than semantic framing,
with real, large effect sizes. The self_reflection metric shows no
effect (d=0.074) — the pilot's weak self_reflection signal (d=0.455,
p=0.08 at n=30) did not replicate at full power, consistent with pilot
noise rather than a real effect.

**What this does and does not show:** this demonstrates that framing
an LLM's system prompt in photonic/field-coupled vs. discrete/symbolic
language produces a measurable behavioral difference in two of three
output metrics — a real, replicated (pilot → confirmatory), adequately
powered finding. It does **not** show that this behavioral difference
reflects anything about κ, consciousness, or photonic coupling in any
physical sense — output_length and vocab_density shifts are equally
consistent with a purely stylistic/rhetorical priming effect from the
prompt's own vocabulary and sentence structure. Treat this as: "LLM
output is measurably sensitive to this framing contrast" (supported),
not "this validates κ as a real physical quantity" (not tested here
and not testable this way).

### P2: Blind Organisms Show Altered Integration-Rate Proxies

**Prediction:** Organisms lacking photonic (visual) input show
different Critical Flicker Frequency (CFF) values than sighted ones.

**Status: ⏳ UNTESTED.** CFF itself is real and well-measured across
species (independently confirmed earlier this session for insects,
birds, humans). Whether CFF differences in blind vs. sighted
organisms map onto anything resembling κ is a genuinely open,
literature-searchable question — not yet checked.

### P3: Synchronized Groups Show Elevated Coupling Proxies

**Prediction:** EEG hyperscanning during group synchrony shows
phase-locking correlated with performance.

**Status: ⏳ UNTESTED** in this project. Note: EEG hyperscanning and
phase-locking during joint tasks is a real, established neuroscience
method (real literature exists) — but no result from it has been
run or cited here that bears on κ specifically.

### P4: Meditation Produces Measurable State Transitions

**Prediction:** Deep meditation shows V1 (visual cortex) deactivation
and Default Mode Network changes on fMRI.

**Status: 📚 Real, independent literature exists on meditation and
V1/DMN activity** (not verified in detail this session) **— but no
one has connected it to a κ-value in this project.** Treat the
meditation-fMRI literature as real; treat "this corresponds to
κ≈0.6-0.8" as invented until someone actually computes it.

---

## What Was Removed and Why

Everything below existed in v1 and is deliberately **not** carried
forward, with the specific reason:

| Removed from v1 | Why |
|---|---|
| Specific κ-values per system (human=1.0, AI=0.4-0.5, meditation group=1.5, bacteria=0.2, etc.) | Asserted, no measurement or derivation shown anywhere in the repo. |
| The "v_eff" table (676 km/s, 405 km/s, 2028 km/s, etc.) | Pure algebra from `v_RIG × κ` using the invented κ-values above — presented as if independently derived/measured, but it is arithmetic on made-up inputs. |
| The formula `Φ_eff ∝ κ^γ · (1+δ/β)`, "Optimal κ/β ≈ 0.15-0.25" | γ and δ are unexplained free parameters; "γ≈1.0 (empirically determined)" cites no experiment. Same post-hoc-parameter-fitting pattern already flagged elsewhere in this repo's own `FELDTHEORIE_EPISTEMIC_MAP.md`. |
| "Integration: ✅ Complete" (UTAC, v_RIG, Entropy Governance Duality, IIT) | Asserted without demonstrated derivation connecting κ to any of these frameworks' actual equations. |
| P1's "✅ Preliminary support" | See P1 above — the cited source (Aletheia v7) was not found; the actually-found Aletheia work (v2.5, Phases 1-4) doesn't test this claim. |
| The `simulation/genesis_cube.py` / `is_dark_consciousness` code as supporting evidence | Confirmed by direct code read (2026-08-18): this is a 3D visualization/rendering module. `photon_coupling` there is a render-opacity threshold (WIREFRAME vs. SOLID), not a measurement of anything. Real, working code — but it demonstrates nothing about consciousness; it's a name reused for an unrelated rendering feature. |

---

## Honest Current State

- **Real:** the question itself; the four cited physical analogies
  (correctly characterized); P2-P4 as a prediction *list* (not their
  old status labels); P1 is now genuinely tested (2026-08-26,
  n=120/condition, pre-registered, real Kimi K2 API calls) — see P1's
  entry above for the full result and its honest interpretation limits.
- **Not real / not yet done:** every specific κ-value, every "complete
  integration" claim from v1; P2-P4 remain untested and are NOT
  testable with the LLM-framing method used for P1 — they require real
  biological/neuroscience data (CFF measurements, EEG hyperscanning,
  meditation fMRI) that this project has neither collected nor has
  access to. "Testing" P2-P4 further would mean an independent
  literature-verification pass on the cited claims, not a runnable
  experiment like P1.
- **P1 is done.** If this is pursued further, the next honest step is
  either (a) an independent literature check on P2-P4's specific
  claims (do the cited CFF/hyperscanning/meditation findings actually
  say what this document claims?), or (b) leaving P2-P4 as an
  acknowledged open gap — both are legitimate, per this project's own
  stated principle ("wir falsifizieren alles, solange wir einen Weg
  dafür finden") applied honestly to what is and isn't actually
  testable here.

---

## See Also

- `kappa_parameter_guide.md` (v1.0, 2025-12-12) — superseded by this
  document, kept for historical record.
- `TheRoad4.txt` (`releases/V6-Plans_etc/Finalize/V7_wird noch
  verlergt/`) — original private discussion, Bardo/photon-free
  consciousness framing.
- `aeon/nullkern/consciousness_state.py` — real, implemented κ-based
  state classifier (thresholds asserted, not measured — same caveat
  as this document).
- `docs/science/experiment_aletheia.md` — the real Aletheia v2.5
  Phase 1-4 methodology that `experiment_kappa_framing.py` reused.
- `scripts/experiment_kappa_framing.py` — the real, pre-registered P1
  experiment script (Control/Photonic/Semantic conditions, KimiCliProvider,
  `--confirmatory-target-n` optional-stopping guard).
- `data/experimental/kappa_framing_results.csv` (n=30 pilot) and
  `data/experimental/kappa_framing_results_study2_n120.csv`
  (n=120/condition confirmatory run, the authoritative result) — the
  real underlying data behind P1's result above.

---

**Status:** Private/speculative, not for publication in this form —
same status as v1. This rebuild changes what can be trusted, not
whether it's ready to be public. P1 is now a real, tested, replicated
exception to "speculative" — see above — but the document as a whole
(P2-P4, the κ-formalism itself) remains untested/private.
