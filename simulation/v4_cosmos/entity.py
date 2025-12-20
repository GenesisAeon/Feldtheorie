from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from simulation.v3_noosphere.cognitive.mind_vector import CognitiveAgent
from simulation.v3_noosphere.spatial.hex_lattice import HexCoord

COSMIC_TYPES = {"PARTICLE", "PLANET", "STAR", "PHOTON"}


@dataclass
class CosmicEntity(CognitiveAgent):
    """A cosmological agent that represents matter on the hex lattice.

    The mind_state vector now encodes physical resonance properties (charge,
    spin, heat). Mass and velocity determine how the entity curves and
    traverses the lattice.
    """

    mass: float = 1.0
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=float))
    type: str = "PARTICLE"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.type == "PHOTON":
            if self.mass != 0:
                raise ValueError("Photons must be massless")
        elif self.mass <= 0:
            raise ValueError("CosmicEntity mass must be positive")

        if self.velocity.shape != (2,):
            raise ValueError("Velocity must be a 2D axial vector [dq, dr]")

        if self.type not in COSMIC_TYPES:
            raise ValueError(f"type must be one of {sorted(COSMIC_TYPES)}")

    def set_coord(self, coord: HexCoord) -> None:
        """Update the entity's lattice coordinate."""

        self.coord = coord

    def update_classification(self, planet_threshold: float = 5.0, star_threshold: float = 15.0) -> None:
        """Update the entity type based on its mass.

        Args:
            planet_threshold: Mass at which particles become planets.
            star_threshold: Mass at which planets ignite into stars.
        """

        if self.type == "PHOTON":
            return

        if self.mass >= star_threshold:
            self.type = "STAR"
        elif self.mass >= planet_threshold:
            self.type = "PLANET"
        else:
            self.type = "PARTICLE"
