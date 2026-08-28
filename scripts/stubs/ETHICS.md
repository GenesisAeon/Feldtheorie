# Ethics and Responsible Use - scripts/stubs

> **Context Depth:** 2 | **Parent:** scripts | **Mode:** Recursive Programming

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

**In this directory (`scripts/stubs`), the following ethical rules apply:**

### Code Ethics

- **No hardcoded secrets**: Use environment variables or secret managers
- **Dependency hygiene**: Pin versions, audit for vulnerabilities
- **Licensing compliance**: Respect open-source licenses (see LICENSE file)
- **Accessibility**: Consider edge cases, error handling, and user feedback
- **Attribution**: Credit external libraries and algorithms properly


---

## Data Governance for This Context

- Configuration files must not contain PII or API keys
- Test fixtures should use synthetic or anonymized data
- Log outputs must redact sensitive information


---

## Misuse Risks Specific to This Context

| Risk | Mitigation |
|------|------------|
| Command injection | Sanitize all user inputs; use parameterized APIs |
| XSS vulnerabilities | Escape HTML; use Content Security Policy |
| SQL injection | Use ORMs or parameterized queries |
| Insecure dependencies | Run `pip-audit` or `npm audit` regularly |


---

## Review Checklist

Before committing work in `scripts/stubs`:
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

**Last Updated:** 2026-08-28 21:35:45 UTC
**Governance Version:** 1.0.0
