r"""Coupled psi-phi threshold fit with logistic-vs-null falsification.

Formal stratum
==============
Generates a driver ramp, evolves the coupled membrane defined in
``models.coupled_threshold_field.CoupledThresholdField``, and fits the resulting
logistic response :math:`\sigma(\beta(R-\Theta))`.  A cubic polynomial serves as
the smooth null reference so we can report :math:`R^2`, AIC, confidence
intervals for :math:`\Theta` and :math:`\beta`, and log the impedance context
:math:`\zeta(R)`.

Empirical stratum
=================
Targets RepoPlan 2.0's request for a psi-phi coupling exemplar: the script saves
``analysis/results/coupled_field_threshold.json`` with the fitted parameters,
null-model deltas, integrated-information proxy, and metadata linking back to the
"Transdisziplinärer Schwellenfeld-Simulator" notes in `Docs/`.  The output aligns
with the cohort ledger conventions so `analysis/resonance_cohort_summary.py` can
ingest it without modification.

Metaphorical stratum
====================
Listens to the breath of gravitation: ``psi`` is the luminous inhalation,
``phi`` the semantic exhalation.  When the driver crosses the membrane's
threshold, the logistic bloom kindles and the null polynomial falls silent.  The
resulting JSON is a lantern for the Simulator manuscript now humming in `Docs/`.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from models import CoupledThresholdField, logistic_semantic_kernel, ramp_driver

RESULT_PATH = Path(__file__).resolve().parent / "results" / "coupled_field_threshold.json"


@dataclass
class LogisticFitResult:
    theta: float
    theta_ci: Tuple[float, float]
    beta: float
    beta_ci: Tuple[float, float]
    sigma_hat: np.ndarray
    residuals: np.ndarray
    metrics: Dict[str, float]


def generate_coupled_run(seed: int = 314159, steps: int = 360) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    kernel = logistic_semantic_kernel(theta=0.52, beta=5.4, resonance_bias=0.65, driver_weight=0.3)
    model = CoupledThresholdField(
        theta=0.52,
        beta=5.4,
        coupling=0.85,
        dt=0.04,
        coupling_kernel=kernel,
    )
    driver = ramp_driver(steps, start=0.1, stop=1.2, curvature=2.5)
    results = model.simulate(driver, R0=0.05, psi0=0.02, phi0=0.01)

    R = np.asarray(results["R"], dtype=float)[1:]
    sigma = np.asarray(results["sigma"], dtype=float)[1:]

    noise = rng.normal(scale=0.015, size=sigma.shape)
    sigma_noisy = np.clip(sigma + noise, 1e-4, 1 - 1e-4)

    return {
        "R": R,
        "sigma": sigma_noisy,
        "sigma_clean": sigma,
        "zeta": np.asarray(results["zeta"], dtype=float)[1:],
        "psi": np.asarray(results["psi"], dtype=float)[1:],
        "phi": np.asarray(results["phi"], dtype=float)[1:],
        "flux": np.asarray(results["flux"], dtype=float),
        "coupling": np.asarray(results["coupling_term"], dtype=float),
        "phi_proxy": model.integrated_information_proxy(
            np.asarray(results["psi"], dtype=float),
            np.asarray(results["phi"], dtype=float),
        )[1:],
        "model": model,
        "driver": driver,
        "time": np.asarray(results["t"], dtype=float)[1:],
    }


def fit_logistic(R: np.ndarray, sigma: np.ndarray) -> LogisticFitResult:
    eps = 1e-8
    clipped = np.clip(sigma, eps, 1 - eps)
    logit = np.log(clipped / (1 - clipped))
    X = np.column_stack([R, np.ones_like(R)])
    coeffs, residuals, _, _ = np.linalg.lstsq(X, logit, rcond=None)
    beta_hat, intercept_hat = coeffs
    theta_hat = -intercept_hat / beta_hat

    sigma_hat = 1.0 / (1.0 + np.exp(-beta_hat * (R - theta_hat)))
    residuals_sigma = sigma - sigma_hat

    n = len(R)
    k = 2
    ss_res = float(np.sum(residuals_sigma**2))
    ss_tot = float(np.sum((sigma - np.mean(sigma)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    aic = float(n * np.log(ss_res / n + eps) + 2 * k)

    # Variance-covariance for [beta, intercept]
    if n > k:
        logit_residuals = logit - X @ coeffs
        sigma_sq = float(np.sum(logit_residuals**2) / max(n - k, 1))
        xtx_inv = np.linalg.inv(X.T @ X)
        cov = sigma_sq * xtx_inv
    else:
        cov = np.zeros((2, 2))

    beta_var = float(cov[0, 0]) if cov.size else 0.0
    beta_ci = (
        beta_hat - 1.96 * np.sqrt(max(beta_var, 0.0)),
        beta_hat + 1.96 * np.sqrt(max(beta_var, 0.0)),
    )

    grad = np.array([intercept_hat / (beta_hat**2), -1.0 / beta_hat]) if beta_hat != 0 else np.array([0.0, 0.0])
    theta_var = float(grad.T @ cov @ grad) if cov.size else 0.0
    theta_ci = (
        theta_hat - 1.96 * np.sqrt(max(theta_var, 0.0)),
        theta_hat + 1.96 * np.sqrt(max(theta_var, 0.0)),
    )

    return LogisticFitResult(
        theta=float(theta_hat),
        theta_ci=theta_ci,
        beta=float(beta_hat),
        beta_ci=beta_ci,
        sigma_hat=sigma_hat,
        residuals=residuals_sigma,
        metrics={
            "r2": r2,
            "aic": aic,
            "ss_res": ss_res,
            "residual_mean": float(np.mean(residuals_sigma)),
            "residual_std": float(np.std(residuals_sigma, ddof=0)),
        },
    )


def cubic_null_model(R: np.ndarray, sigma: np.ndarray) -> Dict[str, float]:
    coeffs = np.polyfit(R, sigma, deg=3)
    sigma_hat = np.polyval(coeffs, R)
    sigma_hat = np.clip(sigma_hat, 0.0, 1.0)

    ss_res = float(np.sum((sigma - sigma_hat) ** 2))
    ss_tot = float(np.sum((sigma - np.mean(sigma)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    n = len(R)
    k = 4  # cubic polynomial parameters
    aic = float(n * np.log(ss_res / n + 1e-8) + 2 * k)

    return {
        "coefficients": coeffs.tolist(),
        "r2": r2,
        "aic": aic,
        "ss_res": ss_res,
    }


def assemble_payload(run: Dict[str, np.ndarray], fit: LogisticFitResult, null: Dict[str, float]) -> Dict[str, object]:
    model: CoupledThresholdField = run["model"]
    observables = model.export_observables(
        {
            "R": run["R"].tolist(),
            "sigma": run["sigma"].tolist(),
            "zeta": run["zeta"].tolist(),
            "flux": run["flux"].tolist(),
            "psi": run["psi"].tolist(),
            "phi": run["phi"].tolist(),
            "coupling_term": run["coupling"].tolist(),
        }
    )

    delta_aic = float(null["aic"] - fit.metrics["aic"])
    delta_r2 = float(fit.metrics["r2"] - null["r2"])

    return {
        "theta_estimate": {
            "value": fit.theta,
            "ci95": list(fit.theta_ci),
        },
        "beta_estimate": {
            "value": fit.beta,
            "ci95": list(fit.beta_ci),
        },
        "logistic_model": fit.metrics,
        "null_models": {
            "cubic_polynomial": null,
        },
        "falsification": {
            "logistic_beats_null": bool(delta_aic > 0),
            "comparisons": {
                "cubic_polynomial": {
                    "delta_aic": delta_aic,
                    "delta_r2": delta_r2,
                }
            },
        },
        "membrane": observables,
        "logistic_fit": {
            "sigma_hat": fit.sigma_hat.tolist(),
            "residuals": fit.residuals.tolist(),
        },
        "dataset": {
            "origin": "models/CoupledThresholdField synthetic run",
            "driver": {
                "description": "Sigmoid ramp inspired by Transdisziplinärer Schwellenfeld-Simulator notes",
                "values": run["driver"].tolist(),
            },
            "time": run["time"].tolist(),
            "measurements": [
                {"R": float(r), "sigma": float(s), "sigma_clean": float(c)}
                for r, s, c in zip(run["R"], run["sigma"], run["sigma_clean"])
            ],
            "coupling_term": run["coupling"].tolist(),
        },
        "impedance": {
            "trace": run["zeta"].tolist(),
            "mean": float(np.mean(run["zeta"])),
            "std": float(np.std(run["zeta"], ddof=0)),
        },
        "phi_proxy": {
            "series": run["phi_proxy"].tolist(),
            "mean": float(np.mean(run["phi_proxy"])),
            "peak": float(np.max(run["phi_proxy"])),
        },
        "meaning_coupling": {
            "series": run["coupling"].tolist(),
            "mean": float(np.mean(run["coupling"])),
            "std": float(np.std(run["coupling"], ddof=0)),
            "peak": float(np.max(run["coupling"])),
        },
        "tri_layer": {
            "formal": "Logit-linear regression for (Theta, beta) with cubic null falsifier.",
            "empirical": "Synthetic psi-phi run seeded from CoupledThresholdField; JSON ready for cohort ledger.",
            "metaphorical": "Gravitationsatem breath where semantic and physical gradients braid a luminous threshold.",
        },
    }


def main() -> None:
    run = generate_coupled_run()
    fit = fit_logistic(run["R"], run["sigma"])
    null = cubic_null_model(run["R"], run["sigma"])
    payload = assemble_payload(run, fit, null)

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)

    print(f"Saved coupled field resonance diagnostics to {RESULT_PATH.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
