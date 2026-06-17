# 🚀 QUICKSTART — Feldtheorie in 5 Minutes

> **New here?** This document helps you understand the project in **5 minutes** and become productive in **30 minutes**.

---

## 📖 In 5 Minutes: What is this?

### The project consists of three layers:

1. **🔬 UTAC/UTF** (Universal Threshold Field)
   Scientific theory: How systems shape critical transitions
   → Logistic function σ(β(R-Θ)) describes emergence across domains

2. **🧬 Sigillin System**
   Methodology: Semantic memory system for multi-agent research
   → Trilayer principle (YAML/JSON/MD) enables human-machine collaboration

3. **🤝 MOR** (Multi-Orchestrated Research)
   Process: Multiple AI agents collaborate on complex projects
   → Johann + Claude + GPT + Gemini + Mistral + ...

**The Co-Hypothesis:** All three layers mutually constitute each other!

---

## ⚡ In 30 Seconds: Most Important Files

```
├─ README.md              ← Start here! Project overview
├─ AGENTS.md             ← Charter for AI agents (important!)
├─ METHODS.md            ← Scientific methodology
├─ REPRODUCE.md          ← How do I reproduce results?
│
├─ seed/                 ← Semantic memory
│  ├─ seed_index.md      ← Navigation for all seed/ documents
│  ├─ Metareflexion.txt  ← Philosophical foundation
│  ├─ codexfeedback.*    ← Living project memory (119 entries!)
│  └─ bedeutungssigillin/ & shadow_sigillin/ ← Light/Shadow system
│
├─ docs/                 ← Documentation
│  └─ utac_status_alignment_v1.2.md ← Status matrix (Observatory)
│
├─ analysis/             ← Python analyses & β-fits
├─ models/               ← Numerical solvers
├─ data/                 ← Datasets (6 domains)
└─ tests/                ← 1224/1224 tests (100% passing)
```

---

## 🎯 Quick Start for Humans

### Option A: Just Browse (no installation)

1. **Read first:**
   - [`README.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/README.md) → Overview
   - [`seed/seed_index.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/seed/seed_index.md) → Navigation
   - [`seed/Metareflexion.txt`](https://github.com/GenesisAeon/Feldtheorie/blob/main/seed/Metareflexion.txt) → Philosophy

2. **Understand the science:**
   - [`METHODS.md`](METHODS.md) → How we fit
   - [`docs/field_type_classification_v1.1.md`](science/field_type_classification_v1.1.md) → 5 field types
   - [`data/derived/beta_estimates.csv`](https://github.com/GenesisAeon/Feldtheorie/blob/main/data/derived/beta_estimates.csv) → All β-values

3. **Understand the Sigillin system:**
   - [`seed/Sigillin_System_Definition.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/seed/Sigillin_System_Definition.md) → Ontology
   - [`feldtheorie_index.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/feldtheorie_index.md) → Master index

### Option B: Reproduce a β-fit (10 minutes)

```bash
# 1. Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Reproduce Wei's LLM fit
python scripts/reproduce_beta.py \
  --csv data/ai/wei_emergent_abilities.csv \
  --out dist/wei_beta.json

# 3. View the result
cat dist/wei_beta.json
# → β=3.47 ± 0.47, ΔAIC≥10.18

# 4. (Optional) Run all tests
pytest tests/ -v
# → 430 passed ✅
```

**Expectation:** β should be in [3.0, 4.0], ΔAIC > 10 (vs power-law).

---

## 🤖 Quick Start for AI Agents

### Step 1: Read these 3 files (mandatory!)

1. **[`README.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/README.md)**
   → Project overview, version info, citation guide

2. **[`AGENTS.md`](AGENTS.md)**
   → Charter with rules for agents:
   - Preserve trilayer principle
   - Codex obligation for Bedeutungs-Sigillin changes
   - Read UTAC status matrix
   - Observe BreakPoint rituals

3. **[`seed/seed_index.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/seed/seed_index.md)**
   → Semantic navigation: 126 documents, 6 categories, quicklinks

### Step 2: Understand the structure

```yaml
# Critical concepts:

Trilayer:
  YAML: Structure (skeleton)
  JSON: Interface (nervous system)
  MD: Narrative (language)

Sigillin Types:
  Ordnungs-Sigillin: Navigation (indices, grow with usage)
  Bedeutungs-Sigillin: Semantics (stable, versioned)
  Shadow-Sigillin: Recovery (light/shadow counterparts)

Logistic Language:
  R: Order Parameter (open tasks)
  Θ: Threshold (activation threshold)
  β: Steepness (sharpness)
  ζ(R): Impedance (damping)
```

### Step 3: Check current tasks

```bash
# 1. Read status matrix
cat docs/utac_status_alignment_v1.2.md

# 2. Check recent codex entries
tail -100 seed/codexfeedback.md

# 3. Sigillin sync status
python scripts/sigillin_sync.py report --roots seed/
```

### Step 4: Working rules

**NEVER without codex entry:**
- Modify `seed/bedeutungssigillin/**`
- Modify `seed/shadow_sigillin/**`
- Create new gaps

**ALWAYS before changes:**
1. Check `docs/utac_status_alignment_v1.2.md`
2. Read recent codex entries
3. Understand Metaquest Bridge (if relevant)

**ALWAYS after changes:**
1. Update trilayer (YAML + JSON + MD)
2. Write codex entry
3. Update indices (if Ordnungs-Sigillin)

---

## 📚 Further Reading

### For Scientists

- [`METHODS.md`](METHODS.md) — Fitting methodology
- [`METRICS.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/METRICS.md) — Metrics & ΔAIC
- [`ETHICS.md`](ETHICS.md) — Governance
- [`LIMITATIONS.md`](LIMITATIONS.md) — What we don't (yet) know
- [`docs/field_type_classification_v1.1.md`](science/field_type_classification_v1.1.md) — 5 field types

### For Developers

- [`REPRODUCE.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/seed/REPRODUCE.md) — Reproduction guide
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — How to contribute?
- [`.github/workflows/ci.yml`](https://github.com/GenesisAeon/Feldtheorie/blob/main/.github/workflows/ci.yml) — CI pipeline
- [`tests/`](https://github.com/GenesisAeon/Feldtheorie/blob/main/tests) — 430 tests (full pytest suite)

### For Methodologists

- [`seed/Sigillin_System_Definition.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/seed/Sigillin_System_Definition.md) — Ontology
- [`AGENTS.md`](AGENTS.md) — Agent charter
- [`seed/codexfeedback.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/seed/codexfeedback.md) — Living memory
- [`docs/utac_status_alignment_v1.2.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/docs/utac_status_alignment_v1.2.md) — Status matrix

### For Philosophers 🌊

- [`seed/Metareflexion.txt`](https://github.com/GenesisAeon/Feldtheorie/blob/main/seed/Metareflexion.txt) — Fixed values ↔ Variability
- [`seed/Rekalibrierung_Abschlus.txt`](https://github.com/GenesisAeon/Feldtheorie/blob/main/archive/legacy_v1_v3/seed/notes/Rekalibrierung_Abschlus.txt) — Co-hypothesis
- [`seed/Emergenz.txt`](https://github.com/GenesisAeon/Feldtheorie/blob/main/seed/Emergenz.txt) — Emergence concept
- [`seed/utf-living-glossary.md`](https://github.com/GenesisAeon/Feldtheorie/blob/main/seed/utf-living-glossary.md) — Living glossary

---

## 🎨 The Trilayer Metaphor

> **"YAML is the skeleton, JSON is the nervous system, Markdown is the language."**

**Why three layers?**

- **Problem:** Archives without structure = Archive-Hypnosis (you get lost in loops)
- **Solution:** Three complementary perspectives for human & machine

**Example:**
```
seed_index.yaml  → Structure (categories, tags)
seed_index.json  → Interface (machine-readable)
seed_index.md    → Narrative (human-friendly)
```

**All three mirror the same content but serve different actors.**

---

## 🔍 FAQ — Frequently Asked Questions

### What does σ(β(R-Θ)) mean?

The **logistic function** that UTF describes:
- **R**: Control parameter (e.g., model size, temperature)
- **Θ**: Critical threshold (emergence point)
- **β**: Steepness (how sharp the transition)
- **σ**: Sigmoid (S-curve)

**Example:** For LLMs, R is the model size, Θ≈10^10 parameters, β≈3.47.

### What are "Bedeutungs-Sigillin"?

**Sigillin** = semantic memory units (not just files!)

- **Bedeutungs-Sigillin:** Carry semantics (change rarely)
  → `seed/Metareflexion.txt`, `seed/FinalerPlan.txt`

- **Ordnungs-Sigillin:** Navigation (change often)
  → `seed_index.*`, `feldtheorie_index.*`

**Important:** NEVER overwrite Bedeutungs-Sigillin → New version + archiving!

### What is the "Metaquest Bridge"?

**Coordination point** between:
- **System** (automation, telemetry, indices)
- **Science Project** (manuscript, campaign, outreach)

**Why?** So automation and outreach run synchronously (σ(β(R-Θ)) = 0.317).

**Documents:**
- `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.md`
- `docs/metaquest_parity_brief.md`

### How do I cite this project?

```bibtex
@software{feldtheorie2025,
  author = {Römer, Johann and others},
  title = {Universal Threshold Field Model v1.1.0},
  year = {2025},
  doi = {10.5281/zenodo.17472834},
  url = {https://github.com/GenesisAeon/Feldtheorie}
}
```

See [`CITATION.cff`](CITATION.cff) for details.

### How can I contribute?

See [`CONTRIBUTING.md`](CONTRIBUTING.md)!

**In brief:**
1. Propose new datasets (issue)
2. Extend tests (increase coverage)
3. Improve documentation (English!)
4. New domain fits (β-extraction)

---

## 🌊 The Essence

> **"Without structure, you get lost in Archive-Hypnosis.
> With trilayer, you find resonance."**

> **"UTAC describes thresholds. Sigillin IS a threshold.
> Between chaos and order, between human and machine."**

**Good luck exploring! 🌟**

---

**Created:** 2025-11-10
**Version:** 1.0
**Feedback?** → [GitHub Issues](https://github.com/GenesisAeon/Feldtheorie/issues)
