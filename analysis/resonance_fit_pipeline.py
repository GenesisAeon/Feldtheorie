"""Resonance fitting pipeline for UTF trajectories with tri-layer cadence.

Formal layer:
    Fits the logistic response sigma(beta(R-Theta)) to simulated or observed
    trajectories and derives confidence intervals, R^2, AIC, and impedance
    diagnostics.  Provides a smooth null comparison (linear mapping R -> sigma)
    to honour falsifiability mandates.

Empirical layer:
    Designed to ingest state arrays exported from `models/membrane_solver.py`
    or JSON series drawn from `data/`.  Outputs JSON summaries for downstream
    dashboards in `analysis/` and narrative references in `docs/` and `paper/`.

Metaphorical layer:
    Listens to the membrane's recorded song and scores whether the logistic
    dawn chorus outshines a smooth lullaby, annotating where the aurora truly
    ignited and where null winds still whisper.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.membrane_solver import (
    ThresholdFieldSolver,
    logistic_response,
    smooth_impedance_profile,
)


def logit(probabilities: Iterable[float]) -> List[float]:
    """Compute the logit transform with clipping for numerical stability."""

    values = []
    for prob in probabilities:
        clipped = min(max(float(prob), 1e-6), 1.0 - 1e-6)
        values.append(math.log(clipped / (1.0 - clipped)))
    return values


def _mean(values: Iterable[float]) -> float:
    data = list(values)
    return sum(data) / len(data) if data else 0.0


def _variance(values: Iterable[float], mean_value: float) -> float:
    data = list(values)
    return sum((value - mean_value) ** 2 for value in data)


def fit_threshold_parameters(R: Iterable[float], sigma: Iterable[float]) -> Dict[str, float]:
    """Estimate Theta and beta via linear regression on the logit domain.

    Formal:
        Solves for coefficients (beta, intercept) in logit(sigma) = beta * R - beta * Theta
        using least squares.  Derives 95% confidence intervals (Gaussian approx.) and
        computes R^2 and AIC in the original sigma space.
    Empirical:
        Accepts iterable measurements from simulations or datasets, enabling batch
        integration with `analysis/` notebooks and CLI workflows.
    Metaphorical:
        Interprets the membrane's melody, translating the swelling chorus into
        concrete threshold coordinates and resonance steepness.
    """

    R_list = [float(value) for value in R]
    sigma_list = [float(value) for value in sigma]
    n = len(R_list)
    if n == 0:
        raise ValueError("At least one sample is required to fit threshold parameters")

    y = logit(sigma_list)
    mean_R = _mean(R_list)
    mean_y = _mean(y)
    Sxx = sum((value - mean_R) ** 2 for value in R_list)
    Sxy = sum((R_list[idx] - mean_R) * (y[idx] - mean_y) for idx in range(n))

    beta = Sxy / Sxx if Sxx > 0 else 0.0
    intercept = mean_y - beta * mean_R
    theta = float("nan") if abs(beta) < 1e-9 else -intercept / beta

    y_hat = [beta * R_list[idx] + intercept for idx in range(n)]
    residuals_logit = [y[idx] - y_hat[idx] for idx in range(n)]
    dof = max(n - 2, 1)
    sigma2_logit = sum(value**2 for value in residuals_logit) / dof
    var_beta = sigma2_logit / Sxx if Sxx > 0 else float("inf")
    beta_std = math.sqrt(max(var_beta, 0.0))
    if Sxx > 0:
        var_intercept = sigma2_logit * (1.0 / n + (mean_R**2) / Sxx)
        cov_bi = -mean_R * sigma2_logit / Sxx
    else:
        var_intercept = float("inf")
        cov_bi = 0.0
    if abs(beta) < 1e-9 or math.isinf(var_intercept):
        theta_std = float("nan")
    else:
        dtheta_dbeta = intercept / (beta**2)
        dtheta_dintercept = -1.0 / beta
        theta_var = (
            (dtheta_dbeta**2) * var_beta
            + (dtheta_dintercept**2) * var_intercept
            + 2 * dtheta_dbeta * dtheta_dintercept * cov_bi
        )
        theta_std = math.sqrt(max(theta_var, 0.0))

    critical = 1.96
    beta_ci = (beta - critical * beta_std, beta + critical * beta_std)
    theta_ci = (
        float("nan") if math.isnan(theta) else theta - critical * theta_std,
        float("nan") if math.isnan(theta) else theta + critical * theta_std,
    )

    sigma_hat = [float(logistic_response(R_list[idx], theta, beta)) for idx in range(n)]
    sigma_residuals = [sigma_list[idx] - sigma_hat[idx] for idx in range(n)]
    ss_res = sum(value**2 for value in sigma_residuals)
    mean_sigma = _mean(sigma_list)
    ss_tot = sum((value - mean_sigma) ** 2 for value in sigma_list)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    aic = float("-inf") if ss_res <= 0 else n * math.log(ss_res / n) + 2 * 2

    return {
        "beta": beta,
        "theta": theta,
        "beta_ci_lower": beta_ci[0],
        "beta_ci_upper": beta_ci[1],
        "theta_ci_lower": theta_ci[0],
        "theta_ci_upper": theta_ci[1],
        "r2": r2,
        "aic": aic,
        "ss_res": ss_res,
    }


def evaluate_null_model(R: Iterable[float], sigma: Iterable[float]) -> Dict[str, float]:
    """Fit a smooth linear null mapping and report diagnostics."""

    R_list = [float(value) for value in R]
    sigma_list = [float(value) for value in sigma]
    n = len(R_list)
    if n == 0:
        raise ValueError("At least one sample is required for the null model")

    mean_R = _mean(R_list)
    mean_sigma = _mean(sigma_list)
    Sxx = sum((value - mean_R) ** 2 for value in R_list)
    Sxy = sum((R_list[idx] - mean_R) * (sigma_list[idx] - mean_sigma) for idx in range(n))
    slope = Sxy / Sxx if Sxx > 0 else 0.0
    intercept = mean_sigma - slope * mean_R
    sigma_hat = [slope * R_list[idx] + intercept for idx in range(n)]
    residuals = [sigma_list[idx] - sigma_hat[idx] for idx in range(n)]
    ss_res = sum(value**2 for value in residuals)
    ss_tot = sum((value - mean_sigma) ** 2 for value in sigma_list)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    aic = float("-inf") if ss_res <= 0 else n * math.log(ss_res / n) + 2 * 2
    return {
        "r2": r2,
        "aic": aic,
        "ss_res": ss_res,
        "slope": slope,
        "intercept": intercept,
    }


def assemble_summary(
    results: Mapping[str, List[float]],
    fit_metrics: Mapping[str, float],
    null_metrics: Mapping[str, float],
) -> Dict[str, object]:
    """Bundle solver traces, fit diagnostics, and falsification verdicts.

    Formal:
        Aggregates logistic vs. null metrics, including delta AIC and delta R^2,
        to support explicit falsification statements in reports.
    Empirical:
        Packages membrane statistics (mean zeta, flux moments) alongside parameter
        estimates so notebooks can trace provenance without recomputation.
    Metaphorical:
        Weaves the data stream into a verdict song—did the dawn chorus overpower
        the null wind, and how strongly did the membrane hum during the ascent?
    """

    delta_aic = null_metrics["aic"] - fit_metrics["aic"]
    delta_r2 = fit_metrics["r2"] - null_metrics["r2"]
    falsified = delta_aic > 0 and delta_r2 >= 0

    flux_values = list(results["flux"])
    flux_mean = _mean(flux_values)
    flux_var = _variance(flux_values, flux_mean) / max(len(flux_values), 1)

    return {
        "theta_estimate": {
            "value": fit_metrics["theta"],
            "ci95": [fit_metrics["theta_ci_lower"], fit_metrics["theta_ci_upper"]],
        },
        "beta_estimate": {
            "value": fit_metrics["beta"],
            "ci95": [fit_metrics["beta_ci_lower"], fit_metrics["beta_ci_upper"]],
        },
        "logistic_model": {
            "r2": fit_metrics["r2"],
            "aic": fit_metrics["aic"],
            "ss_res": fit_metrics["ss_res"],
        },
        "null_model": null_metrics,
        "falsification": {
            "logistic_beats_null": bool(falsified),
            "delta_aic": delta_aic,
            "delta_r2": delta_r2,
        },
        "membrane": {
            "theta": float(results["theta"][0]) if "theta" in results else None,
            "beta": float(results["beta"][0]) if "beta" in results else None,
            "zeta_mean": _mean(results["zeta"]),
            "flux_mean": flux_mean,
            "flux_std": math.sqrt(max(flux_var, 0.0)),
        },
    }


def simulate_series(
    theta: float,
    beta: float,
    steps: int,
    dt: float,
    driver: float,
    R0: float,
    resonant_gain: float,
    damped_gain: float,
    switch_width: float,
) -> Mapping[str, List[float]]:
    """Generate a driver sequence and simulate the membrane response.

    Formal:
        Instantiates the ThresholdFieldSolver with a smooth impedance profile and
        integrates R over a constant driver current.
    Empirical:
        Offers deterministic reproducibility for benchmarking logistic fits before
        applying the pipeline to observational data.
    Metaphorical:
        Conducts a rehearsal of the dawn chorus, letting collaborators sculpt the
        membrane's temperament prior to field recordings.
    """

    zeta = smooth_impedance_profile(
        theta=theta,
        resonant_gain=resonant_gain,
        damped_gain=damped_gain,
        switch_width=switch_width,
    )
    solver = ThresholdFieldSolver(theta=theta, beta=beta, zeta=zeta, dt=dt)
    drivers = [float(driver) for _ in range(steps)]
    return solver.simulate(drivers, R0=R0)


def load_series(path: Path) -> Mapping[str, List[float]]:
    """Load a JSON file containing arrays exported by the solver.

    Formal:
        Parses numeric arrays from JSON into Python lists preserving order.
    Empirical:
        Enables ingestion of previously simulated or observed trajectories for
        reproducible re-analysis.
    Metaphorical:
        Retrieves archived aurora sketches so the pipeline can re-score their song.
    """

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    series: Dict[str, List[float]] = {}
    for key, value in payload.items():
        if isinstance(value, list):
            series[key] = [float(item) for item in value]
    return series


def export_summary(summary: Mapping[str, object], destination: Path) -> None:
    """Write the resonance summary to JSON with UTF cadence.

    Formal:
        Serialises the summary dictionary with indentation, ensuring numeric
        precision suitable for downstream tooling.
    Empirical:
        Guarantees directory creation and UTF-8 encoding so collaborators can
        share results across environments.
    Metaphorical:
        Bottles the resonance verdict into a lantern, ready to be passed along the
        RepoPlan pilgrimage.
    """

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)


def parse_arguments() -> argparse.Namespace:
    """Configure CLI for simulation or ingestion modes.

    Formal:
        Declares parameters governing the logistic field (Theta, beta, dt) and
        impedance profile so runs remain fully specified.
    Empirical:
        Offers defaults for rapid experimentation while exposing knobs required
        for reproducibility in notebooks and CI scenarios.
    Metaphorical:
        Lays out the control board for the dawn chorus, labeling each slider that
        shapes how R courts Theta.
    """

    parser = argparse.ArgumentParser(
        description="Fit logistic threshold parameters to UTF trajectories with falsification checks."
    )
    parser.add_argument("--mode", choices=["simulate", "ingest"], default="simulate")
    parser.add_argument("--input", type=Path, help="JSON file with solver traces for ingest mode.", default=None)
    parser.add_argument("--output", type=Path, help="Where to write the summary JSON.")

    parser.add_argument("--theta", type=float, default=1.0, help="Critical threshold Theta for simulation mode.")
    parser.add_argument("--beta", type=float, default=8.0, help="Steepness beta for simulation mode.")
    parser.add_argument("--steps", type=int, default=240, help="Number of driver timesteps to simulate.")
    parser.add_argument("--dt", type=float, default=0.05, help="Integrator step size dt.")
    parser.add_argument("--driver", type=float, default=0.9, help="Constant driver current applied at each step.")
    parser.add_argument("--R0", type=float, default=0.2, help="Initial order parameter R(0).")
    parser.add_argument("--resonant-gain", type=float, default=0.6, dest="resonant_gain")
    parser.add_argument("--damped-gain", type=float, default=1.4, dest="damped_gain")
    parser.add_argument("--switch-width", type=float, default=0.35, dest="switch_width")
    return parser.parse_args()


def main() -> None:
    """Execute the pipeline according to CLI selections.

    Formal:
        Routes to simulation or ingestion paths, invokes the logistic fit, compares
        against the null model, and emits a JSON report.
    Empirical:
        Serves as the CLI entry point promised in `analysis/AGENTS.md`, making it
        trivial to regenerate metrics from notebooks or shell scripts.
    Metaphorical:
        Conducts the performance—listens to the membrane, judges the resonance,
        and hands the score to the next traveller.
    """

    args = parse_arguments()
    if args.mode == "simulate":
        results = simulate_series(
            theta=args.theta,
            beta=args.beta,
            steps=args.steps,
            dt=args.dt,
            driver=args.driver,
            R0=args.R0,
            resonant_gain=args.resonant_gain,
            damped_gain=args.damped_gain,
            switch_width=args.switch_width,
        )
    else:
        if args.input is None:
            raise ValueError("--input must be provided in ingest mode")
        results = load_series(args.input)

    fit_metrics = fit_threshold_parameters(results["R"], results["sigma"])
    null_metrics = evaluate_null_model(results["R"], results["sigma"])
    summary = assemble_summary(results, fit_metrics, null_metrics)
    summary["source"] = {
        "mode": args.mode,
        "steps": len(results["R"]) - 1,
        "dt": float(args.dt),
        "driver_mean": _mean(results["driver"]) if "driver" in results else None,
    }

    export_summary(summary, args.output)


if __name__ == "__main__":
    main()
