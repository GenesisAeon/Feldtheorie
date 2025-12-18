"""
v11 Gardener Prototype - Multi-Agent Ecosystem

A self-organizing system of agents that:
1. Interact via resonance coupling (κ-matrix)
2. Evolve their σ_Φ signatures dynamically
3. Are cultivated by Gardener agents to maintain metastability
4. Exhibit emergent collective behavior

This is not a simulation - it's a demonstration of living resonance.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.constants import (
    SIGMA_PHI,
    KAPPA_TARGET,
    calculate_sigma_phi,
    is_alive,
    utac_activation,
)


@dataclass
class Agent:
    """Individual agent in the ecosystem"""
    agent_id: str
    position: np.ndarray  # 2D position in resonance field
    entropy: float = 2.5  # Current entropy (bits)
    max_entropy: float = 4.0  # Maximum entropy (4-bit system)
    temperature: float = 1.0  # Effective temperature (activity level)
    internal_state: np.ndarray = field(default_factory=lambda: np.random.rand(4))  # 4-bit internal state
    beta: float = 7.4  # UTAC β parameter (biological regime by default)
    theta: float = 0.5  # UTAC threshold

    @property
    def sigma_phi(self) -> float:
        """Calculate current σ_Φ from entropy"""
        return calculate_sigma_phi(self.entropy, self.max_entropy)

    @property
    def readiness(self) -> float:
        """Calculate UTAC readiness from internal state"""
        return float(np.mean(self.internal_state))

    @property
    def activation(self) -> float:
        """UTAC activation level"""
        return utac_activation(self.readiness, self.theta, self.beta)

    def update_entropy(self, dt: float = 0.1):
        """
        Update entropy based on temperature and internal dynamics

        dH/dt = T × (production) - (dissipation)
        """
        # Entropy production (increases with temperature)
        production = self.temperature * np.random.normal(0.1, 0.05)

        # Entropy dissipation (natural decay toward equilibrium)
        # For σ_Φ ≈ 0.0625 with H_max=4.0, equilibrium should be H ≈ 0.25
        equilibrium_entropy = 0.25  # Target σ_Φ ≈ 0.0625
        dissipation = 0.1 * (self.entropy - equilibrium_entropy)  # Stronger dissipation

        # Update
        dH = (production - dissipation) * dt
        self.entropy = np.clip(self.entropy + dH, 0.0, self.max_entropy)

    def interact(self, other: 'Agent', coupling_strength: float, dt: float = 0.1):
        """
        Interact with another agent via resonance coupling

        Coupling transfers entropy and influences internal states
        """
        # Entropy exchange (flows from high to low)
        entropy_gradient = self.entropy - other.entropy
        entropy_flow = coupling_strength * entropy_gradient * dt * 0.1

        self.entropy -= entropy_flow
        other.entropy += entropy_flow

        # State resonance (states become more similar with coupling)
        state_difference = other.internal_state - self.internal_state
        state_flow = coupling_strength * state_difference * dt * 0.05

        self.internal_state += state_flow
        other.internal_state -= state_flow

        # Clip values
        self.entropy = np.clip(self.entropy, 0.0, self.max_entropy)
        other.entropy = np.clip(other.entropy, 0.0, other.max_entropy)
        self.internal_state = np.clip(self.internal_state, 0.0, 1.0)
        other.internal_state = np.clip(other.internal_state, 0.0, 1.0)

    def apply_temperature_adjustment(self, factor: float):
        """Apply temperature adjustment from gardener"""
        self.temperature *= factor
        self.temperature = np.clip(self.temperature, 0.1, 3.0)


class MultiAgentEcosystem:
    """
    Multi-Agent Ecosystem with Resonance Coupling

    Agents interact via a coupling matrix (κ-matrix) and evolve their
    σ_Φ signatures over time. Gardener agents maintain homeostasis.
    """

    def __init__(
        self,
        n_agents: int = 8,
        field_size: float = 10.0,
        coupling_strength_base: float = 0.1,
        random_seed: Optional[int] = None,
    ):
        """
        Initialize multi-agent ecosystem

        Args:
            n_agents: Number of agents
            field_size: Size of resonance field (agents live in [0, field_size]²)
            coupling_strength_base: Base coupling strength
            random_seed: Random seed for reproducibility
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        self.n_agents = n_agents
        self.field_size = field_size
        self.coupling_strength_base = coupling_strength_base

        # Initialize agents with random positions and states
        self.agents = self._initialize_agents()

        # Initialize coupling matrix (symmetric, distance-based)
        self.coupling_matrix = self._initialize_coupling_matrix()

        # Timestep counter
        self.timestep = 0

        # History tracking
        self.history = {
            'sigma_phi': [],
            'entropy': [],
            'temperature': [],
            'alive_count': [],
            'mean_coupling': [],
        }

    def _initialize_agents(self) -> List[Agent]:
        """Initialize agents with random positions and states"""
        agents = []
        for i in range(self.n_agents):
            position = np.random.rand(2) * self.field_size
            # σ_Φ = H / H_max, target σ_Φ ≈ 0.0625, so H ≈ 0.25
            entropy = np.random.uniform(0.15, 0.35)  # Start varied around target
            temperature = np.random.uniform(0.8, 1.2)
            beta = np.random.choice([4.5, 7.4, 11.0])  # Mix of β-regimes

            agent = Agent(
                agent_id=f"Agent_{i:02d}",
                position=position,
                entropy=entropy,
                temperature=temperature,
                beta=beta,
            )
            agents.append(agent)

        return agents

    def _initialize_coupling_matrix(self) -> np.ndarray:
        """
        Initialize coupling matrix based on spatial distances

        κ_ij = κ_base × exp(-d_ij / λ)

        where d_ij is Euclidean distance and λ is coupling length scale
        """
        n = self.n_agents
        matrix = np.zeros((n, n))
        lambda_coupling = self.field_size * 0.3  # Coupling length scale

        for i in range(n):
            for j in range(i+1, n):
                distance = np.linalg.norm(self.agents[i].position - self.agents[j].position)
                coupling = self.coupling_strength_base * np.exp(-distance / lambda_coupling)

                matrix[i, j] = coupling
                matrix[j, i] = coupling  # Symmetric

        return matrix

    def step(self, dt: float = 0.1):
        """
        Advance ecosystem by one timestep

        Args:
            dt: Timestep size
        """
        # 1. Agents update their own entropy
        for agent in self.agents:
            agent.update_entropy(dt)

        # 2. Agents interact via coupling matrix
        for i in range(self.n_agents):
            for j in range(i+1, self.n_agents):
                coupling_strength = self.coupling_matrix[i, j]
                if coupling_strength > 0.01:  # Only interact if significantly coupled
                    self.agents[i].interact(self.agents[j], coupling_strength, dt)

        # 3. Record state
        self._record_state()

        # 4. Increment timestep
        self.timestep += 1

    def get_agent_states(self) -> Dict[str, Dict[str, float]]:
        """
        Get current states of all agents

        Returns:
            Dict mapping agent_id to state dict
        """
        states = {}
        for i, agent in enumerate(self.agents):
            # Calculate resonance quality (how well coupled to neighbors)
            neighbor_couplings = self.coupling_matrix[i, :]
            resonance_quality = float(np.mean(neighbor_couplings[neighbor_couplings > 0]))

            states[agent.agent_id] = {
                'sigma_phi': agent.sigma_phi,
                'entropy': agent.entropy,
                'temperature': agent.temperature,
                'kappa_total': float(np.sum(neighbor_couplings)),
                'resonance_quality': resonance_quality,
                'activation': agent.activation,
                'readiness': agent.readiness,
            }

        return states

    def get_agent_ids(self) -> List[str]:
        """Get ordered list of agent IDs"""
        return [agent.agent_id for agent in self.agents]

    def apply_cultivation(
        self,
        adjusted_coupling_matrix: np.ndarray,
        adjusted_temperatures: Dict[str, float]
    ):
        """
        Apply cultivation actions from gardener

        Args:
            adjusted_coupling_matrix: Modified coupling matrix
            adjusted_temperatures: Temperature adjustments per agent
        """
        # Update coupling matrix
        self.coupling_matrix = adjusted_coupling_matrix

        # Apply temperature adjustments
        for agent in self.agents:
            if agent.agent_id in adjusted_temperatures:
                factor = adjusted_temperatures[agent.agent_id]
                agent.apply_temperature_adjustment(factor)

    def _record_state(self):
        """Record current state for history"""
        sigma_phis = [agent.sigma_phi for agent in self.agents]
        entropies = [agent.entropy for agent in self.agents]
        temperatures = [agent.temperature for agent in self.agents]
        alive_count = sum(1 for agent in self.agents if is_alive(agent.sigma_phi))
        mean_coupling = float(np.mean(self.coupling_matrix[self.coupling_matrix > 0]))

        self.history['sigma_phi'].append(sigma_phis)
        self.history['entropy'].append(entropies)
        self.history['temperature'].append(temperatures)
        self.history['alive_count'].append(alive_count)
        self.history['mean_coupling'].append(mean_coupling)

    def get_statistics(self) -> Dict:
        """Get current ecosystem statistics"""
        sigma_phis = [agent.sigma_phi for agent in self.agents]
        alive_count = sum(1 for agent in self.agents if is_alive(agent.sigma_phi))

        return {
            'timestep': self.timestep,
            'n_agents': self.n_agents,
            'alive_count': alive_count,
            'alive_fraction': alive_count / self.n_agents,
            'mean_sigma_phi': float(np.mean(sigma_phis)),
            'std_sigma_phi': float(np.std(sigma_phis)),
            'min_sigma_phi': float(np.min(sigma_phis)),
            'max_sigma_phi': float(np.max(sigma_phis)),
            'mean_entropy': float(np.mean([a.entropy for a in self.agents])),
            'mean_temperature': float(np.mean([a.temperature for a in self.agents])),
            'mean_coupling': float(np.mean(self.coupling_matrix[self.coupling_matrix > 0])),
        }

    def get_agent_positions(self) -> np.ndarray:
        """Get agent positions as Nx2 array"""
        return np.array([agent.position for agent in self.agents])

    def get_coupling_matrix(self) -> np.ndarray:
        """Get current coupling matrix"""
        return self.coupling_matrix.copy()


def create_ecosystem(
    n_agents: int = 8,
    scenario: str = "balanced",
    random_seed: Optional[int] = None,
) -> MultiAgentEcosystem:
    """
    Factory function to create ecosystem with preset scenarios

    Args:
        n_agents: Number of agents
        scenario: Scenario type
            - "balanced": Mix of agents near equilibrium
            - "chaotic": High temperature, high entropy
            - "ordered": Low temperature, low entropy
            - "mixed": Mix of all types
        random_seed: Random seed

    Returns:
        Configured MultiAgentEcosystem
    """
    ecosystem = MultiAgentEcosystem(
        n_agents=n_agents,
        field_size=10.0,
        coupling_strength_base=0.1,
        random_seed=random_seed,
    )

    # Adjust initial conditions based on scenario
    # Note: σ_Φ = H / H_max, so for σ_Φ ≈ 0.0625 with H_max=4.0, need H ≈ 0.25
    if scenario == "chaotic":
        for agent in ecosystem.agents:
            agent.entropy = np.random.uniform(0.35, 0.50)  # σ_Φ ≈ 0.0875-0.125 (high)
            agent.temperature = np.random.uniform(1.5, 2.5)

    elif scenario == "ordered":
        for agent in ecosystem.agents:
            agent.entropy = np.random.uniform(0.10, 0.20)  # σ_Φ ≈ 0.025-0.05 (low)
            agent.temperature = np.random.uniform(0.3, 0.7)

    elif scenario == "mixed":
        for i, agent in enumerate(ecosystem.agents):
            if i % 3 == 0:
                agent.entropy = np.random.uniform(0.35, 0.45)  # Too high (chaos)
                agent.temperature = 2.0
            elif i % 3 == 1:
                agent.entropy = np.random.uniform(0.10, 0.18)  # Too low (ordered)
                agent.temperature = 0.5
            else:
                agent.entropy = np.random.uniform(0.22, 0.28)  # Near target
                agent.temperature = 1.0

    return ecosystem