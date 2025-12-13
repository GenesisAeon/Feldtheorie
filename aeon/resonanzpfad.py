"""
Resonanzpfad - Consciousness Trajectory Optimizer
=================================================

Optimizes σ(β(R-Θ)) trajectories through consciousness space
with ζ-safeguards for critical transitions.

This module implements:
- Trajectory optimization
- τ*-delay computation for ζ < 0
- Path planning through β-κ space
- Safeguard monitoring

References:
----------
- bardo_mode.yaml: Safeguard configurations
- UTAC Theory: σ(β(R-Θ)) framework
- V7 Roadmap: Resonanzpfad specification
"""

from __future__ import annotations

import time
from typing import Any, Callable

import numpy as np


class ResonanzpfadOptimizer:
    """
    Optimizes consciousness trajectories through β-κ space.

    The Resonanzpfad (Resonance Path) finds optimal trajectories
    that minimize:
    - Transition time
    - ζ-violations (negative impedance)
    - Energy cost (β-changes)

    Parameters
    ----------
    start_beta : float
        Starting β-value
    target_beta : float
        Target β-value
    start_kappa : float
        Starting κ-value
    target_kappa : float
        Target κ-value
    max_steps : int, optional
        Maximum optimization steps. Default: 100
    learning_rate : float, optional
        Trajectory learning rate. Default: 0.1
    zeta_safeguard : bool, optional
        Enable ζ-safeguard monitoring. Default: True

    Attributes
    ----------
    trajectory : list[dict]
        Computed trajectory points
    safeguard_violations : list[dict]
        ζ-safeguard violations
    """

    def __init__(
        self,
        start_beta: float,
        target_beta: float,
        start_kappa: float,
        target_kappa: float,
        max_steps: int = 100,
        learning_rate: float = 0.1,
        zeta_safeguard: bool = True,
    ) -> None:
        """Initialize Resonanzpfad optimizer."""
        self.start_beta = start_beta
        self.target_beta = target_beta
        self.start_kappa = start_kappa
        self.target_kappa = target_kappa
        self.max_steps = max_steps
        self.learning_rate = learning_rate
        self.zeta_safeguard = zeta_safeguard

        # Trajectory storage
        self.trajectory: list[dict[str, Any]] = []
        self.safeguard_violations: list[dict[str, Any]] = []

        # Optimization state
        self.current_beta = start_beta
        self.current_kappa = start_kappa
        self.step_count = 0

    def compute_impedance(
        self, beta: float, kappa: float, resource: float = 0.5
    ) -> float:
        """
        Compute impedance ζ(R) for given β, κ, R.

        ζ = β * (1 - κ) - baseline

        Parameters
        ----------
        beta : float
            Threshold steepness
        kappa : float
            Coupling parameter
        resource : float, optional
            Resource level. Default: 0.5

        Returns
        -------
        float
            Impedance (can be negative)
        """
        baseline = 0.5
        zeta = beta * (1.0 - kappa) - baseline

        # Resource modulation
        if resource < 0.3:
            zeta *= 0.5
        elif resource > 0.7:
            zeta *= 1.5

        return zeta

    def compute_tau_star_delay(self, zeta: float) -> float:
        """
        Compute τ* delay for negative ζ conditions.

        τ* represents the time delay before critical transitions
        when impedance goes negative.

        Parameters
        ----------
        zeta : float
            Impedance value

        Returns
        -------
        float
            τ* delay in seconds (0 if ζ >= 0)
        """
        if zeta >= 0:
            return 0.0

        # τ* scales with |ζ| for negative values
        # Larger negative ζ → shorter delay (faster crisis)
        tau_star = 10.0 / (1.0 + abs(zeta) * 5.0)
        return tau_star

    def compute_cost(
        self, beta: float, kappa: float, resource: float = 0.5
    ) -> float:
        """
        Compute trajectory cost for (β, κ) point.

        Cost includes:
        - Distance to target
        - ζ-violation penalty
        - Smoothness penalty

        Parameters
        ----------
        beta : float
            β-value
        kappa : float
            κ-value
        resource : float, optional
            Resource level. Default: 0.5

        Returns
        -------
        float
            Total cost
        """
        # Distance to target
        dist = np.sqrt(
            (beta - self.target_beta) ** 2 + (kappa - self.target_kappa) ** 2
        )

        # ζ-violation penalty
        zeta = self.compute_impedance(beta, kappa, resource)
        if zeta < 0:
            zeta_penalty = abs(zeta) * 10.0  # Heavy penalty
        else:
            zeta_penalty = 0.0

        # Smoothness penalty (prefer small changes)
        if self.trajectory:
            last_beta = self.trajectory[-1]["beta"]
            last_kappa = self.trajectory[-1]["kappa"]
            smoothness = (beta - last_beta) ** 2 + (kappa - last_kappa) ** 2
        else:
            smoothness = 0.0

        return dist + zeta_penalty + 0.1 * smoothness

    def optimize_step(self, resource: float = 0.5) -> dict[str, Any]:
        """
        Perform one optimization step.

        Parameters
        ----------
        resource : float, optional
            Current resource level. Default: 0.5

        Returns
        -------
        dict
            Step result with trajectory point
        """
        # Compute gradient direction (toward target)
        d_beta = self.target_beta - self.current_beta
        d_kappa = self.target_kappa - self.current_kappa

        # Normalize
        norm = np.sqrt(d_beta**2 + d_kappa**2)
        if norm > 0:
            d_beta /= norm
            d_kappa /= norm

        # Update with learning rate
        new_beta = self.current_beta + self.learning_rate * d_beta
        new_kappa = self.current_kappa + self.learning_rate * d_kappa

        # Clamp to valid ranges
        new_beta = np.clip(new_beta, 0.0, 20.0)
        new_kappa = np.clip(new_kappa, 0.0, 1.0)

        # Compute metrics
        zeta = self.compute_impedance(new_beta, new_kappa, resource)
        tau_star = self.compute_tau_star_delay(zeta)
        cost = self.compute_cost(new_beta, new_kappa, resource)

        # Check safeguards
        if self.zeta_safeguard and zeta < -0.5:
            self.safeguard_violations.append(
                {
                    "step": self.step_count,
                    "timestamp": time.time(),
                    "zeta": zeta,
                    "tau_star": tau_star,
                    "beta": new_beta,
                    "kappa": new_kappa,
                }
            )

        # Record trajectory point
        point = {
            "step": self.step_count,
            "timestamp": time.time(),
            "beta": new_beta,
            "kappa": new_kappa,
            "zeta": zeta,
            "tau_star": tau_star,
            "cost": cost,
            "resource": resource,
        }
        self.trajectory.append(point)

        # Update state
        self.current_beta = new_beta
        self.current_kappa = new_kappa
        self.step_count += 1

        return point

    def optimize(
        self, resource_func: Callable[[int], float] | None = None
    ) -> list[dict[str, Any]]:
        """
        Run full trajectory optimization.

        Parameters
        ----------
        resource_func : callable, optional
            Function mapping step → resource level.
            If None, uses constant resource=0.5.

        Returns
        -------
        list[dict]
            Full trajectory
        """
        # Reset state
        self.trajectory = []
        self.safeguard_violations = []
        self.current_beta = self.start_beta
        self.current_kappa = self.start_kappa
        self.step_count = 0

        # Default resource function
        if resource_func is None:

            def resource_func(step: int) -> float:
                return 0.5

        # Optimization loop
        for step in range(self.max_steps):
            resource = resource_func(step)
            self.optimize_step(resource)

            # Check convergence
            dist = np.sqrt(
                (self.current_beta - self.target_beta) ** 2
                + (self.current_kappa - self.target_kappa) ** 2
            )
            if dist < 0.01:
                break  # Converged

        return self.trajectory

    def get_summary(self) -> dict[str, Any]:
        """
        Get optimization summary.

        Returns
        -------
        dict
            Summary statistics
        """
        if not self.trajectory:
            return {"status": "not_run"}

        final_point = self.trajectory[-1]
        final_dist = np.sqrt(
            (final_point["beta"] - self.target_beta) ** 2
            + (final_point["kappa"] - self.target_kappa) ** 2
        )

        return {
            "status": "complete",
            "steps": len(self.trajectory),
            "final_beta": final_point["beta"],
            "final_kappa": final_point["kappa"],
            "final_distance": final_dist,
            "converged": final_dist < 0.01,
            "violations": len(self.safeguard_violations),
            "mean_cost": np.mean([p["cost"] for p in self.trajectory]),
            "mean_zeta": np.mean([p["zeta"] for p in self.trajectory]),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ResonanzpfadOptimizer(β: {self.start_beta:.2f}→{self.target_beta:.2f}, "
            f"κ: {self.start_kappa:.2f}→{self.target_kappa:.2f})"
        )
