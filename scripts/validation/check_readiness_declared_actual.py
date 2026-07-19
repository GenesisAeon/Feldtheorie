#!/usr/bin/env python3
"""Validate declared vs actual existence flags in UTAC readiness reports.

This guard keeps the status membrane stable by measuring drift between declared
expectations and runtime filesystem truth in the readiness tri-layer.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def _load_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Report not found: {path}")
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix in {".yaml", ".yml"}:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError(f"Expected mapping at top-level in {path}")
        return loaded
    raise ValueError(f"Unsupported report format: {path}")


def _iter_component_scopes(report: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    """Return named component scopes from known readiness schemas.

    Current readiness reports store components under ``datasets``; older reports
    used ``domains``. We support both so drift checks stay robust during schema
    transitions.
    """

    datasets = report.get("datasets")
    if isinstance(datasets, list):
        scopes: list[tuple[str, list[dict[str, Any]]]] = []
        for dataset in datasets:
            if not isinstance(dataset, dict):
                continue
            dataset_id = str(dataset.get("id", "unknown-dataset"))
            domain = str(dataset.get("domain", "unknown-domain"))
            scope_label = f"{dataset_id} ({domain})"
            components = dataset.get("components", [])
            if isinstance(components, list):
                scopes.append((scope_label, components))
        return scopes

    domains = report.get("domains")
    if isinstance(domains, list):
        scopes = []
        for domain in domains:
            if not isinstance(domain, dict):
                continue
            domain_name = str(domain.get("name", "unknown-domain"))
            components = domain.get("components", [])
            if isinstance(components, list):
                scopes.append((domain_name, components))
        return scopes

    return []


def _collect_mismatches(report: dict[str, Any]) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    for scope_name, components in _iter_component_scopes(report):
        for component in components:
            if not isinstance(component, dict):
                continue
            declared = component.get("declared_exists")
            actual = component.get("actual_exists")
            if declared is None or actual is None:
                continue
            if bool(declared) != bool(actual):
                mismatches.append(
                    {
                        "scope": scope_name,
                        "component": component.get("name", "unknown-component"),
                        "path": component.get("path", "unknown-path"),
                        "declared_exists": bool(declared),
                        "actual_exists": bool(actual),
                    }
                )
    return mismatches


def _print_report(label: str, mismatches: list[dict[str, Any]]) -> None:
    print(f"{label}: {len(mismatches)} declared/actual mismatches")
    for mismatch in mismatches:
        print(
            "  - "
            f"{mismatch['scope']} :: {mismatch['component']} ({mismatch['path']}): "
            f"declared_exists={mismatch['declared_exists']} vs "
            f"actual_exists={mismatch['actual_exists']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check declared_exists vs actual_exists mismatches in readiness reports."
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("analysis/reports/utac_v2_readiness.json"),
        help="Path to readiness JSON report.",
    )
    parser.add_argument(
        "--yaml",
        type=Path,
        default=Path("analysis/reports/utac_v2_readiness.yaml"),
        help="Path to readiness YAML report.",
    )
    args = parser.parse_args()

    json_report = _load_report(args.json)
    yaml_report = _load_report(args.yaml)

    json_mismatches = _collect_mismatches(json_report)
    yaml_mismatches = _collect_mismatches(yaml_report)

    _print_report("JSON", json_mismatches)
    _print_report("YAML", yaml_mismatches)

    if json_mismatches or yaml_mismatches:
        print("❌ readiness drift detected: declared_exists diverges from actual_exists")
        return 1

    print("✅ readiness declared/actual parity is stable (ζ(R) drift guard clear)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
