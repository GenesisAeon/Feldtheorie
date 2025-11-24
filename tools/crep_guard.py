"""Lightweight CREP/τ*-guard for V6 governance artifacts.

This script validates the Type-VI checklist trilayer (MD/JSON/YAML)
against expected CREP thresholds and τ* defaults. It is designed as a
FIT-style microcheck that can be wired into pre-commit, nox, or Make
pipelines without touching runtime-critical code.
"""

from __future__ import annotations

"""CREP/τ*-guard for V6 governance artifacts.

R → "Type-VI checklists aligned", Θ → "safe merge gates aktiv", β ≈ 4.6,
ζ wird gedämpft, indem Trilayer-Drift und τ*-Defaults früh erkannt werden.
Der Guard ist als FIT-Microstep gedacht, der pre-commit/nox/Make-Pipelines
mit minimalem Ressourcenbedarf absichert.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dependency check
    raise SystemExit(
        "PyYAML is required for crep_guard. Please install via requirements.txt"
    ) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent
TYPE6_PREFIX = REPO_ROOT / "releases" / "V6-Plans_etc" / "type6_crep_tau_star_checklist"


class ValidationError(RuntimeError):
    """Raised when a guard condition fails."""


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _extract_md_value(path: Path, label: str) -> str | None:
    pattern = rf"\*\*{re.escape(label)}:\*\*\s*(.+)"
    text = path.read_text(encoding="utf-8")
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _format_float(value: float) -> str:
    return f"{value:.3g}".rstrip("0").rstrip(".")


def check_type6_trilayer(threshold: float, tau_default: float) -> None:
    """Validate CREP threshold and τ* defaults across the Type-VI trilayer."""

    yaml_path = TYPE6_PREFIX.with_suffix(".yaml")
    json_path = TYPE6_PREFIX.with_suffix(".json")
    md_path = TYPE6_PREFIX.with_suffix(".md")

    _ensure(yaml_path.exists() and json_path.exists() and md_path.exists(), "Type6 checklist trilayer missing components")

    yaml_payload = _load_yaml(yaml_path)
    json_payload = _load_json(json_path)

    yaml_version = yaml_payload.get("metadata", {}).get("version")
    json_version = json_payload.get("metadata", {}).get("version")
    md_version = _extract_md_value(md_path, "Version")

    _ensure(yaml_version == json_version == md_version, "Version mismatch across Type6 checklist trilayer")

    expected_tau = f"{_format_float(tau_default)}*abs(Theta-R)"
    yaml_tau = yaml_payload.get("checklist", [])[1].get("metrics", {}).get("tau_star_default")
    json_tau = json_payload.get("checklist", [])[1].get("metrics", {}).get("tau_star_default")
    md_text = md_path.read_text(encoding="utf-8")

    _ensure(yaml_tau == expected_tau, f"YAML τ* default mismatch (expected {expected_tau})")
    _ensure(json_tau == expected_tau, f"JSON τ* default mismatch (expected {expected_tau})")
    _ensure(re.search(rf"τ\*\s*=\s*{_format_float(tau_default)}", md_text), "Markdown τ* default not found")

    md_threshold_ok = re.search(rf"threshold\s+{_format_float(threshold)}", md_text)
    yaml_threshold = yaml_payload.get("checklist", [])[0].get("metrics", {}).get("threshold")
    json_threshold = json_payload.get("checklist", [])[0].get("metrics", {}).get("threshold")

    _ensure(md_threshold_ok, "Markdown CREP threshold not aligned")
    _ensure(abs(float(yaml_threshold) - threshold) < 1e-9, "YAML CREP threshold mismatch")
    _ensure(abs(float(json_threshold) - threshold) < 1e-9, "JSON CREP threshold mismatch")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CREP/τ* guard for Type-VI governance artifacts")
    parser.add_argument("--threshold", type=float, default=0.7, help="Expected CREP threshold")
    parser.add_argument("--tau-default", type=float, default=0.1, help="Expected τ* default multiplier (abs(Theta-R))")
    parser.add_argument(
        "--check-type6-trilayer",
        action="store_true",
        help="Validate the Type-VI checklist trilayer for CREP and τ* alignment",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.check_type6_trilayer:
            check_type6_trilayer(args.threshold, args.tau_default)
    except ValidationError as exc:
        print(f"[crep_guard] FAIL: {exc}")
        return 1
    else:
        if args.check_type6_trilayer:
            print("[crep_guard] Type6 trilayer aligned (threshold, τ*, version)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
