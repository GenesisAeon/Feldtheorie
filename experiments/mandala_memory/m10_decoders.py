"""M10 level D (descriptive): trained decoders on sampled episodes.

Episodes for (seed, role, delay): patterns and observation noise come from
named streams that depend ONLY on (seed, kind, role, delay) -- identical across
networks, nonlinearities and conditions (paired comparisons), disjoint across
roles (train/test). Within a split every drawn pattern is used for one A and one
B episode, so the pattern distribution is exactly equal in both target classes.
The decoder sees only y; never the pattern, the pair index or the stream.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from experiments.mandala_memory.core import MemoryLabError
from experiments.mandala_memory.data import NearestMeanDecoder, balanced_accuracy, stream
from experiments.mandala_memory.m10_task import last_channel

ROLES = ("decoder_train", "test")


@dataclass(frozen=True)
class Episodes:
    role: str
    delay: int
    ids: Tuple[str, ...]
    target: np.ndarray            # (2n,) 0 = A, 1 = B
    pattern_index: np.ndarray     # (2n,) index into the 27 patterns
    last: np.ndarray              # (2n,) 1 = X, 2 = Y, 0 = no pulse
    noise: np.ndarray             # (2n, N)
    derivation: Tuple[Tuple[int, ...], Tuple[int, ...]]


def make_episodes(mode: str, seed: int, role: str, delay: int, n_per_class: int, pats, N: int, sigma: float) -> Episodes:
    if role not in ROLES:
        raise MemoryLabError(f"role must be one of {ROLES}")
    rng_p, key_p = stream(mode, seed, "pattern", role, delay)
    rng_e, key_e = stream(mode, seed, "noise", role, delay)
    probs = np.array([float(pr) for _, pr in pats])
    pi = rng_p.choice(len(pats), size=n_per_class, p=probs / probs.sum())
    pattern_index = np.concatenate([pi, pi])                 # pair: same pattern for A and B
    target = np.repeat([0, 1], n_per_class)
    last = np.array([last_channel(pats[i][0]) or 0 for i in pattern_index])
    noise = rng_e.normal(0.0, sigma, size=(2 * n_per_class, N))
    ids = tuple(f"m10:{mode}:s{seed}:{role}:d{delay}:{c}:{i}" for c in (0, 1) for i in range(n_per_class))
    return Episodes(role, delay, ids, target, pattern_index, last, noise, (key_p, key_e))


def observe(z: np.ndarray, ep: Episodes) -> np.ndarray:
    """y = z(s, pi) + eps; z has shape (2, 27, N)."""
    return z[ep.target, ep.pattern_index] + ep.noise


def check_class_independence(ep: Episodes, n_patterns: int) -> Dict:
    """The pattern distribution must be identical in both target classes (leak check)."""
    counts = [np.bincount(ep.pattern_index[ep.target == c], minlength=n_patterns) for c in (0, 1)]
    return {"identical_pattern_counts": bool(np.array_equal(*counts))}


def check_split(train: Episodes, test: Episodes) -> Dict:
    from scoped_correspondence.validation.modular_networks.decoders import check_split as scf_check_split

    scf_check_split(train.ids, test.ids)                    # raises on shared episode ids
    shared = set(train.derivation) & set(test.derivation)
    if shared or train.role == test.role:
        raise MemoryLabError(f"train and test share a random stream: {sorted(shared)}")
    return {"ids_disjoint": True, "streams_disjoint": True}


class LedoitWolfLDA:
    """Two-class LDA with a pooled within-class covariance shrunk towards
    (tr S / p) I with the Ledoit-Wolf (2004) intensity; equal priors, threshold
    at the midpoint of the class means; fitted on training data only."""

    def fit(self, Y: np.ndarray, labels) -> "LedoitWolfLDA":
        Y = np.asarray(Y, dtype=float)
        labels = np.asarray(labels)
        if set(labels.tolist()) != {0, 1}:
            raise MemoryLabError("training needs both classes")
        self.means = np.array([Y[labels == c].mean(axis=0) for c in (0, 1)])
        Xc = np.concatenate([Y[labels == c] - self.means[c] for c in (0, 1)])
        n, p = Xc.shape
        S = Xc.T @ Xc / n
        mu = np.trace(S) / p
        d2 = float(np.sum((S - mu * np.eye(p)) ** 2))
        # sum_k ||x_k x_k^T - S||_F^2 = sum_k (||x_k||^4 - 2 x_k^T S x_k) + n ||S||_F^2
        sq = np.einsum("ij,ij->i", Xc, Xc)
        quad = np.einsum("ij,jk,ik->i", Xc, S, Xc)
        b2_bar = float(np.sum(sq ** 2 - 2 * quad) + n * np.sum(S ** 2)) / n ** 2
        b2 = min(b2_bar, d2)
        self.shrinkage = 0.0 if d2 == 0 else b2 / d2
        self.cov = self.shrinkage * mu * np.eye(p) + (1 - self.shrinkage) * S
        self.w = np.linalg.solve(self.cov, self.means[1] - self.means[0])
        self.b = -0.5 * self.w @ (self.means[0] + self.means[1])
        return self

    def predict(self, Y: np.ndarray) -> np.ndarray:
        return np.where(np.asarray(Y, dtype=float) @ self.w + self.b > 0, 1, 0)


DECODERS = {"nearest_mean": NearestMeanDecoder, "lda_ledoit_wolf": LedoitWolfLDA}


def evaluate_level_d(z: np.ndarray, train: Episodes, test: Episodes, task: str) -> Dict[str, Optional[float]]:
    """Balanced accuracy per decoder. task 'preserve': labels = target class;
    'update': labels = last channel (X -> 0, Y -> 1), episodes without pulse excluded."""
    Ytr, Yte = observe(z, train), observe(z, test)
    if task == "preserve":
        ltr, lte, mtr, mte = train.target, test.target, np.ones(len(Ytr), bool), np.ones(len(Yte), bool)
    elif task == "update":
        mtr, mte = train.last > 0, test.last > 0
        ltr, lte = (train.last == 2).astype(int), (test.last == 2).astype(int)
    else:
        raise MemoryLabError("task must be preserve or update")
    out = {"n_train": int(mtr.sum()), "n_test": int(mte.sum()), "n_excluded_test": int((~mte).sum())}
    for name, cls in DECODERS.items():
        dec = cls().fit(Ytr[mtr], ltr[mtr])
        out[name] = balanced_accuracy(lte[mte], dec.predict(Yte[mte]))
    return out


__all__ = ["Episodes", "make_episodes", "observe", "check_class_independence", "check_split", "LedoitWolfLDA",
           "DECODERS", "evaluate_level_d"]
