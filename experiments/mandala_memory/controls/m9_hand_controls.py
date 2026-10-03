"""M9 hand controls -- independent of predict.py, SCF and the kernel.

Exact Fractions with an own block matrix: checks the mode eigenvalues of
docs/M9_HERLEITUNG.md section 3 by explicit A v = lambda v, the trace
identity, the projection weights, and the benchmark's linear separation by
EXACT matrix powers (not via the mode formula). Only the factor
g = ell * tanh(a) and Phi are floats.

    python experiments/mandala_memory/controls/m9_hand_controls.py
"""
from __future__ import annotations

import json
import math
from fractions import Fraction as F
from statistics import NormalDist


def block_A(N, M, gamma, c):
    n = N // M
    mod = [i // n for i in range(N)]
    A = [[F(0)] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i != j:
                A[i][j] = gamma / (N - 1) if M == 1 else (gamma * (1 - c) / (n - 1) if mod[i] == mod[j] else gamma * c / (N - n))
    return A, mod, n


def matvec(A, v):
    return [sum(a * x for a, x in zip(row, v)) for row in A]


def modes(N, M, gamma, c, ell):
    n = N // M
    lam_D = None if M == 1 else gamma * (1 - c * F(N, N - n))
    lam_I = -(gamma / (N - 1)) if M == 1 else -(gamma * (1 - c) / (n - 1))
    mu = lambda lam: 1 - ell + ell * lam
    return {"q": mu(gamma), "mu_D": None if lam_D is None else mu(lam_D), "mu_I": mu(lam_I), "lam_D": lam_D, "lam_I": lam_I}


def check_eigen(N, M, gamma, c, ell):
    A, mod, n = block_A(N, M, gamma, c)
    m = modes(N, M, gamma, c, ell)
    ones = [F(1)] * N
    assert matvec(A, ones) == [gamma * x for x in ones]
    if M > 1:
        vD = [F(1) if mod[i] == 0 else (F(-1) if mod[i] == 1 else F(0)) for i in range(N)]
        assert matvec(A, vD) == [m["lam_D"] * x for x in vD]
    vI = [F(0)] * N
    vI[0], vI[1] = F(1), F(-1)                          # nodes 0, 1 share module 0 (n >= 2)
    assert matvec(A, vI) == [m["lam_I"] * x for x in vI]
    tr = gamma + (M - 1) * (m["lam_D"] or 0) + (N - M) * m["lam_I"]
    assert tr == 0 == sum(A[i][i] for i in range(N))
    return m


def sep2_exact(N, M, gamma, c, ell, i, j, d):
    """||J^d (e_i - e_j)||^2 exactly, by repeated multiplication."""
    A, _, _ = block_A(N, M, gamma, c)
    v = [F(0)] * N
    v[i], v[j] = F(1), F(-1)
    for _ in range(d):
        Av = matvec(A, v)
        v = [(1 - ell) * x + ell * y for x, y in zip(v, Av)]
    return sum(x * x for x in v)


def main() -> int:
    out = {}
    # benchmark
    bm = check_eigen(12, 3, F(4, 5), F(1, 4), F(1, 2))
    assert (bm["q"], bm["mu_D"], bm["mu_I"]) == (F(9, 10), F(3, 4), F(2, 5))
    out["benchmark_modes"] = {k: str(v) for k, v in bm.items()}
    # other shapes (eigen identities only)
    for args in [(12, 1, F(4, 5), None, F(1, 2)), (12, 2, F(7, 10), F(1, 3), F(3, 10)), (24, 6, F(9, 10), F(4, 5), F(3, 4)),
                 (18, 9, F(3, 5), F(1, 10), F(1, 1)), (6, 3, F(1, 2), F(0), F(1, 4))]:
        check_eigen(*args)
    # projection weights for e_0 - e_4 (different modules) and closed form vs exact powers
    g = 0.5 * math.tanh(0.6)
    nd = NormalDist()
    curve = {}
    for d in range(0, 17):
        s2 = sep2_exact(12, 3, F(4, 5), F(1, 4), F(1, 2), 0, 4, d)
        closed = F(1, 2) * F(3, 4) ** (2 * d) + F(3, 2) * F(2, 5) ** (2 * d)   # w_D = 2/n, w_I = 2 - 2/n
        assert s2 == closed, d
        curve[d] = nd.cdf(g * math.sqrt(s2) / 0.04)
    # same module (0, 1): only the intra mode
    for d in (0, 3, 7):
        assert sep2_exact(12, 3, F(4, 5), F(1, 4), F(1, 2), 0, 1, d) == 2 * F(2, 5) ** (2 * d)
    r_star = 0.04 * nd.inv_cdf(0.75)
    D = max(d for d in curve if curve[d] >= 0.75)
    out["benchmark_linear_bayes"] = {d: round(curve[d], 6) for d in (0, 1, 2, 4, 6, 7, 8, 16)}
    out["benchmark_linear_D75"] = D
    out["r_star"] = r_star
    assert D == 6 and abs(curve[8] - 0.6827) < 1e-4 and abs(curve[4] - 0.9353) < 1e-4
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
