#!/usr/bin/env python3
"""
Zenodo Release Artifact Preparation Script

This script prepares the Feldtheorie V5.0.0 repository for Zenodo upload by:
1. Creating a clean ZIP archive of the entire repository
2. Excluding development artifacts (.git/, venv/, __pycache__, etc.)
3. Generating a MANIFEST.txt listing all included files
4. Producing a reproducibility-ready artifact

Usage:
    python prepare_upload.py [--output OUTPUT_DIR] [--profile {full,slim}]

Output:
    - Feldtheorie_v5.0.0_Source.zip (Repository snapshot)
    - MANIFEST.txt (File listing with timestamps)
    - UPLOAD_CHECKLIST.md (Instructions for Zenodo upload)

Author: Genesis Aeon (UTAC Framework)
Version: 5.0.0
License: MIT
"""

import argparse
import hashlib
import os
import zipfile
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

VERSION = "5.0.0"
REPO_NAME = "Feldtheorie"
OUTPUT_ZIP_NAME = f"{REPO_NAME}_v{VERSION}_Source.zip"

# Directories and patterns to EXCLUDE from the ZIP
EXCLUSIONS = {
    # Version control
    ".git",
    ".github/workflows",  # Exclude workflows but keep other .github content
    ".gitignore",
    ".gitattributes",
    # Python artifacts
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    "pip-log.txt",
    "pip-delete-this-directory.txt",
    ".pytest_cache",
    ".coverage",
    "htmlcov",
    # Virtual environments
    "venv",
    "env",
    "ENV",
    ".venv",
    # IDE and editor files
    ".vscode",
    ".idea",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    # Temporary and cache files
    "tmp",
    "temp",
    ".cache",
    "*.tmp",
    # Large binary files (optional, adjust as needed)
    "*.mp4",
    "*.avi",
    "*.mov",
    # Build artifacts
    "build",
    "dist",
    "*.egg-info",
    # THIS RELEASE FOLDER (to avoid recursion)
    "releases/v5.0.0_Zenodo_Ready",
}

# Additional exclusions for slimmed-down release bundles. These focus on
# reproducibility-critical assets while omitting historical or exploratory
# material that bloats the archive size.
SLIM_EXCLUSIONS = {
    "archive",
    "output",
    "results",
    "seed",
    "notebooks",
    "dags",
    "vr",
}

# File extensions to INCLUDE (whitelist approach for critical files)
IMPORTANT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".csv",
    ".toml",
    ".cfg",
    ".ini",
    ".sh",
    ".bash",
    ".R",
    ".ipynb",
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def build_exclusion_set(profile: str) -> set[str]:
    """Build the exclusion set based on the selected profile."""

    exclusions = set(EXCLUSIONS)

    if profile == "slim":
        exclusions.update(SLIM_EXCLUSIONS)

    return exclusions


def should_exclude(path: Path, repo_root: Path, exclusions: set[str]) -> bool:
    """
    Check if a path should be excluded from the ZIP.

    Args:
        path: Path to check
        repo_root: Repository root path

    Returns:
        True if path should be excluded, False otherwise
    """
    relative = path.relative_to(repo_root)
    relative_str = str(relative)

    # Check against exclusion patterns
    for exclusion in exclusions:
        if exclusion.startswith("*."):
            # Pattern matching for file extensions
            if relative_str.endswith(exclusion[1:]):
                return True
        else:
            # Direct path matching
            if exclusion in relative_str.split(os.sep):
                return True
            if relative_str.startswith(exclusion):
                return True

    return False


def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA256 hash of a file.

    Args:
        file_path: Path to file

    Returns:
        Hexadecimal hash string
    """
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_all_files(repo_root: Path, exclusions: set[str]) -> list[Path]:
    """
    Get all files in repository that should be included.

    Args:
        repo_root: Repository root path

    Returns:
        List of file paths to include
    """
    all_files = []

    for root, dirs, files in os.walk(repo_root):
        root_path = Path(root)

        # Remove excluded directories from traversal
        dirs[:] = [d for d in dirs if not should_exclude(root_path / d, repo_root, exclusions)]

        for file in files:
            file_path = root_path / file

            if not should_exclude(file_path, repo_root, exclusions):
                all_files.append(file_path)

    return sorted(all_files)


def create_zip_archive(repo_root: Path, output_path: Path, files: list[Path]) -> None:
    """
    Create ZIP archive of repository.

    Args:
        repo_root: Repository root path
        output_path: Output ZIP file path
        files: List of files to include
    """
    print(f"Creating ZIP archive: {output_path}")
    print(f"Total files to archive: {len(files)}")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for i, file_path in enumerate(files, 1):
            arcname = file_path.relative_to(repo_root)
            zipf.write(file_path, arcname)

            if i % 100 == 0:
                print(f"  Archived {i}/{len(files)} files...")

    print(f"✓ ZIP archive created: {output_path}")
    print(f"  Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")


def create_manifest(
    repo_root: Path,
    output_path: Path,
    files: list[Path],
    profile: str,
) -> None:
    """
    Create MANIFEST.txt listing all files with metadata.

    Args:
        repo_root: Repository root path
        output_path: Output manifest file path
        files: List of files included in ZIP
    """
    print(f"Creating manifest: {output_path}")

    with open(output_path, "w") as f:
        f.write(f"# FELDTHEORIE V{VERSION} - SOURCE ARCHIVE MANIFEST\n")
        f.write(f"# Generated: {datetime.utcnow().isoformat()}Z\n")
        f.write(f"# Total files: {len(files)}\n")
        f.write(f"# Profile: {profile}\n")
        f.write("#\n")
        f.write("# Format: <path> | <size_bytes> | <sha256_hash> | <modified_timestamp>\n")
        f.write("#" + "=" * 100 + "\n\n")

        for file_path in files:
            relative = file_path.relative_to(repo_root)
            size = file_path.stat().st_size
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

            # Compute hash only for small files (< 10 MB) to save time
            if size < 10 * 1024 * 1024:
                file_hash = compute_file_hash(file_path)
            else:
                file_hash = "LARGE_FILE_HASH_SKIPPED"

            f.write(f"{relative} | {size} | {file_hash} | {mtime}\n")

    print(f"✓ Manifest created: {output_path}")


def create_upload_checklist(output_path: Path, zip_path: Path) -> None:
    """
    Create upload checklist for Zenodo.

    Args:
        output_path: Output checklist file path
        zip_path: Path to ZIP archive
    """
    print(f"Creating upload checklist: {output_path}")

    content = f"""# Zenodo Upload Checklist

**Version:** {VERSION}
**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
**Archive:** {zip_path.name}

---

## Pre-Upload Verification

- [ ] **Archive Integrity:** Verify ZIP file is not corrupted
  ```bash
  unzip -t {zip_path.name}
  ```

- [ ] **Manifest Review:** Check MANIFEST.txt for completeness
  ```bash
  cat MANIFEST.txt | wc -l  # Should show ~500-1000 files
  ```

- [ ] **Papers Ready:** Ensure both papers are finalized
  - [ ] Paper_1_The_Fractal_Engine.md (Methodological)
  - [ ] Paper_2_Hypothesis_137_Beta.md (Theoretical)

- [ ] **Abstract Ready:** ABSTRACT_ZENODO.md finalized

---

## Zenodo Upload Steps

### Step 1: Create New Upload

1. Go to https://zenodo.org/
2. Click "Upload" → "New Upload"
3. Choose "Upload type: Software"

### Step 2: Upload Files

**Upload in this order:**

1. **Paper_1_The_Fractal_Engine.md** (or converted to PDF)
   - Description: "Methodological paper describing fractal governance system"

2. **Paper_2_Hypothesis_137_Beta.md** (or converted to PDF)
   - Description: "Theoretical note on structural isomorphism hypotheses"

3. **{zip_path.name}**
   - Description: "Complete source repository snapshot (v{VERSION})"

4. **MANIFEST.txt**
   - Description: "File listing with integrity hashes"

### Step 3: Fill Metadata

**Basic Information:**
- **Title:** `Feldtheorie V5: A Fractal Governance System for Structural Isomorphism Research`
- **Upload Type:** Software
- **Publication Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
- **Version:** {VERSION}

**Authors:** (In order)
- Johann Benjamin Römer (Primary author)
- Genesis Aeon (Framework developer)
- MOR Collective (Contributors)

**Description:**
Copy from ABSTRACT_ZENODO.md (first 2-3 paragraphs)

**Keywords:** (Comma-separated)
```
fractal-governance, research-software-engineering, UTAC, structural-isomorphism,
null-hypothesis-testing, cosmic-scaling, social-phase-transitions,
empirical-validation, reproducible-research, 137-beta
```

**License:**
- Software: GPLv3 (copyleft)
- Documentation: CC BY-NC 4.0 (non-commercial; commercial use requires author permission)
- (Select "Other (Open)" and specify in description)

**Related Identifiers:**
- **GitHub Repository:** https://github.com/GenesisAeon/Feldtheorie
- **Is supplement to:** (Add DOI if previous version exists)

**Contributors:**
- MOR Collective (Other)

**References:**
- Böhme et al. (2021) - CMB dipole velocity measurement
- CODATA 2018 - Fundamental constants
- (Add others as needed)

**Subjects:**
- Computer and Information Science → Software Engineering
- Physical Sciences → Astrophysics
- Social Sciences → Complex Systems

**Language:** English

### Step 4: Access Rights

- **Access:** Open Access
- **License:** GPLv3 (Software) / CC BY-NC 4.0 (Docs)
- **Embargo:** None

### Step 5: Funding (Optional)

If applicable, add funding information.

### Step 6: Review and Publish

1. Click "Preview" to review metadata
2. Check all fields are correct
3. Click "Publish"
4. **IMPORTANT:** Save the DOI!

---

## Post-Publication

### Step 1: Update Repository

Add DOI badge to README.md:
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

### Step 2: Update Citation

Update ABSTRACT_ZENODO.md with actual DOI:
```bibtex
@software{{feldtheorie_v5_2025,
  author = {{Römer, Johann Benjamin and {{Genesis Aeon}} and {{MOR Collective}}}},
  title = {{Feldtheorie V5: A Fractal Governance System}},
  year = {{2025}},
  version = {{{VERSION}}},
  publisher = {{Zenodo}},
  doi = {{10.5281/zenodo.XXXXXXX}},  # <-- UPDATE THIS
  url = {{https://github.com/GenesisAeon/Feldtheorie}}
}}
```

### Step 3: Announce

- [ ] Update GitHub release with Zenodo DOI
- [ ] Share on relevant communities (if desired)
- [ ] Archive this checklist with actual DOI

---

## Troubleshooting

**Problem:** ZIP file too large (>50 GB)
- **Solution:** Remove large binary files, create separate data archive

**Problem:** Metadata fields missing
- **Solution:** Use "Save draft" and return later

**Problem:** DOI not appearing
- **Solution:** Wait 5-10 minutes, refresh page

**Problem:** Need to update after publication
- **Solution:** Create new version (Zenodo supports versioning)

---

## Verification Commands

**Check ZIP integrity:**
```bash
unzip -t {zip_path.name}
```

**Count files in ZIP:**
```bash
unzip -l {zip_path.name} | wc -l
```

**Verify manifest:**
```bash
cat MANIFEST.txt | grep -c "\.py"  # Count Python files
cat MANIFEST.txt | grep -c "\.md"  # Count Markdown files
```

**Check archive size:**
```bash
ls -lh {zip_path.name}
```

---

## Contact

**Questions or issues?**
- GitHub Issues: https://github.com/GenesisAeon/Feldtheorie/issues
- Repository Maintainer: [See GitHub profile]

---

**Generated:** {datetime.utcnow().isoformat()}Z
**Script:** prepare_upload.py v{VERSION}
**Status:** 🟢 READY FOR UPLOAD
"""

    with open(output_path, "w") as f:
        f.write(content)

    print(f"✓ Upload checklist created: {output_path}")


# ============================================================================
# MAIN FUNCTION
# ============================================================================


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Prepare Feldtheorie V5.0.0 for Zenodo upload")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: releases/v5.0.0_Zenodo_Ready)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without creating files"
    )
    parser.add_argument(
        "--profile",
        choices=["full", "slim"],
        default="full",
        help="Choose between full repository snapshot or slimmed-down research bundle",
    )

    args = parser.parse_args()

    # Determine paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent  # Go up to repo root

    exclusions = build_exclusion_set(args.profile)

    if args.output:
        output_dir = args.output
    else:
        output_dir = script_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"FELDTHEORIE V{VERSION} - ZENODO ARTIFACT PREPARATION")
    print("=" * 80)
    print(f"Repository root: {repo_root}")
    print(f"Output directory: {output_dir}")
    print(f"Dry run: {args.dry_run}")
    print(f"Profile: {args.profile} (excludes: {len(exclusions)} patterns)")
    print()

    # Step 1: Collect files
    print("[1/4] Collecting files...")
    files = get_all_files(repo_root, exclusions)
    print(f"✓ Found {len(files)} files to include")
    print()

    # Step 2: Create ZIP archive
    if not args.dry_run:
        print("[2/4] Creating ZIP archive...")
        zip_path = output_dir / OUTPUT_ZIP_NAME
        create_zip_archive(repo_root, zip_path, files)
        print()
    else:
        print("[2/4] Skipping ZIP creation (dry run)")
        zip_path = output_dir / OUTPUT_ZIP_NAME
        print(f"Would create: {zip_path}")
        print()

    # Step 3: Create manifest
    if not args.dry_run:
        print("[3/4] Creating manifest...")
        manifest_path = output_dir / "MANIFEST.txt"
        create_manifest(repo_root, manifest_path, files, args.profile)
        print()
    else:
        print("[3/4] Skipping manifest creation (dry run)")
        manifest_path = output_dir / "MANIFEST.txt"
        print(f"Would create: {manifest_path}")
        print()

    # Step 4: Create upload checklist
    if not args.dry_run:
        print("[4/4] Creating upload checklist...")
        checklist_path = output_dir / "UPLOAD_CHECKLIST.md"
        create_upload_checklist(checklist_path, zip_path)
        print()
    else:
        print("[4/4] Skipping checklist creation (dry run)")
        checklist_path = output_dir / "UPLOAD_CHECKLIST.md"
        print(f"Would create: {checklist_path}")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if not args.dry_run:
        print(f"✓ Archive:   {zip_path}")
        print(f"  Size:      {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
        print(f"✓ Manifest:  {manifest_path}")
        print(f"✓ Checklist: {checklist_path}")
        print()
        print("NEXT STEPS:")
        print("1. Review UPLOAD_CHECKLIST.md")
        print("2. Convert papers to PDF (optional but recommended):")
        print("   - Paper_1_The_Fractal_Engine.md → PDF")
        print("   - Paper_2_Hypothesis_137_Beta.md → PDF")
        print("3. Go to https://zenodo.org/ and create new upload")
        print("4. Follow UPLOAD_CHECKLIST.md instructions")
    else:
        print("DRY RUN COMPLETE")
        print(f"Would include {len(files)} files in archive")
        print("Run without --dry-run to create actual artifacts")

    print()
    print("🚀 READY FOR ZENODO UPLOAD!")
    print("=" * 80)


if __name__ == "__main__":
    main()
