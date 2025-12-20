"""V3 Noosphere: From Genesis to Civilization.

The V3 simulation layer marks the transition from biological evolution (V2)
to sociological emergence — from individual agents to collective intelligence,
from organisms to civilizations.

Modules:
- spatial: Hex grids, graph networks, spatial topologies
- cognitive: Vector embeddings, semantic memory, cultural diffusion
- temporal: Epoch management, historical records, technological evolution
"""

__version__ = "3.0.0"
__codename__ = "The Great Transition"

from simulation.v3_noosphere.spatial.hex_lattice import HexCoord, HexCell, HexLattice

__all__ = [
    "HexCoord",
    "HexCell",
    "HexLattice",
]
