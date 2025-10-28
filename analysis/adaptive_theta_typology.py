"""Tri-layer synthesis of adaptive threshold typologies across system classes.

Formal layer:
    Encodes the adaptive threshold function
        Theta(t) = Theta_0 + alpha S_system(t) + beta_c C_sub(t) + gamma E(t) + sum_i delta_i Delta_i(t)
    and generates synthetic observations of the logistic response sigma(beta (R-Theta(t))).
    Contrasts a dynamic-threshold description (k=5 parameters) with a static logistic
    fit (k=2) and smooth null models (linear, power-law), reporting R^2 and AIC so
    falsifiability remains explicit.

Empirical layer:
    Provides a CLI workflow that writes analysis/results/dynamic_theta_tests.json.
    Each scenario instantiates domain-specific complexity traces (insects, neural,
    AI curriculum) to illustrate how minimal interference margins vary with
    substructure density and environmental modulation. The output is ready to be
    cited from docs/meta_schwellen_systemtypen.md and downstream notebooks.

Metaphorical layer:
    Listens for the membrane's meta-memory: how each system type remembers past
    resonances by nudging Theta ever so slightly. When the interference margin
    narrows, the dawn chorus bends—sometimes to welcome a swarm, sometimes to
    guard a cortex from burning bright.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence


@dataclass
class ContextSeries:
    """Container for adaptive-threshold traces."""

    R: List[float]
    theta: List[float]
    sigma_observed: List[float]
    sigma_dynamic: List[float]
    sigma_static: List[float]
    S_system: List[float]
    C_sub: List[float]
    E_context: List[float]
    delta_trace: List[float]


@dataclass
class AdaptiveScenario:
    """Descriptor for a system-type specific adaptive threshold experiment."""

    name: str
    theta0: float
    beta: float
    alpha: float
    beta_c: float
    gamma: float
    delta_magnitude: float
    noise: float

    def _profiles(self, steps: int) -> Dict[str, List[float]]:
        """Generate complexity traces tailored to the scenario."""

        S: List[float] = []
        C: List[float] = []
        E: List[float] = []
        delta_events: List[float] = []
        phase_advance = {
            "biosphere": 0.0,
            "cognition": 0.25,
            "ai": 0.5,
        }
        tag = "biosphere"
        if "neural" in self.name or "cortex" in self.name:
            tag = "cognition"
        elif "ai" in self.name or "curriculum" in self.name:
            tag = "ai"
        offset = phase_advance[tag]
        for idx in range(steps):
            tau = idx / (steps - 1)
            s_wave = 0.6 + 0.35 * math.sin(2.0 * math.pi * (tau + offset))
            c_wave = 0.4 + 0.45 * math.sin(2.0 * math.pi * (tau + 0.35 + offset))
            e_wave = 0.2 + 0.3 * math.cos(2.0 * math.pi * (tau * 1.5 + offset))
            S.append(s_wave)
            C.append(c_wave)
            E.append(e_wave)
            if tag == "biosphere":
                delta_events.append(self.delta_magnitude if tau > 0.55 else 0.0)
            elif tag == "cognition":
                delta_events.append(self.delta_magnitude * math.exp(-10.0 * (tau - 0.5) ** 2))
            else:
                delta_events.append(self.delta_magnitude if 0.3 < tau < 0.6 else 0.0)
        return {"S": S, "C": C, "E": E, "delta": delta_events}

    def generate(self, steps: int = 64, seed: int = 42) -> ContextSeries:
        """Simulate adaptive-threshold logistic observations."""

        rng = random.Random(seed)
        traces = self._profiles(steps)
        R_values: List[float] = []
        theta_values: List[float] = []
        sigma_obs: List[float] = []
        sigma_dyn: List[float] = []
        sigma_static: List[float] = []

        for idx in range(steps):
            tau = idx / (steps - 1)
            R = self.theta0 + 0.8 * math.sin(math.pi * (tau - 0.5)) + 0.35 * tau
            theta_t = (
                self.theta0
                + self.alpha * traces["S"][idx]
                + self.beta_c * traces["C"][idx]
                + self.gamma * traces["E"][idx]
                + traces["delta"][idx]
            )
            sigma_dyn_value = float(logistic_response(R, theta_t, self.beta))
            noise = rng.gauss(0.0, self.noise)
            sigma_observed = min(max(sigma_dyn_value + noise, 1e-3), 1.0 - 1e-3)
            sigma_static_value = float(logistic_response(R, self.theta0, self.beta))

            R_values.append(R)
            theta_values.append(theta_t)
            sigma_dyn.append(sigma_dyn_value)
            sigma_static.append(sigma_static_value)
            sigma_obs.append(sigma_observed)

        return ContextSeries(
            R=R_values,
            theta=theta_values,
            sigma_observed=sigma_obs,
            sigma_dynamic=sigma_dyn,
            sigma_static=sigma_static,
            S_system=traces["S"],
            C_sub=traces["C"],
            E_context=traces["E"],
            delta_trace=traces["delta"],
        )


def logistic_response(R: float, theta: float, beta: float) -> float:
    """Evaluate sigma(beta(R-Theta)) using the UTF membrane convention."""

    return 1.0 / (1.0 + math.exp(-beta * (R - theta)))


def _aic(ss_res: float, n: int, k: int) -> float:
    if ss_res <= 0 or n == 0:
        return float("-inf")
    return n * math.log(ss_res / n) + 2 * k


def _summary_stats(values: Sequence[float]) -> Dict[str, float]:
    if not values:
        return {"min": 0.0, "max": 0.0, "mean": 0.0}
    return {
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def _residual_metrics(observed: Sequence[float], predicted: Sequence[float], k: int) -> Dict[str, float]:
    residuals = [obs - pred for obs, pred in zip(observed, predicted)]
    ss_res = sum(value**2 for value in residuals)
    mean_obs = sum(observed) / len(observed)
    ss_tot = sum((obs - mean_obs) ** 2 for obs in observed)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"ss_res": ss_res, "r2": r2, "aic": _aic(ss_res, len(observed), k)}


def evaluate_null_model(R: Sequence[float], sigma: Sequence[float]) -> Dict[str, float]:
    """Fit a smooth linear null sigma = m R + b for falsification."""

    mean_R = sum(R) / len(R)
    mean_sigma = sum(sigma) / len(sigma)
    Sxx = sum((value - mean_R) ** 2 for value in R)
    Sxy = sum((R[idx] - mean_R) * (sigma[idx] - mean_sigma) for idx in range(len(R)))
    slope = Sxy / Sxx if Sxx > 0 else 0.0
    intercept = mean_sigma - slope * mean_R
    sigma_hat = [slope * R[idx] + intercept for idx in range(len(R))]
    metrics = _residual_metrics(sigma, sigma_hat, k=2)
    metrics.update({"slope": slope, "intercept": intercept})
    return metrics


def evaluate_power_law_null(R: Sequence[float], sigma: Sequence[float]) -> Dict[str, float]:
    """Calibrate sigma = A * R^k as a smooth alternative baseline."""

    clipped = [min(max(value, 1e-3), 1.0 - 1e-3) for value in sigma]
    log_R = [math.log(max(r, 1e-6)) for r in R]
    log_sigma = [math.log(val) for val in clipped]
    mean_log_R = sum(log_R) / len(log_R)
    mean_log_sigma = sum(log_sigma) / len(log_sigma)
    Sxx = sum((value - mean_log_R) ** 2 for value in log_R)
    Sxy = sum((log_R[idx] - mean_log_R) * (log_sigma[idx] - mean_log_sigma) for idx in range(len(R)))
    exponent = Sxy / Sxx if Sxx > 0 else 0.0
    amplitude = math.exp(mean_log_sigma - exponent * mean_log_R)
    sigma_hat = [amplitude * (max(r, 1e-6) ** exponent) for r in R]
    metrics = _residual_metrics(sigma, sigma_hat, k=2)
    metrics.update({"amplitude": amplitude, "exponent": exponent})
    return metrics


def fit_threshold_parameters(R: Sequence[float], sigma: Sequence[float]) -> Dict[str, float]:
    """Estimate Theta and beta via logit-linear regression."""

    def logit(prob: float) -> float:
        clipped = min(max(prob, 1e-6), 1.0 - 1e-6)
        return math.log(clipped / (1.0 - clipped))

    y = [logit(value) for value in sigma]
    mean_R = sum(R) / len(R)
    mean_y = sum(y) / len(y)
    Sxx = sum((value - mean_R) ** 2 for value in R)
    Sxy = sum((R[idx] - mean_R) * (y[idx] - mean_y) for idx in range(len(R)))
    beta = Sxy / Sxx if Sxx > 0 else 0.0
    intercept = mean_y - beta * mean_R
    theta = float("nan") if abs(beta) < 1e-9 else -intercept / beta

    fitted = [beta * R[idx] + intercept for idx in range(len(R))]
    residuals = [y[idx] - fitted[idx] for idx in range(len(R))]
    dof = max(len(R) - 2, 1)
    sigma2 = sum(value**2 for value in residuals) / dof
    var_beta = sigma2 / Sxx if Sxx > 0 else float("inf")
    beta_std = math.sqrt(max(var_beta, 0.0))
    if Sxx > 0:
        var_intercept = sigma2 * (1.0 / len(R) + (mean_R**2) / Sxx)
        cov = -mean_R * sigma2 / Sxx
    else:
        var_intercept = float("inf")
        cov = 0.0

    if abs(beta) < 1e-9 or math.isinf(var_intercept):
        theta_std = float("nan")
    else:
        dtheta_dbeta = intercept / (beta**2)
        dtheta_dintercept = -1.0 / beta
        theta_var = (
            (dtheta_dbeta**2) * var_beta
            + (dtheta_dintercept**2) * var_intercept
            + 2 * dtheta_dbeta * dtheta_dintercept * cov
        )
        theta_std = math.sqrt(max(theta_var, 0.0))

    logistic_hat = [logistic_response(R[idx], theta, beta) for idx in range(len(R))]
    metrics = _residual_metrics(sigma, logistic_hat, k=2)
    critical = 1.96
    beta_ci = (beta - critical * beta_std, beta + critical * beta_std)
    theta_ci = (
        float("nan") if math.isnan(theta) else theta - critical * theta_std,
        float("nan") if math.isnan(theta) else theta + critical * theta_std,
    )

    return {
        "beta": beta,
        "theta": theta,
        "beta_ci_lower": beta_ci[0],
        "beta_ci_upper": beta_ci[1],
        "theta_ci_lower": theta_ci[0],
        "theta_ci_upper": theta_ci[1],
        "r2": metrics["r2"],
        "aic": metrics["aic"],
    }


def evaluate_scenario(scenario: AdaptiveScenario, steps: int = 64) -> Dict[str, object]:
    """Run the adaptive-threshold experiment and collect diagnostics."""

    series = scenario.generate(steps=steps)
    dynamic_metrics = _residual_metrics(series.sigma_observed, series.sigma_dynamic, k=5)
    static_metrics = _residual_metrics(series.sigma_observed, series.sigma_static, k=2)
    linear_null = evaluate_null_model(series.R, series.sigma_observed)
    power_null = evaluate_power_law_null(series.R, series.sigma_observed)
    fit_metrics = fit_threshold_parameters(series.R, series.sigma_observed)

    theta_shifts = [theta - scenario.theta0 for theta in series.theta]
    interference_margin = min(abs(R - theta) for R, theta in zip(series.R, series.theta))

    return {
        "scenario": scenario.name,
        "parameters": {
            "theta0": scenario.theta0,
            "beta": scenario.beta,
            "alpha": scenario.alpha,
            "beta_c": scenario.beta_c,
            "gamma": scenario.gamma,
            "delta_magnitude": scenario.delta_magnitude,
        },
        "metrics": {
            "dynamic": dynamic_metrics,
            "static": static_metrics,
            "linear_null": linear_null,
            "power_law_null": power_null,
            "logit_fit": fit_metrics,
            "delta_aic_dynamic_vs_static": static_metrics["aic"] - dynamic_metrics["aic"],
            "delta_aic_dynamic_vs_linear": linear_null["aic"] - dynamic_metrics["aic"],
            "delta_aic_dynamic_vs_power": power_null["aic"] - dynamic_metrics["aic"],
        },
        "theta_shift": {
            "stats": _summary_stats(theta_shifts),
            "min_interference_margin": interference_margin,
        },
        "series": {
            "R": series.R,
            "theta": series.theta,
            "sigma_observed": series.sigma_observed,
            "sigma_dynamic": series.sigma_dynamic,
            "sigma_static": series.sigma_static,
            "S_system": series.S_system,
            "C_sub": series.C_sub,
            "E_context": series.E_context,
            "delta_trace": series.delta_trace,
        },
        "tri_layer": {
            "formal": "Adaptive Theta(t) logistic response contrasted against fixed Theta0 and smooth nulls.",
            "empirical": "Synthetic traces stand in for insect colonies, cortical clusters, and curriculum ramps.",
            "metaphorical": "Charts how each membrane remembers prior resonance by flexing its threshold subtly.",
        },
    }


def build_scenarios() -> List[AdaptiveScenario]:
    """Define the adaptive-threshold typology cohort."""

    return [
        AdaptiveScenario(
            name="biosphere_insect_membrane",
            theta0=1.15,
            beta=4.1,
            alpha=0.18,
            beta_c=0.22,
            gamma=-0.08,
            delta_magnitude=-0.12,
            noise=0.02,
        ),
        AdaptiveScenario(
            name="cortical_spike_guard",
            theta0=0.85,
            beta=5.0,
            alpha=0.12,
            beta_c=0.28,
            gamma=0.16,
            delta_magnitude=0.09,
            noise=0.018,
        ),
        AdaptiveScenario(
            name="ai_curriculum_feedback",
            theta0=1.05,
            beta=4.6,
            alpha=0.15,
            beta_c=0.18,
            gamma=0.05,
            delta_magnitude=-0.05,
            noise=0.015,
        ),
    ]


def build_summary(steps: int = 64) -> Dict[str, object]:
    """Evaluate all scenarios and compose a JSON-ready summary."""

    scenarios = build_scenarios()
    evaluations = [evaluate_scenario(scenario, steps=steps) for scenario in scenarios]

    mean_delta_aic = sum(item["metrics"]["delta_aic_dynamic_vs_static"] for item in evaluations) / len(evaluations)
    interference_means = [item["theta_shift"]["stats"]["mean"] for item in evaluations]

    return {
        "generated_at": "adaptive_theta_typology",
        "steps": steps,
        "scenarios": evaluations,
        "aggregates": {
            "mean_delta_aic_dynamic_vs_static": mean_delta_aic,
            "mean_theta_shift": sum(interference_means) / len(interference_means),
            "notes": "Positive ΔAIC values show dynamic Θ(t) outperforms static Θ0 fits across typologies.",
        },
    }


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Simulate adaptive threshold typologies and export resonance diagnostics.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/dynamic_theta_tests.json"),
        help="Destination for the JSON summary.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=64,
        help="Number of temporal samples per scenario.",
    )
    return parser.parse_args()


def main() -> None:
    """Entrypoint for CLI invocation."""

    args = parse_args()
    summary = build_summary(steps=args.steps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(json.dumps(summary["aggregates"], indent=2))


if __name__ == "__main__":
    main()
