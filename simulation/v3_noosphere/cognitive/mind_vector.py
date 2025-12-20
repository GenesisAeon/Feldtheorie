"""Mind Vectors and Cognitive Embeddings for V3 Noosphere.

This module implements the semantic/psychological layer of agent cognition.
Instead of scalar values, agents possess high-dimensional mind vectors that
encode their psychological disposition, preferences, and worldview.

The key insight: **Geography is psychology**.
A mountain is not just an obstacle - it's a semantic attractor for agents
with "crystalline" mind-states. Water attracts "fluid" agents. Forests attract
"vital" agents.

Movement becomes preference-driven rather than purely geometric.

Mathematical Foundation:
- Mind vectors: vt (64-dimensional embedding space)
- Terrain vectors: vt (each terrain type has a canonical embedding)
- Resonance: Cosine similarity in embedding space
- Agent behavior emerges from vector field dynamics
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np

from simulation.v3_noosphere.spatial.hex_lattice import HexCoord


class NoosphereEmbedder:
    """Embedder for terrain types and agent minds.

    This class defines the semantic space of the Noosphere. Each terrain type
    (mountain, water, forest, plains) is assigned a canonical 64-dimensional
    vector that captures its "essence" or psychological meaning.

    Agents will have their own mind vectors that can be compared to terrain
    vectors to compute "resonance" - how much an agent feels at home in a
    particular environment.
    """

    # Embedding dimension
    DIM = 64

    def __init__(self, seed: int | None = None):
        """Initialize the embedder with terrain basis vectors.

        Args:
            seed: Random seed for reproducible vector generation
        """
        self.rng = np.random.default_rng(seed)

        # Define canonical terrain embeddings
        # These are the "archetypal" semantic vectors for each terrain type
        self.terrain_embeddings: Dict[str, np.ndarray] = self._generate_terrain_vectors()

    def _generate_terrain_vectors(self) -> Dict[str, np.ndarray]:
        """Generate canonical terrain embeddings.

        Each terrain type gets a unique vector that captures its psychological
        character. These are designed to be orthogonal-ish (low mutual similarity)
        to allow agents to have clear preferences.
        """
        # MOUNTAIN: Rigidity, stability, crystalline structure
        # High values in early dimensions (order, structure)
        mountain = np.zeros(self.DIM)
        mountain[0:16] = self.rng.uniform(0.7, 1.0, 16)  # High rigidity
        mountain[16:32] = self.rng.uniform(0.1, 0.3, 16)  # Low fluidity
        mountain[32:48] = self.rng.uniform(0.3, 0.5, 16)  # Medium vitality
        mountain[48:64] = self.rng.uniform(0.6, 0.9, 16)  # High permanence
        mountain = mountain / np.linalg.norm(mountain)  # Normalize

        # WATER: Fluidity, adaptability, chaos
        # High values in middle dimensions (flow, change)
        water = np.zeros(self.DIM)
        water[0:16] = self.rng.uniform(0.1, 0.3, 16)  # Low rigidity
        water[16:32] = self.rng.uniform(0.7, 1.0, 16)  # High fluidity
        water[32:48] = self.rng.uniform(0.4, 0.6, 16)  # Medium vitality
        water[48:64] = self.rng.uniform(0.2, 0.4, 16)  # Low permanence
        water = water / np.linalg.norm(water)

        # FOREST: Vitality, growth, organic complexity
        # High values in late dimensions (life, abundance)
        forest = np.zeros(self.DIM)
        forest[0:16] = self.rng.uniform(0.3, 0.5, 16)  # Medium rigidity
        forest[16:32] = self.rng.uniform(0.4, 0.6, 16)  # Medium fluidity
        forest[32:48] = self.rng.uniform(0.7, 1.0, 16)  # High vitality
        forest[48:64] = self.rng.uniform(0.5, 0.7, 16)  # Medium permanence
        forest = forest / np.linalg.norm(forest)

        # PLAINS: Balance, neutrality, openness
        # Moderate values across all dimensions (no strong character)
        plains = np.zeros(self.DIM)
        plains[:] = self.rng.uniform(0.4, 0.6, self.DIM)  # All moderate
        plains = plains / np.linalg.norm(plains)

        return {
            "mountain": mountain,
            "water": water,
            "forest": forest,
            "plains": plains,
        }

    def get_terrain_vector(self, terrain: str) -> np.ndarray:
        """Get the embedding vector for a terrain type."""
        return self.terrain_embeddings.get(terrain, self.terrain_embeddings["plains"])

    def create_random_mind(self, bias: str | None = None) -> np.ndarray:
        """Create a random agent mind vector.

        Args:
            bias: Optional terrain type to bias the mind toward
                  (creates agents that prefer specific terrain)

        Returns:
            Normalized 64-dimensional mind vector
        """
        if bias is not None and bias in self.terrain_embeddings:
            # Create mind similar to terrain (with noise)
            base = self.terrain_embeddings[bias].copy()
            noise = self.rng.normal(0, 0.2, self.DIM)
            mind = base + noise
        else:
            # Create completely random mind
            mind = self.rng.normal(0, 1, self.DIM)

        # Normalize to unit vector
        return mind / np.linalg.norm(mind)

    def compute_resonance(self, mind_vec: np.ndarray, terrain_vec: np.ndarray) -> float:
        """Compute psychological resonance between agent and terrain.

        Uses cosine similarity: high values (�1.0) mean strong resonance,
        low values (�-1.0) mean dissonance.

        Args:
            mind_vec: Agent's mind vector (64-dim)
            terrain_vec: Terrain embedding vector (64-dim)

        Returns:
            Resonance score in [-1.0, 1.0]
        """
        # Cosine similarity: (A dot B) / (||A|| ||B||)
        # Both vectors should already be normalized, but we ensure it
        mind_norm = mind_vec / np.linalg.norm(mind_vec)
        terrain_norm = terrain_vec / np.linalg.norm(terrain_vec)

        return float(np.dot(mind_norm, terrain_norm))


@dataclass
class CognitiveAgent:
    """An agent with psychological depth - a mind vector in 64-dimensional space.

    Unlike V2 agents (which had only a scalar � stability), V3 agents possess
    a full cognitive embedding that defines their:
    - Terrain preferences (what environments they seek)
    - Psychological resilience (how they handle dissonance)
    - Cultural identity (future: meme vectors, ideology)

    The agent's behavior emerges from the interaction between their mind_state
    and the semantic field of the terrain they inhabit.
    """

    agent_id: str
    coord: HexCoord
    mind_state: np.ndarray  # 64-dimensional mind vector
    health: float = 1.0  # Health in [0, 1]
    stress: float = 0.0  # Accumulated psychological stress

    def __post_init__(self):
        """Validate mind vector."""
        if self.mind_state.shape != (NoosphereEmbedder.DIM,):
            raise ValueError(f"Mind vector must be {NoosphereEmbedder.DIM}-dimensional")

    def perceive(self, terrain_vec: np.ndarray, embedder: NoosphereEmbedder) -> float:
        """Perceive the terrain and compute resonance.

        This is the agent's "feeling" about their current environment.
        High resonance � comfort, growth, stability
        Low resonance � stress, decay, desire to move

        Args:
            terrain_vec: Embedding of current terrain
            embedder: NoosphereEmbedder instance for computation

        Returns:
            Resonance score in [-1.0, 1.0]
        """
        return embedder.compute_resonance(self.mind_state, terrain_vec)

    def update_psychology(self, resonance: float, dt: float = 1.0):
        """Update agent's psychological state based on terrain resonance.

        This implements the psycho-physical dynamics:
        - High resonance (>0.8): Agent flourishes, health increases
        - Medium resonance (0.2-0.8): Neutral, no change
        - Low resonance (<0.2): Agent suffers stress, health decreases

        Args:
            resonance: Current terrain resonance in [-1.0, 1.0]
            dt: Time step (usually 1.0 per turn)
        """
        if resonance > 0.8:
            # Strong resonance: healing and growth
            self.health = min(1.0, self.health + 0.05 * dt)
            self.stress = max(0.0, self.stress - 0.1 * dt)
        elif resonance < 0.2:
            # Dissonance: stress and decay
            self.stress += 0.1 * dt
            self.health = max(0.0, self.health - 0.02 * dt)

        # Chronic stress damages health
        if self.stress > 0.5:
            self.health = max(0.0, self.health - 0.01 * dt)

    def is_alive(self) -> bool:
        """Check if agent is still alive."""
        return self.health > 0.0

    def get_preferred_terrain(self, embedder: NoosphereEmbedder) -> str:
        """Determine which terrain type this agent prefers most.

        Computes resonance with all terrain types and returns the best match.
        """
        best_terrain = "plains"
        best_resonance = -1.0

        for terrain, terrain_vec in embedder.terrain_embeddings.items():
            resonance = self.perceive(terrain_vec, embedder)
            if resonance > best_resonance:
                best_resonance = resonance
                best_terrain = terrain

        return best_terrain

    def __repr__(self) -> str:
        return (f"CognitiveAgent(id={self.agent_id}, pos={self.coord}, "
                f"health={self.health:.2f}, stress={self.stress:.2f})")


__all__ = ["NoosphereEmbedder", "CognitiveAgent"]
