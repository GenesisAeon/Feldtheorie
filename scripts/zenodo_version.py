#!/usr/bin/env python3
"""Resolve the Zenodo bundle version aligned with the UTAC logistic membrane."""
from __future__ import annotations

import pathlib
import sys


def _load_version_from_pyproject() -> str | None:
    pyproject_path = pathlib.Path("pyproject.toml")
    if not pyproject_path.exists():
        return None

    try:
        import tomllib  # type: ignore[attr-defined]
    except ModuleNotFoundError:  # Python < 3.11
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ModuleNotFoundError:
            return None

    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return data.get("project", {}).get("version")


def main() -> None:
    version = _load_version_from_pyproject() or "dev"
    sys.stdout.write(str(version))


if __name__ == "__main__":
    main()
