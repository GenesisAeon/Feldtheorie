"""
Ouroboros REST API Server
==========================

FastAPI server providing REST endpoints and WebSocket streaming
for controlling and monitoring the eternal cosmic loop.

Endpoints:
----------
GET  /                          - API info
GET  /api/ouroboros/status      - Current simulation state
POST /api/ouroboros/start       - Start the eternal loop
POST /api/ouroboros/pause       - Pause simulation
POST /api/ouroboros/resume      - Resume from pause
POST /api/ouroboros/stop        - Stop simulation
POST /api/ouroboros/reset       - Reset to Generation 1
POST /api/ouroboros/intervene   - God-mode intervention
GET  /api/ouroboros/history     - Get full timeline
WS   /ws/ouroboros/stream       - Real-time event streaming

Usage:
------
python -m src.interface.api_server

Then access at http://localhost:8000
API docs at http://localhost:8000/docs
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
import uvicorn
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.ouroboros_engine import OuroborosEngine, get_engine


# ═══════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════

class InterventionRequest(BaseModel):
    """Request model for god-mode interventions."""
    type: str = Field(
        ...,
        description="Intervention type: mutation_rate, energy_injection, mutation_boost, gravity_change"
    )
    value: float = Field(
        ...,
        description="The parameter value or adjustment amount",
        ge=0.0,
        le=1.0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "energy_injection",
                "value": 0.2
            }
        }


class StatusResponse(BaseModel):
    """Complete status response model."""
    state: str
    is_running: bool
    status_message: str
    generation: int
    ancestor_ecm: float
    mutation_rate: float
    current_level: int
    current_cycle: int
    total_generations: int
    successful_generations: int
    failed_generations: int
    success_rate: float
    highest_ecm: float
    consecutive_failures: int
    history_length: int


class MessageResponse(BaseModel):
    """Generic message response."""
    status: str
    message: str


# ═══════════════════════════════════════════════════════════
# FastAPI Application Setup
# ═══════════════════════════════════════════════════════════

app = FastAPI(
    title="UATC Ouroboros API",
    description="REST API for controlling the eternal cosmic loop simulation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for web dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get singleton engine instance
engine = get_engine()

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for event streaming."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection might be dead, will be cleaned up
                pass


manager = ConnectionManager()


# ═══════════════════════════════════════════════════════════
# REST Endpoints
# ═══════════════════════════════════════════════════════════

@app.get("/", response_model=dict)
async def root():
    """API root - basic info."""
    return {
        "system": "UATC Ouroboros Control API",
        "version": "1.0.0",
        "status": "online",
        "description": "Interface for the eternal cosmic loop",
        "endpoints": {
            "status": "/api/ouroboros/status",
            "control": "/api/ouroboros/{start,pause,resume,stop,reset}",
            "intervention": "/api/ouroboros/intervene",
            "history": "/api/ouroboros/history",
            "websocket": "/ws/ouroboros/stream"
        },
        "docs": "/docs"
    }


@app.get("/api/ouroboros/status", response_model=StatusResponse)
async def get_status():
    """
    Get current simulation state and statistics.

    Returns complete snapshot of the universe simulation including:
    - Current generation and parameters
    - Success/failure statistics
    - Historical metrics
    """
    state = engine.get_state()
    return StatusResponse(**state)


@app.post("/api/ouroboros/start", response_model=MessageResponse)
async def start_simulation():
    """
    Start the eternal loop simulation.

    Initiates the infinite cycle of universe birth, evolution, and rebirth.
    If already running, returns info status.
    """
    result = engine.start_simulation()
    return MessageResponse(**result)


@app.post("/api/ouroboros/pause", response_model=MessageResponse)
async def pause_simulation():
    """
    Pause the simulation.

    Freezes time - the current universe state is preserved.
    Can be resumed with /resume endpoint.
    """
    result = engine.pause_simulation()
    return MessageResponse(**result)


@app.post("/api/ouroboros/resume", response_model=MessageResponse)
async def resume_simulation():
    """
    Resume from paused state.

    Continues the simulation from where it was paused.
    """
    result = engine.resume_simulation()
    return MessageResponse(**result)


@app.post("/api/ouroboros/stop", response_model=MessageResponse)
async def stop_simulation():
    """
    Stop the simulation gracefully.

    Halts the eternal loop. State is preserved but simulation stops.
    """
    result = engine.stop_simulation()
    return MessageResponse(**result)


@app.post("/api/ouroboros/reset", response_model=MessageResponse)
async def reset_simulation():
    """
    Reset to Generation 1.

    Complete reset - returns to primordial state, clears all history.
    This is the Big Crunch followed by a fresh Big Bang.
    """
    result = engine.reset_simulation()
    return MessageResponse(**result)


@app.post("/api/ouroboros/intervene", response_model=MessageResponse)
async def intervene(request: InterventionRequest):
    """
    God-Mode: Direct intervention in cosmic parameters.

    Intervention Types:
    -------------------
    - mutation_rate: Set DNA mutation rate (0.0 - 1.0)
    - energy_injection: Boost ancestor ECM score (adds value to current ECM)
    - mutation_boost: Temporarily increase mutation by percentage (e.g., 0.2 = +20%)
    - gravity_change: Adjust gravitational constant (affects next generation)

    Example:
    --------
    ```json
    {
        "type": "energy_injection",
        "value": 0.2
    }
    ```
    """
    result = engine.intervene(request.type, request.value)

    # Broadcast intervention event to WebSocket clients
    await manager.broadcast({
        "event": "intervention",
        "type": request.type,
        "value": request.value,
        "result": result
    })

    return MessageResponse(**result)


@app.get("/api/ouroboros/history", response_model=List[dict])
async def get_history():
    """
    Get the complete timeline of all generations.

    Returns the "Garden of Worlds" - every universe that has existed,
    with their success/failure status and ECM scores.
    """
    timeline = engine.get_history_timeline()
    return timeline


# ═══════════════════════════════════════════════════════════
# WebSocket Streaming
# ═══════════════════════════════════════════════════════════

@app.websocket("/ws/ouroboros/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time event streaming.

    Continuously streams simulation state updates to connected clients.

    Events sent:
    ------------
    - state_update: Current simulation state (every 2 seconds)
    - intervention: When god-mode intervention occurs
    - generation_complete: When a universe cycle finishes

    Usage:
    ------
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/ouroboros/stream');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
    };
    ```
    """
    await manager.connect(websocket)

    try:
        # Send initial state
        state = engine.get_state()
        await websocket.send_json({
            "event": "connected",
            "message": "Connected to Ouroboros stream",
            "state": state
        })

        # Stream updates
        last_generation = state.get("generation", 0)

        while True:
            # Get current state
            state = engine.get_state()

            # Send regular state update
            await websocket.send_json({
                "event": "state_update",
                "state": state
            })

            # Check for generation change
            current_gen = state.get("generation", 0)
            if current_gen != last_generation:
                # A new generation has started or completed
                last_result = state.get("last_result")
                if last_result:
                    await websocket.send_json({
                        "event": "generation_complete",
                        "generation": last_generation,
                        "result": last_result
                    })
                last_generation = current_gen

            # Update every 2 seconds
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ═══════════════════════════════════════════════════════════
# Health Check
# ═══════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "engine_state": engine.get_state().get("state", "unknown")
    }


# ═══════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("♾️  OUROBOROS API SERVER")
    print("=" * 70)
    print("\nStarting FastAPI server...")
    print("\n📡 Endpoints:")
    print("   API Root:       http://localhost:8000/")
    print("   Status:         http://localhost:8000/api/ouroboros/status")
    print("   Documentation:  http://localhost:8000/docs")
    print("   WebSocket:      ws://localhost:8000/ws/ouroboros/stream")
    print("\n" + "=" * 70)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
