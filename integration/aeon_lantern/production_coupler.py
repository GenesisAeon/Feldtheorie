"""Production coupler for Aeon-lanternNet integration (Phases 2-3).

Extends the existing AeonLanternHub with:
  - Phase 2: Recursive engine (bardo-phase detection, temporal compression)
  - Phase 3: Shadow integration (anti-mode detection, negentropy feedback)

Usage:
    coupler = ProductionCoupler()
    report = coupler.run_production_test(n_cycles=100, recursion_depth=5)
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field

import numpy as np

from theory.afet import AFETConstants, AFETFramework

EPSILON = 1e-12


# ---------------------------------------------------------------------------
# Phase 2: Recursive Engine
# ---------------------------------------------------------------------------


@dataclass
class RecursiveEngine:
    """Bardo-phase detection and temporal compression.

    Simulates recursive depth exploration and tracks coherence
    decay across recursion levels.
    """

    max_depth: int = 10
    coherence_decay_rate: float = 0.05

    def detect_bardo_phase(self, coherence: float) -> str:
        """Classify coherence into bardo phases.

        Phases:
          - chikhai: coherence > 0.8 (clear light)
          - chonyid: 0.4 < coherence <= 0.8 (visions)
          - sidpa: coherence <= 0.4 (rebirth)
        """
        if coherence > 0.8:
            return "chikhai"
        if coherence > 0.4:
            return "chonyid"
        return "sidpa"

    def run_recursion(
        self,
        signal: np.ndarray,
        depth: int,
        seed: int = 42,
    ) -> dict:
        """Simulate recursive processing with coherence tracking."""
        rng = np.random.default_rng(seed)
        actual_depth = min(depth, self.max_depth)
        coherence = 1.0
        iterations = []

        for d in range(actual_depth):
            noise = rng.normal(0, self.coherence_decay_rate)
            coherence = max(0.0, min(1.0, coherence - self.coherence_decay_rate + noise))
            phase = self.detect_bardo_phase(coherence)

            iterations.append({
                "depth": d,
                "coherence": round(coherence, 6),
                "phase": phase,
            })

        return {
            "requested_depth": depth,
            "actual_depth": actual_depth,
            "final_coherence": round(coherence, 6),
            "final_phase": self.detect_bardo_phase(coherence),
            "iterations": iterations,
        }

    def temporal_compression(
        self,
        steps: int = 10,
        compression_factor: float = 2.0,
    ) -> dict:
        """Simulate temporal compression metrics."""
        offsets = []
        v_rig = AFETConstants.V_RIG
        for i in range(steps):
            offset = v_rig * (compression_factor ** (i / steps))
            offsets.append(round(offset, 6))

        return {
            "steps": steps,
            "compression_factor": compression_factor,
            "mean_offset": round(float(np.mean(offsets)), 6),
            "offsets": offsets,
        }


# ---------------------------------------------------------------------------
# Phase 3: Shadow Integration
# ---------------------------------------------------------------------------


@dataclass
class ShadowIntegration:
    """Anti-mode detection and negentropy feedback."""

    anti_mode_threshold: float = 0.3
    negentropy_gain: float = 0.1

    def detect_anti_mode(self, signal: np.ndarray) -> dict:
        """Detect anti-mode patterns in the signal.

        Anti-modes are regions where the signal inverts relative to
        its mean, indicating potential instability.
        """
        arr = np.asarray(signal, dtype=np.float64)
        mean = float(np.mean(arr))
        inverted = np.sum(np.sign(arr - mean) != np.sign(mean)) / max(len(arr), 1)
        is_anti_mode = float(inverted) > self.anti_mode_threshold

        return {
            "inversion_ratio": round(float(inverted), 6),
            "threshold": self.anti_mode_threshold,
            "is_anti_mode": is_anti_mode,
            "mean_signal": round(mean, 6),
        }

    def negentropy_feedback(self, coherence: float, sigma_phi: float) -> dict:
        """Compute negentropy feedback to stabilize the system.

        Negentropy is the complement of entropy — it represents order.
        When sigma_phi drops, negentropy feedback increases to stabilize.
        """
        threshold = AFETConstants.SIGMA_PHI
        deficit = max(0.0, threshold - sigma_phi)
        correction = deficit * self.negentropy_gain * coherence

        return {
            "sigma_phi": round(sigma_phi, 6),
            "coherence": round(coherence, 6),
            "deficit": round(deficit, 6),
            "correction": round(correction, 6),
            "stabilized_sigma_phi": round(sigma_phi + correction, 6),
        }

    def frame_stabilization(self, frames: list[np.ndarray]) -> dict:
        """Stabilize a sequence of signal frames."""
        sigma_phis = []
        anti_modes = 0

        for frame in frames:
            arr = np.asarray(frame, dtype=np.float64).flatten()
            mean = float(np.mean(arr))
            std = float(np.std(arr, ddof=0))
            sigma = std / max(abs(mean), EPSILON)
            sigma_phis.append(sigma)

            detection = self.detect_anti_mode(frame)
            if detection["is_anti_mode"]:
                anti_modes += 1

        arr_sigma = np.array(sigma_phis)
        return {
            "n_frames": len(frames),
            "mean_sigma_phi": round(float(np.mean(arr_sigma)), 6),
            "std_sigma_phi": round(float(np.std(arr_sigma)), 6),
            "anti_modes_detected": anti_modes,
            "stability": round(1.0 - anti_modes / max(len(frames), 1), 4),
        }


# ---------------------------------------------------------------------------
# Production Coupler
# ---------------------------------------------------------------------------


@dataclass
class ProductionCoupler:
    """Full production coupler integrating Phases 1-3.

    Phase 1 (basis coupling) is handled by AeonLanternHub.
    This class adds Phase 2 (recursive engine) and Phase 3 (shadow integration).
    """

    recursive_engine: RecursiveEngine = field(default_factory=RecursiveEngine)
    shadow: ShadowIntegration = field(default_factory=ShadowIntegration)
    afet: AFETFramework = field(default_factory=AFETFramework)

    def run_production_test(
        self,
        n_cycles: int = 100,
        recursion_depth: int = 5,
        seed: int = 42,
    ) -> dict:
        """Full production integration test.

        Runs n_cycles resonance cycles with recursive depth and shadow
        integration. Tracks sigma_Phi stability throughout.
        """
        rng = np.random.default_rng(seed)
        t0 = time.time()

        cycle_results = []
        sigma_phis = []
        crashes = 0

        for i in range(n_cycles):
            # Generate signal
            signal = np.sin(
                2 * np.pi * AFETConstants.FREQ_RES * np.linspace(0, 1, 256)
            )
            signal += rng.normal(0, 0.05, size=256)

            # Phase 2: recursive processing
            recursion = self.recursive_engine.run_recursion(
                signal, recursion_depth, seed=seed + i
            )

            # Phase 3: shadow detection
            anti_mode = self.shadow.detect_anti_mode(signal)
            sigma = float(np.std(signal) / max(abs(float(np.mean(signal))), EPSILON))
            sigma_phis.append(sigma)

            feedback = self.shadow.negentropy_feedback(
                recursion["final_coherence"], sigma
            )

            # Check for crash (sigma_phi below critical)
            if sigma < 0.055:
                crashes += 1

            cycle_results.append({
                "cycle": i,
                "sigma_phi": round(sigma, 6),
                "coherence": recursion["final_coherence"],
                "phase": recursion["final_phase"],
                "anti_mode": anti_mode["is_anti_mode"],
            })

        elapsed = time.time() - t0
        arr = np.array(sigma_phis)

        return {
            "n_cycles": n_cycles,
            "recursion_depth": recursion_depth,
            "elapsed_seconds": round(elapsed, 2),
            "crashes": crashes,
            "mean_sigma_phi": round(float(np.mean(arr)), 6),
            "std_sigma_phi": round(float(np.std(arr)), 6),
            "min_sigma_phi": round(float(np.min(arr)), 6),
            "max_sigma_phi": round(float(np.max(arr)), 6),
            "mean_coherence": round(
                float(np.mean([c["coherence"] for c in cycle_results])), 6
            ),
            "stable": crashes == 0,
            "summary": cycle_results[:10],  # first 10 for brevity
        }
