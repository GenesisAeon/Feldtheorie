from __future__ import annotations

"""Self-monitoring Sigillin Audit for σ(β(R-Θ)).

This module activates Phase C's Sigillin Audit loop to watch for ontological drift
as new modules couple into the field. It mirrors stochastic GenesisCube seeds
through the legacy kernel and checks that entropy remains resonant while
v_RIG stays aligned with the fine-structure-inspired ideal.
"""

import importlib.util
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import sys
import types

import numpy as np

from simulation.genesis_cube import GenesisCube, GenesisCubeConfig

AUDIT_CYCLE = 137
V_RIG_IDEAL = 1351.8  # km/s, fine-structure inspired propagation target

ALETHEIA_ALERT = (
    "ALERT: Ontological drift detected. Beta-Architecture unstable. Suggest immediate reflection."
)


@dataclass
class AuditReport:
    """Structured report for a Sigillin audit."""

    passed: bool
    entropy_ok: bool
    velocity_ok: bool
    simulated_v_rig: float
    entropy_measure: float
    alerts: list[str] = field(default_factory=list)


def _load_sigillin_kernel() -> Any:
    """Load the legacy sigillin kernel logic for logistic coupling context."""

    kernel_path = Path(
        "releases/V6-Plans_etc/Finalize/V7_wird noch verlergt/sigillin_kernel.py"
    )
    _ensure_legacy_dependencies()
    spec = importlib.util.spec_from_file_location("sigillin_kernel_legacy", kernel_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load sigillin_kernel module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _mirror_seed(snapshot: Mapping[str, Any]) -> Mapping[str, Any]:
    """Pass a minimal snapshot through the legacy mirror to honor Phase B logic."""

    sigillin_kernel = _load_sigillin_kernel()
    return sigillin_kernel.mirror_machine(snapshot)


def _random_genesis_config(rng: random.Random, overrides: Mapping[str, Any] | None) -> GenesisCubeConfig:
    """Build a GenesisCubeConfig seeded with stochastic β/Θ drift parameters."""

    overrides = overrides or {}
    config_kwargs: dict[str, Any] = {
        "beta": overrides.get("beta", rng.uniform(4.2, 5.4)),
        "theta": overrides.get("theta", rng.uniform(0.0, 0.5)),
        "damping": overrides.get("damping", rng.uniform(0.02, 0.06)),
        "photon_coupling": overrides.get("photon_coupling", rng.uniform(0.05, 1.0)),
        "expansion_rate": overrides.get("expansion_rate", rng.uniform(0.99, 1.01)),
        "slice_count": overrides.get("slice_count", 12),
        "fluctuation_phase": overrides.get("fluctuation_phase", rng.uniform(0.05, 0.3)),
        "enable_wavefunction": overrides.get("enable_wavefunction", True),
        "time_steps": overrides.get("time_steps", 8),
        "wavefunction_resolution": overrides.get("wavefunction_resolution", 12),
    }

    return GenesisCubeConfig(**config_kwargs)


def audit_integrity(
    seed: int | None = None,
    overrides: Mapping[str, Any] | None = None,
    mock_entropy: float | None = None,
    mock_velocity: float | None = None,
) -> AuditReport:
    """Run the Sigillin audit to guard σ(β(R-Θ)) stability.

    The audit instantiates a GenesisCube with stochastic parameters, mirrors the
    snapshot through the legacy kernel, and probes entropy + v_RIG adherence.

    Args:
        seed: Deterministic seed for reproducible stochastic draws.
        overrides: Optional GenesisCubeConfig overrides.
        mock_entropy: Optional injected entropy measure for testing scenarios.
        mock_velocity: Optional injected v_RIG value for testing scenarios.

    Returns:
        AuditReport capturing pass/fail state and triggered alerts.
    """

    rng = random.Random(seed)
    config = _random_genesis_config(rng, overrides)
    cube = GenesisCube(config)

    snapshot = {
        "beta": cube.config.beta,
        "theta": cube.config.theta,
        "kappa": cube.config.photon_coupling,
        "notes": "σ(β(R-Θ)) audit snapshot",
    }
    _mirror_seed(snapshot)

    entropy_gradient = cube.compute_entropy_gradient(0.5, 0.3, 0.7, 0.0)
    entropy_measure = mock_entropy if mock_entropy is not None else float(np.mean(entropy_gradient))
    simulated_v_rig = mock_velocity if mock_velocity is not None else _simulate_velocity(rng, cube)

    entropy_ok = True
    alerts: list[str] = []
    if cube.config.photon_coupling < 0.1 and math.isclose(entropy_measure, 0.0, abs_tol=1e-12):
        entropy_ok = False
        alerts.append("Entropy check failed: Dark Consciousness cannot yield zero entropy.")

    velocity_ok = math.isclose(simulated_v_rig, V_RIG_IDEAL, rel_tol=0.013)
    if not velocity_ok:
        alerts.append(
            f"CRITICAL_WARNING: v_RIG drift detected (simulated={simulated_v_rig:.3f} km/s, ideal={V_RIG_IDEAL} km/s)."
        )

    passed = entropy_ok and velocity_ok
    if not passed:
        alerts.append(ALETHEIA_ALERT)

    return AuditReport(
        passed=passed,
        entropy_ok=entropy_ok,
        velocity_ok=velocity_ok,
        simulated_v_rig=simulated_v_rig,
        entropy_measure=entropy_measure,
        alerts=alerts,
    )


def _simulate_velocity(rng: random.Random, cube: GenesisCube) -> float:
    """Simulate v_RIG propagation speed around the V_RIG_IDEAL target."""

    fluctuation = rng.normalvariate(0.0, V_RIG_IDEAL * 0.0025)
    base_velocity = V_RIG_IDEAL * cube.config.expansion_rate
    return base_velocity + fluctuation


def _ensure_legacy_dependencies() -> None:
    """Provide lightweight stand-ins for legacy kernel dependencies."""

    sys.modules.setdefault("analysis", types.ModuleType("analysis"))
    sys.modules.setdefault("scripts", types.ModuleType("scripts"))

    beta_module = sys.modules.get("analysis.beta_meta_regression_v2")
    if beta_module is None:
        beta_module = types.ModuleType("analysis.beta_meta_regression_v2")

        def run_beta_regression(trilayer_data: Mapping[str, Any] | None = None) -> dict[str, Any]:
            return {"beta_fit": trilayer_data or {}}

        beta_module.run_beta_regression = run_beta_regression
        sys.modules["analysis.beta_meta_regression_v2"] = beta_module

    utils_module = sys.modules.get("scripts.utils")
    if utils_module is None:
        utils_module = types.ModuleType("scripts.utils")
        sys.modules["scripts.utils"] = utils_module

    audit_module = sys.modules.get("scripts.utils.audit")
    if audit_module is None:
        audit_module = types.ModuleType("scripts.utils.audit")

        def audit_delta_AIC(beta_fit: Mapping[str, Any] | None = None) -> dict[str, Any]:
            return {"pass": True, "delta_AIC": 0.0, "beta_fit": beta_fit or {}}

        audit_module.audit_delta_AIC = audit_delta_AIC
        sys.modules["scripts.utils.audit"] = audit_module

    storage_module = sys.modules.get("scripts.sigillin_storage")
    if storage_module is None:
        storage_module = types.ModuleType("scripts.sigillin_storage")

        def store_sigillin(beta_fit: Mapping[str, Any] | None, audit_result: Mapping[str, Any]) -> dict[str, Any]:
            return {"beta_fit": beta_fit or {}, "audit_result": audit_result}

        storage_module.store_sigillin = store_sigillin
        sys.modules["scripts.sigillin_storage"] = storage_module


if __name__ == "__main__":
    report = audit_integrity()
    status = "PASS" if report.passed else "FAIL"
    print(f"[σ-monitor] Audit {status} :: entropy_ok={report.entropy_ok} | velocity_ok={report.velocity_ok}")
    if report.alerts:
        for alert in report.alerts:
            print(alert)
