"""LR3 reference networks (plan section 7). All conditions of a context use the SAME g.

- uncoupled:          zero matrix;
- uniform_total:      C_ij = sum(C) / (n(n-1)) for i != j (same total weight, not the same strengths);
- strength_surrogate: four distinct nodes a, b, c, d; w_ab += delta, w_cd += delta, w_ac -= delta,
  w_bd -= delta with delta ~ U[lo, hi], lo = max(-w_ab, -w_cd, w_ac - 1, w_bd - 1),
  hi = min(1 - w_ab, 1 - w_cd, w_ac, w_bd); hi <= lo -> unchanged, counted as degenerate.
  Starts from the original C, own null-model stream. Keeps symmetry, zero diagonal, node
  strengths and [0, 1]; all invariants are recomputed. NO claim of an exact uniform ensemble.
A pure node permutation is an isomorphic network (an invariance test, not a reference)."""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

from experiments.lantern_reconstruction.dynamics import check_coupling


def uncoupled(C: np.ndarray) -> np.ndarray:
    return np.zeros_like(check_coupling(C))


def uniform_total(C: np.ndarray) -> np.ndarray:
    C = check_coupling(C)
    n = C.shape[0]
    U = np.full((n, n), C.sum() / (n * (n - 1)))
    np.fill_diagonal(U, 0.0)
    return U


def strength_surrogate(C: np.ndarray, rng: np.random.Generator, proposals: int) -> Tuple[np.ndarray, Dict]:
    C = check_coupling(C)
    if C.max() > 1.0:
        raise ValueError("C must lie in [0, 1]")
    W = C.copy()
    n = W.shape[0]
    degenerate = 0
    for _ in range(int(proposals)):
        a, b, c, d = rng.choice(n, size=4, replace=False)
        lo = max(-W[a, b], -W[c, d], W[a, c] - 1.0, W[b, d] - 1.0)
        hi = min(1.0 - W[a, b], 1.0 - W[c, d], W[a, c], W[b, d])
        if hi <= lo:
            degenerate += 1
            continue
        delta = rng.uniform(lo, hi)
        for i, j, s in ((a, b, 1.0), (c, d, 1.0), (a, c, -1.0), (b, d, -1.0)):
            W[i, j] += s * delta
            W[j, i] = W[i, j]
    excess = float(max(0.0, -W.min(), W.max() - 1.0))
    if excess > 1e-12:
        raise ValueError(f"surrogate left [0, 1] by {excess:.3e} (more than rounding)")
    n_rounded = int(np.count_nonzero((W < 0.0) | (W > 1.0)))
    W = np.clip(W, 0.0, 1.0)                                  # only rounding (<= 1e-12), counted and reported
    rep = invariant_report(C, W)
    rep.update({"proposals": int(proposals), "degenerate": degenerate, "rounding_clipped_entries": n_rounded,
                "rounding_excess_max": excess})
    if not rep["ok"]:
        raise ValueError(f"surrogate invariants violated: {rep}")
    return W, rep


def invariant_report(C: np.ndarray, W: np.ndarray, tol: float = 1e-10) -> Dict:
    up_c, up_w = C[np.triu_indices_from(C, 1)], W[np.triu_indices_from(W, 1)]
    rep = {"symmetric": bool(np.array_equal(W, W.T)), "zero_diagonal": bool(np.all(np.diag(W) == 0.0)),
           "in_unit_interval": bool(W.min() >= 0.0 and W.max() <= 1.0),
           "max_strength_deviation": float(np.max(np.abs(W.sum(1) - C.sum(1)))),
           "frobenius_distance": float(np.linalg.norm(W - C)),
           "weight_quantiles_original": [float(q) for q in np.quantile(up_c, [0, 0.25, 0.5, 0.75, 1])],
           "weight_quantiles_surrogate": [float(q) for q in np.quantile(up_w, [0, 0.25, 0.5, 0.75, 1])],
           "eigenvalues_original_top3": [float(x) for x in np.sort(np.linalg.eigvalsh(C))[::-1][:3]],
           "eigenvalues_surrogate_top3": [float(x) for x in np.sort(np.linalg.eigvalsh(W))[::-1][:3]]}
    rep["ok"] = rep["symmetric"] and rep["zero_diagonal"] and rep["in_unit_interval"] and rep["max_strength_deviation"] <= tol
    return rep
