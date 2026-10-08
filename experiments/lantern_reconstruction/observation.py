"""LR3 observation (plan 5.1, 6, 10, 11): noisy snapshot theta + eps, features sin/cos of the
differences of the allowed nodes to the reference node, in a fixed order.

Task A: all 34 nodes (33 differences to the context's reference -> 66 features).
Task B: the 8 unwritten read nodes and the unwritten reference (8 differences -> 16 features).
B never contains a write coordinate, a written reference or any aggregate of write nodes
(checked structurally by check_observation). Measurement errors eps are addressed per episode,
node and readout time and are the SAME for both tasks on common nodes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from experiments.lantern_reconstruction.contexts import N, ContextSpec, _true_int, check_context

TASKS = ("A", "B")


@dataclass(frozen=True)
class ObservationSpec:
    """A plain record: constructing one does NOT make it valid. Research code obtains specs via
    observation_spec() and features via observe(), which both validate against the context
    (follow-up review LANTERN_LR3_NACHREVIEW F1)."""
    task: str
    nodes: Tuple[int, ...]       # non-reference nodes, fixed feature order
    reference: int

    @property
    def n_features(self) -> int:
        return 2 * len(self.nodes)


def observation_spec(ctx: ContextSpec, task: str) -> ObservationSpec:
    if task == "A":
        spec = ObservationSpec("A", tuple(i for i in range(N) if i != ctx.reference), ctx.reference)
    elif task == "B":
        spec = ObservationSpec("B", tuple(ctx.read_nodes[:-1]), ctx.reference)
    else:
        raise ValueError("task must be 'A' or 'B'")
    check_observation(ctx, spec)
    return spec


def _check_spec_indices(spec: ObservationSpec) -> None:
    """Context-free part (review F1): known task; every index a TRUE integer (no bool, no float, no
    int() conversion) with 0 <= index < 34 -- negative NumPy indices would silently alias nodes."""
    if not isinstance(spec.task, str) or spec.task not in TASKS:
        raise ValueError(f"task must be exactly 'A' or 'B' (got {spec.task!r})")
    if not isinstance(spec.nodes, tuple) or not all(_true_int(i) and 0 <= i < N for i in spec.nodes):
        raise ValueError("feature nodes must be a tuple of integer node indices in [0, 34)")
    if not (_true_int(spec.reference) and 0 <= spec.reference < N):
        raise ValueError("the reference must be an integer node index in [0, 34)")


def check_observation(ctx: ContextSpec, spec: ObservationSpec) -> None:
    """Full validation against the context (review F1): valid context, known task, true in-range
    indices, the context's own unwritten reference and EXACTLY the factory's node order."""
    check_context(ctx)
    _check_spec_indices(spec)
    if spec.reference in spec.nodes or len(set(spec.nodes)) != len(spec.nodes):
        raise ValueError("reference must not be among the feature nodes; nodes must be unique")
    if spec.reference in ctx.write_nodes:
        raise ValueError("the reference node must be unwritten")
    if spec.reference != ctx.reference:
        raise ValueError("the reference must be the context's reference node")
    if spec.task == "B":
        if set(spec.nodes) & set(ctx.write_nodes):
            raise ValueError("task B must not observe a write node")
        if tuple(spec.nodes) + (spec.reference,) != tuple(ctx.read_nodes):
            raise ValueError("task B must observe exactly the context's read nodes")
    if spec.task == "A" and tuple(spec.nodes) != tuple(i for i in range(N) if i != ctx.reference):
        raise ValueError("task A observes all nodes (every non-reference node, ascending order)")


def _check_array(x, what: str) -> np.ndarray:
    """Real, finite (n, 34) array with n >= 1. Allowed dtypes: NumPy integer (not bool) and real
    floating types; bool, complex and object arrays are rejected before any arithmetic."""
    a = np.asarray(x)
    if a.dtype.kind not in "iuf":
        raise ValueError(f"{what} must be a real numeric array (got dtype {a.dtype})")
    if a.ndim != 2 or a.shape[0] < 1 or a.shape[1] != N:
        raise ValueError(f"{what} must have shape (n, 34) with n >= 1 (got {a.shape})")
    if not np.all(np.isfinite(a)):
        raise ValueError(f"{what} must be finite")
    return a


def features(states: np.ndarray, eps: np.ndarray, spec: ObservationSpec) -> np.ndarray:
    """states, eps (n, 34) -> (n, 2m): [sin(d_1..d_m), cos(d_1..d_m)] with d_k = y_node_k - y_ref.

    Context-free kernel. Review F2: both arrays must have the SAME (n, 34) shape -- no implicit
    broadcasting (a (n, 1) noise would cancel exactly in the reference differences) and no NaN/inf.
    Task and indices of the spec are checked here, its consistency with a context only in observe()."""
    _check_spec_indices(spec)
    s, e = _check_array(states, "states"), _check_array(eps, "eps")
    if s.shape != e.shape:
        raise ValueError(f"states {s.shape} and eps {e.shape} must have the same shape (no broadcasting)")
    y = s + e
    d = y[:, list(spec.nodes)] - y[:, [spec.reference]]
    return np.concatenate([np.sin(d), np.cos(d)], axis=1)


def observe(ctx: ContextSpec, spec: ObservationSpec, states: np.ndarray, eps: np.ndarray) -> np.ndarray:
    """Validated research entry point (review F1/F2): context + spec, then the checked kernel.
    LR4 obtains its features only through this function."""
    check_observation(ctx, spec)
    return features(states, eps, spec)
