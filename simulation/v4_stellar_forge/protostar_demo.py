"""Protostar demonstration: gravitational collapse and pp-chain ignition."""

from __future__ import annotations

from typing import List

import numpy as np

from simulation.v3_noosphere.spatial.hex_lattice import HexCoord, HexLattice
from simulation.v4_stellar_forge.atomic_kernel import AtomAgent
from simulation.v4_stellar_forge.universal_forces import StellarForgeEngine


def spawn_molecular_cloud(
    lattice: HexLattice, *, count: int = 100, seed: int | None = None
) -> List[AtomAgent]:
    rng = np.random.default_rng(seed)
    atoms: List[AtomAgent] = []
    coords = list(lattice.cells.keys())
    far_coords = [c for c in coords if c.distance(HexCoord(0, 0)) >= lattice.radius // 2]

    for idx in range(count):
        coord = rng.choice(far_coords)
        drift = np.array([coord.q, coord.r], dtype=float)
        norm = np.linalg.norm(drift) or 1.0
        velocity = -drift / norm * 0.05 + rng.normal(0, 0.01, 2)
        atoms.append(
            AtomAgent.hydrogen(
                agent_id=f"H-{idx}", coord=coord, temperature=0.01, velocity=velocity
            )
        )
    return atoms


def run_protostar(steps: int = 80, seed: int | None = 42) -> List[AtomAgent]:
    lattice = HexLattice(radius=8, seed=seed)
    engine = StellarForgeEngine(lattice=lattice, gravitational_constant=0.6)
    atoms = spawn_molecular_cloud(lattice, seed=seed)

    ignition_reported = False
    for step in range(steps):
        atoms = engine.step(atoms)
        helium_count = sum(1 for a in atoms if a.charge == 2.0)
        photon_count = sum(1 for a in atoms if a.type == "PHOTON")
        if helium_count > 0 and not ignition_reported:
            print(f"[step {step}] ignition detected: {helium_count} helium nuclei formed")
            ignition_reported = True
        if photon_count > 0 and step % 10 == 0:
            print(f"[step {step}] photon flux: {photon_count} photons streaming outward")

    return atoms


if __name__ == "__main__":
    final_state = run_protostar()
    helium_total = sum(1 for a in final_state if a.charge == 2.0)
    photon_total = sum(1 for a in final_state if a.type == "PHOTON")
    print(f"Simulation complete: {helium_total} helium nuclei, {photon_total} photons emitted.")

