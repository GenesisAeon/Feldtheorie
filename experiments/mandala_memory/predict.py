"""M9: closed-form predictions of the ideal recall curve (docs/M9_HERLEITUNG.md).

Deliberately independent of the tested kernel: this module imports neither
core, lab, serve nor SCF. Everything follows from the mode decomposition of
the block-uniform coupling (section 3) and the provable linearisation bound
(section 5). Predictions for held-out combinations are computed here, frozen
(m9_freeze.py) and only afterwards compared with the kernel (m9_evaluate.py).
"""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Dict, List, Optional

import numpy as np

D_MAX = 64
READOUTS = ("full", "module_means", "sum", "node")
COMBO_KEYS = ("N", "M", "c", "gamma", "ell", "amplitude", "sigma", "inputs", "readout", "readout_node", "nonlinearity")
FLOAT_SAFETY = (1e-9, 1e-18)          # E is inflated by (1 + 1e-9) and 1e-18 against rounding in its own evaluation


class OutsideFamily(ValueError):
    """Combination outside the family F of the derivation (section 1)."""


def check_family(p: Dict) -> Dict:
    if set(p) != set(COMBO_KEYS):
        raise OutsideFamily(f"combination needs exactly the keys {COMBO_KEYS}")
    N, M = p["N"], p["M"]
    if not (isinstance(N, int) and isinstance(M, int) and M >= 1 and N % M == 0 and (M == 1 or N // M >= 2)):
        raise OutsideFamily("M must divide N with module size >= 2 (or M = 1)")
    if not (0 < p["gamma"] < 1 and 0 < p["ell"] <= 1 and p["amplitude"] > 0 and p["sigma"] > 0):
        raise OutsideFamily("0 < gamma < 1, 0 < ell <= 1, amplitude > 0, sigma > 0 required")
    if M > 1 and not (p["c"] is not None and 0 <= p["c"] <= 1):
        raise OutsideFamily("c in [0, 1] required for M > 1")
    i, j = p["inputs"]
    if not (0 <= i < N and 0 <= j < N and i != j):
        raise OutsideFamily("two different input nodes required")
    if p["readout"] not in READOUTS or not (0 <= p["readout_node"] < N):
        raise OutsideFamily("unknown readout")
    if p["nonlinearity"] not in ("tanh", "identity"):
        raise OutsideFamily("nonlinearity tanh or identity")
    return p


def modes(p: Dict) -> Dict:
    N, M, g_, c, ell = p["N"], p["M"], p["gamma"], p["c"], p["ell"]
    n = N // M
    lam_D = None if M == 1 else g_ * (1 - c * N / (N - n))
    lam_I = -g_ / (N - 1) if M == 1 else -g_ * (1 - c) / (n - 1)
    mu = lambda lam: 1 - ell + ell * lam
    i, j = p["inputs"]
    same = (i // n) == (j // n)
    mu_D = None if lam_D is None else mu(lam_D)
    rho = abs(mu(lam_I)) if same or M == 1 else max(abs(mu_D), abs(mu(lam_I)))
    return {"n": n, "q": mu(g_), "lam_D": lam_D, "lam_I": lam_I, "mu_D": mu_D, "mu_I": mu(lam_I),
            "rho_antisymmetric": rho, "same_module": same}


def symmetry_permutation(N: int, M: int, i: int, j: int) -> List[int]:
    """Involution P (as image list) with P(i) = j and P A P^T = A for every
    block-uniform A (section 5). Used in the tests, not in the prediction."""
    n = N // M
    perm = list(range(N))
    mi, ti, mj, tj = i // n, i % n, j // n, j % n
    if mi == mj:
        perm[i], perm[j] = j, i
        return perm
    pi = list(range(n))
    pi[ti], pi[tj] = tj, ti
    for t in range(n):
        perm[mi * n + t] = mj * n + pi[t]
        perm[mj * n + t] = mi * n + pi[t]
    return perm


def readout_matrix(p: Dict) -> np.ndarray:
    N, M = p["N"], p["M"]
    n = N // M
    if p["readout"] == "full":
        return np.eye(N)
    if p["readout"] == "sum":
        return np.ones((1, N))
    if p["readout"] == "node":
        H = np.zeros((1, N))
        H[0, p["readout_node"]] = 1.0
        return H
    H = np.zeros((M, N))
    for r in range(N):
        H[r // n, r] = 1.0 / n
    return H


def _components(p: Dict, node: int):
    """(1/N) 1, (1_m/n - 1/N), (e_node - 1_m/n): the three mode components of e_node."""
    N, n = p["N"], p["N"] // p["M"]
    m = node // n
    one = np.full(N, 1.0 / N)
    mod = np.zeros(N)
    mod[m * n:(m + 1) * n] = 1.0 / n
    e = np.zeros(N)
    e[node] = 1.0
    return one, mod - one, e - mod


def _h(z: np.ndarray) -> np.ndarray:
    """z - tanh z, accurate also for small |z| (series), >= 0 for z >= 0."""
    z = np.asarray(z, dtype=float)
    small = np.abs(z) < 1e-2
    zs = z[small]
    out = z - np.tanh(z)
    out[small] = zs ** 3 / 3 - 2 * zs ** 5 / 15 + 17 * zs ** 7 / 315
    return out


def predict(p: Dict, p_star: float = 0.75) -> Dict:
    p = check_family(dict(p))
    m = modes(p)
    N, ell = p["N"], p["ell"]
    i, j = p["inputs"]
    # exact stimulus coupling x_1 = ell f(a) e_i (section 2); f = tanh, or identity in the linear limit
    g = ell * (math.tanh(p["amplitude"]) if p["nonlinearity"] == "tanh" else p["amplitude"])
    H = readout_matrix(p)
    H_norm = float(np.linalg.norm(H, 2))
    # linear difference: g [mu_D^d P_D u + mu_I^d P_I u]; the common part of e_i and e_j cancels
    _, di, ii = _components(p, i)
    _, dj, ij = _components(p, j)
    PDu, PIu = di - dj, ii - ij
    s_lin, lin_vec = [], []
    for d in range(D_MAX + 1):
        v = g * ((m["mu_D"] ** d if m["mu_D"] is not None else 0.0) * PDu + m["mu_I"] ** d * PIu)
        lin_vec.append(v)
        s_lin.append(float(np.linalg.norm(H @ v)))
    # error bound E(d) (section 5); A y_k in closed form, y_1 = x_1 = g e_i
    E = [0.0]
    if p["nonlinearity"] == "tanh":
        one, dmod, intra = _components(p, i)
        lamD = m["lam_D"] if m["lam_D"] is not None else 0.0
        muD = m["mu_D"] if m["mu_D"] is not None else 0.0
        acc = 0.0
        for k in range(1, D_MAX + 1):        # E(d) = rho E(d-1) + 2 ell ||h(A y_d)||, d = k
            Ay = g * (p["gamma"] * m["q"] ** (k - 1) * one + lamD * muD ** (k - 1) * dmod
                      + m["lam_I"] * m["mu_I"] ** (k - 1) * intra)
            acc = m["rho_antisymmetric"] * acc + 2 * ell * float(np.linalg.norm(_h(np.maximum(Ay, 0.0))))
            E.append(acc * (1 + FLOAT_SAFETY[0]) + FLOAT_SAFETY[1])
    else:
        E = [0.0] * (D_MAX + 1)
    nd = NormalDist()
    two_s = 2 * p["sigma"]
    lo = [nd.cdf(max(0.0, s - H_norm * e) / two_s) for s, e in zip(s_lin, E)]
    hi = [nd.cdf((s + H_norm * e) / two_s) for s, e in zip(s_lin, E)]
    lin = [nd.cdf(s / two_s) for s in s_lin]
    s_q = [s_lin[0] * m["q"] ** d for d in range(D_MAX + 1)]
    D_lin, D_lo, D_hi = _last_above(lin, p_star), _last_above(lo, p_star), _last_above(hi, p_star)
    D_q = _last_above([nd.cdf(s / two_s) for s in s_q], p_star)
    return {
        "combination": p, "p_star": p_star, "g": g, "H_norm2": H_norm, "kappa_nl": p["gamma"] * ell * math.tanh(p["amplitude"]),
        "modes": m, "weights": {"PD_u_norm2": float(PDu @ PDu), "PI_u_norm2": float(PIu @ PIu)},
        "separation_linear": s_lin, "error_bound_E": E, "bayes_linear": lin, "bayes_band_lo": lo, "bayes_band_hi": hi,
        "D_linear": D_lin, "D_interval": [D_lo, D_hi], "D_point_prediction": D_lo == D_hi,
        "D_naive_q_rule": D_q,
        "censored_at_d_max": hi[-1] >= p_star,
    }


def _last_above(curve: List[float], p_star: float) -> Optional[int]:
    above = [d for d, b in enumerate(curve) if b >= p_star]
    return above[-1] if above else None


__all__ = ["OutsideFamily", "check_family", "modes", "symmetry_permutation", "readout_matrix", "predict", "D_MAX",
           "COMBO_KEYS"]
