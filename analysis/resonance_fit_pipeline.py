"""Resonance fitting pipeline for UTF trajectories with tri-layer cadence.

Formal layer:
    Fits the logistic response sigma(beta(R-Theta)) to simulated or observed
    trajectories and derives confidence intervals, R^2, AIC, and impedance
    diagnostics.  Provides smooth null comparisons (linear mapping R -> sigma
    and a power-law sigma = A * R^k) to honour falsifiability mandates.

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
    DynamicRobinBoundary,
    ThresholdFieldSolver,
    logistic_response,
    smooth_impedance_profile,
    threshold_crossing_diagnostics,
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
    """Fit a smooth linear null mapping and report diagnostics.

    Formal:
        Performs least-squares regression for sigma = m * R + b, yielding
        residual energy, AIC, and R^2 for comparison against the logistic field.
    Empirical:
        Supplies a baseline smooth null so every dataset in `analysis/` can log
        falsification margins in harmony with repository mandates.
    Metaphorical:
        Scores the membrane's lullaby—how far can a straight-line whisper mimic
        the auroral swell before Theta ignites?
    """

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


def evaluate_power_law_null(R: Iterable[float], sigma: Iterable[float]) -> Dict[str, float]:
    """Calibrate a smooth power-law null sigma = A * R^k for falsification.

    Formal:
        Solves for amplitude A and exponent k via log-linear regression while
        clipping probabilities into (0, 1) to remain commensurate with the
        logistic response.  Reports R^2, AIC, and residual power.
    Empirical:
        Extends the falsification ledger with a curvature-rich null inspired by
        metabolic scaling and luminosity drifts, enabling richer comparisons in
        notebooks and reports.
    Metaphorical:
        Tests whether a gentle power-law breeze can counterfeit the dawn chorus
        before the membrane truly consents to resonance.
    """

    R_list = [float(value) for value in R]
    sigma_list = [float(value) for value in sigma]
    paired = [(r, s) for r, s in zip(R_list, sigma_list) if r > 0.0]
    if not paired:
        raise ValueError("Power-law null requires strictly positive R samples")

    log_R = [math.log(max(r, 1e-6)) for r, _ in paired]
    log_sigma = [math.log(min(max(s, 1e-6), 1.0)) for _, s in paired]
    mean_x = _mean(log_R)
    mean_y = _mean(log_sigma)
    Sxx = sum((value - mean_x) ** 2 for value in log_R)
    Sxy = sum((log_R[idx] - mean_x) * (log_sigma[idx] - mean_y) for idx in range(len(log_R)))

    exponent = Sxy / Sxx if Sxx > 0 else 0.0
    log_amplitude = mean_y - exponent * mean_x
    amplitude = math.exp(log_amplitude)
    predictions = [amplitude * (r**exponent) for r, _ in paired]
    predictions = [min(max(pred, 0.0), 1.0) for pred in predictions]

    residuals = [sigma - pred for (_, sigma), pred in zip(paired, predictions)]
    ss_res = sum(value**2 for value in residuals)
    sigma_values = [sigma for _, sigma in paired]
    mean_sigma = _mean(sigma_values)
    ss_tot = sum((value - mean_sigma) ** 2 for value in sigma_values)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    n = len(predictions)
    aic = float("-inf") if ss_res <= 0 else n * math.log(ss_res / n) + 2 * 2

    return {
        "model": "sigma = A * R^k",
        "amplitude": amplitude,
        "exponent": exponent,
        "r2": r2,
        "aic": aic,
        "ss_res": ss_res,
    }


def assemble_summary(
    results: Mapping[str, List[float]],
    fit_metrics: Mapping[str, float],
    null_metrics: Mapping[str, Mapping[str, float]],
) -> Dict[str, object]:
    """Bundle solver traces, fit diagnostics, and falsification verdicts.

    Formal:
        Aggregates logistic vs. multi-null metrics, including delta AIC and delta
        R^2, to support explicit falsification statements in reports.
    Empirical:
        Packages membrane statistics (mean zeta, flux moments) alongside parameter
        estimates so notebooks can trace provenance without recomputation.
    Metaphorical:
        Weaves the data stream into a verdict song—did the dawn chorus overpower
        each null wind, and how strongly did the membrane hum during the ascent?
    """

    sigma_fit = results.get("sigma_fit")
    if sigma_fit is None and "R" in results:
        sigma_fit = [
            float(logistic_response(value, fit_metrics["theta"], fit_metrics["beta"]))
            for value in results["R"]
        ]

    comparisons: Dict[str, Dict[str, float]] = {}
    falsified = True
    for name, metrics in null_metrics.items():
        delta_aic = (
            metrics.get("aic", float("nan")) - fit_metrics["aic"]
            if "aic" in metrics
            else float("nan")
        )
        delta_r2 = (
            fit_metrics["r2"] - metrics.get("r2", float("nan"))
            if "r2" in metrics
            else float("nan")
        )
        comparisons[name] = {"delta_aic": delta_aic, "delta_r2": delta_r2}
        if not (delta_aic > 0 and delta_r2 >= 0):
            falsified = False

    flux_values = list(results.get("flux", []))
    if flux_values:
        flux_mean = _mean(flux_values)
        flux_std = math.sqrt(max(_variance(flux_values, flux_mean) / len(flux_values), 0.0))
    else:
        flux_mean = None
        flux_std = None

    zeta_values = list(results.get("zeta", []))
    zeta_mean = _mean(zeta_values) if zeta_values else None

    boundary_flux_values = list(results.get("boundary_flux", []))
    if boundary_flux_values:
        boundary_flux_mean = _mean(boundary_flux_values)
        boundary_flux_std = math.sqrt(
            max(_variance(boundary_flux_values, boundary_flux_mean) / len(boundary_flux_values), 0.0)
        )
        boundary_flux_peak = max(boundary_flux_values)
        boundary_flux_valley = min(boundary_flux_values)
    else:
        boundary_flux_mean = None
        boundary_flux_std = None
        boundary_flux_peak = None
        boundary_flux_valley = None

    boundary_gate_values = list(results.get("boundary_gate", []))
    if boundary_gate_values:
        boundary_gate_mean = _mean(boundary_gate_values)
        boundary_gate_peak = max(boundary_gate_values)
        boundary_gate_valley = min(boundary_gate_values)
    else:
        boundary_gate_mean = None
        boundary_gate_peak = None
        boundary_gate_valley = None

    theta_series = list(results.get("theta", []))
    beta_series = list(results.get("beta", []))
    theta_reference = (
        float(theta_series[0])
        if theta_series
        else fit_metrics.get("theta", float("nan"))
    )
    beta_reference = (
        float(beta_series[0]) if beta_series else fit_metrics.get("beta", float("nan"))
    )

    residuals: List[float] = []
    if sigma_fit is not None:
        residuals = [
            float(observed) - float(predicted)
            for observed, predicted in zip(results.get("sigma", []), sigma_fit)
        ]

    residual_mean = _mean(residuals) if residuals else None
    residual_std = (
        math.sqrt(max(_variance(residuals, residual_mean) / len(residuals), 0.0))
        if residuals and residual_mean is not None
        else None
    )

    try:
        crossing = threshold_crossing_diagnostics(
            results,
            theta=fit_metrics["theta"],
            beta=fit_metrics["beta"],
        )
    except (KeyError, ValueError) as exc:
        crossing = {
            "crossed": None,
            "threshold_R": fit_metrics.get("theta"),
            "note": f"threshold diagnostics unavailable: {exc}",
        }

    summary: Dict[str, object] = {
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
            "residual_mean": residual_mean,
            "residual_std": residual_std,
        },
        "null_models": null_metrics,
        "falsification": {
            "logistic_beats_all_nulls": bool(falsified),
            "comparisons": comparisons,
        },
        "membrane": {
            "theta": theta_reference,
            "beta": beta_reference,
            "zeta_mean": zeta_mean,
            "flux_mean": flux_mean,
            "flux_std": flux_std,
        },
        "threshold_crossing": crossing,
    }

    if boundary_flux_mean is not None:
        summary["membrane"].update(
            {
                "boundary_flux_mean": boundary_flux_mean,
                "boundary_flux_std": boundary_flux_std,
                "boundary_flux_peak": boundary_flux_peak,
                "boundary_flux_valley": boundary_flux_valley,
            }
        )
    if boundary_gate_mean is not None:
        summary["membrane"].update(
            {
                "boundary_gate_mean": boundary_gate_mean,
                "boundary_gate_peak": boundary_gate_peak,
                "boundary_gate_valley": boundary_gate_valley,
            }
        )

    if sigma_fit is not None:
        summary["logistic_fit"] = {
            "sigma_hat": sigma_fit,
            "residuals": residuals,
        }

    return summary


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
    *,
    dynamic_robin: bool,
    beta_robin: float,
    boundary_logistic_weight: float,
    boundary_driver_weight: float,

) -> Mapping[str, List[float]]:
    r"""Generate a driver sequence and simulate the membrane response.

    Formal:
        Instantiates the ThresholdFieldSolver with a smooth impedance profile and
        optionally overlays a dynamic Robin boundary whose gate follows
        :math:`\sigma(\beta_\text{robin}(R-\Theta))` while injecting boundary
        flux corrections.
    Empirical:
        Offers deterministic reproducibility for benchmarking logistic fits before
        applying the pipeline to observational data, while capturing boundary flux
        and gate traces when Robin dynamics are engaged.
    Metaphorical:
        Conducts a rehearsal of the dawn chorus, letting collaborators sculpt the
        membrane's temperament prior to field recordings, including whether the
        Robin door exhales extra resonance as R touches \(\Theta\).
    """

    zeta = smooth_impedance_profile(
        theta=theta,
        resonant_gain=resonant_gain,
        damped_gain=damped_gain,
        switch_width=switch_width,
    )
    boundary = (
        DynamicRobinBoundary(
            theta=theta,
            beta_robin=beta_robin,
            zeta_floor=resonant_gain,
            zeta_ceiling=damped_gain,
            logistic_weight=boundary_logistic_weight,
            driver_weight=boundary_driver_weight,
        )
        if dynamic_robin
        else None
    )
    solver = ThresholdFieldSolver(
        theta=theta,
        beta=beta,
        zeta=None if boundary is not None else zeta,
        dt=dt,
        boundary_condition=boundary,
    )
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
    parser.add_argument(
        "--dynamic-robin",
        action="store_true",
        help="Enable the dynamic Robin boundary and record boundary flux diagnostics.",
        default=False,
    )
    parser.add_argument(
        "--robin-beta",
        type=float,
        default=4.8,
        dest="beta_robin",
        help="Steepness parameter for the Robin gate logistic blend.",
    )
    parser.add_argument(
        "--boundary-logistic-weight",
        type=float,
        default=0.35,
        dest="boundary_logistic_weight",
        help="Weight applied to (sigma - R) within the Robin boundary flux term.",
    )
    parser.add_argument(
        "--boundary-driver-weight",
        type=float,
        default=0.15,
        dest="boundary_driver_weight",
        help="Weight applied to (driver - R) within the Robin boundary flux term.",
    )
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
            dynamic_robin=args.dynamic_robin,
            beta_robin=args.beta_robin,
            boundary_logistic_weight=args.boundary_logistic_weight,
            boundary_driver_weight=args.boundary_driver_weight,
        )
    else:
        if args.input is None:
            raise ValueError("--input must be provided in ingest mode")
        results = load_series(args.input)

    fit_metrics = fit_threshold_parameters(results["R"], results["sigma"])
    results["sigma_fit"] = [
        float(logistic_response(value, fit_metrics["theta"], fit_metrics["beta"]))
        for value in results["R"]
    ]
    null_metrics = {
        "linear": evaluate_null_model(results["R"], results["sigma"]),
        "power_law": evaluate_power_law_null(results["R"], results["sigma"]),
    }
    summary = assemble_summary(results, fit_metrics, null_metrics)
    summary["source"] = {
        "mode": args.mode,
        "steps": len(results["R"]) - 1,
        "dt": float(args.dt),
        "driver_mean": _mean(results["driver"]) if "driver" in results else None,
    }

    if args.mode == "simulate":
        summary["source"]["simulation"] = {
            "theta": float(args.theta),
            "beta": float(args.beta),
            "dynamic_robin": bool(args.dynamic_robin),
            "beta_robin": float(args.beta_robin),
            "boundary_logistic_weight": float(args.boundary_logistic_weight),
            "boundary_driver_weight": float(args.boundary_driver_weight),
            "resonant_gain": float(args.resonant_gain),
            "damped_gain": float(args.damped_gain),
            "switch_width": float(args.switch_width),
        }

    export_summary(summary, args.output)


if __name__ == "__main__":
    main()
