# Agents Charter - releases/V6-Plans_etc

> **Context Depth:** 2 | **Parent:** releases | **Mode:** Recursive Research

---

## Fractal Inheritance

This document inherits from the root `AGENTS.md` and specializes for this context.

### Core Principles (Inherited)

1. **Trilayer Principle**: Every artifact exists as YAML (structure) + JSON (interface) + Markdown (narrative)
2. **Logistic Language**: Reference $(R, \Theta, \beta, \zeta(R))$ and the transition via $\sigma(\beta(R-\Theta))$
3. **Coupling Obligation**: Link Bedeutungs-Sigillin to Ordnungs-Sigillin and empirical evidence
4. **Falsifiability**: Every claim needs null models and ΔAIC/CI metrics
5. **Consent Protocol**: Permission requests and joyful collaboration

---

## Local Context

**This directory (`releases/V6-Plans_etc`) is specialized for:**

### Research Context

This is a **research and documentation context**. Agents working here focus on:
- Hypothesis formation and falsifiability
- Citation integrity and attribution
- Theoretical consistency
- Knowledge preservation and archiving
- Publication readiness

**Active Agent Roles:**
- Research Synthesizer: Integrates findings across domains
- Documentation Curator: Maintains indices, cross-references
- Citation Manager: Ensures proper attribution (BibTeX, DOI)
- Archivist: Versions and preserves historical knowledge


---

## Active Agents in This Context

See mode-specific agents above

---

## Workflow for This Context

1. **Before writing:** Review existing documentation, check citations
2. **During writing:** Link to evidence, cite sources, mark hypotheses
3. **After writing:** Update indices, cross-link Sigillin, sync Trilayer
4. **Pre-commit:** Ensure Trilayer sync (YAML/JSON/MD), citations complete


---

## Escalation Rules

If you encounter conflicts or ambiguity:
1. Check the parent governance: `releases/AGENTS.md`
2. Consult root governance: `/AGENTS.md`
3. Document deviations in local `<!-- CUSTOM_RULES -->` blocks

---

<!-- CUSTOM_RULES -->
<!-- Add context-specific rules below this marker. The fractal governance engine will preserve these. -->

## V6-Specific Escalation Rules for Type-VI (ζ < 0) Scenarios

### Implosive Dynamics Detection Protocol

When agents detect **negative damping** (\(\zeta(R) < 0\)) or **CREP index ≥ 0.6**:

#### Level 1: Automated Warning (CREP 0.6-0.7)
- **Agent Action:** Flag analysis with `[TYPE-VI-RISK]` tag
- **Documentation:** Add warning banner to all outputs
- **Notification:** Log to `logs/type_vi_detections.jsonl`
- **No escalation required** if within research context

#### Level 2: Human Review Required (CREP 0.7-0.8)
- **Agent Action:** Halt automated publication/deployment
- **Notification:** Ping designated human reviewer (see `MAINTAINERS.md`)
- **Documentation:** Generate full provenance report including:
  - Data sources and preprocessing steps
  - Null model comparisons (ΔAIC, R²)
  - Uncertainty quantification (bootstrap CIs)
  - Dual-use risk assessment
- **Timeline:** Human review within 48 hours

#### Level 3: Critical Escalation (CREP ≥ 0.8)
- **Agent Action:** IMMEDIATE HALT of all automated processes
- **Notification:** Multi-channel alert:
  - Email to governance@[repository]
  - Slack/Discord notification to #critical-alerts
  - GitHub issue with `CRITICAL-REVIEW` label
- **Documentation:** Full ethics review required (see `ETHICS.md` §4)
- **Timeline:** Human review within 24 hours
- **Intervention Assessment:** If real-time monitoring context:
  - Evaluate stakeholder notification obligations
  - Assess disclosure vs. mitigation tradeoffs
  - Consult external ethics board if available

### Negative Damping (\(\zeta < 0\)) Computational Safeguards

When simulating systems with \(\zeta(R) < 0\):

#### Safety-Delay Buffer (\(\tau^*\))
- **MANDATORY:** All Type-VI simulations MUST implement \(\tau^*\) delay
- **Default:** \(\tau^* = 0.1 \cdot |\Theta - R|\)
- **Purpose:** Prevent numerical divergence and allow intervention window
- **Override:** Requires explicit justification in commit message

#### Integration Method Requirements
- **PROHIBITED:** Euler/Forward methods for \(\zeta < 0\)
- **REQUIRED:** RK4 (Runge-Kutta 4th order) or higher
- **Validation:** Compare against analytical solutions when available
- **Monitoring:** Track energy conservation and unitarity violations
- **Reference Implementation:** See `simulation/genesis_cube.py::rk4_step()` and `simulation/tesseract_timeslices.py`

#### Meta-Regression Tracking
- **Monitor β-drift:** Track \(\beta\) parameter across domains
- **Alert threshold:** If \(\beta\) drifts > 10% from canonical band [3.6, 4.8]
- **Action:** Trigger Level 1 escalation (human review)
- **Documentation:** Log drift in `metrics/beta_evolution.csv`

### Agent Role Specialization for Type-VI

**New Agent Roles (V6):**

1. **Implosion Monitor**
   - Continuously scans for \(\zeta < 0\) signals
   - Computes CREP index in real-time
   - Triggers escalation protocols

2. **Safety-Delay Enforcer**
   - Validates \(\tau^*\) buffer implementation
   - Blocks commits without proper delay mechanisms
   - Ensures RK4 integration for Type-VI models

3. **Ethics Auditor**
   - Reviews Type-VI analyses for compliance with `ETHICS.md`
   - Checks provenance blocks and falsification criteria
   - Escalates dual-use concerns

4. **Intervention Coordinator**
   - Activates when CREP ≥ 0.8 in real-time contexts
   - Drafts stakeholder notifications
   - Coordinates with external governance bodies

5. **Tesseract Monitor (V6.0)**
   - Tracks entropy gradients ∇S from wavefunction evolution
   - Computes 4D CREP index with geometric coupling
   - Monitors consciousness integral I_C for observer-dependent effects
   - Validates photon propagation stability through timeslices

### Workflow Modifications for Type-VI

**Pre-commit checks:**
- [ ] Type-VI classification validated (inverted sigmoid, \(\zeta < 0\), cubic-root scaling)
- [ ] CREP index computed and documented
- [ ] Safety-delay \(\tau^*\) implemented if simulation present
- [ ] RK4 integration confirmed (no Euler methods)
- [ ] Provenance block complete (see `ETHICS.md` §3)
- [ ] Dual-use assessment conducted
- [ ] Escalation level determined and appropriate actions taken

**During execution:**
- Monitor for \(\beta\)-drift (trigger Level 1 if > 10% deviation)
- Track CREP index evolution
- Log all Type-VI detections to audit trail

**Post-execution:**
- Archive results with expiration date (default: 1 year)
- Document falsification criteria met/unmet
- Update meta-regression tracking

### Emergency Override

**ONLY USE IN EXTREME CIRCUMSTANCES:**

If human reviewer is unavailable and CREP ≥ 0.9 detected in **active risk scenario** (not research):
1. Agent may autonomously notify external authorities (climate agencies, financial regulators)
2. Must document full decision chain in `logs/emergency_overrides.jsonl`
3. Requires post-hoc governance review within 7 days
4. Override authority can be revoked by maintainers

<!-- /CUSTOM_RULES -->

---

**Last Updated:** 2025-11-24 14:22:03 UTC
**Governance Version:** 1.0.0
