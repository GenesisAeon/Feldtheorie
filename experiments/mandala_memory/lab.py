"""M8: knob lab -- watch the Mandala remember and change one thing at a time.

EXPLORATIVE ONLY. Nothing here is a benchmark, a test of a hypothesis or a
pre-registered quantity; every computation is logged by serve.py under the
explore directory with its own run id. Benchmark results and the frozen
protocol are never read for writing and never changed.

For one knob setting the lab computes, with the tested kernel
(core.EpisodeOperator, no second physics core):

- both episodes (stimulus A, stimulus B) from x0 = 0 over d_max = 64 pause
  steps, with an optional intervention right after the pulse (clear the
  whole state or one module) and optional edge ablation;
- the ideal recall curve Bayes(d) = Phi(||H (x_A - x_B)||_2 / (2 sigma)) for
  equal priors and isotropic Gaussian observation noise sigma on each
  observed coordinate y = H x + eps (H = full / module means / sum / one node);
- an UPPER bound on that curve from the contraction factor of the actually
  used matrix, q_eff = 1 - ell + ell * max_i sum_j |A_ij|: in the max norm
  ||dx_(d+1)|| <= q_eff^d ||dx_1||, hence ||H dx|| <= kappa(H) q_eff^d ||dx_1||_inf
  with kappa(H) = sqrt(sum_r (sum_c |H_rc|)^2). It is only a bound: single
  patterns can (and in the benchmark do) disappear much faster;
- an explorative memory duration with an explicit threshold p* (default
  0.75): D = the last delay d in 0..64 with Bayes(d) >= p*, plus the
  first-passage variant (first d below p*, minus one) and whether the curve
  is monotone. A finite trained decoder can lie below the ideal curve.
"""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Dict, List

import numpy as np

from experiments.mandala_memory.core import EpisodeOperator, MemoryLabError, NetworkSpec, build_network, one_hot

LAB_SCHEMA = "mandala-memory-lab-v1"
D_MAX = 64
N_CHOICES = (6, 12, 18, 24)
READOUTS = ("full", "module_means", "sum", "node")
CLEARS = ("none", "all", "module")
ABLATION_MODES = ("budget_loss", "renormalize")
BENCHMARK_KNOBS = {"N": 12, "M": 3, "c": 0.25, "gamma": 0.8, "ell": 0.5, "amplitude": 0.6, "sigma": 0.02,
                   "inputs": [0, 4], "nonlinearity": "tanh", "clear": "none", "clear_module": 0,
                   "readout": "full", "readout_node": 0, "ablation": {"edges": [], "mode": "budget_loss"},
                   "p_star": 0.75}
# closed intervals [lo, hi]; gamma < 1 is required by SCF budget_adjacency
FLOAT_RANGES = {"c": (0.0, 1.0), "gamma": (0.01, 0.99), "ell": (0.05, 1.0), "amplitude": (0.05, 3.0),
                "sigma": (0.001, 0.5), "p_star": (0.51, 0.99)}


def _num(name: str, v) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise MemoryLabError(f"{name} must be a finite number")
    lo, hi = FLOAT_RANGES[name]
    if not (lo <= v <= hi):
        raise MemoryLabError(f"{name} must lie in [{lo}, {hi}]")
    return float(v)


def _int(name: str, v, lo: int, hi: int) -> int:
    if isinstance(v, bool) or not isinstance(v, int) or not (lo <= v <= hi):
        raise MemoryLabError(f"{name} must be an integer in {lo}..{hi}")
    return v


def validate_knobs(knobs: Dict) -> Dict:
    """Enumerated / bounded knobs only; missing knobs take the benchmark value.
    Returns a clean, complete copy (no free text, no paths)."""
    if not isinstance(knobs, dict) or set(knobs) - set(BENCHMARK_KNOBS):
        raise MemoryLabError(f"knobs must be an object with keys from {sorted(BENCHMARK_KNOBS)}")
    k = {**BENCHMARK_KNOBS, **knobs}
    N = k["N"]
    if N not in N_CHOICES or isinstance(N, bool):
        raise MemoryLabError(f"N must be one of {N_CHOICES}")
    M = _int("M", k["M"], 1, N // 2)
    if N % M:
        raise MemoryLabError("M must divide N (modules of equal size)")
    out = {"N": N, "M": M}
    for name in FLOAT_RANGES:
        out[name] = _num(name, k[name])
    if M == 1:
        out["c"] = None                                   # not applicable for one module
    inp = k["inputs"]
    if not isinstance(inp, list) or len(inp) != 2:
        raise MemoryLabError("inputs must be a list of two node indices")
    i0, i1 = (_int("inputs", v, 0, N - 1) for v in inp)
    if i0 == i1:
        raise MemoryLabError("the two inputs must be different nodes")
    out["inputs"] = [i0, i1]
    if k["nonlinearity"] not in ("tanh", "identity"):
        raise MemoryLabError("nonlinearity must be 'tanh' or 'identity'")
    out["nonlinearity"] = k["nonlinearity"]
    if k["clear"] not in CLEARS:
        raise MemoryLabError(f"clear must be one of {CLEARS}")
    out["clear"] = k["clear"]
    out["clear_module"] = _int("clear_module", k["clear_module"], 0, M - 1)
    if k["readout"] not in READOUTS:
        raise MemoryLabError(f"readout must be one of {READOUTS}")
    out["readout"] = k["readout"]
    out["readout_node"] = _int("readout_node", k["readout_node"], 0, N - 1)
    ab = k["ablation"]
    if not isinstance(ab, dict) or set(ab) - {"edges", "mode"}:
        raise MemoryLabError("ablation must be {'edges': [[i, j], ...], 'mode': ...}")
    mode = ab.get("mode", "budget_loss")
    if mode not in ABLATION_MODES:
        raise MemoryLabError(f"ablation mode must be one of {ABLATION_MODES}")
    edges = ab.get("edges", [])
    if not isinstance(edges, list) or len(edges) > N * (N - 1) // 2:
        raise MemoryLabError("ablation edges must be a list of at most N(N-1)/2 pairs")
    clean = set()
    for e in edges:
        if not isinstance(e, list) or len(e) != 2:
            raise MemoryLabError("each ablated edge is a pair [i, j]")
        a, b = (_int("edge", v, 0, N - 1) for v in e)
        if a == b:
            raise MemoryLabError("an edge needs two different nodes")
        clean.add((min(a, b), max(a, b)))
    out["ablation"] = {"edges": [list(p) for p in sorted(clean)], "mode": mode}
    return out


def readout_matrix(k: Dict, module_of: List[int]) -> np.ndarray:
    N, M = k["N"], k["M"]
    if k["readout"] == "full":
        return np.eye(N)
    if k["readout"] == "sum":
        return np.ones((1, N))
    if k["readout"] == "node":
        H = np.zeros((1, N))
        H[0, k["readout_node"]] = 1.0
        return H
    n = N // M
    H = np.zeros((M, N))
    for i, m in enumerate(module_of):
        H[m, i] = 1.0 / n
    return H


def build_lab_network(k: Dict) -> Dict:
    """Network for the knobs. Ablation removes an undirected edge (both
    directions). 'budget_loss' leaves the remaining weights as they are (row
    sums drop below gamma); 'renormalize' rescales every touched row back to
    gamma (the other edges of that row grow); a row without any edge left stays
    zero and is reported."""
    # build_network ignores c for M = 1 (SCF: c not applicable)
    spec = build_network(N=k["N"], M=k["M"], c=0.0 if k["c"] is None else k["c"], gamma=k["gamma"], ell=k["ell"],
                         inputs=tuple(k["inputs"]), amplitude=k["amplitude"], nonlinearity=k["nonlinearity"],
                         name="lab")
    A = spec.A.copy()
    already_zero, touched = [], set()
    for i, j in k["ablation"]["edges"]:
        if A[i, j] == 0 and A[j, i] == 0:
            already_zero.append([i, j])
        A[i, j] = A[j, i] = 0.0
        touched.update((i, j))
    emptied = []
    if k["ablation"]["mode"] == "renormalize":
        for r in sorted(touched):
            s = A[r].sum()
            if s > 0:
                A[r] = A[r] * (k["gamma"] / s)
            else:
                emptied.append(r)
    ablated = NetworkSpec(A, spec.B, spec.ell, spec.nonlinearity, spec.name, spec.module_of, spec.mask,
                          {**spec.meta, "ablation": k["ablation"]})
    q_eff = 1 - k["ell"] + k["ell"] * float(np.abs(A).sum(axis=1).max())
    return {"spec": ablated, "q_effective": q_eff, "q_nominal": 1 - k["ell"] + k["ell"] * k["gamma"],
            "row_sums": A.sum(axis=1).tolist(), "ablation_already_zero": already_zero, "rows_emptied": emptied}


def episode(spec: NetworkSpec, s: int, k: Dict) -> Dict:
    """x_0 = 0, pulse e_s, optional intervention, then D_MAX zero steps.
    traj[t]: t = 0 start, t = 1 state after pulse (after the intervention, if
    any), t = d + 1 readout for delay d (same convention as recall_state)."""
    op = EpisodeOperator(spec)
    op.reset()
    raw = op.step(one_hot(s, spec.n_inputs))
    if k["clear"] == "all":
        op.reset()
    elif k["clear"] == "module":
        x = op.x.copy()
        x[[i for i, m in enumerate(spec.module_of) if m == k["clear_module"]]] = 0.0
        op.reset(x)
    traj = [np.zeros(spec.N), op.x.copy()]
    for _ in range(D_MAX):
        traj.append(op.step(np.zeros(spec.n_inputs)))
    return {"traj": np.array(traj), "pulse_raw": raw}


def memory_duration(bayes: List[float], p_star: float) -> Dict:
    above = [d for d, b in enumerate(bayes) if b >= p_star]
    below = [d for d, b in enumerate(bayes) if b < p_star]
    last = above[-1] if above else None
    first_pass = (below[0] - 1 if below[0] > 0 else None) if below else len(bayes) - 1
    return {"threshold_p_star": p_star, "last_delay_at_or_above": last, "first_passage": first_pass,
            "monotone_non_increasing": all(b2 <= b1 for b1, b2 in zip(bayes, bayes[1:])),
            "censored_at_d_max": bool(bayes[-1] >= p_star),
            "definition": "last delay d in 0..64 with ideal accuracy Phi(||H dx(d)||_2 / 2 sigma) >= p*; "
                          "last_delay_at_or_above = None means below p* at every d in 0..64 (a single readout "
                          "node can reach p* only later, so Bayes(0) < p* alone does not mean None); "
                          "first_passage = (first d below p*) - 1, None if Bayes(0) < p* "
                          "(then it says nothing about later delays)"}


def compute(knobs: Dict) -> Dict:
    k = validate_knobs(knobs)
    net = build_lab_network(k)
    spec = net["spec"]
    eA, eB = episode(spec, 0, k), episode(spec, 1, k)
    H = readout_matrix(k, list(spec.module_of))
    dx = eA["traj"] - eB["traj"]                       # (D_MAX + 2, N)
    nd = NormalDist()
    sep = [float(np.linalg.norm(H @ dx[d + 1])) for d in range(D_MAX + 1)]
    bayes = [nd.cdf(s / (2 * k["sigma"])) for s in sep]
    kappa = float(np.sqrt((np.abs(H).sum(axis=1) ** 2).sum()))
    dx1 = float(np.abs(dx[1]).max())
    bound = [min(kappa * dx1 * net["q_effective"] ** d, 1e300) for d in range(D_MAX + 1)]
    return {
        "schema": LAB_SCHEMA, "explorative": True, "knobs": k,
        "network": {"A": spec.A.tolist(), "module_of": list(spec.module_of), "inputs": k["inputs"],
                    "q_effective": net["q_effective"], "q_nominal": net["q_nominal"], "row_sums": net["row_sums"],
                    "ablation": k["ablation"], "ablation_already_zero": net["ablation_already_zero"],
                    "rows_emptied": net["rows_emptied"]},
        "readout": {"H_rows": int(H.shape[0]), "kappa": kappa},
        "trajectory": {"A": eA["traj"].tolist(), "B": eB["traj"].tolist(),
                       "pulse_raw_A": eA["pulse_raw"].tolist(), "pulse_raw_B": eB["pulse_raw"].tolist(),
                       "convention": "t = 0 start, t = 1 after pulse (and intervention), t = d + 1 readout for delay d"},
        "curve": {"delay": list(range(D_MAX + 1)), "separation_l2": sep, "bayes": bayes,
                  "q_bound_separation": bound, "q_bound_bayes": [nd.cdf(b / (2 * k["sigma"])) for b in bound],
                  "bayes_formula": "Phi(||H (x_A - x_B)||_2 / (2 sigma)), equal priors, isotropic noise on y = H x",
                  "bound_formula": "||H dx(d)|| <= kappa(H) q_eff^d ||dx_1||_inf  (upper bound, not a prediction)"},
        "memory_duration": memory_duration(bayes, k["p_star"]),
    }


__all__ = ["LAB_SCHEMA", "BENCHMARK_KNOBS", "D_MAX", "validate_knobs", "build_lab_network", "readout_matrix",
           "episode", "memory_duration", "compute"]
