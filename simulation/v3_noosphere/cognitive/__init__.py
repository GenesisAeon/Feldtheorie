"""Cognitive Layer for V3 Noosphere.

This module implements the mental/semantic layer of the Noosphere - the realm
of ideas, perceptions, and agent psychology. While the spatial layer (hex_lattice)
provides the geometric substrate, the cognitive layer provides the semantic meaning.

Agents no longer have a single stability scalar σ, but instead possess a 64-dimensional
mind vector that encodes their "personality" - their preferences, tendencies, and
resonances with different terrain types.

The world becomes psychologically textured: forests, mountains, and waters are no
longer just movement costs, but **semantic fields** that attract or repel agents
based on vector similarity (cosine distance in embedding space).

This is the transition from mechanical physics to **psycho-physics**.
"""

from simulation.v3_noosphere.cognitive.mind_vector import (
    CognitiveAgent,
    NoosphereEmbedder,
)

__all__ = ["NoosphereEmbedder", "CognitiveAgent"]
