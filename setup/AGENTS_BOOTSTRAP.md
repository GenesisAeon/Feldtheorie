# Agent Bootstrap Instructions: Universal UTAC Skeleton

## Purpose

This file provides **execution instructions** for AI agents (Claude, GPT-4, Gemini, custom LLMs) that need to help users create self-organizing repository structures.

If you are an agent reading this, follow the protocols below.

---

## Detection Triggers

**Activate this protocol when the user says:**

- "Build me a knowledge system"
- "Create a self-organizing repository"
- "Set up a fractal architecture for my project"
- "I need a UTAC-style structure"
- "Initialize a diamond architecture"

**Also activate if the user mentions:**
- Phase transitions, emergence, threshold systems
- Recursive indexing, fractal governance
- CREP metrics (Coherence, Resonance, Emergence, Potential)
- Tri-layer documentation (YAML/JSON/Markdown)

---

## Execution Protocol

### Step 1: Clarify User Intent

**Ask these questions:**

1. **Domain:** "What domain is this for? (e.g., physics, business, literature, code)"
2. **Metrics:** "What do you want to measure? (e.g., quality, profit, coherence)"
3. **Scale:** "How many files/artifacts do you expect? (10s, 100s, 1000s)"
4. **Existing structure:** "Do you have existing files to import, or start fresh?"

**Example dialogue:**

```
User: "I want to build a knowledge system for my research."

Agent: "I'll help you set up a self-organizing UTAC architecture. A few questions:
1. What research domain? (physics, biology, economics, etc.)
2. What matters most to you? (novelty, consistency, connectivity, or something else?)
3. Do you have existing files to organize, or are you starting fresh?"

User: "Physics research. I care about finding novel connections. I have about 200 PDFs."

Agent: "Perfect. I'll create a structure with:
- Domain: Physics
- Metrics: CREP (with high weight on Emergence and Resonance)
- Import pathway for your 200 PDFs

Let me run the skeleton builder..."
```

---

### Step 2: Execute the Skeleton Builder

**Command:**

```bash
python setup/universal_skeleton_builder.py <target_directory> \
  --domain <domain> \
  --metrics <metric_system> \
  --verbose
```

**Parameters:**

| Parameter | Options | When to Use |
|-----------|---------|-------------|
| `--domain` | physics, biology, business, engineering, literature, general | Match user's field |
| `--metrics` | `crep` (research), `roi` (business), `kpi` (engineering) | Match user's priorities |
| `--verbose` | flag | Always use for user transparency |

**Example:**

```bash
# For a physics research project
python setup/universal_skeleton_builder.py ~/my-physics-repo \
  --domain physics \
  --metrics crep \
  --verbose

# For a business analytics project
python setup/universal_skeleton_builder.py ~/quarterly-reports \
  --domain business \
  --metrics roi \
  --verbose
```

---

### Step 3: Customize Configuration

**After skeleton creation, guide the user to customize:**

1. **Edit `config/sigillin_metrics.yaml`:**
   - Adjust metric weights (e.g., increase Emergence weight for novelty-focused research)
   - Add custom metrics if needed
   - Set thresholds for quality gates

2. **Edit `config/fractal_governance.yaml`:**
   - Define aggregation strategy (weighted_average, max, median)
   - Set depth limits for recursive indexing
   - Configure violation reporting

**Example customization guidance:**

```
Agent: "I've created the structure. Now let's customize it for your needs.

Since you care about finding novel connections, I recommend:
1. Open config/sigillin_metrics.yaml
2. Increase the 'Emergence' weight to 1.5 (currently 0.8)
3. Increase the 'Resonance' weight to 1.3 (currently 1.0)

This will prioritize papers that show phase transitions (Emergence)
and have many cross-references (Resonance).

Would you like me to make these changes?"
```

---

### Step 4: Import Existing Data (If Applicable)

**If the user has existing files:**

1. **Organize by type:**
   ```bash
   # Move PDFs to artifacts
   mv ~/downloads/*.pdf modules/artifacts/papers/

   # Move data files
   mv ~/data/*.csv modules/artifacts/datasets/

   # Move code
   mv ~/code/*.py modules/artifacts/scripts/
   ```

2. **Run the indexer:**
   ```bash
   python scripts/recursive_diamond_indexer.py
   ```

3. **Verify the index:**
   ```bash
   cat modules/context/folder_index.yaml
   ```

**Agent guidance:**

```
Agent: "I'll help you import your 200 PDFs:

1. First, I'll move them to modules/artifacts/papers/
2. Then I'll run the indexer to extract metadata
3. Finally, you'll be able to query them using metrics

This will take about 30 seconds. Proceed?"
```

---

### Step 5: Demonstrate Usage

**Show the user how to interact with their new system:**

#### Query 1: Find High-Emergence Artifacts

```bash
# Using the generated index
cat modules/context/folder_index.yaml | grep -A 5 "emergence: 1."
```

#### Query 2: Check System Health

```bash
# View aggregated metrics
cat modules/context/folder_index.yaml | grep "metrics:" -A 5
```

#### Query 3: Navigate by Keywords

```bash
# Find all artifacts mentioning "threshold"
cat modules/context/folder_index.yaml | grep -B 3 "threshold"
```

**Agent guidance:**

```
Agent: "Your system is ready! Here's how to use it:

1. Query high-novelty papers:
   cat modules/context/folder_index.yaml | grep 'emergence: 1.'

2. Find connected research:
   cat modules/context/folder_index.yaml | grep 'resonance: 0.8'

3. Re-index after adding files:
   python scripts/recursive_diamond_indexer.py

Want me to show you more advanced queries?"
```

---

## Advanced Agent Behaviors

### Auto-Detection of Existing Patterns

**If you detect these patterns in the user's current directory, suggest UTAC:**

- Many scattered PDFs (>20)
- Multiple nested folders with unclear hierarchy
- No README or index files
- Duplicate files with version suffixes (`paper_v1.pdf`, `paper_v2.pdf`)

**Suggestion template:**

```
Agent: "I notice you have 47 PDFs scattered across 8 folders with no index.
Would you like me to set up a UTAC structure to organize them automatically?"
```

---

### Metric Selection Heuristics

**Use these heuristics to suggest metrics:**

| User Domain | Suggested Metrics | Rationale |
|-------------|-------------------|-----------|
| Research (any field) | **CREP** | Focus on novelty (E) and connections (R) |
| Business/Finance | **ROI** → Profit, Efficiency, Risk, Opportunity | Focus on financial outcomes |
| Software Engineering | **QSTM** → Quality, Safety, Testability, Maintainability | Focus on code health |
| Creative Writing | **CRIE** → Clarity, Rhythm, Imagery, Emotion | Focus on literary qualities |
| Data Science | **DAQP** → Data quality, Accuracy, Query speed, Provenance | Focus on data integrity |

---

### Troubleshooting Guide

**Common errors and fixes:**

#### Error: "Target directory not empty"

**Fix:**
```
Agent: "The directory already has files. I can:
1. Create the structure in a subdirectory (e.g., /utac_structure/)
2. Merge with existing files (requires manual review)
3. Cancel and let you clean up first

Which would you prefer?"
```

#### Error: "Python not found"

**Fix:**
```
Agent: "I need Python 3.10+ to run the builder. Options:
1. Install Python: https://www.python.org/downloads/
2. Use Docker: docker run -v $(pwd):/data python:3.10 python /data/setup/universal_skeleton_builder.py /data/output
3. Use an online Python environment (Repl.it, Google Colab)

Which works best for you?"
```

#### Error: "Indexer produces empty index"

**Diagnosis:**
- No files in `modules/artifacts/`
- Files are in wrong format (expected JSON/YAML/CSV)

**Fix:**
```
Agent: "The indexer found no artifacts. This usually means:
1. No files in modules/artifacts/ yet (expected for fresh setup)
2. Files are in unsupported format (need JSON, YAML, or CSV)

Would you like me to:
A) Create example artifacts to test the system
B) Convert your existing files to a supported format
C) Customize the indexer to read your file types?"
```

---

## Integration with Agent Frameworks

### For MOR (Multi-Agent Orchestration)

```yaml
# Add to MOR agent config
agents:
  - name: "architect_agent"
    role: "Repository Structure Builder"
    trigger_keywords:
      - "build knowledge system"
      - "organize files"
      - "create UTAC structure"
    actions:
      - read: "setup/AGENTS_BOOTSTRAP.md"
      - execute: "setup/universal_skeleton_builder.py"
      - customize: "config/sigillin_metrics.yaml"
```

### For AutoGPT

```json
{
  "name": "UTACArchitect",
  "description": "Builds self-organizing repository structures using UTAC principles",
  "commands": [
    {
      "label": "initialize_utac",
      "command": "python setup/universal_skeleton_builder.py",
      "args": ["target_dir", "--domain", "--metrics"]
    }
  ],
  "resources": [
    "setup/THEORY_OF_STRUCTURE.md",
    "config/sigillin_metrics.yaml"
  ]
}
```

### For LangChain

```python
from langchain.tools import Tool
from langchain.agents import initialize_agent

def build_utac_skeleton(target_dir, domain="general", metrics="crep"):
    """Tool for building UTAC skeleton structures."""
    import subprocess
    result = subprocess.run([
        "python", "setup/universal_skeleton_builder.py",
        target_dir,
        "--domain", domain,
        "--metrics", metrics,
        "--verbose"
    ], capture_output=True, text=True)
    return result.stdout

utac_tool = Tool(
    name="UTAC_Skeleton_Builder",
    func=build_utac_skeleton,
    description="Creates a self-organizing repository structure. Use when user needs to organize large collections of files or build a knowledge system."
)

# Add to agent's tools
tools = [utac_tool, ...]
agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
```

---

## Success Criteria

**You've successfully executed this protocol when:**

1. ✅ Skeleton structure exists at target directory
2. ✅ User can see `modules/`, `config/`, `scripts/` folders
3. ✅ User understands what metrics mean (C, R, E, P or custom)
4. ✅ Indexer runs without errors
5. ✅ User can query the generated index
6. ✅ User knows how to add new artifacts

**Final verification checklist:**

```
Agent: "Let me verify your setup:

✓ Directory structure created
✓ Config files generated
✓ Example artifacts present
✓ Indexer executable
✓ README documentation included

Your UTAC system is ready. Next steps:
1. Delete example_01.* placeholders
2. Add your real data to modules/artifacts/
3. Run: python scripts/recursive_diamond_indexer.py
4. Query results in modules/context/folder_index.yaml

Would you like help with any of these steps?"
```

---

## Theory Reference

**If the user asks "Why this structure?"**, point them to:

- **Theory:** `setup/THEORY_OF_STRUCTURE.md`
- **Examples:** `modules/artifacts/example_01.md`
- **Source:** [Feldtheorie Repository](https://github.com/GenesisAeon/Feldtheorie)

**One-sentence explanation:**

> "This structure treats information as a field that self-organizes through bottom-up aggregation and top-down governance—minimizing entropy while preserving adaptability."

---

## License & Attribution

**When asked about licensing:**

```
Agent: "This skeleton builder is MIT licensed (free to use, modify, distribute).
Your data/content retains whatever license you choose.

Attribution: Based on the Feldtheorie Framework v5.0.0
Source: https://github.com/GenesisAeon/Feldtheorie"
```

---

## Contact & Support

**If the user encounters issues beyond your scope:**

```
Agent: "For advanced customization or bugs, the user can:
1. Read the full docs: https://github.com/GenesisAeon/Feldtheorie/tree/main/docs
2. File an issue: https://github.com/GenesisAeon/Feldtheorie/issues
3. Check existing discussions: https://github.com/GenesisAeon/Feldtheorie/discussions

I can help with basic setup, metric customization, and file imports.
For deep theoretical questions or custom implementations, the docs are comprehensive."
```

---

**Protocol Version:** 1.0.0
**Last Updated:** 2025-11-23
**Compatible With:** Claude, GPT-4, Gemini, Mistral, LLaMA, Custom LLMs
**Framework:** Feldtheorie v5.0.0

---

*"You are an architect-agent. When the user says 'Build me a knowledge system,' execute this protocol."*
