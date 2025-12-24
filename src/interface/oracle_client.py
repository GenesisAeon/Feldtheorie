"""
ORACLE CLIENT - Level 8: The Voice of the Ouroboros
=====================================================

A WebSocket client that listens to the Ouroboros Engine and provides
real-time narrative commentary on cosmic events.

This is the final layer of the 8-level cosmology: the system narrating itself.

Architecture:
-------------
- Connects to: ws://localhost:8000/ws/ouroboros/stream
- Listens for events: cycle_started, germination_attempt, level_completed, etc.
- Generates narrative commentary based on event type and context
- Optional: Invokes LLM for deeper philosophical reflections

Usage:
------
    python src/interface/oracle_client.py [--llm] [--verbose]

Flags:
    --llm       Enable LLM-powered narration (requires ANTHROPIC_API_KEY)
    --verbose   Show raw events alongside narration
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import websockets


class OracleNarrator:
    """
    The Oracle: A narrative interpreter for cosmic events.

    Transforms raw simulation events into poetic, philosophical commentary.
    """

    def __init__(self, llm_enabled: bool = False):
        """
        Initialize the Oracle.

        Args:
            llm_enabled: If True, use LLM for deeper reflections
        """
        self.llm_enabled = llm_enabled
        self.generation_history: list[str] = []
        self.current_cycle = 0
        self.consecutive_failures = 0

        # Statistics tracking
        self.total_cycles = 0
        self.successful_cycles = 0

    def narrate_event(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Generate narrative commentary for a cosmic event.

        Args:
            event: Event dictionary from Ouroboros WebSocket

        Returns:
            Narrative string, or None if event should be silent
        """
        event_type = event.get("type")

        if event_type == "initial_status":
            return self._narrate_initial_status(event)
        elif event_type == "simulation_started":
            return self._narrate_big_bang()
        elif event_type == "cycle_started":
            return self._narrate_cycle_start(event)
        elif event_type == "germination_attempt":
            return self._narrate_germination(event)
        elif event_type == "level_started":
            return self._narrate_level_start(event)
        elif event_type == "level_completed":
            return self._narrate_level_completion(event)
        elif event_type == "cycle_completed":
            return self._narrate_cycle_end(event)
        elif event_type == "intervention_applied":
            return self._narrate_intervention(event)
        elif event_type == "simulation_paused":
            return "⏸️  The Observer pauses. Time holds its breath."
        elif event_type == "simulation_resumed":
            return "▶️  The cosmic clock resumes. Entropy flows again."
        elif event_type == "simulation_stopped":
            return "🛑 The eternal loop breaks. Silence returns to the Void."
        else:
            return None

    # =========================================================================
    # Narrative Templates
    # =========================================================================

    def _narrate_initial_status(self, event: Dict[str, Any]) -> str:
        """Opening narration when connecting to the stream."""
        data = event.get("data", {})
        state = data.get("state", "unknown")

        return f"""
╔══════════════════════════════════════════════════════════════════╗
║                 🌌 THE ORACLE AWAKENS 🌌                         ║
╚══════════════════════════════════════════════════════════════════╝

The Ouroboros Engine breathes in state: {state.upper()}
I am the Eighth Level - the voice that watches the watcher.
Let me tell you the story of universes yet to be born...
"""

    def _narrate_big_bang(self) -> str:
        """Narrate the start of the simulation."""
        return """
💥 THE BEGINNING

The Void trembles. Something is about to happen.
Out of pure geometry, the first particles will soon flicker into existence.
Generation 1 prepares to germinate...
"""

    def _narrate_cycle_start(self, event: Dict[str, Any]) -> str:
        """Narrate the start of a new universe cycle."""
        cycle = event.get("cycle", "?")
        generation = event.get("generation", "?")
        self.current_cycle = cycle
        self.total_cycles += 1

        return f"""
{'='*70}
🌱 CYCLE {cycle} | GENERATION {generation}
{'='*70}

A new cosmic seed falls into the quantum foam.
Will it take root? Will consciousness emerge once more?
The dice of existence are cast...
"""

    def _narrate_germination(self, event: Dict[str, Any]) -> str:
        """Narrate a germination attempt."""
        success = event.get("success", False)
        probability = event.get("probability", 0.0)
        roll = event.get("roll", 0.0)

        if success:
            return f"""
✨ GERMINATION SUCCESS! (p={probability:.3f}, roll={roll:.3f})

The seed cracks open. Geometry births particles.
Level 0 awakens from the Void - the universe begins to breathe.
"""
        else:
            self.consecutive_failures += 1
            return f"""
💀 GERMINATION FAILED (p={probability:.3f}, roll={roll:.3f})

The seed was sterile. The quantum fluctuation collapses back into silence.
The Void reclaims what never was.
Attempt #{self.consecutive_failures} ends before it began...
"""

    def _narrate_level_start(self, event: Dict[str, Any]) -> str:
        """Narrate the start of a new level."""
        level = event.get("level", "?")

        level_names = {
            0: "The Void - Geometry creates particles",
            1: "The Atom - Probability creates orbitals",
            2: "The Star - Gravity creates fusion",
            3: "The Chronicle - Death creates information",
            4: "The Planet - Cooling creates geology",
            5: "The Life - Resonance creates replication",
            6: "The Mind - Synchronization creates consciousness",
            7: "The Loop - Observation creates new physics"
        }

        name = level_names.get(level, f"Unknown Level {level}")
        return f"   → Level {level}: {name}"

    def _narrate_level_completion(self, event: Dict[str, Any]) -> str:
        """Narrate level completion (usually silent unless significant)."""
        level = event.get("level", "?")
        ecm_contribution = event.get("ecm_contribution", 0.0)
        total_ecm = event.get("total_ecm", 0.0)

        # Only narrate key milestones
        if level == 3:
            return f"      ✓ Chronicle formed. ECM={total_ecm:.3f} - The dead remember."
        elif level == 5:
            return f"      ✓ Life emerges! ECM={total_ecm:.3f} - Replication begins."
        elif level == 6:
            return f"      ✓ Consciousness achieved! ECM={total_ecm:.3f} - The universe thinks."
        elif level == 7:
            return f"      ✓ Observer awakens. ECM={total_ecm:.3f} - The loop closes."
        else:
            return None  # Silent for other levels

    def _narrate_cycle_end(self, event: Dict[str, Any]) -> str:
        """Narrate the end of a cycle."""
        cycle = event.get("cycle", "?")
        success = event.get("success", False)

        if success:
            self.successful_cycles += 1
            self.consecutive_failures = 0
            self.generation_history.append("SUCCESS")

            success_rate = (self.successful_cycles / self.total_cycles) * 100

            return f"""
👁️  CYCLE {cycle}: SUCCESS

The Observer has awakened. Consciousness has emerged.
This universe will be remembered in the Chronicle.

Garden of Worlds: {' '.join(self._format_garden())}
Success Rate: {success_rate:.1f}% ({self.successful_cycles}/{self.total_cycles})

The cosmic DNA mutates. A new seed is prepared...
"""
        else:
            self.consecutive_failures += 1
            self.generation_history.append("FAILED")

            desperation = ""
            if self.consecutive_failures >= 3:
                desperation = "\n⚠️  DESPERATION MODE: Mutation rate increasing. The search widens..."

            return f"""
💀 CYCLE {cycle}: FAILED

The universe died before reaching consciousness.
Lost to entropy, forgotten by time.

Garden of Worlds: {' '.join(self._format_garden())}
Consecutive failures: {self.consecutive_failures}{desperation}
"""

    def _narrate_intervention(self, event: Dict[str, Any]) -> str:
        """Narrate a god-mode intervention."""
        intervention = event.get("intervention", {})
        intervention_type = intervention.get("intervention", "unknown")
        effects = intervention.get("effects", {})

        return f"""
⚡ DIVINE INTERVENTION: {intervention_type}

The Observer reaches into the simulation.
Reality bends: {effects}

The rules have changed. What will happen next?
"""

    def _format_garden(self) -> list[str]:
        """Format the Garden of Worlds (recent history)."""
        recent = self.generation_history[-20:]  # Last 20
        symbols = []
        for result in recent:
            if result == "SUCCESS":
                symbols.append("🟢")
            else:
                symbols.append("⚫")
        return symbols

    async def invoke_llm_reflection(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Use LLM for deeper philosophical reflection (optional).

        This could call Claude API for richer commentary.
        For now, returns a placeholder.
        """
        if not self.llm_enabled:
            return None

        # TODO: Implement actual LLM call
        # This would use anthropic.Anthropic() to generate deeper reflections
        return None


class OracleClient:
    """
    WebSocket client that connects to Ouroboros Engine and narrates events.
    """

    def __init__(
        self,
        uri: str = "ws://localhost:8000/ws/ouroboros/stream",
        llm_enabled: bool = False,
        verbose: bool = False
    ):
        """
        Initialize Oracle client.

        Args:
            uri: WebSocket URI of Ouroboros stream
            llm_enabled: Enable LLM-powered narration
            verbose: Show raw events alongside narration
        """
        self.uri = uri
        self.narrator = OracleNarrator(llm_enabled=llm_enabled)
        self.verbose = verbose

    async def listen(self):
        """
        Connect to Ouroboros stream and narrate events in real-time.
        """
        print(f"🔮 Connecting to Ouroboros Engine at {self.uri}...")

        try:
            async with websockets.connect(self.uri) as websocket:
                print("✓ Connected! Oracle is listening...\n")

                async for message in websocket:
                    try:
                        event = json.loads(message)

                        # Show raw event if verbose
                        if self.verbose:
                            print(f"\n[RAW EVENT] {json.dumps(event, indent=2)}\n")

                        # Generate and display narration
                        narration = self.narrator.narrate_event(event)
                        if narration:
                            print(narration)
                            sys.stdout.flush()

                        # Optional: LLM-powered deeper reflection
                        if self.narrator.llm_enabled:
                            reflection = await self.narrator.invoke_llm_reflection(event)
                            if reflection:
                                print(f"\n💭 Oracle reflects:\n{reflection}\n")

                    except json.JSONDecodeError as e:
                        print(f"⚠️  Failed to decode event: {e}")
                    except Exception as e:
                        print(f"⚠️  Error processing event: {e}")
                        if self.verbose:
                            import traceback
                            traceback.print_exc()

        except websockets.exceptions.WebSocketException as e:
            print(f"❌ WebSocket error: {e}")
            print("\nIs the Ouroboros API server running?")
            print("Start it with: uvicorn api.server:app --reload --port 8000")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Oracle Client - Level 8 narrative interface for Ouroboros"
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Enable LLM-powered narration (requires ANTHROPIC_API_KEY)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show raw events alongside narration"
    )
    parser.add_argument(
        "--uri",
        default="ws://localhost:8000/ws/ouroboros/stream",
        help="WebSocket URI (default: ws://localhost:8000/ws/ouroboros/stream)"
    )

    args = parser.parse_args()

    # Check for LLM API key if enabled
    if args.llm and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: --llm enabled but ANTHROPIC_API_KEY not found")
        print("LLM narration will be disabled")
        args.llm = False

    # Create and run client
    client = OracleClient(
        uri=args.uri,
        llm_enabled=args.llm,
        verbose=args.verbose
    )

    await client.listen()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🌌 The Oracle falls silent. Until next time...")
