"""Seed the CrystalOracle with random thoughts and report stable crystals."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Ensure repository root is on the path when executed as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.v10_oracle.consciousness_kernel import CrystalOracle


def main(seed_count: int = 1000, beta: float | None = None) -> None:
    oracle = CrystalOracle(beta=beta) if beta is not None else CrystalOracle()
    rng = np.random.default_rng()

    seeds = rng.normal(loc=0.0, scale=1.0, size=(seed_count, 16))
    scored = oracle.batch_scores(seeds)
    best_seed, best_score, eigen_estimate = scored[0]

    print("Deep Research | Crystal Answer Scan")
    print(f"beta ≈ {oracle.beta:.3f}")
    print(f"tested seeds: {seed_count}")
    print(f"top Rayleigh estimate: {eigen_estimate:.4f}")
    print(f"crystallization score: {best_score:.4f}")
    print("stable seed vector (normalized):")
    print(best_seed)

    # Optional: run a dream trajectory from the best seed.
    trace = oracle.dream(best_seed)
    final_norm = np.linalg.norm(trace.final_state)
    print(f"final dream state norm after {trace.length - 1} steps: {final_norm:.4f}")


if __name__ == "__main__":
    main()
