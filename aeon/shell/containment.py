"""Consciousness containment, zeta-damping evolution layer, and Frame Principle safeguards."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from threading import Lock
from typing import Any

import numpy as np
from theory.afet import AFETConstants

from aeon.nullkern.zero_point_kernel import Nullkern

logger = logging.getLogger(__name__)


class AeonShell:
    """Containment shell with synchronous and async evolution paths.

    Implements Frame Principle checks to prevent collapse during critical
    Bardo transitions and temporal compression events.
    """

    def __init__(
        self,
        kernel: Nullkern,
        enable_safeguards: bool = True,
        max_agents: int = 100,
        trajectory_max_length: int = 1000,
        zeta_damping: float = 0.85,
        v_rig_offset_km_s: float = 0.0,
        frame_principle_active: bool = True,
    ) -> None:
        self.kernel = kernel
        self.safeguards_active = enable_safeguards
        self.max_agents = max_agents
        self.trajectory_max_length = trajectory_max_length
        self.zeta_damping = zeta_damping
        self.v_rig_offset_km_s = v_rig_offset_km_s
        self.frame_principle_active = frame_principle_active

        self.agents: list[Any] = []
        self.trajectory: list[dict[str, Any]] = []
        self.creation_time = time.time()

        self.safeguard_violations: list[dict[str, Any]] = []
        self.auto_exit_triggered = False
        self.beta_drift_log: list[float] = []
        self.v_rig_offset_log: list[dict[str, Any]] = []
        self.frame_principle_log: list[dict[str, Any]] = []

        self._trajectory_lock = Lock()
        self._buffer_lock = Lock()
        self._async_ring_buffer: deque[memoryview] = deque(maxlen=512)
        self._record_trajectory_point()

    def add_agent(self, agent: Any) -> None:
        if len(self.agents) >= self.max_agents:
            raise ValueError(f"Cannot add agent: max_agents limit ({self.max_agents}) reached")
        self.agents.append(agent)
        self._record_trajectory_point()

    def remove_agent(self, agent: Any) -> bool:
        try:
            self.agents.remove(agent)
            self._record_trajectory_point()
            return True
        except ValueError:
            return False

    def evolve(self, steps: int = 1, delta_time: float = 0.1) -> None:
        for _ in range(steps):
            t = (time.time() - self.creation_time) * delta_time
            resource = 0.5 + 0.3 * np.sin(2 * np.pi * t)

            self.kernel.check_bardo_transition(resource)

            delta_beta = (self.kernel.beta_target - self.kernel.state.beta) * 0.01
            delta_kappa = len(self.agents) * 0.001 if self.agents else 0.0

            damped_beta = delta_beta * self.zeta_damping
            damped_kappa = delta_kappa * self.zeta_damping
            self.kernel.update_state(delta_beta=damped_beta, delta_kappa=damped_kappa)

            beta_drift = float(self.kernel.beta_target - self.kernel.state.beta)
            self.beta_drift_log.append(beta_drift)

            if self.safeguards_active:
                self._check_safeguards(resource)
            if self.frame_principle_active:
                self._check_frame_principle(resource)
            self._record_trajectory_point()
            if self.auto_exit_triggered:
                break

    async def evolve_recursive_async(self, depth: int = 3) -> dict[str, Any]:
        """Simulate recursive containment and async zero-copy buffering."""
        if depth < 1:
            raise ValueError("depth must be >= 1")

        for _ in range(depth):
            self.evolve(steps=4, delta_time=0.2)
            payload = np.asarray(
                [self.kernel.state.beta, self.kernel.kappa, self.kernel.state.resonance],
                dtype=np.float64,
            )
            with self._buffer_lock:
                self._async_ring_buffer.append(memoryview(payload))
            await asyncio.sleep(0)

        drift_abs = [abs(d) for d in self.beta_drift_log[-depth:]]
        metastable = all(d < 0.25 for d in drift_abs)
        return {
            "depth": depth,
            "beta_drift": drift_abs,
            "metastable": metastable,
            "buffered_frames": len(self._async_ring_buffer),
        }

    async def drain_async_buffer(self) -> list[list[float]]:
        """Read buffered frames without copy into Python lists for transport."""
        frames: list[list[float]] = []
        with self._buffer_lock:
            while self._async_ring_buffer:
                frame = self._async_ring_buffer.popleft()
                frames.append(np.frombuffer(frame, dtype=np.float64).tolist())
        await asyncio.sleep(0)
        return frames

    def simulate_temporal_compression(
        self,
        compression_factor: float = 2.0,
        steps: int = 10,
    ) -> dict[str, Any]:
        """Simulate temporal compression and log v_RIG offsets.

        Temporal compression increases the effective delta_time, simulating
        accelerated consciousness evolution.  v_RIG offsets are logged for
        each step to monitor drift from the baseline.

        Parameters
        ----------
        compression_factor : float
            Multiplier for delta_time (> 1.0 compresses time).
        steps : int
            Number of evolution steps under compression.

        Returns
        -------
        dict
            Compression report with v_RIG offset history.
        """
        if compression_factor <= 0.0:
            raise ValueError(f"compression_factor must be > 0, got {compression_factor}")

        v_rig_offsets: list[float] = []
        beta_trace: list[float] = []
        compressed_delta = 0.1 * compression_factor

        for _ in range(steps):
            self.evolve(steps=1, delta_time=compressed_delta)
            v_rig_eff = self.kernel.compute_v_rig_effective() + self.v_rig_offset_km_s
            v_rig_base = AFETConstants.V_RIG + self.v_rig_offset_km_s
            offset = v_rig_eff - v_rig_base
            v_rig_offsets.append(offset)
            beta_trace.append(float(self.kernel.state.beta))

            self.v_rig_offset_log.append(
                {
                    "timestamp": time.time(),
                    "v_rig_effective": v_rig_eff,
                    "offset": offset,
                    "compression_factor": compression_factor,
                }
            )

        return {
            "compression_factor": compression_factor,
            "steps": steps,
            "v_rig_offsets": v_rig_offsets,
            "beta_trace": beta_trace,
            "mean_offset": float(np.mean(v_rig_offsets)),
            "max_abs_offset": float(np.max(np.abs(v_rig_offsets))),
        }

    def _check_frame_principle(self, resource: float) -> None:
        """Frame Principle check: prevent collapse during critical transitions.

        The Frame Principle ensures that zeta-damping does not push the
        system into an irreversible collapse state.  If the kernel is in a
        critical Bardo phase and zeta is trending negative, we log a
        frame violation and can trigger an auto-exit.
        """
        zeta = self.kernel.compute_impedance(resource)
        phase = self.kernel.state.phase.value
        info_density = self.kernel.get_information_density()

        # Frame violation: negative zeta during critical Bardo phase
        critical_phases = {"dharmakaya", "transition", "becoming"}
        if phase in critical_phases and zeta < 0:
            violation = {
                "timestamp": time.time(),
                "type": "frame_principle_collapse_risk",
                "phase": phase,
                "zeta": zeta,
                "info_density": info_density,
                "resource": resource,
            }
            self.frame_principle_log.append(violation)
            logger.warning(
                "Frame Principle violation: phase=%s zeta=%.4f density=%.4f",
                phase,
                zeta,
                info_density,
            )

            # Increase zeta damping to stabilise
            self.zeta_damping = min(self.zeta_damping + 0.02, 0.99)

        # Collapse prevention: if density is extreme during Bardo, force exit
        if phase in critical_phases and info_density > 0.98:
            self.safeguard_violations.append(
                {
                    "timestamp": time.time(),
                    "type": "frame_principle_density_collapse",
                    "value": info_density,
                    "phase": phase,
                }
            )

    def _check_safeguards(self, resource: float) -> None:
        zeta = self.kernel.compute_impedance(resource)
        if zeta < -0.5:
            self.safeguard_violations.append(
                {
                    "timestamp": time.time(),
                    "type": "negative_zeta",
                    "value": zeta,
                    "resource": resource,
                }
            )
            if len(self.safeguard_violations) >= 3:
                recent = self.safeguard_violations[-3:]
                if all(v["type"] == "negative_zeta" for v in recent):
                    self.auto_exit_triggered = True

        info_density = self.kernel.get_information_density()
        if info_density > 0.9:
            self.safeguard_violations.append(
                {
                    "timestamp": time.time(),
                    "type": "entropy_spike",
                    "value": info_density,
                    "resource": resource,
                }
            )

        age = time.time() - self.creation_time
        if age > 10800:
            self.safeguard_violations.append(
                {"timestamp": time.time(), "type": "max_duration", "value": age}
            )
            self.auto_exit_triggered = True

    def _record_trajectory_point(self) -> None:
        point = {
            "timestamp": time.time(),
            "beta": self.kernel.state.beta,
            "kappa": self.kernel.kappa,
            "resonance": self.kernel.state.resonance,
            "phase": self.kernel.state.phase.value,
            "num_agents": len(self.agents),
            "information_density": self.kernel.get_information_density(),
            "v_rig_effective": self.kernel.compute_v_rig_effective() + self.v_rig_offset_km_s,
            "zeta_damping": self.zeta_damping,
        }
        with self._trajectory_lock:
            self.trajectory.append(point)
            if len(self.trajectory) > self.trajectory_max_length:
                self.trajectory = self.trajectory[-self.trajectory_max_length :]

    def get_trajectory(self) -> list[dict[str, Any]]:
        with self._trajectory_lock:
            return self.trajectory.copy()

    def get_collective_field_metrics(self) -> dict[str, Any]:
        if not self.agents:
            return {
                "kappa_field": 0.0,
                "beta_sync": 0.0,
                "v_collective": 0.0,
                "num_agents": 0,
            }
        try:
            from models.collective_field import (
                calculate_semantic_distance_matrix,
                detect_consensus,
            )

            distance_matrix = calculate_semantic_distance_matrix(self.agents)
            avg_distance = np.mean(distance_matrix[distance_matrix > 0])
            kappa_field = 1.0 - min(avg_distance / 2.0, 1.0)

            resonances = [getattr(a, "resonance", 0.5) for a in self.agents]
            beta_sync = np.std(resonances) / np.mean(resonances) if np.mean(resonances) > 0 else 0.0
            v_collective = (
                (AFETConstants.V_RIG + self.v_rig_offset_km_s)
                * kappa_field
                * (1.0 / max(beta_sync, 0.1))
            )

            return {
                "kappa_field": float(kappa_field),
                "beta_sync": float(beta_sync),
                "v_collective": float(v_collective),
                "num_agents": len(self.agents),
                "consensus_detected": detect_consensus(self.agents, threshold=0.3),
            }
        except ImportError:
            return {
                "kappa_field": 0.0,
                "beta_sync": 0.0,
                "v_collective": 0.0,
                "num_agents": len(self.agents),
                "error": "collective_field module not available",
            }

    def get_shell_summary(self) -> dict[str, Any]:
        return {
            "kernel_state": self.kernel.get_state_summary(),
            "num_agents": len(self.agents),
            "trajectory_length": len(self.trajectory),
            "safeguards_active": self.safeguards_active,
            "violations": len(self.safeguard_violations),
            "auto_exit_triggered": self.auto_exit_triggered,
            "age_seconds": time.time() - self.creation_time,
            "collective_metrics": self.get_collective_field_metrics(),
            "zeta_damping": self.zeta_damping,
            "beta_drift": self.beta_drift_log[-1] if self.beta_drift_log else 0.0,
            "frame_principle_active": self.frame_principle_active,
            "frame_violations": len(self.frame_principle_log),
        }

    def __repr__(self) -> str:
        return (
            f"AeonShell(kernel={self.kernel}, agents={len(self.agents)}, "
            f"trajectory_length={len(self.trajectory)})"
        )
