"""Train A: 2D Ising model, temperature ramp, known ground truth.

Fixed seed (42), periodic boundary, checkerboard-vectorized Metropolis
dynamics. Ground truth T_c = 2/ln(1+sqrt(2)) (Onsager), so the
distance-to-instability d*(t) = |T(t) - T_c| / T_c is known exactly from
the ramp protocol -- no estimation needed for Train A's ground truth,
unlike Train B (see run_h1.py).

Per RIG_v0_SCOPING.md section 2: this is the only Train A component that
requires no download, fixed-seed, self-contained.
"""

from __future__ import annotations

import numpy as np

SEED = 42
L = 32  # lattice side length
T_C = 2.0 / np.log(1.0 + np.sqrt(2.0))  # Onsager, ~2.26919
T_START = 1.5
T_END = 3.5
# Raised from an initial 4000 after the first H1 run: the corrected
# e-folding tau estimator (see estimators.py) found tau ~ 830 sweeps near
# criticality (real critical slowing down), leaving too few of the
# spec's block_size=2*tau blocks (need >= 4) to compute I^macro at
# N_SWEEPS=4000. Raising N_SWEEPS is a self-contained simulation-length
# choice with no real-world data constraint (unlike Train B, see
# RESULTS.md) -- not a change to any frozen metric or estimator
# definition.
N_SWEEPS = 12000
SWEEPS_PER_TEMP_STEP = 1  # one sweep per ramp step -> N_SWEEPS ramp points


def _checkerboard_masks(l: int) -> tuple[np.ndarray, np.ndarray]:
    idx = np.indices((l, l)).sum(axis=0) % 2
    return idx == 0, idx == 1


def _metropolis_sweep(spins: np.ndarray, beta: float, rng: np.random.Generator) -> None:
    l = spins.shape[0]
    even_mask, odd_mask = _checkerboard_masks(l)
    for mask in (even_mask, odd_mask):
        neighbor_sum = (
            np.roll(spins, 1, axis=0)
            + np.roll(spins, -1, axis=0)
            + np.roll(spins, 1, axis=1)
            + np.roll(spins, -1, axis=1)
        )
        delta_e = 2.0 * spins * neighbor_sum
        accept_prob = np.exp(-beta * delta_e)
        rand = rng.random((l, l))
        flip = mask & ((delta_e <= 0) | (rand < accept_prob))
        spins[flip] *= -1


def simulate() -> dict[str, np.ndarray]:
    rng = np.random.default_rng(SEED)
    spins = rng.choice([-1, 1], size=(L, L)).astype(np.int8)

    temps = np.linspace(T_START, T_END, N_SWEEPS)
    magnetization = np.empty(N_SWEEPS)

    for i, temp in enumerate(temps):
        beta = 1.0 / temp
        _metropolis_sweep(spins, beta, rng)
        magnetization[i] = spins.mean()  # order parameter, per-spin magnetization

    d_star = np.abs(temps - T_C) / T_C

    return {
        "temps": temps,
        "magnetization": magnetization,
        "d_star": d_star,
        "T_C": np.array([T_C]),
        "L": np.array([L]),
        "seed": np.array([SEED]),
    }


if __name__ == "__main__":
    import json
    from pathlib import Path

    out_dir = Path(__file__).resolve().parents[1] / "data" / "train_a"
    out_dir.mkdir(parents=True, exist_ok=True)

    result = simulate()
    np.savez(
        out_dir / "ising_run.npz",
        temps=result["temps"],
        magnetization=result["magnetization"],
        d_star=result["d_star"],
    )
    meta = {
        "T_C_onsager": float(result["T_C"][0]),
        "L": int(result["L"][0]),
        "seed": int(result["seed"][0]),
        "T_START": T_START,
        "T_END": T_END,
        "N_SWEEPS": N_SWEEPS,
    }
    (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("Ising run complete.")
    print(f"T_c (Onsager) = {result['T_C'][0]:.5f}")
    print(f"magnetization range: [{result['magnetization'].min():.4f}, {result['magnetization'].max():.4f}]")
