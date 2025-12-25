# Customizing Dynamic Sigillin Metrics

**The Metric Constitution: Define Top-Down, Measure Bottom-Up**

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Quick Start: Adapting CREP to Your Project](#quick-start-adapting-crep-to-your-project)
3. [The Metric Constitution File](#the-metric-constitution-file)
4. [Writing Custom Algorithms](#writing-custom-algorithms)
5. [Example Adaptations](#example-adaptations)
6. [Advanced: Fractal Propagation](#advanced-fractal-propagation)
7. [Troubleshooting](#troubleshooting)

---

## Philosophy

The **Dynamic Sigillin Engine** implements a simple but powerful principle:

> **"Define what you value at the top. Measure it at the bottom. Let the truth flow upward."**

### The Problem This Solves

In traditional documentation systems:
- **Code** describes *what* exists (files, functions, classes)
- **Comments** describe *why* things exist (intent, rationale)
- **Metrics** describe *how well* things exist (quality, health)

But **metrics are usually hardcoded** into tools. If you want to measure different things, you need different tools.

### The Sigillin Solution

1. **Centralize metric definitions** in a single YAML config file
2. **Write generic algorithms** that work across domains
3. **Apply fractally** from files → folders → repository → organization
4. **Adapt without code changes** — just edit the YAML

This makes your repository a **"living document"** that measures what *you* care about, not what the tool author cared about.

---

## Quick Start: Adapting CREP to Your Project

Feldtheorie uses **CREP** (Coherence, Resonance, Emergence, Potential) to measure phase transitions in knowledge systems. But your project likely has different priorities.

### Step 1: Identify Your Values

Ask: **"What makes this project successful?"**

| Project Type | Example Metrics |
|--------------|-----------------|
| **Business** | ROI, Efficiency, Compliance, Risk |
| **Poetry** | Clarity, Rhythm, Emotion, Imagery |
| **Engineering** | Safety, Testability, Performance, Maintainability |
| **Research** | Rigor, Reproducibility, Novelty, Impact |
| **Education** | Clarity, Examples, Exercises, Depth |

### Step 2: Map to 3-5 Core Metrics

Don't use too many (cognitive overload) or too few (loss of nuance). **3-5 is ideal.**

Example for a **Business Dashboard Project**:

```yaml
active_metrics:
  R:
    label: "ROI (Return on Investment)"
    weight: 2.0  # Most important
    description: "Financial value generated vs. cost"
    algorithm: "calculate_roi"

  E:
    label: "Efficiency"
    weight: 1.5
    description: "Speed of execution, resource usage"
    algorithm: "calculate_efficiency"

  Q:
    label: "Quality"
    weight: 1.0
    description: "Test coverage, bug density"
    algorithm: "calculate_quality"

  C:
    label: "Compliance"
    weight: 1.2
    description: "Adherence to regulations and standards"
    algorithm: "calculate_compliance"
```

### Step 3: Edit the Config

Open `config/sigillin_core_definition.yaml` and replace the `active_metrics` section with your definitions.

### Step 4: Implement Stubs (or Use Generic Algorithms)

You don't need perfect algorithms immediately. Start with **stubs** that return sensible defaults:

```python
def calculate_roi(data, metric_def):
    """Stub: Estimate ROI from file count and keywords."""
    files = data.get('total_files', 0)
    keywords = len(data.get('keywords', []))
    # Simple heuristic: more files + more docs = higher ROI
    return min((files * 0.1 + keywords * 0.05) / 10, 1.0)
```

### Step 5: Run the Indexer

```bash
python modules/champollion/scripts/recursive_diamond_indexer.py .
```

Your custom metrics will now appear in every `folder_index.yaml`, `README.md`, and `folder_context.json`.

---

## The Metric Constitution File

Location: `config/sigillin_core_definition.yaml`

### Structure Overview

```yaml
# WHO ARE YOU?
project_meta:
  name: "Your Project Name"
  ontology: "What kind of system is this?"

# WHAT DO YOU VALUE?
active_metrics:
  X:  # Short key (1-2 letters)
    label: "Full Name"
    weight: 1.0  # Relative importance
    description: "What this metric captures"
    algorithm: "function_name_in_python"
    enabled: true
    thresholds:
      excellent: 0.9
      good: 0.7
      warning: 0.5
      critical: 0.3

# HOW DO YOU COMBINE THEM?
aggregation:
  method: "weighted_average"
  normalize: true

# WHAT HAPPENS WHEN THINGS GO WRONG?
governance:
  min_coherence_threshold: 0.7
  actions_on_threshold_violation:
    - type: "flag_in_report"
```

### Key Fields Explained

#### `weight`
- Multiplier for importance in aggregate score
- Example: If `ROI.weight = 2.0` and `Quality.weight = 1.0`, ROI contributes twice as much
- Use `> 1.0` for critical metrics, `< 1.0` for secondary metrics

#### `algorithm`
- Name of the Python function in `modules/champollion/engines/dynamic_crep.py`
- Must match exactly (case-sensitive)
- Function signature: `def algorithm_name(data: Dict, metric_def: Dict) -> float`

#### `thresholds`
- Define "good enough" levels for each metric
- Used to color-code results in READMEs (🟢🟡🟠🔴)
- Can be inverted: For "error count", excellent = low values

#### `enabled`
- Set to `false` to temporarily disable a metric without deleting its definition
- Useful during development or A/B testing

---

## Writing Custom Algorithms

Algorithms live in: `modules/champollion/engines/dynamic_crep.py`

### Anatomy of a Metric Algorithm

```python
def calculate_your_metric(data: Dict[str, Any], metric_def: Dict[str, Any]) -> float:
    """
    Calculate [Your Metric Name].

    Args:
        data: Aggregated folder metadata from recursive_diamond_indexer
              Contains keys like 'total_files', 'keywords', 'confidence_scores', etc.
        metric_def: The metric definition from YAML
                    Contains 'label', 'weight', 'thresholds', custom params, etc.

    Returns:
        Float score (typically 0-1, but can exceed 1 for "high" metrics like Emergence)
    """

    # 1. Extract relevant data
    files = data.get('total_files', 0)
    keywords = data.get('keywords', [])

    # 2. Apply your logic
    score = some_calculation(files, keywords)

    # 3. Return a number
    return score
```

### Available Data Fields

The `data` dictionary comes from `aggregate_folder_metadata()` in the indexer:

| Key | Type | Description |
|-----|------|-------------|
| `folder_name` | str | Name of the current folder |
| `total_files` | int | Number of files (excluding ignored) |
| `total_subfolders` | int | Number of subfolders |
| `metadata_files` | list | List of metadata JSON files found |
| `subfolder_contexts` | list | Metadata propagated from child folders |
| `origins` | dict | Count of data origins (empirical, synthetic, etc.) |
| `confidence_scores` | list | List of confidence values from metadata |
| `keywords` | list | Aggregated keywords from all sources |
| `file_types` | dict | Count of file extensions (`.py`, `.md`, etc.) |
| `governance_violations` | list | Any detected policy violations |

### Example: ROI Algorithm

```python
def calculate_roi(data: Dict[str, Any], metric_def: Dict[str, Any]) -> float:
    """
    Calculate Return on Investment.

    Heuristic: ROI = (value generated) / (cost invested)

    We estimate:
    - Value = Number of documented features (keywords like "feature", "api")
    - Cost = Number of files (proxy for development time)
    """
    keywords = data.get('keywords', [])
    files = data.get('total_files', 1)  # Avoid division by zero

    # Count "value" keywords
    value_keywords = ['feature', 'api', 'endpoint', 'service', 'product']
    value_count = sum(1 for kw in keywords if any(v in kw.lower() for v in value_keywords))

    # ROI formula
    roi = value_count / files

    # Normalize to [0, 1] range (assuming 1 value keyword per 2 files is excellent)
    normalized_roi = min(roi / 0.5, 1.0)

    return normalized_roi
```

### Registering Your Algorithm

Add your function to the `algorithm_registry` in `DynamicMetricEngine.__init__()`:

```python
self.algorithm_registry: Dict[str, Callable] = {
    'calculate_coherence': self.calculate_coherence,
    'calculate_resonance': self.calculate_resonance,
    # ... existing algorithms ...
    'calculate_roi': self.calculate_roi,  # ADD THIS LINE
}
```

---

## Example Adaptations

### 1. Business Analytics Dashboard

**Goal:** Measure financial health and performance.

```yaml
active_metrics:
  P:
    label: "Profit Margin"
    weight: 2.5
    algorithm: "calculate_profit_margin"
    thresholds:
      excellent: 0.25  # 25%+ margin
      good: 0.15
      warning: 0.05
      critical: 0.0

  E:
    label: "Efficiency"
    weight: 1.5
    algorithm: "calculate_efficiency"
    thresholds:
      excellent: 0.9
      good: 0.7

  R:
    label: "Risk Score"
    weight: 1.8
    algorithm: "calculate_risk"
    thresholds:
      excellent: 0.1  # LOWER is better for risk
      good: 0.3
      warning: 0.6
      critical: 0.9
```

**Note:** For "inverted" metrics like risk (lower = better), adjust the threshold order.

### 2. Poetry Collection

**Goal:** Measure aesthetic and emotional impact.

```yaml
active_metrics:
  C:
    label: "Clarity"
    weight: 1.0
    description: "How understandable is the language?"
    algorithm: "calculate_clarity"

  R:
    label: "Rhythm"
    weight: 1.2
    description: "Meter, rhyme, musical quality"
    algorithm: "calculate_rhythm"

  E:
    label: "Emotion"
    weight: 1.5
    description: "Affective intensity"
    algorithm: "calculate_emotion"
    markers: ["love", "fear", "joy", "sorrow", "anger"]

  I:
    label: "Imagery"
    weight: 1.0
    description: "Vividness of sensory language"
    algorithm: "calculate_imagery"
```

### 3. Research Lab Notebook

**Goal:** Ensure rigor and reproducibility.

```yaml
active_metrics:
  R:
    label: "Rigor"
    weight: 1.8
    algorithm: "calculate_rigor"
    thresholds:
      excellent: 0.9
      critical: 0.6  # Strict threshold

  V:
    label: "Reproducibility"
    weight: 2.0  # Most critical
    algorithm: "calculate_reproducibility"
    markers: ["seed", "version", "environment", "requirements"]

  N:
    label: "Novelty"
    weight: 1.0
    algorithm: "calculate_novelty"

  I:
    label: "Impact"
    weight: 1.2
    algorithm: "calculate_impact"
```

---

## Advanced: Fractal Propagation

One of Sigillin's most powerful features: **Metrics propagate upward** through the folder hierarchy.

### How It Works

1. **Leaf folders** (no subfolders) calculate metrics from files
2. **Branch folders** (with subfolders) aggregate metrics from children
3. **Root folder** sees the entire repository's health at a glance

### Accessing Parent Metrics

When calculating a folder's metrics, you can access child folder metrics via `subfolder_contexts`:

```python
def calculate_aggregate_quality(data: Dict[str, Any], metric_def: Dict[str, Any]) -> float:
    """Calculate quality as average of child folder qualities."""

    subfolder_contexts = data.get('subfolder_contexts', [])

    if not subfolder_contexts:
        # Leaf folder: calculate from files
        return calculate_quality_from_files(data)

    # Branch folder: aggregate from children
    child_qualities = []
    for sf in subfolder_contexts:
        sigillin = sf.get('sigillin', {})
        components = sigillin.get('components', {})
        if 'Q' in components:  # 'Q' is the quality metric key
            child_qualities.append(components['Q'])

    if child_qualities:
        return sum(child_qualities) / len(child_qualities)
    else:
        return 0.5  # Default
```

### Example: Weighted Propagation

You might want **larger subfolders** to contribute more to the parent's score:

```python
def calculate_weighted_resonance(data: Dict[str, Any], metric_def: Dict[str, Any]) -> float:
    """Resonance weighted by subfolder size."""

    subfolder_contexts = data.get('subfolder_contexts', [])

    total_weighted_score = 0.0
    total_weight = 0.0

    for sf in subfolder_contexts:
        size = sf.get('total_files', 0)
        sigillin = sf.get('sigillin', {})
        resonance = sigillin.get('components', {}).get('R', 0.5)

        total_weighted_score += resonance * size
        total_weight += size

    if total_weight > 0:
        return total_weighted_score / total_weight
    else:
        return 0.5
```

---

## Troubleshooting

### "Algorithm not found" Warning

**Symptom:**
```
⚠️  Warning: Algorithm 'calculate_roi' not found for metric 'R'
```

**Solution:**
1. Check spelling in `config/sigillin_core_definition.yaml` (case-sensitive)
2. Ensure function exists in `dynamic_crep.py`
3. Ensure function is registered in `algorithm_registry`

### Metrics Always Return 0.0

**Possible Causes:**
1. **Empty data:** Your test folder has no files
2. **Algorithm bug:** Check for division by zero
3. **Wrong data keys:** Typo in `data.get('keyword')` (should be `keywords`)

**Debug:**
```python
def calculate_debug(data, metric_def):
    print(f"DEBUG: {data}")  # Print all available data
    return 0.5
```

### Aggregate Score Seems Wrong

**Check:**
1. **Weights:** Are they balanced? Total weight = sum of all metric weights
2. **Normalization:** Set `aggregation.normalize: false` to see raw values
3. **Thresholds:** These don't affect the score, only the color coding

### Import Error on Indexer

**Symptom:**
```
⚠️  Warning: Dynamic Sigillin Engine not available: No module named 'engines'
```

**Solution:**
1. Check that `modules/champollion/engines/dynamic_crep.py` exists
2. Ensure `__init__.py` exists in `modules/champollion/engines/` (for Python package)
3. Run indexer from repository root: `python modules/champollion/scripts/recursive_diamond_indexer.py .`

Create the `__init__.py` if missing:
```bash
touch modules/champollion/engines/__init__.py
```

---

## Next Steps

1. **Fork and Experiment:** Copy `sigillin_core_definition.yaml` and create variants for different projects
2. **Share Configs:** Publish your metric definitions for others to adapt
3. **Build Dashboards:** Use the YAML output to create visualizations (radar charts, time series)
4. **Integrate CI/CD:** Block merges if metrics fall below thresholds

---

## Philosophy Recap

> **"The map is not the territory, but a good map makes the territory navigable."**

Metrics don't *create* quality — they **make quality visible**. By defining what you value at the top and measuring it fractally at every level, you create a **self-documenting, self-regulating system** that breathes with your project.

This is the essence of **Dynamic Sigillin**: Not a rigid framework, but a **living constitution** for knowledge.

---

**Questions? See:**
- `config/sigillin_core_definition.yaml` (working example)
- `modules/champollion/engines/dynamic_crep.py` (algorithm implementations)
- `modules/champollion/scripts/recursive_diamond_indexer.py` (integration logic)

**Contribute:**
- Share your custom metric definitions: [GitHub Discussions](https://github.com/GenesisAeon/Feldtheorie/discussions)
- Report bugs or request features: [Issues](https://github.com/GenesisAeon/Feldtheorie/issues)
