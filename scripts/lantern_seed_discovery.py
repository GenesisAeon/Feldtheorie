"""Discover seed/release modules and build a Lantern inventory.

Scans the seed/ and releases/ directory trees, identifies directories that
contain source or documentation files, and emits a YAML inventory that can be
merged into LanternNet.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import yaml

CONSENT_PROMPT = (
    "Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration."
)
DEFAULT_OUTPUT = Path("v9_alpha/config/lantern_seed_inventory.yaml")
DEFAULT_BASE_DIRS = (Path("seed"), Path("releases"))
ALLOWED_EXTENSIONS = {
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".txt",
    ".pdf",
    ".csv",
    ".nc",
    ".ipynb",
}
EXCLUDED_DIRS = {"__pycache__", ".git", ".venv", ".mypy_cache", ".pytest_cache"}


@dataclass(frozen=True)
class Defaults:
    readiness: float = 0.1
    theta: float = 0.5
    beta: float = 4.8
    order_parameter: str = "module_reflection"
    status: str = "draft"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slugify(text: str) -> str:
    slug = []
    for char in text.lower():
        if char.isalnum():
            slug.append(char)
        else:
            slug.append("-")
    result = "".join(slug)
    while "--" in result:
        result = result.replace("--", "-")
    return result.strip("-")


def _humanize_segment(segment: str) -> str:
    cleaned = segment.replace("_", " ").replace("-", " ")
    if cleaned.lower().startswith("v") and any(char.isdigit() for char in cleaned):
        return segment
    return cleaned.title()


def _domain_from_parts(parts: tuple[str, ...], fallback: str) -> str:
    if not parts:
        return fallback
    return parts[0]


def _documentation_paths(directory: Path, base_path: Path) -> dict[str, str | None]:
    base_path = base_path.resolve()

    def find_file(target: str) -> str | None:
        for candidate in (target, target.lower(), target.upper()):
            path = (directory / candidate).resolve()
            if path.exists():
                return str(path.relative_to(base_path))
        return None

    return {
        "readme": find_file("README.md"),
        "methodology": find_file("methodology.md"),
        "roadmap": find_file("roadmap.md"),
    }


def _has_allowed_files(directory: Path) -> bool:
    for item in directory.iterdir():
        if item.is_file() and item.suffix.lower() in ALLOWED_EXTENSIONS:
            return True
    return False


def _iter_module_dirs(base_dir: Path, max_depth: int) -> Iterable[Path]:
    if not base_dir.exists():
        return []
    candidates = []
    for path in base_dir.rglob("*"):
        if not path.is_dir():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        depth = len(path.relative_to(base_dir).parts)
        if depth == 0 or depth > max_depth:
            continue
        if _has_allowed_files(path):
            candidates.append(path)
    return sorted(candidates)


def _build_entry(directory: Path, base_dir: Path, defaults: Defaults) -> dict[str, object]:
    relative_parts = directory.relative_to(base_dir).parts
    prefix = "seed" if base_dir.name == "seed" else "release"
    slug = _slugify("/".join(relative_parts))
    module_id = f"{prefix}-{slug}"
    name_parts = [_humanize_segment(part) for part in relative_parts]
    module_name = f"{prefix.title()} " + " / ".join(name_parts)
    documentation = _documentation_paths(directory, Path.cwd())
    domain = _domain_from_parts(relative_parts, base_dir.name)
    return {
        "id": module_id,
        "name": module_name,
        "type": prefix,
        "domain": domain,
        "status": defaults.status,
        "readiness": defaults.readiness,
        "order_parameter": defaults.order_parameter,
        "theta": defaults.theta,
        "beta": defaults.beta,
        "documentation": documentation,
        "notes": {
            "formal": "Seed/Release module cataloged for LanternNet reflection.",
            "poetic": "Die Laterne wird sichtbar, sobald σ(β(R-Θ)) das Feld berührt.",
        },
    }


def build_inventory(
    base_dirs: Iterable[Path],
    max_depth: int,
    defaults: Defaults,
) -> list[dict[str, object]]:
    inventory: list[dict[str, object]] = []
    for base_dir in base_dirs:
        for directory in _iter_module_dirs(base_dir, max_depth):
            inventory.append(_build_entry(directory, base_dir, defaults))
    return inventory


def write_inventory(path: Path, lanterns: list[dict[str, object]], defaults: Defaults) -> None:
    payload = {
        "meta": {
            "document": "Seed/Release Lantern Inventory",
            "created": _timestamp(),
            "updated": _timestamp(),
            "source": str(path),
            "base_directories": [str(base) for base in DEFAULT_BASE_DIRS],
            "consent_prompt": CONSENT_PROMPT,
            "default_parameters": {
                "readiness": defaults.readiness,
                "theta": defaults.theta,
                "beta": defaults.beta,
                "order_parameter": defaults.order_parameter,
                "status": defaults.status,
            },
        },
        "lanterns": lanterns,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover seed/release Lantern modules.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument(
        "--base-dir",
        action="append",
        type=Path,
        default=list(DEFAULT_BASE_DIRS),
        help="Base directory to scan (repeatable). Defaults to seed/ and releases/.",
    )
    args = parser.parse_args()

    defaults = Defaults()
    lanterns = build_inventory(args.base_dir, args.max_depth, defaults)
    write_inventory(args.output, lanterns, defaults)


if __name__ == "__main__":
    main()
