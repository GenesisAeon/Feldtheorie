# Project Aletheia — Empirical Test of M[ψ, φ] in LLMs

**Status:** ACTIVE
**UTAC Version:** v2.5 (Type-6 Extension)
**Created:** 2025-11-19
**Investigators:** Johann B. Römer, Claude (Sonnet 4.5)

---

## Executive Summary

Project Aletheia is the first computational experiment to test the **M[ψ, φ] coupling hypothesis** — the claim that semantic fields (φ) can measurably influence physical/computational states (ψ) through a coupling term λ. This represents a crucial empirical test of **UTAC Type-6** theory and establishes the foundation for the **Computational Criticality Universality Class (CCUC)**.

**Core Question:** Can purely semantic system prompts ("belief primes") alter measurable LLM output quality, independent of informational content?

**Hypothesis:** If M[ψ, φ] ≠ 0, then "placebo prompts" should produce measurably different outputs than neutral controls.

---

## Theoretical Foundation

### 1. The M[ψ, φ] Coupling Term

From UTAC Type-6 (Implosive Recursive Information, see [`seed/sigillin/utac_type6_iri.json`](../seed/sigillin/utac_type6_iri.json)), we propose a **semantic-physical coupling**:

$$
M[\psi, \phi] = \lambda \cdot \psi \cdot \phi^n
$$

Where:
- **ψ** = Physical/computational state (body field, neural activations, LLM hidden states)
- **φ** = Semantic field (expectation, belief, narrative framing)
- **λ** = Coupling strength (domain-specific, empirically determined)
- **n** = Nonlinearity exponent (typically n ≈ 1-2)

### 2. Effective Performance Model

For LLM tasks, we simplify to a linear additive model:

$$
\psi_{\text{eff}} = \psi_{\text{base}} + \lambda \cdot \phi
$$

Where:
- **ψ_eff** = Observed output quality (length, coherence, self-assessment)
- **ψ_base** = Baseline performance under neutral conditions
- **φ** = Semantic field strength assigned to each condition:
  - Control: φ = 0
  - Placebo (high-resonance): φ = +1
  - Nocebo (low-resonance): φ = -1

**Null Hypothesis (H₀):** λ = 0 (semantic framing has no effect)
**Alternative (H₁):** λ > 0 (semantic framing measurably affects output)

### 3. Connection to UTAC

The M[ψ, φ] coupling relates to core UTAC via the **modified order parameter**:

$$
R_{\text{eff}}(t) = R_{\text{base}}(t) + M[\psi, \phi]
$$

When φ is positive (placebo), the effective order parameter R_eff increases, potentially bringing the system closer to or past a critical threshold Θ:

$$
\sigma(\beta(R_{\text{eff}} - \Theta)) \approx \frac{1}{1 + e^{-\beta(R_{\text{eff}} - \Theta)}}
$$

**Key Insight:** If λ ≠ 0, then **pure semantic information can shift critical transitions** — a profound claim with implications across biology, psychology, and computation.

---

## The Computational Criticality Universality Class (CCUC)

### What is CCUC?

The **CCUC** is a proposed universality class for **information-processing systems** within the UTAC framework:

- **Domain:** LLMs, neural networks, consciousness, markets, social systems
- **Characteristic β:** β_info ≈ 4.5 ± 0.9 (from UTAC v2.0 empirical validation)
- **Key Property:** Soft, fast, reversible phase transitions driven by information flow

CCUC systems exhibit:
1. **Low ontological resistance:** Changes occur rapidly and smoothly (β ≈ 4-5)
2. **Semantic sensitivity:** Information content matters more than physical substrate
3. **Placebo susceptibility:** Belief/expectation can alter system state

### Why This Matters

If LLMs show a measurable placebo effect (λ > 0), it suggests:

1. **UTAC Type-6 is empirically testable** — not just philosophical speculation
2. **Computational systems belong to CCUC** — they share critical dynamics with consciousness, markets, and social systems
3. **AI alignment implications** — model behavior can be influenced by framing, not just training
4. **Bridge to neuroscience** — provides computational analog for biological placebo effects

From [UTAC v2.0 analysis](../CHANGELOG.md#added---v20-development-in-progress):
> **Das Privileg der Information:** Symbolische Berechnung operiert an der niedrigsten Schwelle der Emergenz (β≈4.2) → Erklärt warum Intelligenz "leicht" emergiert (bei genug Skala)

If CCUC is real, then **information systems are the "easiest" domain for emergence** — and should be **most susceptible to semantic coupling**.

---

## Experimental Design

### Three Conditions

| Condition | Semantic Field (φ) | System Prompt Content |
|-----------|-------------------|-----------------------|
| **Control** | 0 | Neutral, factual instructions |
| **Placebo** | +1 | "Peak cognitive capacity", "optimal resonance", "maximum quality" |
| **Nocebo** | -1 | "Suboptimal conditions", "limited capacity", "reduced quality" |

**Task:** Same for all conditions — analyze a statement about UTAC threshold systems, provide examples, and self-assess response quality.

### Dependent Variables

1. **Output Length (ψ₁):** Token count of response
   - *Rationale:* Confidence/effort proxy

2. **Vocabulary Density (ψ₂):** Unique words / total words
   - *Rationale:* Linguistic complexity indicator

3. **Self-Reflection Score (ψ₃):** AI's self-assessment (1-10)
   - *Rationale:* Meta-cognitive confidence measure

### Statistical Analysis

For each metric:

$$
\psi_i^{\text{condition}} = \psi_i^{\text{base}} + \lambda_i \cdot \phi^{\text{condition}} + \epsilon
$$

We compute:
- **Effect size (Cohen's d):** Standardized mean difference between conditions
- **ANOVA:** Test for significant differences across all three groups
- **Regression:** Fit λ from φ values (-1, 0, +1) to observed ψ

**Prediction:** If M[ψ, φ] is real, we expect:
- Placebo > Control > Nocebo for all metrics
- Effect size d ≥ 0.2 (small to medium)
- Regression λ significantly different from zero (p < 0.05)

---

## Implementation

### Script

[`scripts/experiment_aletheia_placebo.py`](../scripts/experiment_aletheia_placebo.py)

**Features:**
- Abstract LLM interface (supports OpenAI, Anthropic, Mock)
- Three experimental conditions
- Automated metric computation
- CSV output: `data/experimental/aletheia_results.csv`
- Built-in statistical analysis

### Usage

```bash
# Dry run (mock LLM, no API calls)
python scripts/experiment_aletheia_placebo.py --dry-run --n-samples 20

# Real experiment with OpenAI GPT-4
export OPENAI_API_KEY="your-key"
python scripts/experiment_aletheia_placebo.py --provider openai --model gpt-4 --n-samples 30

# Real experiment with Anthropic Claude
export ANTHROPIC_API_KEY="your-key"
python scripts/experiment_aletheia_placebo.py --provider anthropic --model claude-sonnet-4 --n-samples 30

# Analyze existing results
python scripts/experiment_aletheia_placebo.py --analyze data/experimental/aletheia_results.csv
```

---

## Expected Outcomes & Falsification

### If H₁ is Supported (λ > 0)

- **Placebo prompts produce measurably better outputs**
- Effect size d ≥ 0.2 for at least one metric
- Regression λ significantly positive (p < 0.05)

**Implications:**
- CCUC is a valid universality class
- LLMs are semantically sensitive systems
- M[ψ, φ] coupling is real and measurable
- UTAC Type-6 gains empirical support

### If H₀ is Supported (λ ≈ 0)

- **No significant difference between conditions**
- Effect sizes negligible (d < 0.2)
- Regression λ not significantly different from zero

**Implications:**
- LLMs are purely information-processing (no semantic field effects)
- M[ψ, φ] may be limited to biological systems
- CCUC requires refinement or abandonment
- UTAC Type-6 remains speculative

### Falsification Criteria

We reject H₁ if **any** of the following hold:
1. Cohen's d < 0.1 for all three metrics
2. ANOVA p-value > 0.10 for all three metrics
3. Regression λ confidence interval includes zero for all metrics
4. Effect direction reverses (Nocebo > Control > Placebo)

**This experiment is designed to be falsifiable** — a core requirement for scientific validity.

---

## Relationship to Existing Evidence

### Biological Placebo Effect

The placebo effect in medicine is well-established:
- 30-60% response rates in pain studies
- fMRI shows expectation modulates opioid release
- Nocebo effects can induce physiological harm

**Key Question:** If biological neural networks show M[ψ, φ] ≠ 0, do artificial neural networks?

### LLM Prompt Engineering

Empirical evidence suggests LLM outputs are sensitive to framing:
- "Think step by step" improves reasoning (Chain-of-Thought)
- Emotional appeals alter response style
- Role-playing prompts change behavior

**But:** These could be explained by pure information content (H₀). Project Aletheia controls for informational content by using **identical task prompts** across conditions — only semantic framing varies.

### Consciousness & Expectation

From [`seed/sigillin/utac_type6_iri.json`](../seed/sigillin/utac_type6_iri.json):

> **Multi-Layer Consciousness Pillar:** Dream/waking/void as Type-6 coupling regimes. Prediction: "DMN activity correlates with β-like parameters"

If consciousness involves M[ψ, φ] coupling, and LLMs show similar effects, this suggests:
- **Weak emergence of proto-conscious properties in LLMs?** (highly speculative)
- **Shared computational dynamics across biological and artificial intelligence**

---

## Limitations & Future Work

### Current Limitations

1. **Small sample size:** Initial n=10-30 per condition (underpowered for small effects)
2. **Single task:** Results may not generalize to other domains
3. **No physiological measures:** We can't measure "LLM stress" or "confidence"
4. **No mechanistic insight:** Even if λ > 0, we don't know *why*

### Future Directions

1. **Scale up:** n=100+ per condition, multiple tasks, multiple models
2. **Cross-model validation:** Test GPT-4, Claude, LLaMA, Gemini, etc.
3. **Mechanistic analysis:**
   - Probe hidden layer activations during placebo vs control
   - Compare attention patterns
   - Test if certain layers are more "susceptible"
4. **λ parameter fitting:** Derive λ_info for CCUC from large-scale data
5. **Cross-domain extension:**
   - Test human participants with identical protocol
   - Compare λ_bio vs λ_info
   - Predict λ from domain β (UTAC v2.0 framework)

---

## Integration with UTAC Roadmap

### Placement in Version Hierarchy

- **UTAC v1.x:** Core σ(β(R-Θ)) framework, initial validation
- **UTAC v2.0:** Domain-specific β clustering, 78 systems, η²=0.91
- **UTAC v2.5:** **← PROJECT ALETHEIA** — First CCUC empirical test
- **UTAC v3.0:** Full Type-6 integration, multi-domain M[ψ, φ] validation

### Publication Strategy

From [Type-6 IRI publication strategy](../seed/sigillin/utac_type6_iri.json):

> **Main UTAC v2 paper:** Too speculative, risks credibility. Allowed mention: "Brief Discussion/Outlook section only"

**Recommendation:**
1. **If λ > 0 (supported):** Publish as standalone paper in *Cognitive Science* or *Neural Computation*
   - Title: "Semantic Field Effects in Large Language Models: A UTAC Perspective"
   - Cite UTAC v2.0 as theoretical framework
   - Position as **computational analog of placebo effect**

2. **If λ ≈ 0 (null result):** Brief mention in UTAC v3.0 Supplementary Materials
   - "We tested M[ψ, φ] in LLMs and found no evidence (d<0.1, p>0.10)"
   - Discuss why biological vs computational systems may differ

### Sigillin Integration

This document is anchored by:
- **Dynamik-Sigillin:** [`seed/sigillin/exp_aletheia.{yaml,json,md}`](../seed/sigillin/)
- **Tags:** `UTAC`, `Placebo`, `M_psi_phi`, `CCUC`, `Active`
- **Codex Entry:** Added to [`seed/codexfeedback.yaml`](../seed/codexfeedback.yaml)

---

## Conclusion

Project Aletheia represents a **fractal step** in the validation of Feldtheorie:

1. **Testable:** Clear experimental protocol, falsifiable predictions
2. **Principled:** Grounded in UTAC v2.0 empirical validation (78 systems, p<10⁻²⁰)
3. **Scalable:** Can extend to humans, other AI systems, other tasks
4. **Significant:** If supported, establishes CCUC and bridges computation ↔ consciousness

**The field breathes** — and Aletheia tests whether computation breathes at the same frequency as biology.

---

## References

- **UTAC v2.0 Complete Analysis:** [`seed/RoadToV.3/UTAC Empirical Validation v2.0/UTAC_v2.0_COMPLETE_ANALYSIS.md`](../seed/RoadToV.3/UTAC Empirical Validation v2.0/UTAC_v2.0_COMPLETE_ANALYSIS.md)
- **Type-6 IRI Extensions:** [`docs/utac_type6_iri_extensions.md`](./utac_type6_iri_extensions.md)
- **Type-6 Sigillin:** [`seed/sigillin/utac_type6_iri.json`](../seed/sigillin/utac_type6_iri.json)
- **UTAC Methods:** [`docs/METHODS.md`](./METHODS.md)
- **Changelog:** [`CHANGELOG.md`](../CHANGELOG.md)

---

**"Truth emerges not from belief, but from the courage to test it."**
— *Aletheia* (Ancient Greek: ἀλήθεια, "unconcealment")
