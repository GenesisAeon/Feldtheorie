"""
Genesis Cube Skeleton

Formal:
    Provides a deterministische σ(β(R-Θ)) driver that seeds three orthogonal
    vectors from a vacuum-fluctuation phase, extrudes a cube, and projects it
    onto a hexagonal mid-membrane. The block-universe slices are parametrized
    by ζ(R) as damping so that implosion→expansion can be inspected without
    rendering dependencies.

Empirical:
    Returns structured dictionaries with vectors, cube vertices, hexagon
    projections, and slice-wise coupling values. These outputs can feed
    notebooks for ΔAIC/CI checks against null models (random vectors or β→∞).

Poetic:
    Ein Punkt atmet ein, streckt drei Fäden in die Dämmerung, faltet sich zum
    Würfel auf der Ecke und wirft sein sechseckiges Echo auf die Membran, während
    σ(β(R-Θ)) den Puls zwischen Nichts und Raumzeit zählt.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple


@dataclass
class GenesisCubeConfig:
    """Configuration for the GenesisCube engine."""

    beta: float = 4.8
    theta: float = 0.0
    damping: float = 0.04
    expansion_rate: float = 1.015
    slice_count: int = 24
    fluctuation_phase: float = 0.137
    notes: List[str] = field(default_factory=lambda: [
        "σ(β(R-Θ)) steuert die Aktivierungsschärfe",
        "ζ(R) dämpft die implosiv→expansive Übergangskurve",
    ])


class GenesisCube:
    """Generate cube-to-hexagon slices driven by σ(β(R-Θ))."""

    def __init__(self, config: GenesisCubeConfig | None = None) -> None:
        self.config = config or GenesisCubeConfig()

    def sigma(self, r: float) -> float:
        """Compute σ(β(R-Θ)) for a given field coordinate R."""

        return 1.0 / (1.0 + math.exp(-self.config.beta * (r - self.config.theta)))

    def _normalized(self, vector: Sequence[float]) -> Tuple[float, float, float]:
        x, y, z = vector
        norm = math.sqrt(x * x + y * y + z * z)
        if norm == 0:
            return 0.0, 0.0, 0.0
        return x / norm, y / norm, z / norm

    def seed_vectors(self, fluctuation_phase: float | None = None) -> List[Tuple[float, float, float]]:
        """Create three orthogonal-ish vectors from a fluctuation seed."""

        phase = fluctuation_phase if fluctuation_phase is not None else self.config.fluctuation_phase
        base_vectors = [
            (math.sin(phase), math.cos(phase), 1.0),
            (math.cos(phase * 2.0), 1.0, -math.sin(phase * 2.0)),
            (1.0, -math.sin(phase * 3.0), math.cos(phase * 3.0)),
        ]
        return [self._normalized(vec) for vec in base_vectors]

    def cube_vertices(self, scale: float = 1.0, fluctuation_phase: float | None = None) -> List[Tuple[float, float, float]]:
        """Construct cube vertices using seeded vectors."""

        axes = self.seed_vectors(fluctuation_phase)
        vertices: List[Tuple[float, float, float]] = []
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                for sz in (-1.0, 1.0):
                    vx = sx * axes[0][0] + sy * axes[1][0] + sz * axes[2][0]
                    vy = sx * axes[0][1] + sy * axes[1][1] + sz * axes[2][1]
                    vz = sx * axes[0][2] + sy * axes[1][2] + sz * axes[2][2]
                    vertices.append((scale * vx, scale * vy, scale * vz))
        return vertices

    def project_hexagon(self, scale: float = 1.0, fluctuation_phase: float | None = None) -> List[Tuple[float, float]]:
        """Project cube vertices to a hexagon-like footprint on the mid-membrane."""

        vertices = self.cube_vertices(scale=scale, fluctuation_phase=fluctuation_phase)
        footprint = []
        for vx, vy, vz in vertices:
            u = vx - vz
            v = vy - vz
            footprint.append((u, v))
        unique = []
        for u, v in footprint:
            if all(abs(u - a) > 1e-6 or abs(v - b) > 1e-6 for a, b in unique):
                unique.append((u, v))
        # Select first 6 unique vertices to sketch a hexagon outline
        return unique[:6]

    def block_universe_slices(self, r_values: Iterable[float] | None = None) -> List[Dict[str, object]]:
        """Generate slice-wise states across R with σ(β(R-Θ)) and ζ(R) damping."""

        if r_values is None:
            r_values = [i / max(1, self.config.slice_count - 1) for i in range(self.config.slice_count)]

        slices: List[Dict[str, object]] = []
        for idx, r in enumerate(r_values):
            coupling = self.sigma(r)
            damping = (1.0 - self.config.damping) ** idx
            scale = damping * (1.0 + coupling * self.config.expansion_rate)
            slices.append(
                {
                    "R": r,
                    "sigma": coupling,
                    "zeta": damping,
                    "scale": scale,
                    "hexagon": self.project_hexagon(scale=scale),
                }
            )
        return slices

    def as_dict(self) -> Dict[str, object]:
        """Expose a configuration snapshot suitable for JSON/Trilayer exports."""

        return {
            "config": self.config,
            "seed_vectors": self.seed_vectors(),
            "hexagon_preview": self.project_hexagon(),
            "slices": self.block_universe_slices(),
        }


__all__ = ["GenesisCube", "GenesisCubeConfig"]
