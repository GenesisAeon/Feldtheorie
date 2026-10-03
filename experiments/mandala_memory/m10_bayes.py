"""M10 level B: Bayes accuracy of finite Gaussian mixtures with an EXPLICIT likelihood.

For classes c with equal prior and class-conditional densities
    p(y | c) = sum_k w_ck N(y; m_ck, sigma^2 I),
the Bayes accuracy is acc_B = E_y[ max_c P(c | y) ] with y drawn from the
equal-prior mixture. The estimator averages max_c P(c|y) over n_MC draws: it is
unbiased, bounded in [1/C, 1] and has a smaller variance than counting hits.

Numerics (fixed before the freeze; review ASTRA_FOLLOWUP_R5_R8, item 3):
- log-likelihoods via log-sum-exp over the components; constants common to all
  classes (same sigma, same dimension) are dropped;
- squared distances from CENTRED coordinates (common centre = mean of all
  component means), ||y'||^2 - 2 y'.m' + ||m'||^2, clipped at 0;
- draws in fixed blocks; per-block mean and sum of squared deviations, merged
  with Chan's parallel formula; SE = sqrt(var / n);
- one fixed, independent named stream per estimate; n_MC fixed in the protocol,
  never increased depending on data;
- SE = 0 (e.g. every posterior exactly 1.0) is reported as 0 and handled by the
  explicit rule in m10_evaluate (no division by zero).
The reported uncertainty is the Monte Carlo (statistical) uncertainty; the
normal approximation of the MC mean and floating-point rounding are separate,
named error sources.
"""
from __future__ import annotations

from statistics import NormalDist
from typing import Dict, List, Sequence, Tuple

import numpy as np

from experiments.mandala_memory.m10_task import NONE, X, Y, last_channel

Mixture = Tuple[np.ndarray, np.ndarray]          # (means (K, D), weights (K,))


def _logsumexp(a: np.ndarray, axis: int) -> np.ndarray:
    m = np.max(a, axis=axis, keepdims=True)
    m = np.where(np.isfinite(m), m, 0.0)
    return np.squeeze(m, axis=axis) + np.log(np.sum(np.exp(a - m), axis=axis))


def _merge(acc: Dict, n_b: int, mean_b: float, m2_b: float) -> None:
    """Chan et al. parallel update of (n, mean, M2)."""
    if acc["n"] == 0:
        acc.update(n=n_b, mean=mean_b, m2=m2_b)
        return
    n = acc["n"] + n_b
    delta = mean_b - acc["mean"]
    acc["mean"] += delta * n_b / n
    acc["m2"] += m2_b + delta * delta * acc["n"] * n_b / n
    acc["n"] = n


def max_posterior(y: np.ndarray, classes: Sequence[Mixture], sigma: float) -> np.ndarray:
    """max_c P(c | y) for every row of y (equal priors)."""
    all_means = np.concatenate([m for m, _ in classes])
    centre = all_means.mean(axis=0)
    yc = y - centre
    yy = np.einsum("ij,ij->i", yc, yc)
    ll = []
    for means, w in classes:
        mc = means - centre
        d2 = np.maximum(yy[:, None] - 2.0 * yc @ mc.T + np.einsum("ij,ij->i", mc, mc)[None, :], 0.0)
        with np.errstate(divide="ignore"):
            logw = np.log(np.asarray(w, dtype=float))
        ll.append(_logsumexp(logw[None, :] - d2 / (2.0 * sigma ** 2), axis=1))
    ll = np.stack(ll, axis=1)                                   # (n, C)
    return np.exp(np.max(ll, axis=1) - _logsumexp(ll, axis=1))


def bayes_accuracy_mc(classes: Sequence[Mixture], sigma: float, n: int, rng: np.random.Generator,
                      block: int = 50_000) -> Dict:
    C = len(classes)
    cum = [np.cumsum(np.asarray(w, dtype=float) / np.sum(w)) for _, w in classes]
    acc = {"n": 0, "mean": 0.0, "m2": 0.0}
    done = 0
    while done < n:
        b = min(block, n - done)
        c = rng.integers(0, C, size=b)
        u = rng.random(b)
        eps = rng.normal(0.0, sigma, size=(b, classes[0][0].shape[1]))
        y = np.empty_like(eps)
        for ci, (means, _) in enumerate(classes):
            idx = c == ci
            k = np.minimum(np.searchsorted(cum[ci], u[idx], side="right"), len(cum[ci]) - 1)
            y[idx] = means[k] + eps[idx]
        v = max_posterior(y, classes, sigma)
        if not np.all(np.isfinite(v)):
            raise FloatingPointError("non-finite posterior")
        mb = float(np.mean(v))
        _merge(acc, b, mb, float(np.sum((v - mb) ** 2)))
        done += b
    var = acc["m2"] / (acc["n"] - 1) if acc["n"] > 1 else 0.0
    return {"estimate": acc["mean"], "se": float(np.sqrt(var / acc["n"])), "n": acc["n"], "block": block,
            "estimator": "mean of max posterior"}


# --- the two M10 tasks --------------------------------------------------------
def preserve_mixtures(z: np.ndarray, pats) -> List[Mixture]:
    """Classes s = A, B; components = the 27 patterns with P(pi)."""
    w = np.array([float(pr) for _, pr in pats])
    return [(z[0], w), (z[1], w)]


def update_mixtures(z: np.ndarray, pats) -> List[Mixture]:
    """Classes L = X, Y (channel of the LAST pulse), conditioned on at least one
    pulse: p(y | L=l) = sum_s 1/2 sum_{pi: last(pi)=l} P(pi)/P(last=l) N(y; z(s,pi), sigma^2 I).
    P(last = X) = P(last = Y) = 7/16, so the two classes have equal prior."""
    out = []
    for lab in (X, Y):
        idx = [i for i, (pat, _) in enumerate(pats) if last_channel(pat) == lab]
        p_last = sum(pats[i][1] for i in idx)
        means = np.concatenate([z[0][idx], z[1][idx]])
        w = np.array([0.5 * float(pats[i][1] / p_last) for i in idx] * 2)
        out.append((means, w))
    return out


def k0_preserve_analytic(z0: np.ndarray, sigma: float) -> float:
    """No distractor: two Gaussians, Bayes = Phi(||z_A - z_B|| / 2 sigma)."""
    return NormalDist().cdf(float(np.linalg.norm(z0[0] - z0[1])) / (2.0 * sigma))


__all__ = ["max_posterior", "bayes_accuracy_mc", "preserve_mixtures", "update_mixtures", "k0_preserve_analytic"]
