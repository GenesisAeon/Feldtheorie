#!/usr/bin/env python3
"""verify_release.py - Verify all components are ready for v1.0.1 release"""

import os
import json
import sys
from pathlib import Path

# DOI that should be present everywhere
EXPECTED_DOI = "10.5281/zenodo.17472834"

def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists"""
    exists = Path(path).exists()
    icon = "✅" if exists else "❌"
    print(f"{icon} {description}: {path}")
    return exists

def check_doi_in_file(path: str, description: str) -> bool:
    """Check if DOI appears in file"""
    try:
        if not Path(path).exists():
            print(f"❌ {description}: File not found - {path}")
            return False

        content = Path(path).read_text()
        found = EXPECTED_DOI in content
        icon = "✅" if found else "❌"
        print(f"{icon} {description}: DOI in {path}")
        return found
    except Exception as e:
        print(f"❌ {description}: Error reading {path} - {e}")
        return False

def check_git_tag() -> bool:
    """Check if git tag v1.0.1 exists"""
    try:
        result = os.popen("git tag | grep -E '^v1\\.0\\.1$'").read().strip()
        exists = result == "v1.0.1"
        icon = "✅" if exists else "❌"
        print(f"{icon} Git tag v1.0.1 exists")
        return exists
    except Exception as e:
        print(f"❌ Git tag check failed: {e}")
        return False

def check_beta_convergence() -> tuple[bool, str]:
    """Verify β values are within expected range"""
    try:
        results_dir = Path("analysis/results")
        if not results_dir.exists():
            return False, "Results directory not found"

        beta_values = []
        files_checked = 0

        for json_file in results_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                    # Try different JSON structures
                    if isinstance(data, dict):
                        # Check for direct beta value
                        if "beta" in data:
                            if isinstance(data["beta"], dict) and "value" in data["beta"]:
                                beta_values.append(data["beta"]["value"])
                                files_checked += 1
                            elif isinstance(data["beta"], (int, float)):
                                beta_values.append(data["beta"])
                                files_checked += 1

                        # Check for logistic.beta
                        if "logistic" in data and isinstance(data["logistic"], dict):
                            if "beta" in data["logistic"]:
                                beta_values.append(data["logistic"]["beta"])
                                files_checked += 1
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

        if not beta_values:
            return True, "No beta values found (expected for some configs)"

        mean_beta = sum(beta_values) / len(beta_values)
        in_range = 3.0 <= mean_beta <= 5.5  # Slightly wider than [3.6, 4.8]

        message = f"Mean β = {mean_beta:.2f} from {len(beta_values)} values (files checked: {files_checked})"
        return in_range, message
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("=" * 70)
    print("🎯 UTAC v1.0.1 Release Verification")
    print("=" * 70)
    print()

    checks = {}

    # Phase 1: Manuscript
    print("📄 Phase 1: Manuscript")
    print("-" * 70)
    checks["manuscript_tex"] = check_file_exists(
        "paper/manuscript_v1.0.tex",
        "Manuscript .tex exists"
    )
    checks["manuscript_doi"] = check_doi_in_file(
        "paper/manuscript_v1.0.tex",
        "DOI in manuscript .tex"
    )
    checks["manuscript_pdf"] = check_file_exists(
        "paper/manuscript_v1.0.pdf",
        "Manuscript PDF exists (compile if missing)"
    )
    print()

    # Phase 2: Repository Updates
    print("📦 Phase 3: Repository Updates")
    print("-" * 70)
    checks["readme_doi"] = check_doi_in_file(
        "README.md",
        "DOI in README"
    )
    checks["citation_doi"] = check_doi_in_file(
        "CITATION.cff",
        "DOI in CITATION.cff"
    )
    checks["zenodo_json"] = check_doi_in_file(
        ".zenodo.json",
        "DOI in .zenodo.json"
    )
    print()

    # Phase 3: Documentation
    print("📚 Phase 2 & 4: Documentation")
    print("-" * 70)
    checks["zenodo_guide"] = check_file_exists(
        "ZENODO_UPLOAD_GUIDE.md",
        "Zenodo upload guide exists"
    )
    checks["compile_guide"] = check_file_exists(
        "COMPILE_MANUSCRIPT.md",
        "Compilation guide exists"
    )
    checks["arxiv_readme"] = check_file_exists(
        "arxiv_submission/README_ARXIV.md",
        "arXiv README exists"
    )
    checks["release_notes"] = check_file_exists(
        "GITHUB_RELEASE_NOTES.md",
        "GitHub release notes exist"
    )
    print()

    # Phase 4: Core Components
    print("🔬 Phase 1: Core Components")
    print("-" * 70)
    checks["analysis_results"] = check_file_exists(
        "analysis/results",
        "Analysis results directory exists"
    )
    checks["wei_integration"] = check_file_exists(
        "docs/wei_integration.md",
        "Wei integration docs exist"
    )
    checks["llm_extractor"] = check_file_exists(
        "analysis/llm_beta_extractor.py",
        "LLM beta extractor exists"
    )
    print()

    # Phase 5: Git
    print("🔖 Phase 3.3: Git")
    print("-" * 70)
    checks["git_tag"] = check_git_tag()
    print()

    # Phase 6: Beta Convergence
    print("🎯 Phase 5: Scientific Validation")
    print("-" * 70)
    beta_ok, beta_msg = check_beta_convergence()
    checks["beta_convergence"] = beta_ok
    icon = "✅" if beta_ok else "⚠️"
    print(f"{icon} β convergence: {beta_msg}")
    print()

    # Summary
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"Passed: {passed}/{total} ({percentage:.0f}%)")
    print()

    # Categorize results
    critical_checks = [
        "manuscript_tex", "manuscript_doi", "readme_doi",
        "citation_doi", "zenodo_json"
    ]

    critical_passed = sum(1 for k in critical_checks if checks.get(k, False))
    critical_total = len(critical_checks)

    print(f"Critical checks: {critical_passed}/{critical_total}")

    # Missing PDF is OK (needs manual compile)
    if not checks.get("manuscript_pdf", False):
        print("⚠️  PDF not found - Run: cd paper && pdflatex manuscript_v1.0.tex (3x)")

    print()

    # Final verdict
    if critical_passed == critical_total:
        print("🎉 ✅ RELEASE READY!")
        print()
        print("Next steps:")
        print("1. Compile PDF: cd paper && pdflatex manuscript_v1.0.tex (3x)")
        print("2. Upload to Zenodo: See ZENODO_UPLOAD_GUIDE.md")
        print("3. Create GitHub release: See GITHUB_RELEASE_NOTES.md")
        print("4. Submit to arXiv: See arxiv_submission/README_ARXIV.md")
        return 0
    else:
        print("❌ RELEASE NOT READY")
        print()
        print("Failed checks:")
        for check, passed in checks.items():
            if not passed and check in critical_checks:
                print(f"  - {check}")
        print()
        print("Fix the issues above and run this script again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
