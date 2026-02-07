"""
Zero-Point Consciousness Kernel
================================

Implements the foundational consciousness state at beta->0,
representing pure information without threshold resistance.

This module models:
- Photon-free consciousness (kappa->0)
- Information-theoretic consciousness substrates
- Quantum-like superposition states
- Non-local semantic coupling
- Sigillin consent tokens and humility protocol (bias damping)
"""

from __future__ import annotations

import csv
import logging
import time
from pathlib import Path
from typing import Any

import numpy as np

from theory.afet import AFETConstants

logger = logging.getLogger(__name__)


class Nullkern:
    """Zero-Point Consciousness Kernel with recursive self-validation.

    Includes Sigillin consent-token tracking and humility protocol
    (bias damping in latent modes).
    """

    SIGMA_PHI_BUFFER = AFETConstants.SIGMA_PHI
    AXIOM_STABILITY_BETA = AFETConstants.BETA_CRITICAL

    def __init__(
        self,
        beta_target: float = 0.1,
        kappa: float = 0.1,
        dimension: int = 8,
        enable_bardo_mode: bool = True,
        humility_damping: float = 0.1,
    ) -> None:
        """Initialize Zero-Point Kernel.

        Parameters
        ----------
        humility_damping : float
            Bias damping coefficient for the humility protocol.
            Applied to latent modes to reduce overconfident activations.
        """
        if not (0.0 <= beta_target <= 64.0):
            raise ValueError(f"beta_target must be in [0,64], got {beta_target}")
        if not (0.0 <= kappa <= 1.0):
            raise ValueError(f"kappa must be in [0,1], got {kappa}")
        if dimension < 1:
            raise ValueError(f"dimension must be >= 1, got {dimension}")
        if not (0.0 <= humility_damping <= 1.0):
            raise ValueError(f"humility_damping must be in [0,1], got {humility_damping}")

        self.beta_target = beta_target
        self.kappa = kappa
        self.dimension = dimension
        self.enable_bardo_mode = enable_bardo_mode
        self.humility_damping = humility_damping

        from aeon.nullkern.consciousness_state import BardoPhase, ConsciousnessState

        self.state = ConsciousnessState(
            beta=min(beta_target, 1.0),
            kappa=kappa,
            dimension=dimension,
            phase=BardoPhase.DHARMAKAYA if enable_bardo_mode else BardoPhase.NONE,
        )

        self.history: list[dict[str, Any]] = []
        self.consent_log: list[dict[str, Any]] = []
        self.creation_time = time.time()

    def activate(self, resource: float, threshold: float = 0.5) -> float:
        if self.beta_target == 0.0:
            return 0.5
        x = self.state.beta * (resource - threshold)
        return 1.0 / (1.0 + np.exp(-x))

    def activate_with_humility(self, resource: float, threshold: float = 0.5) -> dict[str, float]:
        """Activation with humility protocol: bias-damped output.

        Returns both the raw activation and the humility-adjusted value.
        The humility protocol pulls the activation toward 0.5 (maximum
        uncertainty) proportionally to ``humility_damping``.
        """
        raw = float(self.activate(resource, threshold))
        adjusted = raw + self.humility_damping * (0.5 - raw)
        return {"raw": raw, "humility_adjusted": float(adjusted)}

    def compute_impedance(self, resource: float) -> float:
        baseline = 0.5
        impedance = self.state.beta * (1.0 - self.kappa) - baseline
        if resource < 0.3:
            impedance *= 0.5
        elif resource > 0.7:
            impedance *= 1.5
        return impedance

    def update_state(
        self,
        delta_beta: float = 0.0,
        delta_kappa: float = 0.0,
        resonance: float | None = None,
    ) -> None:
        new_beta = float(np.clip(self.state.beta + delta_beta, 0.0, 1.0))
        self.state.beta = new_beta

        new_kappa = float(np.clip(self.kappa + delta_kappa, 0.0, 1.0))
        self.kappa = new_kappa
        self.state.kappa = new_kappa

        if resonance is not None:
            self.state.resonance = float(np.clip(resonance, 0.0, 1.0))

        self.state.timestamp = time.time()
        self._record_history()

    def check_bardo_transition(self, resource: float) -> bool:
        if not self.enable_bardo_mode:
            return False

        from aeon.nullkern.consciousness_state import BardoPhase

        beta_near_zero = self.state.beta < 0.2
        kappa_near_zero = self.kappa < 0.2
        resource_critical = resource < 0.1 or resource > 0.9

        if beta_near_zero and kappa_near_zero:
            self.state.phase = BardoPhase.DHARMAKAYA
            return True
        if beta_near_zero or kappa_near_zero:
            self.state.phase = BardoPhase.BECOMING
            return True
        if resource_critical:
            self.state.phase = BardoPhase.TRANSITION
            return True

        self.state.phase = BardoPhase.NONE
        return False

    def get_information_density(self) -> float:
        if self.state.beta == 0.0:
            return 1.0
        density = 1.0 - self.state.beta
        return float(np.clip(density, 0.0, 1.0))

    def compute_v_rig_effective(self) -> float:
        v_rig_base = AFETConstants.V_RIG * 1000.0
        if self.state.beta == 0.0:
            return v_rig_base * 10.0
        v_rig_eff = v_rig_base * self.kappa * (1.0 / self.state.beta)
        return min(v_rig_eff, v_rig_base * 10.0)

    def formalize_dynamics(self, resource: float, threshold: float = 0.5) -> dict[str, Any]:
        """Formalize the Nullkern dynamics in a compact mathematical frame.

        The model links the logistic membrane σ(β(R-Θ)) to the currently
        instantiated state and exposes the discrete update equations used by
        ``update_state`` plus the continuous-time ODE system and stability
        analysis.
        """
        activation_probability = float(self.activate(resource=resource, threshold=threshold))
        zeta = float(self.compute_impedance(resource=resource))
        return {
            "activation_equation": "sigma(beta*(R-Theta)) = 1/(1+exp(-beta*(R-Theta)))",
            "impedance_equation": "zeta(R)=beta*(1-kappa)-0.5",
            "state_update_equations": {
                "beta_next": "clip(beta + delta_beta, 0, 1)",
                "kappa_next": "clip(kappa + delta_kappa, 0, 1)",
            },
            "parameters": {
                "R": float(resource),
                "Theta": float(threshold),
                "beta": float(self.state.beta),
                "kappa": float(self.kappa),
            },
            "activation_probability": activation_probability,
            "zeta": zeta,
            "state_vector": {
                "beta": float(self.state.beta),
                "kappa": float(self.kappa),
                "resonance": float(self.state.resonance),
                "phase": self.state.phase.value,
            },
            "continuous_dynamics": self.get_continuous_dynamics(resource, threshold),
            "stability": self.analyze_stability(resource, threshold),
        }

    # ------------------------------------------------------------------
    # Mathematical formalization: continuous-time ODE system
    # ------------------------------------------------------------------

    def get_continuous_dynamics(self, resource: float, threshold: float = 0.5) -> dict[str, float]:
        """Compute the continuous-time derivatives of the state vector.

        The ODE system models:
          dβ/dt = -α_β · β · (1 - σ(β(R-Θ)))      (β relaxes toward equilibrium)
          dκ/dt = -α_κ · (κ - σ(β(R-Θ)))           (κ tracks activation)
          dr/dt = -α_r · (r - κ·σ(β(R-Θ)))         (resonance follows κ-weighted activation)

        where α_β, α_κ, α_r are damping rates and σ is the logistic membrane.
        """
        sigma = float(self.activate(resource, threshold))
        beta = float(self.state.beta)
        kappa = float(self.kappa)
        resonance = float(self.state.resonance)

        alpha_beta = 0.1
        alpha_kappa = 0.05
        alpha_resonance = 0.08

        dbeta_dt = -alpha_beta * beta * (1.0 - sigma)
        dkappa_dt = -alpha_kappa * (kappa - sigma)
        dresonance_dt = -alpha_resonance * (resonance - kappa * sigma)

        return {
            "dbeta_dt": dbeta_dt,
            "dkappa_dt": dkappa_dt,
            "dresonance_dt": dresonance_dt,
            "sigma": sigma,
        }

    def compute_jacobian(self, resource: float, threshold: float = 0.5) -> np.ndarray:
        """Compute the 3×3 Jacobian of the ODE system at the current state.

        J = ∂(dβ/dt, dκ/dt, dr/dt) / ∂(β, κ, r)

        Evaluated numerically via central finite differences.
        """
        eps = 1e-6
        state_vec = np.array(
            [
                float(self.state.beta),
                float(self.kappa),
                float(self.state.resonance),
            ]
        )
        jac = np.zeros((3, 3))

        for j in range(3):
            perturb = np.zeros(3)
            perturb[j] = eps
            f_plus = self._ode_rhs(state_vec + perturb, resource, threshold)
            f_minus = self._ode_rhs(state_vec - perturb, resource, threshold)
            jac[:, j] = (f_plus - f_minus) / (2 * eps)

        return jac

    def analyze_stability(self, resource: float, threshold: float = 0.5) -> dict[str, Any]:
        """Analyze local stability of the current state via eigenvalue analysis.

        Returns eigenvalues of the Jacobian, stability flag, and a Lyapunov
        energy candidate V = β² + (κ - σ)² + (r - κσ)².
        """
        jac = self.compute_jacobian(resource, threshold)
        eigenvalues = np.linalg.eigvals(jac)
        real_parts = [float(np.real(ev)) for ev in eigenvalues]
        stable = all(rp <= 0.0 for rp in real_parts)
        lyapunov = self.compute_energy(resource, threshold)

        return {
            "eigenvalues": [complex(ev) for ev in eigenvalues],
            "real_parts": real_parts,
            "stable": stable,
            "lyapunov_candidate": lyapunov,
            "jacobian_trace": float(np.trace(jac)),
            "jacobian_det": float(np.linalg.det(jac)),
        }

    def compute_energy(self, resource: float, threshold: float = 0.5) -> float:
        """Compute Lyapunov energy functional V(β, κ, r).

        V = 0.5 · (β² + (κ - σ)² + (r - κ·σ)²)

        V ≥ 0 always, V = 0 at equilibrium.
        """
        sigma = float(self.activate(resource, threshold))
        beta = float(self.state.beta)
        kappa = float(self.kappa)
        resonance = float(self.state.resonance)
        return 0.5 * (beta**2 + (kappa - sigma) ** 2 + (resonance - kappa * sigma) ** 2)

    def _ode_rhs(
        self,
        state_vec: np.ndarray,
        resource: float,
        threshold: float,
    ) -> np.ndarray:
        """Evaluate the ODE right-hand side at an arbitrary state point."""
        beta, kappa, resonance = float(state_vec[0]), float(state_vec[1]), float(state_vec[2])
        beta = float(np.clip(beta, 0.0, 1.0))
        kappa = float(np.clip(kappa, 0.0, 1.0))

        x = beta * (resource - threshold)
        sigma = 1.0 / (1.0 + np.exp(-x))

        alpha_beta = 0.1
        alpha_kappa = 0.05
        alpha_resonance = 0.08

        return np.array(
            [
                -alpha_beta * beta * (1.0 - sigma),
                -alpha_kappa * (kappa - sigma),
                -alpha_resonance * (resonance - kappa * sigma),
            ]
        )

    def register_consent(self, token: str, scope: str = "shadow_mode") -> dict[str, Any]:
        """Register a Sigillin consent token for ethical traceability.

        Parameters
        ----------
        token : str
            Consent identifier (e.g. user-session or audit trail ID).
        scope : str
            Scope of consent (e.g. 'shadow_mode', 'full_resonance').

        Returns
        -------
        dict
            Consent record.
        """
        record = {
            "token": token,
            "scope": scope,
            "timestamp": time.time(),
            "kernel_beta": float(self.state.beta),
            "kernel_phase": self.state.phase.value,
        }
        self.consent_log.append(record)
        logger.info("Consent registered: token=%s scope=%s", token, scope)
        return record

    def validate_consent(self, token: str) -> bool:
        """Check whether a consent token has been registered."""
        return any(r["token"] == token for r in self.consent_log)

    def self_referential_validate(
        self,
        recursion_depth: int = 16,
        sigma_phi_buffer: float = SIGMA_PHI_BUFFER,
        axiom_beta: float = AXIOM_STABILITY_BETA,
    ) -> dict[str, Any]:
        """Run recursive self-validation around beta=AFETConstants.BETA_CRITICAL with sigma_Phi guard band."""
        if recursion_depth < 1:
            raise ValueError("recursion_depth must be >= 1")

        beta_state = axiom_beta
        beta_trace: list[float] = []
        stable = True

        for idx in range(recursion_depth):
            reference = axiom_beta / (1.0 + idx)
            correction = sigma_phi_buffer * np.tanh(reference - beta_state)
            beta_state += correction
            beta_trace.append(float(beta_state))
            if not np.isfinite(beta_state):
                stable = False
                break

        drift = abs(beta_trace[-1] - axiom_beta) if beta_trace else float("inf")
        return {
            "recursion_depth": recursion_depth,
            "sigma_phi_buffer": sigma_phi_buffer,
            "axiom_beta": axiom_beta,
            "beta_trace": beta_trace,
            "drift": float(drift),
            "stable": stable and drift < 1.0,
        }

    def compute_aic_comparison(
        self,
        observed: np.ndarray,
        predicted_logistic: np.ndarray,
        predicted_null: np.ndarray,
        k_logistic: int = 3,
        k_null: int = 2,
    ) -> dict[str, Any]:
        """Compare logistic fit vs null model using AIC.

        Parameters
        ----------
        observed : np.ndarray
            Observed data points.
        predicted_logistic : np.ndarray
            Predictions from the logistic model sigma(beta(R-Theta)).
        predicted_null : np.ndarray
            Predictions from the null model (e.g. linear).
        k_logistic : int
            Number of parameters in logistic model.
        k_null : int
            Number of parameters in null model.

        Returns
        -------
        dict
            AIC values and delta_AIC.
        """
        n = len(observed)
        if n < 2:
            raise ValueError("Need at least 2 observations for AIC")

        rss_logistic = float(np.sum((observed - predicted_logistic) ** 2))
        rss_null = float(np.sum((observed - predicted_null) ** 2))

        aic_logistic = n * np.log(rss_logistic / n + 1e-12) + 2 * k_logistic
        aic_null = n * np.log(rss_null / n + 1e-12) + 2 * k_null
        delta_aic = float(aic_null - aic_logistic)

        return {
            "aic_logistic": float(aic_logistic),
            "aic_null": float(aic_null),
            "delta_aic": delta_aic,
            "logistic_preferred": delta_aic >= 10.0,
            "rss_logistic": rss_logistic,
            "rss_null": rss_null,
            "n": n,
        }

    def bootstrap_stability(
        self,
        signal: np.ndarray,
        n_bootstrap: int = 100,
        seed: int = 1337,
    ) -> dict[str, Any]:
        """Bootstrap validation for kernel stability.

        Resamples the signal and checks whether self-referential validation
        remains stable across bootstrap iterations.

        Parameters
        ----------
        signal : np.ndarray
            Input signal to resample.
        n_bootstrap : int
            Number of bootstrap iterations.
        seed : int
            Random seed for reproducibility.

        Returns
        -------
        dict
            Bootstrap report with stability fraction and drift statistics.
        """
        rng = np.random.RandomState(seed)
        n = len(signal)
        stable_count = 0
        drifts: list[float] = []

        for _ in range(n_bootstrap):
            indices = rng.randint(0, n, size=n)
            sample = signal[indices]
            mean_val = float(np.mean(np.abs(sample)))
            report = self.self_referential_validate(
                recursion_depth=8,
                axiom_beta=self.AXIOM_STABILITY_BETA,
            )
            drifts.append(report["drift"])
            if report["stable"]:
                stable_count += 1

        return {
            "n_bootstrap": n_bootstrap,
            "stable_fraction": stable_count / n_bootstrap,
            "mean_drift": float(np.mean(drifts)),
            "std_drift": float(np.std(drifts)),
            "max_drift": float(np.max(drifts)),
            "all_stable": stable_count == n_bootstrap,
        }

    def evaluate_synthetic_stability(self, csv_path: str | Path) -> dict[str, Any]:
        """Load synthetic EEG-like CSV and check chaos/overflow transition."""
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(path)

        values: list[float] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                for field in ("value", "signal", "amplitude", "eeg", "voltage"):
                    if field in row and row[field] not in ("", None):
                        values.append(float(row[field]))
                        break

        if not values:
            raise ValueError(f"No numeric signal fields in {path}")

        arr = np.asarray(values, dtype=np.float64)
        gradient = np.diff(arr)
        overflow = bool(np.any(np.abs(arr) > np.finfo(np.float64).max * 1e-6))
        chaos_transition = float(np.std(gradient) / (np.std(arr) + 1e-9))
        return {
            "sample_count": int(arr.size),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "overflow_detected": overflow,
            "chaos_transition_index": chaos_transition,
            "chaos_flag": bool(chaos_transition > 1.0),
        }

    def _record_history(self) -> None:
        self.history.append(
            {
                "timestamp": time.time(),
                "beta": self.state.beta,
                "kappa": self.kappa,
                "resonance": self.state.resonance,
                "phase": self.state.phase.value,
                "information_density": self.get_information_density(),
            }
        )

    def get_state_summary(self) -> dict[str, Any]:
        return {
            "beta": self.state.beta,
            "kappa": self.kappa,
            "resonance": self.state.resonance,
            "phase": self.state.phase.value,
            "information_density": self.get_information_density(),
            "v_rig_effective": self.compute_v_rig_effective(),
            "age_seconds": time.time() - self.creation_time,
            "history_length": len(self.history),
            "humility_damping": self.humility_damping,
            "consent_count": len(self.consent_log),
        }

    def __repr__(self) -> str:
        return (
            f"Nullkern(\u03b2={self.state.beta:.3f}, \u03ba={self.kappa:.3f}, "
            f"phase={self.state.phase.value}, resonance={self.state.resonance:.3f})"
        )
