"""M3/M4: experiment runner "pulse -> pause -> recall".

For every seed: adapt a copy of the frozen network on separate adaptation
episodes (model.adapt_network) and freeze it; then, for every delay d,
draw decoder-training and test episodes (plus validation in the research
round) and evaluate every condition on them. Test noise is shared across
conditions (paired). Raw per-seed values are stored -- no aggregate score.

Writes only below an output directory that must NOT be on drive C:.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import platform
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from experiments.mandala_memory import SCHEMA_VERSION
from experiments.mandala_memory.core import MemoryLabError, recall_state
from experiments.mandala_memory.data import (
    NearestMeanDecoder,
    assert_disjoint,
    balanced_accuracy,
    confusion,
    make_episodes,
    observe_episodes,
    permutation_observation,
    sum_observation,
)
from experiments.mandala_memory.model import adapt_network, condition_specs, resources

PERMUTATION = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]   # invertible sensor remap (reversal)


def config_hash(cfg: Dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def peak_rss_bytes() -> Optional[int]:
    """Peak working set of this process (Windows) or max RSS (POSIX)."""
    if platform.system() == "Windows":
        class PMC(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        k32, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
        k32.GetCurrentProcess.restype = ctypes.c_void_p       # 64-bit pseudo-handle; default int truncates it
        psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(PMC), ctypes.c_ulong]
        psapi.GetProcessMemoryInfo.restype = ctypes.c_int
        if psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
            return int(pmc.PeakWorkingSetSize)
        return None
    import resource
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _check_output_dir(out_dir: Path) -> Path:
    out_dir = Path(out_dir).resolve()
    if out_dir.drive.upper().startswith("C"):
        raise MemoryLabError(f"refusing to write on C: ({out_dir}); the protocol keeps all data on D:")
    return out_dir


def _evaluate(dec: NearestMeanDecoder, Y, labels):
    pred = dec.predict(Y)
    return {"balanced_accuracy": balanced_accuracy(labels, pred), "confusion": confusion(labels, pred)}


def run_seed(cfg: Dict, mode: str, seed: int, sizes: Dict, timings: Dict) -> Dict:
    net_cfg, obs = cfg["network"], cfg["observation"]
    sigma = float(obs["sigma"])
    specs = condition_specs(net_cfg)
    frozen = specs["frozen"]
    A_frozen_before = frozen.A.copy()
    t0 = time.perf_counter()
    adapted, rec = adapt_network(frozen, cfg["adaptation"], mode=mode, seed=seed)
    timings["adaptation_s"] = timings.get("adaptation_s", 0.0) + time.perf_counter() - t0
    A_adapted_after_training = adapted.A.copy()
    N = frozen.N
    H = np.eye(N)
    P = permutation_observation(N, PERMUTATION)
    out = {"seed": seed, "adaptation": rec.__dict__, "delays": {}}
    for d in cfg["episode"]["delay_steps"]:
        t1 = time.perf_counter()
        tr = make_episodes(mode, seed, "decoder_train", d, sizes["train"], N, sigma)
        te = make_episodes(mode, seed, "test", d, sizes["test"], N, sigma)
        sets = [tr, te]
        if sizes.get("validation"):
            sets.append(make_episodes(mode, seed, "validation", d, sizes["validation"], N, sigma))
        assert_disjoint(*sets)
        tr1 = make_episodes(mode, seed, "decoder_train", d, sizes["train"], 1, sigma)   # sum observation
        te1 = make_episodes(mode, seed, "test", d, sizes["test"], 1, sigma)

        def states(spec, **kw):
            return {c: recall_state(spec, c, d, **kw) for c in (0, 1)}

        row = {}
        st = {"frozen": states(frozen), "adapted": states(adapted)}
        for name in ("uncoupled_leak", "linear", "uniform_M1", "renamed_M3_c8_11"):
            st[name] = states(specs[name])
        st["reset_control"] = states(frozen, reset_after_pulse=True)
        decoders = {}
        for name, s in st.items():
            Ytr, Yte = observe_episodes(s, H, tr), observe_episodes(s, H, te)
            dec = NearestMeanDecoder().fit(Ytr, tr.labels)
            decoders[name] = dec
            row[name] = {**_evaluate(dec, Yte, te.labels),
                         "state_separation_l2": float(np.linalg.norm(s[0] - s[1])),
                         "state_separation_inf": float(np.max(np.abs(s[0] - s[1])))}
        # pre-registered second mode: decoder frozen on the PRE network, applied to the adapted network
        row["adapted_with_frozen_decoder"] = _evaluate(decoders["frozen"], observe_episodes(st["adapted"], H, te), te.labels)
        # sum observation (separate information-loss control; other observation dimension!)
        dec_sum = NearestMeanDecoder().fit(observe_episodes(st["frozen"], sum_observation(N), tr1), tr1.labels)
        row["sum_observation_frozen"] = _evaluate(dec_sum, observe_episodes(st["frozen"], sum_observation(N), te1), te1.labels)
        # invertible sensor permutation: frozen decoder vs refit
        row["permutation_frozen_decoder"] = _evaluate(decoders["frozen"], observe_episodes(st["frozen"], P, te), te.labels)
        dec_perm = NearestMeanDecoder().fit(observe_episodes(st["frozen"], P, tr), tr.labels)
        row["permutation_refit_decoder"] = _evaluate(dec_perm, observe_episodes(st["frozen"], P, te), te.labels)
        row["checks"] = {
            "uniform_equals_renamed_states": bool(all(np.array_equal(st["uniform_M1"][c], st["renamed_M3_c8_11"][c]) for c in (0, 1))),
            "reset_control_states_identical": bool(np.array_equal(st["reset_control"][0], st["reset_control"][1])),
            "split_sizes": {e.role: len(e.ids) for e in sets},
            "split_derivations": {e.role: list(e.derivation) for e in sets},
        }
        out["delays"][str(d)] = row
        timings["evaluation_s"] = timings.get("evaluation_s", 0.0) + time.perf_counter() - t1
    out["checks"] = {
        "frozen_A_unchanged": bool(np.array_equal(frozen.A, A_frozen_before)),
        "adapted_A_unchanged_during_tests": bool(np.array_equal(adapted.A, A_adapted_after_training)),
        "adapted_masked_entries_zero": rec.masked_entries_zero,
        "adapted_row_sums_gamma": bool(np.allclose(rec.row_sums_after, float(net_cfg["gamma"]), atol=1e-12)),
    }
    out["resources"] = {name: resources(spec) for name, spec in {**specs, "adapted": adapted}.items()}
    out["decoder"] = {"kind": "nearest_mean", "standardization": "none", "tie_break_class": 0,
                      "parameters_full_observation": 2 * N, "parameters_sum_observation": 2}
    return out


def run_experiment(cfg: Dict, mode: str, out_dir: Path, *, timeout_s: Optional[float] = None,
                   seeds: Optional[List[int]] = None) -> Dict:
    if mode not in ("smoke", "research"):
        raise MemoryLabError("mode must be smoke or research")
    out_dir = _check_output_dir(out_dir)
    block = cfg[mode]
    declared = list(block["seeds"])
    seeds = list(seeds if seeds is not None else declared)
    if len(set(seeds)) != len(seeds):
        raise MemoryLabError("duplicate seeds are not allowed (they would fake independent repetitions)")
    if not seeds:
        raise MemoryLabError("at least one seed required")
    sizes = {"train": block["decoder_train_per_class_per_delay"], "test": block["test_per_class_per_delay"],
             "validation": block.get("validation_per_class_per_delay", 0)}
    timeout_explicit = timeout_s is not None
    if timeout_s is None:
        timeout_s = cfg["limits"]["smoke_timeout_seconds"] if mode == "smoke" else None
    if timeout_s is not None and not (timeout_s > 0):
        raise MemoryLabError("timeout_s must be > 0 (or None)")
    chash = config_hash(cfg)
    # Review R1: the PROTOCOL id stays fixed for a configuration; every execution
    # gets its own unique id, so partial, aborted and repeated runs never overwrite
    # each other.
    protocol_id = f"{mode}-{chash[:10]}"
    execution_id = time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    run_id = f"{protocol_id}--{execution_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {"schema_version": SCHEMA_VERSION, "run_id": run_id, "protocol_id": protocol_id, "execution_id": execution_id,
              "mode": mode, "config_sha256": chash, "config": cfg,
              "seeds": seeds, "seeds_declared_by_protocol": declared,
              "execution_options": {"seeds_override": seeds != declared, "timeout_s": timeout_s,
                                    "timeout_explicit": timeout_explicit},
              "status": "running",
              "evidence_kind": "numerical_sample", "empirical_status": "synthetic_only",
              "time_convention": "u_0 = e_s pulse, then d zero steps; readout x_(d+1); d = 0 directly after the pulse",
              "runs": [], "failed_seeds": [], "abort_reason": None}
    t_start = time.perf_counter()
    timings: Dict[str, float] = {}
    for seed in seeds:
        if timeout_s is not None and time.perf_counter() - t_start > timeout_s:
            result["status"] = "aborted"
            result["abort_reason"] = f"timeout {timeout_s}s reached before seed {seed}; completed seeds kept"
            break
        try:
            result["runs"].append(run_seed(cfg, mode, seed, sizes, timings))
        except Exception as e:  # never drop a failed seed silently
            result["failed_seeds"].append({"seed": seed, "error": f"{type(e).__name__}: {e}"})
    if result["status"] == "running":
        result["status"] = "complete" if not result["failed_seeds"] else "complete_with_failures"
    result["resources"] = {"wall_time_s": round(time.perf_counter() - t_start, 3), **{k: round(v, 3) for k, v in timings.items()},
                           "peak_rss_mib": None if peak_rss_bytes() is None else round(peak_rss_bytes() / 2 ** 20, 1),
                           "python": sys.version.split()[0], "numpy": np.__version__,
                           "blas_threads_env": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}}
    from experiments.mandala_memory.evaluate import inference_release

    result["inference_release"] = inference_release(result)       # review R2: completeness gate, not the mode alone
    path = out_dir / f"{run_id}.json"
    write_exclusive(path, json.dumps(result, indent=1, ensure_ascii=False, allow_nan=False) + "\n")
    result["output_path"] = str(path)
    return result


def write_exclusive(path: Path, text: str) -> None:
    """Atomic, never-overwriting write: temp file in the same directory, then a
    rename that FAILS if the target exists (os.link semantics on every platform)."""
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    tmp.write_text(text, encoding="utf-8")
    try:
        os.link(tmp, path)            # raises FileExistsError if the target exists
    except FileExistsError:
        raise MemoryLabError(f"refusing to overwrite existing result {path.name}") from None
    finally:
        tmp.unlink(missing_ok=True)


__all__ = ["config_hash", "peak_rss_bytes", "run_seed", "run_experiment", "write_exclusive", "PERMUTATION"]
