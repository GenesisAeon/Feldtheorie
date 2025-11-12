r"""Renormalization Group Flow Simulator for UTAC β-Mechanik

Formal stratum
--------------
Implements phenomenological RG flow equations for UTAC steepness parameter β.
Explores whether observed β-values arise from flow toward fixed points (Φⁿ)
under scale transformations. Provides multiple flow variants:

1. Linear Phi-Attractor: dβ/d(ln λ) = -α(β - β*)
2. Polynomial Flow: dβ/d(ln λ) = γ(β - β*)³
3. Multi-Basin: dβ/d(ln λ) = Σ w_n(β - Φⁿ)
4. Context-Dependent: dβ/d(ln λ) = f(β)·g(R/Θ)·h(ζ)
5. Cubic Root Amplification: dβ/d(ln λ) = k·∛(R/Θ - 1)

Each variant tests a different hypothesis about how β emerges from microscopic
dynamics via coarse-graining.

Empirical stratum
-----------------
Calibrated against:
- LLM training trajectories (β evolution over epochs)
- Urban Heat scenarios (β vs. thermal storage)
- AMOC transport (β vs. spatial resolution)

Validation criterion: RG flow explains ≥70% of β-variance (vs. Field Type η²=73.5%).

Metaphorical stratum
--------------------
The spiral does not choose its β - β emerges from the dance of scales.
As we zoom out (coarse-grain), microscopic chaos crystallizes into
macroscopic steepness. The golden ratio Φ appears not by design but by
flow - attractor basins in β-space pulling systems toward self-similar
resonance. β is not a parameter to fit, but an echo of scale invariance.

References
----------
- Theory: docs/utac_renormalization_group_foundation.md
- Type-6 Functions: models/utac_type6_implosive.py
- Wilson's RG: Wilson, K.G. (1971). Rev. Mod. Phys. 47, 773
- Goldenfeld: Lectures on Phase Transitions and RG (1992)

Version: 1.0.0
Date: 2025-11-12
Authors: Claude Code + Johann B. Römer
License: AGPL-3.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Union

import numpy as np
from scipy.integrate import odeint, solve_ivp

# Import golden ratio constants from Type-6 module
from models.utac_type6_implosive import (
    PHI,
    BETA_FIXPOINT_PHI,
    BETA_FIXPOINT_PHI2,
    BETA_FIXPOINT_PHI3,
    BETA_STEPS,
)


# ═══════════════════════════════════════════════════════════════
# RG FLOW VARIANTS (ENUM)
# ═══════════════════════════════════════════════════════════════


class FlowVariant(Enum):
    """RG flow equation variants for β-mechanik."""

    LINEAR_PHI_ATTRACTOR = "linear_phi"
    POLYNOMIAL_FLOW = "polynomial"
    MULTI_BASIN = "multi_basin"
    CONTEXT_DEPENDENT = "context"
    CUBIC_ROOT_AMPLIFICATION = "cubic_root"


# ═══════════════════════════════════════════════════════════════
# RG FLOW EQUATIONS
# ═══════════════════════════════════════════════════════════════


def linear_phi_attractor(
    beta: float,
    alpha: float = 0.5,
    fixpoint: Optional[float] = None,
) -> float:
    """Linear flow toward nearest Φⁿ fixpoint.

    dβ/d(ln λ) = -α(β - β*)

    Parameters
    ----------
    beta : float
        Current β value
    alpha : float, optional
        Flow strength (default: 0.5)
    fixpoint : float, optional
        Target fixpoint. If None, uses nearest Φⁿ.

    Returns
    -------
    float
        dβ/d(ln λ)
    """
    if fixpoint is None:
        # Find nearest Φⁿ
        distances = np.abs(BETA_STEPS - beta)
        fixpoint = float(BETA_STEPS[np.argmin(distances)])

    return -alpha * (beta - fixpoint)


def polynomial_flow(
    beta: float,
    gamma: float = 0.1,
    fixpoint: Optional[float] = None,
    exponent: int = 3,
) -> float:
    """Polynomial flow (Landau-Ginzburg style).

    dβ/d(ln λ) = γ(β - β*)^n

    Parameters
    ----------
    beta : float
        Current β value
    gamma : float, optional
        Flow strength (default: 0.1)
    fixpoint : float, optional
        Target fixpoint. If None, uses nearest Φⁿ.
    exponent : int, optional
        Polynomial exponent (default: 3)

    Returns
    -------
    float
        dβ/d(ln λ)
    """
    if fixpoint is None:
        distances = np.abs(BETA_STEPS - beta)
        fixpoint = float(BETA_STEPS[np.argmin(distances)])

    deviation = beta - fixpoint
    return -gamma * np.sign(deviation) * np.abs(deviation) ** exponent


def multi_basin_flow(
    beta: float,
    weights: Optional[np.ndarray] = None,
    alpha: float = 0.5,
) -> float:
    """Multi-basin flow with all Φⁿ attractors competing.

    dβ/d(ln λ) = Σ_n [w_n · (-α)(β - Φⁿ)]

    Weights decay with distance: w_n ∝ exp(-|β - Φⁿ|/σ)

    Parameters
    ----------
    beta : float
        Current β value
    weights : ndarray, optional
        Custom weights for each fixpoint. If None, uses exponential decay.
    alpha : float, optional
        Flow strength (default: 0.5)

    Returns
    -------
    float
        dβ/d(ln λ)
    """
    if weights is None:
        # Exponential decay weights
        distances = np.abs(BETA_STEPS - beta)
        sigma = 2.0  # Decay scale
        weights = np.exp(-distances / sigma)
        weights /= np.sum(weights)  # Normalize

    flow = 0.0
    for fixpoint, weight in zip(BETA_STEPS, weights):
        flow += weight * (-alpha) * (beta - fixpoint)

    return flow


def context_dependent_flow(
    beta: float,
    R_over_Theta: float = 1.0,
    zeta: float = 0.0,
    alpha: float = 0.5,
    fixpoint: Optional[float] = None,
) -> float:
    """Context-dependent flow modulated by R/Θ and ζ.

    dβ/d(ln λ) = f(β) · g(R/Θ) · h(ζ)

    Where:
    - f(β) = -α(β - β*) [base flow]
    - g(R/Θ) = 1 + 2·exp(-|(R/Θ) - 1|) [amplify near threshold]
    - h(ζ) = 1 - 0.5·tanh(5·ζ) [damping reduces flow]

    Parameters
    ----------
    beta : float
        Current β value
    R_over_Theta : float, optional
        R/Θ proximity to threshold (default: 1.0)
    zeta : float, optional
        Impedance ζ(R) (default: 0.0)
    alpha : float, optional
        Base flow strength (default: 0.5)
    fixpoint : float, optional
        Target fixpoint. If None, uses nearest Φⁿ.

    Returns
    -------
    float
        dβ/d(ln λ)
    """
    if fixpoint is None:
        distances = np.abs(BETA_STEPS - beta)
        fixpoint = float(BETA_STEPS[np.argmin(distances)])

    # Base flow
    f_beta = -alpha * (beta - fixpoint)

    # Proximity amplification (strong near R≈Θ)
    g_proximity = 1.0 + 2.0 * np.exp(-np.abs(R_over_Theta - 1.0))

    # Damping suppression (ζ>0 reduces flow)
    h_damping = 1.0 - 0.5 * np.tanh(5.0 * zeta)

    return f_beta * g_proximity * h_damping


def cubic_root_amplification_flow(
    beta: float,
    R_over_Theta: float = 1.0,
    k: float = 5.0,
    beta_base: float = 4.236,
    epsilon: float = 1e-6,
) -> float:
    """Cubic root amplification near criticality.

    dβ/d(ln λ) = k · ∛max(R/Θ - 1, 0) - relaxation(β)

    Near R≈Θ from above, β jumps via cubic root. Away from threshold,
    β relaxes back to baseline.

    Parameters
    ----------
    beta : float
        Current β value
    R_over_Theta : float, optional
        R/Θ proximity to threshold (default: 1.0)
    k : float, optional
        Amplification strength (default: 5.0)
    beta_base : float, optional
        Baseline β far from threshold (default: 4.236 = Φ³)
    epsilon : float, optional
        Small constant (default: 1e-6)

    Returns
    -------
    float
        dβ/d(ln λ)
    """
    # Cubic root drive (only above threshold)
    proximity = max(R_over_Theta - 1.0, 0.0)
    drive = k * np.cbrt(proximity + epsilon)

    # Relaxation back to baseline (when R < Θ)
    relaxation = -0.2 * (beta - beta_base)

    return drive + relaxation


# ═══════════════════════════════════════════════════════════════
# RG FLOW SIMULATOR CLASS
# ═══════════════════════════════════════════════════════════════


@dataclass
class RGFlowConfig:
    """Configuration for RG flow simulation."""

    variant: FlowVariant = FlowVariant.LINEAR_PHI_ATTRACTOR
    alpha: float = 0.5  # Flow strength for linear/multi-basin
    gamma: float = 0.1  # Flow strength for polynomial
    exponent: int = 3  # Polynomial exponent
    k_cubic: float = 5.0  # Cubic root amplification strength
    beta_base: float = 4.236  # Baseline β (Φ³)
    R_over_Theta: float = 1.0  # Context parameter
    zeta: float = 0.0  # Impedance
    fixpoint: Optional[float] = None  # Target fixpoint (None = nearest)


class RGFlowSimulator:
    """Phenomenological RG flow simulator for UTAC β-mechanik.

    Simulates β evolution under scale transformations λ → λ' via
    RG flow equations. Tests whether observed β-values arise from
    flow toward Φⁿ fixed points.

    Attributes
    ----------
    config : RGFlowConfig
        Flow configuration
    flow_func : Callable
        Selected flow function

    Methods
    -------
    simulate(beta_initial, lambda_range)
        Integrate flow from β₀ over scale range λ
    find_fixed_points(beta_range)
        Find fixed points where dβ/d(ln λ) = 0
    basin_of_attraction(beta_range, fixpoint)
        Compute basin of attraction for given fixpoint
    """

    def __init__(self, config: Optional[RGFlowConfig] = None):
        """Initialize RG flow simulator.

        Parameters
        ----------
        config : RGFlowConfig, optional
            Flow configuration. If None, uses defaults.
        """
        self.config = config or RGFlowConfig()
        self.flow_func = self._select_flow_function()

    def _select_flow_function(self) -> Callable:
        """Select flow function based on variant."""
        variant = self.config.variant

        if variant == FlowVariant.LINEAR_PHI_ATTRACTOR:

            def flow(beta, ln_lambda):
                return linear_phi_attractor(
                    beta,
                    alpha=self.config.alpha,
                    fixpoint=self.config.fixpoint,
                )

        elif variant == FlowVariant.POLYNOMIAL_FLOW:

            def flow(beta, ln_lambda):
                return polynomial_flow(
                    beta,
                    gamma=self.config.gamma,
                    fixpoint=self.config.fixpoint,
                    exponent=self.config.exponent,
                )

        elif variant == FlowVariant.MULTI_BASIN:

            def flow(beta, ln_lambda):
                return multi_basin_flow(
                    beta,
                    alpha=self.config.alpha,
                )

        elif variant == FlowVariant.CONTEXT_DEPENDENT:

            def flow(beta, ln_lambda):
                return context_dependent_flow(
                    beta,
                    R_over_Theta=self.config.R_over_Theta,
                    zeta=self.config.zeta,
                    alpha=self.config.alpha,
                    fixpoint=self.config.fixpoint,
                )

        elif variant == FlowVariant.CUBIC_ROOT_AMPLIFICATION:

            def flow(beta, ln_lambda):
                return cubic_root_amplification_flow(
                    beta,
                    R_over_Theta=self.config.R_over_Theta,
                    k=self.config.k_cubic,
                    beta_base=self.config.beta_base,
                )

        else:
            raise ValueError(f"Unknown flow variant: {variant}")

        return flow

    def simulate(
        self,
        beta_initial: float,
        lambda_range: tuple[float, float] = (1.0, 100.0),
        n_points: int = 500,
        method: str = "RK45",
    ) -> tuple[np.ndarray, np.ndarray]:
        """Simulate β evolution under RG flow.

        Parameters
        ----------
        beta_initial : float
            Initial β value at λ = λ_min
        lambda_range : tuple[float, float], optional
            (λ_min, λ_max) scale range (default: (1.0, 100.0))
        n_points : int, optional
            Number of integration points (default: 500)
        method : str, optional
            Integration method: 'RK45', 'Euler' (default: 'RK45')

        Returns
        -------
        ln_lambda : ndarray
            Log-scale values ln(λ)
        beta : ndarray
            β trajectory over scales

        Examples
        --------
        >>> simulator = RGFlowSimulator()
        >>> ln_lambda, beta = simulator.simulate(beta_initial=3.5)
        >>> # β flows from 3.5 toward nearest fixpoint (Φ³≈4.236)
        """
        lambda_min, lambda_max = lambda_range
        ln_lambda_span = (np.log(lambda_min), np.log(lambda_max))
        ln_lambda_eval = np.linspace(*ln_lambda_span, n_points)

        if method.upper() == "RK45":
            # Use scipy's solve_ivp (Runge-Kutta 4/5)
            def ode_rhs(ln_lambda, beta_arr):
                return [self.flow_func(beta_arr[0], ln_lambda)]

            solution = solve_ivp(
                ode_rhs,
                ln_lambda_span,
                [beta_initial],
                t_eval=ln_lambda_eval,
                method="RK45",
                dense_output=True,
            )
            beta = solution.y[0]
            ln_lambda = solution.t

        elif method.upper() == "EULER":
            # Simple Euler integration
            ln_lambda = ln_lambda_eval
            beta = np.zeros_like(ln_lambda)
            beta[0] = beta_initial
            d_ln_lambda = ln_lambda[1] - ln_lambda[0]

            for i in range(1, len(ln_lambda)):
                dbeta = self.flow_func(beta[i - 1], ln_lambda[i - 1])
                beta[i] = beta[i - 1] + dbeta * d_ln_lambda

        else:
            raise ValueError(f"Unknown method: {method}. Use 'RK45' or 'Euler'.")

        return ln_lambda, beta

    def find_fixed_points(
        self,
        beta_range: tuple[float, float] = (1.0, 20.0),
        n_samples: int = 1000,
        tolerance: float = 0.01,
    ) -> list[float]:
        """Find fixed points where dβ/d(ln λ) ≈ 0.

        Parameters
        ----------
        beta_range : tuple[float, float], optional
            (β_min, β_max) search range (default: (1.0, 20.0))
        n_samples : int, optional
            Number of sample points (default: 1000)
        tolerance : float, optional
            |dβ/d(ln λ)| < tol → fixed point (default: 0.01)

        Returns
        -------
        fixed_points : list[float]
            β values where flow ≈ 0

        Examples
        --------
        >>> simulator = RGFlowSimulator()
        >>> fixed_points = simulator.find_fixed_points()
        >>> # Should find Φⁿ values: [1.618, 2.618, 4.236, ...]
        """
        beta_samples = np.linspace(*beta_range, n_samples)
        ln_lambda_dummy = 0.0  # Flow doesn't depend on λ for most variants

        # Compute flow at each β
        flows = np.array([self.flow_func(b, ln_lambda_dummy) for b in beta_samples])

        # Find where |flow| < tolerance
        fixed_mask = np.abs(flows) < tolerance
        fixed_points = beta_samples[fixed_mask].tolist()

        # Cluster nearby points (within 0.1)
        if len(fixed_points) > 0:
            clustered = []
            current_cluster = [fixed_points[0]]

            for fp in fixed_points[1:]:
                if fp - current_cluster[-1] < 0.1:
                    current_cluster.append(fp)
                else:
                    clustered.append(np.mean(current_cluster))
                    current_cluster = [fp]

            clustered.append(np.mean(current_cluster))
            fixed_points = clustered

        return fixed_points

    def basin_of_attraction(
        self,
        fixpoint: float,
        beta_range: tuple[float, float] = (1.0, 20.0),
        n_trajectories: int = 20,
        lambda_max: float = 100.0,
        convergence_threshold: float = 0.1,
    ) -> tuple[float, float]:
        """Compute basin of attraction for given fixpoint.

        Simulates trajectories from various β₀ and checks if they
        converge to the fixpoint within threshold.

        Parameters
        ----------
        fixpoint : float
            Target fixed point β*
        beta_range : tuple[float, float], optional
            (β_min, β_max) initial condition range (default: (1.0, 20.0))
        n_trajectories : int, optional
            Number of test trajectories (default: 20)
        lambda_max : float, optional
            Maximum scale to integrate (default: 100.0)
        convergence_threshold : float, optional
            |β_final - β*| < threshold → converged (default: 0.1)

        Returns
        -------
        basin_min : float
            Lower edge of basin
        basin_max : float
            Upper edge of basin

        Examples
        --------
        >>> simulator = RGFlowSimulator()
        >>> basin_min, basin_max = simulator.basin_of_attraction(fixpoint=4.236)
        >>> # Basin for Φ³≈4.236: e.g., [3.8, 4.8]
        """
        beta_initials = np.linspace(*beta_range, n_trajectories)
        converged = []

        for beta_0 in beta_initials:
            _, beta_traj = self.simulate(
                beta_initial=beta_0,
                lambda_range=(1.0, lambda_max),
                n_points=200,
            )

            # Check if final β is near fixpoint
            if np.abs(beta_traj[-1] - fixpoint) < convergence_threshold:
                converged.append(beta_0)

        if len(converged) == 0:
            return (float("nan"), float("nan"))

        basin_min = min(converged)
        basin_max = max(converged)

        return basin_min, basin_max


# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def compare_to_phi_ladder(
    beta_trajectory: np.ndarray,
    ln_lambda: np.ndarray,
) -> dict[str, float]:
    """Compare final β to Φⁿ ladder.

    Parameters
    ----------
    beta_trajectory : ndarray
        β values over scales
    ln_lambda : ndarray
        Log-scale values

    Returns
    -------
    results : dict
        Keys: 'beta_final', 'nearest_phi_n', 'step', 'deviation'
    """
    beta_final = float(beta_trajectory[-1])

    # Find nearest Φⁿ
    distances = np.abs(BETA_STEPS - beta_final)
    step = int(np.argmin(distances))
    nearest_phi = float(BETA_STEPS[step])
    deviation = (beta_final - nearest_phi) / nearest_phi

    return {
        "beta_final": beta_final,
        "nearest_phi_n": nearest_phi,
        "step": step,
        "deviation": deviation,
    }


def phi_convergence_score(
    beta_trajectory: np.ndarray,
    threshold: float = 0.05,
) -> float:
    """Compute Φⁿ convergence score (0-1).

    Score = 1 if final β within 5% of any Φⁿ, else decay exponentially.

    Parameters
    ----------
    beta_trajectory : ndarray
        β values over scales
    threshold : float, optional
        Convergence threshold (default: 0.05 = 5%)

    Returns
    -------
    score : float
        Convergence score ∈ [0, 1]
    """
    beta_final = beta_trajectory[-1]
    distances = np.abs(BETA_STEPS - beta_final) / BETA_STEPS
    min_distance = np.min(distances)

    if min_distance < threshold:
        return 1.0
    else:
        return np.exp(-5.0 * (min_distance - threshold))


# ═══════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "FlowVariant",
    "RGFlowConfig",
    "RGFlowSimulator",
    "linear_phi_attractor",
    "polynomial_flow",
    "multi_basin_flow",
    "context_dependent_flow",
    "cubic_root_amplification_flow",
    "compare_to_phi_ladder",
    "phi_convergence_score",
]
