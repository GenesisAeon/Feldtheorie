"""Spatial topology layer for V3 Noosphere.

This module provides geometric substrates for agent simulations:
- Hex lattices (crystalline grids)
- Graph networks (social/trade graphs)
- Proximity engines (local interaction calculations)
"""

from simulation.v3_noosphere.spatial.hex_lattice import HexCoord, HexCell, HexLattice

__all__ = [
    "HexCoord",
    "HexCell",
    "HexLattice",
]
