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
from experiments.lantern_reconstruction.contexts import N, ContextSpec, check_context, fingerprint
from experiments.lantern_reconstruction.encoding import initial_state

CONDITIONS = ("lantern", "uncoupled", "uniform_total", "strength_surrogate")


@dataclass(frozen=True)
class EpisodeBatch:
    study_id: int
    context_id: int
    context_fingerprint: str
    config_sha256: str
    split: str
    episode_ids: tuple
    u: np.ndarray          # (n, 4)
    phi: np.ndarray        # (n,)
    eps: np.ndarray        # (n, 7, 34): per episode, readout time and node


def _episode_ids(episode_ids) -> tuple:
    """Materialised ONCE; true non-negative integers, no duplicates, not empty (review R1)."""
    ids = tuple(episode_ids)
    if not ids:
        raise ValueError("a batch needs at least one episode")
    ids = tuple(streams.check_index(e, "episode id") for e in ids)
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate episode ids in a batch")
    return ids


def make_batch(ctx: ContextSpec, split: str, episode_ids) -> EpisodeBatch:
    check_context(ctx)
    d = streams.defaults()
    sigma, T = d["measurement"]["sigma_rad"], len(d["time_grid"])
    if split not in ("train", "val", "test"):
        raise ValueError("split must be train, val or test")
    ids = _episode_ids(episode_ids)
    u, phi, eps = [], [], []
    for e in ids:
        u.append(streams.generator(ctx.study_id, ctx.context_id, split, "targets", e).uniform(-1.0, 1.0, 4))
        phi.append(streams.generator(ctx.study_id, ctx.context_id, split, "global_phase", e).uniform(-np.pi, np.pi))
        eps.append(streams.generator(ctx.study_id, ctx.context_id, split, "measurement", e).normal(0.0, sigma, (T, N)))
    arr = [np.array(x, dtype=np.float64) for x in (u, phi, eps)]
    for a in arr:
        a.setflags(write=False)
    return EpisodeBatch(ctx.study_id, ctx.context_id, fingerprint(ctx), streams.config_sha256(), split, ids, *arr)


def check_batch(ctx: ContextSpec, batch: EpisodeBatch) -> int:
    """The batch must belong to THIS study, context and configuration, with consistent shapes (review R2)."""
    check_context(ctx)
    if (batch.study_id, batch.context_id) != (ctx.study_id, ctx.context_id):
        raise ValueError(f"batch belongs to study {batch.study_id} / context {batch.context_id}, not {ctx.study_id} / {ctx.context_id}")
    if batch.context_fingerprint != fingerprint(ctx):
        raise ValueError("batch was made for a different context definition (fingerprint mismatch)")
    if batch.config_sha256 != streams.config_sha256():
        raise ValueError("batch was made under a different study configuration")
    if batch.split not in ("train", "val", "test"):
        raise ValueError("invalid split")
    n = len(_episode_ids(batch.episode_ids))
    T = len(streams.defaults()["time_grid"])
    for name, arr, shape in (("u", batch.u, (n, 4)), ("phi", batch.phi, (n,)), ("eps", batch.eps, (n, T, N))):
        a = np.asarray(arr)
        if a.shape != shape or a.dtype != np.float64 or not np.all(np.isfinite(a)):
            raise ValueError(f"batch.{name} must be finite float64 with shape {shape}")
    return n


def coupling_matrices_with_report(C_lantern: np.ndarray, ctx: ContextSpec, proposals: Optional[int] = None):
    """The four condition matrices plus the surrogate's invariant report bound to context, stream and
    proposal count (review: the report must be kept for the artifact path). proposals=None means the
    protocol default; any other value must be a positive integer (0 is NOT silently the default)."""
    check_context(ctx)
    n_prop = streams.defaults()["strength_surrogate"]["proposals"] if proposals is None else proposals
    key = streams.key(ctx.study_id, ctx.context_id, "context", "surrogate")
    S, rep = surrogates.strength_surrogate(C_lantern, streams.generator(ctx.study_id, ctx.context_id, "context", "surrogate"), n_prop)
    mats = {"lantern": np.array(C_lantern), "uncoupled": surrogates.uncoupled(C_lantern),
            "uniform_total": surrogates.uniform_total(C_lantern), "strength_surrogate": S}
    return mats, {**rep, "study_id": ctx.study_id, "context_id": ctx.context_id, "context_fingerprint": fingerprint(ctx),
                  "stream_key": list(key), "config_sha256": streams.config_sha256()}


def coupling_matrices(C_lantern: np.ndarray, ctx: ContextSpec, proposals: Optional[int] = None) -> Dict[str, np.ndarray]:
    return coupling_matrices_with_report(C_lantern, ctx, proposals)[0]


def simulate(ctx: ContextSpec, batch: EpisodeBatch, C: np.ndarray, g: float, control: str = "none", chunk: int = 256) -> np.ndarray:
    """States at the 7 grid times, (n, 7, 34); chunked (results independent of the chunk size).
    Everything is validated BEFORE any allocation or dynamics (review R2, R3)."""
    if isinstance(chunk, (bool, np.bool_)) or not isinstance(chunk, (int, np.integer)) or chunk < 1:
        raise ValueError(f"chunk must be a positive integer (got {chunk!r})")
    check_batch(ctx, batch)
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
