#!/usr/bin/env python3
"""Version synchronisation script.

Reads VERSION.yaml (single source of truth) and ensures that
pyproject.toml and README.md carry consistent version strings.

Usage
-----
Check only (CI-safe, no writes)::

    python scripts/update_version.py --check

Apply changes in-place::

    python scripts/update_version.py --apply
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
VERSION_FILE = BASE_DIR / "VERSION.yaml"
PYPROJECT = BASE_DIR / "pyproject.toml"
README = BASE_DIR / "README.md"


def load_version_yaml() -> dict[str, str]:
    with VERSION_FILE.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    required = ("package_version", "release_stream", "stable_version", "alpha_version")
    for key in required:
        if key not in data:
            raise KeyError(f"VERSION.yaml missing required key: {key}")
    return data


# ---------------------------------------------------------------------------
# pyproject.toml
# ---------------------------------------------------------------------------

_PYPROJECT_VERSION_RE = re.compile(r'^(version\s*=\s*")([^"]+)(")', re.MULTILINE)


def check_pyproject(expected: str) -> tuple[bool, str]:
    text = PYPROJECT.read_text(encoding="utf-8")
    match = _PYPROJECT_VERSION_RE.search(text)
    if not match:
        return False, "Could not locate version field in pyproject.toml"
    current = match.group(2)
    if current == expected:
        return True, f"pyproject.toml version OK ({current})"
    return False, f"pyproject.toml version mismatch: {current} != {expected}"


def apply_pyproject(expected: str) -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    new_text, count = _PYPROJECT_VERSION_RE.subn(rf"\g<1>{expected}\3", text)
    if count == 0:
        raise RuntimeError("Could not locate version field in pyproject.toml")
    PYPROJECT.write_text(new_text, encoding="utf-8")
    return f"pyproject.toml updated to {expected}"


# ---------------------------------------------------------------------------
# README.md badges
# ---------------------------------------------------------------------------

_BADGE_PATTERNS: dict[str, re.Pattern[str]] = {
    "stable": re.compile(
        r"(\[!\[Stable\]\(https://img\.shields\.io/badge/Stable-)([^)]+?)(-[a-z]+\.svg\))"
    ),
    "release": re.compile(
        r"(\[!\[Release\]\(https://img\.shields\.io/badge/Release-)([^)]+?)(-[a-z0-9]+\.svg\))"
    ),
    "alpha": re.compile(
        r"(\[!\[V9 Alpha\]\(https://img\.shields\.io/badge/Alpha-)([^)]+?)(-[a-z]+\.svg\))"
    ),
}


def _badge_value(raw: str) -> str:
    """URL-encode spaces and hyphens for shields.io badge values."""
    return raw.replace(" ", "%20").replace("-", "--")


def check_readme_versions(versions: dict[str, str]) -> list[tuple[bool, str]]:
    text = README.read_text(encoding="utf-8")
    results: list[tuple[bool, str]] = []
    mapping = {
        "stable": versions["stable_version"],
        "release": versions["release_stream"],
        "alpha": versions["alpha_version"],
    }
    for key, expected_raw in mapping.items():
        pattern = _BADGE_PATTERNS[key]
        match = pattern.search(text)
        if not match:
            results.append((False, f"README badge '{key}' not found"))
            continue
        expected_encoded = _badge_value(expected_raw)
        current = match.group(2)
        if current == expected_encoded:
            results.append((True, f"README badge '{key}' OK ({expected_raw})"))
        else:
            results.append(
                (False, f"README badge '{key}' mismatch: {current} != {expected_encoded}")
            )
    return results


def apply_readme_versions(versions: dict[str, str]) -> list[str]:
    text = README.read_text(encoding="utf-8")
    messages: list[str] = []
    mapping = {
        "stable": versions["stable_version"],
        "release": versions["release_stream"],
        "alpha": versions["alpha_version"],
    }
    for key, expected_raw in mapping.items():
        expected_encoded = _badge_value(expected_raw)
        pattern = _BADGE_PATTERNS[key]
        text, count = pattern.subn(rf"\g<1>{expected_encoded}\3", text)
        if count:
            messages.append(f"README badge '{key}' updated to {expected_raw}")
        else:
            messages.append(f"README badge '{key}' not found — skipped")
    README.write_text(text, encoding="utf-8")
    return messages


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Synchronise version strings from VERSION.yaml")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Check consistency (exit 1 on drift)")
    group.add_argument("--apply", action="store_true", help="Write corrected values in-place")
    args = parser.parse_args()

    try:
        versions = load_version_yaml()
    except Exception as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2

    pkg = versions["package_version"]
    ok = True

    if args.check:
        pyp_ok, pyp_msg = check_pyproject(pkg)
        print(pyp_msg)
        ok = ok and pyp_ok
        for badge_ok, badge_msg in check_readme_versions(versions):
            print(badge_msg)
            ok = ok and badge_ok
        return 0 if ok else 1

    # --apply
    print(apply_pyproject(pkg))
    for msg in apply_readme_versions(versions):
        print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
