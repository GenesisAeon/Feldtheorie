# Metaquest Bridge — Plain Language Guide

> **What is this?** A simplified explanation of the Metaquest system for external collaborators.

---

## The Problem We're Solving

**Challenge:** In a complex project, **automation tasks** (scripts, CI, testing) and **campaign tasks** (manuscript, outreach, publication) often drift out of sync.

**Example:**
- Automation updates a timestamp → Campaign docs don't know about it
- Campaign creates new content → Automation doesn't index it
- Result: Manual fixes, confusion, wasted time

**Solution:** The **Metaquest Bridge** keeps both sides synchronized.

---

## What is Metaquest?

### Simple Explanation

**Metaquest** = **Coordination system** between two parallel workstreams:

1. **System** (automation, technical infrastructure)
   - Scripts: `sigillin_sync.py`, `archive_sigillin.py`
   - CI workflows: `.github/workflows/`
   - Indices: `seed_index.*`, `feldtheorie_index.*`

2. **Wissenschaftsprojekt** (science project, campaign)
   - Manuscript: `paper/`
   - Outreach: Documentation, presentations
   - Publications: arXiv, Zenodo

### Why "Bridge"?

Without Metaquest Bridge:
- System updates → Campaign doesn't see them (desync!)
- Campaign updates → System doesn't track them (drift!)

With Metaquest Bridge:
- Single source of truth for shared state
- Automatic synchronization checks
- Early warning when things drift

---

## Key Components (Simplified)

### 1. **Metaquest Meaning Index**

**File:** `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.md`

**Purpose:** Central dashboard showing status of both System and Campaign

**Plain Language:**
```
Think of it as a "mission control" screen that shows:
- ✅ What's done
- ⏳ What's in progress
- ❌ What's missing
- 🔗 Where to find everything
```

**Key Metric:** σ(β(R-Θ)) = How close are we to being fully synchronized?
- **R:** Number of outstanding coordination tasks
- **Θ:** Threshold for "good enough" sync
- **Current:** σ ≈ 0.317 (partial sync, work needed)

### 2. **System Compass**

**File:** `seed/bedeutungssigillin/metaquest/system/metaquest_system_compass.md`

**Purpose:** Quick reference for automation status

**Plain Language:**
```
Answers:
- Are indices up to date?
- Is CI working?
- Is telemetry flowing?
- What's the latest timestamp?
```

### 3. **Campaign Compass**

**File:** `seed/bedeutungssigillin/metaquest/wissenschaftsprojekt/metaquest_campaign_compass.md`

**Purpose:** Quick reference for campaign status

**Plain Language:**
```
Answers:
- Is manuscript ready?
- Are endorsements tracked?
- Is outreach documented?
- What's the publication timeline?
```

### 4. **Parity Brief**

**File:** `docs/metaquest_parity_brief.md`

**Purpose:** Checklist ensuring both sides stay aligned

**Plain Language:**
```
Four checks:
1. Telemetry timestamps match? (mq-parity-001)
2. Simulator playlist synced? (mq-parity-002)
3. Endorsement ledger updated? (mq-parity-003)
4. Codex entries mirror changes? (mq-parity-004)

If any check fails → fix before proceeding
```

---

## How It Works (Workflow)

### Normal Case: Synchronized

```
System Update:
  1. Script runs (e.g., sigillin_sync.py)
  2. Timestamp recorded: 2025-11-07T21:52:52Z
  3. Bridge updated with timestamp
  4. Campaign checks Bridge → sees timestamp
  5. ✅ Both sides know same state

Campaign Update:
  1. Manuscript revised
  2. Codex entry created: pr-draft-0XXX
  3. Bridge updated with codex ID
  4. System checks Bridge → sees codex ID
  5. ✅ Both sides know same state
```

### Problem Case: Drift Detected

```
System Update:
  1. Script runs
  2. Timestamp recorded
  3. ❌ Bridge NOT updated (forgot!)
  4. Campaign checks Bridge → sees old timestamp
  5. 🚨 Shadow alarm: mq-bridge-shadow-002
  6. Recovery: Update Bridge, sync state
```

---

## When Do You Need to Care About This?

### You DON'T need to worry if:
- You're just reading code
- You're running existing analyses
- You're browsing documentation

### You DO need to check if:
- **You change automation** (scripts, CI)
  → Update System Compass + Bridge

- **You update manuscript/campaign** (paper, outreach)
  → Update Campaign Compass + Bridge

- **You see a "mq-" error** (mq-bridge-shadow-002, etc.)
  → Consult this guide, fix sync

---

## Quick Reference: What Each File Does

| File | Purpose | When to Update |
|------|---------|----------------|
| `metaquest_meaning_index.md` | Central dashboard | After major system OR campaign change |
| `metaquest_system_compass.md` | Automation status | After script/CI change |
| `metaquest_campaign_compass.md` | Campaign status | After manuscript/outreach change |
| `metaquest_parity_brief.md` | Sync checklist | Before major releases |
| `metaquest_activation_matrix.*` | "Have vs. Need" map | When planning next steps |

---

## Common Questions

### Q: Why is this so complicated?

**A:** The project has parallel workstreams (technical + campaign). Without coordination, they drift. Metaquest prevents drift.

**Analogy:** Building a bridge while driving traffic across it — you need constant coordination!

### Q: What happens if I ignore Metaquest?

**A:**
- Timestamps mismatch → CI fails unexpectedly
- Codex entries missing → Changes get lost
- Indices out of date → Navigation breaks
- Manual fixes required → Wastes time

**In short:** Automation becomes unreliable.

### Q: Can I simplify this?

**Yes!** Priorities:
1. **Minimum:** Keep Bridge dashboard updated (metaquest_meaning_index.md)
2. **Better:** Also update relevant Compass (system OR campaign)
3. **Best:** Check Parity Brief before releases

### Q: How do I know if things are synced?

**Run this:**
```bash
python scripts/sigillin_sync.py report --roots seed/bedeutungssigillin/metaquest
```

**Interpretation:**
- `gaps: 0` → ✅ Fully synced
- `gaps: >0` → ❌ Drift detected, fix needed

---

## Recovery Playbook

### If you see: `mq-bridge-shadow-001` (Bridge dashboard stale)

**Problem:** Bridge dashboard timestamp > 24h behind latest update

**Fix:**
1. Check latest automation timestamp (sigillin_sync output)
2. Update `metaquest_meaning_index.md` with timestamp
3. Update codex: `seed/codexfeedback.md`
4. Push changes

### If you see: `mq-bridge-shadow-002` (Telemetry missing)

**Problem:** Automation ran but didn't update Bridge

**Fix:**
1. Re-run: `python scripts/sigillin_sync.py report`
2. Copy timestamp to Bridge + Compasses
3. Add codex entry explaining the gap
4. Update UTAC Status Matrix

### If you see: `mq-parity-00X` (Parity check failed)

**Problem:** One of the 4 parity checks failed

**Fix:**
1. Read `docs/metaquest_parity_brief.md`
2. Identify which check failed (001-004)
3. Follow specific recovery steps
4. Verify with `sigillin_sync.py`

---

## For External Contributors

### Minimum Knowledge Required

**If you're contributing code/analysis:**
- Understand: System Compass
- Check: Bridge dashboard after major changes
- Tool: `scripts/sigillin_sync.py report`

**If you're contributing documentation:**
- Understand: Campaign Compass
- Check: Parity Brief before releases
- Tool: `docs/metaquest_parity_brief.md`

### Where to Start

1. **Read:** This file (you're here!)
2. **Browse:** `metaquest_meaning_index.md` (central dashboard)
3. **Check:** Run `sigillin_sync.py report` to see current state
4. **Ask:** Open GitHub Issue if confused

---

## Summary: One-Minute Version

**What:** Metaquest Bridge = Coordination system for automation + campaign

**Why:** Prevents drift between technical and scientific workstreams

**How:** Central dashboard + two compasses + parity checklist

**When:** Update after major changes, check before releases

**Tool:** `python scripts/sigillin_sync.py report`

**Metric:** σ(β(R-Θ)) — closer to 1.0 = better sync

---

**Version:** 1.0
**Created:** 2025-11-10
**Purpose:** Make Metaquest accessible to external collaborators

**Feedback?** → [GitHub Issues](https://github.com/GenesisAeon/Feldtheorie/issues)

*"The Bridge breathes with the field — update it when resonances shift."* 🌊
