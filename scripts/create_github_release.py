#!/usr/bin/env python3
"""Create a GitHub Release for AFET v1.0.

Uses the GitHub CLI (`gh`) to create a tagged release with the release notes
from GITHUB_RELEASE_BODY.md and attaches the release asset (afet-v1.0.zip).

Usage:
    # Dry-run (prints commands, does not execute):
    python scripts/create_github_release.py --dry-run

    # Real release (requires gh auth):
    python scripts/create_github_release.py

Prerequisites:
    - `gh` CLI installed and authenticated
    - Working git repository with push access
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
TAG = "v1.0"
RELEASE_TITLE = "AFET v1.0 — General Field Entropy Theory: World Release"

RELEASE_BODY_PATH = REPO_ROOT / "releases" / "vAFET-1.0" / "GITHUB_RELEASE_BODY.md"
ASSET_DIR = REPO_ROOT / "releases" / "vAFET-1.0" / "github_release"

# Files to include in the release ZIP
RELEASE_FILES: list[tuple[str, Path]] = [
    # Manifests
    ("manifest/afet_release_manifest.md", REPO_ROOT / "releases/vAFET-1.0/afet_release_manifest.md"),
    ("manifest/afet_release_manifest.json", REPO_ROOT / "releases/vAFET-1.0/afet_release_manifest.json"),
    ("manifest/afet_release_manifest.yaml", REPO_ROOT / "releases/vAFET-1.0/afet_release_manifest.yaml"),
    # Paper + Preprint
    ("paper/AFET_Universal_Framework_Paper_final.md", REPO_ROOT / "docs/AFET/AFET_Universal_Framework_Paper_final.md"),
    ("paper/Afet universal framework paper final.pdf", REPO_ROOT / "docs/AFET/Afet universal framework paper final.pdf"),
    ("preprint/preprint_v12_consciousness.md", REPO_ROOT / "docs/AFET/preprint_v12_consciousness.md"),
    # DOI table
    ("doi_table/doi_citation_table.md", REPO_ROOT / "docs/AFET/doi_citation_table.md"),
    # Supplementary
    ("supplementary/PERPLEXITY_INTEGRATION_SUMMARY.md", REPO_ROOT / "docs/AFET/PERPLEXITY_INTEGRATION_SUMMARY.md"),
    # Intake register
    ("intake/afet_intake_register.json", REPO_ROOT / "docs/AFET/afet_intake_register.json"),
    ("intake/afet_intake_register.yaml", REPO_ROOT / "docs/AFET/afet_intake_register.yaml"),
    # Metadata
    (".zenodo.json", REPO_ROOT / ".zenodo.json"),
    ("CITATION.cff", REPO_ROOT / "CITATION.cff"),
]

# Badge markdown for the release body
BADGES = """\
![GitHub Downloads](https://img.shields.io/github/downloads/GenesisAeon/Feldtheorie/v1.0/total?style=flat-square&label=Downloads)
![GitHub Views](https://img.shields.io/github/watchers/GenesisAeon/Feldtheorie?style=flat-square&label=Watchers)
![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.XXXXXXX-blue?style=flat-square)
![License Code](https://img.shields.io/badge/Code-GPL--3.0-green?style=flat-square)
![License Content](https://img.shields.io/badge/Content-CC%20BY--NC%204.0-orange?style=flat-square)
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(cmd: list[str], *, dry_run: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command, optionally in dry-run mode."""
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(cmd)}")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True, check=check, cwd=str(REPO_ROOT))


def build_release_zip() -> Path:
    """Create afet-v1.0.zip containing all release artifacts."""
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = ASSET_DIR / "afet-v1.0.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        included = 0
        for arcname, src in RELEASE_FILES:
            if not src.exists():
                print(f"  WARN: missing {src}, skipping")
                continue
            zf.write(src, f"afet-v1.0/{arcname}")
            included += 1
        print(f"  Packaged {included} files into {zip_path.name}")

    print(f"  ZIP size: {zip_path.stat().st_size / 1024:.1f} KB")
    return zip_path


def build_release_body() -> str:
    """Construct the full release body with badges prepended."""
    if RELEASE_BODY_PATH.exists():
        body = RELEASE_BODY_PATH.read_text(encoding="utf-8")
    else:
        print(f"  WARN: {RELEASE_BODY_PATH} not found, using minimal body")
        body = "## AFET v1.0\n\nSee repository for details.\n"

    return f"{BADGES}\n---\n\n{body}"


def create_tag(*, dry_run: bool = False) -> None:
    """Create and push the release tag."""
    # Check if tag exists
    result = run(["git", "tag", "-l", TAG], dry_run=False)
    if TAG in result.stdout.strip().split("\n"):
        print(f"  Tag {TAG} already exists, skipping creation")
        return

    run(["git", "tag", "-a", TAG, "-m", f"AFET {TAG} — World Release 2026-02-15"], dry_run=dry_run)
    run(["git", "push", "origin", TAG], dry_run=dry_run)


def create_release(zip_path: Path, body: str, *, dry_run: bool = False) -> str | None:
    """Create the GitHub release using gh CLI."""
    # Write body to temp file for gh
    body_file = ASSET_DIR / "RELEASE_BODY_FINAL.md"
    body_file.write_text(body, encoding="utf-8")

    cmd = [
        "gh", "release", "create", TAG,
        "--title", RELEASE_TITLE,
        "--notes-file", str(body_file),
        str(zip_path),
    ]

    result = run(cmd, dry_run=dry_run, check=not dry_run)

    if dry_run:
        print(f"\n  Release URL would be: https://github.com/GenesisAeon/Feldtheorie/releases/tag/{TAG}")
        return f"https://github.com/GenesisAeon/Feldtheorie/releases/tag/{TAG} (dry-run)"

    url = result.stdout.strip()
    print(f"\n  Release created: {url}")
    return url


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create GitHub Release for AFET v1.0.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print commands without executing.")
    parser.add_argument("--skip-tag", action="store_true",
                        help="Skip tag creation (tag already exists).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("AFET v1.0 GitHub Release")
    print("=" * 40)

    # Step 1: Build ZIP
    print("\n1. Building release asset...")
    zip_path = build_release_zip()

    # Step 2: Build release body
    print("\n2. Building release notes...")
    body = build_release_body()
    print(f"  Body length: {len(body)} chars")

    # Step 3: Create tag
    if not args.skip_tag:
        print(f"\n3. Creating tag {TAG}...")
        create_tag(dry_run=args.dry_run)
    else:
        print(f"\n3. Skipping tag creation (--skip-tag)")

    # Step 4: Create release
    print("\n4. Creating GitHub release...")
    url = create_release(zip_path, body, dry_run=args.dry_run)

    # Step 5: Summary
    summary = {
        "tag": TAG,
        "title": RELEASE_TITLE,
        "asset": str(zip_path.name),
        "url": url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
    }
    summary_file = ASSET_DIR / "release_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"\n{'='*40}")
    print(f"Summary saved: {summary_file}")
    if url:
        print(f"Release: {url}")
    print("Done.")


if __name__ == "__main__":
    main()
