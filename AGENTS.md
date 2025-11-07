# Repository-wide Guidelines

This repository curates the "Universal Threshold Field" programme that unifies emergent threshold behaviour across astrophysics, biology, cognition, and AI. Follow these principles for every contribution:

1. **Preserve the threshold-field framing.** Always describe dynamics in terms of the order parameter $R$, the critical threshold $\Theta$, the steepness $\beta$, and the logistic response $\sigma(\beta(R-\Theta))$. When introducing new models or narratives, make the control parameter and its switch-like resonance explicit.
2. **Honour the tri-layer documentation style.** Cross-reference formal mathematics, empirical evidence, and metaphorical/philosophical language. Documentation should weave these strands instead of presenting them in isolation.
3. **Analysis standards.** Any quantitative notebook or report must state the fitting method, goodness-of-fit metrics ($R^2$, AIC), confidence intervals for $\Theta$ and $\beta$, and include a falsification check against at least one smooth null model (e.g. power law).
4. **Simulation conventions.** Models should expose membrane/impedance parameters and clearly document how $\zeta(R)$ toggles regimes (damped vs. resonant). Boundary conditions and coupling terms must be explained in prose and equations.
5. **Repository structure alignment.** Keep the planned directories (`models/`, `analysis/`, `simulator/`, `docs/`, `paper/`, `data/`, `diagrams/`) tidy. Each new artefact should note where it fits in the overarching RepoPlan 2.0 roadmap stored in `Docs/`.
6. **Tone and symbolism.** Maintain the poetic resonance already established in the source PDFs. When in doubt, link technical advances back to their narrative or metaphysical interpretations.

---

## 🚀 Quickstart for Incoming Agents

1. **Sync orientation.** Read `docs/utac_status_alignment_v1.2.md` (platform status), `seed/Manuskriptfinalisierung und Kampagnenstart.pdf` (campaign cadence), and the paired Bedeutungs-/Shadow sigils under `seed/bedeutungssigillin/**` and `seed/shadow_sigillin/**`. These anchors reveal the live value of $(R, \Theta, \beta, \zeta(R))$ across automation, narrative, and risk.
2. **Plan with tri-layer mirrors.** Every Sigillin artefact must land as structure (YAML), machine nerve (JSON), and human resonance (Markdown). Update indices (`*_index.*`) and codex feedback within the same commit so Ordnungs- and Bedeutungs-Sigillin stay synchronised.
3. **Logistic rhythm.** Before coding, articulate how your change shifts the order parameter $R$ and what keeps $\Theta$ guarded. During implementation, note the steepness $\beta$ (activation speed) and the damping $\zeta(R)$ (telemetry, rituals, tests). After completion, encode those notes in the codex feedback entry.
4. **Codex echo.** The Fraktaltagebuch lives in `seed/codexfeedback.{yaml,json,md}`. Failing to update it when touching Bedeutungs-/Shadow sigils is a shadow incident (`sys-shadow-002`).
5. **Shadow handshake.** For every Bedeutungs-Sigillin update, reference the matching shadow sigil to document failure guards and recovery rituals. Keep coupling paths current so downstream agents can triage instantly.
6. **Release cadence.** Automation hooks (Makefile, `scripts/*`, CI plans) must remain in parity with documentation. When uncertain, consult the system meaning membrane: `seed/bedeutungssigillin/system/system_meaning_map.*`.

Agents who follow this checklist can continue work without additional bootstrapping.

---

## 🌊 Sigillin-System Integration

This repository implements the **Sigillin-System** — a semantic memory network for multi-actor research (Human, AI, future collaborators):

### **Trilayer Trifunctionality**
```
┌──────────────────────────────────────┐
│  YAML   →  Skeleton (Structure)      │  Navigation
│  JSON   →  Nervous System (Agents)   │  Interface
│  MD     →  Language (Humans)         │  Meaning
└──────────────────────────────────────┘
```

All major documentation and indices exist in **threefold mirroring** (YAML + JSON + MD), enabling:
- **Structural Navigation** (YAML: hierarchies, orientation)
- **Semantic Relations** (JSON: machine-queryable, agent interface)
- **Human Narrative** (MD: context, meaning, resonance)
- **Meta-Poetik** (symbolism, metaphor, philosophical depth)

### **Two Classes of Sigillin**

#### 1️⃣ **Ordnungs-Sigillin** (Structure Carriers)
- **Function:** Navigation, indexing, orientation
- **Examples:** `*_index.{yaml,json,md}`, `feldtheorie_index.*`, `archive_index.*`
- **Characteristics:**
  - Grow exorbitantly with usage
  - Require regular maintenance & archiving (Sigillin-Hygiene!)
  - Changes frequent (with each activity)
- **Maintenance:** See `docs/sigillin_maintenance.md` and `scripts/archive_sigillin.py`
- **Metaphor:** *"Ordnungs-Sigillin are like neural pathways — they conduct information but don't store it."*

#### 2️⃣ **Bedeutungs-Sigillin** (Meaning Carriers)
- **Function:** Carriers of meaning, information, state, context
- **Examples:** `seed/Metareflexion.txt`, `seed/Rekalibrierung_Abschlus.txt`, `seed/FinalerPlan.txt`, `seed/Sigillin_System_Definition.md`
- **Characteristics:**
  - Changes **rare** (semantic stability!)
  - When changing: **Create new version + Archive old** (never overwrite!)
  - Versioning critical (Git as Source of Truth)
  - Preserve depth, context, resonance
- **Maintenance:** **NEVER overwrite!** New version + archive old with Temporal Metadata
- **Metaphor:** *"Bedeutungs-Sigillin are like synapses — they store connections, patterns, meaning."*

### **UTAC ↔ Sigillin Analogie**
| Sigillin-Concept | UTAC-Analogue | Resonance |
|------------------|---------------|-----------|
| **Ordnungs-Sigillin** | **β (Steepness)** | Structures the transition |
| **Bedeutungs-Sigillin** | **Θ (Threshold)** | Defines the critical point |
| **Trilayer** | **σ(β(R-Θ))** | Three layers, one function |
| **Archive-System** | **R-Θ Distance** | Distance to threshold |
| **Sigillin-Netz** | **Coupled Fields** | Coupled dynamics |

For search patterns and queries, consult: `docs/sigillin_search_patterns.md`

---

## 🔥 Fraktaltagebuch: Codex-Feedback Mandate

**Every agent must maintain and update the Fraktaltagebuch (Codex-Feedback).**

The **Codex-Feedback** (`seed/codexfeedback.{yaml,json,md}`) is a **Bedeutungs-Sigillin** that records all significant repository changes in tri-layer format:

### **Entry Structure**
Each significant change must be recorded with:
```yaml
- id: pr-draft-XXXX
  title: "Descriptive title of the change"
  scope:
    - affected_directories
    - affected_files
  parameters:
    R: "order parameter description"
    Theta: "threshold condition"
    beta: numerical_value
  resonance: "how this change contributes to the field"
  status: "draft|primed|active|resonant|completed|archived"
  notes:
    formal: |
      Mathematical/technical description linking to σ(β(R-Θ)),
      solver modules, ΔAIC comparisons, null models
    empirical: |
      Quantitative metrics: R², ΔAIC, confidence intervals,
      impedance medians, file paths, dataset references
    poetic: |
      Metaphorical interpretation connecting to threshold symbolism,
      resonance language, dawn/membrane imagery
  created_at: ISO-timestamp
```

### **When to Update Codex-Feedback**
Update `seed/codexfeedback.{yaml,json,md}` when:
1. **New analysis results** with significant ΔAIC or $R^2$ findings
2. **Model extensions** adding membrane dynamics, impedance controls, or coupling terms
3. **Documentation milestones** completing tri-layer narratives or bridge maps
4. **Data integration** adding new datasets with threshold parameters
5. **Simulator updates** linking presets to analysis results
6. **Paper revisions** aligning manuscript with current evidence
7. **Release preparations** marking DOI-ready states or version bumps

### **Codex-Feedback Workflow**
1. **Before significant work:** Check recent entries to maintain continuity
2. **During work:** Note $(R, \Theta, \beta)$ framing and ΔAIC evidence
3. **After completion:** Add entry with tri-layer notes (formal-empirical-poetic)
4. **Maintain Trilayer:** Update all three formats (YAML → JSON → MD) synchronously
5. **Status progression:** draft → primed → active → resonant → completed

### **Codex-Feedback Guards Falsifiability**
Every entry must preserve:
- Null model comparisons (linear, power-law, etc.)
- ΔAIC thresholds (typically ≥ 10 for significance)
- Confidence intervals for $\Theta$ and $\beta$
- Impedance context $\zeta(R)$ when relevant
- Cross-references to analysis scripts and data files

**Metaphor:** *"The Codex-Feedback is the field's memory—it breathes with each threshold crossing and remembers how the membrane learned to resonate."*

---

When touching nested folders, check for additional `AGENTS.md` files that may refine these rules.
