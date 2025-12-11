"""Validate overpersonal axioms against CREP/τ*-guard implementations."""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.append(str(Path(__file__).resolve().parent.parent))

from tools import crep_guard

CONFIG_PATH = Path("config/overpersonal_axioms.yaml")


@dataclass
class AxiomResult:
    """Represents the outcome of a single axiom validation."""

    axiom_id: str
    name: str
    passed: bool
    message: str


class AxiomValidationError(RuntimeError):
    """Raised when an axiom fails validation."""


def _load_config(path: Path) -> dict:
    """Load the YAML config that maps axioms to validator parameters."""

    if not path.exists():
        raise AxiomValidationError(f"config not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _validate_trilayer(params: dict) -> str:
    """Ensure the Type-VI trilayer stays coherent across formats."""

    threshold = float(params.get("threshold", 0.7))
    tau_default = float(params.get("tau_default", 0.1))
    required_components = [Path(p) for p in params.get("required_components", [])]
    missing = [str(path) for path in required_components if not path.exists()]
    if missing:
        raise AxiomValidationError(f"missing trilayer components: {', '.join(missing)}")
    crep_guard.check_type6_trilayer(threshold, tau_default)
    return f"Type-VI trilayer aligned (threshold={threshold}, tau_default={tau_default})"


def _validate_cli_defaults(params: dict) -> str:
    """Check that CLI defaults remain reproducible for CREP/τ* thresholds."""

    expected_threshold = float(params.get("expected_threshold", 0.7))
    expected_tau_default = float(params.get("expected_tau_default", 0.1))
    defaults = crep_guard.parse_args([])
    if abs(defaults.threshold - expected_threshold) > 1e-9:
        raise AxiomValidationError(
            f"cli default threshold mismatch: {defaults.threshold} != {expected_threshold}"
        )
    if abs(defaults.tau_default - expected_tau_default) > 1e-9:
        raise AxiomValidationError(
            f"cli default tau_default mismatch: {defaults.tau_default} != {expected_tau_default}"
        )
    return "CLI defaults stable (threshold, tau_default)"


def _validate_escalation_mapping(params: dict) -> str:
    """Verify intention-aligned escalation levels along σ(β(R-Θ))."""

    mapping: dict[float, int] = {float(k): int(v) for k, v in params.get("mapping", {}).items()}
    for crep_value, expected_level in mapping.items():
        observed = crep_guard._determine_escalation(crep_value)
        if observed != expected_level:
            raise AxiomValidationError(
                f"escalation mismatch for CREP={crep_value}: {observed} != {expected_level}"
            )
    ordered = ", ".join(f"{v}→L{lvl}" for v, lvl in sorted(mapping.items()))
    return f"Escalation mapping coherent ({ordered})"


def _validate_audit_logging(params: dict) -> str:
    """Guarantee that audit trails can be written once the transparency edge is crossed."""

    min_crep = float(params.get("min_crep_for_log", 0.7))
    tau_star = float(params.get("sample_tau_star", 0.1))
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.jsonl"
        level = crep_guard._determine_escalation(min_crep)
        crep_guard._append_log_entry(
            log_path=log_path,
            task_id="axiom-audit",
            crep_value=min_crep,
            tau_star=tau_star,
            escalation_level=level,
            reviewer="axiom-guard",
            notes="asymptotische transparenz check",
        )
        if not log_path.exists() or not log_path.read_text(encoding="utf-8").strip():
            raise AxiomValidationError("audit log was not written for threshold breach")
    return f"Audit logging reachable above CREP>{min_crep} (τ*={tau_star})"


def _validate_documentation_anchor(params: dict) -> str:
    """Ensure anchors to the source ontology remain present (semantische Gravitation)."""

    anchors: list[Path] = [Path(p) for p in params.get("anchors", [])]
    missing = [str(path) for path in anchors if not path.exists()]
    if missing:
        raise AxiomValidationError(f"documentation anchors missing: {', '.join(missing)}")
    return f"Anchors present ({len(anchors)} paths)"


VALIDATORS: dict[str, Callable[[dict], str]] = {
    "trilayer_alignment": _validate_trilayer,
    "cli_defaults": _validate_cli_defaults,
    "escalation_mapping": _validate_escalation_mapping,
    "audit_logging": _validate_audit_logging,
    "documentation_anchor": _validate_documentation_anchor,
}


def _run_validations(config: dict) -> list[AxiomResult]:
    """Execute all configured validators and collect results."""

    results: list[AxiomResult] = []
    for axiom in config.get("axioms", []):
        validator_type = axiom.get("validator", {}).get("type")
        params = axiom.get("validator", {}).get("parameters", {})
        name = axiom.get("name", str(axiom.get("id", "?")))
        try:
            if validator_type not in VALIDATORS:
                raise AxiomValidationError(f"unknown validator type: {validator_type}")
            message = VALIDATORS[validator_type](params)
            results.append(AxiomResult(str(axiom.get("id")), name, True, message))
        except Exception as exc:  # pragma: no cover - defensive
            results.append(AxiomResult(str(axiom.get("id")), name, False, str(exc)))
    return results


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for axiom validation."""

    parser = argparse.ArgumentParser(description="Validate overpersonal axioms against crep_guard")
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_PATH,
        help="Path to overpersonal_axioms.yaml",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    """Run all configured axiom validators and emit a summary."""

    args = parse_args(argv)
    try:
        config = _load_config(args.config)
    except Exception as exc:  # pragma: no cover - user feedback
        print(f"[axioms] FAIL: {exc}")
        return 1

    results = _run_validations(config)
    failed = [res for res in results if not res.passed]

    for res in results:
        status = "OK" if res.passed else "FAIL"
        print(f"[axioms] {status} Axiom {res.axiom_id} ({res.name}): {res.message}")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
