"""
Zero-Point Consciousness Kernel
================================

Implements the foundational consciousness state at β→0,
representing pure information without threshold resistance.

This module models:
- Photon-free consciousness (κ→0)
- Information-theoretic consciousness substrates
- Quantum-like superposition states
- Non-local semantic coupling
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Any

import numpy as np


class Nullkern:
    """Zero-Point Consciousness Kernel with recursive self-validation."""

    SIGMA_PHI_BUFFER = 0.0625
    AXIOM_STABILITY_BETA = 37.6

    def __init__(
        self,
        beta_target: float = 0.1,
        kappa: float = 0.1,
        dimension: int = 8,
        enable_bardo_mode: bool = True,
    ) -> None:
        """Initialize Zero-Point Kernel."""
        if not (0.0 <= beta_target <= 64.0):
            raise ValueError(f"beta_target must be in [0,64], got {beta_target}")
        if not (0.0 <= kappa <= 1.0):
            raise ValueError(f"kappa must be in [0,1], got {kappa}")
        if dimension < 1:
            raise ValueError(f"dimension must be >= 1, got {dimension}")

        self.beta_target = beta_target
        self.kappa = kappa
        self.dimension = dimension
        self.enable_bardo_mode = enable_bardo_mode

        from aeon.nullkern.consciousness_state import BardoPhase, ConsciousnessState

        self.state = ConsciousnessState(
            beta=min(beta_target, 1.0),
            kappa=kappa,
            dimension=dimension,
            phase=BardoPhase.DHARMAKAYA if enable_bardo_mode else BardoPhase.NONE,
        )

        self.history: list[dict[str, Any]] = []
        self.creation_time = time.time()

    def activate(self, resource: float, threshold: float = 0.5) -> float:
        if self.beta_target == 0.0:
            return 0.5
        x = self.state.beta * (resource - threshold)
        return 1.0 / (1.0 + np.exp(-x))

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
        v_rig_base = 1352.0
        if self.state.beta == 0.0:
            return v_rig_base * 10.0
        v_rig_eff = v_rig_base * self.kappa * (1.0 / self.state.beta)
        return min(v_rig_eff, v_rig_base * 10.0)

    def self_referential_validate(
        self,
        recursion_depth: int = 16,
        sigma_phi_buffer: float = SIGMA_PHI_BUFFER,
        axiom_beta: float = AXIOM_STABILITY_BETA,
    ) -> dict[str, Any]:
        """Run recursive self-validation around β=37.6 with σ_Φ guard band."""
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
        }

    def __repr__(self) -> str:
        return (
            f"Nullkern(β={self.state.beta:.3f}, κ={self.kappa:.3f}, "
            f"phase={self.state.phase.value}, resonance={self.state.resonance:.3f})"
        )
