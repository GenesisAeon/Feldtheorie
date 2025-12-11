#!/usr/bin/env python3
"""
Universal UTAC Skeleton Builder
================================

This script generates an empty, self-organizing repository structure based on
the "Feldtheorie" framework (Diamond Architecture + Fractal Governance).

PHILOSOPHY:
    "Structure is frozen information. This script helps you keep your information fluid."

    The UTAC (Universal Threshold Activation-Coupling) framework models information
    as a field that undergoes phase transitions. This builder creates a repository
    structure that embodies these principles:

    - Emergent: Order arises from bottom-up indexing
    - Entropic: Information compression through recursive aggregation
    - Self-similar: Each subfolder mirrors the root structure
    - Adaptive: Metrics evolve with your project's needs

USAGE:
    python universal_skeleton_builder.py /path/to/new/project

    Optional arguments:
        --domain: Project domain (physics, business, literature, etc.)
        --metrics: Metric system (crep, roi, kpi, custom)
        --verbose: Show detailed output

WHAT IT CREATES:
    config/
        sigillin_metrics.yaml      - Your quality measurement system
        fractal_governance.yaml    - Self-similar propagation rules
    modules/
        context/                   - Where indices live (generated)
        artifacts/                 - Where your data goes (you fill this)
        navigation/                - YAML navigation maps
    scripts/
        recursive_diamond_indexer.py   - Bottom-up aggregation engine
        fractal_governance.py          - Top-down rule propagation
    README.md                      - Project documentation

THEORY:
    Read setup/THEORY_OF_STRUCTURE.md for the physics behind this architecture.

LICENSE: MIT
AUTHOR: Feldtheorie Framework (adapted from v5.0.0)
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class UniversalSkeletonBuilder:
    """Builds a self-organizing repository skeleton based on UTAC principles."""

    def __init__(
        self,
        target_path: Path,
        domain: str = "general",
        metrics: str = "crep",
        verbose: bool = False,
    ):
        self.target = target_path
        self.domain = domain
        self.metrics = metrics
        self.verbose = verbose

        if verbose:
            logger.setLevel(logging.DEBUG)

    def build(self) -> None:
        """Execute the full build pipeline."""
        logger.info(f"🚀 Initializing Universal UTAC Skeleton at: {self.target}")

        try:
            self._validate_target()
            self._create_directory_structure()
            self._generate_config_files()
            self._create_dummy_artifacts()
            self._install_base_scripts()
            self._generate_root_readme()

            logger.info("✅ Skeleton successfully created!")
            logger.info(f"📂 Navigate to: {self.target}")
            logger.info("📖 Read THEORY_OF_STRUCTURE.md to understand the architecture")
            logger.info("🔧 Customize config/sigillin_metrics.yaml to fit your project")

        except Exception as e:
            logger.error(f"❌ Build failed: {e}")
            sys.exit(1)

    def _validate_target(self) -> None:
        """Ensure target directory is safe to use."""
        if self.target.exists():
            if any(self.target.iterdir()):
                response = input(f"⚠️  Directory {self.target} is not empty. Continue? [y/N]: ")
                if response.lower() != "y":
                    logger.info("Build cancelled.")
                    sys.exit(0)
        else:
            self.target.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created target directory: {self.target}")

    def _create_directory_structure(self) -> None:
        """Create the Diamond Architecture folder hierarchy."""
        logger.info("📁 Creating directory structure...")

        directories = [
            "config",
            "modules/context",
            "modules/artifacts",
            "modules/navigation",
            "scripts",
            "docs",
            "data",
            "tests",
        ]

        for directory in directories:
            path = self.target / directory
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"  ✓ {directory}/")

        # Create .gitkeep files for empty directories
        (self.target / "modules" / "context" / ".gitkeep").write_text(
            "# This directory will be populated by the recursive indexer\n"
        )

    def _generate_config_files(self) -> None:
        """Generate configuration templates."""
        logger.info("⚙️  Generating configuration files...")

        # 1. Sigillin Metrics Configuration
        metrics_config = self._get_metrics_template()
        metrics_path = self.target / "config" / "sigillin_metrics.yaml"
        metrics_path.write_text(metrics_config)
        logger.debug(f"  ✓ {metrics_path.name}")

        # 2. Fractal Governance Configuration
        governance_config = self._get_governance_template()
        governance_path = self.target / "config" / "fractal_governance.yaml"
        governance_path.write_text(governance_config)
        logger.debug(f"  ✓ {governance_path.name}")

    def _get_metrics_template(self) -> str:
        """Generate metrics configuration based on selected system."""
        if self.metrics == "crep":
            return self._get_crep_metrics()
        elif self.metrics == "roi":
            return self._get_roi_metrics()
        elif self.metrics == "kpi":
            return self._get_kpi_metrics()
        else:
            return self._get_crep_metrics()  # Default fallback

    def _get_crep_metrics(self) -> str:
        """CREP metrics template (default for research/theory)."""
        return """# =============================================================================
# SIGILLIN METRICS CONFIGURATION - CREP Framework
# =============================================================================
#
# This file defines WHAT you measure and HOW you aggregate it.
# CREP = Coherence, Resonance, Emergence, Potential
#
# ADAPT THIS to your project:
#   - Change weights to prioritize what matters
#   - Replace metrics entirely (see examples below)
#   - Add custom metrics using the extension system
# =============================================================================

project_meta:
  name: "Your Project Name"
  version: "1.0.0"
  domain: "general"
  ontology: "Tri-Layer (Machine/Logic/Narrative)"

active_metrics:

  C:
    label: "Coherence"
    weight: 1.2
    description: |
      Internal consistency: Are code, docs, and metadata aligned?
      High coherence = low variance in confidence scores.
    algorithm: "calculate_coherence"
    enabled: true
    thresholds:
      excellent: 0.9
      good: 0.7
      warning: 0.5

  R:
    label: "Resonance"
    weight: 1.0
    description: |
      External connectivity: How many other artifacts reference this?
      Based on link density and keyword overlap.
    algorithm: "calculate_resonance"
    enabled: true
    thresholds:
      excellent: 0.8
      good: 0.6
      warning: 0.4

  E:
    label: "Emergence"
    weight: 0.8
    description: |
      Novelty and phase transitions: Is this artifact creating new patterns?
      Detects entropy spikes and complexity increases.
    algorithm: "calculate_emergence"
    enabled: true
    thresholds:
      excellent: 1.5
      good: 1.0
      warning: 0.5

  P:
    label: "Potential"
    weight: 1.1
    description: |
      Future capacity: Open TODOs, experimental markers, growth opportunities.
    algorithm: "calculate_potential"
    enabled: true
    thresholds:
      excellent: 0.9
      good: 0.7
      warning: 0.5
    markers:
      - "TODO"
      - "FIXME"
      - "WIP"

# -----------------------------------------------------------------------------
# ALTERNATIVE METRIC SYSTEMS (Uncomment to use)
# -----------------------------------------------------------------------------

# For BUSINESS projects, replace CREP with:
# active_metrics:
#   P:
#     label: "Profit"
#     weight: 2.0
#   E:
#     label: "Efficiency"
#     weight: 1.5
#   R:
#     label: "Risk"
#     weight: 1.0
#   O:
#     label: "Opportunity"
#     weight: 1.2

# For ENGINEERING projects:
# active_metrics:
#   Q:
#     label: "Quality"
#     weight: 1.5
#   S:
#     label: "Safety"
#     weight: 2.0
#   T:
#     label: "Testability"
#     weight: 1.0
#   M:
#     label: "Maintainability"
#     weight: 1.2

aggregation:
  method: "weighted_average"
  normalize: true
  include_disabled: false

governance:
  min_coherence_threshold: 0.7
  min_resonance_threshold: 0.4
  violation_report_path: "docs/governance/metric_violations.md"

algorithm_params:
  coherence:
    use_confidence_variance: true
    use_keyword_alignment: true
  resonance:
    count_internal_links: true
    decay_factor: 0.5
  emergence:
    mode: "stub"
    stub_randomness: 0.3
  potential:
    scan_file_contents: true
    max_files_to_scan: 100

output:
  include_in_yaml_index: true
  include_in_readme: true
  readme_section_title: "📊 System Metrics"

meta:
  config_version: "1.0.0"
  adaptable: true
  documentation: "See setup/THEORY_OF_STRUCTURE.md"
"""

    def _get_roi_metrics(self) -> str:
        """ROI-focused metrics for business/finance projects."""
        return """# Business Metrics Template (ROI-focused)
# Adapt this for financial, business, or investment projects

project_meta:
  name: "Your Business Project"
  domain: "business"

active_metrics:
  P:
    label: "Profit"
    weight: 2.0
    description: "Revenue minus costs"
    enabled: true

  E:
    label: "Efficiency"
    weight: 1.5
    description: "Output per unit input"
    enabled: true

  R:
    label: "Risk"
    weight: 1.0
    description: "Exposure to uncertainty"
    enabled: true

  O:
    label: "Opportunity"
    weight: 1.2
    description: "Potential future growth"
    enabled: true

aggregation:
  method: "weighted_average"
  normalize: true

meta:
  config_version: "1.0.0"
  adaptable: true
"""

    def _get_kpi_metrics(self) -> str:
        """KPI template for tech/engineering projects."""
        return """# Technical KPI Template
# For software engineering, DevOps, or technical operations

project_meta:
  name: "Your Tech Project"
  domain: "engineering"

active_metrics:
  Q:
    label: "Quality"
    weight: 1.5
    description: "Code quality, test coverage, bug density"
    enabled: true

  S:
    label: "Safety"
    weight: 2.0
    description: "Security vulnerabilities, error handling"
    enabled: true

  T:
    label: "Testability"
    weight: 1.0
    description: "Ease of testing, test isolation"
    enabled: true

  M:
    label: "Maintainability"
    weight: 1.2
    description: "Code complexity, documentation quality"
    enabled: true

aggregation:
  method: "weighted_average"
  normalize: true

meta:
  config_version: "1.0.0"
  adaptable: true
"""

    def _get_governance_template(self) -> str:
        """Generate fractal governance configuration."""
        return """# =============================================================================
# FRACTAL GOVERNANCE CONFIGURATION
# =============================================================================
#
# This file defines HOW metrics and rules propagate through the folder hierarchy.
# Principle: "Define Top-Down, Measure Bottom-Up"
#
# The Diamond Architecture ensures that:
#   1. Each subfolder inherits metrics from its parent (Top-Down)
#   2. Each subfolder aggregates data from its children (Bottom-Up)
#   3. The result is self-similar: Every level looks like the root
# =============================================================================

governance_meta:
  version: "1.0.0"
  framework: "Fractal Diamond Architecture"
  principle: "Define Top-Down, Measure Bottom-Up"

# -----------------------------------------------------------------------------
# PROPAGATION RULES
# -----------------------------------------------------------------------------

propagation:
  mode: "inherit_with_override"  # Child folders can override parent metrics

  # Which files propagate to subfolders?
  inherited_configs:
    - "sigillin_metrics.yaml"
    - "fractal_governance.yaml"

  # Should children see parent metrics?
  parent_visibility: true

  # Maximum depth for recursive aggregation (prevents infinite loops)
  max_depth: 10

# -----------------------------------------------------------------------------
# AGGREGATION STRATEGY
# -----------------------------------------------------------------------------

aggregation:
  # How to combine metrics from subfolders?
  strategy: "weighted_average"  # Options: weighted_average, max, min, median

  # Should the root folder include its own metrics, or only children's?
  include_root_self: true

  # Decay factor: Do deeper folders matter less?
  depth_decay_factor: 0.9  # 1.0 = no decay, 0.5 = strong decay

# -----------------------------------------------------------------------------
# CONFLICT RESOLUTION
# -----------------------------------------------------------------------------

conflicts:
  # What happens when child and parent define the same metric differently?
  resolution_strategy: "child_wins"  # Options: child_wins, parent_wins, merge

  # Log conflicts for review?
  log_conflicts: true
  log_path: "docs/governance/conflicts.md"

# -----------------------------------------------------------------------------
# INDEXING BEHAVIOR
# -----------------------------------------------------------------------------

indexing:
  # Which files should the indexer create?
  generate_yaml_index: true
  generate_json_index: true
  generate_markdown_index: true

  # Naming convention
  index_filename_base: "folder_index"  # Creates folder_index.{yaml,json,md}

  # Should indices be committed to git?
  git_tracked: true

# -----------------------------------------------------------------------------
# VALIDATION RULES
# -----------------------------------------------------------------------------

validation:
  # Enforce minimum metric scores?
  enforce_thresholds: false  # Set true for strict governance

  # Block commits if metrics fall below threshold?
  block_on_violation: false  # Requires CI/CD integration

  # Generate violation reports?
  report_violations: true
  report_path: "docs/governance/violations.md"

# -----------------------------------------------------------------------------
# METADATA
# -----------------------------------------------------------------------------

meta:
  created: "2025-11-23"
  author: "Universal UTAC Skeleton Builder"
  license: "MIT"
  documentation: "See setup/THEORY_OF_STRUCTURE.md"
"""

    def _create_dummy_artifacts(self) -> None:
        """Create placeholder artifacts with instructions."""
        logger.info("📝 Creating example artifacts...")

        # JSON data example
        example_json = {
            "id": "example_01",
            "type": "placeholder",
            "description": "This is a template artifact. Replace with your real data.",
            "metadata": {
                "created": "2025-11-23",
                "domain": self.domain,
                "tags": ["example", "template", "delete-me"],
            },
            "data": {
                "x": [1, 2, 3, 4, 5],
                "y": [2, 4, 6, 8, 10],
                "note": "This is sample data. Delete when you add real artifacts.",
            },
        }

        json_path = self.target / "modules" / "artifacts" / "example_01.json"
        json_path.write_text(json.dumps(example_json, indent=2))
        logger.debug(f"  ✓ {json_path.name}")

        # Markdown narrative example
        example_md = """# Example Artifact 01

## Purpose
This is a **placeholder artifact** demonstrating the tri-layer structure:
- **Data Layer:** `example_01.json` (machine-readable)
- **Narrative Layer:** This file (human-readable context)
- **Logic Layer:** Processing scripts in `/scripts/` (executable)

## Instructions
1. Delete this file when you add real data
2. Follow the naming convention: `<name>.json` + `<name>.md`
3. Keep narratives concise but meaningful

## Metadata
- **Domain:** General
- **Type:** Placeholder
- **Status:** DELETE_ME

---

**Note:** Read `setup/THEORY_OF_STRUCTURE.md` to understand why we use this tri-layer approach.
"""

        md_path = self.target / "modules" / "artifacts" / "example_01.md"
        md_path.write_text(example_md)
        logger.debug(f"  ✓ {md_path.name}")

    def _install_base_scripts(self) -> None:
        """Create minimal script stubs (users can replace with full versions)."""
        logger.info("🔧 Installing base scripts...")

        # Minimal indexer stub
        indexer_stub = """#!/usr/bin/env python3
\"\"\"
Recursive Diamond Indexer - Minimal Stub
=========================================

This is a MINIMAL stub. For the full implementation, see:
https://github.com/GenesisAeon/Feldtheorie/tree/main/scripts

WHAT IT SHOULD DO:
    1. Walk through modules/artifacts/
    2. Read all JSON files
    3. Extract metadata and keywords
    4. Aggregate into modules/context/folder_index.{yaml,json,md}
    5. Calculate CREP metrics using config/sigillin_metrics.yaml
    6. Propagate results up the folder hierarchy

TODO: Implement full recursive aggregation logic.
\"\"\"

import json
from pathlib import Path

def index_artifacts(artifacts_dir: Path, context_dir: Path):
    \"\"\"Minimal indexer stub.\"\"\"
    print(f"🔍 Indexing artifacts in {artifacts_dir}")

    # Find all JSON files
    json_files = list(artifacts_dir.glob("**/*.json"))

    # Create a simple index
    index = {
        "total_artifacts": len(json_files),
        "files": [str(f.relative_to(artifacts_dir)) for f in json_files]
    }

    # Write to context directory
    output_path = context_dir / "folder_index.json"
    output_path.write_text(json.dumps(index, indent=2))

    print(f"✅ Created index: {output_path}")
    print("⚠️  This is a minimal stub. Implement full logic for production use.")

if __name__ == "__main__":
    artifacts = Path("modules/artifacts")
    context = Path("modules/context")

    if artifacts.exists():
        index_artifacts(artifacts, context)
    else:
        print(f"❌ Artifacts directory not found: {artifacts}")
"""

        indexer_path = self.target / "scripts" / "recursive_diamond_indexer.py"
        indexer_path.write_text(indexer_stub)
        indexer_path.chmod(0o755)  # Make executable
        logger.debug(f"  ✓ {indexer_path.name} (stub)")

        # Governance script stub
        governance_stub = """#!/usr/bin/env python3
\"\"\"
Fractal Governance Engine - Minimal Stub
=========================================

This is a MINIMAL stub. For the full implementation, see:
https://github.com/GenesisAeon/Feldtheorie/tree/main/scripts

WHAT IT SHOULD DO:
    1. Read config/fractal_governance.yaml
    2. Propagate rules to all subfolders
    3. Validate metric thresholds
    4. Generate violation reports

TODO: Implement full governance logic.
\"\"\"

from pathlib import Path
import yaml

def propagate_governance(config_path: Path):
    \"\"\"Minimal governance stub.\"\"\"
    print(f"📐 Propagating governance from {config_path}")

    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        return

    with open(config_path) as f:
        config = yaml.safe_load(f)

    print(f"✅ Loaded config: {config['governance_meta']['framework']}")
    print("⚠️  This is a minimal stub. Implement full logic for production use.")

if __name__ == "__main__":
    config = Path("config/fractal_governance.yaml")
    if config.exists():
        propagate_governance(config)
    else:
        print(f"❌ Governance config not found: {config}")
"""

        governance_path = self.target / "scripts" / "fractal_governance.py"
        governance_path.write_text(governance_stub)
        governance_path.chmod(0o755)
        logger.debug(f"  ✓ {governance_path.name} (stub)")

    def _generate_root_readme(self) -> None:
        """Generate a minimal README with setup instructions."""
        logger.info("📄 Generating README.md...")

        readme = f"""# {self.domain.title()} Project - UTAC Architecture

## Welcome!

This repository was generated using the **Universal UTAC Skeleton Builder**.

It follows the principles of:
- **Diamond Architecture**: Data, Context, Navigation layers
- **Fractal Governance**: Self-similar rules at all scales
- **Tri-Layer Documentation**: Machine (YAML/JSON), Logic (Python), Narrative (Markdown)

## Quick Start

1. **Add your data:**
   ```bash
   # Put your files in modules/artifacts/
   cp my_data.csv modules/artifacts/
   ```

2. **Customize metrics:**
   ```bash
   # Edit config/sigillin_metrics.yaml to define what you measure
   nano config/sigillin_metrics.yaml
   ```

3. **Run the indexer:**
   ```bash
   # Generate indices from your artifacts
   python scripts/recursive_diamond_indexer.py
   ```

4. **Check results:**
   ```bash
   # View the aggregated index
   cat modules/context/folder_index.json
   ```

## Directory Structure

```
.
├── config/
│   ├── sigillin_metrics.yaml       ← What you measure (CREP, ROI, KPI, etc.)
│   └── fractal_governance.yaml     ← How rules propagate
├── modules/
│   ├── artifacts/                  ← YOUR DATA GOES HERE
│   ├── context/                    ← Generated indices (don't edit manually)
│   └── navigation/                 ← Navigation maps
├── scripts/
│   ├── recursive_diamond_indexer.py  ← Generates indices
│   └── fractal_governance.py         ← Propagates rules
└── README.md                       ← You are here
```

## Understanding the Architecture

Read **`setup/THEORY_OF_STRUCTURE.md`** to understand:
- Why folders are "states" not "containers"
- How bottom-up indexing compresses information
- Why self-similarity matters for scalability

## Customization

### Change Metrics

The default CREP framework measures:
- **C**oherence (internal consistency)
- **R**esonance (external connectivity)
- **E**mergence (novelty, phase transitions)
- **P**otential (future capacity)

**For business projects**, replace with ROI metrics:
```yaml
active_metrics:
  P:
    label: "Profit"
    weight: 2.0
  E:
    label: "Efficiency"
    weight: 1.5
```

**For engineering**, use KPIs:
```yaml
active_metrics:
  Q:
    label: "Quality"
  S:
    label: "Safety"
```

See `config/sigillin_metrics.yaml` for examples.

## Philosophy

> "Structure is frozen information. This repo helps you keep your information fluid."

The UTAC framework models information as a field undergoing phase transitions.
By organizing your project this way, you're not just filing documents—you're
creating a **self-organizing knowledge system**.

## Next Steps

1. Delete `modules/artifacts/example_01.*` (placeholders)
2. Add your real data
3. Customize `config/sigillin_metrics.yaml`
4. Run the indexer
5. Watch your system self-organize!

## License

This skeleton structure: MIT License
(Your data/content retains your own license)

---

**Generated by:** Universal UTAC Skeleton Builder v1.0.0
**Based on:** Feldtheorie Framework v5.0.0
**Learn more:** https://github.com/GenesisAeon/Feldtheorie
"""

        readme_path = self.target / "README.md"
        readme_path.write_text(readme)
        logger.debug(f"  ✓ {readme_path.name}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Universal UTAC Skeleton Builder - Create self-organizing repository structures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python universal_skeleton_builder.py ~/my-new-project
  python universal_skeleton_builder.py /tmp/test --metrics roi --verbose
  python universal_skeleton_builder.py . --domain physics --metrics crep

Theory:
  Read setup/THEORY_OF_STRUCTURE.md to understand the architecture.

Source:
  https://github.com/GenesisAeon/Feldtheorie
        """,
    )

    parser.add_argument("target", type=Path, help="Target directory for the new skeleton")

    parser.add_argument(
        "--domain",
        type=str,
        default="general",
        help="Project domain (physics, business, literature, etc.)",
    )

    parser.add_argument(
        "--metrics",
        type=str,
        default="crep",
        choices=["crep", "roi", "kpi"],
        help="Metric system to use (crep=research, roi=business, kpi=engineering)",
    )

    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    # Build the skeleton
    builder = UniversalSkeletonBuilder(
        target_path=args.target, domain=args.domain, metrics=args.metrics, verbose=args.verbose
    )

    builder.build()


if __name__ == "__main__":
    main()
