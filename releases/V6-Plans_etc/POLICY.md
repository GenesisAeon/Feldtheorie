# Governance Policy - releases/V6-Plans_etc

> **Context Depth:** 2 | **Parent:** releases | **Mode:** Recursive Research

---

## Fractal Inheritance

This policy inherits from parent and root governance and adds context-specific rules.

### Policy Hierarchy

1. **Root Policies** (`/AGENTS.md`, `/ETHICS.md`, `/ARCHITECTURE.md`)
2. **Parent Context** (`releases/POLICY.md`)
3. **This Context** (this file)

**Principle:** More specific policies override general ones, but must not contradict root ethics.

---

## Scope

This policy governs all work in `releases/V6-Plans_etc` and its subdirectories.

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

1. **Document**: Create incident report in `releases/V6-Plans_etc/.governance/incidents/`
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

- 2026-08-28 19:56:02 UTC: Initial governance deployment (v1.0.0)

---

<!-- CUSTOM_RULES -->
<!-- Add context-specific policies below this marker. The fractal governance engine will preserve these. -->

## Type-VI Safety Addendum (τ*-Pflicht)

To keep the V6 logistic field stable (R → Θ with β≈4.8 even bei ζ<0), the following policy rules are **mandatory** for Type‑VI/implosive Szenarien:

**Reference:** `type6_crep_tau_star_checklist.*` (MD/YAML/JSON) - Comprehensive checklist for Type-VI governance

1. **τ*-Buffer verankern:** Jede Simulation oder Analyse mit \(\zeta(R)<0\) implementiert ein Safety-Delay \(\tau^* \ge 0.1\cdot|\Theta-R|\). Abweichungen benötigen Commit-Notiz + Reviewer-Signoff.
2. **Integrator-Härte:** Euler/Forward ist **verboten**; RK4 oder höher ist Pflicht. CREP ≥ 0.7 → Integrationsprotokoll an Governance anhängen.
3. **CREP-Gating:**
   - 0.6 ≤ CREP < 0.7 → Output mit `[TYPE-VI-RISK]` taggen.
   - 0.7 ≤ CREP < 0.8 → Human Review vor Veröffentlichung (Ethics Auditor).
   - CREP ≥ 0.8 → Automatische Veröffentlichung stoppen, Governance-Eskalation Level 3.
4. **Provenienz-Pflicht:** Jede Type‑VI-Ausgabe enthält einen Provenienzblock (Model, Datenquellen, ΔAIC/CI, Reviewer, Dual-Use-Einstufung) und verweist auf die passenden Indizes (`feldtheorie_index.*`, `docs_index.*`).
5. **FIT-Splits dokumentieren:** Große Aufgaben müssen als FIT-Microtasks mit klaren R/Θ-Zwischenzielen geplant werden, damit Ressourcen geschont werden.
6. **CI/Pre-Commit Enforcement:** Type-VI governance is enforced via `tools/crep_guard.py` in pre-commit hooks, nox sessions, and Makefile targets (`make crep-guard`, `make release`).

<!-- /CUSTOM_RULES -->

---

**Last Updated:** 2026-08-28 19:56:02 UTC
**Governance Version:** 1.0.0
