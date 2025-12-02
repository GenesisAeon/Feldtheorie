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
from datetime import datetime
from pathlib import Path
from typing import Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
TYPE6_PREFIX = REPO_ROOT / "releases" / "V6-Plans_etc" / "type6_crep_tau_star_checklist"
DEFAULT_LOG_PATH = REPO_ROOT / "logs" / "type_vi_detections.jsonl"


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


def _determine_escalation(crep_value: float) -> int:
    """Map CREP to escalation level following AGENTS thresholds."""

    if crep_value >= 0.8:
        return 3
    if crep_value >= 0.7:
        return 2
    if crep_value >= 0.6:
        return 1
    return 0


def _append_log_entry(
    *,
    log_path: Path,
    task_id: str,
    crep_value: float,
    tau_star: float,
    escalation_level: int,
    reviewer: str,
    notes: str,
) -> None:
    """Append a Type-VI detection entry to the JSONL audit trail."""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "task_id": task_id,
        "crep_value": crep_value,
        "tau_star": tau_star,
        "escalation_level": escalation_level,
        "reviewer": reviewer,
        "notes": notes,
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


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
    parser.add_argument(
        "--log-detection",
        action="store_true",
        help="Append a CREP/τ* detection entry to logs/type_vi_detections.jsonl",
    )
    parser.add_argument("--task-id", default="v6r-crep-guard-ci", help="Task identifier to log")
    parser.add_argument("--crep-value", type=float, help="CREP value to log when --log-detection is set")
    parser.add_argument("--tau-star", type=float, help="τ* value to log when --log-detection is set")
    parser.add_argument("--escalation-level", type=int, help="Override computed escalation level")
    parser.add_argument("--reviewer", default="", help="Reviewer or routing hint for escalation")
    parser.add_argument("--notes", default="", help="Additional notes to capture in the audit trail")
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH, help="Path to the JSONL audit log")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    escalation_level: int | None = None
    try:
        if args.check_type6_trilayer:
            check_type6_trilayer(args.threshold, args.tau_default)

        if args.log_detection:
            _ensure(
                args.crep_value is not None and args.tau_star is not None,
                "--crep-value and --tau-star are required when logging detections",
            )
            escalation_level = (
                args.escalation_level
                if args.escalation_level is not None
                else _determine_escalation(args.crep_value)
            )
            _append_log_entry(
                log_path=args.log_path,
                task_id=args.task_id,
                crep_value=args.crep_value,
                tau_star=args.tau_star,
                escalation_level=escalation_level,
                reviewer=args.reviewer,
                notes=args.notes,
            )
    except ValidationError as exc:
        print(f"[crep_guard] FAIL: {exc}")
        return 1
    else:
        if args.check_type6_trilayer:
            print("[crep_guard] Type6 trilayer aligned (threshold, τ*, version)")
        if args.log_detection:
            print(
                f"[crep_guard] logged CREP={_format_float(args.crep_value or 0)} "
                f"τ*={_format_float(args.tau_star or 0)} escalation={_format_float(escalation_level or 0)}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
