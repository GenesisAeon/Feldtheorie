"""LR3 random streams (plan section 11): explicit PCG64 generators from SeedSequence keys
(study_id, context_id, split_id, role_id, episode_id[, extra...]) with fixed numeric role IDs.

- never Python hash(), never the global RNG;
- one stream per (episode, role): results do not depend on batch size or execution order;
- train / val / test have different split IDs and therefore never share a stream;
- context-level streams (locations, frequencies, surrogate) use split_id 9 and episode_id 0.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict

import numpy as np

HERE = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def defaults() -> dict:
    from experiments.lantern_reconstruction.registry_adapter import strict_json

    return strict_json((HERE / "protocol" / "study_defaults.json").read_text(encoding="utf-8"))


def roles() -> Dict[str, int]:
    return dict(defaults()["streams"]["roles"])


def splits() -> Dict[str, int]:
    return dict(defaults()["streams"]["splits"])


class StreamError(ValueError):
    pass


def check_study_id(study_id) -> int:
    if isinstance(study_id, bool) or not isinstance(study_id, (int, np.integer)) or study_id < 0:
        raise StreamError("study_id must be a non-negative integer")
    ex = defaults()["streams"]["excluded_master_seeds"]
    if ex["from"] <= int(study_id) <= ex["to"]:
        raise StreamError(f"study_id {study_id} is an excluded development seed ({ex['reason']})")
    return int(study_id)


def key(study_id: int, context_id: int, split: str, role: str, episode: int = 0, *extra: int) -> tuple:
    r, s = roles(), splits()
    if role not in r or split not in s:
        raise StreamError(f"unknown role {role!r} or split {split!r}")
    parts = (check_study_id(study_id), int(context_id), s[split], r[role], int(episode)) + tuple(int(e) for e in extra)
    if any(p < 0 for p in parts):
        raise StreamError("stream key components must be non-negative")
    return parts


def generator(study_id: int, context_id: int, split: str, role: str, episode: int = 0, *extra: int) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(list(key(study_id, context_id, split, role, episode, *extra)))))
