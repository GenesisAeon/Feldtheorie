#!/usr/bin/env python3
"""AFET v1.0 Post-Release Checklist.

Validates release artifacts and prints a checklist of manual steps
required after the automated release pipeline completes.

Usage:
    python scripts/post_release_checklist.py
    python scripts/post_release_checklist.py --verify  # Check artifact existence
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Artifacts that should exist after a successful release
REQUIRED_ARTIFACTS = [
    ("Release manifest (JSON)", "releases/vAFET-1.0/afet_release_manifest.json"),
    ("Release manifest (YAML)", "releases/vAFET-1.0/afet_release_manifest.yaml"),
    ("Release manifest (MD)", "releases/vAFET-1.0/afet_release_manifest.md"),
    ("GitHub release body", "releases/vAFET-1.0/GITHUB_RELEASE_BODY.md"),
    ("DOI citation table", "docs/AFET/doi_citation_table.md"),
    ("Paper (MD)", "docs/AFET/AFET_Universal_Framework_Paper_final.md"),
    ("Paper (PDF)", "docs/AFET/Afet universal framework paper final.pdf"),
    ("v12 preprint", "docs/AFET/preprint_v12_consciousness.md"),
    ("Zenodo metadata", ".zenodo.json"),
    ("Citation file", "CITATION.cff"),
    ("Self-snapshot", "docs/self_snapshot_v1.0_2026-02-15.html"),
]

MANUAL_STEPS = [
    {
        "step": "Register or update ORCID",
        "detail": (
            "Go to https://orcid.org and add the new Zenodo DOI to your works.\n"
            "   Then update .zenodo.json creators[0].orcid with your ORCID ID."
        ),
    },
    {
        "step": "Generate PDF via Pandoc",
        "detail": (
            "Run: pandoc docs/AFET/AFET_Universal_Framework_Paper_final.md \\\n"
            "       -o docs/AFET/AFET_v1.0_paper.pdf \\\n"
            "       --citeproc --bibliography=paper.bib \\\n"
            "       --pdf-engine=xelatex"
        ),
    },
    {
        "step": "Verify Zenodo DOI resolves",
        "detail": "Visit https://doi.org/<your-new-doi> and confirm it loads.",
    },
    {
        "step": "Update CITATION.cff with final DOI",
        "detail": (
            "Replace the placeholder DOI in CITATION.cff with the\n"
            "   DOI assigned by Zenodo after upload."
        ),
    },
    {
        "step": "Configure GitHub 'release' environment",
        "detail": (
            "In GitHub Settings > Environments, create a 'release' environment\n"
            "   with required reviewers. Add ZENODO_TOKEN as an environment secret."
        ),
    },
    {
        "step": "Announce release",
        "detail": (
            "Post on X/community channels. Reference DOI, GitHub release URL,\n"
            "   and key validation metrics (78 datasets, r^2=0.88, DAIC>=10)."
        ),
    },
]


def verify_artifacts() -> list[tuple[str, str, bool]]:
    """Check existence of required release artifacts."""
    results = []
    for label, rel_path in REQUIRED_ARTIFACTS:
        exists = (REPO_ROOT / rel_path).exists()
        results.append((label, rel_path, exists))
    return results


def check_zenodo_metadata() -> list[str]:
    """Validate .zenodo.json for common issues."""
    issues = []
    zpath = REPO_ROOT / ".zenodo.json"
    if not zpath.exists():
        issues.append(".zenodo.json not found")
        return issues

    with open(zpath) as f:
        meta = json.load(f)

    creators = meta.get("creators", [])
    if not creators:
        issues.append("No creators defined in .zenodo.json")
    elif not creators[0].get("orcid"):
        issues.append("ORCID is empty for primary creator — fill before Zenodo upload")

    if meta.get("license", {}).get("id") == "other-open":
        issues.append("License is 'other-open' — update to 'GPL-3.0-only' or specific ID")

    if not meta.get("publication_date"):
        issues.append("publication_date is missing")

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="AFET v1.0 post-release checklist")
    parser.add_argument("--verify", action="store_true", help="Verify artifact existence")
    args = parser.parse_args()

    print("=" * 60)
    print("  AFET v1.0 Post-Release Checklist")
    print("=" * 60)

    if args.verify:
        print("\n--- Artifact Verification ---\n")
        results = verify_artifacts()
        all_ok = True
        for label, path, exists in results:
            status = "OK" if exists else "MISSING"
            if not exists:
                all_ok = False
            print(f"  [{status:7s}] {label}")
            if not exists:
                print(f"           -> {path}")

        print()
        issues = check_zenodo_metadata()
        if issues:
            print("--- Zenodo Metadata Issues ---\n")
            for issue in issues:
                print(f"  [!] {issue}")
            print()

        if not all_ok or issues:
            print("Some checks failed. Address above issues before publishing.\n")
            sys.exit(1)
        else:
            print("All artifacts present. Metadata looks good.\n")

    print("--- Manual Steps Required ---\n")
    for i, item in enumerate(MANUAL_STEPS, 1):
        print(f"  {i}. {item['step']}")
        print(f"   {item['detail']}")
        print()

    print("=" * 60)


if __name__ == "__main__":
    main()
