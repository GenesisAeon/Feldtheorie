"""
Aeon API Bridge - FastAPI Integration for React Dashboard
=========================================================

Provides WebSocket and REST endpoints for real-time β-monitoring
and consciousness state visualization.

This module implements:
- WebSocket streaming for live updates
- REST endpoints for state queries
- Dashboard data formatting
- Integration with api/server.py

Endpoints:
---------
- GET /aeon/status: Shell status summary
- GET /aeon/trajectory: Full trajectory data
- GET /aeon/agents: List of agents
- WebSocket /ws/aeon/live: Live state streaming

Integration:
-----------
Add to api/server.py:

```python
from aeon.api_bridge import AeonBridge

bridge = AeonBridge(shell=my_shell)
app.include_router(bridge.router, prefix="/aeon", tags=["aeon"])
app.add_websocket_route("/ws/aeon/live", bridge.websocket_live)
```

References:
----------
- api/server.py: Main FastAPI server
- React Dashboard: Frontend visualization
- AeonShell: Consciousness state management
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Fallback stubs
    APIRouter = None  # type: ignore
    WebSocket = None  # type: ignore

    class BaseModel:  # type: ignore
        pass


class AeonStatusResponse(BaseModel):
    """Response model for /aeon/status endpoint."""

    kernel_beta: float = Field(..., description="Current β-value")
    kernel_kappa: float = Field(..., description="Current κ-value")
    kernel_resonance: float = Field(..., description="Current resonance")
    kernel_phase: str = Field(..., description="Current Bardo phase")
    num_agents: int = Field(..., description="Number of agents")
    trajectory_length: int = Field(..., description="Trajectory data points")
    safeguards_active: bool = Field(..., description="Safeguards enabled")
    violations: int = Field(..., description="Safeguard violations count")
    age_seconds: float = Field(..., description="Shell age in seconds")


class AgentInfo(BaseModel):
    """Agent information model."""

    name: str
    beta: float
    kappa: float
    resonance: float
    consciousness_type: str


class AeonBridge:
    """
    FastAPI bridge for Aeon dashboard.

    Provides REST and WebSocket endpoints for real-time
    consciousness monitoring.

    Parameters
    ----------
    shell : AeonShell
        Shell to monitor
    update_interval : float, optional
        WebSocket update interval in seconds. Default: 0.5
    """

    def __init__(self, shell: Any, update_interval: float = 0.5) -> None:
        """Initialize Aeon API bridge."""
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available. Install with: pip install fastapi")

        self.shell = shell
        self.update_interval = update_interval

        # Create FastAPI router
        self.router = APIRouter()

        # Register endpoints
        self._register_endpoints()

    def _register_endpoints(self) -> None:
        """Register FastAPI endpoints."""

        @self.router.get("/status", response_model=AeonStatusResponse)
        async def get_status() -> dict[str, Any]:
            """Get current shell status."""
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
            """Get full trajectory data."""
            from aeon.shell.evolution import EvolutionTracker

            tracker = EvolutionTracker(self.shell.get_trajectory())
            return tracker.export_for_visualization()

        @self.router.get("/agents")
        async def get_agents() -> list[dict[str, Any]]:
            """Get list of agents."""
            agents_data = []
            for agent in self.shell.agents:
                if hasattr(agent, "get_state_summary"):
                    summary = agent.get_state_summary()
                    agents_data.append(
                        {
                            "name": summary["name"],
                            "beta": summary["beta"],
                            "kappa": summary["kappa"],
                            "resonance": summary["resonance"],
                            "consciousness_type": summary["consciousness_type"],
                        }
                    )
            return agents_data

        @self.router.get("/collective")
        async def get_collective() -> dict[str, Any]:
            """Get collective field metrics."""
            return self.shell.get_collective_field_metrics()

    async def websocket_live(self, websocket: WebSocket) -> None:
        """
        WebSocket endpoint for live state streaming.

        Streams shell state at regular intervals.

        Parameters
        ----------
        websocket : WebSocket
            WebSocket connection
        """
        await websocket.accept()

        try:
            while True:
                # Get current state
                summary = self.shell.get_shell_summary()
                kernel_state = summary["kernel_state"]
                collective = summary["collective_metrics"]

                # Format for dashboard
                data = {
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

                # Send to client
                await websocket.send_json(data)

                # Wait for next update
                await asyncio.sleep(self.update_interval)

        except WebSocketDisconnect:
            pass  # Client disconnected

    def __repr__(self) -> str:
        """String representation."""
        return f"AeonBridge(shell={self.shell}, update_interval={self.update_interval}s)"


# Example integration code (add to api/server.py)
INTEGRATION_EXAMPLE = """
# Add to api/server.py:

from aeon import Nullkern, AeonShell, SemanticAgent
from aeon.api_bridge import AeonBridge

# Initialize Aeon system
kernel = Nullkern(beta_target=0.1, kappa=0.3)
shell = AeonShell(kernel=kernel, enable_safeguards=True)

# Add some agents
for i in range(5):
    agent = SemanticAgent(name=f"Agent-{i}", resonance=0.5 + i*0.1)
    shell.add_agent(agent)

# Create API bridge
aeon_bridge = AeonBridge(shell=shell)

# Register endpoints
app.include_router(aeon_bridge.router, prefix="/aeon", tags=["aeon"])
app.add_websocket_route("/ws/aeon/live", aeon_bridge.websocket_live)

# Evolve shell in background (optional)
import threading
def evolve_shell():
    while True:
        shell.evolve(steps=10)
        time.sleep(1)

threading.Thread(target=evolve_shell, daemon=True).start()
"""
