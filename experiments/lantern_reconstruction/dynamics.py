"""LR2 numerical core: batched, noise-free Kuramoto dynamics (plan sections 5.1, 10, 11).

    d theta_i / dt = omega_i + g * sum_j C_ij sin(theta_j - theta_i)

- pure functions on explicit arrays; NO random source at all (the original kernel draws from the
  global NumPy RNG even with zero noise -- this core never does);
- the coupling uses the DIFFERENCE theta_j - theta_i (axis order matters: a swapped axis would
  reverse the coupling; tested);
- explicit Euler step with the same wrap as the original, arctan2(sin, cos) into [-pi, pi];
- inputs are validated strictly: finite float arrays, exact shapes, C symmetric with zero diagonal
  and NON-NEGATIVE entries (negative couplings are rejected, never silently clipped), no bools;
- the inputs are never modified (C and omega are read-only inside; tested before/after);
- batches: theta has shape (B, N); omega (N,) or (B, N); only per-step (B, N, N) difference
  tensors for the given batch are formed -- callers keep batches small.
"""
from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple

import numpy as np

TWO_PI = 2.0 * np.pi


class DynamicsError(ValueError):
    pass


def wrap(x: np.ndarray) -> np.ndarray:
    """Circular wrap into [-pi, pi] exactly as the original kernel (arctan2(sin, cos))."""
    return np.arctan2(np.sin(x), np.cos(x))


def circular_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs(wrap(np.asarray(a) - np.asarray(b)))


def _float_array(x, what: str) -> np.ndarray:
    a = np.asarray(x)
    if a.dtype == bool or a.dtype.kind not in "fiu":
        raise DynamicsError(f"{what}: numeric array required (got dtype {a.dtype})")
    a = a.astype(np.float64, copy=False)
    if not np.all(np.isfinite(a)):
        raise DynamicsError(f"{what}: not finite")
    return a


def check_coupling(C) -> np.ndarray:
    C = _float_array(C, "C")
    if C.ndim != 2 or C.shape[0] != C.shape[1]:
        raise DynamicsError(f"C must be square, got shape {C.shape}")
    if not np.array_equal(C, C.T):
        raise DynamicsError("C must be exactly symmetric")
    if np.any(np.diag(C) != 0.0):
        raise DynamicsError("C must have a zero diagonal")
    if C.size and C.min() < 0.0:
        raise DynamicsError("negative couplings are rejected (never silently clipped)")
    return C


def check_inputs(theta, C, omega, g) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    C = check_coupling(C)
    n = C.shape[0]
    theta = _float_array(theta, "theta")
    if theta.ndim != 2 or theta.shape[1] != n:
        raise DynamicsError(f"theta must have shape (B, {n}), got {theta.shape}")
    omega = _float_array(omega, "omega")
    if omega.shape not in ((n,), theta.shape):
        raise DynamicsError(f"omega must have shape ({n},) or {theta.shape}, got {omega.shape}")
    if isinstance(g, (bool, np.bool_)) or not np.isfinite(float(g)) or float(g) < 0.0:
        raise DynamicsError("g must be a finite non-negative number")
    return theta, C, omega, float(g)


def drift(theta: np.ndarray, C: np.ndarray, omega: np.ndarray, g: float) -> np.ndarray:
    """omega_i + g * sum_j C_ij sin(theta_j - theta_i) for a batch theta (B, N). No validation (hot path)."""
    diff = theta[:, None, :] - theta[:, :, None]          # [b, i, j] = theta_j - theta_i
    return omega + g * np.einsum("ij,bij->bi", C, np.sin(diff))


def euler_step(theta: np.ndarray, C: np.ndarray, omega: np.ndarray, g: float, dt: float) -> np.ndarray:
    return wrap(theta + dt * drift(theta, C, omega, g))


def integrate(theta0, C, omega, g: float, dt: float, n_steps: int, record_steps: Optional[Sequence[int]] = None,
              *, wrap_states: bool = True) -> np.ndarray:
    """Euler integration of a batch. Returns states at `record_steps` (default: only the final step),
    shape (len(record_steps), B, N). `wrap_states=False` integrates the unwrapped continuous phases
    (for comparisons with an ODE solver); the drift itself is wrap-invariant."""
    theta, C, omega, g = check_inputs(theta0, C, omega, g)
    if not (isinstance(n_steps, (int, np.integer)) and not isinstance(n_steps, bool) and n_steps >= 0):
        raise DynamicsError("n_steps must be a non-negative integer")
    if not (np.isfinite(dt) and dt > 0):
        raise DynamicsError("dt must be finite and positive")
    rec = [int(n_steps)] if record_steps is None else [int(s) for s in record_steps]
    if any(s < 0 or s > n_steps for s in rec) or rec != sorted(rec):
        raise DynamicsError("record_steps must be sorted and within [0, n_steps]")
    C_ro, om_ro = C.copy(), omega.copy()
    C_ro.setflags(write=False)
    om_ro.setflags(write=False)
    x = theta.copy()
    out = []
    want = iter(rec)
    nxt = next(want, None)
    for step in range(n_steps + 1):
        while nxt is not None and nxt == step:
            out.append(x.copy())
            nxt = next(want, None)
        if step == n_steps:
            break
        x = x + dt * drift(x, C_ro, om_ro, g)
        if wrap_states:
            x = wrap(x)
    return np.stack(out)


def steps_for_times(times: Iterable[float], dt: float) -> list:
    """Integer step indices for model times; rejects times that are not multiples of dt."""
    out = []
    for t in times:
        s = round(float(t) / dt)
        if abs(s * dt - float(t)) > 1e-9 * max(1.0, abs(float(t))):
            raise DynamicsError(f"time {t} is not a multiple of dt={dt}")
        out.append(s)
    return out


def ode_rhs(C: np.ndarray, omega: np.ndarray, g: float):
    """Right-hand side for scipy.integrate.solve_ivp (single state, unwrapped)."""
    C = check_coupling(C)
    om = _float_array(omega, "omega")

    def f(_t, y):
        return drift(y[None, :], C, om, g)[0]
    return f
