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
