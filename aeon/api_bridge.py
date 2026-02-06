"""FastAPI bridges for Aeon shell and high-throughput lantern coupling."""

from __future__ import annotations

import asyncio
import time
from dataclasses import asdict, dataclass
from multiprocessing import shared_memory
from threading import Lock
from typing import Any

import numpy as np

try:
    from fastapi import APIRouter, WebSocket, WebSocketDisconnect
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None  # type: ignore
    WebSocket = None  # type: ignore

    class BaseModel:  # type: ignore
        pass


class AeonStatusResponse(BaseModel):
    kernel_beta: float = Field(..., description="Current β-value")
    kernel_kappa: float = Field(..., description="Current κ-value")
    kernel_resonance: float = Field(..., description="Current resonance")
    kernel_phase: str = Field(..., description="Current Bardo phase")
    num_agents: int = Field(..., description="Number of agents")
    trajectory_length: int = Field(..., description="Trajectory data points")
    safeguards_active: bool = Field(..., description="Safeguards enabled")
    violations: int = Field(..., description="Safeguard violations count")
    age_seconds: float = Field(..., description="Shell age in seconds")


class EmergenceTelemetryResponse(BaseModel):
    coherence_delta: float = Field(..., description="ΔC(t) coherence drift")
    system_impedance: float = Field(..., description="System impedance, nominally ≈221.7")
    metastability_offset: float = Field(..., description="σΦ offset, nominally 0.0625")
    mode_frequency_hz: float = Field(..., description="Current collective mode frequency")
    frame_counter: int = Field(..., description="Bridge frame counter")


@dataclass
class ResonatorConfig:
    """Hardware abstraction for future Vesta.V5 resonator integration."""

    device_name: str = "Vesta.V5"
    transport: str = "mock"
    endpoint: str = ""
    enabled: bool = False


class AeonBridge:
    """Original shell monitoring bridge."""

    def __init__(self, shell: Any, update_interval: float = 0.5) -> None:
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available. Install with: pip install fastapi")
        self.shell = shell
        self.update_interval = update_interval
        self.router = APIRouter()
        self._register_endpoints()

    def _register_endpoints(self) -> None:
        @self.router.get("/status", response_model=AeonStatusResponse)
        async def get_status() -> dict[str, Any]:
            summary = self.shell.get_shell_summary()
            kernel_state = summary["kernel_state"]
            return {
                "kernel_beta": kernel_state["beta"],
                "kernel_kappa": kernel_state["kappa"],
                "kernel_resonance": kernel_state["resonance"],
                "kernel_phase": kernel_state["phase"],
                "num_agents": summary["num_agents"],
                "trajectory_length": summary["trajectory_length"],
                "safeguards_active": summary["safeguards_active"],
                "violations": summary["violations"],
                "age_seconds": summary["age_seconds"],
            }

        @self.router.get("/trajectory")
        async def get_trajectory() -> dict[str, Any]:
            from aeon.shell.evolution import EvolutionTracker

            return EvolutionTracker(self.shell.get_trajectory()).export_for_visualization()

        @self.router.get("/agents")
        async def get_agents() -> list[dict[str, Any]]:
            return [a.get_state_summary() for a in self.shell.agents if hasattr(a, "get_state_summary")]

        @self.router.get("/collective")
        async def get_collective() -> dict[str, Any]:
            return self.shell.get_collective_field_metrics()

    async def websocket_live(self, websocket: WebSocket) -> None:
        await websocket.accept()
        try:
            while True:
                summary = self.shell.get_shell_summary()
                kernel_state = summary["kernel_state"]
                collective = summary["collective_metrics"]
                await websocket.send_json(
                    {
                        "timestamp": time.time(),
                        "beta": kernel_state["beta"],
                        "kappa": kernel_state["kappa"],
                        "resonance": kernel_state["resonance"],
                        "phase": kernel_state["phase"],
                        "information_density": kernel_state["information_density"],
                        "v_rig_effective": kernel_state["v_rig_effective"],
                        "num_agents": summary["num_agents"],
                        "kappa_field": collective.get("kappa_field", 0.0),
                        "beta_sync": collective.get("beta_sync", 0.0),
                        "v_collective": collective.get("v_collective", 0.0),
                        "violations": summary["violations"],
                        "auto_exit": summary["auto_exit_triggered"],
                    }
                )
                await asyncio.sleep(self.update_interval)
        except WebSocketDisconnect:
            return


class AeonLanternAsyncBridge:
    """High-throughput async EM↔Aeon bridge with zero-copy buffer semantics."""

    MODE_FREQUENCY_HZ = 13.5e6
    SYSTEM_IMPEDANCE = 221.7
    METASTABILITY_OFFSET = 0.0625

    def __init__(
        self,
        shell: Any,
        update_interval: float = 0.01,
        frame_capacity: int = 4096,
        resonator: ResonatorConfig | None = None,
    ) -> None:
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available. Install with: pip install fastapi")

        self.shell = shell
        self.update_interval = update_interval
        self.frame_capacity = frame_capacity
        self.router = APIRouter()
        self.resonator = resonator or ResonatorConfig()

        self._frame_dtype = np.float64
        self._frame_size = 6
        self._shm = shared_memory.SharedMemory(
            create=True,
            size=self.frame_capacity * self._frame_size * np.dtype(self._frame_dtype).itemsize,
        )
        self._frame_view = np.ndarray(
            (self.frame_capacity, self._frame_size), dtype=self._frame_dtype, buffer=self._shm.buf
        )
        self._frame_index = 0
        self._frame_counter = 0
        self._last_coherence = 0.0
        self._lock = Lock()
        self._register_endpoints()

    def _register_endpoints(self) -> None:
        @self.router.get("/v10/emergence_telemetry", response_model=EmergenceTelemetryResponse)
        async def emergence_telemetry() -> dict[str, Any]:
            return self.get_emergence_telemetry()

    def get_emergence_telemetry(self) -> dict[str, Any]:
        coherence = self._latest_frame()[3]
        coherence_delta = float(coherence - self._last_coherence)
        self._last_coherence = float(coherence)
        return {
            "coherence_delta": coherence_delta,
            "system_impedance": self.SYSTEM_IMPEDANCE,
            "metastability_offset": self.METASTABILITY_OFFSET,
            "mode_frequency_hz": self.MODE_FREQUENCY_HZ,
            "frame_counter": self._frame_counter,
        }

    def ingest_em_frame(self, em_vector: np.ndarray, timestamp: float | None = None) -> None:
        """Ingest a frame into shared memory without copy (numpy view assignment)."""
        now = timestamp if timestamp is not None else time.time()
        summary = self.shell.get_shell_summary()["kernel_state"]
        coherence = float(np.clip(np.mean(np.abs(em_vector)), 0.0, 1.0))

        with self._lock:
            self._frame_view[self._frame_index, :] = (
                now,
                summary["beta"],
                summary["kappa"],
                coherence,
                self.MODE_FREQUENCY_HZ,
                self.SYSTEM_IMPEDANCE,
            )
            self._frame_index = (self._frame_index + 1) % self.frame_capacity
            self._frame_counter += 1

    def _latest_frame(self) -> np.ndarray:
        with self._lock:
            idx = (self._frame_index - 1) % self.frame_capacity
            return self._frame_view[idx].copy()

    async def websocket_em_bridge(self, websocket: WebSocket) -> None:
        await websocket.accept()
        try:
            while True:
                frame = self._latest_frame()
                await websocket.send_json(
                    {
                        "timestamp": frame[0],
                        "beta": frame[1],
                        "kappa": frame[2],
                        "coherence": frame[3],
                        "mode_frequency_hz": frame[4],
                        "system_impedance": frame[5],
                        "metastability_offset": self.METASTABILITY_OFFSET,
                        "resonator": asdict(self.resonator),
                    }
                )
                await asyncio.sleep(self.update_interval)
        except WebSocketDisconnect:
            return

    def close(self) -> None:
        self._shm.close()
        self._shm.unlink()
