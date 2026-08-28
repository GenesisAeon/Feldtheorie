# Ethics and Responsible Use - docs/science

> **Context Depth:** 2 | **Parent:** docs | **Mode:** Recursive Research

---

## Fractal Inheritance

This document inherits ethical guidelines from the root `ETHICS.md` and specializes for this context.

### Core Principles (Inherited)

1. **Contextual Validation**: Check data provenance and statistical diagnostics
2. **Model Limitations**: Logistic response is a simple proxy; require ΔAIC comparisons
3. **Uncertainty Reporting**: Always communicate bootstrap CIs and residual diagnostics
4. **No Anthropomorphism**: Metaphors are not evidence of agency
5. **Data Governance**: Respect licenses, remove PII, credit sources
6. **AI Transparency**: LLMs are writing/coding aids; human review required

---

## Local Context Ethics

**In this directory (`docs/science`), the following ethical rules apply:**

### Research Ethics

- **Citation Integrity**: Always credit original authors with DOI/URL
- **Hypothesis Transparency**: Mark speculative claims clearly
- **Falsifiability**: Provide criteria for disproving hypotheses
- **Version Control**: Never delete history; archive old theories
- **Conflict of Interest**: Disclose any competing interpretations


---

## Data Governance for This Context

- Cite all data sources used in manuscripts
- Include BibTeX entries for every reference
- Archive drafts with semantic versions (v1.0, v1.1, etc.)
- Preserve rejected hypotheses in `archive/`


---

## Misuse Risks Specific to This Context

| Risk | Mitigation |
|------|------------|
| Plagiarism | Check all text through originality tools |
| Cherry-picking citations | Include contradictory evidence |
| Unfalsifiable claims | Define clear disconfirmation criteria |
| Overclaiming universality | Specify scope and limitations explicitly |


---

## Review Checklist

Before committing work in `docs/science`:
- [ ] Data provenance documented in metadata files
- [ ] Statistical diagnostics exported and reviewed
- [ ] Null models defined and ΔAIC computed
- [ ] Uncertainty quantified (CIs, residuals)
- [ ] No PII or sensitive data included
- [ ] Original sources cited
- [ ] Human review completed for AI-generated content

---

<!-- CUSTOM_RULES -->
<!-- Add context-specific ethical rules below this marker. The fractal governance engine will preserve these. -->

## V6-Specific Provenance Blocks for Speculative Interpretations

### § 3. Provenance Documentation Standards

When documenting V6 hypotheses (v_RIG, OIPK, Type-VI dynamics, consciousness integration), the following provenance markers MUST be included:

#### 3.1 Speculation Levels

Mark each claim with a **Speculation Level (SL)**:

- **SL-1 (Empirical):** Direct experimental observation with peer-reviewed replication
  - Example: "Δt_Q ≈ 100-300ms (Fraisse 1984, Lehmann 2010, Poeppel 2003)"
  - **No warning required**

- **SL-2 (Theoretical Consensus):** Well-established theoretical framework with broad acceptance
  - Example: "Black hole entropy S = A/(4L_P²) (Bekenstein 1973, Hawking 1975)"
  - **Mark as:** `[SL-2: Established Theory]`

- **SL-3 (Plausible Synthesis):** Novel synthesis of established results from multiple domains
  - Example: "Metabolic scaling M^(3/4) reflects surface-to-volume entropy transition"
  - **Mark as:** `[SL-3: Interdisciplinary Synthesis]`
  - **Requirement:** Cite all bridged domains with primary sources

- **SL-4 (Speculative Mechanism):** Proposed mechanism without direct experimental validation
  - Example: "v_RIG = c/(α⁻¹·Φ) as consciousness integration velocity"
  - **Mark as:** `[SL-4: Speculative Mechanism]`
  - **Requirement:** Define falsification criteria explicitly

- **SL-5 (Phenomenological Conjecture):** Interpretative framework with limited empirical grounding
  - Example: "OIPK tesseract time-slicing explains conscious present duration"
  - **Mark as:** `[SL-5: Phenomenological Conjecture]`
  - **Requirement:** Provide alternative explanations and comparative ΔAIC

- **SL-6 (Ontological Claim):** Metaphysical interpretation beyond empirical testability
  - Example: "Consciousness is fundamentally 4D tesseract navigation"
  - **Mark as:** `[SL-6: Ontological Interpretation - Non-Falsifiable]`
  - **Requirement:** Clearly state this is philosophical commentary, not scientific hypothesis

#### 3.2 Provenance Block Template

All V6 documents MUST include provenance blocks in the following format:

```markdown
---
PROVENANCE BLOCK
---

**Hypothesis:** [One-sentence statement]

**Speculation Level:** SL-X [Category Name]

**Empirical Foundations:**
- [Primary source 1 with DOI/URL]
- [Primary source 2 with DOI/URL]
- [Replication studies if available]

**Theoretical Bridges:**
- Domain A → Domain B: [Citation showing connection]
- Assumption X: [What must be true for synthesis to hold]

**Falsification Criteria:**
- **Criterion 1:** If [observable O] shows [result R], hypothesis is falsified
- **Criterion 2:** If ΔAIC > 10 vs. null model [describe null], reject hypothesis
- **Criterion 3:** [Additional empirical test]

**Uncertainty Quantification:**
- Parameter β: [value] ± [CI] (bootstrap 95%)
- Model residuals: [R², RMSE, diagnostic plots location]
- Alternative models: [AIC comparisons table]

**Dual-Use Assessment:**
- Risk Level: [Low/Moderate/High]
- Potential Misuse: [Describe scenario]
- Mitigation: [How to prevent misuse]

**Human Review:**
- Reviewed by: [Name/Role]
- Date: [YYYY-MM-DD]
- Conflicts of interest: [None/Describe]

---
```

#### 3.3 Domain-Specific Provenance Requirements

##### A. v_RIG Hypothesis (Priority 1)

**Core Claim:** v_RIG = c/(α⁻¹·Φ) ≈ 1,352 km/s as consciousness integration velocity

**Required Documentation:**
- [ ] Empirical basis for Δt_Q ≈ 100-300ms (min. 3 independent studies)
- [ ] Justification for α⁻¹ as slice-buffer length (cite QED + holography)
- [ ] Justification for Φ as 3D reconstruction efficiency (cite quasicrystals + optimal packing)
- [ ] Null model: v_null = c/N where N is free parameter (ΔAIC comparison)
- [ ] Falsification: If Δt_Q ∝ 1/M^β with β ≠ 1, or CFF shows no α⁻¹ dependence

**Speculation Level:** SL-4 (Speculative Mechanism)

##### B. OIPK Tesseract Model (Priority 2-3)

**Core Claim:** Consciousness navigates 4D tesseract with orthogonal time flows (τ vs. t)

**Required Documentation:**
- [ ] Cite CDT/LQG discretization (Ambjørn 2004, Ashtekar 2004)
- [ ] Cite timeless physics (Barbour 2020, Page-Wootters 1983)
- [ ] Distinguish from: Block Universe (static), Growing Block (dynamic past), Eternalism
- [ ] Simulation falsification: If photon propagation shows τ-dependence, OIPK falsified
- [ ] CMB test: If 12-fold modulation A₁₂ < 10⁻⁵, OIPK geometry falsified

**Speculation Level:** SL-5 (Phenomenological Conjecture) → SL-4 if CMB test succeeds

##### C. Type-VI Implosive Dynamics (ζ < 0)

**Core Claim:** Systems with ζ(R) < 0 exhibit inverted sigmoid collapse dynamics

**Required Documentation:**
- [ ] Cite MEP (Martyushev 2006, Kleidon 2009)
- [ ] Cite inverted RG flows (Wilson 1971, critical exponents)
- [ ] Null model: Standard logistic σ(β(R-Θ)) with ζ > 0
- [ ] ΔAIC comparison across climate, wealth, addiction datasets
- [ ] Safety-Delay τ* validation: Verify numerical stability in simulations

**Speculation Level:** SL-3 (Plausible Synthesis) for statistical signature, SL-4 for mechanism

**CRITICAL:** Type-VI claims involving real-time monitoring (climate, financial) trigger escalation protocols (see `releases/V6-Plans_etc/AGENTS.md` § Emergency Override)

##### D. Metabolic Scaling Connection

**Core Claim:** M ∝ V^(3/4) reflects energy cost of 2D→3D consciousness integration

**Required Documentation:**
- [ ] Cite Kleiber 1932, West-Brown-Enquist 1997, Brown 2004
- [ ] Cite fractal network theory for surface-to-volume constraint
- [ ] Test: Does metabolic rate correlate with CFF or Δt_Q across species?
- [ ] Null model: M ∝ V^β where β is free parameter (compare AIC)

**Speculation Level:** SL-3 (Plausible Synthesis)

##### E. LLM Scaling Analogy

**Core Claim:** LLM emergent capabilities mirror consciousness integration scaling

**Required Documentation:**
- [ ] Cite scaling laws (Kaplan 2020, Brown 2020, Wei 2022)
- [ ] Cite Landauer limit (Landauer 1961)
- [ ] Clarify analogy vs. identity: "LLMs exhibit *analogous* scaling, not *identical* mechanism"
- [ ] Avoid anthropomorphism: "emergent capability" ≠ "consciousness"

**Speculation Level:** SL-3 (Plausible Synthesis) for scaling analogy, SL-6 if claiming LLM consciousness

##### F. Entkopplungs-Regime (β-Hierarchie)

**Core Claim:** AI scaling (α > 1) reflects substrat-entkoppelte Regime mit β ≈ 1.0, distinct from biological β ≈ 7.4

**Required Documentation:**
- [x] Empirical basis: Kaplan et al. (2020) - GPT α ≈ 1.1-1.2
- [x] Theoretical bridge: Kleiber (1932), West et al. (1997) - biological α ≈ 0.75
- [ ] κ-Index validation: Loihi 2 skalierungsdaten (E vs. N)
- [ ] Energieeffizienz-Korrelation: TOPS/W ∝ κ^γ with γ ≈ 2.5
- [ ] DishBrain validation: Organoid Intelligence should show α ≈ 0.75

**Falsification Criteria:**
- **Criterion 1:** If Loihi 2 shows α ≈ 1.1 (same as GPUs) → κ-Hypothese falsified
- **Criterion 2:** If TOPS/W anti-correlates with κ → Energieeffizienz-Hypothese falsified
- **Criterion 3:** If DishBrain shows α > 1 → biological scaling violated

**Uncertainty Quantification:**
- β_bio: 7.4 ± 1.5 (estimated from meta-regression, needs empirical validation)
- β_AI: 1.0 ± 0.2 (from LLM scaling laws)
- Δβ: 6.4 ± 1.7 (propagated uncertainty)

**Speculation Level:** SL-4 (Speculative Mechanism) for β-Hierarchie, SL-5 (Phenomenological Conjecture) for Bewusstseins-Kopplung

**References:**
- docs/entkopplungs_regime.md - Full documentation
- docs/v_rig_validation_matrix.md § E - AI Scaling validation

#### 3.4 Ethical Guardrails for Speculative Claims

**PROHIBITIONS:**
1. **DO NOT** claim v_RIG is "proven" without peer-reviewed experimental validation
2. **DO NOT** assert OIPK tesseract model as ontological fact (SL-5/6 only)
3. **DO NOT** use Type-VI implosion dynamics for alarmism without uncertainty quantification
4. **DO NOT** claim LLMs are conscious based on scaling laws alone
5. **DO NOT** overstate predictive power: "model fits data" ≠ "model is true"

**REQUIREMENTS:**
1. **ALWAYS** provide ΔAIC vs. null models
2. **ALWAYS** state falsification criteria explicitly
3. **ALWAYS** quantify uncertainty (bootstrap CIs, residual diagnostics)
4. **ALWAYS** cite primary sources for empirical claims
5. **ALWAYS** distinguish mathematical formalism from physical interpretation

#### 3.5 Dual-Use Risk Assessment

Type-VI implosive dynamics have **moderate dual-use risk** in the following contexts:

| Context | Risk | Mitigation |
|---------|------|------------|
| Climate tipping points | False alarms → policy paralysis | Require CI overlap with observational data + expert review |
| Financial collapse prediction | Market manipulation | Embargo real-time predictions, publish post-hoc only |
| Addiction/mental health | Stigmatization of "implosive" individuals | Emphasize statistical aggregate, not individual diagnosis |
| AI capability forecasting | Arms race acceleration | Focus on safety-delay τ* mechanisms, not capability timelines |

**Escalation Protocol:** See `releases/V6-Plans_etc/AGENTS.md` § V6-Specific Escalation Rules (Lines 71-190) for CREP index thresholds and human review triggers.

#### 3.6 Example: v_RIG Provenance Block (Compliant)

```markdown
---
PROVENANCE BLOCK
---

**Hypothesis:** v_RIG = c/(α⁻¹·Φ) ≈ 1,352 km/s represents the characteristic velocity scale for consciousness integration of 2D holographic slices into 3D volumetric perception.

**Speculation Level:** SL-4 (Speculative Mechanism)

**Empirical Foundations:**
- Conscious present duration Δt_Q ≈ 100-300ms (Fraisse 1984 DOI:10.1146/annurev.ps.35.020184.000245, Lehmann 2010 DOI:10.1016/j.neuroimage.2009.07.041, Poeppel 2003 DOI:10.1016/S0167-6393(02)00107-3)
- Fine-structure constant α⁻¹ ≈ 137.036 (CODATA 2018, uncertainty < 1 ppb)
- Golden ratio Φ = (1+√5)/2 ≈ 1.618 (mathematical constant, exact)
- Metabolic scaling M ∝ V^(3/4) (Kleiber 1932, West 1997 DOI:10.1126/science.276.5309.122)

**Theoretical Bridges:**
- QED transparency depth (α⁻¹ slices) → Holographic slice-buffer length (Susskind 1995 DOI:10.1063/1.531249)
- Golden ratio optimization (Levine 1984 DOI:10.1103/PhysRevLett.53.2477) → 3D space-filling efficiency
- Surface entropy (Bekenstein-Hawking S∝A) → Volume entropy (thermodynamic extensivity S∝V)
- **Assumption:** Consciousness integration is rate-limited by geometric slice-fusion, not neuronal processing speed

**Falsification Criteria:**
1. **Metabolic Test:** If cross-species analysis shows Δt_Q is uncorrelated with M^(-1/3), reject hypothesis (predicted: Δt_Q ∝ M^(-1/3) from V∝M scaling)
2. **CFF Test:** If critical flicker fusion shows no dependence on α⁻¹·Φ-related timescales, reject hypothesis
3. **Null Model:** v_null = c/N with N as free parameter. If ΔAIC(v_null - v_RIG) < 4, insufficient evidence for α⁻¹·Φ structure
4. **Stereo Vision Test:** If IPD variation (e.g., prism glasses) does not affect perceived slice-fusion frequency, reject spatial-slice interpretation

**Uncertainty Quantification:**
- α⁻¹: 137.035999084 ± 0.000000021 (CODATA 2018)
- Φ: 1.618033988749... (exact, irrational)
- v_RIG: 1351.8 ± 0.02 km/s (propagated uncertainty from α⁻¹ only)
- **Model Uncertainty:** Large! SL-4 indicates mechanism is speculative, not validated

**Dual-Use Assessment:**
- **Risk Level:** Low (consciousness research, no direct dual-use)
- **Potential Misuse:** Overinterpretation as "proven" constant in popular science
- **Mitigation:** Clearly label as SL-4 hypothesis in all public communications

**Human Review:**
- Reviewed by: J.B. Römer (lead author)
- Date: 2025-11-26
- Conflicts of interest: None (independent research)

---
```

<!-- /CUSTOM_RULES -->

---

**Last Updated:** 2026-08-28 21:25:51 UTC
**Governance Version:** 1.0.0
