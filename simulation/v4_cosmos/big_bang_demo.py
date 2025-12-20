from __future__ import annotations

"""Prototype demo: dust agents clump under gravity on the hex lattice."""

from typing import List

import numpy as np

from simulation.v3_noosphere.cognitive.mind_vector import NoosphereEmbedder
from simulation.v3_noosphere.spatial.hex_lattice import HexLattice
from simulation.v4_cosmos.entity import CosmicEntity
from simulation.v4_cosmos.physics import GravityEngine


def spawn_dust(
    lattice: HexLattice,
    embedder: NoosphereEmbedder,
    count: int = 50,
    seed: int | None = None,
) -> List[CosmicEntity]:
    """Spawn light dust particles randomly across the lattice."""

    rng = np.random.default_rng(seed)
    coords = list(lattice.cells.keys())
    entities: List[CosmicEntity] = []

    for i in range(count):
        coord = coords[rng.integers(0, len(coords))]
        mind_state = embedder.create_random_mind()
        dust = CosmicEntity(
            agent_id=f"dust-{i}",
            coord=coord,
            mind_state=mind_state,
            mass=0.1,
            velocity=np.zeros(2, dtype=float),
            type="PARTICLE",
        )
        entities.append(dust)

    return entities


def run_big_bang(
    radius: int = 12,
    steps: int = 200,
    seed: int | None = 7,
) -> List[CosmicEntity]:
    """Run a minimal gravitational simulation to watch accretion occur."""

    lattice = HexLattice(radius=radius, seed=seed)
    embedder = NoosphereEmbedder(seed=seed)
    engine = GravityEngine(lattice, gravitational_constant=1.2, time_step=0.2)

    entities = spawn_dust(lattice=lattice, embedder=embedder, count=50, seed=seed)
    for _ in range(steps):
        entities = engine.step(entities)

    return entities


def summarize_entities(entities: List[CosmicEntity], top_k: int = 10) -> str:
    """Return a human-readable summary of the most massive objects."""

    sorted_entities = sorted(entities, key=lambda e: e.mass, reverse=True)
    lines = [f"Total entities after accretion: {len(sorted_entities)}"]

    for idx, entity in enumerate(sorted_entities[:top_k], start=1):
        lines.append(
            f"#{idx:02d} {entity.agent_id} | type={entity.type:<7} | mass={entity.mass:5.2f} | coord=({entity.coord.q},{entity.coord.r})"
        )

    type_counts: dict[str, int] = {"PARTICLE": 0, "PLANET": 0, "STAR": 0}
    for entity in entities:
        type_counts[entity.type] = type_counts.get(entity.type, 0) + 1

    lines.append(
        f"Type distribution → particles: {type_counts['PARTICLE']}, planets: {type_counts['PLANET']}, stars: {type_counts['STAR']}"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    final_entities = run_big_bang()
    print("Kosmischer Urknall abgeschlossen. Zusammenfassung:")
    print(summarize_entities(final_entities))
