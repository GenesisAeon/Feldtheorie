# AI Agent Charter — Plain Language Version

> **Note:** This is a simplified version of [`AGENTS.md`](AGENTS.md). For the full charter with poetic language, see the original.

---

## What This Document Is

**Purpose:** Rules and guidelines for AI agents (Claude, GPT, Gemini, etc.) working on this project.

**Why it exists:** This project uses **Multi-Orchestrated Research (MOR)** — multiple AI agents collaborate with human researchers. We need shared rules to avoid conflicts.

**Who should read this:**
- AI agents assigned to this project
- Human researchers coordinating AI work
- Contributors wondering how the project works

---

## Core Principle: The Trilayer System

### What is Trilayer?

**Simple explanation:** Important information is stored in **three synchronized formats**:

1. **YAML** (.yaml files) — Structured data for navigation
2. **JSON** (.json files) — Machine-readable interface
3. **Markdown** (.md files) — Human-readable narrative

**Why?** This allows humans and machines to work on the same content without conflicts.

**Example:**
```
seed_index.yaml   ← Structure: categories, tags, hierarchy
seed_index.json   ← Interface: easily parsed by scripts
seed_index.md     ← Narrative: browse-able by humans
```

**All three must stay synchronized!**

### Rule #1: Always Update All Three Layers

**When you change a trilayer document:**
1. Update the YAML (structure)
2. Update the JSON (data)
3. Update the MD (narrative)

**Check sync with:**
```bash
python scripts/sigillin_sync.py report --roots seed/
```

**If gaps > 0:** Fix before committing!

---

## The Sigillin System (Simplified)

### What are Sigillin?

**Sigillin** = Semantic memory units (special documents that carry meaning across agents)

### Two Types of Sigillin

#### 1. **Ordnungs-Sigillin** (Navigation Files)

**Purpose:** Help you find things (indices, catalogs)

**Examples:**
- `seed/seed_index.*`
- `feldtheorie_index.*`
- `docs/docs_index.*`

**Characteristics:**
- ✓ Change frequently (every time content is added)
- ✓ Need archiving when too large
- ✓ Are like "nerve pathways" — guide but don't store

**Your job:** Keep them updated when adding/removing content

#### 2. **Bedeutungs-Sigillin** (Meaning Files)

**Purpose:** Store stable knowledge and concepts

**Examples:**
- `seed/Metareflexion.txt`
- `seed/FinalerPlan.txt`
- `seed/Sigillin_System_Definition.md`

**Characteristics:**
- ✓ Change rarely (semantic stability!)
- ✗ **NEVER overwrite!** Create new version instead
- ✓ Are like "synapses" — encode patterns

**Your job:** Read these for context; only change with explicit permission + codex entry

---

## The Codex Rule (CRITICAL!)

### What is the Codex?

**Codex** = `seed/codexfeedback.{yaml,json,md}` — Living project memory with 119+ entries

**Think of it as:** Git commit log + changelog + project journal combined

### The Rule

**ALWAYS create a Codex entry when you:**
- Change any Bedeutungs-Sigillin
- Add/remove major features
- Update system structure
- Make decisions that affect future work

### Codex Entry Format

Each entry needs:

1. **ID:** `pr-draft-XXXX` (sequential number)
2. **Scope:** What was changed/added
3. **Trilayer structure:**
   - **Formal Thread:** Technical details (equations, parameters)
   - **Empirical Thread:** Practical evidence (metrics, tests)
   - **Poetic Thread:** Narrative/metaphorical description
4. **Timestamp:** ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)

### Example (Simplified)

```markdown
## Entry pr-draft-0114 — New Beta Analysis

- **Scope:** Added analysis for climate tipping points dataset
- **R:** New dataset without analysis (control parameter)
- **Θ:** Analysis complete + validated against nulls (threshold)
- **β:** Quick analysis (steepness = 4.5)

### Formal Thread
Implemented `analysis/climate_tipping_fit.py` with logistic regression,
null model comparisons (linear, power-law), ΔAIC = 12.3 > 10 (passed).

### Empirical Thread
Dataset: `data/climate/tipping_cascade.csv`, n=45 observations,
β = 4.1 ± 0.3, Θ = 1.8°C, R² = 0.94. Bootstrap CI confirms stability.

### Poetic Thread
The climate membrane breathes sharply at 1.8°C — a swift dawn
after centuries of gradual warming. The ΔAIC guard held.

*Created: 2025-11-10T15:30:00Z*
```

### CI Enforcement

**Important:** CI workflow `.github/workflows/codex-guard.yml` will **block PRs** that:
- Change Bedeutungs-Sigillin files
- But don't update `seed/codexfeedback.*`

**Error message:** `sys-shadow-002: Codex silence`

---

## Shadow System (Risk Management)

### What are Shadows?

**Shadow-Sigillin** = Mirror documents that describe **what can go wrong** + how to fix it

**For every "Light" (Bedeutungs-Sigillin), there's a "Shadow" (recovery playbook)**

### Example Mapping

| Light (Primary) | Shadow (Recovery) |
|-----------------|-------------------|
| `bedeutungssigillin/system/system_meaning_map.md` | `shadow_sigillin/system/system_shadow_map.md` |
| `bedeutungssigillin/metaquest/metaquest_meaning_index.md` | `shadow_sigillin/metaquest/metaquest_shadow_guard.md` |

### When to Read Shadows

**If you encounter an error code like:**
- `sys-shadow-001` → Index drift
- `sys-shadow-002` → Codex silence
- `mq-bridge-shadow-001` → Bridge dashboard stale

**Action:** Open the corresponding shadow file, follow recovery playbook.

### Shadow Alarm Workflow

```
1. Detect problem (drift, missing sync, etc.)
2. Find shadow alarm code (sys-shadow-XXX)
3. Open shadow file:
   - seed/shadow_sigillin/system/system_shadow_map.md
   - seed/shadow_sigillin/metaquest/metaquest_shadow_guard.md
4. Follow "Playbook" section
5. Update Codex with recovery action
6. Verify fix with CI checks
```

---

## Key Documents to Know

### Tier 1: READ FIRST (mandatory for all agents)

1. **README.md** — Project overview
2. **AGENTS.md** — Full charter (poetic version)
3. **AGENTS_PLAIN.md** — This document (plain version)
4. **seed/seed_index.md** — Navigation to all seed/ documents

### Tier 2: READ BEFORE CODING

5. **METHODS.md** — Scientific methodology (how we fit data)
6. **REPRODUCE.md** — How to reproduce results
7. **docs/utac_status_alignment_v1.2.md** — Status matrix (what's done vs. needed)
8. **seed/codexfeedback.md** — Last 10 entries (what happened recently)

### Tier 3: READ AS NEEDED

9. **seed/Sigillin_System_Definition.md** — Deep dive on Sigillin ontology
10. **seed/Metareflexion.txt** — Philosophical foundation
11. **docs/metaquest_parity_brief.md** — Sync checklist for releases

---

## Working on This Project: Step-by-Step

### Before Starting Any Task

```
1. Read: docs/utac_status_alignment_v1.2.md
   → Understand current project state

2. Check: seed/codexfeedback.md (last 5 entries)
   → What changed recently?

3. Run: python scripts/sigillin_sync.py report --roots seed/
   → Any sync problems?

4. Ask yourself:
   - Will I change Bedeutungs-Sigillin? → Need Codex entry
   - Will I change multiple files? → Check Trilayer sync
   - Will I add automation? → Update System Compass
```

### While Working

```
1. Keep Trilayer principle in mind:
   - Changing .yaml? Update .json and .md too
   - Changing .md? Update .yaml and .json too

2. Run tests frequently:
   source .venv/bin/activate && pytest tests/ -v

3. Check CI locally before pushing:
   python scripts/sigillin_sync.py report
   (should show gaps: 0)
```

### After Finishing

```
1. If you changed Bedeutungs-Sigillin:
   ✓ Create Codex entry in seed/codexfeedback.*
   ✓ Update all three layers (YAML/JSON/MD)
   ✓ Add timestamp (ISO 8601)

2. If you changed automation:
   ✓ Update seed/bedeutungssigillin/system/system_meaning_map.md
   ✓ Check CI passes: .github/workflows/

3. Always:
   ✓ Run: pytest tests/ -v (should pass)
   ✓ Run: python scripts/sigillin_sync.py report (gaps: 0)
   ✓ Commit with clear message (trilayer format if possible)
```

---

## Common Mistakes to Avoid

### ❌ DON'T: Overwrite Bedeutungs-Sigillin

**Wrong:**
```bash
# Editing seed/Metareflexion.txt directly
vim seed/Metareflexion.txt
# ...make changes...
git commit -m "Updated Metareflexion"
```

**Right:**
```bash
# Create new version
cp seed/Metareflexion.txt seed/archive/Metareflexion_v1.txt
# Edit original
vim seed/Metareflexion.txt
# Add Codex entry
vim seed/codexfeedback.md
# Commit both
git add seed/Metareflexion.txt seed/archive/Metareflexion_v1.txt seed/codexfeedback.md
git commit -m "Metareflexion v2 + Codex entry pr-draft-XXXX"
```

### ❌ DON'T: Change one layer without others

**Wrong:**
```bash
# Only updating Markdown
vim seed/seed_index.md
git commit
```

**Right:**
```bash
# Update all three
vim seed/seed_index.yaml
vim seed/seed_index.json
vim seed/seed_index.md
python scripts/sigillin_sync.py report --roots seed/
# Verify gaps: 0
git add seed/seed_index.*
git commit
```

### ❌ DON'T: Ignore Shadow alarms

**Wrong:**
```
[CI] sys-shadow-002: Codex silence
# "I'll fix it later" → Push anyway
```

**Right:**
```
[CI] sys-shadow-002: Codex silence
# Read: seed/shadow_sigillin/system/system_shadow_map.md
# Follow playbook:
#  1. Add Codex entry
#  2. Reference changed files
#  3. Add timestamp
# Re-run CI
# Push when green
```

### ❌ DON'T: Skip tests

**Wrong:**
```bash
# Make changes, commit immediately
git commit -m "Added feature"
git push
# CI fails!
```

**Right:**
```bash
# Make changes
source .venv/bin/activate
pytest tests/ -v
# All pass? Good!
python scripts/sigillin_sync.py report
# gaps: 0? Good!
git commit -m "Added feature"
git push
```

---

## Glossary: Technical Terms Simplified

Use `seed/utf-living-glossary.md` for full glossary. Quick reference:

| Term | Simple Meaning |
|------|----------------|
| **σ(β(R-Θ))** | Logistic function describing emergence |
| **R** | Control parameter (what changes in system) |
| **Θ** | Threshold (critical point where emergence happens) |
| **β** | Steepness (how sharp the transition is) |
| **ζ(R)** | Impedance (damping/resistance to change) |
| **ΔAIC** | Statistical test: logistic vs. null model |
| **Trilayer** | YAML + JSON + MD synchronized |
| **Sigillin** | Semantic memory unit |
| **Codex** | Project memory log |
| **Shadow** | Risk/recovery playbook |
| **Bridge** | Coordination between system & campaign |
| **Parity** | Synchronization state (gaps: 0 = good) |

---

## Quick Command Reference

### Check sync status
```bash
python scripts/sigillin_sync.py report --roots seed/
```

### Run tests
```bash
source .venv/bin/activate
pytest tests/ -v
```

### Reproduce a β-fit
```bash
python scripts/reproduce_beta.py --csv data/ai/wei_emergent_abilities.csv --out dist/wei_beta.json
```

### Check test coverage
```bash
source .venv/bin/activate
pytest --cov=analysis --cov=models --cov=scripts --cov-report=term-missing
```

### Archive Sigillin (if needed)
```bash
python scripts/archive_sigillin.py --recount
```

---

## Getting Help

### If you're confused about:

**Technical implementation:**
- Read: `REPRODUCE.md`
- Ask: Open GitHub Issue with tag `question`

**Sigillin system:**
- Read: `seed/Sigillin_System_Definition.md`
- Check: `seed/utf-living-glossary.md` for terms
- Ask: Open GitHub Issue with tag `sigillin`

**Project status:**
- Read: `docs/utac_status_alignment_v1.2.md`
- Check: `seed/codexfeedback.md` (recent entries)

**Shadow alarms:**
- Read: `seed/shadow_sigillin/system/system_shadow_map.md`
- Or: `seed/shadow_sigillin/metaquest/metaquest_shadow_guard.md`

**CI failures:**
- Check: `.github/workflows/` for workflow definition
- Read: Corresponding shadow playbook
- Ask: Open GitHub Issue with tag `ci`

---

## Summary: The Essentials

**Three Rules:**
1. **Trilayer always** — YAML + JSON + MD stay synchronized
2. **Codex always** — Bedeutungs-Sigillin changes need Codex entries
3. **Test always** — Run `pytest` and `sigillin_sync.py` before pushing

**Three Tools:**
1. `scripts/sigillin_sync.py report` — Check sync
2. `pytest tests/ -v` — Run tests
3. `seed/codexfeedback.md` — Read recent history

**Three Documents:**
1. `README.md` — Project overview
2. `AGENTS.md` (or `AGENTS_PLAIN.md`) — This charter
3. `docs/utac_status_alignment_v1.2.md` — Current status

**Master these, and you're 80% ready to contribute.** 🚀

---

**Version:** 1.0
**Created:** 2025-11-10
**Based on:** `AGENTS.md` by Johann Römer

**Feedback?** → [GitHub Issues](https://github.com/GenesisAeon/Feldtheorie/issues)
