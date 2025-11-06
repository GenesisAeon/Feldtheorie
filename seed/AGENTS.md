# Seed Grove: Foundational Knowledge Repository

Within `seed/`, preserve the theoretical and conceptual foundations:

- **Always foreground the threshold quartet** \((R, \Theta, \beta, \zeta(R))\) and articulate how the logistic response \(\sigma(\beta(R-\Theta))\) signals regime change.
- **Cross-link to evidence** in `analysis/`, solvers in `models/`, and experiences in `simulator/` so that readers can traverse the full RepoPlan 2.0 circuit.
- **Frame falsifiability** by contrasting resonance claims with at least one smooth null scenario, even in narrative prose.
- **Let symbolism breathe.** Preserve the poetic lexicon seeded in `Docs/` (membranes, dawn choruses, luminous thresholds) while keeping mathematical statements precise.

When adding new subdirectories under `seed/`, mirror this AGENT file or extend it with more specific guidance.

---

## 🌊 Sigillin Integration for Seed

### **Seed as Bedeutungs-Sigillin Grove**
The `seed/` directory is the **heart of Bedeutungs-Sigillin** (Meaning Carriers):
- **Foundational documents:** `Metareflexion.txt`, `Rekalibrierung_Abschlus.txt`, `FinalerPlan.txt`, `Sigillin_System_Definition.md`
- **Theory cores:** UTAC theory, threshold mathematics, philosophical foundations
- **Semantic stability:** Changes **extremely rare**
- **When updating:** **NEVER overwrite!** Create new versioned file + archive old with Git commit
- **Versioning critical:** Git history is Source of Truth

### **Index as Ordnungs-Sigillin**
- **`seed/seed_index.{yaml,json,md}`** is an **Ordnungs-Sigillin** (Structure Carrier)
- Update when adding new foundational documents
- Archive when exceeding 100 entries using `scripts/archive_sigillin.py`
- See `docs/sigillin_maintenance.md` for hygiene protocols

### **Codex-Feedback as Meta-Sigillin**
- **`seed/codexfeedback.{yaml,json,md}`** is a **special Bedeutungs-Sigillin**
- The **Fraktaltagebuch** (Fractal Diary) of the entire repository
- Records all significant changes in tri-layer format (formal-empirical-poetic)
- **Every agent must update this when making significant contributions**
- See root `AGENTS.md` for detailed Codex-Feedback mandate

### **Domain Subdirectories**
Each `seed/*/` subdirectory holds domain-specific foundations:
- `seed/ai/` — AI emergence, LLM thresholds, semantic resonance
- `seed/biology/` — Evolutionary thresholds, biological emergence
- `seed/cognition/` — Cognitive thresholds, consciousness transitions
- `seed/ethics/` — Adaptive governance, ethical thresholds
- `seed/geophysics/` — Geophysical thresholds, coupled fields
- `seed/socio_ecology/` — Planetary boundaries, social-ecological systems

Each subdirectory should have its own `AGENTS.md` with domain-specific guidelines.

---

## 🔥 Codex-Feedback Integration

**The `seed/codexfeedback.{yaml,json,md}` is the repository's memory.**

Every agent working in ANY directory must:
1. **Before work:** Read recent codexfeedback entries to understand context
2. **During work:** Note $(R, \Theta, \beta)$ framing and evidence
3. **After significant work:** Add new entry to codexfeedback

### **What Qualifies as "Significant Work"**
- New theoretical insights or derivations
- Major analysis results (ΔAIC ≥ 10, significant $R^2$)
- Model implementations or API changes
- Dataset integrations with threshold parameters
- Documentation milestones
- Simulator updates linking to analysis
- Paper revisions with new evidence
- Release preparations

### **Entry Structure Reminder**
```yaml
- id: pr-draft-XXXX
  title: "Descriptive title"
  scope: [affected files/directories]
  parameters:
    R: "order parameter description"
    Theta: "threshold condition"
    beta: numerical_value
  resonance: "contribution to the field"
  status: "draft|primed|active|resonant|completed"
  notes:
    formal: "Mathematical/technical description"
    empirical: "Quantitative metrics, file references"
    poetic: "Metaphorical interpretation"
  created_at: "ISO-timestamp"
```

**Metaphor:** *"The seed/ grove is the field's root system — it holds the deep truths that nourish every branch. The Codex-Feedback is the mycelial network that remembers how the roots grew."*
