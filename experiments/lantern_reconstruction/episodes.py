"""LR3 episodes (plan sections 6, 7, 11, 13): per (context, split) the targets u, global phases phi
and measurement errors eps come from one stream per episode and role; the trajectory per
(context, split, condition, control) is computed ONCE with RK4 (AE-01) and read at the 7 grid
times. All conditions share u, phi and eps; train/val/test use different split IDs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from experiments.lantern_reconstruction import dynamics as dyn
from experiments.lantern_reconstruction import streams, surrogates
from experiments.lantern_reconstruction.contexts import N, ContextSpec
from experiments.lantern_reconstruction.encoding import initial_state

CONDITIONS = ("lantern", "uncoupled", "uniform_total", "strength_surrogate")


@dataclass(frozen=True)
class EpisodeBatch:
    context_id: int
    split: str
    episode_ids: tuple
    u: np.ndarray          # (n, 4)
    phi: np.ndarray        # (n,)
    eps: np.ndarray        # (n, 7, 34): per episode, readout time and node


def make_batch(ctx: ContextSpec, split: str, episode_ids) -> EpisodeBatch:
    d = streams.defaults()
    sigma, T = d["measurement"]["sigma_rad"], len(d["time_grid"])
    if split not in ("train", "val", "test"):
        raise ValueError("split must be train, val or test")
    u, phi, eps = [], [], []
    for e in episode_ids:
        u.append(streams.generator(ctx.study_id, ctx.context_id, split, "targets", e).uniform(-1.0, 1.0, 4))
        phi.append(streams.generator(ctx.study_id, ctx.context_id, split, "global_phase", e).uniform(-np.pi, np.pi))
        eps.append(streams.generator(ctx.study_id, ctx.context_id, split, "measurement", e).normal(0.0, sigma, (T, N)))
    arr = [np.array(x, dtype=np.float64) for x in (u, phi, eps)]
    for a in arr:
        a.setflags(write=False)
    return EpisodeBatch(ctx.context_id, split, tuple(int(e) for e in episode_ids), *arr)


def coupling_matrices(C_lantern: np.ndarray, ctx: ContextSpec, proposals: Optional[int] = None) -> Dict[str, np.ndarray]:
    d = streams.defaults()
    rng = streams.generator(ctx.study_id, ctx.context_id, "context", "surrogate")
    S, _ = surrogates.strength_surrogate(C_lantern, rng, proposals or d["strength_surrogate"]["proposals"])
    return {"lantern": np.array(C_lantern), "uncoupled": surrogates.uncoupled(C_lantern),
            "uniform_total": surrogates.uniform_total(C_lantern), "strength_surrogate": S}


def simulate(ctx: ContextSpec, batch: EpisodeBatch, C: np.ndarray, g: float, control: str = "none", chunk: int = 256) -> np.ndarray:
    """States at the 7 grid times, (n, 7, 34); chunked (results independent of the chunk size)."""
    d = streams.defaults()
    if d["integration"]["method"] != "rk4":
        raise ValueError("the study integrates with RK4 (plan change AE-01)")
    dt = d["integration"]["dt"]
    steps = dyn.steps_for_times(d["time_grid"], dt)
    theta0 = initial_state(ctx, batch.u, batch.phi, d["content"]["impulse_rad"], control)
    out = np.empty((theta0.shape[0], len(steps), N))
    for s in range(0, theta0.shape[0], chunk):
        out[s:s + chunk] = np.transpose(dyn.integrate_rk4(theta0[s:s + chunk], C, ctx.omega_array(), g, dt, steps[-1], steps), (1, 0, 2))
    return out
