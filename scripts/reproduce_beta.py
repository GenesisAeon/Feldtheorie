#!/usr/bin/env python3
"""Run a reproducible logistic threshold fit across a single dataset.

This script operationalises the UTAC logistic quartet (R, Theta, beta, zeta(R))
for a given CSV file.  It loads the control parameter R and response values,
fits the canonical logistic curve \sigma(\beta(R-\Theta)), contrasts it against
smooth null models, and reports the steepness beta together with ΔAIC, BIC,
RMSE, R^2, and bootstrap confidence intervals.  Outputs are stored as JSON so
analysis, simulator, and documentation layers can trace the same resonance.
"""
from __future__ import annotations

import argparse
import json
import logging
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from scipy.optimize import curve_fit

LOGGER = logging.getLogger(__name__)

RANDOM_SEED = 1337


def logistic(x: ArrayLike, beta: float, theta: float, L: float = 1.0) -> np.ndarray:
    """Canonical logistic response with optional upper asymptote L."""
    x = np.asarray(x, dtype=float)
    return L / (1.0 + np.exp(-beta * (x - theta)))


def _poly_fit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    coeffs = np.polyfit(x, y, deg=1)
    yhat = np.polyval(coeffs, x)
    return coeffs, yhat


def _exp_fit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mask = y > 0
    if not np.any(mask):
        raise ValueError("Exponential fit requires positive response values")
    coeffs = np.polyfit(x[mask], np.log(y[mask]), deg=1)
    yhat = np.exp(coeffs[1]) * np.exp(coeffs[0] * x)
    return coeffs, yhat


def _power_fit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mask = (x > 0) & (y > 0)
    if not np.any(mask):
        raise ValueError("Power-law fit requires positive control and response")
    coeffs = np.polyfit(np.log(x[mask]), np.log(y[mask]), deg=1)
    log_pred = coeffs[1] + coeffs[0] * np.log(np.clip(x, 1e-12, None))
    return coeffs, np.exp(log_pred)


def _rss(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    residuals = y_true - y_pred
    return float(np.sum(residuals**2))


def _aic_bic(y_true: np.ndarray, y_pred: np.ndarray, k: int) -> tuple[float, float]:
    n = y_true.size
    rss = _rss(y_true, y_pred)
    if rss <= 0:
        rss = 1e-12
    aic = n * np.log(rss / n) + 2 * k
    bic = n * np.log(rss / n) + k * np.log(n)
    return float(aic), float(bic)


def _r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = _rss(y_true, y_pred)
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot == 0:
        return 1.0
    return float(1 - ss_res / ss_tot)


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(_rss(y_true, y_pred) / y_true.size))


def fit_logistic(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    theta0 = np.median(x)
    beta0 = 3.5
    L0 = min(1.0, max(y)) if np.all((0 <= y) & (y <= 1)) else max(y)
    bounds = ([0.01, np.min(x), 0.1], [20.0, np.max(x), 5.0])
    params, cov = curve_fit(
        logistic,
        x,
        y,
        p0=(beta0, theta0, L0),
        bounds=bounds,
        maxfev=200_000,
    )
    return params, cov


def bootstrap_beta(
    x: np.ndarray,
    y: np.ndarray,
    n_resamples: int = 1000,
    rng: np.random.Generator | None = None,
) -> tuple[float, float]:
    if rng is None:
        rng = np.random.default_rng(RANDOM_SEED)

    betas: list[float] = []
    n = x.size
    for _ in range(n_resamples):
        indices = rng.integers(0, n, size=n)
        x_sample = x[indices]
        y_sample = y[indices]
        try:
            params, _ = fit_logistic(x_sample, y_sample)
        except Exception as exc:  # pragma: no cover - fallback when optimisation fails
            LOGGER.debug("bootstrap refit failed", exc_info=exc)
            continue
        betas.append(float(params[0]))

    if not betas:
        return float("nan"), float("nan")
    lower, upper = np.percentile(betas, [2.5, 97.5])
    return float(lower), float(upper)


@dataclass
class FitSummary:
    beta: float
    theta: float
    upper_asymptote: float
    r_squared: float
    rmse: float
    aic: float
    bic: float
    delta_aic_linear: float
    delta_aic_exponential: float
    delta_aic_power: float
    beta_ci_95: tuple[float, float]


def run_analysis(
    dataset_csv: Path,
    null_models: Iterable[str],
    bootstrap_samples: int,
    seed: int,
) -> Mapping[str, object]:
    frame = pd.read_csv(dataset_csv)
    missing = {"R", "response"} - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    x = frame["R"].to_numpy(dtype=float)
    y = frame["response"].to_numpy(dtype=float)

    params, _ = fit_logistic(x, y)
    beta, theta, L = params
    logistic_pred = logistic(x, beta, theta, L)
    logistic_aic, logistic_bic = _aic_bic(y, logistic_pred, k=3)

    r2 = _r_squared(y, logistic_pred)
    rmse = _rmse(y, logistic_pred)

    rng = np.random.default_rng(seed)
    ci_low, ci_high = bootstrap_beta(x, y, n_resamples=bootstrap_samples, rng=rng)

    null_outputs: dict[str, dict[str, float]] = {}
    for model in null_models:
        model = model.lower()
        if model == "linear":
            coeffs, yhat = _poly_fit(x, y)
            k = len(coeffs)
        elif model == "exponential":
            coeffs, yhat = _exp_fit(x, y)
            k = len(coeffs)
        elif model == "power":
            coeffs, yhat = _power_fit(x, y)
            k = len(coeffs)
        else:
            raise ValueError(f"Unsupported null model: {model}")

        aic, bic = _aic_bic(y, yhat, k=k)
        null_outputs[model] = {
            "parameters": [float(c) for c in coeffs],
            "aic": aic,
            "bic": bic,
            "delta_aic": float(aic - logistic_aic),
            "delta_bic": float(bic - logistic_bic),
        }

    summary = FitSummary(
        beta=float(beta),
        theta=float(theta),
        upper_asymptote=float(L),
        r_squared=r2,
        rmse=rmse,
        aic=logistic_aic,
        bic=logistic_bic,
        delta_aic_linear=null_outputs.get("linear", {}).get("delta_aic", float("nan")),
        delta_aic_exponential=null_outputs.get("exponential", {}).get("delta_aic", float("nan")),
        delta_aic_power=null_outputs.get("power", {}).get("delta_aic", float("nan")),
        beta_ci_95=(ci_low, ci_high),
    )

    return {
        "dataset": dataset_csv.name,
        "records": len(frame),
        "control_parameter": "R",
        "order_parameter": "response",
        "logistic_parameters": asdict(summary),
        "null_models": null_outputs,
        "logistic_quartet": {
            "R": "control parameter drawn from dataset column R",
            "Theta": summary.theta,
            "beta": summary.beta,
            "zeta(R)": "implicit impedance encoded via dataset preprocessing",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fit the UTAC logistic response to a dataset and report ΔAIC versus "
            "smooth null models."
        )
    )
    parser.add_argument(
        "--csv",
        type=Path,
        required=True,
        help="CSV file containing columns R and response.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Where to store the JSON summary.",
    )
    parser.add_argument(
        "--null-models",
        nargs="+",
        default=["linear", "power", "exponential"],
        help="Null models to compare (subset of linear, power, exponential).",
    )
    parser.add_argument(
        "--bootstrap-samples",
        type=int,
        default=1000,
        help="Number of bootstrap resamples for beta confidence intervals.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help="Random seed for bootstrap resampling.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_analysis(
        dataset_csv=args.csv,
        null_models=args.null_models,
        bootstrap_samples=args.bootstrap_samples,
        seed=args.seed,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2))
    print(f"[OK] wrote {args.out}")


if __name__ == "__main__":
    main()
