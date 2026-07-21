# Ethics and Responsible Use - output/frames/1ab225b7

> **Context Depth:** 3 | **Parent:** output/frames | **Mode:** Recursive Data Analysis

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

**In this directory (`output/frames/1ab225b7`), the following ethical rules apply:**

### Data Ethics

- **Open Data Only**: Use only openly licensed datasets (CC-BY, CC0, etc.)
- **Provenance Required**: Every dataset must have a `.metadata.json` file
- **Privacy First**: Remove PII before ingestion; anonymize if necessary
- **Uncertainty Transparency**: Report confidence intervals, p-values, ΔAIC
- **Null Models**: Always compare against baseline (linear, power law, etc.)


---

## Data Governance for This Context

- All datasets must include `*.metadata.json` with:
  - Source URL and license
  - Date of acquisition
  - Preprocessing steps
  - Known limitations
- Raw data is immutable (store in `data/raw/`)
- Processed data is versioned (store in `data/processed/vX.Y/`)
- Personal identifiers are NEVER committed


---

## Misuse Risks Specific to This Context

| Risk | Mitigation |
|------|------------|
| P-hacking | Pre-register hypotheses; document all tests run |
| Cherry-picking | Report all models tested, including null models |
| Data leakage | Use strict train/test splits; never touch test data |
| Overfitting | Cross-validate; report out-of-sample metrics |
| License violations | Check and document licenses in metadata |


---

## Review Checklist

Before committing work in `output/frames/1ab225b7`:
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

<!-- /CUSTOM_RULES -->

---

**Last Updated:** 2026-07-21 18:28:20 UTC
**Governance Version:** 1.0.0
