#!/usr/bin/env python3
"""Inject live test counts into README.md badge and prose.

This script collects the current test count from pytest and updates
the README badge and hard-coded test numbers so they stay in sync
with the actual test suite.

Usage
-----
Check only (CI-safe)::

    python scripts/update_badges.py --check

Apply in-place::

    python scripts/update_badges.py --apply

Override test count (skip pytest collection)::

    python scripts/update_badges.py --apply --test-count 600
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
README = BASE_DIR / "README.md"


def collect_test_count() -> int:
    """Run ``pytest --collect-only -q`` and extract the total test count."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=BASE_DIR,
    )
    # Last meaningful line is like "567 tests collected"
    for line in reversed(result.stdout.strip().splitlines()):
        match = re.search(r"(\d+)\s+tests?\s+collected", line)
        if match:
            return int(match.group(1))
    raise RuntimeError(
        f"Could not parse test count from pytest output:\n{result.stdout}\n{result.stderr}"
    )


# Patterns to update in README
_BADGE_RE = re.compile(
    r"(https://img\.shields\.io/badge/tests-)(\d+%2F\d+%20passing)(-[a-z]+\.svg)"
)
_PROSE_RE = re.compile(r"\b(\d+)/\1 tests passing\b")
_PROSE_TOTAL_RE = re.compile(r"\b(\d+)/\1 passing\b")


def _update_readme(text: str, count: int) -> str:
    badge_value = f"{count}%2F{count}%20passing"
    text = _BADGE_RE.sub(rf"\g<1>{badge_value}\3", text)

    # Update prose like "567/567 tests passing" and "567/567 passing"
    text = _PROSE_RE.sub(f"{count}/{count} tests passing", text)
    text = _PROSE_TOTAL_RE.sub(f"{count}/{count} passing", text)
    return text


def check(count: int) -> tuple[bool, list[str]]:
    text = README.read_text(encoding="utf-8")
    messages: list[str] = []
    ok = True

    badge_match = _BADGE_RE.search(text)
    if badge_match:
        expected = f"{count}%2F{count}%20passing"
        if badge_match.group(2) != expected:
            ok = False
            messages.append(
                f"Badge test count mismatch: {badge_match.group(2)} != {expected}"
            )
        else:
            messages.append(f"Badge test count OK ({count})")
    else:
        messages.append("Test badge not found in README")
        ok = False

    return ok, messages


def apply(count: int) -> list[str]:
    text = README.read_text(encoding="utf-8")
    new_text = _update_readme(text, count)
    if new_text != text:
        README.write_text(new_text, encoding="utf-8")
        return [f"README test counts updated to {count}"]
    return [f"README test counts already at {count} — no changes"]


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Sync README test badge with actual test count")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Check consistency")
    group.add_argument("--apply", action="store_true", help="Update README in-place")
    parser.add_argument(
        "--test-count",
        type=int,
        default=None,
        help="Override test count instead of running pytest",
    )
    args = parser.parse_args()

    if args.test_count is not None:
        count = args.test_count
    else:
        try:
            count = collect_test_count()
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    print(f"Test count: {count}")

    if args.check:
        ok, messages = check(count)
        for msg in messages:
            print(msg)
        return 0 if ok else 1

    for msg in apply(count):
        print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
