"""LR2 linear explanation adapter (plan section 5.3).

Near a synchronous state with equal frequencies, small deviations obey x' = -g L x with
L = diag(C 1) - C, hence
    H(t) = D_O expm(-g L t) a E,
where D_O forms the phase differences of the allowed read nodes to their reference node. For
the observation noise eps_i ~ N(0, sigma^2) per node, the m reference differences have covariance
    R = sigma^2 (I_m + 1 1^T)        (shared reference error; NOT 2m independent sensor errors).
Whitened singular values of R^{-1/2} H describe the LOCAL, noise-weighted visibility of the input
directions; H^T R^{-1} H is the Fisher information of THIS linear observation model only -- no
measured bit value and no statement about the nonlinear sin/cos pipeline. The tangent equation
along heterogeneous trajectories follows later (plan section 5.3, second part).
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy.linalg import expm

from experiments.lantern_reconstruction.dynamics import check_coupling, DynamicsError


def laplacian(C) -> np.ndarray:
    C = check_coupling(C)
    return np.diag(C.sum(axis=1)) - C


def pair_write_matrix(n: int, pairs: Sequence[Sequence[int]]) -> np.ndarray:
    """E (n x k): column j carries +1/sqrt(2), -1/sqrt(2) on its pair; disjoint pairs; E^T E = I, 1^T E = 0."""
    flat = [i for p in pairs for i in p]
    if any(len(p) != 2 for p in pairs) or len(set(flat)) != len(flat) or not all(0 <= i < n for i in flat):
        raise DynamicsError("pairs must be disjoint index pairs within the network")
    E = np.zeros((n, len(pairs)))
    for j, (a, b) in enumerate(pairs):
        E[a, j], E[b, j] = 1.0 / np.sqrt(2.0), -1.0 / np.sqrt(2.0)
    return E


def difference_operator(n: int, read: Sequence[int], ref: int) -> np.ndarray:
    """D_O (m x n): rows e_r - e_ref for every read node r != ref (feature order = order of `read`)."""
    rows = [r for r in read if r != ref]
    if len(set(rows)) != len(rows) or not all(0 <= r < n for r in rows) or not 0 <= ref < n:
        raise DynamicsError("invalid read/reference indices")
    D = np.zeros((len(rows), n))
    for k, r in enumerate(rows):
        D[k, r], D[k, ref] = 1.0, -1.0
    return D


def H(t: float, C, g: float, E: np.ndarray, a: float, D: np.ndarray) -> np.ndarray:
    return D @ expm(-g * laplacian(C) * float(t)) @ (a * E)


def reference_noise_covariance(m: int, sigma: float) -> np.ndarray:
    return sigma ** 2 * (np.eye(m) + np.ones((m, m)))


def whitened_singular_values(Hm: np.ndarray, sigma: float) -> np.ndarray:
    R = reference_noise_covariance(Hm.shape[0], sigma)
    w, V = np.linalg.eigh(R)
    R_inv_sqrt = V @ np.diag(1.0 / np.sqrt(w)) @ V.T
    return np.linalg.svd(R_inv_sqrt @ Hm, compute_uv=False)


def fisher_information(Hm: np.ndarray, sigma: float) -> np.ndarray:
    R = reference_noise_covariance(Hm.shape[0], sigma)
    return Hm.T @ np.linalg.solve(R, Hm)
