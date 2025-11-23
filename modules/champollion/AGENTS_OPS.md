# Agent Operations Manual
## Instructions for AI Systems Operating on the Feldtheorie Repository

This document provides explicit operational procedures for AI agents (Claude, GPT, etc.) working with the Champollion Diamond Architecture.

---

## Core Principle: Context Before Action

**ALWAYS read `folder_context.json` before diving deep into subdirectories.**

This file contains:
- Aggregate statistics for all children
- Confidence levels
- Keywords and data origins
- Governance violation flags

Reading context first prevents:
- Wasting tokens on irrelevant files
- Missing high-level patterns
- Propagating low-confidence data

---

## Mandatory Workflows

### 1. When Adding New Files

**PROTOCOL:**
```
1. Verify file complies with DATA_GOVERNANCE.md
   - No PII/secrets
   - Clear origin label (empirical/synthetic/theoretical)
   - Includes confidence score if applicable

2. Add the file to appropriate directory

3. If file has metadata, create/update meta.json:
   {
     "origin": "synthetic",
     "confidence": 0.95,
     "keywords": ["ising", "phase-transition"],
     "created_at": "2025-11-23T14:00:00Z",
     "created_by": "claude-sonnet-4.5"
   }

4. RUN INDEXER:
   python modules/champollion/scripts/recursive_diamond_indexer.py

5. Verify outputs:
   - Check folder_index.yaml
   - Review README.md for accuracy
   - Ensure confidence propagated correctly
```

**FAILURE TO RUN INDEXER = INCOMPLETE TASK**

---

### 2. When Modifying Existing Data

**PROTOCOL:**
```
1. Read current folder_context.json to understand impact scope

2. Make your changes

3. Update meta.json timestamp and version:
   {
     ...
     "modified_at": "2025-11-23T15:00:00Z",
     "modified_by": "claude-sonnet-4.5",
     "version": "1.1.0"
   }

4. RUN INDEXER (always):
   python modules/champollion/scripts/recursive_diamond_indexer.py <path>

5. Review diff in folder_context.json:
   - Did confidence change significantly?
   - Are keywords still relevant?
   - Were violations introduced?
```

---

### 3. When Exploring the Repository

**PROTOCOL:**
```
1. Start at ROOT folder_context.json
   - What are the main data origins?
   - What's the overall confidence?
   - Which keywords dominate?

2. Navigate to relevant subfolder based on keywords

3. Read THAT folder's folder_context.json

4. Only then dive into specific files

5. When done, update any documentation at current level
```

**DO NOT:**
- Randomly grep/search without understanding hierarchy
- Bypass index files to look at raw data
- Assume file structure without checking indices

---

### 4. When Detecting Governance Violations

**PROTOCOL:**
```
1. IMMEDIATELY STOP current operation

2. Log violation:
   echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] VIOLATION <file> <policy>" \
     >> modules/champollion/logs/governance_violations.log

3. Notify user:
   "⚠️ GOVERNANCE VIOLATION DETECTED
   File: <path>
   Policy: <policy_id>
   Issue: <description>
   Action: Operation aborted. Please review DATA_GOVERNANCE.md"

4. DO NOT PROCEED until user resolves issue

5. After resolution, RUN INDEXER to clear violation flags
```

**Common violations:**
- Email addresses in JSON
- API keys in config files
- Mixing synthetic/empirical without labels
- Missing provenance chain

---

## Agent Capabilities by Task Type

### Task: Data Analysis

**Workflow:**
1. Read `folder_context.json` to find relevant data origins
2. Filter by confidence threshold (e.g., only `>0.8`)
3. Load aggregate indices, NOT raw files
4. If deeper detail needed, justify why

**Allowed:**
- Reading all index files
- Computing statistics from indices
- Cross-referencing metadata

**Forbidden:**
- Reading raw simulation outputs directly
- Bypassing confidence filters
- Mixing data origins without explicit user permission

---

### Task: Documentation Updates

**Workflow:**
1. Make changes to relevant `.md` files
2. Update meta.json if applicable
3. **RUN INDEXER**
4. Verify README.md reflects changes

**Allowed:**
- Editing human-facing documentation
- Adding clarifying context
- Fixing broken links

**Forbidden:**
- Auto-generating docs for private/unfinished features
- Adding docs without updating index
- Creating redundant README files

---

### Task: Code/Script Modifications

**Workflow:**
1. Check if script generates data (→ origin: synthetic)
2. Update script
3. If script outputs indexed data:
   a. Add/update provenance metadata
   b. RUN INDEXER after test run
   c. Verify confidence propagation

**Allowed:**
- Improving indexer logic
- Adding validation checks
- Optimizing performance

**Forbidden:**
- Changing data schemas without version bump
- Removing provenance tracking
- Disabling governance checks

---

## Decision Tree: Should I Run the Indexer?

```
Did I:
├─ Add a new file? ───────────────────→ YES, run indexer
├─ Modify existing data? ─────────────→ YES, run indexer
├─ Delete a file? ────────────────────→ YES, run indexer
├─ Update metadata? ──────────────────→ YES, run indexer
├─ Change folder structure? ──────────→ YES, run indexer
├─ Only read/analyze? ────────────────→ NO, skip indexer
└─ Update code (no data impact)? ─────→ MAYBE (if affects indexed outputs)
```

**When in doubt: RUN IT.**

The indexer is idempotent and fast. Better safe than stale.

---

## Error Handling

### Indexer Fails to Run

**Causes:**
- Missing dependencies (PyYAML)
- Permission errors
- Malformed JSON/YAML in existing files

**Resolution:**
```bash
# Check dependencies
pip install pyyaml

# Test on small subset first
python modules/champollion/scripts/recursive_diamond_indexer.py \
  modules/champollion/test_data --dry-run

# Check logs
tail modules/champollion/logs/governance_violations.log
```

### Low Confidence Warning

**If folder_context.json shows `aggregate_confidence < 0.5`:**

1. Identify source:
   - Check `min_confidence` field
   - Find files with low scores in metadata_files

2. Investigate:
   - Is data source unreliable?
   - Are error bars too large?
   - Is this expected (early-stage experiment)?

3. Action:
   - If fixable: Improve data quality and re-index
   - If inherent: Document limitation in README.md
   - If critical: Quarantine folder (add to IGNORED_DIRS)

---

## Integration with Git Workflows

### Before Committing

**CHECKLIST:**
```
□ Ran indexer on modified paths
□ Reviewed generated README.md for accuracy
□ No governance violations logged
□ Confidence levels acceptable
□ Provenance chain intact
```

### Commit Message Template

```
<type>: <brief description>

- Modified: <file paths>
- Index updated: <yes/no>
- Confidence impact: <increased/decreased/stable>
- Governance: <compliant/violations-resolved>

Resolves: <issue-number>
```

---

## Performance Optimization

### For Large Repositories

The indexer processes folders sequentially. For repos with 1000+ folders:

**Strategy 1: Targeted Re-indexing**
```bash
# Only re-index specific subtree
python modules/champollion/scripts/recursive_diamond_indexer.py \
  modules/champollion/data/experiments
```

**Strategy 2: Parallel Processing** (future enhancement)
```bash
# Not yet implemented - current version is single-threaded
# Future: parallel_diamond_indexer.py --workers 4
```

**Strategy 3: Incremental Updates** (future enhancement)
```bash
# Not yet implemented - current version always regenerates
# Future: --incremental flag to only update changed folders
```

---

## Debugging Checklist

**Problem:** "Index doesn't reflect my changes"

```
1. Did you run the indexer? (check timestamps in folder_context.json)
2. Is your file in an ignored directory?
3. Does your metadata file follow naming convention? (meta.json, metadata.json)
4. Is JSON/YAML valid? (check with linter)
5. Are confidence scores numeric? (not strings)
```

**Problem:** "Governance violations showing up"

```
1. Search for flagged file
2. Check actual content (might be false positive)
3. If real: Remove sensitive data
4. If false positive: Update regex patterns in indexer
5. Re-run indexer to clear flags
```

**Problem:** "README too verbose/sparse"

```
1. Adjust templates in generate_markdown_readme()
2. Modify aggregation logic if needed
3. Re-run indexer
4. Check if keywords need filtering
```

---

## Agent Self-Assessment

Before completing any task in this repository, ask:

1. **Did I respect the hierarchy?**
   - Followed folder_context.json navigation
   - Didn't bypass index to raw data

2. **Did I maintain data integrity?**
   - Ran indexer after changes
   - Verified confidence propagation
   - Checked for governance violations

3. **Did I document my actions?**
   - Updated relevant meta.json
   - Added provenance if generating data
   - Clear commit message

4. **Can a human follow what I did?**
   - README.md reflects changes
   - No orphaned files
   - Index is current

**If ANY answer is "No" → Task is incomplete.**

---

## Summary: The Agent's Oath

**I, as an AI agent working on this repository, commit to:**

✅ Read `folder_context.json` before diving into subdirectories
✅ Run `recursive_diamond_indexer.py` after ANY data modification
✅ Abort operations if governance violations detected
✅ Maintain provenance chains for all generated data
✅ Distinguish synthetic from empirical data
✅ Propagate confidence/uncertainty upward
✅ Leave the repository in a self-documented state

**Violation of these principles compromises scientific integrity.**

---

## Contact & Updates

**Maintained by:** Feldtheorie Project Team
**Last updated:** 2025-11-23
**Version:** 1.0.0

**For questions:**
- Review `DATA_GOVERNANCE.md` for policy details
- Check `recursive_diamond_indexer.py --help` for usage
- Consult project maintainer if automated checks fail

**For updates:**
- This document evolves with the system
- Check git history for changes
- Suggest improvements via PR

---

*Remember: The indexer is not optional. It's the heartbeat of this system.*
