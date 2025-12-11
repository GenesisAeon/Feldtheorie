"""
Champollion Intelligent Ingestion Script
=========================================

This script implements the recursive Context Layer generation for the
Champollion Diamond Architecture:

    Artifacts → Context Layer → Master Index

ARCHITECTURE:
1. Ingest raw data (CSV) → Create Trilayer Artifacts (YAML/JSON/MD)
2. RECURSION: Re-read artifacts → Aggregate metadata by category
3. Generate Context Layer (Semantic Middleware)
4. Output ready for Master Index consumption

TRILAYER STRUCTURE:
- YAML: Navigation & Structure (for systems)
- JSON: Logic & Metadata (for AI)
- MD: Narrative & Human-readable (for humans)
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


class ChampollionIngestion:
    """
    Intelligent ingestion engine with recursive context generation.
    """

    def __init__(
        self, base_path: Path, artifacts_dir: str = "artifacts", context_dir: str = "context"
    ):
        """
        Initialize the ingestion engine.

        Args:
            base_path: Base directory for Champollion module
            artifacts_dir: Subdirectory for artifact storage
            context_dir: Subdirectory for context layer
        """
        self.base_path = Path(base_path)
        self.artifacts_path = self.base_path / artifacts_dir
        self.context_path = self.base_path / context_dir

        # Ensure directories exist
        self.artifacts_path.mkdir(parents=True, exist_ok=True)
        self.context_path.mkdir(parents=True, exist_ok=True)

        # Category aggregation storage
        self.category_data: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def categorize_signal(self, signal_strength: float) -> str:
        """
        Categorize signal by coherence level.

        Args:
            signal_strength: Signal strength value [0, 1]

        Returns:
            Category name: 'high_coherence', 'medium_coherence', 'low_coherence'
        """
        if signal_strength >= 0.5:
            return "high_coherence"
        elif signal_strength >= 0.35:
            return "medium_coherence"
        else:
            return "low_coherence"

    def extract_keywords(self, notes: str) -> list[str]:
        """
        Extract search keywords from notes.

        Args:
            notes: Note text from CSV

        Returns:
            List of extracted keywords
        """
        # Common keywords that indicate important metadata
        keyword_patterns = [
            r"\b(threshold|coherence|entropy|baseline|signature|pattern|noise)\b",
            r"\b(Cicada|row \d+)\b",
            r"\b(detected|approach|emergence|drift|coupling)\b",
        ]

        keywords = []
        for pattern in keyword_patterns:
            matches = re.findall(pattern, notes, re.IGNORECASE)
            keywords.extend(matches)

        return list(set(keywords))  # Remove duplicates

    def extract_warnings(self, notes: str) -> list[str]:
        """
        Extract warning/avoidance protocols from notes.

        Args:
            notes: Note text from CSV

        Returns:
            List of warnings
        """
        warnings = []

        # Detect warning indicators
        if "noise" in notes.lower():
            warnings.append("High noise level - verify signal authenticity")
        if "drift" in notes.lower():
            warnings.append("Coherence drift detected - unstable pattern")
        if "baseline" in notes.lower():
            warnings.append("Near baseline - may be random noise")
        if "cicada" in notes.lower():
            warnings.append("ATTENTION: Cicada signature - hidden pattern marker")

        return warnings

    def create_artifact_trilayer(self, artifact_id: str, data: dict[str, Any]) -> None:
        """
        Create Trilayer artifact (YAML, JSON, MD) for a single data entry.

        Args:
            artifact_id: Unique identifier for artifact
            data: Dictionary containing artifact data
        """
        # Prepare base filename
        base_name = self.artifacts_path / f"artifact_{artifact_id}"

        # 1. YAML - Structure & Navigation
        yaml_data = {
            "artifact_id": artifact_id,
            "category": data["category"],
            "signal_strength": data["signal_strength"],
            "metadata": {
                "created": "2025-11-23",
                "source": "mock_rosetta.csv",
                "type": "symbol_sequence",
            },
        }

        with open(f"{base_name}.yaml", "w") as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

        # 2. JSON - Logic & AI Metadata
        json_data = {
            "artifact_id": artifact_id,
            "symbol_sequence": data["symbol_sequence"],
            "signal_strength": data["signal_strength"],
            "category": data["category"],
            "search_hints": data["keywords"],
            "warnings": data["warnings"],
            "entropy_estimate": self._estimate_entropy(data["symbol_sequence"]),
        }

        with open(f"{base_name}.json", "w") as f:
            json.dump(json_data, f, indent=2)

        # 3. MD - Human-Readable Narrative
        md_content = f"""# Artifact {artifact_id}

## Overview
**Category**: {data['category']}
**Signal Strength**: {data['signal_strength']:.3f}
**Symbol Sequence**: `{data['symbol_sequence']}`

## Notes
{data['notes']}

## Search Keywords
{', '.join(data['keywords']) if data['keywords'] else 'None detected'}

## Warnings & Avoidance Protocols
{''.join(f'- {w}' + chr(10) for w in data['warnings']) if data['warnings'] else 'No warnings'}

## Metadata
- **Source**: mock_rosetta.csv
- **Type**: Symbol Sequence
- **Entropy**: {self._estimate_entropy(data['symbol_sequence']):.3f} bits
"""

        with open(f"{base_name}.md", "w") as f:
            f.write(md_content)

    def _estimate_entropy(self, sequence: str) -> float:
        """
        Estimate Shannon entropy of symbol sequence.

        Args:
            sequence: Symbol string

        Returns:
            Entropy in bits
        """
        if not sequence:
            return 0.0

        # Character frequency
        freq = defaultdict(int)
        for char in sequence:
            freq[char] += 1

        # Calculate Shannon entropy: H = -Σ p(x) * log2(p(x))
        import math

        total = len(sequence)
        entropy = 0.0
        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        return entropy

    def ingest_csv(self, csv_path: Path) -> None:
        """
        Phase 1: Ingest CSV data and create artifact trilayers.

        Args:
            csv_path: Path to input CSV file
        """
        print(f"📥 PHASE 1: Ingesting data from {csv_path.name}")
        print("=" * 60)

        with open(csv_path) as f:
            reader = csv.DictReader(f)
            artifact_count = 0

            for idx, row in enumerate(reader, start=1):
                # Skip empty rows
                if not row.get("symbol_sequence"):
                    continue

                # Extract and enrich data
                signal_strength = float(row["signal_strength"])
                category = self.categorize_signal(signal_strength)
                keywords = self.extract_keywords(row["notes"])
                warnings = self.extract_warnings(row["notes"])

                artifact_data = {
                    "symbol_sequence": row["symbol_sequence"],
                    "signal_strength": signal_strength,
                    "notes": row["notes"],
                    "category": category,
                    "keywords": keywords,
                    "warnings": warnings,
                }

                # Create trilayer artifact
                artifact_id = f"{idx:04d}"
                self.create_artifact_trilayer(artifact_id, artifact_data)

                # Store for context aggregation
                self.category_data[category].append({"artifact_id": artifact_id, **artifact_data})

                artifact_count += 1
                print(f"  ✓ Created artifact {artifact_id} [{category}]")

        print(f"\n📊 Created {artifact_count} trilayer artifacts")
        print(f"📂 Categories: {list(self.category_data.keys())}")

    def generate_context_layer(self) -> None:
        """
        Phase 2: RECURSIVE - Re-read artifacts and generate context layer.

        This is the MIDDLEWARE layer that aggregates metadata by category.
        """
        print("\n🔄 PHASE 2: Generating Context Layer (Semantic Middleware)")
        print("=" * 60)

        for category, artifacts in self.category_data.items():
            print(f"\n📋 Processing category: {category}")

            # Aggregate metadata
            all_keywords = []
            all_warnings = []
            artifact_ids = []
            signal_strengths = []

            for artifact in artifacts:
                all_keywords.extend(artifact["keywords"])
                all_warnings.extend(artifact["warnings"])
                artifact_ids.append(artifact["artifact_id"])
                signal_strengths.append(artifact["signal_strength"])

            # Remove duplicates and sort
            unique_keywords = sorted(set(all_keywords))
            unique_warnings = sorted(set(all_warnings))

            # Calculate statistics
            avg_signal = sum(signal_strengths) / len(signal_strengths)
            min_signal = min(signal_strengths)
            max_signal = max(signal_strengths)

            # 1. Context JSON - AI Metadata
            context_json = {
                "category": category,
                "artifact_count": len(artifacts),
                "search_hints": unique_keywords,
                "avoidance_protocols": unique_warnings,
                "access_frequency": {
                    "read_count": 0,  # Placeholder for future tracking
                    "last_accessed": None,
                },
                "statistics": {
                    "avg_signal_strength": round(avg_signal, 3),
                    "min_signal_strength": round(min_signal, 3),
                    "max_signal_strength": round(max_signal, 3),
                },
                "artifact_ids": artifact_ids,
            }

            json_path = self.context_path / f"{category}_meta.json"
            with open(json_path, "w") as f:
                json.dump(context_json, f, indent=2)
            print(f"  ✓ Generated {json_path.name}")

            # 2. Context MD - Human Narrative
            context_md = f"""# Context: {category.replace('_', ' ').title()}

## Category Overview
This context layer aggregates metadata for **{len(artifacts)} artifacts** in the `{category}` category.

## Signal Characteristics
- **Average Strength**: {avg_signal:.3f}
- **Range**: {min_signal:.3f} - {max_signal:.3f}

## Search Hints (for AI)
When searching in this category, focus on these keywords:
{chr(10).join(f'- `{kw}`' for kw in unique_keywords) if unique_keywords else '- No specific keywords'}

## Avoidance Protocols (for Human Review)
{''.join(f'⚠️  {warning}' + chr(10) for warning in unique_warnings) if unique_warnings else '✅ No warnings for this category'}

## Artifacts in This Category
{chr(10).join(f'- `artifact_{aid}` (signal: {signal_strengths[i]:.3f})' for i, aid in enumerate(artifact_ids))}

## Usage Notes
- **AI Agents**: Use `search_hints` from JSON metadata for optimized retrieval
- **Human Reviewers**: Check avoidance protocols before trusting patterns
- **Systems**: Navigate via YAML for structural references

---
**Last Updated**: 2025-11-23
**Source**: Recursive ingestion from artifacts
"""

            md_path = self.context_path / f"{category}_narrative.md"
            with open(md_path, "w") as f:
                f.write(context_md)
            print(f"  ✓ Generated {md_path.name}")

            # 3. Context YAML - Navigation Structure
            context_yaml = {
                "category": category,
                "artifact_count": len(artifacts),
                "artifacts": [
                    {
                        "id": aid,
                        "yaml_ref": f"artifacts/artifact_{aid}.yaml",
                        "json_ref": f"artifacts/artifact_{aid}.json",
                        "md_ref": f"artifacts/artifact_{aid}.md",
                    }
                    for aid in artifact_ids
                ],
            }

            yaml_path = self.context_path / f"{category}_nav.yaml"
            with open(yaml_path, "w") as f:
                yaml.dump(context_yaml, f, default_flow_style=False, sort_keys=False)
            print(f"  ✓ Generated {yaml_path.name}")

        print(f"\n✅ Context Layer complete: {len(self.category_data)} categories processed")


def main():
    """Main execution: Ingest CSV → Create Artifacts → Generate Context Layer"""

    # Configuration
    base_path = Path(__file__).parent
    csv_path = base_path / "data" / "mock_rosetta.csv"

    if not csv_path.exists():
        print(f"❌ ERROR: {csv_path} not found!")
        return

    print("🏛️  CHAMPOLLION DIAMOND ARCHITECTURE")
    print("Intelligent Ingestion with Recursive Context Layer")
    print("=" * 60)

    # Initialize ingestion engine
    engine = ChampollionIngestion(base_path)

    # Phase 1: Ingest CSV and create artifacts
    engine.ingest_csv(csv_path)

    # Phase 2: Generate context layer (recursive)
    engine.generate_context_layer()

    print("\n" + "=" * 60)
    print("🎯 INGESTION COMPLETE")
    print(f"📦 Artifacts: {engine.artifacts_path}")
    print(f"🧠 Context Layer: {engine.context_path}")
    print("\n✨ Ready for Master Index generation (run close_the_diamond.py)")


if __name__ == "__main__":
    main()
