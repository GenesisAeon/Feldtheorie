"""M0: independent re-derivation of the handover controls K1-K9.

Written for package M0 of experiments/mandala_memory (see ROADMAP.md) BEFORE
any production code, deliberately along different routes than the delivered
``kontrollen.py``: exact Fractions for every rational claim,
``statistics.NormalDist`` instead of ``math.erf``, an independent
budget-matrix construction, a Lipschitz/sup-norm argument for K8, and an
explicit state machine for K9. Standard library only; imports no production
code (neither this experiment nor SCF nor Feldtheorie models).

Run:  python independent_controls_m0.py [--output FILE]
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction as F
from statistics import NormalDist

RESULTS: dict = {}


def k1_linear_memory():
    # x_{k+1} = x_k / 2 + u_k, x0 = 0, u0 = +-1, then zeros -> x_{d+1} = +-2^-d
    out = {}
    for d in (0, 1, 2, 4, 8):
        for s in (1, -1):
            x = F(0)
            for u in [F(s)] + [F(0)] * d:
                x = x / 2 + u
            assert x == F(s, 2 ** d), (d, s, x)
        out[d] = str(F(1, 2 ** d))
    RESULTS["K1"] = out


def k2_bayes_threshold():
    # equal priors, y = +-a + N(0, sigma^2), threshold 0: accuracy = Phi(a / sigma)
    nd = NormalDist()
    acc = {d: nd.cdf(2.0 ** -d / 0.25) for d in (0, 1, 2, 4, 8)}
    ref = [0.9999683287581669, 0.9772498680518209, 0.8413447460685428, 0.5987063256829237, 0.5062332194998896]
    for (d, a), r in zip(acc.items(), ref):
        assert abs(a - r) < 1e-12, (d, a, r)
    # strictly decreasing toward 1/2 (never below for a > 0)
    vals = list(acc.values())
    assert all(v1 > v2 > 0.5 for v1, v2 in zip(vals, vals[1:]))
    RESULTS["K2"] = acc


def k3_reset():
    # after a reset the state is exactly zero for both classes -> identical distributions
    states = []
    for s in (1, -1):
        x = F(0)
        x = x / 2 + s       # pulse
        x = F(0)            # reset right after the pulse
        for _ in range(8):
            x = x / 2
        states.append(x)
    assert states[0] == states[1] == 0
    RESULTS["K3"] = {"states": [str(v) for v in states], "bayes_accuracy": "1/2"}


def k4_sum_observation():
    a = F(1, 8)
    c0, c1 = (a, F(0)), (F(0), a)
    assert c0 != c1 and sum(c0) == sum(c1)
    # additive noise with the SAME distribution for both classes keeps the sum distributions equal:
    # Sum = a + (n1 + n2) in both cases, so the law of the observation is identical
    RESULTS["K4"] = {"sum": str(sum(c0)), "full_distinct": True}


def k5_units():
    nd = NormalDist()
    for d in (0, 1, 2, 4, 8):
        a, s = 2.0 ** -d, 0.25
        assert nd.cdf(a / s) == nd.cdf((a * 1000) / (s * 1000))
    RESULTS["K5"] = {"scale": 1000, "invariant": True}


def k6_permutation():
    T = ((0, 1), (1, 0))  # swap
    det = T[0][0] * T[1][1] - T[0][1] * T[1][0]
    assert det != 0
    stim = [(1, 0), (0, 1)]
    swapped = [(x[1], x[0]) for x in stim]
    frozen = lambda x: 0 if x[0] > x[1] else 1
    refit = lambda x: 1 if x[0] > x[1] else 0  # decoder refitted on swapped data
    assert sum(frozen(x) == lab for x, lab in zip(swapped, (0, 1))) == 0
    assert sum(refit(x) == lab for x, lab in zip(swapped, (0, 1))) == 2
    RESULTS["K6"] = {"frozen_accuracy": 0, "refit_accuracy": 1, "det": det}


def k7_budget_matrix():
    def build(N, M, gamma, c):
        n = N // M
        mod = [i // n for i in range(N)]
        A = []
        for i in range(N):
            row = []
            for j in range(N):
                if i == j:
                    row.append(F(0))
                elif M == 1:
                    row.append(gamma / (N - 1))
                elif mod[i] == mod[j]:
                    row.append(gamma * (1 - c) / (n - 1))
                else:
                    row.append(gamma * c / (N - n))
            A.append(row)
        return A

    g = F(4, 5)
    U, Mx = build(12, 1, g, None), build(12, 3, g, F(8, 11))
    assert U == Mx and all(sum(r) == g for r in U) and U[0][1] == F(4, 55)
    # and c = 1/4 (the experiment) differs from uniform:
    assert build(12, 3, g, F(1, 4)) != U
    RESULTS["K7"] = {"identical": True, "off_diagonal": "4/55", "row_sum": "4/5"}


def k8_contraction():
    # q = 1 - ell + ell * gamma with ell = 1/2, gamma = 4/5
    q = F(1, 2) + F(1, 2) * F(4, 5)
    assert q == F(9, 10) and q ** 10 == F(3486784401, 10 ** 10)
    # scalar example: F(x) = x/2 + tanh(0.8 x)/2, Lipschitz <= 1/2 + 0.8/2 = 0.9 since |tanh'| <= 1
    x, z = 0.2, 0.7
    d0 = abs(x - z)
    worst = 0.0
    for k in range(1, 11):
        x, z = 0.5 * x + 0.5 * math.tanh(0.8 * x), 0.5 * z + 0.5 * math.tanh(0.8 * z)
        worst = max(worst, abs(x - z) / (float(q) ** k * d0))
    assert worst <= 1 + 1e-12
    RESULTS["K8"] = {"q": "9/10", "q10": str(q ** 10), "max_ratio_to_bound": worst}


def k9_continuation():
    def run(inputs, x=F(0)):
        out = []
        for u in inputs:
            x = x / 2 + u
            out.append(x)
        return out, x

    stim = [F(1), F(0), F(0), F(0), F(0)]
    whole, _ = run(stim)
    head, state = run(stim[:2])
    tail, _ = run(stim[2:], state)
    tail_reset, _ = run(stim[2:], F(0))
    assert whole == head + tail and whole != head + tail_reset
    RESULTS["K9"] = {"whole": [str(v) for v in whole], "reset_tail": [str(v) for v in tail_reset]}


CHECKS = [k1_linear_memory, k2_bayes_threshold, k3_reset, k4_sum_observation, k5_units,
          k6_permutation, k7_budget_matrix, k8_contraction, k9_continuation]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    failed = []
    for c in CHECKS:
        try:
            c()
        except AssertionError as e:
            failed.append((c.__name__, repr(e)))
    out = {"passed": len(CHECKS) - len(failed), "total": len(CHECKS), "failed": failed,
           "imports_production_code": False, "results": RESULTS}
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, default=str, allow_nan=False)
    print(f"{out['passed']}/{out['total']} independent control groups re-derived")
    for f in failed:
        print("FAIL", *f)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
