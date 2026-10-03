"""M1: episode operator and reference kernels (ROADMAP.md, IMPLEMENTIERUNGSPLAN.md §3-§4).

Model (one step, time index k = model steps, dimensionless activities):

    x_(k+1) = (1 - ell) x_k + ell * f(A x_k + B u_k),   f = tanh (main) or identity (linear ablation)

This is the SAME mathematical step as SCF ``simulate_trial``, but unlike
that function (which always starts from x = 0 and holds u constant), the
operator here takes an explicit initial state and an arbitrary input
sequence u_0, u_1, ... . SCF's function is not reinterpreted; it is used
as a parity reference in the tests (constant u, x0 = 0).

Episode convention (pulse -> pause -> recall):
    u_0 = e_s (one pulse step, class s in {0, 1}), u_1 .. u_d = 0;
    the readout is the state x_(d+1), i.e. after d + 1 steps.
    d = 0 reads directly after the pulse.

Interfaces (plan §3): reset(initial_state), step(u), snapshot(),
restore(snapshot), observe(H). The snapshot holds every dynamic
variable (x, step counter) and the weights A, B and parameters; the
operator itself draws no random numbers (observation noise lives in M2).
Weights are never changed here -- adaptation is a separate, explicit
training step (M3).
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, Optional, Sequence

import numpy as np

NONLINEARITIES = ("tanh", "identity")


class MemoryLabError(ValueError):
    """Input outside the declared scope of the experiment."""


def is_drive_c(path) -> bool:
    """True if the path names drive C: -- checked on the RAW spelling with Windows
    path rules, so that the guard also holds on POSIX (where Path("C:/x").drive
    is empty and "C:/x" would become a relative folder)."""
    from pathlib import Path, PureWindowsPath

    raw = str(path)
    if PureWindowsPath(raw).drive.upper().startswith("C"):
        return True
    return Path(raw).resolve().drive.upper().startswith("C")


@dataclass
class NetworkSpec:
    """Frozen description of one network condition."""

    A: np.ndarray
    B: np.ndarray
    ell: float
    nonlinearity: str = "tanh"
    name: str = "network"
    module_of: Optional[Sequence[int]] = None
    mask: Optional[np.ndarray] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.A = np.array(self.A, dtype=float)
        self.B = np.array(self.B, dtype=float)
        N = self.A.shape[0]
        if self.A.shape != (N, N) or self.B.ndim != 2 or self.B.shape[0] != N:
            raise MemoryLabError(f"A must be N x N and B N x m; got {self.A.shape}, {self.B.shape}")
        if not (np.all(np.isfinite(self.A)) and np.all(np.isfinite(self.B))):
            raise MemoryLabError("A and B must be finite")
        if not (0 < self.ell <= 1):
            raise MemoryLabError("0 < ell <= 1 required")
        if self.nonlinearity not in NONLINEARITIES:
            raise MemoryLabError(f"nonlinearity must be one of {NONLINEARITIES}")

    @property
    def N(self) -> int:
        return self.A.shape[0]

    @property
    def n_inputs(self) -> int:
        return self.B.shape[1]


class EpisodeOperator:
    """Stateful operator for one network; deterministic, no randomness."""

    def __init__(self, spec: NetworkSpec):
        self.spec = spec
        self._f = np.tanh if spec.nonlinearity == "tanh" else (lambda z: z)
        self.x = np.zeros(spec.N)
        self.k = 0

    def reset(self, initial_state: Optional[Sequence[float]] = None) -> np.ndarray:
        x0 = np.zeros(self.spec.N) if initial_state is None else np.array(initial_state, dtype=float)
        if x0.shape != (self.spec.N,) or not np.all(np.isfinite(x0)):
            raise MemoryLabError("initial state must be a finite vector of length N")
        self.x = x0.copy()
        self.k = 0
        return self.x.copy()

    def step(self, u: Sequence[float]) -> np.ndarray:
        u = np.array(u, dtype=float)
        if u.shape != (self.spec.n_inputs,) or not np.all(np.isfinite(u)):
            raise MemoryLabError(f"input must be a finite vector of length {self.spec.n_inputs}")
        s = self.spec
        self.x = (1 - s.ell) * self.x + s.ell * self._f(s.A @ self.x + s.B @ u)
        self.k += 1
        return self.x.copy()

    def run(self, inputs: Sequence[Sequence[float]]) -> np.ndarray:
        """Apply the inputs in order from the CURRENT state; returns the
        trajectory including the starting state, shape (len(inputs)+1, N)."""
        traj = [self.x.copy()]
        for u in inputs:
            traj.append(self.step(u))
        return np.array(traj)

    def snapshot(self) -> Dict[str, Any]:
        s = self.spec
        return {"x": self.x.copy(), "k": self.k, "A": s.A.copy(), "B": s.B.copy(), "ell": s.ell,
                "nonlinearity": s.nonlinearity, "name": s.name, "rng_state": None}

    def restore(self, snap: Dict[str, Any]) -> None:
        s = self.spec
        if not (np.array_equal(snap["A"], s.A) and np.array_equal(snap["B"], s.B) and snap["ell"] == s.ell
                and snap["nonlinearity"] == s.nonlinearity):
            raise MemoryLabError("snapshot belongs to a different network (A, B, ell or nonlinearity differ)")
        self.x = np.array(snap["x"], dtype=float).copy()
        self.k = int(snap["k"])

    def observe(self, H: np.ndarray) -> np.ndarray:
        """Noise-free observation H x (noise is added by the observation layer, M2)."""
        H = np.array(H, dtype=float)
        if H.ndim != 2 or H.shape[1] != self.spec.N:
            raise MemoryLabError("H must have N columns")
        return H @ self.x


def one_hot(s: int, m: int = 2) -> np.ndarray:
    if s not in range(m):
        raise MemoryLabError(f"class must be in 0..{m - 1}")
    e = np.zeros(m)
    e[s] = 1.0
    return e


def pulse_delay_inputs(s: int, d: int, m: int = 2):
    """u_0 = e_s, then d zero steps (plan §4)."""
    if d < 0:
        raise MemoryLabError("delay d must be >= 0")
    return [one_hot(s, m)] + [np.zeros(m)] * d


def recall_state(spec: NetworkSpec, s: int, d: int, *, reset_after_pulse: bool = False) -> np.ndarray:
    """State x_(d+1) for one episode from x0 = 0. With ``reset_after_pulse``
    the state is set to zero right after the pulse (reset control, plan §5.5);
    A stays unchanged and the pause inputs are zero."""
    op = EpisodeOperator(spec)
    op.reset()
    op.step(one_hot(s, spec.n_inputs))
    if reset_after_pulse:
        op.reset()
    for _ in range(d):
        op.step(np.zeros(spec.n_inputs))
    return op.x.copy()


def build_network(N=12, M=3, c=0.25, gamma=0.8, ell=0.5, inputs=(0, 4), amplitude=0.6,
                  nonlinearity="tanh", *, coupling=True, name=None) -> NetworkSpec:
    """Network from SCF public APIs (budget_adjacency, edge_mask, input_matrix).
    ``coupling=False`` gives the uncoupled leak model (A = 0, same N/B/ell)."""
    from scoped_correspondence.validation.modular_networks.adaptive_model import (
        budget_adjacency, edge_mask, input_matrix)

    # exact construction: gamma and c as Fractions (decimal strings of floats),
    # converted to float only at the end, so that exactly equal matrices (e.g.
    # M = 1 vs M = 3 with c = 8/11, control K7) are also bit-identical floats
    g = gamma if isinstance(gamma, Fraction) else Fraction(str(gamma))
    cc = None if M == 1 else (c if isinstance(c, Fraction) else Fraction(str(c)))
    A_list, mod = budget_adjacency(N, M, g, cc)
    A = np.array([[float(v) for v in row] for row in A_list]) if coupling else np.zeros((N, N))
    mask = np.array(edge_mask(N, mod), dtype=int)
    B = input_matrix(N, tuple(inputs), amplitude)
    label = name or f"N{N}_M{M}_c{c}_{nonlinearity}{'' if coupling else '_uncoupled'}"
    return NetworkSpec(A, B, ell, nonlinearity, label, list(mod), mask,
                       {"N": N, "M": M, "c": c, "gamma": gamma, "inputs": list(inputs), "amplitude": amplitude,
                        "coupling": coupling, "edges_allowed": int(mask.sum()), "row_sums": A.sum(axis=1).tolist()})


class LinearScalarKernel:
    """Reference kernel x_(k+1) = decay * x_k + u_k (controls K1, K9); exact
    with Fractions."""

    def __init__(self, decay=Fraction(1, 2), x0=0):
        self.decay = decay
        self.x = x0

    def reset(self, x0=0):
        self.x = x0

    def run(self, inputs):
        out = []
        for u in inputs:
            self.x = self.decay * self.x + u
            out.append(self.x)
        return out


__all__ = ["MemoryLabError", "NetworkSpec", "EpisodeOperator", "one_hot", "pulse_delay_inputs", "recall_state",
           "build_network", "LinearScalarKernel"]
