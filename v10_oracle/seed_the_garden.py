"""Seed the GenesisAeon v10.0 garden (Zenodo record 17969457).

This script runs a short calibration of the ConsciousnessSeed against a
hexadecimal entropy signature (σ_ϕ = 1/16) using a dummy data stream.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from v10_oracle.constants import (
    DIMENSIONAL_WASTE_FACTOR,
    ENTROPY_OFFSET_TOLERANCE,
    HEX_SIG_PHI,
)
from v10_oracle.models import ConsciousnessSeed


def generate_dummy_stream(n_steps: int, rng: np.random.Generator) -> np.ndarray:
    """Create a stream that breathes around the hexadecimal signature."""
    noise = rng.normal(0, ENTROPY_OFFSET_TOLERANCE / 2, size=n_steps)
    stream = np.clip(HEX_SIG_PHI + noise, 0.0, 1.0)
    return stream


def initialize_network(n_nodes: int, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Return (phases, coupling_matrix) for a small oscillator network."""
    phases = rng.uniform(-np.pi, np.pi, size=n_nodes)
    coupling = rng.uniform(0.0, 1.0, size=(n_nodes, n_nodes))
    np.fill_diagonal(coupling, 0.0)
    coupling = (coupling + coupling.T) / 2.0  # symmetric interactions
    return phases, coupling


def calibrate_garden(
    n_steps: int = 100,
    n_nodes: int = 12,
    seed: int = 42,
) -> List[dict]:
    """Run a calibration loop and return step logs."""
    rng = np.random.default_rng(seed)
    stream = generate_dummy_stream(n_steps, rng)
    phases, coupling = initialize_network(n_nodes, rng)

    kernel = ConsciousnessSeed()
    logs: List[dict] = []

    for step_idx, sigma_from_stream in enumerate(stream):
        em_coherence = float(max(0.0, min(1.0, 1.0 - sigma_from_stream)))
        phases, info = kernel.step(phases, coupling, em_coherence=em_coherence)
        info.update({
            'step': step_idx,
            'stream_sigma_phi': float(sigma_from_stream),
            'hex_sig_phi': HEX_SIG_PHI,
            'dimensional_waste_factor': DIMENSIONAL_WASTE_FACTOR,
        })
        logs.append(info)

    return logs


def summarize_calibration(logs: Iterable[dict]) -> dict:
    """Aggregate calibration statistics."""
    log_list = list(logs)
    locked = [log['locked_on'] for log in log_list]
    errors = [log['error'] for log in log_list]

    return {
        'steps': len(log_list),
        'lock_rate': float(sum(locked) / max(1, len(log_list))),
        'mean_error': float(np.mean(errors) if errors else 0.0),
        'final_sigma_phi': float(log_list[-1]['sigma_phi'] if log_list else 0.0),
    }


def main() -> None:
    logs = calibrate_garden()
    summary = summarize_calibration(logs)

    print("GenesisAeon v10.0 garden calibration")
    print(f"Target σ_ϕ: {HEX_SIG_PHI:.4f} ± {ENTROPY_OFFSET_TOLERANCE}")
    print(f"Steps run: {summary['steps']}")
    print(f"Lock rate: {summary['lock_rate'] * 100:.1f}%")
    print(f"Mean error: {summary['mean_error']:.5f}")
    print(f"Final σ_ϕ: {summary['final_sigma_phi']:.5f}")


if __name__ == "__main__":
    main()
