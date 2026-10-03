"""M10 runner: states, diagnostics (A1, A2 structural), level B (Bayes, MC) and
level D (trained decoders) for one mode.

Modes:
  dev       development conditions/seeds of the protocol (tests, tool checks,
            runtime check); not part of the study; allowed before the freeze
  smoke     runtime/format check with the research conditions -- AFTER the freeze only
  research  the study -- AFTER the freeze only
Both smoke and research require a valid freeze (review R11): FROZEN_PROTOCOL_SHA256
set and equal to the protocol file, and the freeze record protocol/m10_freeze.json
naming the same protocol hash, the reviewed code commit and the SHA-256 of every
M10 code file, which must match the files on disk.

Controls are ENFORCED (review R10): a failed leak or split check, or a
deterministic diagnostic (A1, A2 structural) that is not as expected, ends the run
with status "failed". Statistical 4-SE alarms are evaluated and only REPORTED by
m10_evaluate (protocol alarm policy).

Time budget (review R12): elapsed wall-clock time of run() (time.monotonic),
protocol resources.time_limit. It is checked COOPERATIVELY before every state
computation, every diagnostic unit, every Monte Carlo block and every level-D unit,
and once more immediately before the run is declared complete; on exceeding it the
run stops with status "aborted_timeout" and the partial result is still written
exclusively. The overshoot is therefore at most the duration of one unit; the
measured duration of an MC block (about 0.16 s) is an observation, not a guaranteed
bound.

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
from typing import Callable, Dict, Iterable, List, Optional

import numpy as np

from experiments.mandala_memory.core import MemoryLabError, is_drive_c
from experiments.mandala_memory.data import stream
from experiments.mandala_memory import m10_bayes as mb
from experiments.mandala_memory import m10_decoders as md
from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory.runner import peak_rss_bytes, write_exclusive

# Freeze 2026-10-03: the ONLY code change of the freeze commit relative to the reviewed commit
# 6f2acfd2a8a153c8f48bc50194cbcf651a510758 (final review ABSCHLUSSPRUEFUNG_6f2acfd.md). The code hashes in
# protocol/m10_freeze.json were computed AFTER this line was set.
FROZEN_PROTOCOL_SHA256: Optional[str] = "84d2b523d5f4c7dc9acc8e91d1986d71306e9aedbd4f99ef74c35c5b2056c345"
FREEZE_RECORD = mt.HERE / "protocol" / "m10_freeze.json"
CODE_FILES = ("m10_task.py", "m10_bayes.py", "m10_decoders.py", "m10_run.py", "m10_evaluate.py", "data.py", "core.py",
              "predict.py")
SCHEMA = "mandala-memory-m10-result-v1"
NETWORKS = ("modular", "uniform")
NONLINEARITIES = ("tanh", "identity")
clock: Callable[[], float] = time.monotonic           # replaceable in tests (controlled clock)


class RunTimeout(MemoryLabError):
    """The run exceeded the protocol time limit."""


class ControlFailure(MemoryLabError):
    """A deterministic control (leak, split, A1, A2 structural) failed."""


def _json_scalar(o):
    """numpy scalars -> Python scalars; anything else is a bug and raises."""
    if isinstance(o, (np.bool_, np.integer, np.floating)):
        return o.item()
    raise TypeError(f"not JSON serialisable: {type(o).__name__}")


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def protocol_sha256(path: Path = mt.PROTOCOL) -> str:
    return _sha(path)


def code_sha256() -> Dict[str, str]:
    return {f: _sha(mt.HERE / f) for f in CODE_FILES}


def require_frozen(mode: str) -> Dict:
    """Valid freeze for smoke and research (review R11), including the code hashes."""
    if FROZEN_PROTOCOL_SHA256 is None:
        raise MemoryLabError(f"{mode} run blocked: the M10 protocol is not frozen yet (FROZEN_PROTOCOL_SHA256 unset)")
    if protocol_sha256() != FROZEN_PROTOCOL_SHA256:
        raise MemoryLabError(f"{mode} run blocked: protocol differs from the frozen protocol")
    if not FREEZE_RECORD.is_file():
        raise MemoryLabError(f"{mode} run blocked: freeze record {FREEZE_RECORD.name} missing")
    rec = json.loads(FREEZE_RECORD.read_text(encoding="utf-8"))
    if rec.get("protocol_sha256") != FROZEN_PROTOCOL_SHA256 or not rec.get("reviewed_code_commit"):
        raise MemoryLabError(f"{mode} run blocked: freeze record does not match the frozen protocol")
    if rec.get("code_sha256") != code_sha256():
        raise MemoryLabError(f"{mode} run blocked: M10 code differs from the frozen code")
    return rec


def mode_settings(proto: Dict, mode: str) -> Dict:
    if mode == "research":
        require_frozen(mode)
        return {"conditions": proto["conditions"], "seeds": proto["level_D"]["seeds"], "n_mc": proto["level_B"]["n_mc"],
                "bayes_seed": proto["level_B"]["streams"]["base_seed"],
                "n_train": proto["level_D"]["n_train_per_class"], "n_test": proto["level_D"]["n_test_per_class"]}
    if mode == "smoke":
        require_frozen(mode)
        s = proto["smoke"]
        return {"conditions": proto["conditions"], "seeds": s["seeds"], "n_mc": s["n_mc"], "bayes_seed": s["bayes_base_seed"],
                "n_train": s["n_train_per_class"], "n_test": s["n_test_per_class"]}
    if mode == "dev":
        s = proto["development"]
        return {"conditions": s["conditions"], "seeds": s["seeds"], "n_mc": proto["level_B"]["n_mc"],
                "bayes_seed": s["bayes_base_seed"], "n_train": proto["level_D"]["n_train_per_class"],
                "n_test": proto["level_D"]["n_test_per_class"]}
    raise MemoryLabError("mode must be dev, smoke or research")


def make_deadline(limit_s: float) -> Callable[[], None]:
    start = clock()

    def deadline() -> None:
        if clock() - start > limit_s:
            raise RunTimeout(f"time limit of {limit_s} s exceeded")
    return deadline


def compute_states(proto: Dict, conditions: Dict, delays: Iterable[int], pats, deadline=None) -> Dict:
    out = {}
    for net in NETWORKS:
        for nl in NONLINEARITIES:
            for cname, cond in conditions.items():
                spec = mt.network(proto, net, nl, cond)
                for d in delays:
                    if deadline:
                        deadline()
                    out[(net, nl, cname, d)] = {"spec": spec, "z": mt.readout_states(spec, d, pats)}
    return out


def diagnostics(proto: Dict, states: Dict, conditions: Dict, pats, deadline=None) -> List[Dict]:
    rows = []
    tol1 = proto["diagnostics"]["A1"]["tol_rel"]
    tol2 = proto["diagnostics"]["A2_structural"]["tol"]
    for (net, nl, cname, d), st in states.items():
        cond = conditions[cname]
        if cond is None:
            continue
        if deadline:
            deadline()
        perm = mt.swap_permutation(proto["network"]["N"], proto["networks"][net]["M"])
        fixed = mt.condition_is_p_fixed(perm, cond)
        a1 = mt.check_a1(st["spec"], perm, d, pats, tol1)
        row = {"network": net, "nonlinearity": nl, "condition": cname, "delay": d, "p_fixed": fixed,
               "A1": a1, "A1_expected": fixed, "A1_as_expected": bool(a1["holds"] == fixed)}
        if nl == "identity" and fixed:
            row["A2_structural"] = mt.check_a2_structural(st["z"], pats, perm, tol2)
        rows.append(row)
    return rows


def enforce_diagnostics(rows: List[Dict]) -> None:
    """Deterministic controls must be as expected (the expected negative A1 control
    N/modular counts as 'as expected'); otherwise the run fails (review R10)."""
    bad = [f"A1 {r['network']}/{r['nonlinearity']}/{r['condition']}/d{r['delay']}" for r in rows if not r["A1_as_expected"]]
    bad += [f"A2 {r['network']}/{r['condition']}/d{r['delay']}" for r in rows
            if "A2_structural" in r and not r["A2_structural"]["holds"]]
    if bad:
        raise ControlFailure("deterministic control failed: " + ", ".join(bad))


def level_b(proto: Dict, states: Dict, conditions: Dict, pats, n_mc: int, base_seed: int, deadline=None) -> List[Dict]:
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
                row[task] = {**mb.bayes_accuracy_mc(mix, sigma, n_mc, rng, block, deadline=deadline), "stream": list(key),
                             "seconds": time.perf_counter() - t0}
        rows.append(row)
    return rows


def level_d(proto: Dict, states: Dict, conditions: Dict, pats, seeds: List[int], delays: Iterable[int],
            n_train: int, n_test: int, mode: str = "m10", deadline=None) -> List[Dict]:
    sigma, N = proto["observation"]["sigma"], proto["network"]["N"]
    rows = []
    for seed in seeds:
        for d in delays:
            tr = md.make_episodes(mode, seed, "decoder_train", d, n_train, pats, N, sigma)
            te = md.make_episodes(mode, seed, "test", d, n_test, pats, N, sigma)
            checks = {**md.check_split(tr, te), **{f"train_{k}": v for k, v in md.check_class_independence(tr, len(pats)).items()},
                      **{f"test_{k}": v for k, v in md.check_class_independence(te, len(pats)).items()}}
            if not all(checks.values()):                              # review R10: enforced, not only stored
                raise ControlFailure(f"level-D control failed for seed {seed}, d {d}: "
                                     + ", ".join(k for k, v in checks.items() if not v))
            streams = {"decoder_train": [list(k) for k in tr.derivation], "test": [list(k) for k in te.derivation]}
            for net in NETWORKS:
                for nl in NONLINEARITIES:
                    for cname, cond in conditions.items():
                        if deadline:
                            deadline()
                        z = states[(net, nl, cname, d)]["z"]
                        rows.append({"seed": seed, "delay": d, "network": net, "nonlinearity": nl, "condition": cname,
                                     "preserve": md.evaluate_level_d(z, tr, te, "preserve"),
                                     "update": None if cond is None else md.evaluate_level_d(z, tr, te, "update"),
                                     "checks": checks, "streams": streams})
    return rows


def run(mode: str, out_dir: Optional[Path], *, delays: Optional[List[int]] = None, n_mc: Optional[int] = None,
        seeds: Optional[List[int]] = None, skip_level_d: bool = False, write: bool = True,
        time_limit_s: Optional[float] = None) -> Dict:
    """Overrides (delays, n_mc, seeds, skip_level_d, time_limit_s) are allowed only in
    'dev' and are recorded in the result."""
    if write and is_drive_c(out_dir):
        raise MemoryLabError("refusing to write on C:")
    proto = mt.load_protocol()
    st = mode_settings(proto, mode)
    overrides = {"delays": delays, "n_mc": n_mc, "seeds": seeds, "skip_level_d": skip_level_d, "time_limit_s": time_limit_s}
    if mode != "dev" and any(v not in (None, False) for v in overrides.values()):
        raise MemoryLabError(f"no overrides in the {mode} mode")
    limit = time_limit_s if time_limit_s is not None else proto["resources"]["time_limit"]["seconds"]
    deadline = make_deadline(limit)
    delays = delays or proto["delays"]["all"]
    n_mc = n_mc or st["n_mc"]
    seeds = seeds or st["seeds"]
    pats = mt.patterns()
    t0 = time.perf_counter()
    result = {"schema": SCHEMA, "mode": mode, "protocol_sha256": protocol_sha256(), "frozen_protocol_sha256": FROZEN_PROTOCOL_SHA256,
              "code_sha256": code_sha256(), "overrides": overrides, "delays": delays, "n_mc": n_mc, "seeds": seeds,
              "time_limit_s": limit, "status": "running", "failures": [], "timing_s": {},
              "diagnostics": [], "level_B": [], "level_D": []}
    try:
        states = compute_states(proto, st["conditions"], delays, pats, deadline)
        result["timing_s"]["states"] = time.perf_counter() - t0
        t = time.perf_counter()
        result["diagnostics"] = diagnostics(proto, states, st["conditions"], pats, deadline)
        result["timing_s"]["diagnostics"] = time.perf_counter() - t
        enforce_diagnostics(result["diagnostics"])
        t = time.perf_counter()
        result["level_B"] = level_b(proto, states, st["conditions"], pats, n_mc, st["bayes_seed"], deadline)
        result["timing_s"]["level_B"] = time.perf_counter() - t
        t = time.perf_counter()
        result["level_D"] = [] if skip_level_d else level_d(proto, states, st["conditions"], pats, seeds, delays,
                                                           st["n_train"], st["n_test"], deadline=deadline)
        result["timing_s"]["level_D"] = time.perf_counter() - t
        deadline()                                           # also an overrun in the LAST unit must not count as complete
        result["status"] = "complete"
    except RunTimeout as e:
        result["failures"].append(f"{type(e).__name__}: {e}")
        result["status"] = "aborted_timeout"
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
