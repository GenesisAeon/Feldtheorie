# v_RIG and the Relational Tipping-Band Framework: An Independent Literature Convergence Check (2026-08)

**Status:** Speculative core (v_RIG, φ^(1/3), σ_Φ) remains an explicitly frozen
secondary hypothesis. This document does not claim validation of AFET's
specific constants. It documents what independent 2026 literature *does*
and *does not* support, and sharpens exactly where the open question sits.

**Date:** 2026-08-29
**Authors:** Independently produced by three separate AI research passes
(deep-research literature mapping, a synthesis pass, and an adversarial
fact-check pass), reviewed and corrected by Johann Römer and Claude Code.
**Supersedes in tone, not in content:** the "KEINE Numerologie" framing in
`v_RIG_empirical_validation.md` and the "fundamentale Naturkonstante"
framing in `v_rig_validation_final.md` / `v_rig_validation_matrix.md` —
see "Relationship to earlier v_RIG documents" below.

---

## Why this document exists

GenesisAeon's Träger/Variable (carrier/variable) typing and the "relational
tipping band instead of a fixed critical point" idea have been the
project's working position since UTAC v1.0.0 (Johann's own account:
early AI collaborators repeatedly wanted to promote β ≈ 4.2 to a universal
constant; he rejected this from the start, insisting it must be a *band*,
not a point). This document checks that position, and the more speculative
v_RIG construction, against real, independently verified 2026 literature —
not literature selected to confirm the framework, but literature that
*operationalizes* the same underlying questions (how is a scale hierarchy
detected, how does finite integration time affect an optimum, how does a
tipping threshold depend on forcing rate).

Source material (raw, unedited AI research passes, kept as working
material, not duplicated here): `deep-research-report.md`, `Emergente
DeepResearch-Analyse.md`, `spekulatives Hypothesengerüst.md`, and
`compass_artifact_wf-aac18913-fcb4-5133-b210-c4ab6935f161_text_markdown.md`
(the adversarial fact-check pass) in the GenesisAeon workspace root
(`D:\mandala\docs\`, not part of this repo).

## What was independently re-verified (2026-08-29, this session)

Two of the most load-bearing citations were checked directly against
their live sources (not just trusted from the source documents):

- **Azizpour, S., Priesemann, V., Zierenberg, J. & Levina, A. (2026).
  "Finite integration time can shift optimal sensitivity away from
  criticality." *Communications Physics* 9, 119.** DOI:
  10.1038/s42005-026-02584-w. Confirmed real via direct fetch: title,
  authors, and core claim (a recurrent network's functional optimum sits
  at a subcritical safety margin for any finite integration time, and
  only approaches the critical point as integration time grows) match
  exactly.
- **van Westen, R. M., Börner, R. & Dijkstra, H. A. (2026). "Failure to
  track a stable AMOC state under rapid climate change." *Nature Climate
  Change*.** DOI: 10.1038/s41558-026-02730-w. Confirmed real via direct
  fetch: AMOC stays stable to +5.5°C under slow CO2 forcing (+0.5 ppm/yr)
  but collapses around +2°C under faster forcing — rate-induced tipping,
  not a fixed temperature threshold.

## What structurally converges with the Träger/Variable framework

Both confirmed papers, plus Rosas et al. (2020, PLOS Comp Biol,
information-theoretic causal emergence), Hoel (2026, *Patterns*, Causal
Emergence 2.0) and Jansma & Hoel (2025 preprint, "Engineering Emergence")
support the same qualitative shape this project has argued since UTAC
v1.0.0: **a tipping point is not a fixed universal value; it is a band
whose position depends on integration time, forcing rate, coupling, and
task/observer context.** This is a genuine, independently-arrived-at
structural match, not something these papers set out to confirm about
AFET specifically — none of them reference this project.

This is the part worth being glad about. It is not proof of AFET. It is
evidence that the *shape* of the claim (relational band, not fixed point)
is showing up independently in current peer-reviewed physics, neuroscience,
and climate science, four years after this project first insisted on it
against AI collaborators' pull toward declaring a fixed constant.

## What does NOT converge: v_RIG's specific number

The adversarial fact-check pass (`compass_artifact...md`) found the
sharpest, most concrete result in the whole set, and it cuts against the
constant, not for it:

$$v_{\text{RIG}} = \frac{c}{\alpha^{-1}\cdot\varphi}$$

splits into two parts. **c/α⁻¹ = αc is real, established physics** — the
velocity of the electron in the hydrogen atom's ground-state Bohr orbit
(≈ 2187.7 km/s), a textbook result since 1913, not a recent finding. It
was **not fitted to this framework after the fact** — the v_RIG formula
predates this literature check, and αc was found by independent research
tooling searching the literature afterward. That ordering (motivated
construction first, later discovery of a real partial anchor) is
meaningfully different from post-hoc curve-fitting, and worth noting as
such.

**The φ factor that turns αc into v_RIG has no known physical
mechanism.** Dividing a real velocity by the golden ratio is dimensionally
valid but not physically motivated by anything in the cited literature —
critical exponents in physics come from universality classes (symmetry,
dimensionality), not from φ, and the numerology linking φ to physical
constants is explicitly rejected by the physics community in every source
the fact-check pass could find. This does not mean v_RIG is wrong. It
means the open question is now sharper and more specific than before:
**not "is v_RIG real," but "why divide αc by φ specifically, and not by
2^(1/3), e^(1/3), or a freely fitted constant."**

φ^(1/3) as a cross-domain scaling exponent has the same status: no
renormalization-group or universality-class derivation exists for it in
the checked literature.

## Falsifiable next steps identified by all three research passes

Independently converging across all three AI research passes:

1. **Freeze v_RIG, σ_Φ, φ^(1/3) as secondary hypotheses.** Do not
   recalibrate them against new data. State explicit tolerance bands now,
   so a future match or miss means something.
2. **Test φ^(1/3) against alternatives** (2^(1/3), e^(1/3), √φ, a freely
   fitted exponent, and a null model with no distinguished constant) —
   not just against "does it look close."
3. **Operationalize Träger/Variable as a computable role vector** instead
   of semantic assignment, e.g. r_i = (τ_i, C_i, I_i^macro, V_i,
   R_i^causal): relaxation/memory time, structural centrality, irreducible
   macroscopic information contribution (via partial information
   decomposition), local state variability, and causal reach across
   coarse-grainings (via effective information / Causal Emergence 2.0).
   This is a real, multi-session research/engineering program, not
   something built in this session — noted here as the concrete target,
   not implemented here.
4. **A pre-registered, blinded frequency scan (1-50 MHz) at fixed pulse
   parameters** would be the decisive test for the 13.5 MHz neurite-growth
   anchor (Fontana et al. 2024) — determining whether it is a narrow
   resonance peak or part of a broad effective band.
5. **Three-domain, held-out benchmark**: calibrate any mapping rule on two
   domains (e.g. a synthetic network with known ground truth + a neural/
   Azizpour-style model), test blind on a third (e.g. AMOC), scored on
   out-of-sample prediction error against power-law/spline/change-point
   baselines — not in-sample R².

None of these five are executed by this document. They are the concrete,
falsifiable target this literature check converged on, kept here so the
next session that picks this up doesn't have to re-derive it.

## Relationship to earlier v_RIG documents in this repo

`v_RIG_empirical_validation.md` (2025-12-08) and `v_rig_validation_final.md`
/ `v_rig_validation_matrix.md` (2025-12) describe v_RIG as a "fundamentale
Naturkonstante" and explicitly claim "KEINE Numerologie". Per this
independent 2026 check, that framing overstates the current evidence
status: the φ-step is exactly the kind of dimensionally-valid-but-
physically-unmotivated construction the physics community treats as
numerology-adjacent until a mechanism is shown. Those documents' *data*
(the Böhme et al. dipol comparison, the simulation results) are not
contradicted here — only the "proven/no numerology" framing is corrected.
`v_rig_simulation_analysis_report.md` (2025-12-01, "Hypothesis NOT
supported") already carried the appropriately cautious framing and needs
no correction.

## References

- Azizpour, S., Priesemann, V., Zierenberg, J., Levina, A. (2026).
  *Communications Physics* 9, 119. DOI: 10.1038/s42005-026-02584-w.
- van Westen, R. M., Börner, R., Dijkstra, H. A. (2026). *Nature Climate
  Change*. DOI: 10.1038/s41558-026-02730-w.
- Jacobson, T. (2016). "Entanglement Equilibrium and the Einstein
  Equation." *Phys. Rev. Lett.* 116, 201101. arXiv:1505.04753. (Note: an
  earlier draft of the source research mis-cited this via PubMed; corrected
  here per the fact-check pass.)
- Casini, H., Galante, D., Myers, R. C. (2016). "Comments on Jacobson's
  'Entanglement equilibrium and the Einstein equation'." *JHEP* 03, 194.
  arXiv:1601.00528. (Documented critique of Jacobson 2016's non-conformal
  assumption.)
- Cao, C., Carroll, S. M., Michalakis, S. (2017). "Space from Hilbert
  Space: Recovering geometry from bulk entanglement." *Phys. Rev. D* 95,
  024031. arXiv:1606.08444.
- Rosas, F. E. et al. (2020). "Reconciling emergences." *PLOS
  Computational Biology* 16, e1008289.
- Hoel, E. (2026). "Quantifying emergent complexity." *Patterns* 7,
  101472. arXiv:2503.13395 (preprint at time of first citation).
- Jansma, A., Hoel, E. (2025). "Engineering Emergence." Preprint,
  arXiv:2510.02649.
- Fontana, F. et al. (2024). "Pulsed electromagnetic field stimulation
  enhances neurite outgrowth in neural cells..." *Engineered
  Regeneration* 5, 80-91. DOI: 10.1016/j.engreg.2023.11.003.
