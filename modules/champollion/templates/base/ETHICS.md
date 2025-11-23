# Ethics and Responsible Use - {{PATH}}

> **Context Depth:** {{CURRENT_DEPTH}} | **Parent:** {{PARENT_CONTEXT}} | **Mode:** {{MODE}}

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

**In this directory (`{{PATH}}`), the following ethical rules apply:**

{{MODE_SPECIFIC_ETHICS}}

---

## Data Governance for This Context

{{DATA_GOVERNANCE_RULES}}

---

## Misuse Risks Specific to This Context

{{MISUSE_RISKS}}

---

## Review Checklist

Before committing work in `{{PATH}}`:
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

**Last Updated:** {{TIMESTAMP}}
**Governance Version:** {{GOVERNANCE_VERSION}}
