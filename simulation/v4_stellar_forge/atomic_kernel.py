"""Atomic kernel for V4 stellar forge.

This module defines atomic agents as physically grounded entities whose mind
vectors encode basic quantum numbers. The presets allow quick construction of
hydrogen, helium, and photon agents that participate in nucleosynthesis on the
hex lattice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from simulation.v3_noosphere.cognitive.mind_vector import NoosphereEmbedder
from simulation.v3_noosphere.spatial.hex_lattice import HexCoord
from simulation.v4_cosmos.entity import CosmicEntity

HYDROGEN_MASS = 1.007  # AMU
HELIUM_MASS = 4.0026  # AMU
PHOTON_SPEED = 1.0


def _encode_state(mass: float, charge: float, temperature: float) -> np.ndarray:
    """Create a 64-dim mind vector with quantum numbers in the first slots."""

    vec = np.zeros(NoosphereEmbedder.DIM, dtype=float)
    vec[0] = mass
    vec[1] = charge
    vec[2] = temperature
    return vec


@dataclass
class AtomAgent(CosmicEntity):
    """Atomic agent representing a nucleus (or photon) on the lattice."""

    charge: float = 0.0
    temperature: float = 0.0

    def __post_init__(self) -> None:
        # Keep the cognitive embedding consistent with physical parameters.
        self.mind_state = self.mind_state.copy()
        self.mind_state[0] = self.mass
        self.mind_state[1] = self.charge
        self.mind_state[2] = self.temperature
        super().__post_init__()

    @classmethod
    def from_quantum(
        cls,
        agent_id: str,
        coord: HexCoord,
        *,
        mass: float,
        charge: float,
        temperature: float = 0.0,
        velocity: Iterable[float] | None = None,
        entity_type: str = "PARTICLE",
    ) -> "AtomAgent":
        """Construct an atom with a mind vector matching quantum numbers."""

        velocity_vec = (
            np.array(list(velocity), dtype=float)
            if velocity is not None
            else np.zeros(2, dtype=float)
        )
        mind_state = _encode_state(mass, charge, temperature)
        return cls(
            agent_id=agent_id,
            coord=coord,
            mind_state=mind_state,
            mass=mass,
            charge=charge,
            temperature=temperature,
            velocity=velocity_vec,
            type=entity_type,
        )

    @classmethod
    def hydrogen(
        cls,
        agent_id: str,
        coord: HexCoord,
        temperature: float = 0.0,
        velocity: Iterable[float] | None = None,
    ) -> "AtomAgent":
        """Preset for a hydrogen atom (proton + electron)."""

        return cls.from_quantum(
            agent_id,
            coord,
            mass=HYDROGEN_MASS,
            charge=+1.0,
            temperature=temperature,
            velocity=velocity,
        )

    @classmethod
    def helium(
        cls,
        agent_id: str,
        coord: HexCoord,
        temperature: float = 0.0,
        velocity: Iterable[float] | None = None,
    ) -> "AtomAgent":
        """Preset for a helium nucleus."""

        return cls.from_quantum(
            agent_id,
            coord,
            mass=HELIUM_MASS,
            charge=+2.0,
            temperature=temperature,
            velocity=velocity,
        )

    @classmethod
    def photon(
        cls,
        agent_id: str,
        coord: HexCoord,
        direction: Iterable[float] | None = None,
    ) -> "AtomAgent":
        """Preset for a photon (massless, speed = 1 hex per tick)."""

        direction_vec = (
            np.array(list(direction), dtype=float)
            if direction is not None
            else np.array([1.0, 0.0], dtype=float)
        )
        norm = np.linalg.norm(direction_vec)
        if norm == 0:
            direction_vec = np.array([1.0, 0.0], dtype=float)
        else:
            direction_vec = direction_vec / norm

        return cls.from_quantum(
            agent_id,
            coord,
            mass=0.0,
            charge=0.0,
            temperature=0.0,
            velocity=direction_vec * PHOTON_SPEED,
            entity_type="PHOTON",
        )

