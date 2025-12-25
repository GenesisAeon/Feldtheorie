#!/usr/bin/env python3
"""
Audit all datasets in data/ for metadata completeness.

Checks:
- Existence of .metadata.json files
- Required fields: source, license, doi_or_url
- Optional but recommended fields: variables, fitted_parameters
- Data file existence

Usage:
    python scripts/audit_data_sources.py
    python scripts/audit_data_sources.py --fix  # Create missing templates
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Required metadata fields
REQUIRED_FIELDS = ["name", "source", "license"]
RECOMMENDED_FIELDS = ["doi", "url", "variables", "description"]
OPTIONAL_FIELDS = ["fitted_parameters", "citation", "notes"]

# Color codes for terminal output
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"


class DatasetAudit:
    """Audit datasets for metadata completeness."""

    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.issues: List[Dict] = []
        self.stats = {
            "total_datasets": 0,
            "with_metadata": 0,
            "missing_metadata": 0,
            "incomplete_metadata": 0,
            "complete_datasets": 0,
        }

    def find_datasets(self) -> List[Path]:
        """Find all CSV files in data directory."""
        csv_files = []
        for csv_path in self.data_dir.rglob("*.csv"):
            # Skip derived/aggregated files
            if "derived" not in csv_path.parts and "beta_estimates" not in csv_path.name:
                csv_files.append(csv_path)
        return sorted(csv_files)

    def check_metadata_exists(self, csv_path: Path) -> Optional[Path]:
        """Check if .metadata.json exists for CSV file."""
        metadata_path = csv_path.with_suffix(".metadata.json")
        return metadata_path if metadata_path.exists() else None

    def validate_metadata(self, metadata_path: Path) -> Dict:
        """Validate metadata file structure."""
        issues = []

        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "issues": [f"Invalid JSON: {e}"],
                "metadata": None,
            }
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Error reading file: {e}"],
                "metadata": None,
            }

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in metadata:
                issues.append(f"Missing required field: {field}")

        # Check for DOI or URL
        has_doi = "doi" in metadata and metadata["doi"]
        has_url = "url" in metadata and metadata["url"]
        if not (has_doi or has_url):
            issues.append("Missing both 'doi' and 'url' (at least one required)")

        # Check recommended fields
        missing_recommended = [
            field for field in RECOMMENDED_FIELDS if field not in metadata
        ]
        if missing_recommended:
            issues.append(f"Missing recommended fields: {', '.join(missing_recommended)}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "metadata": metadata,
        }

    def create_metadata_template(self, csv_path: Path) -> Dict:
        """Create metadata template for a dataset."""
        dataset_name = csv_path.stem.replace("_", " ").title()

        template = {
            "name": dataset_name,
            "source": "TODO: Add source (e.g., 'Wei et al. (2022)')",
            "license": "TODO: Add license (e.g., 'CC BY 4.0', 'Public Domain')",
            "doi": "TODO: Add DOI if available (e.g., '10.48550/arXiv.2206.07682')",
            "url": "TODO: Add URL if no DOI",
            "description": f"TODO: Describe {dataset_name} dataset",
            "variables": {
                "R": "TODO: Describe control parameter",
                "sigma": "TODO: Describe response variable",
            },
            "domain": "TODO: information | biological | climate | geophysical | neurodegeneration",
            "citation": "TODO: Full citation",
            "notes": "TODO: Any additional notes",
        }

        return template

    def audit_dataset(self, csv_path: Path) -> Dict:
        """Audit a single dataset."""
        result = {
            "path": str(csv_path),
            "metadata_exists": False,
            "metadata_valid": False,
            "issues": [],
        }

        # Check metadata file exists
        metadata_path = self.check_metadata_exists(csv_path)
        if not metadata_path:
            result["issues"].append("No .metadata.json file found")
            self.stats["missing_metadata"] += 1
            return result

        result["metadata_exists"] = True
        result["metadata_path"] = str(metadata_path)

        # Validate metadata
        validation = self.validate_metadata(metadata_path)
        result["metadata_valid"] = validation["valid"]
        result["issues"].extend(validation["issues"])

        if not validation["valid"]:
            self.stats["incomplete_metadata"] += 1
        else:
            self.stats["complete_datasets"] += 1

        self.stats["with_metadata"] += 1
        return result

    def run_audit(self) -> List[Dict]:
        """Run full audit on all datasets."""
        print(f"{BLUE}🔍 Auditing datasets in {self.data_dir}...{RESET}\n")

        datasets = self.find_datasets()
        self.stats["total_datasets"] = len(datasets)

        results = []
        for csv_path in datasets:
            result = self.audit_dataset(csv_path)
            results.append(result)

        return results

    def print_results(self, results: List[Dict]):
        """Print audit results in a formatted way."""
        print(f"\n{BLUE}{'=' * 80}{RESET}")
        print(f"{BLUE}📊 AUDIT RESULTS{RESET}")
        print(f"{BLUE}{'=' * 80}{RESET}\n")

        # Summary statistics
        print(f"{GREEN}✅ Complete datasets:{RESET} {self.stats['complete_datasets']}")
        print(f"{YELLOW}⚠️  With metadata (incomplete):{RESET} {self.stats['incomplete_metadata']}")
        print(f"{RED}❌ Missing metadata:{RESET} {self.stats['missing_metadata']}")
        print(f"{BLUE}📁 Total datasets:{RESET} {self.stats['total_datasets']}\n")

        # Coverage percentage
        if self.stats["total_datasets"] > 0:
            coverage = (
                self.stats["complete_datasets"] / self.stats["total_datasets"] * 100
            )
            print(f"{BLUE}Coverage:{RESET} {coverage:.1f}% complete\n")

        # Detailed issues
        print(f"{BLUE}{'=' * 80}{RESET}")
        print(f"{BLUE}📋 DETAILED ISSUES{RESET}")
        print(f"{BLUE}{'=' * 80}{RESET}\n")

        for result in results:
            if not result.get("metadata_valid", False):
                symbol = RED + "❌" if not result["metadata_exists"] else YELLOW + "⚠️ "
                print(f"{symbol} {result['path']}{RESET}")

                for issue in result["issues"]:
                    print(f"   • {issue}")
                print()

    def generate_fix_script(self, results: List[Dict], output_path: Path):
        """Generate a script to create missing metadata files."""
        missing = [r for r in results if not r["metadata_exists"]]

        if not missing:
            print(f"{GREEN}✅ No missing metadata files!{RESET}")
            return

        with open(output_path, "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write('"""Auto-generated script to create missing metadata templates."""\n\n')
            f.write("import json\nfrom pathlib import Path\n\n")

            for result in missing:
                csv_path = Path(result["path"])
                metadata_path = csv_path.with_suffix(".metadata.json")
                template = self.create_metadata_template(csv_path)

                f.write(f"# {csv_path}\n")
                f.write(f"metadata = {json.dumps(template, indent=2)}\n")
                f.write(f"Path('{metadata_path}').write_text(json.dumps(metadata, indent=2))\n")
                f.write(f'print("Created: {metadata_path}")\n\n')

        print(f"{GREEN}✅ Fix script generated: {output_path}{RESET}")
        print(f"   Run with: python {output_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Audit dataset metadata")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Data directory to audit",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Generate fix script for missing metadata",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("scripts/fix_metadata.py"),
        help="Output path for fix script",
    )
    args = parser.parse_args()

    # Run audit
    auditor = DatasetAudit(data_dir=args.data_dir)
    results = auditor.run_audit()
    auditor.print_results(results)

    # Generate fix script if requested
    if args.fix:
        auditor.generate_fix_script(results, args.output)

    # Exit code based on completeness
    if auditor.stats["missing_metadata"] > 0:
        print(f"\n{YELLOW}⚠️  Some datasets are missing metadata{RESET}")
        sys.exit(1)
    elif auditor.stats["incomplete_metadata"] > 0:
        print(f"\n{YELLOW}⚠️  Some metadata files are incomplete{RESET}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}✅ All datasets have complete metadata!{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
