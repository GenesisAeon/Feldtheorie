"""M5: separate pilot with Feldtheorie's AdaptiveLogisticMembrane (plan §7).

Its theta/beta semantics are NOT changed. The membrane's internal
parameters are themselves state: resetting only the visible output does
not remove their memory. One fresh instance per independent episode; a
continuation uses the very same instance.

Task (a different task from the network benchmark -- no model contest):
amplitude stimulus R = 0.2 (class 0) vs R = 0.8 (class 1) for one step,
pause R = 0 for d steps, then a PROBE R = 0.5 (its own, logged
intervention). Because ``propagate`` updates first and outputs afterwards,
both are reported: the response the probe would give with the state
before the probe ("pre_probe_sigma") and the returned post-update output
("post_probe_sigma"). Adaptive vs frozen membrane (all plasticity and
relaxation gains 0, so theta/beta constant).

Pilot assumptions not fixed by the plan, documented here: theta0 = 0.5,
beta0 = 6.0, all other membrane parameters at their defaults, dt = 1,
observation noise sigma = 0.02 on the probe output as in the main protocol.

Loader: the single file ``models/adaptive_logistic_membrane.py`` is loaded
by path, because ``import models...`` executes ``models/__init__.py``,
which imports the whole Feldtheorie model package (about 2.9 s, unrelated
solvers). Smallest adapter; Feldtheorie itself is not modified.
"""
from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict

import numpy as np

from experiments.mandala_memory.data import NearestMeanDecoder, balanced_accuracy, make_episodes

REPO = Path(__file__).resolve().parents[2]
CLASS_AMPLITUDES = {0: 0.2, 1: 0.8}
PROBE_R = 0.5
PILOT = {"theta0": 0.5, "beta0": 6.0, "dt": 1.0, "sigma": 0.02}
FROZEN_GAINS = dict(plasticity=0.0, relaxation=0.0, beta_plasticity=0.0, beta_relaxation=0.0,
                    impedance_tilt=0.0, sigma_weight=0.0)


@lru_cache(maxsize=1)
def membrane_class():
    path = REPO / "models" / "adaptive_logistic_membrane.py"
    name = "feldtheorie_adaptive_logistic_membrane"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod      # dataclasses with postponed annotations look the module up here
    spec.loader.exec_module(mod)
    return mod.AdaptiveLogisticMembrane


def new_membrane(frozen: bool = False):
    cls = membrane_class()
    return cls(theta=PILOT["theta0"], beta=PILOT["beta0"], **(FROZEN_GAINS if frozen else {}))


def logistic(r: float, theta: float, beta: float) -> float:
    return float(1.0 / (1.0 + np.exp(-beta * (r - theta))))


def episode(s: int, d: int, *, frozen: bool = False, membrane=None) -> Dict[str, float]:
    """One episode on a FRESH instance unless ``membrane`` is given (continuation)."""
    m = membrane if membrane is not None else new_membrane(frozen)
    m.propagate([CLASS_AMPLITUDES[s]] + [0.0] * d, dt=PILOT["dt"])
    theta_pre, beta_pre = float(m.theta), float(m.beta)
    pre = logistic(PROBE_R, theta_pre, beta_pre)
    out = m.propagate([PROBE_R], dt=PILOT["dt"])
    return {"theta_before_probe": theta_pre, "beta_before_probe": beta_pre, "pre_probe_sigma": pre,
            "post_probe_sigma": float(out["sigma"][-1]), "theta_after_probe": float(m.theta), "beta_after_probe": float(m.beta)}


def run_pilot(delays=(0, 1, 2, 4, 8, 16, 32), seeds=(2026100300, 2026100301, 2026100302), n_per_class=40,
              mode: str = "smoke") -> Dict:
    rows = {"adaptive": {}, "frozen": {}}
    for variant in rows:
        frozen = variant == "frozen"
        for d in delays:
            st = {c: episode(c, d, frozen=frozen) for c in (0, 1)}
            per_seed = []
            for seed in seeds:
                obs = {}
                for key in ("pre_probe_sigma", "post_probe_sigma"):
                    tr = make_episodes(mode, seed, "decoder_train", 1000 + d, n_per_class, 1, PILOT["sigma"])
                    te = make_episodes(mode, seed, "test", 1000 + d, n_per_class, 1, PILOT["sigma"])
                    Ytr = np.array([[st[c][key]] for c in tr.labels]) + tr.noise
                    Yte = np.array([[st[c][key]] for c in te.labels]) + te.noise
                    dec = NearestMeanDecoder().fit(Ytr, tr.labels)
                    obs[key] = balanced_accuracy(te.labels, dec.predict(Yte))
                per_seed.append(obs)
            rows[variant][str(d)] = {
                "theta_before_probe": [st[c]["theta_before_probe"] for c in (0, 1)],
                "beta_before_probe": [st[c]["beta_before_probe"] for c in (0, 1)],
                "pre_probe_sigma": [st[c]["pre_probe_sigma"] for c in (0, 1)],
                "post_probe_sigma": [st[c]["post_probe_sigma"] for c in (0, 1)],
                "probe_output_difference": abs(st[1]["post_probe_sigma"] - st[0]["post_probe_sigma"]),
                "balanced_accuracy_per_seed": per_seed,
            }
    return {"schema": "mandala-memory-membrane-pilot-v1", "task": "amplitude 0.2 vs 0.8, pause R = 0, probe R = 0.5",
            "assumptions": PILOT, "frozen_gains": FROZEN_GAINS, "delays": list(delays), "seeds": list(seeds),
            "n_per_class": n_per_class, "evidence_kind": "numerical_sample", "empirical_status": "synthetic_only",
            "note": "separate task; not comparable with the two-input network benchmark (no model contest)",
            "results": rows}


__all__ = ["membrane_class", "new_membrane", "episode", "run_pilot", "CLASS_AMPLITUDES", "PROBE_R", "PILOT", "FROZEN_GAINS"]
