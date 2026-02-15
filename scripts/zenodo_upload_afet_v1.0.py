#!/usr/bin/env python3
"""AFET v1.0 Zenodo Upload Script.

Packages the AFET v1.0 release bundle (manifest, DOI table, PDFs, code tarball)
and uploads it to Zenodo via the REST API.  Reads metadata from .zenodo.json.

Usage:
    # Dry-run (no upload, just package):
    python scripts/zenodo_upload_afet_v1.0.py --dry-run

    # Real upload (requires ZENODO_TOKEN):
    ZENODO_TOKEN=your_token python scripts/zenodo_upload_afet_v1.0.py

Environment variables:
    ZENODO_TOKEN   — Personal access token from zenodo.org (required for upload)
    ZENODO_SANDBOX — Set to "1" to use sandbox.zenodo.org instead of production
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
ZENODO_JSON = REPO_ROOT / ".zenodo.json"
OUTPUT_DIR = REPO_ROOT / "releases" / "vAFET-1.0" / "zenodo_package"

# Artifacts to include in the release ZIP/tarball
ARTIFACTS: list[tuple[str, Path]] = [
    # Manifest
    ("manifest/afet_release_manifest.md", REPO_ROOT / "releases/vAFET-1.0/afet_release_manifest.md"),
    ("manifest/afet_release_manifest.json", REPO_ROOT / "releases/vAFET-1.0/afet_release_manifest.json"),
    ("manifest/afet_release_manifest.yaml", REPO_ROOT / "releases/vAFET-1.0/afet_release_manifest.yaml"),
    # DOI table
    ("doi_table/doi_citation_table.md", REPO_ROOT / "docs/AFET/doi_citation_table.md"),
    # Paper
    ("paper/AFET_Universal_Framework_Paper_final.md", REPO_ROOT / "docs/AFET/AFET_Universal_Framework_Paper_final.md"),
    ("paper/Afet universal framework paper final.pdf", REPO_ROOT / "docs/AFET/Afet universal framework paper final.pdf"),
    # Preprint
    ("preprint/preprint_v12_consciousness.md", REPO_ROOT / "docs/AFET/preprint_v12_consciousness.md"),
    # Supplementary
    ("supplementary/PERPLEXITY_INTEGRATION_SUMMARY.md", REPO_ROOT / "docs/AFET/PERPLEXITY_INTEGRATION_SUMMARY.md"),
    ("supplementary/Perplexity integration summary final.pdf", REPO_ROOT / "docs/AFET/Perplexity integration summary final.pdf"),
    # Intake register
    ("intake/afet_intake_register.json", REPO_ROOT / "docs/AFET/afet_intake_register.json"),
    ("intake/afet_intake_register.yaml", REPO_ROOT / "docs/AFET/afet_intake_register.yaml"),
    # Zenodo metadata
    (".zenodo.json", ZENODO_JSON),
]

# ORCID placeholders — fill in before real upload
ORCID_PLACEHOLDERS = {
    "Römer, Johann Benjamin": "0000-0000-0000-0000",  # TODO: replace with real ORCID
}

ZENODO_API_PROD = "https://zenodo.org/api"
ZENODO_API_SANDBOX = "https://sandbox.zenodo.org/api"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest for a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_zenodo_metadata() -> dict[str, Any]:
    """Load and enrich .zenodo.json with ORCID placeholders."""
    with open(ZENODO_JSON, encoding="utf-8") as f:
        meta = json.load(f)

    # Inject ORCID placeholders into creators
    for creator in meta.get("creators", []):
        name = creator.get("name", "")
        if name in ORCID_PLACEHOLDERS and not creator.get("orcid"):
            creator["orcid"] = ORCID_PLACEHOLDERS[name]

    return meta


def build_code_tarball(dest_dir: Path) -> Path:
    """Create a reproducible source tarball of the repository code."""
    tarball_path = dest_dir / "afet-v1.0-source.tar.gz"

    code_dirs = ["src", "modules", "models", "analysis", "scripts", "utils"]
    code_files = ["live_afet_mirror.py", "setup.py", "pyproject.toml",
                  "requirements.txt", ".zenodo.json", "CITATION.cff", "LICENSE"]

    with tarfile.open(tarball_path, "w:gz") as tar:
        for d in code_dirs:
            full = REPO_ROOT / d
            if full.is_dir():
                tar.add(str(full), arcname=f"afet-v1.0/{d}")
        for f in code_files:
            full = REPO_ROOT / f
            if full.is_file():
                tar.add(str(full), arcname=f"afet-v1.0/{f}")

    return tarball_path


def package_release(output_dir: Path) -> Path:
    """Assemble the release package directory and return the final tarball path."""
    staging = output_dir / "staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)

    # Copy artifacts
    manifest_entries = []
    for arcname, src in ARTIFACTS:
        if not src.exists():
            print(f"  WARN: artifact missing, skipping: {src}")
            continue
        dest = staging / arcname
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        manifest_entries.append({
            "path": arcname,
            "sha256": sha256_file(src),
            "size_bytes": src.stat().st_size,
        })

    # Build code tarball
    code_tarball = build_code_tarball(staging)
    manifest_entries.append({
        "path": code_tarball.name,
        "sha256": sha256_file(code_tarball),
        "size_bytes": code_tarball.stat().st_size,
    })

    # Write package manifest
    pkg_manifest = {
        "package": "afet-v1.0-zenodo",
        "created": datetime.now(timezone.utc).isoformat(),
        "files": manifest_entries,
    }
    manifest_path = staging / "PACKAGE_MANIFEST.json"
    manifest_path.write_text(json.dumps(pkg_manifest, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")

    # Create final tarball
    final_tarball = output_dir / "afet-v1.0-zenodo.tar.gz"
    with tarfile.open(final_tarball, "w:gz") as tar:
        for item in staging.iterdir():
            tar.add(str(item), arcname=item.name)

    print(f"\nPackage created: {final_tarball}")
    print(f"  Files: {len(manifest_entries)}")
    print(f"  Size: {final_tarball.stat().st_size / 1024:.1f} KB")

    return final_tarball


def zenodo_upload(tarball: Path, metadata: dict[str, Any], *, dry_run: bool = False) -> str | None:
    """Upload package to Zenodo via REST API. Returns the assigned DOI or None."""
    token = os.environ.get("ZENODO_TOKEN", "")
    if not token and not dry_run:
        print("ERROR: ZENODO_TOKEN not set. Use --dry-run or export ZENODO_TOKEN.")
        sys.exit(1)

    use_sandbox = os.environ.get("ZENODO_SANDBOX", "0") == "1"
    base_url = ZENODO_API_SANDBOX if use_sandbox else ZENODO_API_PROD
    env_label = "SANDBOX" if use_sandbox else "PRODUCTION"

    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN — would upload to Zenodo ({env_label})")
        print(f"{'='*60}")
        print(f"  Endpoint: {base_url}/deposit/depositions")
        print(f"  File: {tarball.name} ({tarball.stat().st_size / 1024:.1f} KB)")
        print(f"  Title: {metadata.get('title', 'N/A')}")
        print(f"  Version: {metadata.get('version', 'N/A')}")
        print(f"  Creators: {json.dumps(metadata.get('creators', []), ensure_ascii=False)}")
        print(f"  Keywords: {', '.join(metadata.get('keywords', []))}")
        print(f"  License: {metadata.get('license', {}).get('id', 'N/A')}")
        print(f"\n  ORCID placeholders (fill before real upload):")
        for name, orcid in ORCID_PLACEHOLDERS.items():
            print(f"    {name}: {orcid}")
        print(f"\n  To upload for real:")
        print(f"    ZENODO_TOKEN=<token> python {__file__}")
        if not use_sandbox:
            print(f"    ZENODO_SANDBOX=1 ZENODO_TOKEN=<token> python {__file__}  # sandbox first")
        return "10.5281/zenodo.XXXXXXX (dry-run)"

    # --- Real upload path (requires `requests`) ---
    try:
        import requests
    except ImportError:
        print("ERROR: 'requests' package required for upload. Install with: pip install requests")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Create deposition
    print(f"\nCreating deposition on {env_label}...")
    dep_data = {"metadata": {
        "title": metadata["title"],
        "upload_type": metadata.get("upload_type", "publication"),
        "publication_type": metadata.get("publication_type", "workingpaper"),
        "description": metadata.get("description", ""),
        "creators": metadata.get("creators", []),
        "keywords": metadata.get("keywords", []),
        "version": metadata.get("version", "1.0"),
        "publication_date": metadata.get("publication_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "access_right": metadata.get("access_right", "open"),
        "license": metadata.get("license", {}).get("id", "other-open"),
        "notes": metadata.get("notes", ""),
        "related_identifiers": metadata.get("related_identifiers", []),
        "language": metadata.get("language", "eng"),
    }}

    resp = requests.post(f"{base_url}/deposit/depositions", json=dep_data, headers=headers)
    resp.raise_for_status()
    deposition = resp.json()
    dep_id = deposition["id"]
    bucket_url = deposition["links"]["bucket"]
    print(f"  Deposition created: {dep_id}")

    # Step 2: Upload file
    print(f"  Uploading {tarball.name}...")
    with open(tarball, "rb") as f:
        resp = requests.put(f"{bucket_url}/{tarball.name}", data=f, headers=headers)
        resp.raise_for_status()
    print("  Upload complete.")

    # Step 3: Publish
    print("  Publishing...")
    resp = requests.post(f"{base_url}/deposit/depositions/{dep_id}/actions/publish",
                         headers=headers)
    resp.raise_for_status()
    published = resp.json()
    doi = published.get("doi", "N/A")
    print(f"\n  DOI assigned: {doi}")
    print(f"  URL: https://doi.org/{doi}")
    return doi


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package and upload AFET v1.0 to Zenodo.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Package only, do not upload.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR,
                        help="Directory for the packaged release.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("AFET v1.0 Zenodo Upload")
    print("=" * 40)

    # Load metadata
    metadata = load_zenodo_metadata()
    print(f"Loaded metadata: {metadata['title']}")

    # Package
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tarball = package_release(args.output_dir)

    # Upload (or dry-run)
    doi = zenodo_upload(tarball, metadata, dry_run=args.dry_run)

    if doi:
        # Write DOI record
        doi_record = {
            "doi": doi,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "package": str(tarball.name),
            "sha256": sha256_file(tarball),
            "dry_run": args.dry_run,
        }
        doi_file = args.output_dir / "zenodo_doi_record.json"
        doi_file.write_text(json.dumps(doi_record, indent=2) + "\n", encoding="utf-8")
        print(f"\nDOI record saved: {doi_file}")

    print("\nDone.")


if __name__ == "__main__":
    main()
