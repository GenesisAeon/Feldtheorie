#!/usr/bin/env python3
"""
UTAC WebSocket Test Client

Simple test client to validate WebSocket bridge functionality.
Connects to server, subscribes to systems, prints received updates.

Usage:
    python3 test_client.py
    python3 test_client.py --server ws://localhost:8765
    python3 test_client.py --systems amoc urban_heat

Author: Claude Code
Date: 2025-11-12
Version: 1.0.0
"""

import asyncio
import json
import argparse
from datetime import datetime
import websockets


async def test_client(server_url: str, system_ids: list):
    """
    Test WebSocket client.

    Args:
        server_url: WebSocket server URL (e.g., ws://localhost:8765)
        system_ids: List of system IDs to subscribe to
    """
    print(f"🔗 Connecting to {server_url}...")

    try:
        async with websockets.connect(server_url) as websocket:
            print(f"✅ Connected to WebSocket server")

            # Send subscribe message
            subscribe_msg = {
                "type": "subscribe",
                "system_ids": system_ids,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

            print(f"📤 Subscribing to {len(system_ids)} systems: {system_ids}")
            await websocket.send(json.dumps(subscribe_msg))

            # Listen for messages
            print(f"📥 Listening for messages (Press Ctrl+C to stop)...\n")

            message_count = 0
            async for message in websocket:
                message_count += 1
                data = json.loads(message)

                # Print message
                msg_type = data.get("type", "unknown")
                timestamp = data.get("timestamp", "N/A")

                if msg_type == "system_update":
                    system_id = data["system_id"]
                    beta = data["data"]["beta"]
                    sigma = data["data"]["sigma"]
                    field_type = data["data"]["field_type"]

                    print(f"[{message_count}] {timestamp}")
                    print(f"    System: {system_id}")
                    print(f"    β: {beta:.2f}, σ: {sigma:.2f}")
                    print(f"    Field Type: {field_type}")
                    print()

                elif msg_type == "pong":
                    print(f"[{message_count}] PONG received")
                    print(f"    Server Time: {data.get('server_timestamp', 'N/A')}")
                    print()

                elif msg_type == "systems_list":
                    systems = data["systems"]
                    print(f"[{message_count}] Systems List ({len(systems)} systems):")
                    for system in systems:
                        print(f"    - {system['id']}: {system['name']} (β={system['beta']:.2f})")
                    print()

                elif msg_type == "error":
                    code = data.get("code", "UNKNOWN")
                    message = data.get("message", "N/A")
                    print(f"[{message_count}] ❌ ERROR: {code}")
                    print(f"    Message: {message}")
                    print()

                else:
                    print(f"[{message_count}] Unknown message type: {msg_type}")
                    print(json.dumps(data, indent=2))
                    print()

    except websockets.exceptions.ConnectionRefused:
        print(f"❌ Connection refused. Is the server running at {server_url}?")
        print(f"   Start server: python3 bridge_server.py --test-mode")

    except KeyboardInterrupt:
        print(f"\n🛑 Stopped by user")

    except Exception as e:
        print(f"❌ Error: {e}")


async def interactive_test(server_url: str):
    """
    Interactive test mode with menu.

    Args:
        server_url: WebSocket server URL
    """
    print(f"🔗 Connecting to {server_url}...")

    async with websockets.connect(server_url) as websocket:
        print(f"✅ Connected\n")

        while True:
            print("=" * 50)
            print("UTAC WebSocket Test Client - Interactive Mode")
            print("=" * 50)
            print("1. Subscribe to systems")
            print("2. Unsubscribe from systems")
            print("3. Send ping")
            print("4. List all systems")
            print("5. Exit")
            print("=" * 50)

            choice = input("Enter choice (1-5): ").strip()

            if choice == "1":
                # Subscribe
                system_ids = input("Enter system IDs (comma-separated): ").strip().split(",")
                system_ids = [s.strip() for s in system_ids if s.strip()]

                msg = {
                    "type": "subscribe",
                    "system_ids": system_ids,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                await websocket.send(json.dumps(msg))
                print(f"✅ Subscribed to {len(system_ids)} systems")

                # Receive initial messages
                for _ in range(len(system_ids)):
                    response = await websocket.recv()
                    data = json.loads(response)
                    if data["type"] == "system_update":
                        print(f"   - {data['system_id']}: β={data['data']['beta']:.2f}")

            elif choice == "2":
                # Unsubscribe
                system_ids = input("Enter system IDs (comma-separated): ").strip().split(",")
                system_ids = [s.strip() for s in system_ids if s.strip()]

                msg = {
                    "type": "unsubscribe",
                    "system_ids": system_ids
                }
                await websocket.send(json.dumps(msg))
                print(f"✅ Unsubscribed from {len(system_ids)} systems")

            elif choice == "3":
                # Ping
                msg = {
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                await websocket.send(json.dumps(msg))
                print("✅ Ping sent")

                response = await websocket.recv()
                data = json.loads(response)
                if data["type"] == "pong":
                    print(f"   Server Time: {data.get('server_timestamp', 'N/A')}")

            elif choice == "4":
                # List systems
                msg = {"type": "list_systems"}
                await websocket.send(json.dumps(msg))
                print("✅ Requesting systems list...")

                response = await websocket.recv()
                data = json.loads(response)
                if data["type"] == "systems_list":
                    systems = data["systems"]
                    print(f"\n{len(systems)} systems available:")
                    for system in systems:
                        print(f"   - {system['id']:20s} β={system['beta']:6.2f}  {system['field_type']}")

            elif choice == "5":
                # Exit
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice")

            print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UTAC WebSocket Test Client")
    parser.add_argument(
        "--server",
        default="ws://localhost:8765",
        help="WebSocket server URL (default: ws://localhost:8765)"
    )
    parser.add_argument(
        "--systems",
        nargs="+",
        default=["amoc", "urban_heat"],
        help="System IDs to subscribe to (default: amoc urban_heat)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode with menu"
    )

    args = parser.parse_args()

    try:
        if args.interactive:
            asyncio.run(interactive_test(args.server))
        else:
            asyncio.run(test_client(args.server, args.systems))

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
