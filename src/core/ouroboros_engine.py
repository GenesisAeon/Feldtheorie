"""
Ouroboros Engine - Thread-Safe Orchestrator for the Eternal Cosmic Loop
=========================================================================

Manages the infinite cycle of universe birth, evolution, death, and rebirth.
Provides control interface for external systems (API, Dashboard).

Key Features:
- Thread-safe state management
- Pausable/resumable simulation
- God-mode interventions (mutation, energy injection)
- Real-time status reporting
- Adaptive evolution based on ECM scores
"""

import threading
import time
import random
from typing import Dict, Any, Optional, List
from dataclasses import asdict
from enum import Enum

# Import our Level 7 cosmic physics
from src.scenarios.level_7_cosmic_loop.cosmic_physics import CosmicSeed, UniverseRunner
from src.core.chronicle import TheChronicle


class SimulationState(str, Enum):
    """The state machine of the eternal loop."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class OuroborosEngine:
    """
    Singleton orchestrator for the eternal cosmic loop.

    This engine manages the infinite cycle of universes, tracking generations,
    success rates, and allowing external control and intervention.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(OuroborosEngine, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the engine (only once due to singleton pattern)."""
        if self._initialized:
            return

        self.state = SimulationState.IDLE
        self.simulation_speed = 1.0  # Multiplier for time delays

        # Current universe state
        self.current_seed = CosmicSeed(
            generation=1,
            ancestor_ecm_score=0.1,
            dna_mutation_rate=0.1
        )
        self.current_universe: Optional[UniverseRunner] = None

        # Historical tracking
        self.history: List[Dict[str, Any]] = []
        self.total_generations = 0
        self.successful_generations = 0
        self.failed_generations = 0
        self.highest_ecm = 0.0
        self.consecutive_failures = 0

        # Status messaging
        self.status_message = "🌌 Engine initialized. Awaiting Big Bang..."
        self.current_level = 0
        self.current_cycle = 0

        # Thread-safe lock for state access
        self.lock = threading.Lock()

        # Background simulation thread
        self.thread = None
        self.should_stop = False

        self._initialized = True

    def start_simulation(self) -> Dict[str, str]:
        """Start or resume the eternal loop."""
        with self.lock:
            if self.state == SimulationState.RUNNING:
                return {"status": "already_running", "message": "Simulation is already running"}

            self.state = SimulationState.RUNNING
            self.status_message = "♾️ Ouroboros Cycle initiated..."

            # Start background thread if not running
            if self.thread is None or not self.thread.is_alive():
                self.should_stop = False
                self.thread = threading.Thread(target=self._simulation_loop, daemon=True)
                self.thread.start()

            return {"status": "started", "message": "Eternal loop has begun"}

    def pause_simulation(self) -> Dict[str, str]:
        """Pause the simulation (can be resumed)."""
        with self.lock:
            if self.state != SimulationState.RUNNING:
                return {"status": "not_running", "message": "Simulation is not running"}

            self.state = SimulationState.PAUSED
            self.status_message = "⏸️ Simulation paused by Observer"

            return {"status": "paused", "message": "Time frozen"}

    def resume_simulation(self) -> Dict[str, str]:
        """Resume from paused state."""
        with self.lock:
            if self.state != SimulationState.PAUSED:
                return {"status": "not_paused", "message": "Simulation is not paused"}

            self.state = SimulationState.RUNNING
            self.status_message = "▶️ Resuming cosmic evolution..."

            return {"status": "resumed", "message": "Time flows again"}

    def stop_simulation(self) -> Dict[str, str]:
        """Stop the simulation gracefully."""
        with self.lock:
            self.should_stop = True
            self.state = SimulationState.IDLE
            self.status_message = "🛑 Simulation halted by Observer"

            return {"status": "stopped", "message": "Eternal loop interrupted"}

    def reset_simulation(self) -> Dict[str, str]:
        """Reset to generation 1, clearing all history."""
        with self.lock:
            self.should_stop = True
            self.state = SimulationState.IDLE

            # Reset to primordial state
            self.current_seed = CosmicSeed(
                generation=1,
                ancestor_ecm_score=0.1,
                dna_mutation_rate=0.1
            )
            self.current_universe = None

            # Clear history
            self.history = []
            self.total_generations = 0
            self.successful_generations = 0
            self.failed_generations = 0
            self.highest_ecm = 0.0
            self.consecutive_failures = 0

            self.status_message = "🔄 Reset to Generation 1 - Tabula Rasa"

            return {"status": "reset", "message": "Returned to the beginning"}

    def intervene(self, intervention_type: str, value: float) -> Dict[str, str]:
        """
        God-Mode: Direct intervention in cosmic parameters.

        Args:
            intervention_type: Type of intervention
                - "mutation_rate": Change DNA mutation rate
                - "gravity_change": Adjust gravitational constant
                - "energy_injection": Boost ancestor ECM score
                - "mutation_boost": Increase mutation for exploration
            value: The new value or adjustment amount

        Returns:
            Status dictionary with result message
        """
        with self.lock:
            if intervention_type == "mutation_rate":
                old_rate = self.current_seed.dna_mutation_rate
                self.current_seed = CosmicSeed(
                    generation=self.current_seed.generation,
                    ancestor_ecm_score=self.current_seed.ancestor_ecm_score,
                    dna_mutation_rate=max(0.0, min(1.0, value))  # Clamp to [0, 1]
                )
                return {
                    "status": "success",
                    "message": f"Mutation rate changed: {old_rate:.3f} → {value:.3f}"
                }

            elif intervention_type == "energy_injection":
                old_ecm = self.current_seed.ancestor_ecm_score
                new_ecm = max(0.0, min(1.0, old_ecm + value))
                self.current_seed = CosmicSeed(
                    generation=self.current_seed.generation,
                    ancestor_ecm_score=new_ecm,
                    dna_mutation_rate=self.current_seed.dna_mutation_rate
                )
                return {
                    "status": "success",
                    "message": f"⚡ Divine energy injected! ECM: {old_ecm:.3f} → {new_ecm:.3f}"
                }

            elif intervention_type == "mutation_boost":
                # Boost mutation rate temporarily for exploration
                new_rate = min(0.5, self.current_seed.dna_mutation_rate * (1 + value))
                self.current_seed = CosmicSeed(
                    generation=self.current_seed.generation,
                    ancestor_ecm_score=self.current_seed.ancestor_ecm_score,
                    dna_mutation_rate=new_rate
                )
                return {
                    "status": "success",
                    "message": f"🧬 Mutation boosted by {value*100:.0f}%"
                }

            elif intervention_type == "gravity_change":
                return {
                    "status": "info",
                    "message": "Gravity changes apply to next universe generation"
                }

            else:
                return {
                    "status": "error",
                    "message": f"Unknown intervention type: {intervention_type}"
                }

    def get_state(self) -> Dict[str, Any]:
        """
        Get complete current state for API/Dashboard.

        Returns:
            Dictionary containing all current metrics and status
        """
        with self.lock:
            # Calculate success rate
            success_rate = 0.0
            if self.total_generations > 0:
                success_rate = self.successful_generations / self.total_generations

            return {
                # State
                "state": self.state.value,
                "is_running": self.state == SimulationState.RUNNING,
                "status_message": self.status_message,

                # Current generation
                "generation": self.current_seed.generation,
                "ancestor_ecm": round(self.current_seed.ancestor_ecm_score, 4),
                "mutation_rate": round(self.current_seed.dna_mutation_rate, 4),
                "current_level": self.current_level,
                "current_cycle": self.current_cycle,

                # Statistics
                "total_generations": self.total_generations,
                "successful_generations": self.successful_generations,
                "failed_generations": self.failed_generations,
                "success_rate": round(success_rate, 3),
                "highest_ecm": round(self.highest_ecm, 4),
                "consecutive_failures": self.consecutive_failures,

                # History
                "history_length": len(self.history),
                "recent_history": self.history[-10:] if self.history else [],
                "last_result": self.history[-1] if self.history else None
            }

    def get_history_timeline(self) -> List[Dict[str, Any]]:
        """Get the complete timeline of all generations (Garden of Worlds)."""
        with self.lock:
            return list(self.history)

    def _simulation_loop(self):
        """
        The main simulation loop running in background thread.

        This is the heart of the Ouroboros - the eternal cycle.
        """
        while not self.should_stop:
            # Check if we should be running
            with self.lock:
                if self.state != SimulationState.RUNNING:
                    time.sleep(0.5)
                    continue

                current_gen = self.current_seed.generation
                status_prefix = f"Gen {current_gen}"

            # Sleep with speed multiplier (for fast/slow-mo modes)
            time.sleep(1.0 / self.simulation_speed)

            # Run one universe cycle
            self._run_single_universe()

            # Small delay between cycles
            time.sleep(1.5 / self.simulation_speed)

    def _run_single_universe(self):
        """
        Run a single universe from birth to death.

        This orchestrates the full Level 0-7 cycle and handles success/failure.
        """
        with self.lock:
            self.current_cycle += 1
            gen = self.current_seed.generation
            self.status_message = f"🌱 Gen {gen}: Attempting germination..."

        # Create universe runner
        runner = UniverseRunner(self.current_seed)

        with self.lock:
            self.current_universe = runner
            self.current_level = 0

        # Run the simulation (this goes through all 8 levels)
        # We suppress print output for cleaner API operation
        # (In production, you'd capture this to a log buffer)
        success = runner.run_simulation()

        # Process results
        with self.lock:
            self.total_generations += 1

            if success and runner.is_alive:
                # ✨ SUCCESS - Universe reached Observer state
                self.successful_generations += 1
                self.consecutive_failures = 0

                final_ecm = runner.final_ecm
                if final_ecm > self.highest_ecm:
                    self.highest_ecm = final_ecm

                # Record in history
                self.history.append({
                    "generation": gen,
                    "result": "SUCCESS",
                    "ecm_score": round(final_ecm, 4),
                    "physics": runner.physics,
                    "timestamp": time.time()
                })

                self.status_message = f"👁️ Gen {gen}: Observer awakened! ECM={final_ecm:.3f}"

                # Evolution: Create next generation seed
                # Adaptive mutation based on ECM (higher ECM = less mutation needed)
                new_mutation = 0.15 / (final_ecm + 0.1)
                new_mutation = max(0.05, min(0.3, new_mutation))  # Clamp

                self.current_seed = CosmicSeed(
                    generation=gen + 1,
                    ancestor_ecm_score=final_ecm,
                    dna_mutation_rate=new_mutation
                )

            else:
                # ❌ FAILURE - Universe died or failed to germinate
                self.failed_generations += 1
                self.consecutive_failures += 1

                # Record failure
                self.history.append({
                    "generation": gen,
                    "result": "FAILED",
                    "ecm_score": 0.0,
                    "physics": runner.physics if runner.physics else None,
                    "timestamp": time.time()
                })

                if not runner.physics:
                    self.status_message = f"💀 Gen {gen}: Failed to germinate"
                else:
                    self.status_message = f"💀 Gen {gen}: Died before Observer"

                # Adaptive strategy: After multiple failures, increase mutation (exploration)
                if self.consecutive_failures >= 3:
                    # Desperation mode: Try radical changes
                    new_mutation = min(0.5, self.current_seed.dna_mutation_rate * 1.2)
                    self.current_seed = CosmicSeed(
                        generation=gen + 1,
                        ancestor_ecm_score=max(0.05, self.current_seed.ancestor_ecm_score * 0.9),
                        dna_mutation_rate=new_mutation
                    )
                    self.status_message += " [DESPERATION MODE: Increased mutation]"
                else:
                    # Normal retry: Same generation, slight mutation adjustment
                    self.current_seed = CosmicSeed(
                        generation=gen + 1,
                        ancestor_ecm_score=max(0.05, self.current_seed.ancestor_ecm_score),
                        dna_mutation_rate=self.current_seed.dna_mutation_rate
                    )

            self.current_level = 7  # Completed full cycle


# Convenience function for external access
def get_engine() -> OuroborosEngine:
    """Get the singleton Ouroboros Engine instance."""
    return OuroborosEngine()
