r"""Logistic preset alignment guard for the simulator membrane.

Formal cadence
--------------
This module verifies that every preset in ``simulator/presets`` references
an analysis JSON whose logistic quartet \((R, \Theta, \beta, \zeta(R))\)
matches the documented values.  It recomputes the best falsification null
and ensures \(\sigma(\beta(R-\Theta))\) keeps its recorded steepness.

Empirical cadence
-----------------
The guard walks through presets, loads the referenced analysis payloads,
compares \(\Theta\), \(\beta\), $R^2$, and $\Delta\text{AIC}$ against the
JSON ground truth, and emits structured issues if any drift appears.
This allows CI and local rituals to halt when simulator sliders fall out
of resonance with the underlying fits.

Metaphorical cadence
--------------------
Each preset becomes a lantern on the bridge.  When the numbers align, the
membrane hums in sync; when they diverge, this guard rings a bell so we can
retune the impedance before dawn breaks.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

DEFAULT_REL_TOL = 1e-3
ABS_FLOOR = 1e-6


@dataclass
class PresetIssue:
    """A single mismatch between preset metadata and analysis results."""

    preset: Path
    field: str
    expected: Any
    actual: Any

    def __str__(self) -> str:  # pragma: no cover - human readable convenience
        return (
            f"{self.preset}: {self.field} mismatch — preset={self.expected!r}"
            f", analysis={self.actual!r}"
        )


def _relative_close(expected: float, actual: float, rel_tol: float) -> bool:
    scale = max(abs(actual), 1.0)
    return abs(expected - actual) <= max(rel_tol * scale, ABS_FLOOR)


def _extract_sequence(value: Any) -> Optional[List[float]]:
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
        result: List[float] = []
        for item in value:
            if isinstance(item, (int, float)):
                result.append(float(item))
            else:
                return None
        return result
    return None


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _extract_theta(payload: Mapping[str, Any]) -> tuple[Optional[float], Optional[List[float]]]:
    if isinstance(payload.get("theta_estimate"), Mapping):
        block = payload["theta_estimate"]
        return (
            float(block["value"]) if isinstance(block.get("value"), (int, float)) else None,
            _extract_sequence(block.get("ci95")),
        )
    aggregate = payload.get("aggregate")
    parameters = payload.get("parameters")
    if isinstance(aggregate, Mapping):
        value = aggregate.get("theta")
        if isinstance(value, (int, float)):
            return float(value), _extract_sequence(aggregate.get("theta_ci95"))

        final_value = aggregate.get("theta_final")
        if isinstance(final_value, (int, float)):
            ci = _extract_sequence(aggregate.get("theta_ci95"))
            if ci is None and isinstance(parameters, Mapping):
                baseline = parameters.get("theta0")
                if isinstance(baseline, (int, float)):
                    ci = [float(baseline), float(final_value)]
            return float(final_value), ci
    return (None, None)


def _extract_beta(payload: Mapping[str, Any]) -> tuple[Optional[float], Optional[List[float]]]:
    if isinstance(payload.get("beta_estimate"), Mapping):
        block = payload["beta_estimate"]
        return (
            float(block["value"]) if isinstance(block.get("value"), (int, float)) else None,
            _extract_sequence(block.get("ci95")),
        )
    aggregate = payload.get("aggregate")
    parameters = payload.get("parameters")
    if isinstance(aggregate, Mapping):
        value = aggregate.get("beta")
        if isinstance(value, (int, float)):
            return float(value), _extract_sequence(aggregate.get("beta_ci95"))

        final_value = aggregate.get("beta_final")
        if isinstance(final_value, (int, float)):
            ci = _extract_sequence(aggregate.get("beta_ci95"))
            if ci is None and isinstance(parameters, Mapping):
                baseline = parameters.get("beta0")
                if isinstance(baseline, (int, float)):
                    ci = [float(baseline), float(final_value)]
            return float(final_value), ci
    return (None, None)


def _extract_logistic_r2(payload: Mapping[str, Any]) -> Optional[float]:
    logistic = payload.get("logistic_model")
    if isinstance(logistic, Mapping) and isinstance(logistic.get("r2"), (int, float)):
        return float(logistic["r2"])
    aggregate = payload.get("aggregate")
    if isinstance(aggregate, Mapping) and isinstance(aggregate.get("r2"), (int, float)):
        return float(aggregate["r2"])
    return None


def _extract_best_null(payload: Mapping[str, Any]) -> tuple[Optional[str], Optional[float], Optional[float]]:
    comparisons: Dict[str, Mapping[str, Any]] = {}
    falsification = payload.get("falsification")
    if isinstance(falsification, Mapping):
        comps = falsification.get("comparisons")
        if isinstance(comps, Mapping):
            comparisons.update({k: v for k, v in comps.items() if isinstance(v, Mapping)})
    aggregate = payload.get("aggregate")
    if isinstance(aggregate, Mapping):
        nulls = aggregate.get("null_models")
        if isinstance(nulls, Mapping):
            comparisons.update({k: v for k, v in nulls.items() if isinstance(v, Mapping)})

    best_name: Optional[str] = None
    best_delta_aic: Optional[float] = None
    best_delta_r2: Optional[float] = None
    for name, metrics in comparisons.items():
        delta_aic = metrics.get("delta_aic")
        if not isinstance(delta_aic, (int, float)):
            continue
        delta_r2 = metrics.get("delta_r2")
        candidate_delta_r2 = float(delta_r2) if isinstance(delta_r2, (int, float)) else None
        if best_delta_aic is None or float(delta_aic) > best_delta_aic:
            best_name = name
            best_delta_aic = float(delta_aic)
            best_delta_r2 = candidate_delta_r2
    return best_name, best_delta_aic, best_delta_r2


def validate_presets(
    root: Optional[Path] = None,
    *,
    presets_dir: Optional[Path] = None,
    rel_tol: float = DEFAULT_REL_TOL,
) -> List[PresetIssue]:
    """Validate every simulator preset against its analysis source."""

    base_root = root or Path(__file__).resolve().parents[1]
    directory = presets_dir or base_root / "simulator" / "presets"
    issues: List[PresetIssue] = []

    for preset_path in sorted(directory.glob("*.json")):
        preset_data = _load_json(preset_path)
        analysis_block = preset_data.get("analysis")
        if not isinstance(analysis_block, Mapping):
            issues.append(PresetIssue(preset_path, "analysis", analysis_block, "missing block"))
            continue
        result_path_value = analysis_block.get("result_path")
        if not isinstance(result_path_value, str):
            issues.append(
                PresetIssue(preset_path, "analysis.result_path", result_path_value, "missing path")
            )
            continue
        result_path = (base_root / result_path_value).resolve()
        if not result_path.exists():
            issues.append(
                PresetIssue(preset_path, "analysis.result_path", result_path_value, "file not found")
            )
            continue

        payload = _load_json(result_path)
        theta, theta_ci = _extract_theta(payload)
        beta, beta_ci = _extract_beta(payload)
        logistic_r2 = _extract_logistic_r2(payload)
        best_name, best_delta_aic, best_delta_r2 = _extract_best_null(payload)

        preset_theta = analysis_block.get("theta")
        if isinstance(theta, float) and isinstance(preset_theta, (int, float)):
            if not _relative_close(float(preset_theta), theta, rel_tol):
                issues.append(PresetIssue(preset_path, "theta", preset_theta, theta))
        elif theta is not None or preset_theta is not None:
            issues.append(PresetIssue(preset_path, "theta", preset_theta, theta))

        preset_theta_ci = _extract_sequence(analysis_block.get("theta_ci"))
        if theta_ci is not None and preset_theta_ci is not None:
            if len(theta_ci) == len(preset_theta_ci):
                for idx, (expected, actual) in enumerate(zip(preset_theta_ci, theta_ci)):
                    if not _relative_close(expected, actual, rel_tol):
                        issues.append(
                            PresetIssue(
                                preset_path,
                                f"theta_ci[{idx}]",
                                expected,
                                actual,
                            )
                        )
            else:
                issues.append(PresetIssue(preset_path, "theta_ci", preset_theta_ci, theta_ci))
        elif theta_ci is not None or preset_theta_ci is not None:
            issues.append(PresetIssue(preset_path, "theta_ci", preset_theta_ci, theta_ci))

        preset_beta = analysis_block.get("beta")
        if isinstance(beta, float) and isinstance(preset_beta, (int, float)):
            if not _relative_close(float(preset_beta), beta, rel_tol):
                issues.append(PresetIssue(preset_path, "beta", preset_beta, beta))
        elif beta is not None or preset_beta is not None:
            issues.append(PresetIssue(preset_path, "beta", preset_beta, beta))

        preset_beta_ci = _extract_sequence(analysis_block.get("beta_ci"))
        if beta_ci is not None and preset_beta_ci is not None:
            if len(beta_ci) == len(preset_beta_ci):
                for idx, (expected, actual) in enumerate(zip(preset_beta_ci, beta_ci)):
                    if not _relative_close(expected, actual, rel_tol):
                        issues.append(
                            PresetIssue(
                                preset_path,
                                f"beta_ci[{idx}]",
                                expected,
                                actual,
                            )
                        )
            else:
                issues.append(PresetIssue(preset_path, "beta_ci", preset_beta_ci, beta_ci))
        elif beta_ci is not None or preset_beta_ci is not None:
            issues.append(PresetIssue(preset_path, "beta_ci", preset_beta_ci, beta_ci))

        preset_r2 = analysis_block.get("logistic_r2")
        if isinstance(logistic_r2, float) and isinstance(preset_r2, (int, float)):
            if not _relative_close(float(preset_r2), logistic_r2, rel_tol):
                issues.append(PresetIssue(preset_path, "logistic_r2", preset_r2, logistic_r2))
        elif logistic_r2 is not None or preset_r2 is not None:
            issues.append(PresetIssue(preset_path, "logistic_r2", preset_r2, logistic_r2))

        preset_best = analysis_block.get("best_null_model")
        if best_name is not None:
            if preset_best != best_name:
                issues.append(PresetIssue(preset_path, "best_null_model", preset_best, best_name))
        elif preset_best is not None:
            issues.append(PresetIssue(preset_path, "best_null_model", preset_best, None))

        preset_delta_aic = analysis_block.get("delta_aic_best_null")
        if isinstance(best_delta_aic, float) and isinstance(preset_delta_aic, (int, float)):
            if not _relative_close(float(preset_delta_aic), best_delta_aic, rel_tol):
                issues.append(PresetIssue(preset_path, "delta_aic_best_null", preset_delta_aic, best_delta_aic))
        elif best_delta_aic is not None or preset_delta_aic is not None:
            issues.append(
                PresetIssue(preset_path, "delta_aic_best_null", preset_delta_aic, best_delta_aic)
            )

        preset_delta_r2 = analysis_block.get("delta_r2_best_null")
        if isinstance(best_delta_r2, float) and isinstance(preset_delta_r2, (int, float)):
            if not _relative_close(float(preset_delta_r2), best_delta_r2, rel_tol):
                issues.append(PresetIssue(preset_path, "delta_r2_best_null", preset_delta_r2, best_delta_r2))
        elif best_delta_r2 is not None or preset_delta_r2 is not None:
            issues.append(
                PresetIssue(preset_path, "delta_r2_best_null", preset_delta_r2, best_delta_r2)
            )

    return issues


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate simulator presets against logistic analysis exports so the"
            " resonance bridge stays aligned."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (defaults to the parent of this module).",
    )
    parser.add_argument(
        "--presets-dir",
        type=Path,
        default=None,
        help="Override the presets directory (defaults to simulator/presets).",
    )
    parser.add_argument(
        "--rel-tol",
        type=float,
        default=DEFAULT_REL_TOL,
        help="Relative tolerance for floating-point comparisons.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point for ``utf-preset-guard``."""

    parser = build_argument_parser()
    args = parser.parse_args(argv)
    issues = validate_presets(root=args.root, presets_dir=args.presets_dir, rel_tol=args.rel_tol)
    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("All simulator presets resonate with their analysis sources.")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
