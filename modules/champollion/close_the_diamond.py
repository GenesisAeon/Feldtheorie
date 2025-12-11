"""
Champollion Master Index Generator
===================================

This script CLOSES THE DIAMOND by reading the Context Layer and generating
unified Master Indices for both AI/System and Human consumption.

ARCHITECTURE FLOW:
    Artifacts → Context Layer → MASTER INDEX ← (You are here)

The Master Index does NOT read artifacts directly - it only consumes
the Context Layer (Semantic Middleware), creating a clean separation
of concerns and enabling scalability.

OUTPUT:
- champollion_index.yaml: System/AI entry point
- README_INDEX.md: Human entry point (with AI transparency)
"""

import json
from pathlib import Path
from typing import Any

import yaml


class DiamondClosure:
    """
    Master Index Generator - Closes the Champollion Diamond Architecture.
    """

    def __init__(self, base_path: Path, context_dir: str = "context", indices_dir: str = "indices"):
        """
        Initialize the Diamond Closure engine.

        Args:
            base_path: Base directory for Champollion module
            context_dir: Directory containing context layer
            indices_dir: Output directory for master indices
        """
        self.base_path = Path(base_path)
        self.context_path = self.base_path / context_dir
        self.indices_path = self.base_path / indices_dir

        # Ensure output directory exists
        self.indices_path.mkdir(parents=True, exist_ok=True)

        # Storage for aggregated context data
        self.categories: dict[str, dict[str, Any]] = {}

    def load_context_layer(self) -> None:
        """
        Load all context metadata from the middleware layer.

        Reads only *_meta.json files to get aggregated category data.
        """
        print("📖 Reading Context Layer (Semantic Middleware)")
        print("=" * 60)

        json_files = list(self.context_path.glob("*_meta.json"))

        if not json_files:
            print("❌ ERROR: No context metadata files found!")
            print(f"   Expected files matching: {self.context_path}/*_meta.json")
            return

        for json_file in json_files:
            category = json_file.stem.replace("_meta", "")

            with open(json_file) as f:
                metadata = json.load(f)

            # Load corresponding narrative
            md_file = self.context_path / f"{category}_narrative.md"
            narrative = ""
            if md_file.exists():
                with open(md_file) as f:
                    narrative = f.read()

            # Load corresponding navigation
            yaml_file = self.context_path / f"{category}_nav.yaml"
            navigation = {}
            if yaml_file.exists():
                with open(yaml_file) as f:
                    navigation = yaml.safe_load(f)

            self.categories[category] = {
                "metadata": metadata,
                "narrative": narrative,
                "navigation": navigation,
            }

            print(f"  ✓ Loaded context for: {category}")
            print(f"    - Artifacts: {metadata.get('artifact_count', 0)}")
            print(f"    - Keywords: {len(metadata.get('search_hints', []))}")
            print(f"    - Warnings: {len(metadata.get('avoidance_protocols', []))}")

        print(f"\n✅ Loaded {len(self.categories)} categories from Context Layer")

    def generate_master_yaml(self) -> Path:
        """
        Generate champollion_index.yaml - The System/AI entry point.

        Returns:
            Path to generated YAML file
        """
        print("\n🔨 Generating Master Index (YAML) for Systems/AI")
        print("=" * 60)

        master_index = {
            "champollion_version": "5.0",
            "architecture": "Diamond (Trilayer with Context Middleware)",
            "description": "Master index for Champollion artifact system",
            "last_updated": "2025-11-23",
            "categories": {},
        }

        for category, data in self.categories.items():
            metadata = data["metadata"]
            navigation = data["navigation"]

            master_index["categories"][category] = {
                "artifact_count": metadata.get("artifact_count", 0),
                "context_layer": {
                    "json_ref": f"context/{category}_meta.json",
                    "yaml_ref": f"context/{category}_nav.yaml",
                    "md_ref": f"context/{category}_narrative.md",
                },
                "statistics": metadata.get("statistics", {}),
                "artifacts": navigation.get("artifacts", []),
            }

        output_path = self.indices_path / "champollion_index.yaml"
        with open(output_path, "w") as f:
            yaml.dump(master_index, f, default_flow_style=False, sort_keys=False)

        print(f"  ✓ Generated: {output_path}")
        return output_path

    def generate_master_readme(self) -> Path:
        """
        Generate README_INDEX.md - The Human entry point with AI transparency.

        Returns:
            Path to generated README file
        """
        print("\n📝 Generating Master Index (Markdown) for Humans")
        print("=" * 60)

        # Header
        readme_content = """# Champollion Master Index

## Overview
This is the **Master Index** for the Champollion Diamond Architecture. It provides a unified entry point to all artifacts, aggregated through an intelligent **Context Layer (Semantic Middleware)**.

### Architecture
```
┌─────────────────────────────────────┐
│      MASTER INDEX (You are here)    │
│   champollion_index.yaml + README   │
└─────────────────────────────────────┘
                 ▲
                 │ Reads from
                 │
┌─────────────────────────────────────┐
│      CONTEXT LAYER (Middleware)     │
│  Aggregated metadata by category    │
│  - search_hints (for AI)            │
│  - avoidance_protocols (for human)  │
│  - navigation (for systems)         │
└─────────────────────────────────────┘
                 ▲
                 │ Recursively aggregates
                 │
┌─────────────────────────────────────┐
│      ARTIFACTS (Raw Data)           │
│  Trilayer: YAML + JSON + MD         │
└─────────────────────────────────────┘
```

---

## Categories

"""

        # Generate category sections
        for category, data in sorted(self.categories.items()):
            metadata = data["metadata"]
            stats = metadata.get("statistics", {})

            readme_content += f"### {category.replace('_', ' ').title()}\n\n"
            readme_content += f"**Artifacts**: {metadata.get('artifact_count', 0)} | "
            readme_content += f"**Avg Signal**: {stats.get('avg_signal_strength', 0):.3f}\n\n"

            # AI Transparency Section
            search_hints = metadata.get("search_hints", [])
            if search_hints:
                readme_content += "**🤖 AI Search Hints** (What the AI looks for):\n"
                readme_content += "```\n"
                readme_content += ", ".join(search_hints)
                readme_content += "\n```\n\n"

            # Human Warnings Section
            warnings = metadata.get("avoidance_protocols", [])
            if warnings:
                readme_content += "**⚠️  Human Review Protocols**:\n"
                for warning in warnings:
                    readme_content += f"- {warning}\n"
                readme_content += "\n"

            # Navigation
            readme_content += "**📂 Context Files**:\n"
            readme_content += (
                f"- Metadata: [`context/{category}_meta.json`](context/{category}_meta.json)\n"
            )
            readme_content += f"- Narrative: [`context/{category}_narrative.md`](context/{category}_narrative.md)\n"
            readme_content += (
                f"- Navigation: [`context/{category}_nav.yaml`](context/{category}_nav.yaml)\n"
            )
            readme_content += "\n---\n\n"

        # Footer
        readme_content += """## How to Use This Index

### For AI Agents
1. Read `champollion_index.yaml` for structured navigation
2. Use `search_hints` from context JSON files for optimized retrieval
3. Check `statistics` for signal quality assessment

### For Human Researchers
1. Start with this README for overview
2. Review **Avoidance Protocols** before trusting patterns
3. Navigate to context narratives for detailed category explanations
4. Access individual artifacts only when needed

### For Systems/Scripts
1. Parse `champollion_index.yaml` for programmatic access
2. Use context YAML files for artifact references
3. Follow trilayer structure: YAML (structure) → JSON (data) → MD (narrative)

---

## Transparency Principle

This index makes AI reasoning **visible** to humans. The "AI Search Hints" sections
show exactly what keywords and patterns the AI uses for retrieval. This ensures that
both human and machine intelligence work with the same context.

**Architecture Version**: 5.0 (Diamond with Semantic Middleware)
**Last Updated**: 2025-11-23
**Maintained by**: MOR-FIT Collective
"""

        output_path = self.indices_path / "README_INDEX.md"
        with open(output_path, "w") as f:
            f.write(readme_content)

        print(f"  ✓ Generated: {output_path}")
        return output_path

    def generate_root_readme_reference(self) -> None:
        """
        Update the main Champollion README with a reference to the master index.
        """
        main_readme_path = self.base_path / "README.md"

        if not main_readme_path.exists():
            print("⚠️  Warning: Main README.md not found, skipping update")
            return

        with open(main_readme_path) as f:
            content = f.read()

        # Check if reference already exists
        if "indices/README_INDEX.md" in content:
            print("\n✓ Main README already contains index reference")
            return

        # Add reference before the "Roadmap" section
        reference = """

---

## 📚 Master Index

**NEW**: All artifacts are now accessible through the [Master Index](indices/README_INDEX.md).

The Master Index provides:
- 🤖 **AI Search Hints**: See what keywords the AI uses for retrieval
- 📊 **Category Statistics**: Signal quality metrics per category
- ⚠️  **Avoidance Protocols**: Human-readable warnings for data quality
- 🏗️  **Architecture Transparency**: Full visibility into the Context Layer

**For quick access**: [`indices/README_INDEX.md`](indices/README_INDEX.md)

---

"""

        # Insert before "## Roadmap"
        if "## Roadmap" in content:
            content = content.replace("## Roadmap", reference + "## Roadmap")
        else:
            # Append at end if no roadmap section
            content += reference

        with open(main_readme_path, "w") as f:
            f.write(content)

        print("\n✓ Updated main README with index reference")

    def close_diamond(self) -> None:
        """
        Complete the diamond closure: Generate all master indices.
        """
        # Load context data
        self.load_context_layer()

        if not self.categories:
            print("\n❌ No categories loaded. Cannot generate master indices.")
            return

        # Generate master indices
        yaml_path = self.generate_master_yaml()
        readme_path = self.generate_master_readme()

        # Update main README
        self.generate_root_readme_reference()

        print("\n" + "=" * 60)
        print("💎 DIAMOND CLOSURE COMPLETE")
        print("=" * 60)
        print("\n📍 Entry Points:")
        print(f"   - System/AI: {yaml_path}")
        print(f"   - Human:     {readme_path}")
        print("\n✨ The Champollion Diamond is now complete!")


def main():
    """Main execution: Close the diamond by generating master indices."""

    base_path = Path(__file__).parent

    print("💎 CHAMPOLLION DIAMOND CLOSURE")
    print("Master Index Generation from Context Layer")
    print("=" * 60)

    # Initialize closure engine
    closure = DiamondClosure(base_path)

    # Execute closure
    closure.close_diamond()


if __name__ == "__main__":
    main()
