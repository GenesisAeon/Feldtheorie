"""Quantum extension of the AFET framework.

Maps σ_Φ to quantum decoherence observables.  The core insight is that
the AFET entropy-density threshold σ_Φ = 1/16 has a natural quantum
analogue via the decoherence time τ_dec:

    σ_Φ_q = (ℏ / kT) · (1 / τ_dec)

This module provides:
  - ``sigma_phi_quantum(T, tau_dec)`` — quantum σ_Φ from temperature and
    decoherence time
  - ``decoherence_threshold(T)`` — critical τ_dec at the AFET boundary
  - ``adaptive_switching(sigma_q, sigma_classical)`` — decision function
    for quantum ↔ classical regime transition

The formalism connects AFET's universality claim to quantum information
theory: if σ_Φ is truly universal, it should govern decoherence in the
same way it governs classical phase transitions.

References:
  - AFET framework: theory/afet.py
  - Zurek (2003), Decoherence and the transition from quantum to classical
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from theory.afet import AFETConstants, AFETFramework

# Physical constants (SI)
HBAR = 1.0545718e-34  # Planck's reduced constant (J·s)
K_BOLTZMANN = 1.380649e-23  # Boltzmann constant (J/K)


@dataclass(frozen=True)
class QuantumAFETResult:
    """Result of a quantum σ_Φ calculation."""

    sigma_phi_quantum: float
    temperature_K: float
    tau_dec_s: float
    is_quantum_regime: bool
    classical_probability: float


class QuantumAFET(AFETFramework):
    """AFET framework extended to quantum decoherence systems.

    Inherits classical AFET methods and adds quantum-specific
    calculations for decoherence tracking and regime switching.
    """

    def __init__(self, constants: AFETConstants = AFETConstants()) -> None:
        super().__init__(constants)

    def sigma_phi_quantum(self, temperature_K: float, tau_dec_s: float) -> float:
        """Compute quantum σ_Φ from temperature and decoherence time.

        Formula: σ_Φ_q = (ℏ / kT) · (1 / τ_dec)

        Parameters
        ----------
        temperature_K : float
            System temperature in Kelvin (must be > 0).
        tau_dec_s : float
            Decoherence time in seconds (must be > 0).

        Returns
        -------
        float
            Quantum entropy density σ_Φ_q.
        """
        T = float(temperature_K)
        tau = float(tau_dec_s)
        if T <= 0.0 or tau <= 0.0:
            raise ValueError("Temperature and decoherence time must be positive")
        return (HBAR / (K_BOLTZMANN * T)) / tau

    def decoherence_threshold(self, temperature_K: float) -> float:
        """Compute critical decoherence time at the AFET σ_Φ boundary.

        At the boundary σ_Φ_q = σ_Φ = 0.0625, so:
            τ_dec_crit = ℏ / (kT · σ_Φ)

        Parameters
        ----------
        temperature_K : float
            System temperature in Kelvin.

        Returns
        -------
        float
            Critical decoherence time (seconds). Systems with τ_dec below
            this value are in the metastable (quantum-coherent) regime.
        """
        T = float(temperature_K)
        if T <= 0.0:
            raise ValueError("Temperature must be positive")
        return HBAR / (K_BOLTZMANN * T * self.constants.SIGMA_PHI)

    def critical_temperature(self, omega_rad_s: float) -> float:
        """Compute critical temperature from angular frequency.

        Formula: T_crit = ℏω / (k · ln(1/σ_Φ))

        Parameters
        ----------
        omega_rad_s : float
            Angular frequency in rad/s.

        Returns
        -------
        float
            Critical temperature in Kelvin.
        """
        omega = float(omega_rad_s)
        if omega <= 0.0:
            raise ValueError("Angular frequency must be positive")
        return (HBAR * omega) / (K_BOLTZMANN * math.log(1.0 / self.constants.SIGMA_PHI))

    def classical_probability(self, t_elapsed_s: float, tau_dec_s: float) -> float:
        """Probability that the system has decohered to classical.

        Formula: P_classical = 1 - exp(-t / τ_dec)

        Parameters
        ----------
        t_elapsed_s : float
            Elapsed time since preparation (seconds).
        tau_dec_s : float
            Decoherence time (seconds).

        Returns
        -------
        float
            Probability in [0, 1].
        """
        t = float(t_elapsed_s)
        tau = float(tau_dec_s)
        if tau <= 0.0:
            raise ValueError("Decoherence time must be positive")
        if t < 0.0:
            return 0.0
        return 1.0 - math.exp(-t / tau)

    def adaptive_switching(
        self,
        sigma_quantum: float,
        sigma_classical: float,
    ) -> dict[str, float | str | bool]:
        """Decide whether to use quantum or classical AFET regime.

        The system uses the quantum regime when σ_Φ_q is smaller than
        the classical σ_Φ (stronger coherence).  When decoherence
        pushes σ_Φ_q above σ_Φ_classical, the system switches to
        classical monitoring.

        Parameters
        ----------
        sigma_quantum : float
            Quantum-computed σ_Φ.
        sigma_classical : float
            Classically-computed σ_Φ.

        Returns
        -------
        dict
            Regime decision with active σ_Φ value and reasoning.
        """
        sq = float(sigma_quantum)
        sc = float(sigma_classical)
        use_quantum = sq < sc

        return {
            "sigma_phi_quantum": sq,
            "sigma_phi_classical": sc,
            "regime": "quantum" if use_quantum else "classical",
            "active_sigma_phi": sq if use_quantum else sc,
            "use_quantum": use_quantum,
            "ratio": sq / max(sc, 1e-30),
        }

    def evaluate_quantum_system(
        self,
        temperature_K: float,
        tau_dec_s: float,
        t_elapsed_s: float = 0.0,
        sigma_classical: float | None = None,
    ) -> QuantumAFETResult:
        """Full quantum AFET evaluation of a system.

        Parameters
        ----------
        temperature_K : float
            System temperature (Kelvin).
        tau_dec_s : float
            Decoherence time (seconds).
        t_elapsed_s : float
            Time since state preparation (seconds).
        sigma_classical : float, optional
            Classical σ_Φ for regime comparison.

        Returns
        -------
        QuantumAFETResult
        """
        sigma_q = self.sigma_phi_quantum(temperature_K, tau_dec_s)
        p_classical = self.classical_probability(t_elapsed_s, tau_dec_s)
        is_quantum = p_classical < 0.5

        if sigma_classical is not None:
            switching = self.adaptive_switching(sigma_q, sigma_classical)
            is_quantum = switching["use_quantum"]

        return QuantumAFETResult(
            sigma_phi_quantum=sigma_q,
            temperature_K=temperature_K,
            tau_dec_s=tau_dec_s,
            is_quantum_regime=is_quantum,
            classical_probability=p_classical,
        )
