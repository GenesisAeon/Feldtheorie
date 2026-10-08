"""LR3 context specification (plan sections 6, 11): a context = frequencies + location permutation
(+ its surrogate draw and all learning random sources). Same registry matrix for all contexts;
contexts are NOT different network architectures (plan 3.2, point 3)."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
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


def _true_int(x) -> bool:
    return isinstance(x, (int, np.integer)) and not isinstance(x, (bool, np.bool_))


def check_context(ctx: ContextSpec) -> None:
    """Structural validation (review REVIEW_LR3 R2): true integers in range, exactly four disjoint
    pairs, write/read/reference consistent with the STORED permutation, finite centred omega."""
    streams.check_study_id(ctx.study_id)
    streams.check_index(ctx.context_id, "context_id")
    perm = ctx.permutation
    if not isinstance(perm, tuple) or len(perm) != N or not all(_true_int(i) for i in perm) or sorted(perm) != list(range(N)):
        raise ValueError("permutation must be a tuple of the 34 node indices, each once")
    if (not isinstance(ctx.write_pairs, tuple) or len(ctx.write_pairs) != 4
            or not all(isinstance(p, tuple) and len(p) == 2 and all(_true_int(i) for i in p) for p in ctx.write_pairs)):
        raise ValueError("write_pairs must be exactly four pairs of integer node indices")
    if ctx.write_pairs != tuple((perm[2 * k], perm[2 * k + 1]) for k in range(4)):
        raise ValueError("write pairs must be the first eight entries of the stored permutation")
    if not isinstance(ctx.read_nodes, tuple) or ctx.read_nodes != tuple(perm[8:17]) or not _true_int(ctx.reference) or ctx.reference != ctx.read_nodes[-1]:
        raise ValueError("read nodes/reference must follow the stored permutation (reference = last read node)")
    w, r = set(ctx.write_nodes), set(ctx.read_nodes)
    if len(w) != 8 or len(r) != 9 or w & r or ctx.reference not in r or ctx.reference in w:
        raise ValueError("write and read sets must be disjoint; the reference is an unwritten read node")
    om = ctx.omega
    if (not isinstance(om, tuple) or len(om) != N or any(isinstance(x, (bool, np.bool_)) for x in om)
            or not np.all(np.isfinite(np.asarray(om, dtype=np.float64))) or abs(sum(om)) > 1e-12):
        raise ValueError("omega must be 34 finite, centred values")


def fingerprint(ctx: ContextSpec) -> str:
    """Identity of a context (all fields incl. the exact omega bits)."""
    d = asdict(ctx)
    d["omega"] = [float(x).hex() for x in ctx.omega]
    return hashlib.sha256(json.dumps(d, sort_keys=True).encode("utf-8")).hexdigest()
