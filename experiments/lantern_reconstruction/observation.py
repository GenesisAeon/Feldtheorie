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

from experiments.lantern_reconstruction.contexts import N, ContextSpec


@dataclass(frozen=True)
class ObservationSpec:
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


def check_observation(ctx: ContextSpec, spec: ObservationSpec) -> None:
    if spec.reference in spec.nodes or len(set(spec.nodes)) != len(spec.nodes):
        raise ValueError("reference must not be among the feature nodes; nodes must be unique")
    if spec.reference in ctx.write_nodes:
        raise ValueError("the reference node must be unwritten")
    if spec.task == "B":
        if set(spec.nodes) & set(ctx.write_nodes):
            raise ValueError("task B must not observe a write node")
        if tuple(spec.nodes) + (spec.reference,) != tuple(ctx.read_nodes):
            raise ValueError("task B must observe exactly the context's read nodes")
    if spec.task == "A" and len(spec.nodes) != N - 1:
        raise ValueError("task A observes all nodes")


def features(states: np.ndarray, eps: np.ndarray, spec: ObservationSpec) -> np.ndarray:
    """states, eps (n, 34) -> (n, 2m): [sin(d_1..d_m), cos(d_1..d_m)] with d_k = y_node_k - y_ref."""
    y = np.asarray(states) + np.asarray(eps)
    d = y[:, list(spec.nodes)] - y[:, [spec.reference]]
    return np.concatenate([np.sin(d), np.cos(d)], axis=1)
