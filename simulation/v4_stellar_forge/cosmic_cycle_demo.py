"""Demo showing stellar collapse into a black hole and Hawking evaporation."""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from simulation.v4_stellar_forge.physics_engine import (
    AtomAgent,
    ElementTypes,
    accretion_step,
    fusion_step,
    gravity_step,
    hawking_process,
)


def _initialize_ancient_star(seed: int | None = None) -> List[AtomAgent]:
    rng = np.random.default_rng(seed)
    particles: List[AtomAgent] = []

    for _ in range(36):
        position = rng.normal(0.0, 0.7, size=2)
        velocity = rng.normal(0.0, 0.02, size=2)
        particles.append(
            AtomAgent(
                position=position,
                velocity=velocity,
                mass=4.0,
                element=ElementTypes.HELIUM,
            )
        )

    for _ in range(18):
        position = rng.normal(0.0, 0.6, size=2)
        velocity = rng.normal(0.0, 0.02, size=2)
        particles.append(
            AtomAgent(
                position=position,
                velocity=velocity,
                mass=12.0,
                element=ElementTypes.CARBON,
            )
        )

    for _ in range(8):
        position = rng.normal(0.0, 0.25, size=2)
        velocity = rng.normal(0.0, 0.01, size=2)
        particles.append(
            AtomAgent(
                position=position,
                velocity=velocity,
                mass=56.0,
                element=ElementTypes.IRON,
            )
        )

    return particles


def _summarize(particles: List[AtomAgent]) -> Dict[str, int]:
    summary: Dict[str, int] = {}
    for p in particles:
        summary[p.element.value] = summary.get(p.element.value, 0) + 1
    return summary


def run_cosmic_cycle(steps: int = 150, seed: int | None = 7) -> List[AtomAgent]:
    particles = _initialize_ancient_star(seed=seed)
    print("Initialized ancient star core with He/C shell and iron heart.")

    for step in range(steps):
        gravity_step(particles)
        particles = fusion_step(particles)
        particles = accretion_step(particles)
        particles = hawking_process(particles)

        if step % 10 == 0:
            summary = _summarize(particles)
            print(f"[step {step}] {summary}")

    return particles


if __name__ == "__main__":
    final_state = run_cosmic_cycle()
    final_summary = _summarize(final_state)
    print(f"Final state: {final_summary}")
