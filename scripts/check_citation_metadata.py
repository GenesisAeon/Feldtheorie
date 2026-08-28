"""Guard against known-wrong numeric literals reappearing in citation-facing
metadata (CITATION.cff, .zenodo.json, README.md).

These files are plain text/JSON, disconnected from the Python source of
truth (theory.afet.AFETConstants), so a code-level fix does not protect
them from a future manual edit reintroducing an old, since-corrected value
by hand or via copy-paste from an outdated source (Zenodo abstract, X post
draft, etc.).

Usage: python scripts/check_citation_metadata.py
"""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

# (file, banned substring, reason)
CHECKS: list[tuple[str, str, str]] = [
    (
        "CITATION.cff",
        "1.352 km/s",
        "v_RIG = c/(alpha^-1 * phi) = 1352.07 km/s, not 1.352 -- the '1.352' "
        "spelling misreads internationally as a decimal fraction (German-style "
        "thousands separator), a real factor-1000 error.",
    ),
    (
        ".zenodo.json",
        "1.352 km/s",
        "v_RIG = c/(alpha^-1 * phi) = 1352.07 km/s, not 1.352 -- feeds the next "
        "automated Zenodo release, so this regressing here reintroduces it live.",
    ),
    (
        "README.md",
        "1.352 km/s",
        "v_RIG = c/(alpha^-1 * phi) = 1352.07 km/s, not 1.352.",
    ),
]


def main() -> int:
    violations: list[str] = []
    for rel_path, banned, reason in CHECKS:
        path = BASE_DIR / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if banned in text:
            violations.append(f"{rel_path}: contains {banned!r} -- {reason}")

    if violations:
        print("Citation metadata guard failed:")
        for v in violations:
            print(f" - {v}")
        return 1

    print("Citation metadata guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
