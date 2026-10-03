"""M2: random streams, episodes, observation noise, splits and decoder.

RNG contract (protocol/startkonfiguration.json, "rng_contract"):
every random draw comes from a NAMED stream derived with
``numpy.random.SeedSequence`` from (mode, seed, purpose, ...). Smoke and
research use different mode codes, so their streams are disjoint even for
equal seeds. Observation noise is a function of the EPISODE (mode, seed,
role, delay, class, index) and NOT of the network condition: paired
conditions (e.g. frozen vs adapted network) therefore see exactly the same
exogenous test noise. Adaptation, decoder training and test noise use
separate streams.

Decoder: nearest class mean in the raw observation space (protocol:
``standardization: none``), deterministic tie-break to class 0 on exact
distance equality. ``predict`` never receives labels. This is a deliberate
deviation from SCF's NearestMeanDecoder, which always standardises (M0
finding 5).
"""
from __future__ import annotations

import zlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from experiments.mandala_memory.core import MemoryLabError

MODES = {"smoke": 1, "research": 2, "explore": 3, "test": 9}
ROLES = ("adapt_train", "decoder_train", "validation", "test")


def _code(name: str) -> int:
    return zlib.crc32(name.encode("utf-8"))


def stream(mode: str, seed: int, *names) -> Tuple[np.random.Generator, Tuple[int, ...]]:
    """Named generator plus its recorded derivation key."""
    if mode not in MODES:
        raise MemoryLabError(f"mode must be one of {tuple(MODES)}")
    key = (int(seed), MODES[mode]) + tuple(_code(str(n)) for n in names)
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(list(key)))), key


@dataclass(frozen=True)
class EpisodeSet:
    """Episodes of one role at one delay: ids, labels and observation noise."""

    role: str
    delay: int
    ids: Tuple[str, ...]
    labels: Tuple[int, ...]
    noise: np.ndarray          # (n_episodes, obs_dim), independent of the network condition
    derivation: Tuple[int, ...]


def make_episodes(mode: str, seed: int, role: str, delay: int, n_per_class: int, obs_dim: int,
                  sigma: float) -> EpisodeSet:
    if role not in ROLES:
        raise MemoryLabError(f"role must be one of {ROLES}")
    if n_per_class < 1 or obs_dim < 1 or not (sigma >= 0):
        raise MemoryLabError("n_per_class >= 1, obs_dim >= 1, sigma >= 0 required")
    rng, key = stream(mode, seed, "observation", role, delay, obs_dim)
    labels = tuple([0] * n_per_class + [1] * n_per_class)
    ids = tuple(f"{mode}:s{seed}:{role}:d{delay}:c{c}:{i}" for c in (0, 1) for i in range(n_per_class))
    noise = rng.normal(0.0, sigma, size=(2 * n_per_class, obs_dim)) if sigma > 0 else np.zeros((2 * n_per_class, obs_dim))
    return EpisodeSet(role, delay, ids, labels, noise, key)


def observe_episodes(states_by_class: Dict[int, np.ndarray], H: np.ndarray, eps: EpisodeSet) -> np.ndarray:
    """y = H x_(d+1) + epsilon for every episode; x depends only on the class
    (deterministic dynamics, no process noise), epsilon on the episode."""
    H = np.asarray(H, dtype=float)
    rows = [H @ np.asarray(states_by_class[c], dtype=float) for c in eps.labels]
    Y = np.array(rows) + eps.noise
    if Y.shape != eps.noise.shape:
        raise MemoryLabError("observation dimension does not match the episode noise")
    return Y


def assert_disjoint(*episode_sets: EpisodeSet) -> None:
    from scoped_correspondence.validation.modular_networks.decoders import check_split

    for i, a in enumerate(episode_sets):
        for b in episode_sets[i + 1:]:
            check_split(a.ids, b.ids)


class NearestMeanDecoder:
    """Nearest class mean, no standardisation, tie -> class 0."""

    def __init__(self):
        self.means: Optional[np.ndarray] = None   # (2, dim)

    def fit(self, Y, labels: Sequence[int]) -> "NearestMeanDecoder":
        Y = np.asarray(Y, dtype=float)
        labels = np.asarray(labels)
        if Y.ndim != 2 or len(Y) != len(labels) or not np.all(np.isfinite(Y)):
            raise MemoryLabError("training data must be a finite (n, dim) matrix with one label per row")
        if set(labels.tolist()) != {0, 1}:
            raise MemoryLabError("training needs both classes 0 and 1")
        self.means = np.array([Y[labels == c].mean(axis=0) for c in (0, 1)])
        return self

    def predict(self, Y) -> np.ndarray:
        if self.means is None:
            raise MemoryLabError("decoder is not fitted")
        Y = np.asarray(Y, dtype=float)
        if Y.ndim != 2 or Y.shape[1] != self.means.shape[1] or not np.all(np.isfinite(Y)):
            raise MemoryLabError("prediction input must be a finite (n, dim) matrix with the trained dimension")
        d0 = np.sum((Y - self.means[0]) ** 2, axis=1)
        d1 = np.sum((Y - self.means[1]) ** 2, axis=1)
        return np.where(d1 < d0, 1, 0)       # exact tie -> class 0

    def params(self) -> Dict[str, object]:
        return {"kind": "nearest_mean", "standardization": "none", "tie_break_class": 0,
                "n_parameters": None if self.means is None else int(self.means.size),
                "means": None if self.means is None else self.means.tolist()}


def balanced_accuracy(labels, predictions) -> float:
    from scoped_correspondence.validation.modular_networks.decoders import balanced_accuracy as scf_bacc

    return float(scf_bacc(list(map(int, labels)), list(map(int, predictions))))


def confusion(labels, predictions) -> List[List[int]]:
    m = [[0, 0], [0, 0]]
    for t, p in zip(labels, predictions):
        m[int(t)][int(p)] += 1
    return m


def sum_observation(N: int) -> np.ndarray:
    return np.ones((1, N))


def permutation_observation(N: int, perm: Sequence[int]) -> np.ndarray:
    perm = list(perm)
    if sorted(perm) != list(range(N)):
        raise MemoryLabError("perm must be a permutation of 0..N-1")
    return np.eye(N)[perm]


__all__ = ["MODES", "ROLES", "stream", "EpisodeSet", "make_episodes", "observe_episodes", "assert_disjoint",
           "NearestMeanDecoder", "balanced_accuracy", "confusion", "sum_observation", "permutation_observation"]
