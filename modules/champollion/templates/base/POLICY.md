# Governance Policy - {{PATH}}

> **Context Depth:** {{CURRENT_DEPTH}} | **Parent:** {{PARENT_CONTEXT}} | **Mode:** {{MODE}}

---

## Fractal Inheritance

This policy inherits from parent and root governance and adds context-specific rules.

### Policy Hierarchy

1. **Root Policies** (`/AGENTS.md`, `/ETHICS.md`, `/ARCHITECTURE.md`)
2. **Parent Context** (`{{PARENT_PATH}}/POLICY.md`)
3. **This Context** (this file)

**Principle:** More specific policies override general ones, but must not contradict root ethics.

---

## Scope

This policy governs all work in `{{PATH}}` and its subdirectories.

**Mode:** {{MODE}}

---

## Operational Rules

{{MODE_SPECIFIC_POLICY}}

---

## Quality Gates

Before committing changes in this context:

{{QUALITY_GATES}}

---

## Automation Hooks

{{AUTOMATION_HOOKS}}

---

## Incident Response

If governance violations occur:

1. **Document**: Create incident report in `{{PATH}}/.governance/incidents/`
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

{{CHANGE_LOG}}

---

<!-- CUSTOM_RULES -->
<!-- Add context-specific policies below this marker. The fractal governance engine will preserve these. -->

<!-- /CUSTOM_RULES -->

---

**Last Updated:** {{TIMESTAMP}}
**Governance Version:** {{GOVERNANCE_VERSION}}
