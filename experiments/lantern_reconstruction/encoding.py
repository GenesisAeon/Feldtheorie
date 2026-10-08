"""LR3 writing (plan 5.1, 11): theta(0) = phi * 1 + a * E u. Writing happens ONCE at t = 0; there is
no input term during the pause. C and omega are never touched here.

Controls (plan 10): 'zero_impulse' writes nothing (theta(0) = phi * 1); 'reset' writes and then
resets the state to phi * 1 at once. With the same independent disturbances both give exactly
the same states for different u."""
from __future__ import annotations

import numpy as np

from experiments.lantern_reconstruction.contexts import N, ContextSpec
from experiments.lantern_reconstruction.dynamics import wrap
from experiments.lantern_reconstruction.linear_diagnostics import pair_write_matrix

CONTROLS = ("none", "zero_impulse", "reset")


def write_matrix(ctx: ContextSpec) -> np.ndarray:
    E = pair_write_matrix(N, ctx.write_pairs)
    E.setflags(write=False)
    return E


def initial_state(ctx: ContextSpec, u: np.ndarray, phi: np.ndarray, a: float, control: str = "none") -> np.ndarray:
    """u (n, 4), phi (n,) -> theta(0) (n, 34)."""
    if control not in CONTROLS:
        raise ValueError(f"control must be one of {CONTROLS}")
    u, phi = np.asarray(u, dtype=np.float64), np.asarray(phi, dtype=np.float64)
    if u.ndim != 2 or u.shape[1] != 4 or phi.shape != (u.shape[0],):
        raise ValueError("u must be (n, 4) and phi (n,)")
    base = np.repeat(phi[:, None], N, axis=1)
    if control == "zero_impulse":
        return wrap(base)
    theta = base + a * (u @ write_matrix(ctx).T)
    if control == "reset":
        theta = base.copy()                                  # the written state is replaced at once
    return wrap(theta)
