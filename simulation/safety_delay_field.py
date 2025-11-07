r"""Safety Delay Field simulation for UTAC v1.2.

This module implements a time-dependent saddle-node controller that exposes
how the Universal Threshold Adaptive Criticality (UTAC) safety-delay term
stretches the opportunity window between the deterministic breaking time
(\tau_break) and the actual tipping time (\tau_escape).

The model tracks the logistic response \(\sigma(\beta(R-\Theta))\) as the
control parameter \(R\) drifts toward the critical threshold \(\Theta\).
Control centrality and CREP-resonance diagnostics are provided so the module
can plug directly into the Sigillin-Netz resonance ledger.
r"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import curve_fit

# -----------------------------------------------------------------------------
# Logistic scaffolding
# -----------------------------------------------------------------------------

def logistic_response(R: ArrayLike, beta: ArrayLike, theta: float) -> np.ndarray:
    """Compute the logistic response for control parameter values ``R``.

    Parameters
    ----------
    R:
        Control parameter values (order parameter distance to the threshold).
    beta:
        Steepness parameter. May be scalar or broadcastable to ``R``.
    theta:
        Threshold parameter (critical point).

    Returns
    -------
    numpy.ndarray
        Logistic response values ``sigma(beta * (R - theta))``.
    """

    R = np.asarray(R, dtype=float)
    beta = np.asarray(beta, dtype=float)
    return 1.0 / (1.0 + np.exp(-beta * (R - theta)))


def estimate_logistic_parameters(R: np.ndarray, field: np.ndarray) -> Tuple[float, float, float]:
    """Estimate ``beta`` and ``theta`` via non-linear least squares.

    The routine mirrors the analysis layer by fitting ``sigma(beta(R-Theta))``
    to the simulated field response. The returned ``r_squared`` is measured
    against a flat null model, guarding falsifiability.
    """

    def _logistic(x: np.ndarray, beta: float, theta: float) -> np.ndarray:
        return logistic_response(x, beta, theta)

    popt, _ = curve_fit(
        _logistic,
        R,
        field,
        p0=[4.2, 0.0],
        bounds=([0.1, -2.0], [25.0, 2.0]),
        maxfev=20000,
    )
    beta_hat, theta_hat = popt

    residuals = field - _logistic(R, beta_hat, theta_hat)
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((field - np.mean(field)) ** 2))
    r_squared = 1.0 - (ss_res / ss_tot if ss_tot > 0 else np.nan)

    return beta_hat, theta_hat, r_squared


# -----------------------------------------------------------------------------
# Safety Delay Simulation
# -----------------------------------------------------------------------------


def default_control_schedule(time: ArrayLike, midpoint: float = 35.0, kappa: float = 0.25) -> np.ndarray:
    """Smooth control ramp used when no custom schedule is provided."""

    t = np.asarray(time, dtype=float)
    return 1.0 / (1.0 + np.exp(-kappa * (t - midpoint)))


@dataclass
class SafetyDelayResult:
    """Container summarising the safety-delay simulation outcome."""

    time: np.ndarray
    control_parameter: np.ndarray
    state: np.ndarray
    field_response: np.ndarray
    beta_hat: float
    theta_hat: float
    r_squared: float
    tau_break: float
    tau_delay: float
    control_energy: float
    beta_shift: float
    diagnostics: Dict[str, float]


def simulate_safety_delay_field(
    t_max: float = 120.0,
    dt: float = 0.05,
    mu0: float = 0.9,
    drift_rate: float = 0.01,
    control_strength: float = 0.35,
    control_schedule: Optional[Callable[[ArrayLike], ArrayLike]] = None,
    beta_base: float = 4.2,
    beta_gain: float = 1.1,
    theta: float = 0.0,
    noise_std: float = 0.01,
    initial_state: Optional[float] = None,
    random_state: Optional[np.random.Generator] = None,
) -> SafetyDelayResult:
    """Simulate the UTAC safety-delay controller.

    The dynamics follow a time-dependent saddle-node bifurcation
    ``dx/dt = mu(t) - x^2`` with an adaptive control signal embedded in ``mu``.
    ``mu(t)`` drifts at ``drift_rate`` toward the critical point while the
    control schedule counter-acts the drift to prolong the metastable regime.

    Returns
    -------
    SafetyDelayResult
        Rich summary containing the logistic fit, delay metrics, and
        resonance diagnostics linking to the Sigillin-Netz.
    """

    if dt <= 0:
        raise ValueError("dt must be positive")

    if random_state is None:
        random_state = np.random.default_rng()

    schedule = control_schedule or default_control_schedule

    time = np.arange(0.0, t_max + dt, dt)
    state = np.zeros_like(time)
    control_parameter = np.zeros_like(time)
    control_signal = np.zeros_like(time)

    x = np.sqrt(mu0) if initial_state is None else float(initial_state)

    for idx, t in enumerate(time):
        schedule_val = float(np.asarray(schedule(t)))
        control_signal[idx] = control_strength * schedule_val
        mu_t = mu0 - drift_rate * t + control_signal[idx]
        control_parameter[idx] = mu_t

        # Euler-Maruyama integration step
        x_clamped = np.clip(x, -1e6, 1e6)
        deterministic = (mu_t - x_clamped**2) * dt
        stochastic = random_state.normal(scale=noise_std * np.sqrt(dt)) if noise_std > 0 else 0.0
        x = x_clamped + deterministic + stochastic
        x = float(np.clip(x, -1e6, 1e6))
        state[idx] = x

    beta_dynamic = beta_base + beta_gain * (control_signal / np.maximum(control_strength, 1e-8))
    field_response = logistic_response(control_parameter, beta_dynamic, theta)

    beta_hat, theta_hat, r_squared = estimate_logistic_parameters(control_parameter, field_response)

    tau_break = float(mu0 / drift_rate) if drift_rate > 0 else np.inf
    below_threshold = np.where(control_parameter <= theta)[0]
    tau_threshold = time[below_threshold[0]] if below_threshold.size else np.nan

    escape_condition = state <= (theta - 0.5)
    tau_escape = time[np.argmax(escape_condition)] if np.any(escape_condition) else np.nan
    tau_delay = float(tau_escape - tau_threshold) if np.isfinite(tau_escape) and np.isfinite(tau_threshold) else np.nan

    control_energy = float(np.trapz(control_signal**2, time))
    beta_shift = float(beta_hat - beta_base)

    diagnostics = {
        "tau_threshold": float(tau_threshold),
        "tau_escape": float(tau_escape),
        "mu_final": float(control_parameter[-1]),
        "state_final": float(state[-1]),
        "control_energy": control_energy,
    }

    return SafetyDelayResult(
        time=time,
        control_parameter=control_parameter,
        state=state,
        field_response=field_response,
        beta_hat=beta_hat,
        theta_hat=theta_hat,
        r_squared=r_squared,
        tau_break=float(tau_break),
        tau_delay=float(tau_delay),
        control_energy=control_energy,
        beta_shift=beta_shift,
        diagnostics=diagnostics,
    )


# -----------------------------------------------------------------------------
# Resonance diagnostics
# -----------------------------------------------------------------------------


def control_centrality(adjacency: np.ndarray) -> float:
    """Compute a simple control-centrality proxy from the adjacency spectrum."""

    if adjacency.ndim != 2 or adjacency.shape[0] != adjacency.shape[1]:
        raise ValueError("adjacency must be a square matrix")

    eigenvalues = np.linalg.eigvals(adjacency)
    return float(np.max(np.real(eigenvalues)))


def crep_resonance(field_response: np.ndarray) -> float:
    """Estimate CREP-resonance as modulation over the logistic membrane."""

    field_response = np.asarray(field_response, dtype=float)
    mean_level = np.mean(np.abs(field_response)) + 1e-9
    return float(np.std(field_response) / mean_level)


def meta_resonance_analysis(adjacency: np.ndarray, field_response: np.ndarray) -> Dict[str, float]:
    """Combine control centrality and CREP-resonance for ledger ingestion."""

    cc = control_centrality(adjacency)
    resonance = crep_resonance(field_response)
    return {
        "control_centrality": cc,
        "crep_resonance": resonance,
        "combined_signal": cc * resonance,
    }


__all__ = [
    "SafetyDelayResult",
    "simulate_safety_delay_field",
    "logistic_response",
    "estimate_logistic_parameters",
    "control_centrality",
    "crep_resonance",
    "meta_resonance_analysis",
]
