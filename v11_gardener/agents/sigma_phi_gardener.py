"""
v11 Gardener Prototype - σ_Φ Homeostatic Gardener Agent

Evolution from v9:
    v9:  EFI-based cultivation (Entropy Fertility Index)
    v11: σ_Φ homeostasis - maintains "living crystal" signature

Goal: Keep agents in the metastable zone where:
    σ_Φ ∈ [0.0525, 0.0725] ≈ 1/16 ± 0.01

The Gardener doesn't control - it cultivates resonance.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.constants import (
    SIGMA_PHI,
    SIGMA_PHI_MIN,
    SIGMA_PHI_MAX,
    SIGMA_PHI_TOLERANCE,
    KAPPA_TARGET,
    ACTION_LEARNING_RATE,
    is_alive,
    health_indicator,
    calculate_sigma_phi,
)


class CultivationAction(Enum):
    """Cultivation actions for σ_Φ homeostasis"""
    COOL = "cool"  # Reduce entropy (system too chaotic, σ_Φ too high)
    WARM = "warm"  # Increase entropy (system too ordered, σ_Φ too low)
    STABILIZE = "stabilize"  # Maintain current state (σ_Φ in optimal range)
    RESUSCITATE = "resuscitate"  # Emergency action for critically low σ_Φ
    DAMPEN = "dampen"  # Emergency action for critically high σ_Φ
    OBSERVE = "observe"  # No action needed


@dataclass
class AgentHealth:
    """Health assessment of a single agent"""
    agent_id: str
    sigma_phi: float  # Current σ_Φ value
    entropy: float  # Current entropy (bits)
    temperature: float  # Effective "temperature" (activity level)
    kappa_total: float  # Total coupling strength
    resonance_quality: float  # Quality of resonance with neighbors
    is_alive: bool  # Within living range?
    health_status: str  # Health indicator string
    recommended_action: CultivationAction
    action_strength: float  # How strongly to apply (0.0-1.0)
    persistence_time: int  # How long in current state (timesteps)

    def __repr__(self):
        status_emoji = "✨" if self.is_alive else "💀"
        return (f"AgentHealth({status_emoji} {self.agent_id}, "
                f"σ_Φ={self.sigma_phi:.4f}, "
                f"action={self.recommended_action.value}, "
                f"strength={self.action_strength:.2f})")


@dataclass
class GardenerMemory:
    """Memory of past cultivation cycles"""
    cycle_history: List[Dict] = field(default_factory=list)
    alive_count_history: List[int] = field(default_factory=list)
    mean_sigma_phi_history: List[float] = field(default_factory=list)
    emergent_events: List[Dict] = field(default_factory=list)


class SigmaPhiGardener:
    """
    σ_Φ Homeostatic Gardener Agent

    Maintains the "living crystal" signature across a multi-agent system.

    Core principle:
        σ_Φ = H / H_max ≈ 1/16 = 0.0625

    where:
        H: Shannon entropy of agent state
        H_max: Maximum possible entropy (4.0 bits for 4-bit systems)

    Cultivation strategy:
        - σ_Φ < 0.0525 → WARM (increase entropy, prevent crystal death)
        - σ_Φ > 0.0725 → COOL (decrease entropy, prevent thermal chaos)
        - σ_Φ ∈ [0.0525, 0.0725] → STABILIZE (maintain metastability)
    """

    def __init__(
        self,
        name: str = "SigmaPhiGardener",
        sigma_phi_target: float = SIGMA_PHI,
        tolerance: float = SIGMA_PHI_TOLERANCE,
        action_learning_rate: float = ACTION_LEARNING_RATE,
        kappa_target: float = KAPPA_TARGET,
        emergency_threshold: float = 0.02,  # How far from target triggers emergency
    ):
        """
        Initialize σ_Φ Homeostatic Gardener

        Args:
            name: Gardener identifier
            sigma_phi_target: Target σ_Φ value (default: 0.0625)
            tolerance: Acceptable deviation (default: 0.01)
            action_learning_rate: Strength of cultivation actions (0.0-1.0)
            kappa_target: Optimal coupling strength
            emergency_threshold: Distance from target that triggers emergency actions
        """
        self.name = name
        self.sigma_phi_target = sigma_phi_target
        self.tolerance = tolerance
        self.action_learning_rate = action_learning_rate
        self.kappa_target = kappa_target
        self.emergency_threshold = emergency_threshold

        # Bounds
        self.sigma_phi_min = sigma_phi_target - tolerance
        self.sigma_phi_max = sigma_phi_target + tolerance

        # Emergency bounds (further out)
        self.emergency_min = sigma_phi_target - emergency_threshold
        self.emergency_max = sigma_phi_target + emergency_threshold

        # Memory
        self.memory = GardenerMemory()

        # Agent persistence tracking (how long each agent has been in current state)
        self.agent_persistence: Dict[str, int] = {}

    def assess_agent(
        self,
        agent_id: str,
        sigma_phi: float,
        entropy: float,
        temperature: float,
        kappa_total: float,
        resonance_quality: float,
    ) -> AgentHealth:
        """
        Assess individual agent health and recommend action

        Args:
            agent_id: Agent identifier
            sigma_phi: Current σ_Φ value
            entropy: Current entropy (bits)
            temperature: Effective temperature (activity level)
            kappa_total: Total coupling strength
            resonance_quality: Quality of resonance (0.0-1.0)

        Returns:
            AgentHealth assessment
        """
        # Check if alive
        alive = is_alive(sigma_phi)
        health_status = health_indicator(sigma_phi)

        # Update persistence tracking
        if agent_id not in self.agent_persistence:
            self.agent_persistence[agent_id] = 0
        else:
            self.agent_persistence[agent_id] += 1

        persistence_time = self.agent_persistence[agent_id]

        # Determine cultivation action
        deviation = sigma_phi - self.sigma_phi_target

        # EMERGENCY ACTIONS (far from target)
        if sigma_phi < self.emergency_min:
            # Critical: too ordered, approaching crystal death
            action = CultivationAction.RESUSCITATE
            strength = min(1.0, abs(deviation) / self.emergency_threshold)

        elif sigma_phi > self.emergency_max:
            # Critical: too chaotic, approaching thermal runaway
            action = CultivationAction.DAMPEN
            strength = min(1.0, abs(deviation) / self.emergency_threshold)

        # NORMAL HOMEOSTATIC ACTIONS
        elif sigma_phi < self.sigma_phi_min:
            # Too ordered, needs warming
            action = CultivationAction.WARM
            strength = abs(deviation) / self.tolerance

        elif sigma_phi > self.sigma_phi_max:
            # Too chaotic, needs cooling
            action = CultivationAction.COOL
            strength = abs(deviation) / self.tolerance

        elif abs(deviation) < self.tolerance / 2:
            # Well within optimal range, just stabilize
            action = CultivationAction.STABILIZE
            strength = 1.0 - (abs(deviation) / (self.tolerance / 2))

        else:
            # No action needed, just observe
            action = CultivationAction.OBSERVE
            strength = 0.0

        return AgentHealth(
            agent_id=agent_id,
            sigma_phi=sigma_phi,
            entropy=entropy,
            temperature=temperature,
            kappa_total=kappa_total,
            resonance_quality=resonance_quality,
            is_alive=alive,
            health_status=health_status,
            recommended_action=action,
            action_strength=strength,
            persistence_time=persistence_time,
        )

    def cultivate_ecosystem(
        self,
        agent_states: Dict[str, Dict[str, float]],
        coupling_matrix: np.ndarray,
        agent_ids: List[str],
        timestep: int = 0,
    ) -> Tuple[np.ndarray, Dict[str, float], List[AgentHealth]]:
        """
        Cultivate entire multi-agent ecosystem

        Args:
            agent_states: Dict mapping agent_id to state dict
                         (sigma_phi, entropy, temperature, kappa_total, resonance_quality)
            coupling_matrix: Current NxN coupling matrix
            agent_ids: Ordered list of agent IDs
            timestep: Current simulation timestep

        Returns:
            (adjusted_coupling_matrix, adjusted_temperatures, agent_assessments)
        """
        assessments = []
        adjusted_matrix = coupling_matrix.copy()
        adjusted_temps = {}

        # Assess all agents
        for i, agent_id in enumerate(agent_ids):
            if agent_id not in agent_states:
                continue

            state = agent_states[agent_id]
            assessment = self.assess_agent(
                agent_id=agent_id,
                sigma_phi=state.get('sigma_phi', 0.0),
                entropy=state.get('entropy', 0.0),
                temperature=state.get('temperature', 1.0),
                kappa_total=state.get('kappa_total', 0.0),
                resonance_quality=state.get('resonance_quality', 0.5),
            )
            assessments.append(assessment)

            # Apply cultivation action
            temp_adjustment = self._apply_action(
                assessment=assessment,
                agent_idx=i,
                coupling_matrix=adjusted_matrix,
            )

            adjusted_temps[agent_id] = temp_adjustment

        # Ensure matrix stays symmetric
        adjusted_matrix = (adjusted_matrix + adjusted_matrix.T) / 2

        # Record cycle
        self._record_cycle(timestep, assessments)

        # Detect emergent events
        self._detect_emergence(assessments, timestep)

        return adjusted_matrix, adjusted_temps, assessments

    def _apply_action(
        self,
        assessment: AgentHealth,
        agent_idx: int,
        coupling_matrix: np.ndarray,
    ) -> float:
        """
        Apply cultivation action to agent

        Returns:
            Temperature adjustment factor
        """
        action = assessment.recommended_action
        strength = assessment.action_strength

        temp_adjustment = 1.0  # Default: no change

        if action == CultivationAction.COOL:
            # Reduce temperature (decrease entropy production)
            temp_adjustment = 1.0 - (self.action_learning_rate * strength)
            # Slightly reduce coupling to dampen interactions
            factor = 1.0 - (self.action_learning_rate * strength * 0.5)
            coupling_matrix[agent_idx, :] *= factor
            coupling_matrix[:, agent_idx] *= factor

        elif action == CultivationAction.WARM:
            # Increase temperature (increase entropy production)
            temp_adjustment = 1.0 + (self.action_learning_rate * strength)
            # Slightly increase coupling to encourage interactions
            factor = 1.0 + (self.action_learning_rate * strength * 0.5)
            coupling_matrix[agent_idx, :] *= factor
            coupling_matrix[:, agent_idx] *= factor

        elif action == CultivationAction.RESUSCITATE:
            # Emergency warming
            temp_adjustment = 1.0 + (self.action_learning_rate * strength * 2.0)
            # Boost coupling significantly
            factor = 1.0 + (self.action_learning_rate * strength)
            coupling_matrix[agent_idx, :] *= factor
            coupling_matrix[:, agent_idx] *= factor

        elif action == CultivationAction.DAMPEN:
            # Emergency cooling
            temp_adjustment = 1.0 - (self.action_learning_rate * strength * 2.0)
            # Reduce coupling significantly
            factor = 1.0 - (self.action_learning_rate * strength)
            coupling_matrix[agent_idx, :] *= factor
            coupling_matrix[:, agent_idx] *= factor

        elif action == CultivationAction.STABILIZE:
            # Gentle normalization toward target
            # Keep temperature but normalize coupling
            current_sum = np.sum(coupling_matrix[agent_idx, :])
            if current_sum > 0:
                target_sum = self.kappa_target * len(coupling_matrix)
                gentle_factor = 1.0 + self.action_learning_rate * 0.5 * (target_sum / current_sum - 1.0)
                coupling_matrix[agent_idx, :] *= gentle_factor
                coupling_matrix[:, agent_idx] *= gentle_factor

        # Ensure temperature stays positive and reasonable
        temp_adjustment = np.clip(temp_adjustment, 0.1, 3.0)

        return temp_adjustment

    def _record_cycle(self, timestep: int, assessments: List[AgentHealth]):
        """Record cultivation cycle in memory"""
        alive_count = sum(1 for a in assessments if a.is_alive)
        mean_sigma_phi = np.mean([a.sigma_phi for a in assessments])

        self.memory.cycle_history.append({
            'timestep': timestep,
            'assessments': assessments,
            'alive_count': alive_count,
            'mean_sigma_phi': mean_sigma_phi,
            'actions': {
                'cool': sum(1 for a in assessments if a.recommended_action == CultivationAction.COOL),
                'warm': sum(1 for a in assessments if a.recommended_action == CultivationAction.WARM),
                'stabilize': sum(1 for a in assessments if a.recommended_action == CultivationAction.STABILIZE),
                'resuscitate': sum(1 for a in assessments if a.recommended_action == CultivationAction.RESUSCITATE),
                'dampen': sum(1 for a in assessments if a.recommended_action == CultivationAction.DAMPEN),
                'observe': sum(1 for a in assessments if a.recommended_action == CultivationAction.OBSERVE),
            }
        })

        self.memory.alive_count_history.append(alive_count)
        self.memory.mean_sigma_phi_history.append(mean_sigma_phi)

    def _detect_emergence(self, assessments: List[AgentHealth], timestep: int):
        """Detect emergent events in the ecosystem"""
        # Event 1: Full resonance (all agents alive)
        if all(a.is_alive for a in assessments):
            if not any(e.get('type') == 'full_resonance' for e in self.memory.emergent_events[-5:]):
                self.memory.emergent_events.append({
                    'timestep': timestep,
                    'type': 'full_resonance',
                    'description': 'All agents achieved σ_Φ homeostasis',
                    'mean_sigma_phi': np.mean([a.sigma_phi for a in assessments]),
                })

        # Event 2: Critical state (>50% in emergency)
        emergency_count = sum(1 for a in assessments
                            if a.recommended_action in [CultivationAction.RESUSCITATE, CultivationAction.DAMPEN])
        if emergency_count > len(assessments) / 2:
            self.memory.emergent_events.append({
                'timestep': timestep,
                'type': 'critical_state',
                'description': f'{emergency_count}/{len(assessments)} agents in emergency',
                'emergency_count': emergency_count,
            })

        # Event 3: Perfect convergence (all agents within ±0.005 of target)
        perfect_count = sum(1 for a in assessments if abs(a.sigma_phi - SIGMA_PHI) < 0.005)
        if perfect_count == len(assessments):
            self.memory.emergent_events.append({
                'timestep': timestep,
                'type': 'perfect_convergence',
                'description': 'All agents converged to σ_Φ ≈ 0.0625 ± 0.005',
                'std_sigma_phi': np.std([a.sigma_phi for a in assessments]),
            })

    def get_cultivation_summary(self) -> Dict:
        """Get summary statistics of cultivation history"""
        if not self.memory.cycle_history:
            return {'cycles': 0}

        total_actions = {action: 0 for action in ['cool', 'warm', 'stabilize', 'resuscitate', 'dampen', 'observe']}
        for cycle in self.memory.cycle_history:
            for action, count in cycle['actions'].items():
                total_actions[action] += count

        return {
            'gardener_name': self.name,
            'cycles': len(self.memory.cycle_history),
            'alive_count_history': self.memory.alive_count_history,
            'mean_sigma_phi_history': self.memory.mean_sigma_phi_history,
            'final_alive_count': self.memory.alive_count_history[-1] if self.memory.alive_count_history else 0,
            'final_mean_sigma_phi': self.memory.mean_sigma_phi_history[-1] if self.memory.mean_sigma_phi_history else 0.0,
            'total_actions': total_actions,
            'emergent_events': self.memory.emergent_events,
            'cultivation_style': self._classify_style(total_actions),
        }

    def _classify_style(self, actions: Dict[str, int]) -> str:
        """Classify gardener's cultivation style"""
        total = sum(actions.values())
        if total == 0:
            return "observer"

        emergency_ratio = (actions['resuscitate'] + actions['dampen']) / total
        homeostatic_ratio = (actions['cool'] + actions['warm']) / total
        stable_ratio = actions['stabilize'] / total

        if emergency_ratio > 0.3:
            return "emergency_responder"
        elif stable_ratio > 0.5:
            return "stabilizer"
        elif homeostatic_ratio > 0.5:
            return "active_homeostatic"
        else:
            return "balanced"
