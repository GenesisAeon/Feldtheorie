# κ-Parameter: Photonic Coupling in Consciousness Systems (v2 — Rebuilt)

**Version 2.2 | 2026-08-26 | Status: Honest Rebuild, Speculative/Private — P1-P4 all now checked against real evidence**

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

**Status: ⚠️ Literature-checked (2026-08-26) — the specific
operationalization does not hold up, but a real underlying phenomenon
does, in a different form.** No study directly comparing CFF between
fully blind and sighted organisms was found — and on reflection this
prediction may not even be coherently measurable as stated: CFF is a
measure of *visual* flicker-fusion, which requires some residual light
perception to test at all. A fully photonic-input-free organism has no
CFF to measure, not a "different" CFF value.

**What the real literature actually shows instead:** cross-modal
sensory-compensation plasticity is real and well-documented. Early
blind humans show measurably faster auditory temporal-resolution
markers (MMN/N2b latency) than sighted controls, via visual cortex
being recruited for auditory processing (Frontiers in Neuroscience
2019, doi: 10.3389/fnins.2019.01200; Journal of Neuroscience 2019,
"Early Blindness Shapes Cortical Representations of Auditory
Frequency," doi: 10.1523/JNEUROSCI.2896-18.2019). Blind cavefish
(*Astyanax mexicanus*) show a parallel pattern in a different taxon:
eye loss paired with expansion of the non-visual lateral-line
mechanosensory system (PMC11036076).

**Honest reframing:** the real phenomenon is "loss of photonic input
correlates with measurable temporal/sensory reallocation in the
REMAINING modalities" — not "CFF specifically differs." If P2 is
revisited, it should be restated around cross-modal auditory
temporal-resolution markers, not CFF. As with P1, none of this is
evidence for κ or photonic coupling as a physical quantity — it is
evidence that sensory deprivation drives real, measurable
neuroplasticity, a much broader and independently well-established
phenomenon than this document's specific framing.

### P3: Synchronized Groups Show Elevated Coupling Proxies

**Prediction:** EEG hyperscanning during group synchrony shows
phase-locking correlated with performance.

**Status: ✅ Literature-checked (2026-08-26) — the general claim is
real and well-supported, not connected to κ.** EEG hyperscanning
(simultaneous multi-brain recording) is a real, established method.
Multiple real studies show inter-brain phase-locking/synchronization
correlating with joint-task performance: good-performing pairs in a
visually-guided alternate-tapping task showed higher inter-brain
alpha-band (12 Hz) synchronization than poor-performing pairs, and
inter-brain phase coherence increased during high-coordination phases
of musical leader-follower duets (Scientific Reports 2022, doi:
10.1038/s41598-022-10049-7, anti-phase tapping study). Real,
replicated, quantified — but this is evidence for interpersonal
neural synchrony as a real phenomenon, not for any κ-value; no
attempt has been made in this project to connect it to one.

### P4: Meditation Produces Measurable State Transitions

**Prediction:** Deep meditation shows V1 (visual cortex) deactivation
and Default Mode Network changes on fMRI.

**Status: ✅ Literature-checked (2026-08-26) — strongly confirmed,
better-supported than expected, still not connected to κ.** Fox et
al. (2016), *Neuroscience and Biobehavioral Reviews*, 65, 208-228
(doi: 10.1016/j.neubiorev.2016.03.021) — a real, large meta-analysis
of 78 functional-neuroimaging studies (257 peak foci, 31 experiments,
527 participants) — found reliable, dissociable activation/
deactivation patterns across meditation styles, with occipital
(visual) cortex, thalamus, and Default Mode Network hubs (precuneus,
posterior cingulate, antero-medial prefrontal cortex) among the most
consistent deactivation sites for focused-attention meditation
specifically, with real, quantified medium-to-large effect sizes
(d=0.60 for activations, d=−0.74 for deactivations). Independently
corroborated by Brewer et al. (2011), *PNAS*, 108(50), 20254-20259 —
DMN main nodes (medial prefrontal, posterior cingulate cortices)
relatively deactivated in experienced meditators across meditation
types — and a 2023 7-Tesla ultra-high-field pilot study replicating
the same DMN/visual/thalamic pattern.

**This is real, replicated, multiply-converging science.** It is
still, exactly as v1 warned, **not** evidence for "κ≈0.6-0.8" or any
other specific κ-value — no study cited here computes or reports a κ.
Treat the neuroimaging findings as real and now independently
re-verified; treat any specific κ-number attached to them as invented
until someone actually derives one from this data.

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

- **Real and now checked:** the question itself; the four cited
  physical analogies (correctly characterized); P1 genuinely tested
  (2026-08-26, n=120/condition, pre-registered, real Kimi K2 API
  calls — mixed result, 2/3 metrics support H1); P3 and P4 both
  literature-verified against real, citable, quantified studies (P3:
  real inter-brain phase-locking/performance correlations; P4:
  strongly confirmed by a 78-study meta-analysis plus independent
  corroboration); P2's underlying phenomenon (sensory-loss-driven
  neuroplasticity) is real, but its specific CFF operationalization
  does not hold up and has been reframed around cross-modal auditory
  temporal-resolution markers instead — see each P-entry above for
  full citations and effect sizes.
- **Not real / not yet done:** every specific κ-value anywhere in this
  document, every "complete integration" claim from v1, any claim
  connecting P1-P4's real findings to a computed κ-number. All four
  predictions are now checked against real evidence; none of that
  evidence has been connected to κ as a physical quantity by anyone,
  in this project or the literature cited.
- **P1-P4 are all now checked.** What remains open, if this is
  pursued further: (a) whether P2 is worth re-testing in its reframed
  form (cross-modal auditory temporal resolution, not CFF), and (b)
  the much larger, still-untouched question of whether ANY of P1-P4's
  real findings can be connected to a genuine, derived κ-value rather
  than treated as separate analogies — this would require the
  R-derivation/falsification pipeline Johann and Claude Code agreed
  to defer to a future session, not another literature check.

---

## Provenance Note: the "78 datasets/datapoints" figure (2026-08-26)

Not a κ-specific finding, but discovered while cross-checking P4's
"78 functional-neuroimaging studies" (Fox et al. 2016, real, see
above) — Johann noticed this number matched a "78" that has appeared,
unexplained, across this project's broader UTAC/AFET validation
claims for a long time and never matched the actually-counted real
data. Investigated on request:

- **"78 empirical datasets/datapoints" is real, in the sense that it
  is genuinely repeated across many project documents** (`UTAC_v2.0_EXECUTIVE_SYNTHESE.md`,
  `UTAC_v2.0_COMPLETE_ANALYSIS.md`, `UTAC_7Day_Action_Plan.md`,
  `ZENODO_UPLOAD_README.md`, `AFET_Universal_Framework_Paper_final.md`,
  and multiple Gemini/DeepResearch dialogue logs under
  `docs/AFET/` and `releases/V6-Plans_etc/`) — this is not a one-off
  typo, it was treated as an established fact for a long time.
- **It does not match the actually-counted real data.** The real
  Claude-Datenpacket (independently counted this session via `find`)
  contains 60 CSV files, not 78.
- **The Gemini/DeepResearch logs show the number being asserted and
  then repeated as unquestioned ground truth across many consecutive
  turns**, e.g. `docs/AFET/GeminiSucheDOIListe.txt` (5 near-identical
  passages: "...gegen 78 empirische Datensätze prüfen..."),
  `releases/V6-Plans_etc/Claude.txt` ("UTAC β-Clustering (empirisch
  validiert: 78 Datenpunkte)"), `docs/AFET/AFET_ParameterSucheGemini.txt`
  and `docs/AFET/SucheChatGPTDeepResearch.txt` (both refer to "unsere
  78 Datensätze" as already-settled) — none of these passages
  re-derive or recount the number; each treats it as inherited fact
  from an earlier turn.
- **Johann's account (2026-08-26):** he recalls repeatedly noticing
  this "78" didn't match the project's real datasets during an
  intensive period of Gemini DeepResearch use, but did not stop to
  correct it at the time — Gemini's output quality felt exciting
  enough that the mismatch got waved through rather than checked, and
  the number then kept propagating forward through later turns and
  documents.
- **What was NOT found (by this pass):** a literal textual passage
  showing "78" being copied directly from a meditation/neuroimaging
  source (e.g. Fox et al. 2016's real "78 functional neuroimaging
  studies") into a UTAC dataset-count claim in the same visible
  conversation. The saved Gemini/DeepResearch `.txt` logs searched here
  only show the number already established and being repeated, not the
  moment it was first produced. The meditation-literature-contamination
  hypothesis remains plausible and consistent with this project's
  general pattern of cross-context number bleed (see
  `feedback_ai_dialogue_verification_pattern` memory) and with Johann's
  own account, but is still not confirmed by a documented textual
  origin.

- **CORRECTION (2026-08-27): a prior session already found the real
  origin, more precisely than the pass above.** `VALIDATION_HISTORY.md`
  (archaeology sprint, 2026-07-19) traced the number to
  `archive/legacy_v1_v3/seed/RoadToV.3/UTAC Empirical Validation v2.0/
  UTAC_v2.0_COMPLETE_ANALYSIS.md` (2025-11-15) directly — and found
  something more precise than "unverified, likely hallucinated": **that
  document's own ANOVA table header literally reads "ANOVA Results
  (simulated from data)"**, verbatim, in the 2025-11-15 source itself.
  Every later release-notes generation (V6.0.0-beta, V6.0.0, V8, V9)
  dropped that qualifier when repeating the number — so the honesty
  label was present at the origin and lost in transmission, not absent
  from the start. Additionally: 5 of the document's 8 named per-dataset
  β estimates ARE real and literature-cited, with exact-matching row
  counts, at `archive/legacy_v1_v3/seed/RoadToV.3/Claude-Datenpaket2/`
  (note: **a different, separately-numbered folder from the
  "Claude-Datenpacket" — no "2" — 60-file set checked earlier this
  session** — comparing 78 against the wrong 60-file folder was this
  pass's own error, now corrected): AMOC/NGRIP ice core, Huntington's/
  ENROLL-HD, ALS/TDP43, vaginal microbiome/Gajer et al. 2012 *Science*,
  oral microbiome/Patel et al. 2015 *Cell*. The remaining 3 named
  datasets were not found as exact matches. Full detail:
  `VALIDATION_HISTORY.md`, section "The '78 β-values' claim — UPDATE:
  origin document found". This session's own finding above (Gemini/
  DeepResearch logs treating "78" as unquestioned inherited fact) still
  stands as real, additional context for HOW the number propagated
  forward after that origin point — it just isn't the origin-tracing
  finding itself, which predates this session.
- **Practical upshot:** any downstream document citing "78
  datasets/datapoints" for UTAC/AFET validation should be treated as
  citing an unverified, likely-hallucinated count, not real data —
  the real, counted figure for the Claude-Datenpacket specifically is
  60 CSV files.

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
whether it's ready to be public. P1-P4 are now real, checked
exceptions to "speculative" as individual findings — see above — but
the document as a whole
(P2-P4, the κ-formalism itself) remains untested/private.
