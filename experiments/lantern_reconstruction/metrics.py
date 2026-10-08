"""LR4 metrics and context inference (plan sections 9, 10).

Per episode   loss = mean_j (u_hat_j - u_j)^2   with u_hat projected onto [-1, 1],
              loss_zero = mean_j u_j^2           (the information-free zero prediction).
Per cell      S = 1 - 3 mean(loss),  G = 3 mean(loss_zero - loss)  -- reported SEPARATELY; G may be
              negative (a valid result, never discarded, plan mutant 14).
Per curve     A = sum_k w_k G(tau_k): trapezoid rule on z = log(1 + tau) over the fixed grid, divided by
              log(11) -- a predefined GRID statistic, not a certified integral (control K21).

The INFERENTIAL UNIT is the context (plan 6): the inference functions take one value per context ID
and refuse anything else; episodes, times and output coordinates are never counted as replicates
(plan mutant 15). A missing grid cell is an error, never a zero (plan mutant 16)."""
from __future__ import annotations

import math
from typing import Dict, Mapping, Sequence

import numpy as np
from scipy import stats

from experiments.lantern_reconstruction import streams

MARGIN_B = 0.05          # plan 9: H-B1 / H-B2 minimum value (a declared evaluation choice, not proven relevance)
FAMILY_ALPHA_B = 0.05
LEAK_ALPHA = 0.01        # plan 10: Holm over the 12 leak-alarm cells
N_LEAK_CELLS = 12


# --- per episode / per cell ------------------------------------------------------------------------
def project(pred: np.ndarray) -> np.ndarray:
    """The fixed projection step of the main loss (plan 8): clip onto [-1, 1]. Raw values are kept separately."""
    return np.clip(np.asarray(pred, dtype=np.float64), -1.0, 1.0)


def _targets_and_predictions(pred, U):
    p, u = np.asarray(pred, dtype=np.float64), np.asarray(U, dtype=np.float64)
    if p.ndim != 2 or p.shape[1] != 4 or p.shape != u.shape or p.shape[0] < 1:
        raise ValueError(f"predictions {p.shape} and targets {u.shape} must both be (n, 4), n >= 1")
    if not (np.all(np.isfinite(p)) and np.all(np.isfinite(u))):
        raise ValueError("predictions and targets must be finite")
    return p, u


def episode_losses(pred_projected, U):
    """(loss, loss_zero), each (n,). The predictions must already be projected (see project())."""
    p, u = _targets_and_predictions(pred_projected, U)
    if np.any(np.abs(p) > 1.0):
        raise ValueError("episode_losses expects projected predictions in [-1, 1]")
    return np.mean((p - u) ** 2, axis=1), np.mean(u ** 2, axis=1)


def scores(loss: np.ndarray, loss_zero: np.ndarray) -> Dict[str, float]:
    """S and G of one cell from the episode losses (K19: S can be large while G is exactly 0)."""
    loss, loss_zero = np.asarray(loss, dtype=np.float64), np.asarray(loss_zero, dtype=np.float64)
    if loss.ndim != 1 or loss.shape != loss_zero.shape or loss.size < 1 or not (np.all(np.isfinite(loss)) and np.all(np.isfinite(loss_zero))):
        raise ValueError("loss and loss_zero must be finite (n,) arrays of the same length")
    return {"S": float(1.0 - 3.0 * np.mean(loss)), "G": float(3.0 * np.mean(loss_zero - loss)), "n_episodes": int(loss.size)}


# --- fixed grid aggregate -------------------------------------------------------------------------------
def grid_weights(times: Sequence[float] = None) -> np.ndarray:
    """Trapezoid weights on z = log(1 + tau), normalised by z_last - z_first (= log 11 for the protocol grid)."""
    t = np.asarray(streams.defaults()["time_grid"] if times is None else times, dtype=np.float64)
    if t.ndim != 1 or t.size < 2 or not np.all(np.isfinite(t)) or t[0] < 0 or np.any(np.diff(t) <= 0):
        raise ValueError("times must be a strictly increasing finite grid starting at >= 0")
    z = np.log1p(t)
    w = np.zeros(t.size)
    w[:-1] += np.diff(z) / 2
    w[1:] += np.diff(z) / 2
    return w / (z[-1] - z[0])


def curve_aggregate(G_by_time: Mapping[float, float]) -> float:
    """A from EXACTLY the protocol grid's G values: every grid time present, no extra time, all finite.
    Negative G values are valid and enter unchanged."""
    grid = [float(x) for x in streams.defaults()["time_grid"]]
    if not isinstance(G_by_time, Mapping):
        raise ValueError("G values must be given per grid time (a mapping time -> G)")
    keys = sorted(float(k) for k in G_by_time)
    if keys != grid or len(G_by_time) != len(grid):
        raise ValueError(f"the curve needs exactly the grid times {grid} (got {keys}); a missing cell is not zero")
    g = np.array([G_by_time[k] for k in grid], dtype=np.float64)         # 1.0 and 1 are the same mapping key
    if not np.all(np.isfinite(g)):
        raise ValueError("G values must be finite")
    return float(grid_weights(grid) @ g)


# --- context-level inference ------------------------------------------------------------------------------
def _context_values(values: Mapping[int, float]) -> np.ndarray:
    if not isinstance(values, Mapping):
        raise ValueError("inference needs ONE value per context: a mapping context_id -> value")
    for k in values:
        streams.check_index(k, "context id")
    v = np.array([values[k] for k in sorted(values)], dtype=np.float64)
    if v.ndim != 1 or v.size < 2 or not np.all(np.isfinite(v)):
        raise ValueError("inference needs at least two contexts with finite values")
    return v


def _sd(v: np.ndarray) -> float:
    """Sample SD (ddof 1); EXACTLY 0 when all context values are identical (np.std can return ~1e-17 there,
    which would turn the degenerate case into a huge t statistic)."""
    return 0.0 if np.all(v == v[0]) else float(np.std(v, ddof=1))


def paired_differences(a: Mapping[int, float], b: Mapping[int, float]) -> Dict[int, float]:
    """a - b per context; both must cover exactly the same contexts (pairing by context ID)."""
    if set(a) != set(b):
        raise ValueError("paired values must cover the same contexts")
    _context_values(a), _context_values(b)
    return {k: float(a[k]) - float(b[k]) for k in sorted(a)}


def summarize(values: Mapping[int, float], level: float = 0.95) -> Dict:
    """Mean, SD (ddof 1), SE and the two-sided t interval over the CONTEXTS (df = n_contexts - 1).
    Zero SD is a descriptive degenerate case: no interval width is invented and no statistic is infinite."""
    v = _context_values(values)
    n = int(v.size)
    mean, sd = float(np.mean(v)), _sd(v)
    se = sd / math.sqrt(n)
    out = {"n_contexts": n, "df": n - 1, "mean": mean, "sd": sd, "se": se, "level": level,
           "interval_kind": "pointwise two-sided t interval (model-based approximation, not simultaneous)"}
    if se == 0.0:                                   # all values identical: the mean IS that value
        out.update(degenerate=True, mean=float(v[0]), interval=[float(v[0]), float(v[0])])
    else:
        q = float(stats.t.ppf(0.5 + level / 2, n - 1))
        out.update(degenerate=False, t_quantile=q, interval=[mean - q * se, mean + q * se])
    return out


def one_sided_t(values: Mapping[int, float], margin: float) -> Dict:
    """H0: E[value] <= margin vs H1: E[value] > margin; t = (mean - margin) / SE over the contexts."""
    v = _context_values(values)
    n, mean, sd = int(v.size), float(np.mean(v)), _sd(v)
    se = sd / math.sqrt(n)
    if se == 0.0:
        return {"n_contexts": n, "df": n - 1, "mean": mean, "margin": margin, "degenerate": True, "t": None, "p": None}
    t = (mean - margin) / se
    return {"n_contexts": n, "df": n - 1, "mean": mean, "margin": margin, "degenerate": False, "t": t, "p": float(stats.t.sf(t, n - 1))}


def holm(pvalues: Sequence[float]) -> list:
    """Holm step-down adjusted p-values (monotone, capped at 1), in the input order (control K20)."""
    p = np.asarray(pvalues, dtype=np.float64)
    if p.ndim != 1 or p.size < 1 or not np.all((p >= 0) & (p <= 1)):
        raise ValueError("p-values must be a non-empty list in [0, 1]")
    m = p.size
    order = np.argsort(p, kind="stable")
    adj_sorted = np.minimum(1.0, np.maximum.accumulate((m - np.arange(m)) * p[order]))
    adj = np.empty(m)
    adj[order] = adj_sorted
    return adj.tolist()


def hypotheses_B(A_lantern: Mapping[int, float], A_surrogate: Mapping[int, float], margin: float = MARGIN_B,
                 alpha: float = FAMILY_ALPHA_B) -> Dict:
    """Plan 9: H-B1 E[A_lantern] > margin, H-B2 E[A_lantern - A_strength_surrogate] > margin; one-sided t
    tests on the context values minus margin, Holm over exactly these two p-values at the family level;
    raw 95% intervals (NOT simultaneous) and two Bonferroni intervals (t quantile 1 - alpha/4 = .9875)."""
    diff = paired_differences(A_lantern, A_surrogate)
    t1, t2 = one_sided_t(A_lantern, margin), one_sided_t(diff, margin)
    out = {"H_B1": t1, "H_B2": t2, "margin": margin, "family_alpha": alpha}
    if t1["degenerate"] or t2["degenerate"]:
        out.update(holm_adjusted=None, rejected=None, note="degenerate context SD: descriptive case, no test decision")
    else:
        adj = holm([t1["p"], t2["p"]])
        out.update(holm_adjusted=adj, rejected=[a <= alpha for a in adj])
    out["raw_intervals_95"] = {"H_B1": summarize(A_lantern), "H_B2": summarize(diff)}
    out["bonferroni_intervals"] = {"H_B1": summarize(A_lantern, 1 - alpha / 2), "H_B2": summarize(diff, 1 - alpha / 2)}
    return out


# --- permutation leak alarm (plan 10, empirical controls) ----------------------------------------------------
def permutation_p(b: int, B: int) -> float:
    """p = (1 + b) / (1 + B) with b permutation statistics >= the observed one out of B."""
    for x, name in ((b, "b"), (B, "B")):
        if isinstance(x, (bool, np.bool_)) or not isinstance(x, (int, np.integer)) or x < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    if B < 1 or b > B:
        raise ValueError("need 0 <= b <= B and B >= 1")
    return (1 + int(b)) / (1 + int(B))


def permutation_gain_test(cells: Mapping[int, tuple], rng: np.random.Generator, n_perm: int = 9999) -> Dict:
    """One leak-alarm cell: statistic = mean over contexts of G; test targets permuted WITHIN each context,
    predictions fixed. cells: context_id -> (projected predictions (n, 4), targets (n, 4))."""
    if not isinstance(rng, np.random.Generator):
        raise ValueError("an explicit numpy Generator is required (no global RNG)")
    _context_values({k: 0.0 for k in cells})
    data = []
    for k in sorted(cells):
        p, u = _targets_and_predictions(*cells[k])
        data.append((p, u, np.mean(u ** 2, axis=1)))

    def stat(perms):
        return float(np.mean([3.0 * np.mean(lz[pi] - np.mean((p - u[pi]) ** 2, axis=1)) for (p, u, lz), pi in zip(data, perms)]))

    observed = stat([np.arange(len(d[1])) for d in data])
    b = sum(stat([rng.permutation(len(d[1])) for d in data]) >= observed for _ in range(n_perm))
    return {"observed_mean_G": observed, "b": int(b), "B": int(n_perm), "p": permutation_p(int(b), int(n_perm))}


def leak_alarm(pvalues: Sequence[float], alpha: float = LEAK_ALPHA) -> Dict:
    """Holm over exactly the 12 predefined control cells; any adjusted p <= alpha raises the alarm, which
    blocks the scientific release until investigated. Strongly negative G is no leak alarm."""
    if len(pvalues) != N_LEAK_CELLS:
        raise ValueError(f"the leak alarm uses exactly {N_LEAK_CELLS} predefined cells")
    adj = holm(pvalues)
    return {"holm_adjusted": adj, "alarm": any(a <= alpha for a in adj), "alpha": alpha}
