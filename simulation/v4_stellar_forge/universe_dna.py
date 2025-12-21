"""DNA-like container for tunable cosmic constants.

This module encodes a compact set of knobs that define a universe's behavior.
Mutations perturb the constants slightly, letting descendant universes explore
nearby parameter space.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Tuple

import numpy as np


@dataclass(frozen=True)
class UniverseDNA:
    """Immutable bundle of simulation constants.

    Attributes
    ----------
    gravity_const:
        Scales gravitational attraction between particles.
    fusion_threshold:
        Characteristic radius for fusion clustering.
    entropy_rate:
        Rate at which compact objects evaporate, a proxy for entropy increase.
    """

    gravity_const: float = 0.05
    fusion_threshold: float = 0.5
    entropy_rate: float = 0.001
    mutation_scale: float = 0.05

    @property
    def gravity_strength(self) -> float:
        """Alias used by newer V4 multiverse components."""

        return self.gravity_const

    def mutate(self, rng: np.random.Generator | None = None) -> "UniverseDNA":
        """Return a mutated copy with constants jittered by up to ±5%.

        Parameters
        ----------
        rng:
            Optional random generator for reproducibility.
        """

        generator = rng or np.random.default_rng()

        def _jitter(value: float) -> float:
            factor = generator.uniform(1.0 - self.mutation_scale, 1.0 + self.mutation_scale)
            return float(value * factor)

        return UniverseDNA(
            gravity_const=_jitter(self.gravity_const),
            fusion_threshold=_jitter(self.fusion_threshold),
            entropy_rate=_jitter(self.entropy_rate),
            mutation_scale=self.mutation_scale,
        )

    def to_seed_token(self) -> str:
        """Serialize the DNA to a JSON string suitable for CLI handoff."""

        return json.dumps(asdict(self))

    @classmethod
    def from_seed_token(cls, token: str) -> Tuple["UniverseDNA" | None, int]:
        """Decode a seed token into DNA and RNG seed.

        The token can be either an integer seed or a JSON-encoded DNA payload.
        When JSON is supplied, a deterministic hash creates a reproducible RNG
        seed alongside the parsed DNA.
        """

        try:
            seed = int(token)
            return None, seed
        except ValueError:
            pass

        try:
            data = json.loads(token)
        except json.JSONDecodeError:
            hashed_seed = cls._hash_seed(token)
            return None, hashed_seed

        if not isinstance(data, dict):
            hashed_seed = cls._hash_seed(token)
            return None, hashed_seed

        required_keys = {"gravity_const", "fusion_threshold", "entropy_rate"}
        if not required_keys.issubset(data.keys()):
            hashed_seed = cls._hash_seed(token)
            return None, hashed_seed

        dna = cls(
            gravity_const=float(data["gravity_const"]),
            fusion_threshold=float(data["fusion_threshold"]),
            entropy_rate=float(data["entropy_rate"]),
            mutation_scale=float(data.get("mutation_scale", 0.05)),
        )
        rng_seed = cls._hash_seed(token)
        return dna, rng_seed

    @staticmethod
    def _hash_seed(token: str) -> int:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()[:8]
        return int(digest, 16)
