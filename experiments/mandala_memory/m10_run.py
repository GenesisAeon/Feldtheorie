"""M10 runner: states, diagnostics (A1, A2 structural), level B (Bayes, MC) and
level D (trained decoders) for one mode.

Modes:
  dev       development conditions/seeds of the protocol (tests, tool checks,
            runtime check); not part of the study
  smoke     after the freeze: runtime and format only
  research  BLOCKED until FROZEN_PROTOCOL_SHA256 is set to the SHA-256 of the
            frozen protocol (freeze commit) and the protocol file matches it

Writes one result file exclusively (never overwrites), never on C:.

    python -m experiments.mandala_memory.m10_run --mode dev --out-dir D:/mandala/mandala-memory-results/m10/dev
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np

from experiments.mandala_memory.core import MemoryLabError, is_drive_c
from experiments.mandala_memory.data import stream
from experiments.mandala_memory import m10_bayes as mb
from experiments.mandala_memory import m10_decoders as md
from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory.runner import peak_rss_bytes, write_exclusive

FROZEN_PROTOCOL_SHA256: Optional[str] = None          # set in the freeze commit; until then no research run
SCHEMA = "mandala-memory-m10-result-v1"
NETWORKS = ("modular", "uniform")
NONLINEARITIES = ("tanh", "identity")


def _json_scalar(o):
    """numpy scalars -> Python scalars; anything else is a bug and raises."""
    if isinstance(o, (np.bool_, np.integer, np.floating)):
        return o.item()
    raise TypeError(f"not JSON serialisable: {type(o).__name__}")


def protocol_sha256(path: Path = mt.PROTOCOL) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def mode_settings(proto: Dict, mode: str) -> Dict:
    if mode == "research":
        if FROZEN_PROTOCOL_SHA256 is None:
            raise MemoryLabError("research run blocked: the M10 protocol is not frozen yet (FROZEN_PROTOCOL_SHA256 unset)")
        if protocol_sha256() != FROZEN_PROTOCOL_SHA256:
            raise MemoryLabError("research run blocked: protocol differs from the frozen protocol")
        return {"conditions": proto["conditions"], "seeds": proto["level_D"]["seeds"], "n_mc": proto["level_B"]["n_mc"],
                "bayes_seed": proto["level_B"]["streams"]["base_seed"],
                "n_train": proto["level_D"]["n_train_per_class"], "n_test": proto["level_D"]["n_test_per_class"]}
    if mode == "smoke":
        s = proto["smoke"]
        return {"conditions": proto["conditions"], "seeds": s["seeds"], "n_mc": s["n_mc"], "bayes_seed": s["bayes_base_seed"],
                "n_train": s["n_train_per_class"], "n_test": s["n_test_per_class"]}
    if mode == "dev":
        s = proto["development"]
        return {"conditions": s["conditions"], "seeds": s["seeds"], "n_mc": proto["level_B"]["n_mc"],
                "bayes_seed": s["bayes_base_seed"], "n_train": proto["level_D"]["n_train_per_class"],
                "n_test": proto["level_D"]["n_test_per_class"]}
    raise MemoryLabError("mode must be dev, smoke or research")


def compute_states(proto: Dict, conditions: Dict, delays: Iterable[int], pats) -> Dict:
    out = {}
    for net in NETWORKS:
        for nl in NONLINEARITIES:
            for cname, cond in conditions.items():
                spec = mt.network(proto, net, nl, cond)
                for d in delays:
                    out[(net, nl, cname, d)] = {"spec": spec, "z": mt.readout_states(spec, d, pats)}
    return out


def diagnostics(proto: Dict, states: Dict, conditions: Dict, pats) -> List[Dict]:
    rows = []
    tol1 = proto["diagnostics"]["A1"]["tol_rel"]
    tol2 = proto["diagnostics"]["A2_structural"]["tol"]
    for (net, nl, cname, d), st in states.items():
        cond = conditions[cname]
        if cond is None:
            continue
        perm = mt.swap_permutation(proto["network"]["N"], proto["networks"][net]["M"])
        fixed = mt.condition_is_p_fixed(perm, cond)
        a1 = mt.check_a1(st["spec"], perm, d, pats, tol1)
        row = {"network": net, "nonlinearity": nl, "condition": cname, "delay": d, "p_fixed": fixed,
               "A1": a1, "A1_expected": fixed, "A1_as_expected": a1["holds"] == fixed}
        if nl == "identity" and fixed:
            row["A2_structural"] = mt.check_a2_structural(st["z"], pats, perm, tol2)
        rows.append(row)
    return rows


def level_b(proto: Dict, states: Dict, conditions: Dict, pats, n_mc: int, base_seed: int) -> List[Dict]:
    sigma = proto["observation"]["sigma"]
    block = proto["level_B"]["block"]
    rows = []
    for (net, nl, cname, d), st in states.items():
        z = st["z"]
        row = {"network": net, "nonlinearity": nl, "condition": cname, "delay": d}
        if conditions[cname] is None:
            row["preserve"] = {"estimate": mb.k0_preserve_analytic(z[:, 0], sigma), "se": 0.0, "n": 0,
                               "estimator": "analytic Phi(||dz|| / 2 sigma)"}
            row["update"] = None                                            # N/A for K0
        else:
            for task, mix in (("preserve", mb.preserve_mixtures(z, pats)), ("update", mb.update_mixtures(z, pats))):
                rng, key = stream("m10bayes", base_seed, task, net, nl, cname, d)
                t0 = time.perf_counter()
                row[task] = {**mb.bayes_accuracy_mc(mix, sigma, n_mc, rng, block), "stream": list(key),
                             "seconds": time.perf_counter() - t0}
        rows.append(row)
    return rows


def level_d(proto: Dict, states: Dict, conditions: Dict, pats, seeds: List[int], delays: Iterable[int],
            n_train: int, n_test: int, mode: str = "m10") -> List[Dict]:
    sigma, N = proto["observation"]["sigma"], proto["network"]["N"]
    rows = []
    for seed in seeds:
        for d in delays:
            tr = md.make_episodes(mode, seed, "decoder_train", d, n_train, pats, N, sigma)
            te = md.make_episodes(mode, seed, "test", d, n_test, pats, N, sigma)
            checks = {**md.check_split(tr, te), **{f"train_{k}": v for k, v in md.check_class_independence(tr, len(pats)).items()},
                      **{f"test_{k}": v for k, v in md.check_class_independence(te, len(pats)).items()}}
            for net in NETWORKS:
                for nl in NONLINEARITIES:
                    for cname, cond in conditions.items():
                        z = states[(net, nl, cname, d)]["z"]
                        rows.append({"seed": seed, "delay": d, "network": net, "nonlinearity": nl, "condition": cname,
                                     "preserve": md.evaluate_level_d(z, tr, te, "preserve"),
                                     "update": None if cond is None else md.evaluate_level_d(z, tr, te, "update"),
                                     "checks": checks})
    return rows


def run(mode: str, out_dir: Path, *, delays: Optional[List[int]] = None, n_mc: Optional[int] = None,
        seeds: Optional[List[int]] = None, skip_level_d: bool = False, write: bool = True) -> Dict:
    """Overrides (delays, n_mc, seeds, skip_level_d) are allowed only outside 'research'
    and are recorded in the result."""
    if write and is_drive_c(out_dir):
        raise MemoryLabError("refusing to write on C:")
    proto = mt.load_protocol()
    st = mode_settings(proto, mode)
    overrides = {"delays": delays, "n_mc": n_mc, "seeds": seeds, "skip_level_d": skip_level_d}
    if mode == "research" and any(v not in (None, False) for v in overrides.values()):
        raise MemoryLabError("no overrides in the research mode")
    delays = delays or proto["delays"]["all"]
    n_mc = n_mc or st["n_mc"]
    seeds = seeds or st["seeds"]
    pats = mt.patterns()
    t0 = time.perf_counter()
    result = {"schema": SCHEMA, "mode": mode, "protocol_sha256": protocol_sha256(), "frozen_protocol_sha256": FROZEN_PROTOCOL_SHA256,
              "overrides": overrides, "delays": delays, "n_mc": n_mc, "seeds": seeds, "status": "running", "failures": [],
              "timing_s": {}}
    try:
        states = compute_states(proto, st["conditions"], delays, pats)
        result["timing_s"]["states"] = time.perf_counter() - t0
        t = time.perf_counter()
        result["diagnostics"] = diagnostics(proto, states, st["conditions"], pats)
        result["timing_s"]["diagnostics"] = time.perf_counter() - t
        t = time.perf_counter()
        result["level_B"] = level_b(proto, states, st["conditions"], pats, n_mc, st["bayes_seed"])
        result["timing_s"]["level_B"] = time.perf_counter() - t
        t = time.perf_counter()
        result["level_D"] = [] if skip_level_d else level_d(proto, states, st["conditions"], pats, seeds, delays,
                                                           st["n_train"], st["n_test"])
        result["timing_s"]["level_D"] = time.perf_counter() - t
        result["status"] = "complete"
    except Exception as e:                                   # logged, never silently repaired
        result["failures"].append(f"{type(e).__name__}: {e}")
        result["status"] = "failed"
    result["timing_s"]["total"] = time.perf_counter() - t0
    result["peak_rss_bytes"] = peak_rss_bytes()
    result["run_id"] = f"m10-{mode}-{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}"
    if write:
        Path(out_dir).resolve().mkdir(parents=True, exist_ok=True)
        path = Path(out_dir).resolve() / f"{result['run_id']}.json"
        write_exclusive(path, json.dumps(result, indent=1, allow_nan=False, default=_json_scalar) + "\n")
        result["output_path"] = str(path)
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=("dev", "smoke", "research"))
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--delays", type=int, nargs="*")
    ap.add_argument("--n-mc", type=int)
    ap.add_argument("--skip-level-d", action="store_true")
    a = ap.parse_args(argv)
    res = run(a.mode, a.out_dir, delays=a.delays, n_mc=a.n_mc, skip_level_d=a.skip_level_d)
    print(json.dumps({"run_id": res["run_id"], "status": res["status"], "failures": res["failures"],
                      "timing_s": res["timing_s"], "peak_rss_mib": (res["peak_rss_bytes"] or 0) / 2 ** 20,
                      "output": res.get("output_path")}, indent=1))
    return 0 if res["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
