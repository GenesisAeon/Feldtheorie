"""LR3 context specification (plan sections 6, 11): a context = frequencies + location permutation
(+ its surrogate draw and all learning random sources). Same registry matrix for all contexts;
contexts are NOT different network architectures (plan 3.2, point 3)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from experiments.lantern_reconstruction import streams

N = 34


@dataclass(frozen=True)
class ContextSpec:
    study_id: int
    context_id: int
    permutation: Tuple[int, ...]          # of the canonically sorted node indices
    write_pairs: Tuple[Tuple[int, int], ...]
    read_nodes: Tuple[int, ...]           # 9 nodes, the last one is the reference
    reference: int
    omega: Tuple[float, ...]

    @property
    def write_nodes(self) -> Tuple[int, ...]:
        return tuple(i for p in self.write_pairs for i in p)

    def omega_array(self) -> np.ndarray:
        a = np.array(self.omega, dtype=np.float64)
        a.setflags(write=False)
        return a


def make_context(study_id: int, context_id: int) -> ContextSpec:
    perm = streams.generator(study_id, context_id, "context", "locations").permutation(N)
    om = streams.generator(study_id, context_id, "context", "frequencies").normal(0.0, 0.1, N)
    om = om - om.mean()
    pairs = tuple((int(perm[2 * k]), int(perm[2 * k + 1])) for k in range(4))
    read = tuple(int(i) for i in perm[8:17])
    ctx = ContextSpec(study_id, context_id, tuple(int(i) for i in perm), pairs, read, read[-1], tuple(float(x) for x in om))
    check_context(ctx)
    return ctx


def check_context(ctx: ContextSpec) -> None:
    if sorted(ctx.permutation) != list(range(N)):
        raise ValueError("permutation must cover all 34 nodes once")
    w, r = set(ctx.write_nodes), set(ctx.read_nodes)
    if len(w) != 8 or len(r) != 9 or w & r or ctx.reference not in r or ctx.reference in w:
        raise ValueError("write and read sets must be disjoint; the reference is an unwritten read node")
    if len(ctx.omega) != N or not np.all(np.isfinite(ctx.omega)) or abs(sum(ctx.omega)) > 1e-12:
        raise ValueError("omega must be 34 finite, centred values")
