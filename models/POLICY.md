# Governance Policy - science/models

> **Context Depth:** 2 | **Parent:** / | **Mode:** Recursive Programming

---

## Fractal Inheritance

This policy inherits from parent and root governance and adds context-specific rules.

### Policy Hierarchy

1. **Root Policies** (`/AGENTS.md`, `/ETHICS.md`, `/ARCHITECTURE.md`)
2. **Parent Context** (`//POLICY.md`)
3. **This Context** (this file)

**Principle:** More specific policies override general ones, but must not contradict root ethics.

---

## Scope

This policy governs all work in `science/models` and its subdirectories.

**Mode:** Recursive Programming

---

## Operational Rules

### Code Policy

1. **Test Coverage**: Minimum 80% for new code
2. **Code Review**: All PRs require review by at least one other agent
3. **Linting**: Code must pass `pylint`, `black`, `mypy` (Python) or equivalent
4. **Documentation**: Public APIs must have docstrings with type hints
5. **Commit Hygiene**: Use conventional commits (feat:, fix:, docs:, etc.)


---

## Quality Gates

Before committing changes in this context:

- [ ] All tests pass (`pytest`, `unittest`, etc.)
- [ ] Linters report no errors
- [ ] Type hints added (Python 3.9+)
- [ ] Docstrings complete for public functions
- [ ] No hardcoded secrets or API keys
- [ ] CHANGELOG updated


---

## Automation Hooks

- **Pre-commit**: Run linters and formatters
- **CI Pipeline**: Execute full test suite on push
- **Nightly**: Security audit of dependencies
- **Release**: Automated version tagging and deployment


---

## Incident Response

If governance violations occur:

1. **Document**: Create incident report in `science/models/.governance/incidents/`
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

- 2026-08-28 20:00:22 UTC: Initial governance deployment (v1.0.0)

---

<!-- CUSTOM_RULES -->
<!-- Add context-specific policies below this marker. The fractal governance engine will preserve these. -->

<!-- /CUSTOM_RULES -->

---

**Last Updated:** 2026-08-28 20:00:22 UTC
**Governance Version:** 1.0.0
