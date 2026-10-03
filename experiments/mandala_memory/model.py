"""M3: frozen and adapted networks, ablation conditions (IMPLEMENTIERUNGSPLAN.md §4-§5).

Adaptation (protocol "adaptation"): ``trials_total`` balanced training
episodes in random order (own named stream "adaptation"), each episode a
pulse step plus ``delay_steps`` zero steps from x0 = 0. The lagged activity
pairs (x_k, x_(k+1)) of one episode feed ONE call of SCF ``hebb_update``
(eta, fixed edge mask, renormalisation to gamma). Weights are frozen
afterwards; no test label and no test episode ever touches A.

This episodic training is a NEW protocol, not a repetition of the old ON
benchmark (which used SCF ``adapt`` with constant input).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Dict, List

import numpy as np

from experiments.mandala_memory.core import (
    EpisodeOperator,
    MemoryLabError,
    NetworkSpec,
    build_network,
    pulse_delay_inputs,
)
from experiments.mandala_memory.data import stream


@dataclass(frozen=True)
class AdaptationRecord:
    order: tuple            # class sequence actually used
    derivation: tuple       # stream key
    n_updates: int
    steps_per_episode: int
    eta: float
    weight_change_fro: float
    weight_change_max: float
    row_sums_after: tuple
    masked_entries_zero: bool
    inter_fraction_after_mean: float


def network_from_config(net_cfg: Dict, **overrides) -> NetworkSpec:
    p = dict(N=net_cfg["N"], M=net_cfg["M"], c=net_cfg["c"], gamma=net_cfg["gamma"], ell=net_cfg["ell"],
             inputs=tuple(net_cfg["inputs_zero_based"]), amplitude=net_cfg["B_amplitude"])
    p.update(overrides)
    return build_network(**p)


def adapt_network(spec: NetworkSpec, adaptation_cfg: Dict, *, mode: str, seed: int) -> (NetworkSpec, AdaptationRecord):
    """Episodic Hebb training on separate adaptation episodes; returns a NEW
    frozen spec (the input spec is not modified)."""
    from scoped_correspondence.validation.modular_networks.adaptive_model import hebb_update, inter_fraction

    if adaptation_cfg.get("update_on") != "training_only":
        raise MemoryLabError("adaptation must be declared training_only")
    n = int(adaptation_cfg["trials_total"])
    if n % 2 or n < 2:
        raise MemoryLabError("balanced adaptation needs an even number of episodes")
    steps = int(adaptation_cfg["delay_steps"])
    eta = float(adaptation_cfg["eta"])
    gamma = float(spec.meta["gamma"])
    rng, key = stream(mode, seed, "adaptation")
    order = np.array([0] * (n // 2) + [1] * (n // 2))
    rng.shuffle(order)
    A = spec.A.copy()
    mask = spec.mask.tolist()
    for s in order:
        op = EpisodeOperator(replace(spec, A=A))
        op.reset()
        traj = op.run(pulse_delay_inputs(int(s), steps))
        pairs = [(traj[k].tolist(), traj[k + 1].tolist()) for k in range(len(traj) - 1)]
        A = np.array(hebb_update(A.tolist(), pairs, mask, eta, gamma), dtype=float)
    dA = A - spec.A
    masked_zero = bool(np.all(A[np.array(mask) == 0] == 0))
    inter = inter_fraction(A.tolist(), spec.module_of)
    new = replace(spec, A=A, name=spec.name + "_hebb", meta={**spec.meta, "adapted": True})
    rec = AdaptationRecord(tuple(int(s) for s in order), key, n, steps + 1, eta, float(np.linalg.norm(dA)),
                           float(np.max(np.abs(dA))), tuple(float(v) for v in A.sum(axis=1)), masked_zero,
                           float(np.mean([v for v in inter if v is not None])))
    return new, rec


def condition_specs(net_cfg: Dict) -> Dict[str, NetworkSpec]:
    """Frozen (pre-adaptation) condition networks; the adapted one is derived per seed."""
    return {
        "frozen": network_from_config(net_cfg, name="frozen"),
        "uncoupled_leak": network_from_config(net_cfg, coupling=False, name="uncoupled_leak"),
        "linear": network_from_config(net_cfg, nonlinearity="identity", name="linear"),
        "uniform_M1": network_from_config(net_cfg, M=1, name="uniform_M1"),
        "renamed_M3_c8_11": network_from_config(net_cfg, M=3, c=Fraction(8, 11), name="renamed_M3_c8_11"),
    }


def resources(spec: NetworkSpec) -> Dict[str, object]:
    A = spec.A
    return {"N": spec.N, "edges_allowed": int(spec.mask.sum()) if spec.mask is not None else None,
            "edges_nonzero": int(np.count_nonzero(A)), "row_sums": [round(float(v), 12) for v in A.sum(axis=1)],
            "nonlinearity": spec.nonlinearity, "coupling_budget_total": round(float(A.sum()), 12)}


__all__ = ["AdaptationRecord", "network_from_config", "adapt_network", "condition_specs", "resources"]
