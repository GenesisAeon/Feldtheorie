#!/usr/bin/env python3
"""
Sigillin Trilayer Parser & Validator

Parses, validates, and indexes Sigillin Selfmeta triplets (JSON/YAML/MD).
Creates an index of all selfmeta files and validates trilayer consistency.

Based on: releases/V6-Plans_etc/V6ToDorefresh.yaml:v6r-sigillin-parser
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


class SigillinParser:
    """Parser and validator for Sigillin Selfmeta triplets."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.triplets: list[dict[str, Any]] = []
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def find_sigil_files(self) -> list[Path]:
        """Find all *.sigil.json files recursively."""
        return sorted(self.root_path.rglob("*.sigil.json"))

    def load_json(self, path: Path) -> dict[str, Any] | None:
        """Load JSON file."""
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON parse error in {path}: {e}")
            return None
        except Exception as e:
            self.errors.append(f"Error reading {path}: {e}")
            return None

    def load_yaml(self, path: Path) -> dict[str, Any] | None:
        """Load YAML file."""
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parse error in {path}: {e}")
            return None
        except Exception as e:
            self.errors.append(f"Error reading {path}: {e}")
            return None

    def load_markdown(self, path: Path) -> str | None:
        """Load Markdown file."""
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.errors.append(f"Error reading {path}: {e}")
            return None

    def validate_triplet(self, json_path: Path) -> dict[str, Any] | None:
        """Validate that JSON/YAML/MD triplet exists and is consistent."""

        # Derive paths
        base_path = json_path.parent / json_path.stem.replace(".sigil", "")
        yaml_path = Path(str(base_path) + ".yaml")
        md_path = Path(str(base_path) + ".md")

        # Load files
        json_data = self.load_json(json_path)
        if json_data is None:
            return None

        yaml_data = None
        md_content = None

        # Check YAML
        if not yaml_path.exists():
            self.warnings.append(f"Missing YAML companion for {json_path}")
        else:
            yaml_data = self.load_yaml(yaml_path)

        # Check MD
        if not md_path.exists():
            self.warnings.append(f"Missing MD companion for {json_path}")
        else:
            md_content = self.load_markdown(md_path)

        # Validate core fields
        required_fields = ["sigil_id", "title", "version", "status"]
        for field in required_fields:
            if field not in json_data:
                self.errors.append(f"{json_path}: Missing required field '{field}'")

        # Cross-validate JSON ↔ YAML
        if yaml_data:
            for field in required_fields:
                if field in json_data and field in yaml_data:
                    if json_data[field] != yaml_data[field]:
                        self.errors.append(
                            f"{json_path}: Field '{field}' mismatch between JSON and YAML"
                        )

        # Validate MD contains sigil_id
        if md_content and "sigil_id" in json_data:
            sigil_id = json_data["sigil_id"]
            if sigil_id not in md_content:
                self.warnings.append(f"{md_path}: Sigil ID '{sigil_id}' not found in markdown")

        return {
            "sigil_id": json_data.get("sigil_id", "unknown"),
            "title": json_data.get("title", "untitled"),
            "version": json_data.get("version", "unknown"),
            "status": json_data.get("status", "unknown"),
            "json_path": str(json_path.relative_to(self.root_path)),
            "yaml_path": str(yaml_path.relative_to(self.root_path)) if yaml_path.exists() else None,
            "md_path": str(md_path.relative_to(self.root_path)) if md_path.exists() else None,
            "field_type": json_data.get("field_type", "unknown"),
            "beta_window": json_data.get("resonance_pattern", {}).get("beta_window"),
            "crep_index": json_data.get("resonance_pattern", {}).get("crep_index"),
        }

    def parse_all(self) -> list[dict[str, Any]]:
        """Parse and validate all Sigillin triplets."""
        sigil_files = self.find_sigil_files()

        if not sigil_files:
            self.warnings.append("No *.sigil.json files found")
            return []

        for json_path in sigil_files:
            triplet = self.validate_triplet(json_path)
            if triplet:
                self.triplets.append(triplet)

        return self.triplets

    def generate_index(self, output_path: Path):
        """Generate index file of all Sigillin triplets."""
        index_data = {
            "generated_at": "2025-12-04",
            "total_triplets": len(self.triplets),
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "triplets": self.triplets,
            "errors": self.errors,
            "warnings": self.warnings,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Index written to {output_path}")

    def print_report(self):
        """Print validation report."""
        print("\n" + "=" * 60)
        print("📋 SIGILLIN TRILAYER VALIDATION REPORT")
        print("=" * 60)

        print(f"\n✅ Triplets found: {len(self.triplets)}")

        if self.triplets:
            print("\nSigillin Registry:")
            for t in self.triplets:
                status_icon = {
                    "active": "🟢",
                    "pending": "🟡",
                    "completed": "✅",
                    "deprecated": "🔴",
                }.get(t["status"], "⚪")

                print(
                    f"  {status_icon} {t['sigil_id']:30s} | "
                    f"v{t['version']:6s} | "
                    f"{t['title'][:40]}"
                )

                if t.get("crep_index"):
                    print(f"      CREP: {t['crep_index']:.2f}", end="")
                if t.get("beta_window"):
                    print(f" | β-Window: {t['beta_window']}", end="")
                print()

        if self.warnings:
            print(f"\n⚠️  Warnings: {len(self.warnings)}")
            for w in self.warnings[:10]:  # Show first 10
                print(f"  - {w}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")

        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for e in self.errors[:10]:  # Show first 10
                print(f"  - {e}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        else:
            print("\n✅ No critical errors found")

        print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Parse and validate Sigillin Selfmeta triplets")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Root directory to search (default: current directory)",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=Path("docs/meta/sigillin_index.json"),
        help="Output path for index file",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code if any errors found",
    )

    args = parser.parse_args()

    print(f"🔍 Searching for Sigillin triplets in {args.root}")

    sigillin = SigillinParser(args.root)
    sigillin.parse_all()
    sigillin.print_report()

    if sigillin.triplets:
        sigillin.generate_index(args.index)
    else:
        print("⚠️  No triplets found, skipping index generation")

    # Exit with error if strict mode and errors found
    if args.strict and sigillin.errors:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
