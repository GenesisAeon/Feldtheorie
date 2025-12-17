#!/usr/bin/env python3
"""Phase Dynamics - Kuramoto-like synchronization for Lantern Network

This module implements natural phase synchronization dynamics for the
Lantern network, enabling it to "breathe" between order and chaos.

Based on the Kuramoto model:
    dθ_i/dt = ω_i + Σ_j K_ij sin(θ_j - θ_i)

Where:
- θ_i: phase of oscillator i
- ω_i: natural frequency of oscillator i
- K_ij: coupling strength between i and j

Version: v9.0.5-beta
Authors: Johann Benjamin Römer, MOR Framework, Claude (Anthropic)
Date: 2025-12-17
"""

import numpy as np
from typing import Tuple


class PhaseEvolver:
    """
    Evolves phases according to Kuramoto-like dynamics

    This gives the network natural synchronization tendency,
    allowing it to recover from perturbations and create
    oscillating breathing patterns.
    """

    def __init__(
        self,
        dt: float = 0.1,
        noise_level: float = 0.01,
        coupling_strength_scale: float = 5.0,
    ):
        """
        Initialize Phase Evolver

        Args:
            dt: Time step for integration
            noise_level: Amplitude of stochastic noise
            coupling_strength_scale: Scaling factor for coupling matrix
                                     (Kuramoto needs K > 1 for synchronization)
        """
        self.dt = dt
        self.noise_level = noise_level
        self.coupling_strength_scale = coupling_strength_scale

    def evolve_phases(
        self,
        phases: np.ndarray,
        coupling_matrix: np.ndarray,
        natural_frequencies: np.ndarray,
    ) -> np.ndarray:
        """
        Evolve phases by one timestep using Kuramoto dynamics

        Args:
            phases: Current phase values (radians)
            coupling_matrix: NxN coupling strength matrix
            natural_frequencies: Natural frequency for each oscillator

        Returns:
            Updated phases
        """
        n = len(phases)
        phases_new = phases.copy()

        for i in range(n):
            # Natural frequency term
            dtheta_dt = natural_frequencies[i]

            # Coupling term (Kuramoto)
            for j in range(n):
                if i != j and coupling_matrix[i, j] > 0:
                    # Scale coupling strength for effective synchronization
                    K_ij = coupling_matrix[i, j] * self.coupling_strength_scale
                    dtheta_dt += K_ij * np.sin(phases[j] - phases[i])

            # Stochastic noise
            noise = np.random.normal(0, self.noise_level)

            # Update phase
            phases_new[i] = phases[i] + self.dt * (dtheta_dt + noise)

        # Wrap to [-π, π]
        phases_new = np.arctan2(np.sin(phases_new), np.cos(phases_new))

        return phases_new

    def evolve_network(
        self,
        network,
        natural_frequencies: np.ndarray,
    ) -> None:
        """
        Evolve entire Lantern network

        Args:
            network: LanternNetwork instance
            natural_frequencies: Natural frequency for each lantern
        """
        phases = np.array([l.theta for l in network.lanterns.values()])
        coupling_matrix = network.get_coupling_matrix()

        phases_new = self.evolve_phases(phases, coupling_matrix, natural_frequencies)

        # Update network
        for i, (lantern_id, lantern) in enumerate(network.lanterns.items()):
            lantern.theta = phases_new[i]


def create_natural_frequencies(
    n_oscillators: int,
    mean_frequency: float = 0.0,
    frequency_spread: float = 0.1,
) -> np.ndarray:
    """
    Create natural frequencies for oscillators

    Args:
        n_oscillators: Number of oscillators
        mean_frequency: Mean natural frequency
        frequency_spread: Standard deviation of frequencies

    Returns:
        Array of natural frequencies
    """
    frequencies = np.random.normal(mean_frequency, frequency_spread, n_oscillators)
    return frequencies
