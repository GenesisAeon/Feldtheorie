"""LR4 Ridge fit in NumPy closed form (plan section 8; LR0-O1: no scikit-learn in the lab venv).

Objective (plan 8), with X_s the standardised training features and an UNPENALISED intercept b:

    (1/N) ||X_s W + 1 b^T - U||_F^2 + lambda ||W||_F^2.

Minimising over b gives b = mean(U) - mean(X_s) W; with the centred Xc = X_s - mean(X_s) and Uc = U - mean(U)
the optimal W solves (Xc^T Xc / N + lambda I) W = Xc^T Uc / N. It is computed from the thin SVD
Xc = P diag(s) Q^T as W = Q diag(s / (s^2 + N lambda)) P^T Uc -- stable for every lambda > 0, also with
constant or collinear columns, and one SVD serves the whole lambda grid. (scikit-learn's Ridge minimises
the UNAVERAGED residual sum: its alpha equals N * lambda here; plan mutant 13.)

Standardisation and every fit quantity come from the TRAINING split only; the validation split only
selects lambda; the test split is never an argument of this module (plan mutants 11, 12)."""
from __future__ import annotations

import platform
from typing import Dict, Optional, Sequence

import numpy as np

from experiments.lantern_reconstruction.decoders import FEATURE_ORDER, RidgeDecoder, predict, select_lambda
from experiments.lantern_reconstruction.metrics import project
from experiments.lantern_reconstruction.observation import ObservationSpec

LAMBDA_GRID = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0)     # plan 8
SOLVER = "numpy.linalg.svd of the centred standardised training features (closed form, no iteration)"


def _real_matrix(x, what: str, cols: Optional[int] = None) -> np.ndarray:
    a = np.asarray(x)
    if a.dtype.kind not in "iuf" or a.ndim != 2 or a.shape[0] < 1 or (cols is not None and a.shape[1] != cols) or not np.all(np.isfinite(a)):
        raise ValueError(f"{what} must be a finite real 2-D array" + (f" with {cols} columns" if cols else "") + f" (got {a.dtype}, {a.shape})")
    return a.astype(np.float64)


def standardisation(X_train) -> tuple:
    """mean and population SD (ddof 0) of the training features.

    An EXACTLY constant column (all values identical) is recognised by its values, not by its computed SD:
    NumPy can return a tiny positive SD there (review REVIEW_LR4 R1: 1000 x 0.1 gave 1.39e-17, which would
    blow up any later deviation). Such a column gets mean = its value and scale = 1, so it standardises to
    exactly 0. No epsilon threshold: a nearly constant but varying column keeps its true SD. Non-constant
    columns are computed exactly as before."""
    x = _real_matrix(X_train, "X_train")
    mean, sd = x.mean(axis=0), x.std(axis=0, ddof=0)
    const = np.all(x == x[0], axis=0)
    mean = np.where(const, x[0], mean)
    return mean, np.where(const, 1.0, sd)


def ridge_path(Xs: np.ndarray, U: np.ndarray, lambdas: Sequence[float]):
    """Exact minimisers (W, b) of the plan-8 objective in the standardised space for every lambda."""
    N = Xs.shape[0]
    xbar, ubar = Xs.mean(axis=0), U.mean(axis=0)
    Xc, Uc = Xs - xbar, U - ubar
    P, s, Qt = np.linalg.svd(Xc, full_matrices=False)
    PtU = P.T @ Uc
    out = []
    for lam in lambdas:
        W = Qt.T @ ((s / (s ** 2 + N * lam))[:, None] * PtU)
        out.append((W, ubar - xbar @ W))
    return out


def _check_grid(lambda_grid) -> tuple:
    grid = tuple(lambda_grid)
    if (not grid or any(isinstance(v, (bool, np.bool_)) or not isinstance(v, (int, float, np.integer, np.floating)) for v in grid)
            or not all(np.isfinite(v) and v > 0 for v in grid) or len(set(grid)) != len(grid)):
        raise ValueError("lambda grid must be distinct finite positive numbers")
    return tuple(float(v) for v in grid)


def permuted_null_gains(X_train, U_train, X_val, U_val, X_test, U_test, rng: np.random.Generator, n_perm: int,
                        lambda_grid: Sequence[float] = LAMBDA_GRID, chunk: int = 128) -> np.ndarray:
    """Null distribution of the permuted-target control (decision Johann 2026-10-09, LR6 acceptance alarm): for
    each of n_perm draws, NEW permutations of the training targets and then of the validation targets (in this
    order, from `rng`), the complete fit_ridge procedure (train-only standardisation, unpenalised intercept,
    lambda by projected validation MSE with the larger lambda on an exact tie) and the test gain
    G = 3 mean(loss_zero - loss) on the REAL test targets. Exactly fit_ridge + scoring, vectorised: the SVD of
    the centred standardised training features is computed once (a permutation keeps the target mean)."""
    if not isinstance(rng, np.random.Generator):
        raise ValueError("an explicit numpy Generator is required")
    if isinstance(n_perm, (bool, np.bool_)) or not isinstance(n_perm, (int, np.integer)) or n_perm < 1:
        raise ValueError("n_perm must be a positive integer")
    grid = np.array(_check_grid(lambda_grid))
    Xtr, Xva, Xte = (_real_matrix(x, n) for x, n in ((X_train, "X_train"), (X_val, "X_val"), (X_test, "X_test")))
    Utr, Uva, Ute = (_real_matrix(u, n, 4) for u, n in ((U_train, "U_train"), (U_val, "U_val"), (U_test, "U_test")))
    mean, scale = standardisation(Xtr)
    Xs, Xvs, Xts = (Xtr - mean) / scale, (Xva - mean) / scale, (Xte - mean) / scale
    N, Nv = Xs.shape[0], Xvs.shape[0]
    xbar, ubar = Xs.mean(axis=0), Utr.mean(axis=0)
    P, s, Qt = np.linalg.svd(Xs - xbar, full_matrices=False)
    Uc = Utr - ubar
    shrink = s[None, :] / (s[None, :] ** 2 + N * grid[:, None])                 # (L, r)
    loss_zero = np.mean(Ute ** 2, axis=1)
    out = np.empty(n_perm)
    for start in range(0, n_perm, chunk):
        k = min(chunk, n_perm - start)
        perms = [(rng.permutation(N), rng.permutation(Nv)) for _ in range(k)]
        Ucb = np.stack([Uc[pt] for pt, _ in perms])                               # (k, N, 4)
        Uvb = np.stack([Uva[pv] for _, pv in perms])                              # (k, Nv, 4)
        PtU = np.matmul(P.T, Ucb)                                                 # (k, r, 4)
        W = np.matmul(Qt.T, shrink[None, :, :, None] * PtU[:, None, :, :])       # (k, L, d, 4)
        b = ubar - np.matmul(xbar, W)                                             # (k, L, 4)
        pv = np.clip(np.matmul(Xvs, W) + b[:, :, None, :], -1.0, 1.0)            # (k, L, Nv, 4)
        mse = np.mean((pv - Uvb[:, None]) ** 2, axis=(2, 3))                       # (k, L)
        best = np.argmax(np.where(mse == mse.min(axis=1, keepdims=True), grid[None, :], -np.inf), axis=1)
        Wsel, bsel = W[np.arange(k), best], b[np.arange(k), best]
        pt = np.clip(np.matmul(Xts, Wsel) + bsel[:, None, :], -1.0, 1.0)
        out[start:start + k] = 3.0 * np.mean(loss_zero[None, :] - np.mean((pt - Ute[None]) ** 2, axis=2), axis=1)
    return out


def fit_ridge(spec: ObservationSpec, X_train, U_train, X_val, U_val, lambda_grid: Sequence[float] = LAMBDA_GRID,
              provenance: Optional[Dict] = None) -> RidgeDecoder:
    """Fit on train, choose lambda on val (projected MSE; exact tie -> larger lambda). No test argument."""
    grid = _check_grid(lambda_grid)
    d = spec.n_features
    Xtr, Xva = _real_matrix(X_train, "X_train", d), _real_matrix(X_val, "X_val", d)
    Utr, Uva = _real_matrix(U_train, "U_train", 4), _real_matrix(U_val, "U_val", 4)
    if Xtr.shape[0] != Utr.shape[0] or Xva.shape[0] != Uva.shape[0]:
        raise ValueError("features and targets must have the same number of episodes per split")
    mean, scale = standardisation(Xtr)
    path = ridge_path((Xtr - mean) / scale, Utr, grid)
    feature_definition = {"task": spec.task, "nodes": [int(i) for i in spec.nodes], "reference": int(spec.reference),
                          "order": FEATURE_ORDER}
    val_mse = []
    for W, b in path:          # a provisional decoder per lambda, only to predict the validation split
        probe = RidgeDecoder(spec.task, feature_definition, mean, scale, W, b, max(grid), np.array(grid), np.zeros(len(grid)), 1, 1)
        val_mse.append(float(np.mean((project(predict(probe, Xva)) - Uva) ** 2)))
    lam = select_lambda(grid, val_mse)
    W, b = path[grid.index(lam)]
    return RidgeDecoder(spec.task, feature_definition, mean, scale, W, b, lam, np.array(grid), np.array(val_mse),
                        int(Xtr.shape[0]), int(Xva.shape[0]), dict(provenance or {}),
                        {"python": platform.python_version(), "numpy": np.__version__, "solver": SOLVER})
