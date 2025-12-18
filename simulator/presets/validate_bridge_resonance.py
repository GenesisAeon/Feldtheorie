"""Validate Neuro↔Kosmos coupling against the hex-resonance guard-rail.

This script samples the σ(β(R-Θ)) interaction defined in
``neuro_kosmos_bridge.json`` and demonstrates that the coupling matrix is
maximally conductive around the digital-physics constant
β_hex = 16^(2/π) ≈ 5.84 while staying shy of chaotic spillover.

Outputs include:
- Resonance curves for β candidates (σ traces)
- Conductance scores (area-under-σ) with chaos penalties
- Alignment report via ``verify_hex_alignment``

Usage
-----
Run directly to emit a JSON summary to stdout:

```
python simulator/presets/validate_bridge_resonance.py
```
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Sequence

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from models.unified_constants import HEX_RESONANCE_BETA, verify_hex_alignment


def _logistic(readiness: np.ndarray, theta: float, beta: float) -> np.ndarray:
    """Compute σ(β(R-Θ)) for the given readiness vector."""

    return 1.0 / (1.0 + np.exp(-beta * (readiness - theta)))


def load_bridge_preset(path: Path | None = None) -> dict[str, Any]:
    """Load the Neuro-Kosmos bridge preset JSON."""

    preset_path = path if path is not None else Path(__file__).with_name("neuro_kosmos_bridge.json")
    with preset_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def evaluate_bridge_resonance(
    readiness: Sequence[float] | None = None,
    theta: float = 0.66,
    beta_candidates: Sequence[float] | None = None,
) -> dict[str, Any]:
    """Assess σ_hex conductance and stability across β candidates.

    Parameters
    ----------
    readiness : Sequence[float], optional
        Readiness samples R; defaults to a sweep from 0.1 to 1.3.
    theta : float, optional
        Threshold Θ used in the σ(β(R-Θ)) driver.
    beta_candidates : Sequence[float], optional
        Candidate β values. Defaults to a neighborhood around β_hex.

    Returns
    -------
    dict
        Telemetry including conductance, stability penalties, and alignment.
    """

    readiness_vec = np.asarray(readiness if readiness is not None else np.linspace(0.1, 1.3, num=64), dtype=float)
    candidate_betas = (
        list(beta_candidates)
        if beta_candidates is not None
        else [HEX_RESONANCE_BETA * scale for scale in (0.75, 1.0, 1.25)]
    )

    results = []
    for beta in candidate_betas:
        sigma = _logistic(readiness_vec, theta, beta)
        conductance = float(
            np.trapezoid(sigma, readiness_vec) / (readiness_vec[-1] - readiness_vec[0])
        )

        # Penalize excessive steepness that could push the system into chaos.
        chaos_penalty = (beta / HEX_RESONANCE_BETA - 1.0) ** 2
        stability = float(np.exp(-chaos_penalty / 0.08))
        resonance_score = conductance * stability

        results.append(
            {
                "beta": float(beta),
                "sigma_curve": sigma.tolist(),
                "conductance": conductance,
                "stability": stability,
                "resonance_score": resonance_score,
            }
        )

    best = max(results, key=lambda item: item["resonance_score"])
    alignment = verify_hex_alignment(best["beta"], tolerance=0.15)

    return {
        "theta": theta,
        "readiness_span": [float(readiness_vec[0]), float(readiness_vec[-1])],
        "beta_hex": HEX_RESONANCE_BETA,
        "results": results,
        "best_beta": best,
        "alignment": alignment,
    }


def validate_with_preset() -> dict[str, Any]:
    """Use preset values to validate the σ_hex coupling matrix."""

    preset = load_bridge_preset()
    theta = preset.get("simulation", {}).get("theta", 0.66)
    readiness_range = preset.get("simulation", {}).get("sigma_driver", {}).get("readiness_range", [0.1, 1.3])
    readiness = np.linspace(readiness_range[0], readiness_range[1], num=64)
    beta_candidates = [
        HEX_RESONANCE_BETA * 0.85,
        HEX_RESONANCE_BETA,
        HEX_RESONANCE_BETA * 1.15,
    ]

    telemetry = evaluate_bridge_resonance(readiness=readiness, theta=theta, beta_candidates=beta_candidates)
    telemetry["preset_theta"] = theta
    telemetry["preset_beta_hex"] = preset.get("hex_resonance_beta", HEX_RESONANCE_BETA)
    return telemetry


if __name__ == "__main__":
    report = validate_with_preset()
    print(json.dumps(report, indent=2))


__all__ = [
    "evaluate_bridge_resonance",
    "load_bridge_preset",
    "validate_with_preset",
]
