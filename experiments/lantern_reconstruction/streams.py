"""LR3 random streams (plan section 11): explicit PCG64 generators from SeedSequence keys
(study_id, context_id, split_id, role_id, episode_id[, extra...]) with fixed numeric role IDs.

- never Python hash(), never the global RNG;
- one stream per (episode, role): results do not depend on batch size or execution order;
- train / val / test have different split IDs and therefore never share a stream;
- context-level streams (locations, frequencies, surrogate) use split_id 9 and episode_id 0.
"""
from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict

import numpy as np

HERE = Path(__file__).resolve().parent


DEFAULTS_FILE = HERE / "protocol" / "study_defaults.json"


def _freeze(x: Any) -> Any:
    if isinstance(x, dict):
        return MappingProxyType({k: _freeze(v) for k, v in x.items()})
    if isinstance(x, list):
        return tuple(_freeze(v) for v in x)
    return x


@lru_cache(maxsize=1)
def _loaded():
    from experiments.lantern_reconstruction.registry_adapter import strict_json

    raw = DEFAULTS_FILE.read_bytes().replace(b"\r\n", b"\n")
    return _freeze(strict_json(raw.decode("utf-8"))), hashlib.sha256(raw).hexdigest()


def defaults():
    """The study configuration as a deeply IMMUTABLE view (review REVIEW_LR3): in-memory changes
    cannot drift away from the stored protocol identity config_sha256()."""
    return _loaded()[0]


def config_sha256() -> str:
    """SHA-256 of the LF-normalised study_defaults.json the running code uses."""
    return _loaded()[1]


def roles() -> Dict[str, int]:
    return dict(defaults()["streams"]["roles"])


def splits() -> Dict[str, int]:
    return dict(defaults()["streams"]["splits"])


class StreamError(ValueError):
    pass


def check_index(x, what: str) -> int:
    """A non-negative TRUE integer (no bool, no float), checked before any conversion."""
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, (int, np.integer)) or x < 0:
        raise StreamError(f"{what} must be a non-negative integer (got {x!r})")
    return int(x)


def check_study_id(study_id) -> int:
    check_index(study_id, "study_id")
    ex = defaults()["streams"]["excluded_master_seeds"]
    if ex["from"] <= int(study_id) <= ex["to"]:
        raise StreamError(f"study_id {study_id} is an excluded development seed ({ex['reason']})")
    return int(study_id)


def key(study_id: int, context_id: int, split: str, role: str, episode: int = 0, *extra: int) -> tuple:
    r, s = roles(), splits()
    if role not in r or split not in s:
        raise StreamError(f"unknown role {role!r} or split {split!r}")
    return ((check_study_id(study_id), check_index(context_id, "context_id"), s[split], r[role], check_index(episode, "episode"))
            + tuple(check_index(e, "extra key component") for e in extra))


def generator(study_id: int, context_id: int, split: str, role: str, episode: int = 0, *extra: int) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(list(key(study_id, context_id, split, role, episode, *extra)))))
