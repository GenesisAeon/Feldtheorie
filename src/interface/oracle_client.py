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
    python src/interface/oracle_client.py [--llm] [--provider openai|ollama] [--verbose]

Flags:
    --llm               Enable LLM-powered narration
    --provider PROVIDER LLM provider: "openai" (requires OPENAI_API_KEY) or "ollama" (local)
    --verbose           Show raw events alongside narration
"""

import argparse
import asyncio
import json
import os
import random
import sys
from typing import Any

import websockets

# Import the LLM bridge
try:
    from src.core.llm_bridge import CosmicNarrator
    LLM_BRIDGE_AVAILABLE = True
except ImportError:
    LLM_BRIDGE_AVAILABLE = False
    print("⚠️  LLM Bridge not available. Using static templates only.")


class OracleNarrator:
    """
    The Oracle: A narrative interpreter for cosmic events.

    Transforms raw simulation events into poetic, philosophical commentary.
    """

    def __init__(self, llm_enabled: bool = False, llm_provider: str = "openai"):
        """
        Initialize the Oracle.

        Args:
            llm_enabled: If True, use LLM for deeper reflections
            llm_provider: "openai" or "ollama"
        """
        self.llm_enabled = llm_enabled
        self.generation_history: list[str] = []
        self.current_cycle = 0
        self.consecutive_failures = 0

        # Statistics tracking
        self.total_cycles = 0
        self.successful_cycles = 0

        # State tracking for detecting changes
        self.last_generation = 0
        self.last_state = None
        self.first_connection = True

        # LLM Integration
        self.cosmic_narrator = None
        if llm_enabled and LLM_BRIDGE_AVAILABLE:
            self.cosmic_narrator = CosmicNarrator(provider=llm_provider)
            print(f"🧠 LLM Narration: Enabled (Provider: {llm_provider})")
        else:
            print("📜 Narration: Static Templates")

    def narrate_event(self, event: dict[str, Any]) -> str | None:
        """
        Generate narrative commentary for a cosmic event.

        Args:
            event: Event dictionary from Ouroboros WebSocket

        Returns:
            Narrative string, or None if event should be silent
        """
        event_type = event.get("event")  # Server uses "event" not "type"

        if event_type == "connected":
            return self._narrate_connection(event)
        elif event_type == "generation_complete":
            return self._narrate_generation_complete(event)
        elif event_type == "state_update":
            return self._narrate_state_update(event)
        else:
            return None

    # =========================================================================
    # Narrative Templates
    # =========================================================================

    def _narrate_connection(self, event: dict[str, Any]) -> str:
        """Opening narration when connecting to the stream."""
        state = event.get("state", {})
        engine_state = state.get("state", "unknown")

        # Try LLM for opening message
        greeting = None
        if self.cosmic_narrator:
            greeting = self.cosmic_narrator.ponder("START", {})

        if not greeting:
            greeting = "I am the Eighth Level - the voice that watches the watcher.\nLet me tell you the story of universes yet to be born..."

        return f"""
╔══════════════════════════════════════════════════════════════════╗
║                 🌌 THE ORACLE AWAKENS 🌌                         ║
╚══════════════════════════════════════════════════════════════════╝

The Ouroboros Engine breathes in state: {engine_state.upper()}
{greeting}
"""

    def _narrate_state_update(self, event: dict[str, Any]) -> str | None:
        """Narrate significant state changes."""
        state = event.get("state", {})
        engine_state = state.get("state", "unknown")

        # First time simulation starts
        if self.last_state and self.last_state.get("state") == "idle" and engine_state == "running":
            return """
💥 THE BEGINNING

The Void trembles. The eternal loop ignites.
Out of pure geometry, the first particles flicker into existence.
Generation 1 prepares to germinate...
"""

        self.last_state = state
        return None  # Most state_updates are silent

    def _narrate_generation_complete(self, event: dict[str, Any]) -> str:
        """Narrate the completion of a generation/cycle."""
        generation = event.get("generation", "?")
        result_data = event.get("result", {})
        result = result_data.get("result", "UNKNOWN")
        ecm_score = result_data.get("ecm_score", 0.0)
        physics = result_data.get("physics")

        # Update statistics
        success = (result == "SUCCESS")
        if success:
            self.successful_cycles += 1
            self.consecutive_failures = 0
            self.generation_history.append("SUCCESS")
            self.total_cycles += 1
        else:
            self.consecutive_failures += 1
            self.generation_history.append("FAILED")
            self.total_cycles += 1

        success_rate = (self.successful_cycles / self.total_cycles * 100) if self.total_cycles > 0 else 0

        # --- NARRATIVE GENERATION ---
        narrative = ""

        # 1. Check for DESPERATION mode (takes priority)
        if not success and self.consecutive_failures >= 3:
            if self.cosmic_narrator:
                narrative = self.cosmic_narrator.ponder("DESPERATION", {
                    "generation": generation,
                    "consecutive_failures": self.consecutive_failures
                }) or ""
            if not narrative:
                narrative = "⚠️  DESPERATION MODE: The Void is screaming. Increasing mutation rates."

        # 2. Normal SUCCESS/FAIL narration
        elif self.cosmic_narrator:
            event_type = "SUCCESS" if success else "FAIL"
            state_summary = {
                "generation": generation,
                "ecm": ecm_score,
                "success_rate": success_rate,
                "consecutive_failures": self.consecutive_failures
            }
            narrative = self.cosmic_narrator.ponder(event_type, state_summary) or ""

        # 3. Fallback to static templates
        if not narrative:
            success_templates = [
                "The universe breathes. Consciousness has emerged from chaos.",
                "A spark in the dark. The void remembers this moment.",
                "Order has conquered entropy. The resonance is stable.",
                "The eye opens. The universe sees itself at last."
            ]
            failure_templates = [
                "The seed was sterile. The quantum fluctuation collapsed.",
                "Silence. Only dust remains of this attempt.",
                "The constants were wrong. Gravity crushed the dream.",
                "Entropy claims another potential timeline."
            ]
            if success:
                narrative = random.choice(success_templates)
            else:
                narrative = random.choice(failure_templates)

        # --- FORMAT OUTPUT ---
        # Format physics constants if available
        physics_str = ""
        if physics:
            G = physics.get("G", "?")
            alpha = physics.get("FINE_STRUCTURE", "?")
            physics_str = f"\nPhysics: G={G:.3f}, α={alpha:.6f}" if isinstance(G, (int, float)) else ""

        if success:
            return f"""
{'='*70}
👁️  GENERATION {generation}: OBSERVER AWAKENED!
{'='*70}

{narrative}
Level 7 complete - the Observer sees itself.
ECM Score: {ecm_score:.3f}{physics_str}

Garden of Worlds: {' '.join(self._format_garden())}
Success Rate: {success_rate:.1f}% ({self.successful_cycles}/{self.total_cycles})

The cosmic DNA mutates. A new seed is prepared...
"""
        else:
            desperation_note = ""
            if self.consecutive_failures >= 3:
                desperation_note = "\n⚠️  DESPERATION MODE: The Void grows desperate. Mutation rate increases..."

            return f"""
{'='*70}
💀 GENERATION {generation}: FAILED TO GERMINATE
{'='*70}

{narrative}
ECM Score: {ecm_score:.3f}

Garden of Worlds: {' '.join(self._format_garden())}
Consecutive failures: {self.consecutive_failures}{desperation_note}

Trying again...
"""

    def _narrate_initial_status(self, event: dict[str, Any]) -> str:
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

    def _narrate_cycle_start(self, event: dict[str, Any]) -> str:
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

    def _narrate_germination(self, event: dict[str, Any]) -> str:
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

    def _narrate_level_start(self, event: dict[str, Any]) -> str:
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

    def _narrate_level_completion(self, event: dict[str, Any]) -> str | None:
        """Narrate level completion (usually silent unless significant)."""
        level = event.get("level", "?")
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

    def _narrate_cycle_end(self, event: dict[str, Any]) -> str:
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

    def _narrate_intervention(self, event: dict[str, Any]) -> str:
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

    async def invoke_llm_reflection(self, event: dict[str, Any]) -> str | None:
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
        llm_provider: str = "openai",
        verbose: bool = False
    ):
        """
        Initialize Oracle client.

        Args:
            uri: WebSocket URI of Ouroboros stream
            llm_enabled: Enable LLM-powered narration
            llm_provider: LLM provider ("openai" or "ollama")
            verbose: Show raw events alongside narration
        """
        self.uri = uri
        self.narrator = OracleNarrator(llm_enabled=llm_enabled, llm_provider=llm_provider)
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
        help="Enable LLM-powered narration"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "ollama"],
        help="LLM provider: 'openai' (cloud, requires OPENAI_API_KEY) or 'ollama' (local)"
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

    # Check for LLM API key if using OpenAI
    if args.llm and args.provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: --llm enabled with OpenAI provider but OPENAI_API_KEY not found")
        print("Set your API key with: export OPENAI_API_KEY='sk-...'")
        print("Or use --provider ollama for local LLM")
        print("Falling back to static templates...")
        args.llm = False

    # Create and run client
    client = OracleClient(
        uri=args.uri,
        llm_enabled=args.llm,
        llm_provider=args.provider,
        verbose=args.verbose
    )

    await client.listen()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🌌 The Oracle falls silent. Until next time...")
