"""M11 runner: train NM, LDA and the MLP procedure on nested draws and evaluate them
(plan Fassung 2, section 3). The Mandala is unchanged (frozen M10 functions).

Modes: dev (development cases/seeds; before the freeze), smoke and research (only after a
valid M11 freeze: protocol + reference artifact + code hashes + reviewed commit).
Time limit: elapsed wall-clock, checked cooperatively before every unit and before
completion; timeout -> status aborted_timeout, written exclusively, never released.

    python -m experiments.mandala_memory.m11_run --mode dev --out-dir D:/mandala/mandala-memory-results/m11/dev
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np

from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory import m11_readout as mr
from experiments.mandala_memory import m11_references as mref
from experiments.mandala_memory.core import MemoryLabError, is_drive_c
from experiments.mandala_memory.runner import peak_rss_bytes, write_exclusive

FROZEN_PROTOCOL_SHA256: Optional[str] = None          # set in the M11 freeze commit
FREEZE_RECORD = mref.HERE / "protocol" / "m11_freeze.json"
CODE_FILES = ("m11_readout.py", "m11_references.py", "m11_run.py", "m11_evaluate.py", "m10_task.py", "m10_decoders.py",
              "core.py", "predict.py", "data.py")
SCHEMA = "mandala-memory-m11-result-v1"
clock: Callable[[], float] = time.monotonic


class RunTimeout(MemoryLabError):
    pass


def code_sha256() -> Dict[str, str]:
    return {f: mref.sha(mref.HERE / f) for f in CODE_FILES}


def require_frozen(mode: str) -> Dict:
    if FROZEN_PROTOCOL_SHA256 is None:
        raise MemoryLabError(f"{mode} run blocked: the M11 protocol is not frozen yet")
    if mref.sha(mref.PROTOCOL) != FROZEN_PROTOCOL_SHA256:
        raise MemoryLabError(f"{mode} run blocked: protocol differs from the frozen protocol")
    if not FREEZE_RECORD.is_file() or not mref.RESEARCH_REFERENCES.is_file():
        raise MemoryLabError(f"{mode} run blocked: freeze record or reference artifact missing")
    rec = json.loads(FREEZE_RECORD.read_text(encoding="utf-8"))
    if (rec.get("protocol_sha256") != FROZEN_PROTOCOL_SHA256 or not rec.get("reviewed_code_commit")
            or rec.get("references_sha256") != mref.sha(mref.RESEARCH_REFERENCES)
            or rec.get("m10_binding") != mref.require_m10_frozen()):
        raise MemoryLabError(f"{mode} run blocked: freeze record does not match protocol/references")
    if rec.get("code_sha256") != code_sha256():
        raise MemoryLabError(f"{mode} run blocked: code differs from the frozen code")
    return rec


def settings(proto: Dict, mode: str) -> Dict:
    mref.require_m10_frozen()                 # review M11-R5: the Mandala must be the frozen M10 one, before any state
    m10 = mt.load_protocol()
    if mode in ("smoke", "research"):
        require_frozen(mode)
        return {"cases": proto["cases"], "conditions": m10["conditions"], "seeds": proto["seeds"][mode],
                "stream_mode": proto["modes"][mode]}
    if mode == "dev":
        return {"cases": proto["development"]["cases"], "conditions": m10["development"]["conditions"],
                "seeds": proto["seeds"]["dev"], "stream_mode": proto["modes"]["dev"]}
    raise MemoryLabError("mode must be dev, smoke or research")


def mlp_hyper(proto: Dict, override: Optional[Dict]) -> Dict:
    h = proto["decoders"]["mlp"]
    if override is not None:
        return override
    if not isinstance(h.get("hyperparameters"), dict):
        raise MemoryLabError("MLP hyperparameters not set in the protocol yet")
    return {**h["hyperparameters"], "hidden": h["hidden"], "inits": h["inits"]}


def run(mode: str, out_dir: Optional[Path], *, seeds: Optional[List[int]] = None, n_grid: Optional[List[int]] = None,
        test_pairs: Optional[int] = None, hyper: Optional[Dict] = None, time_limit_s: Optional[float] = None,
        write: bool = True) -> Dict:
    if write and is_drive_c(out_dir):
        raise MemoryLabError("refusing to write on C:")
    proto = mref.load_protocol()
    st = settings(proto, mode)
    overrides = {"seeds": seeds, "n_grid": n_grid, "test_pairs": test_pairs, "hyper": hyper, "time_limit_s": time_limit_s}
    if mode != "dev" and any(v is not None for v in overrides.values()):
        raise MemoryLabError(f"no overrides in the {mode} mode")
    hp = mlp_hyper(proto, hyper)
    seeds = seeds or st["seeds"]
    n_grid = n_grid or proto["n_grid"]
    n_max, n_test = max(n_grid), test_pairs or proto["test_pairs"]
    limit = time_limit_s if time_limit_s is not None else proto["resources"]["time_limit"]["seconds"]
    start = clock()

    def deadline():
        if clock() - start > limit:
            raise RunTimeout(f"time limit of {limit} s exceeded")

    m10 = mt.load_protocol()
    pats = mt.patterns()
    probs = np.array([float(p) for _, p in pats])
    sigma = m10["observation"]["sigma"]
    t0 = time.perf_counter()
    result = {"schema": SCHEMA, "mode": mode, "protocol_sha256": mref.sha(mref.PROTOCOL), "frozen_protocol_sha256": FROZEN_PROTOCOL_SHA256,
              "m10_binding": mref.require_m10_frozen(),
              "references_sha256": mref.sha(mref.RESEARCH_REFERENCES) if mode != "dev" else None,
              "code_sha256": code_sha256(), "overrides": overrides, "seeds": seeds, "n_grid": n_grid, "test_pairs": n_test,
              "mlp_hyper": hp, "time_limit_s": limit, "status": "running", "failures": [], "rows": []}
    try:
        Z = {}
        for case in st["cases"]:
            deadline()
            Z[case["name"]] = mref.case_states(case, m10, st["conditions"], pats, proto["delay"])
        for seed in seeds:
            train = mr.draw_pairs(st["stream_mode"], seed, "train", n_max, probs, 12, sigma)
            test = mr.draw_pairs(st["stream_mode"], seed, "test", n_test, probs, 12, sigma)
            for case in st["cases"]:
                z = Z[case["name"]]
                T, tl, _ = mr.episodes(z, test, n_test)
                for n in n_grid:
                    deadline()
                    Y, lab, pair = mr.episodes(z, train, n)
                    row = {"seed": seed, "case": case["name"], "n": n, "train_streams": train["streams"],
                           "test_streams": test["streams"], "n_test_pairs": n_test}
                    for name, fit in (("nm", mr.nm_rule), ("lda", mr.lda_rule)):
                        w, b = fit(Y, lab)
                        row[name] = {"exact": mr.exact_accuracy(w, b, z, probs, sigma),
                                     "test": mr.balanced_accuracy(tl, mr.predict_linear(w, b, T))}
                    t1 = time.perf_counter()
                    model, info = mr.fit_mlp(Y, lab, pair, n, hp, st["stream_mode"], seed, case["name"], deadline=deadline)
                    if hyper is None:                    # review M11-R7: the procedure is checked in the runner too
                        from experiments.mandala_memory.m11_evaluate import mlp_procedure_problems

                        bad = mlp_procedure_problems(info, proto, st["stream_mode"], seed, case["name"], n)
                        if bad:
                            raise MemoryLabError(f"MLP procedure deviates for seed {seed}, {case['name']}, n {n}: {bad}")
                    row["mlp"] = {"test": mr.balanced_accuracy(tl, model.predict(T)), "fit": info,
                                  "seconds": time.perf_counter() - t1}
                    result["rows"].append(row)
        deadline()
        result["status"] = "complete"
    except RunTimeout as e:
        result["failures"].append(f"{type(e).__name__}: {e}")
        result["status"] = "aborted_timeout"
    except Exception as e:
        result["failures"].append(f"{type(e).__name__}: {e}")
        result["status"] = "failed"
    result["timing_s"] = time.perf_counter() - t0
    result["peak_rss_bytes"] = peak_rss_bytes()
    result["run_id"] = f"m11-{mode}-{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}"
    if write:
        Path(out_dir).resolve().mkdir(parents=True, exist_ok=True)
        path = Path(out_dir).resolve() / f"{result['run_id']}.json"
        write_exclusive(path, json.dumps(result, indent=1, allow_nan=False, default=_json) + "\n")
        result["output_path"] = str(path)
    return result


def _json(o):
    if isinstance(o, (np.bool_, np.integer, np.floating)):
        return o.item()
    raise TypeError(f"not JSON serialisable: {type(o).__name__}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=("dev", "smoke", "research"))
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    res = run(a.mode, a.out_dir)
    print(json.dumps({"run_id": res["run_id"], "status": res["status"], "failures": res["failures"],
                      "timing_s": res["timing_s"], "peak_rss_mib": (res["peak_rss_bytes"] or 0) / 2 ** 20,
                      "output": res.get("output_path")}, indent=1))
    return 0 if res["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
