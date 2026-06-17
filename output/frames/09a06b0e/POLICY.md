# Governance Policy - output/frames/09a06b0e

> **Context Depth:** 3 | **Parent:** output/frames | **Mode:** Recursive Data Analysis

---

## Fractal Inheritance

This policy inherits from parent and root governance and adds context-specific rules.

### Policy Hierarchy

1. **Root Policies** (`/AGENTS.md`, `/ETHICS.md`, `/ARCHITECTURE.md`)
2. **Parent Context** (`output/frames/POLICY.md`)
3. **This Context** (this file)

**Principle:** More specific policies override general ones, but must not contradict root ethics.

---

## Scope

This policy governs all work in `output/frames/09a06b0e` and its subdirectories.

**Mode:** Recursive Data Analysis

---

## Operational Rules

### Data Policy

1. **Metadata Mandatory**: No data without `.metadata.json`
2. **Immutable Raw Data**: Never modify files in `raw/`
3. **Versioned Outputs**: Tag processed datasets with semantic versions
4. **Statistical Rigor**: Always compute ΔAIC and bootstrap CIs
5. **Privacy Compliance**: PII removal audited before commit


---

## Quality Gates

Before committing changes in this context:

- [ ] Metadata file exists and is complete
- [ ] Data provenance documented (source, license, date)
- [ ] No PII in committed files
- [ ] Null models defined and tested
- [ ] Statistical diagnostics exported (ΔAIC, R², residuals)
- [ ] Stochastic seeds logged
- [ ] Confidence intervals computed


---

## Automation Hooks

- **Pre-commit**: Scan for PII (email, SSN, names)
- **CI Pipeline**: Validate metadata schemas
- **Nightly**: Re-run key analyses with different seeds
- **Release**: Archive datasets with DOI (Zenodo integration)


---

## Incident Response

If governance violations occur:

1. **Document**: Create incident report in `output/frames/09a06b0e/.governance/incidents/`
2. **Escalate**: Notify in root `GOVERNANCE_REPORT.md`
3. **Remediate**: Fix violation and update this policy
4. **Review**: Parent context reviews and approves changes

---

## Policy Evolution

This policy can be updated by:
- Local agents (with documentation in CUSTOM_RULES)
- Parent context governance review
- Root governance mandate

**Change Log:**

- 2026-06-17 06:32:02 UTC: Initial governance deployment (v1.0.0)

---

<!-- CUSTOM_RULES -->
<!-- Add context-specific policies below this marker. The fractal governance engine will preserve these. -->

<!-- /CUSTOM_RULES -->

---

**Last Updated:** 2026-06-17 06:32:02 UTC
**Governance Version:** 1.0.0
