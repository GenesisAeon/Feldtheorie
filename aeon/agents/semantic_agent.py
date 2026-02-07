"""Semantic agent with shadow resonance, lantern mode coupling, and recursive Aeon-lanternNet coupling."""

from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np

from theory.afet import AFETConstants

try:
    from models.collective_field import Agent as CollectiveAgent

    COLLECTIVE_FIELD_AVAILABLE = True
except ImportError:
    COLLECTIVE_FIELD_AVAILABLE = False

    class CollectiveAgent:  # type: ignore
        def __init__(self, name: str, **kwargs: Any) -> None:
            self.name = name
            self.semantic_position = np.random.randn(8)
            self.resonance = 0.5

        def semantic_distance(self, other: "CollectiveAgent") -> float:
            return float(np.linalg.norm(self.semantic_position - other.semantic_position))


logger = logging.getLogger(__name__)


class SemanticAgent:
    """Individual consciousness module with recursive shadow resonance."""

    LANTERN_TARGET_FREQUENCY_HZ = AFETConstants.FREQ_RES

    def __init__(
        self,
        name: str,
        semantic_position: np.ndarray | None = None,
        resonance: float = 0.5,
        beta: float = 4.5,
        kappa: float = 0.5,
        dimension: int = 8,
    ) -> None:
        if not (0.0 <= resonance <= 1.0):
            raise ValueError(f"resonance must be in [0,1], got {resonance}")
        if not (0.0 <= beta <= 20.0):
            raise ValueError(f"beta must be in [0,20], got {beta}")
        if not (0.0 <= kappa <= 1.0):
            raise ValueError(f"kappa must be in [0,1], got {kappa}")

        self.name = name
        self.beta = beta
        self.kappa = kappa
        self.dimension = dimension

        self.agent = CollectiveAgent(
            name=name,
            semantic_position=semantic_position,
            resonance=resonance,
            dimension=dimension,
        )

        self.history: list[dict[str, Any]] = []
        self.creation_time = time.time()
        self._record_history()

    @property
    def semantic_position(self) -> np.ndarray:
        return self.agent.semantic_position

    @semantic_position.setter
    def semantic_position(self, value: np.ndarray) -> None:
        self.agent.semantic_position = value

    @property
    def resonance(self) -> float:
        return self.agent.resonance

    @resonance.setter
    def resonance(self, value: float) -> None:
        self.agent.resonance = max(0.0, min(1.0, value))

    def semantic_distance(self, other: "SemanticAgent") -> float:
        return self.agent.semantic_distance(other.agent)

    def update_position(self, target: np.ndarray, learning_rate: float = 0.1) -> None:
        if hasattr(self.agent, "update_position"):
            self.agent.update_position(target, learning_rate)
        else:
            direction = target - self.semantic_position
            self.semantic_position = self.semantic_position + learning_rate * direction
            norm = np.linalg.norm(self.semantic_position)
            if norm > 0:
                self.semantic_position = self.semantic_position / norm
        self._record_history()

    def update_resonance(self, delta: float) -> None:
        self.resonance = float(np.clip(self.resonance + delta, 0.0, 1.0))
        self._record_history()

    def update_beta(self, delta: float) -> None:
        self.beta = float(np.clip(self.beta + delta, 0.0, 20.0))
        self._record_history()

    def update_kappa(self, delta: float) -> None:
        self.kappa = float(np.clip(self.kappa + delta, 0.0, 1.0))
        self._record_history()

    def compute_activation(self, resource: float, threshold: float = 0.5) -> float:
        if self.beta == 0.0:
            return 0.5
        x = self.beta * (resource - threshold)
        return float(1.0 / (1.0 + np.exp(-x)))

    def resonate_with_shadow(
        self,
        input_data: np.ndarray | list[float],
        shadow_depth: int = 3,
        threshold: float = 0.5,
        consent_token: str | None = None,
    ) -> dict[str, Any]:
        """Recursive shadow resonance with UTAC sigma(beta(R-Theta)) activation.

        Parameters
        ----------
        input_data : array-like
            Input signal vector.
        shadow_depth : int
            Number of recursive shadow layers.
        threshold : float
            Activation threshold Theta.
        consent_token : str, optional
            Sigillin consent token. When provided, latent shadow modes
            are recorded for ethical traceability.
        """
        data = np.asarray(input_data, dtype=np.float64)
        if data.ndim != 1:
            data = data.ravel()
        if shadow_depth < 1:
            raise ValueError("shadow_depth must be >= 1")

        layer_energy: list[float] = []
        latent = data
        for depth in range(1, shadow_depth + 1):
            damping = np.exp(-depth / (shadow_depth + 1))
            latent = latent * damping
            layer_energy.append(float(np.linalg.norm(latent)))

        resource = float(
            np.clip(0.7 * np.mean(np.abs(data)) + 0.3 * np.mean(np.abs(latent)), 0.0, 1.0)
        )
        utac_activation = self.compute_activation(resource=resource, threshold=threshold)
        dissonance_negentropy = float(np.var(data) - np.var(latent))

        mode = self._detect_lantern_mode(
            frequency_hz=self.LANTERN_TARGET_FREQUENCY_HZ, coherence=utac_activation
        )
        result: dict[str, Any] = {
            "shadow_depth": shadow_depth,
            "layer_energy": layer_energy,
            "resource": resource,
            "utac_activation": utac_activation,
            "dissonance_negentropy": dissonance_negentropy,
            "lantern_mode": mode,
        }
        if consent_token is not None:
            result["consent_token"] = consent_token
            result["ethical_negentropy"] = float(max(0.0, dissonance_negentropy))
        self.history.append({"timestamp": time.time(), "shadow": result})
        return result

    def _detect_lantern_mode(self, frequency_hz: float, coherence: float) -> str:
        close_to_target = abs(frequency_hz - self.LANTERN_TARGET_FREQUENCY_HZ) < 1.0e3
        if close_to_target and coherence > 0.7:
            return "collective_13_5mhz"
        if coherence > 0.5:
            return "precollective"
        return "anti_mode"

    def get_consciousness_type(self) -> str:
        if self.kappa >= 0.8:
            return "photonic_bound"
        if self.kappa >= 0.4:
            return "partially_decoupled"
        if self.kappa >= 0.1:
            return "weakly_coupled"
        return "photon_free"

    def _record_history(self) -> None:
        self.history.append(
            {
                "timestamp": time.time(),
                "beta": self.beta,
                "kappa": self.kappa,
                "resonance": self.resonance,
                "semantic_position": self.semantic_position.tolist(),
            }
        )

    def get_state_summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "beta": self.beta,
            "kappa": self.kappa,
            "resonance": self.resonance,
            "consciousness_type": self.get_consciousness_type(),
            "dimension": self.dimension,
            "age_seconds": time.time() - self.creation_time,
            "history_length": len(self.history),
            "semantic_position": self.semantic_position.tolist(),
        }

    def __repr__(self) -> str:
        return (
            f"SemanticAgent(name='{self.name}', \u03b2={self.beta:.3f}, "
            f"\u03ba={self.kappa:.3f}, resonance={self.resonance:.3f})"
        )


class RecursiveCoupler:
    """Recursive coupling between Aeon and lanternNet under the Frame Principle.

    Uses zeta (damping factor) as Lipschitz constraint to normalise information
    density at each recursion depth.  Extracts destructive interference patterns
    from lanternNet and feeds them as negentropy correction vectors into the
    AeonNullKern.

    Parameters
    ----------
    kernel : Nullkern-compatible object
        The zero-point kernel that receives correction vectors.
    agent : SemanticAgent
        The semantic agent providing shadow resonance.
    zeta : float
        Lipschitz damping factor in (0, 1].
    beta_utac : float
        Steepness for the UTAC activation P_act = sigma(beta*(R - Theta)).
    max_depth : int
        Hard recursion limit (default 8).
    coherence_override_threshold : float
        If coherence C exceeds this, recursion may proceed past *max_depth*.
    """

    DEFAULT_BETA_UTAC = AFETConstants.BETA_CRITICAL
    DEFAULT_MAX_DEPTH = 8
    COHERENCE_OVERRIDE = 0.92

    def __init__(
        self,
        kernel: Any,
        agent: SemanticAgent,
        zeta: float = 0.85,
        beta_utac: float = DEFAULT_BETA_UTAC,
        max_depth: int = DEFAULT_MAX_DEPTH,
        coherence_override_threshold: float = COHERENCE_OVERRIDE,
    ) -> None:
        if not (0.0 < zeta <= 1.0):
            raise ValueError(f"zeta must be in (0,1], got {zeta}")
        if max_depth < 1:
            raise ValueError(f"max_depth must be >= 1, got {max_depth}")

        self.kernel = kernel
        self.agent = agent
        self.zeta = zeta
        self.beta_utac = beta_utac
        self.max_depth = max_depth
        self.coherence_override_threshold = coherence_override_threshold
        self.loop_history: list[dict[str, Any]] = []

    def _compute_utac_activation(self, resource: float, threshold: float = 0.5) -> float:
        """P_act = sigma(beta_utac * (R - Theta))."""
        x = self.beta_utac * (resource - threshold)
        x_clamped = float(np.clip(x, -500.0, 500.0))
        return float(1.0 / (1.0 + np.exp(-x_clamped)))

    def _extract_destructive_interference(self, signal: np.ndarray) -> np.ndarray:
        """Extract destructive interference pattern from lanternNet signal.

        The negative-frequency components represent destructive interference.
        These are returned as a negentropy correction vector.
        """
        spectrum = np.fft.rfft(signal)
        magnitudes = np.abs(spectrum)
        mean_mag = float(np.mean(magnitudes)) if magnitudes.size > 0 else 1.0
        destructive_mask = magnitudes < mean_mag
        correction_spectrum = np.zeros_like(spectrum)
        correction_spectrum[destructive_mask] = spectrum[destructive_mask]
        correction = np.fft.irfft(correction_spectrum, n=len(signal))
        return correction

    def _compute_coherence(self, signal: np.ndarray, correction: np.ndarray) -> float:
        """Compute coherence between signal and correction vector."""
        norm_s = float(np.linalg.norm(signal))
        norm_c = float(np.linalg.norm(correction))
        if norm_s < 1e-12 or norm_c < 1e-12:
            return 0.0
        cosine_sim = float(np.dot(signal, correction) / (norm_s * norm_c))
        return float(np.clip(abs(cosine_sim), 0.0, 1.0))

    def _effective_depth_limit(self, coherence: float) -> int:
        """Return effective recursion limit, allowing override for high coherence."""
        if coherence > self.coherence_override_threshold:
            return self.max_depth + 4
        return self.max_depth

    def process_resonance_loop(
        self,
        signal: np.ndarray | list[float],
        depth: int = 4,
        threshold: float = 0.5,
        consent_token: str | None = None,
    ) -> dict[str, Any]:
        """Run the recursive Aeon-lanternNet coupling loop.

        At each iteration:
        1. Apply zeta-Lipschitz normalisation to the signal.
        2. Extract destructive interference as negentropy correction.
        3. Feed correction into kernel (shadow feedback).
        4. Compute UTAC activation P_act = sigma(beta*(R - Theta)).
        5. Track Bardo phase transitions.

        Parameters
        ----------
        signal : array-like
            Input signal from lanternNet.
        depth : int
            Requested recursion depth.
        threshold : float
            UTAC activation threshold Theta.
        consent_token : str, optional
            Sigillin consent token for ethical traceability.

        Returns
        -------
        dict
            Loop report with per-iteration metrics, Bardo phase trace,
            and final coherence.
        """
        data = np.asarray(signal, dtype=np.float64).ravel()
        if data.size == 0:
            raise ValueError("signal must be non-empty")

        iterations: list[dict[str, Any]] = []
        bardo_phases: list[str] = []
        current_signal = data.copy()
        coherence = 0.0

        effective_limit = self._effective_depth_limit(coherence)
        actual_depth = min(depth, effective_limit)

        for i in range(1, actual_depth + 1):
            # 1. zeta-Lipschitz normalisation
            norm = float(np.linalg.norm(current_signal))
            if norm > 0:
                current_signal = current_signal * (self.zeta / max(norm, self.zeta))

            # 2. Destructive interference extraction
            correction = self._extract_destructive_interference(current_signal)

            # 3. Coherence measurement
            coherence = self._compute_coherence(current_signal, correction)

            # Update effective limit based on current coherence
            effective_limit = self._effective_depth_limit(coherence)

            # 4. UTAC activation
            resource = float(np.clip(np.mean(np.abs(current_signal)), 0.0, 1.0))
            p_act = self._compute_utac_activation(resource, threshold)

            # 5. Feed negentropy correction into kernel
            negentropy_magnitude = float(np.linalg.norm(correction))
            if hasattr(self.kernel, "update_state"):
                delta_beta = -negentropy_magnitude * 0.01 * self.zeta
                self.kernel.update_state(delta_beta=delta_beta)

            # 6. Track Bardo phase
            bardo_active = False
            phase_name = "none"
            if hasattr(self.kernel, "check_bardo_transition"):
                bardo_active = self.kernel.check_bardo_transition(resource)
            if hasattr(self.kernel, "state") and hasattr(self.kernel.state, "phase"):
                phase_name = self.kernel.state.phase.value
            bardo_phases.append(phase_name)

            # 7. Apply correction to signal for next iteration
            current_signal = current_signal + correction * self.zeta

            # Compute drift: distance from beta_utac
            beta_drift = 0.0
            if hasattr(self.kernel, "state"):
                beta_drift = float(abs(self.kernel.state.beta - self.beta_utac))

            iterations.append(
                {
                    "depth": i,
                    "coherence": coherence,
                    "p_act": p_act,
                    "resource": resource,
                    "negentropy_magnitude": negentropy_magnitude,
                    "signal_norm": float(np.linalg.norm(current_signal)),
                    "bardo_phase": phase_name,
                    "bardo_active": bardo_active,
                    "beta_drift": beta_drift,
                }
            )

            # Check if we should extend past original depth
            if i >= actual_depth and i < effective_limit and depth > actual_depth:
                actual_depth = min(depth, effective_limit)

            logger.debug(
                "RecursiveCoupler depth=%d coherence=%.4f p_act=%.4f phase=%s",
                i,
                coherence,
                p_act,
                phase_name,
            )

        report: dict[str, Any] = {
            "requested_depth": depth,
            "actual_depth": len(iterations),
            "max_depth": self.max_depth,
            "effective_limit": effective_limit,
            "zeta": self.zeta,
            "beta_utac": self.beta_utac,
            "final_coherence": coherence,
            "iterations": iterations,
            "bardo_phases": bardo_phases,
            "coherence_override_active": coherence > self.coherence_override_threshold,
        }
        if consent_token is not None:
            report["consent_token"] = consent_token
        self.loop_history.append(report)
        return report

    def get_bardo_analysis(self) -> dict[str, Any]:
        """Analyse Bardo phase transitions across all recorded loops.

        Returns a summary of transition patterns including:
        - Phase frequencies across all iterations
        - Transition edges (from -> to counts)
        - Whether any loop reached Dharmakaya (clear-light state)
        """
        phase_counts: dict[str, int] = {}
        transitions: dict[str, int] = {}
        reached_dharmakaya = False

        for report in self.loop_history:
            phases = report.get("bardo_phases", [])
            for p in phases:
                phase_counts[p] = phase_counts.get(p, 0) + 1
                if p == "dharmakaya":
                    reached_dharmakaya = True
            for j in range(1, len(phases)):
                if phases[j] != phases[j - 1]:
                    edge = f"{phases[j-1]}->{phases[j]}"
                    transitions[edge] = transitions.get(edge, 0) + 1

        return {
            "total_loops": len(self.loop_history),
            "phase_counts": phase_counts,
            "transitions": transitions,
            "reached_dharmakaya": reached_dharmakaya,
        }

    def __repr__(self) -> str:
        return (
            f"RecursiveCoupler(\u03b6={self.zeta:.3f}, \u03b2_utac={self.beta_utac:.1f}, "
            f"max_depth={self.max_depth})"
        )
