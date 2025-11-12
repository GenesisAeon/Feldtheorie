#!/usr/bin/env python3
"""
UTAC WebSocket Bridge Server

Connects Unity VR clients to UTAC API via WebSocket protocol.
Streams real-time system updates (β, Θ, R, σ, CREP scores).

Usage:
    python3 bridge_server.py
    python3 bridge_server.py --test-mode
    python3 bridge_server.py --port 8765

Author: Claude Code
Date: 2025-11-12
Version: 1.0.0
"""

import asyncio
import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Set, Dict, List
import websockets
from websockets.server import WebSocketServerProtocol

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Connected clients
clients: Set[WebSocketServerProtocol] = set()

# Subscriptions (client -> system_ids mapping)
subscriptions: Dict[WebSocketServerProtocol, Set[str]] = {}

# Test mode (synthetic data)
TEST_MODE = False


# ============================================================================
# Test Data (for --test-mode)
# ============================================================================

TEST_SYSTEMS = {
    "amoc": {
        "beta": 4.2,
        "theta": 150.0,
        "R": 148.0,
        "sigma": 0.85,
        "field_type": "Strongly Coupled",
        "crep_scores": {
            "coherence": 0.95,
            "resilience": 0.80,
            "empathy": 0.90,
            "propagation": 0.92
        },
        "metadata": {
            "domain": "climate",
            "citation": "Caesar et al. (2018)",
            "last_updated": "2025-11-12T12:00:00Z"
        }
    },
    "urban_heat": {
        "beta": 16.28,
        "theta": 145.5,
        "R": 148.2,
        "sigma": 0.92,
        "field_type": "Meta-Adaptive",
        "crep_scores": {
            "coherence": 0.99,
            "resilience": 0.85,
            "empathy": 1.00,
            "propagation": 0.98
        },
        "metadata": {
            "domain": "urban_climate",
            "citation": "Smith et al. (2023)",
            "last_updated": "2025-11-12T12:00:00Z"
        }
    },
    "llm_emergence": {
        "beta": 3.47,
        "theta": 1e9,  # 1B parameters
        "R": 1.5e9,    # 1.5B parameters
        "sigma": 0.73,
        "field_type": "High-Dimensional",
        "crep_scores": {
            "coherence": 0.98,
            "resilience": 0.65,
            "empathy": 0.88,
            "propagation": 0.91
        },
        "metadata": {
            "domain": "ai",
            "citation": "Wei et al. (2022)",
            "last_updated": "2025-11-12T12:00:00Z"
        }
    },
    "theta_plasticity": {
        "beta": 2.50,
        "theta": 50.0,
        "R": 45.0,
        "sigma": 0.38,
        "field_type": "Weakly Coupled",
        "crep_scores": {
            "coherence": 0.82,
            "resilience": 0.75,
            "empathy": 0.70,
            "propagation": 0.68
        },
        "metadata": {
            "domain": "neuroscience",
            "citation": "Bienenstock et al. (1982)",
            "last_updated": "2025-11-12T12:00:00Z"
        }
    },
    "climate_tipping": {
        "beta": 9.23,
        "theta": 2.0,  # 2°C warming
        "R": 1.8,      # 1.8°C current
        "sigma": 0.68,
        "field_type": "Physically Constrained",
        "crep_scores": {
            "coherence": 0.93,
            "resilience": 0.55,
            "empathy": 0.95,
            "propagation": 0.87
        },
        "metadata": {
            "domain": "climate",
            "citation": "Lenton et al. (2008)",
            "last_updated": "2025-11-12T12:00:00Z"
        }
    }
}


async def fetch_system_data(system_id: str) -> Dict:
    """
    Fetch system data from UTAC API.

    In TEST_MODE: Returns synthetic data.
    In production: Would call UTAC API at http://localhost:8000/api/system/{system_id}

    Args:
        system_id: System identifier (e.g., "amoc", "urban_heat")

    Returns:
        Dict with system data (β, θ, R, σ, CREP scores)
    """
    if TEST_MODE:
        # Return test data
        if system_id in TEST_SYSTEMS:
            return TEST_SYSTEMS[system_id]
        else:
            raise ValueError(f"Unknown system: {system_id}")

    else:
        # Production: Call UTAC API
        # TODO: Implement aiohttp GET request
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(f"http://localhost:8000/api/system/{system_id}") as resp:
        #         return await resp.json()

        # For now, return test data as fallback
        logger.warning(f"UTAC API not implemented, using test data for {system_id}")
        if system_id in TEST_SYSTEMS:
            return TEST_SYSTEMS[system_id]
        else:
            raise ValueError(f"Unknown system: {system_id}")


async def send_system_update(websocket: WebSocketServerProtocol, system_id: str, data: Dict):
    """
    Send system_update message to client.

    Args:
        websocket: WebSocket connection
        system_id: System identifier
        data: System data (β, θ, R, σ, CREP scores)
    """
    message = {
        "type": "system_update",
        "system_id": system_id,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        await websocket.send(json.dumps(message))
        logger.debug(f"Sent system_update for {system_id}")
    except Exception as e:
        logger.error(f"Error sending system_update: {e}")


async def handle_subscribe(websocket: WebSocketServerProtocol, system_ids: List[str]):
    """
    Handle subscribe message from client.

    Args:
        websocket: WebSocket connection
        system_ids: List of system IDs to subscribe to
    """
    # Store subscription
    if websocket not in subscriptions:
        subscriptions[websocket] = set()

    subscriptions[websocket].update(system_ids)

    logger.info(f"Client subscribed to {len(system_ids)} systems: {system_ids}")

    # Send initial data for each system
    for system_id in system_ids:
        try:
            data = await fetch_system_data(system_id)
            await send_system_update(websocket, system_id, data)
        except Exception as e:
            logger.error(f"Error fetching {system_id}: {e}")
            # Send error message
            await websocket.send(json.dumps({
                "type": "error",
                "code": "SYSTEM_NOT_FOUND",
                "message": f"System '{system_id}' not found",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))


async def handle_unsubscribe(websocket: WebSocketServerProtocol, system_ids: List[str]):
    """
    Handle unsubscribe message from client.

    Args:
        websocket: WebSocket connection
        system_ids: List of system IDs to unsubscribe from
    """
    if websocket in subscriptions:
        subscriptions[websocket].difference_update(system_ids)
        logger.info(f"Client unsubscribed from {len(system_ids)} systems: {system_ids}")


async def handle_ping(websocket: WebSocketServerProtocol, timestamp: str):
    """
    Handle ping message from client.

    Args:
        websocket: WebSocket connection
        timestamp: Client timestamp (for latency measurement)
    """
    pong = {
        "type": "pong",
        "client_timestamp": timestamp,
        "server_timestamp": datetime.now(timezone.utc).isoformat()
    }
    await websocket.send(json.dumps(pong))
    logger.debug("Sent pong")


async def handle_list_systems(websocket: WebSocketServerProtocol):
    """
    Handle list_systems request.

    Args:
        websocket: WebSocket connection
    """
    systems_list = [
        {"id": sid, "name": sid.replace("_", " ").title(),
         "field_type": data["field_type"], "beta": data["beta"]}
        for sid, data in TEST_SYSTEMS.items()
    ]

    message = {
        "type": "systems_list",
        "systems": systems_list,
        "count": len(systems_list),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    await websocket.send(json.dumps(message))
    logger.info(f"Sent systems_list with {len(systems_list)} systems")


async def handle_message(websocket: WebSocketServerProtocol, message: str):
    """
    Handle incoming WebSocket message from client.

    Args:
        websocket: WebSocket connection
        message: JSON message string
    """
    try:
        data = json.loads(message)
        msg_type = data.get("type")

        if msg_type == "subscribe":
            await handle_subscribe(websocket, data["system_ids"])

        elif msg_type == "unsubscribe":
            await handle_unsubscribe(websocket, data["system_ids"])

        elif msg_type == "ping":
            await handle_ping(websocket, data.get("timestamp", ""))

        elif msg_type == "list_systems":
            await handle_list_systems(websocket)

        elif msg_type == "disconnect":
            logger.info(f"Client requested disconnect: {data.get('reason', 'N/A')}")

        else:
            # Unknown message type
            await websocket.send(json.dumps({
                "type": "error",
                "code": "UNKNOWN_MESSAGE_TYPE",
                "message": f"Unknown message type: {msg_type}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))

    except json.JSONDecodeError:
        logger.error("Invalid JSON message")
        await websocket.send(json.dumps({
            "type": "error",
            "code": "INVALID_JSON",
            "message": "Message is not valid JSON",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await websocket.send(json.dumps({
            "type": "error",
            "code": "INTERNAL_ERROR",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))


async def stream_updates_task(websocket: WebSocketServerProtocol):
    """
    Background task: Stream updates for subscribed systems at 1 Hz.

    Args:
        websocket: WebSocket connection
    """
    while True:
        try:
            await asyncio.sleep(1.0)  # 1 Hz update rate

            if websocket in subscriptions:
                system_ids = subscriptions[websocket]
                for system_id in system_ids:
                    try:
                        data = await fetch_system_data(system_id)
                        await send_system_update(websocket, system_id, data)
                    except Exception as e:
                        logger.error(f"Error streaming {system_id}: {e}")

        except asyncio.CancelledError:
            # Task cancelled (client disconnected)
            break
        except Exception as e:
            logger.error(f"Error in stream_updates_task: {e}")


async def handler(websocket: WebSocketServerProtocol):
    """
    Main WebSocket connection handler.

    Args:
        websocket: WebSocket connection
    """
    # Register client
    clients.add(websocket)
    logger.info(f"✅ Client connected from {websocket.remote_address}. Total clients: {len(clients)}")

    # Start streaming task
    stream_task = asyncio.create_task(stream_updates_task(websocket))

    try:
        # Listen for messages from client
        async for message in websocket:
            await handle_message(websocket, message)

    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")

    finally:
        # Cleanup
        stream_task.cancel()
        clients.discard(websocket)
        if websocket in subscriptions:
            del subscriptions[websocket]
        logger.info(f"❌ Client disconnected. Total clients: {len(clients)}")


async def main(host: str, port: int):
    """
    Start WebSocket server.

    Args:
        host: Host address (default: "localhost")
        port: Port number (default: 8765)
    """
    logger.info(f"🚀 Starting UTAC WebSocket Bridge Server...")
    logger.info(f"   Protocol Version: 1.0.0")
    logger.info(f"   Mode: {'TEST' if TEST_MODE else 'PRODUCTION'}")
    logger.info(f"   Host: {host}")
    logger.info(f"   Port: {port}")

    async with websockets.serve(handler, host, port):
        logger.info(f"✅ WebSocket Bridge running on ws://{host}:{port}")
        logger.info(f"   Press Ctrl+C to stop")

        # Run forever
        await asyncio.Future()


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="UTAC WebSocket Bridge Server")
    parser.add_argument("--host", default="localhost", help="Host address (default: localhost)")
    parser.add_argument("--port", type=int, default=8765, help="Port number (default: 8765)")
    parser.add_argument("--test-mode", action="store_true", help="Use synthetic test data (no UTAC API)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Set test mode
    TEST_MODE = args.test_mode

    # Set logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Run server
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
