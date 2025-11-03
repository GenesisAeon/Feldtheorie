#!/usr/bin/env python3
"""Release readiness checks for the Universal Threshold Field Model."""

import json
import subprocess
from pathlib import Path
from statistics import mean
from typing import List

ROOT = Path(__file__).resolve().parent


def check_file_contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False


def gather_beta_values(results_dir: Path) -> List[float]:
    beta_values: List[float] = []
    for json_file in results_dir.glob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        value = None
        if isinstance(data, dict):
            if "beta" in data:
                beta_entry = data["beta"]
                if isinstance(beta_entry, dict) and "value" in beta_entry:
                    value = beta_entry.get("value")
                elif isinstance(beta_entry, (int, float)):
                    value = beta_entry
            elif "beta_values" in data and isinstance(data["beta_values"], list):
                numeric = [item for item in data["beta_values"] if isinstance(item, (int, float))]
                if numeric:
                    value = mean(numeric)
        if isinstance(value, (int, float)):
            beta_values.append(float(value))
    return beta_values


def git_tag_exists(tag_name: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "tag", "--list", tag_name],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    return tag_name in result.stdout.splitlines()


def main() -> None:
    checks = {
        "Manuscript PDF exists": (ROOT / "paper" / "manuscript_v1.0.pdf").exists(),
        "DOI noted in README": check_file_contains(ROOT / "README.md", "10.5281/zenodo.17472834"),
        "DOI noted in CITATION.cff": check_file_contains(ROOT / "CITATION.cff", "10.5281/zenodo.17472834"),
        "DOI noted in manuscript": check_file_contains(ROOT / "paper" / "manuscript_v1.0.tex", "10.5281/zenodo.17472834"),
        "Git tag v1.0.1 present": git_tag_exists("v1.0.1"),
    }

    results_dir = ROOT / "analysis" / "results"
    if results_dir.exists():
        beta_values = gather_beta_values(results_dir)
        if beta_values:
            mean_beta = mean(beta_values)
            checks["β mean within [3.6, 4.8]"] = 3.6 <= mean_beta <= 4.8
        else:
            checks["β mean within [3.6, 4.8]"] = False
    else:
        checks["β mean within [3.6, 4.8]"] = False

    print("🎯 UTAC v1.0.1 Release Checklist\n")
    all_passed = True
    for label, passed in checks.items():
        icon = "✅" if passed else "❌"
        print(f"{icon} {label}")
        all_passed = all_passed and passed

    if all_passed:
        print("\n🎉 ALL CHECKS PASSED! Ready for release!")
    else:
        print("\n⚠️  Some checks failed. Review the items above before publishing.")


if __name__ == "__main__":
    main()
