# Governance Policy - seed/V4-Grundlagen

> **Context Depth:** 2 | **Parent:** seed | **Mode:** Recursive Research

---

## Fractal Inheritance

This policy inherits from parent and root governance and adds context-specific rules.

### Policy Hierarchy

1. **Root Policies** (`/AGENTS.md`, `/ETHICS.md`, `/ARCHITECTURE.md`)
2. **Parent Context** (`seed/POLICY.md`)
3. **This Context** (this file)

**Principle:** More specific policies override general ones, but must not contradict root ethics.

---

## Scope

This policy governs all work in `seed/V4-Grundlagen` and its subdirectories.

**Mode:** Recursive Research

---

## Operational Rules

### Research Policy

1. **Trilayer Sync**: All major docs exist in YAML/JSON/MD
2. **Citation Required**: Every claim backed by reference or data
3. **Hypothesis Registry**: Testable claims logged in `hypotheses/`
4. **Peer Review**: Pre-publication review by independent agent
5. **Archival**: Old versions preserved in `archive/` with timestamps


---

## Quality Gates

Before committing changes in this context:

- [ ] Citations complete (DOI/URL for every reference)
- [ ] BibTeX entries formatted correctly
- [ ] Hypotheses marked as testable/speculative
- [ ] Trilayer documents synchronized
- [ ] Indices updated (seed_index, docs_index, etc.)
- [ ] Cross-references validated
- [ ] No broken links


---

## Automation Hooks

- **Pre-commit**: Check for broken links and missing citations
- **CI Pipeline**: Validate Trilayer synchronization
- **Weekly**: Re-index all documentation
- **Release**: Generate DOI, archive with Zenodo


---

## Incident Response

If governance violations occur:

1. **Document**: Create incident report in `seed/V4-Grundlagen/.governance/incidents/`
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

- 2025-11-23 17:21:06 UTC: Initial governance deployment (v1.0.0)

---

<!-- CUSTOM_RULES -->
<!-- Add context-specific policies below this marker. The fractal governance engine will preserve these. -->

<!-- /CUSTOM_RULES -->

---

**Last Updated:** 2025-11-23 17:21:06 UTC
**Governance Version:** 1.0.0
