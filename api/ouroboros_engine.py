"""
OUROBOROS ENGINE
=================

The central orchestrator for the 8-Level Cosmology Simulation.

This engine manages the eternal loop from Level 0 (The Void) to Level 7 (The Cosmic Loop),
providing a stateful interface for external control and observation.

Levels:
-------
- Level 0: The Void (Geometry creates particles)
- Level 1: The Atom (Probability creates orbitals)
- Level 2: The Star (Gravity creates fusion)
- Level 3: The Chronicle (Death creates information)
- Level 4: The Planet (Cooling creates geology)
- Level 5: The Life (Resonance creates replication)
- Level 6: The Mind (Synchronization creates consciousness)
- Level 7: The Loop (Observation creates new physics)

Architecture:
-------------
The engine maintains a persistent state across multiple simulation cycles,
allowing for:
- Live status queries
- Mid-simulation interventions
- Agent dialogue with running systems
- Evolutionary tracking across generations
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


class SimulationState(str, Enum):
    """Current state of the simulation."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class UniverseMetrics:
    """Metrics for a single universe instance."""
    generation: int
    cycle_number: int
    current_level: int
    ecm_score: float = 0.0
    is_alive: bool = True
    particle_count: int = 0
    energy_level: float = 0.0
    complexity_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CosmicHistory:
    """Historical record of universe attempts."""
    total_cycles: int = 0
    successful_universes: int = 0
    failed_universes: int = 0
    timeline: List[str] = field(default_factory=list)  # ["SUCCESS", "FAIL", ...]
    successful_metrics: List[UniverseMetrics] = field(default_factory=list)
    current_generation: int = 1
    highest_ecm_score: float = 0.0


class OuroborosEngine:
    """
    The Ouroboros Engine: A self-contained cosmology simulator.

    This class orchestrates the entire simulation lifecycle, from the primordial
    void to conscious reincarnation, while providing real-time status and control.

    Attributes:
        state: Current simulation state (idle, running, paused, etc.)
        current_metrics: Metrics for the current universe instance
        history: Aggregated history across all cycles
        config: Configuration parameters (G, mutation_rate, etc.)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Ouroboros Engine.

        Args:
            config: Optional configuration dictionary with parameters like:
                - base_ecm: Initial ECM score (default: 0.1)
                - mutation_rate: DNA mutation rate (default: 0.15)
                - gravity: Gravitational constant (default: 1.0)
                - max_cycles: Maximum cycles to run (default: None = infinite)
        """
        self.state = SimulationState.IDLE
        self.current_metrics = UniverseMetrics(generation=1, cycle_number=0, current_level=0)
        self.history = CosmicHistory()

        # Default configuration
        self.config = {
            "base_ecm": 0.1,
            "mutation_rate": 0.15,
            "gravity": 1.0,
            "max_cycles": None,
            "enable_interventions": True,
            "pause_between_cycles": 2.0,  # seconds
        }

        if config:
            self.config.update(config)

        # Runtime state
        self._current_seed = None
        self._task: Optional[asyncio.Task] = None
        self._observers: List[asyncio.Queue] = []  # For WebSocket streaming

    async def start_simulation(self):
        """
        Start the eternal cosmic loop.

        Runs asynchronously, allowing external queries during execution.
        """
        if self.state == SimulationState.RUNNING:
            raise RuntimeError("Simulation is already running")

        self.state = SimulationState.RUNNING
        self._task = asyncio.create_task(self._eternal_loop())

        await self._broadcast_event({
            "type": "simulation_started",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    async def pause_simulation(self):
        """Pause the running simulation."""
        if self.state != SimulationState.RUNNING:
            raise RuntimeError("Cannot pause: simulation is not running")

        self.state = SimulationState.PAUSED
        await self._broadcast_event({"type": "simulation_paused"})

    async def resume_simulation(self):
        """Resume a paused simulation."""
        if self.state != SimulationState.PAUSED:
            raise RuntimeError("Cannot resume: simulation is not paused")

        self.state = SimulationState.RUNNING
        await self._broadcast_event({"type": "simulation_resumed"})

    async def stop_simulation(self):
        """Stop the simulation gracefully."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        self.state = SimulationState.COMPLETED
        await self._broadcast_event({"type": "simulation_stopped"})

    async def reset_simulation(self):
        """Reset the simulation to initial state."""
        await self.stop_simulation()

        self.current_metrics = UniverseMetrics(generation=1, cycle_number=0, current_level=0)
        self.history = CosmicHistory()
        self._current_seed = None
        self.state = SimulationState.IDLE

        await self._broadcast_event({"type": "simulation_reset"})

    async def intervene(self, intervention_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        God-mode intervention in the running universe.

        Args:
            intervention_type: Type of intervention ("asteroid", "gravity_change", "mutation_boost", etc.)
            params: Parameters for the intervention

        Returns:
            Result of the intervention
        """
        if not self.config["enable_interventions"]:
            raise RuntimeError("Interventions are disabled in configuration")

        result = {
            "success": True,
            "intervention": intervention_type,
            "applied_at": {
                "cycle": self.current_metrics.cycle_number,
                "level": self.current_metrics.current_level,
                "generation": self.current_metrics.generation
            },
            "effects": {}
        }

        # Apply intervention based on type
        if intervention_type == "gravity_change":
            old_g = self.config["gravity"]
            self.config["gravity"] = params.get("new_gravity", 1.0)
            result["effects"] = {"old_gravity": old_g, "new_gravity": self.config["gravity"]}

        elif intervention_type == "mutation_boost":
            old_rate = self.config["mutation_rate"]
            self.config["mutation_rate"] = params.get("new_rate", 0.15)
            result["effects"] = {"old_rate": old_rate, "new_rate": self.config["mutation_rate"]}

        elif intervention_type == "energy_injection":
            energy_boost = params.get("energy", 100.0)
            self.current_metrics.energy_level += energy_boost
            result["effects"] = {"energy_added": energy_boost, "new_level": self.current_metrics.energy_level}

        else:
            result["success"] = False
            result["error"] = f"Unknown intervention type: {intervention_type}"

        await self._broadcast_event({
            "type": "intervention_applied",
            "intervention": result
        })

        return result

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the simulation.

        Returns:
            Comprehensive status dictionary
        """
        return {
            "state": self.state.value,
            "current_metrics": {
                "generation": self.current_metrics.generation,
                "cycle": self.current_metrics.cycle_number,
                "level": self.current_metrics.current_level,
                "ecm_score": self.current_metrics.ecm_score,
                "is_alive": self.current_metrics.is_alive,
                "particle_count": self.current_metrics.particle_count,
                "energy": self.current_metrics.energy_level,
                "complexity": self.current_metrics.complexity_score,
            },
            "history": {
                "total_cycles": self.history.total_cycles,
                "successful": self.history.successful_universes,
                "failed": self.history.failed_universes,
                "success_rate": (
                    self.history.successful_universes / self.history.total_cycles * 100
                    if self.history.total_cycles > 0 else 0.0
                ),
                "current_generation": self.history.current_generation,
                "highest_ecm": self.history.highest_ecm_score,
                "timeline_recent": self.history.timeline[-20:],  # Last 20 attempts
            },
            "config": self.config,
        }

    async def subscribe_observer(self) -> asyncio.Queue:
        """
        Subscribe to real-time events.

        Returns:
            An asyncio.Queue that will receive event dictionaries
        """
        queue = asyncio.Queue()
        self._observers.append(queue)
        return queue

    async def unsubscribe_observer(self, queue: asyncio.Queue):
        """Unsubscribe from events."""
        if queue in self._observers:
            self._observers.remove(queue)

    # ═══════════════════════════════════════════════════════════════════════════
    # Private Methods: The Internal Mechanics
    # ═══════════════════════════════════════════════════════════════════════════

    async def _eternal_loop(self):
        """
        The main simulation loop.

        This is the heart of the Ouroboros: the eternal cycle of birth, death,
        and reincarnation.
        """
        try:
            while True:
                # Check if we should stop
                if self.config["max_cycles"] and self.history.total_cycles >= self.config["max_cycles"]:
                    break

                # Wait if paused
                while self.state == SimulationState.PAUSED:
                    await asyncio.sleep(0.1)

                # Run one cycle
                await self._run_single_cycle()

                # Pause between cycles
                if self.config["pause_between_cycles"] > 0:
                    await asyncio.sleep(self.config["pause_between_cycles"])

        except asyncio.CancelledError:
            self.state = SimulationState.COMPLETED
            raise

        except Exception as e:
            self.state = SimulationState.FAILED
            await self._broadcast_event({
                "type": "simulation_error",
                "error": str(e)
            })
            raise

    async def _run_single_cycle(self):
        """
        Run a single universe cycle from Level 0 to Level 7.

        This simulates the complete cosmological evolution:
        1. Try to germinate a cosmic seed
        2. If successful, evolve through all levels
        3. Extract final ECM score
        4. Create new seed for next generation
        """
        self.history.total_cycles += 1
        self.current_metrics.cycle_number = self.history.total_cycles

        await self._broadcast_event({
            "type": "cycle_started",
            "cycle": self.history.total_cycles,
            "generation": self.current_metrics.generation
        })

        # Simulate germination (Level 0-7 in simplified form)
        # In a full implementation, this would call actual level physics
        germinated = await self._try_germination()

        if germinated:
            # Successful universe!
            final_ecm = await self._evolve_through_levels()

            if final_ecm > 0:
                self._handle_success(final_ecm)
            else:
                self._handle_failure()
        else:
            # Failed to germinate
            self._handle_failure()

        await self._broadcast_event({
            "type": "cycle_completed",
            "cycle": self.history.total_cycles,
            "success": self.current_metrics.is_alive
        })

    async def _try_germination(self) -> bool:
        """
        Try to germinate a cosmic seed.

        Returns:
            True if germination succeeded
        """
        # Calculate germination probability based on ancestral ECM
        base_chance = 0.4
        ancestor_ecm = self.config.get("base_ecm", 0.1) if self.history.total_cycles == 1 else self.current_metrics.ecm_score

        success_prob = base_chance + (ancestor_ecm * 0.2)
        success_prob -= self.config["mutation_rate"] * 0.3  # Stability penalty

        roll = random.random()
        germinated = roll < success_prob

        await self._broadcast_event({
            "type": "germination_attempt",
            "success": germinated,
            "probability": success_prob,
            "roll": roll
        })

        return germinated

    async def _evolve_through_levels(self) -> float:
        """
        Evolve through all 8 levels.

        Returns:
            Final ECM score
        """
        ecm_accumulator = 0.0

        for level in range(8):
            self.current_metrics.current_level = level

            await self._broadcast_event({
                "type": "level_started",
                "level": level
            })

            # Simulate level progression (simplified)
            # In full implementation, this would call actual level physics modules
            await asyncio.sleep(0.2)  # Simulate processing time

            # Each level contributes to ECM
            level_contribution = random.uniform(0.05, 0.15) * (1 + level * 0.1)
            ecm_accumulator += level_contribution

            # Update metrics
            self.current_metrics.particle_count += random.randint(10, 100)
            self.current_metrics.energy_level += random.uniform(5, 20)
            self.current_metrics.complexity_score = ecm_accumulator

            await self._broadcast_event({
                "type": "level_completed",
                "level": level,
                "ecm_contribution": level_contribution,
                "total_ecm": ecm_accumulator
            })

        return ecm_accumulator

    def _handle_success(self, final_ecm: float):
        """Handle a successful universe."""
        self.history.successful_universes += 1
        self.history.timeline.append("SUCCESS")
        self.current_metrics.ecm_score = final_ecm
        self.current_metrics.is_alive = True

        # Track metrics
        self.history.successful_metrics.append(
            UniverseMetrics(
                generation=self.current_metrics.generation,
                cycle_number=self.current_metrics.cycle_number,
                current_level=7,
                ecm_score=final_ecm,
                is_alive=True,
                particle_count=self.current_metrics.particle_count,
                energy_level=self.current_metrics.energy_level,
                complexity_score=self.current_metrics.complexity_score
            )
        )

        # Update records
        if final_ecm > self.history.highest_ecm_score:
            self.history.highest_ecm_score = final_ecm

        # Prepare next generation
        self.history.current_generation += 1
        self.current_metrics.generation = self.history.current_generation

        # Adaptive mutation: higher ECM = lower mutation (fine-tuning)
        new_mutation = 0.15 / (final_ecm + 0.1)
        self.config["mutation_rate"] = max(0.05, min(new_mutation, 0.3))

    def _handle_failure(self):
        """Handle a failed universe."""
        self.history.failed_universes += 1
        self.history.timeline.append("FAIL")
        self.current_metrics.is_alive = False

        # Check for repeated failures
        recent_failures = self.history.timeline[-3:].count("FAIL")
        if recent_failures >= 3:
            # Increase mutation rate (desperation mode)
            self.config["mutation_rate"] = min(0.3, self.config["mutation_rate"] * 1.2)

    async def _broadcast_event(self, event: Dict[str, Any]):
        """Broadcast an event to all observers."""
        for queue in self._observers:
            try:
                await queue.put(event)
            except Exception:
                # Remove dead observers
                self._observers.remove(queue)
