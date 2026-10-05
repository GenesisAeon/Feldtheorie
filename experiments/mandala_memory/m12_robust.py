"""M12 robustness evaluation (plan Fassung 2, sections 5 and 6): FIXED models, 9 conditions.

Only loads the checked artifacts (m12_models.require_models) and evaluates them. Every fit
entry point (m11_readout.MLP.fit, m11_readout.lda_rule, m11_readout.fit_mlp,
m12_common.fit_mlp) is blocked for the whole evaluation; model files are hashed before and
after, and the weights/standardisation in use are compared with the loaded copies.
Test episodes: ONE draw per seed (patterns + standard-normal noise) shared by all
conditions and both decoders: y = z(c) + sigma(c) * eps.

    python -m experiments.mandala_memory.m12_robust --mode dev --models D:/.../models-x --refs D:/.../references-dev.json --seeds 921 --out-dir D:/mandala/mandala-memory-results/m12/dev
    python -m experiments.mandala_memory.m12_robust --mode research --out-dir D:/mandala/mandala-memory-results/m12/research

Research (review M12-R7): ONLY through evaluation_phase() -- one attempt, independent of the
output folder: preconditions, then an exclusive claim BEFORE any state/test computation; a
failure or timeout leaves a failure record; a second call after success, timeout or failure
is refused before any computation. Research results are always written.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import time
import uuid
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np

from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory import m11_readout as mr
from experiments.mandala_memory import m12_common as mc
from experiments.mandala_memory import m12_models as mm
from experiments.mandala_memory import m12_references as mref
from experiments.mandala_memory.core import MemoryLabError, is_drive_c
from experiments.mandala_memory.runner import peak_rss_bytes

SCHEMA = "mandala-memory-m12-result-v1"
EVAL_CLAIM = mc.HERE / "protocol" / "m12_evaluation.claim.json"
EVAL_FAILURE = mc.HERE / "protocol" / "m12_evaluation.failed.json"
EVAL_DONE = mc.HERE / "protocol" / "m12_evaluation.done.json"
clock: Callable[[], float] = time.monotonic


class RunTimeout(MemoryLabError):
    pass


class FitCalledDuringEvaluation(MemoryLabError):
    pass


@contextlib.contextmanager
def no_fit():
    """Blocks every training entry point while the evaluation runs."""
    def blocked(*_a, **_k):
        raise FitCalledDuringEvaluation("a fit was called during the robustness evaluation")

    saved = [(mr.MLP, "fit", mr.MLP.fit), (mr, "lda_rule", mr.lda_rule), (mr, "fit_mlp", mr.fit_mlp), (mc, "fit_mlp", mc.fit_mlp)]
    try:
        for obj, name, _ in saved:
            setattr(obj, name, blocked)
        yield
    finally:
        for obj, name, orig in saved:
            setattr(obj, name, orig)


def run(mode: str, out_dir: Optional[Path], *, models_dir: Optional[Path] = None, refs_path: Optional[Path] = None,
        seeds: Optional[List[int]] = None, test_pairs: Optional[int] = None, time_limit_s: Optional[float] = None,
        write: bool = True, _claimed: bool = False) -> Dict:
    if mode == "research" and not _claimed:
        raise MemoryLabError("research evaluation only via evaluation_phase() (one attempt, exclusive claim)")
    if mode == "research" and not write:
        raise MemoryLabError("a research evaluation is always written")
    if write and (out_dir is None or is_drive_c(out_dir)):
        raise MemoryLabError("an output directory on D: is required")
    proto = mc.load_protocol()
    overrides = {"test_pairs": test_pairs, "time_limit_s": time_limit_s}
    if mode in ("research", "smoke"):
        if any(v is not None for v in overrides.values()) or models_dir is not None or refs_path is not None or seeds is not None:
            raise MemoryLabError(f"no overrides in the {mode} mode")
        refs = mref.require_references(mode)
        models = mm.require_models(mode)
        case_set, smode = ("research" if mode == "research" else "smoke"), proto["modes"][mode]
    elif mode == "dev":
        if models_dir is None or refs_path is None or seeds is None:
            raise MemoryLabError("dev evaluation needs --models, --refs and --seeds")
        refs = mref.require_references("dev", refs_path)
        models = mm.require_models("dev", models_dir, seeds=seeds, references_sha256=refs["sha256"])
        case_set, smode = "dev", proto["modes"]["dev"]
    else:
        raise MemoryLabError("mode must be dev, smoke or research")
    pred = mc.require_predecessors_frozen()
    n_test = test_pairs or proto["test"]["pairs"]
    limit = time_limit_s if time_limit_s is not None else proto["resources"]["time_limits_s"]["evaluation"]
    start = clock()

    def deadline():
        if clock() - start > limit:
            raise RunTimeout(f"time limit of {limit} s exceeded")

    conds = mc.conditions(proto, case_set)
    if [c["name"] for c in conds] != list(refs["refs"]["conditions"]):
        raise MemoryLabError("reference conditions differ from the protocol grid")
    seeds = list(models["manifest"]["seeds"])
    hyper = mc.mlp_hyper(proto)
    pats = mt.patterns()
    probs = mc.probabilities(pats)
    t0 = time.perf_counter()
    result = {"schema": SCHEMA, "mode": mode, "protocol_sha256": mc.sha(mc.PROTOCOL), "frozen_protocol_sha256": mref.FROZEN_PROTOCOL_SHA256,
              "references_sha256": refs["sha256"], "manifest_sha256": models["manifest_sha256"],
              "model_freeze_sha256": mc.sha(mm.MODEL_FREEZE) if mode == "research" else None,
              "code_sha256": mc.code_sha256(), "predecessors": pred, "overrides": overrides, "seeds": seeds,
              "conditions": conds, "test_pairs": n_test, "time_limit_s": limit, "fit_guard": "active",
              "model_file_hashes_before": models["file_hashes"], "status": "running", "failures": [], "rows": []}
    try:
        with no_fit():
            zs = {}
            for c in conds:
                a = round(c["amplitude"], 10)
                if a not in zs:
                    zs[a] = mc.states(proto, case_set, c["amplitude"], pats)
            for seed in seeds:
                arr, meta = models["models"][seed]
                originals = {k: v.copy() for k, v in arr.items()}
                mlp = mc.mlp_from_arrays(arr, hyper)
                w, b = arr["lda_w"], float(arr["lda_b"][0])
                d = mc.draw(smode, seed, "test", n_test, probs)
                if d["streams"] == meta["train_streams"]:
                    raise MemoryLabError("test stream equals the training stream")
                for c in conds:
                    deadline()
                    z = zs[round(c["amplitude"], 10)]
                    Y, _, _ = mc.episodes(z, d, n_test, c["sigma"])
                    pm, pl = mlp.predict(Y), mr.predict_linear(w, b, Y)
                    rm, rl = mc.pair_scores(pm, n_test), mc.pair_scores(pl, n_test)
                    diff = rm - rl
                    result["rows"].append({
                        "seed": seed, "condition": c["name"], "test_streams": d["streams"], "n_test_pairs": int(len(Y) // 2),
                        "mlp": mc.acc_and_se(pm, n_test),
                        "lda": {**mc.acc_and_se(pl, n_test), "exact": mr.exact_accuracy(w, b, z, probs, c["sigma"])},
                        "advantage_test": {"mean": float(diff.mean()), "se_pair": float(diff.std(ddof=1) / np.sqrt(n_test))}})
                used = mc.model_arrays(mlp, w, b)
                if any(not np.array_equal(used[k], originals[k]) for k in originals):
                    raise MemoryLabError(f"seed {seed}: weights or standardisation changed during the evaluation")
        after = mc.directory_hashes(Path(models["directory"]))
        result["model_file_hashes_after"] = after
        if after != models["file_hashes"]:
            raise MemoryLabError("model files changed during the evaluation")
        deadline()
        result["status"] = "complete"
    except RunTimeout as e:
        result["failures"].append(f"{type(e).__name__}: {e}")
        result["status"] = "aborted_timeout"
    except Exception as e:
        result["failures"].append(f"{type(e).__name__}: {e}")
        result["status"] = "failed"
    result.setdefault("model_file_hashes_after", mc.directory_hashes(Path(models["directory"])))
    result["timing_s"] = time.perf_counter() - t0
    result["peak_rss_bytes"] = peak_rss_bytes()
    result["run_id"] = f"m12-{mode}-{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}"
    if write:
        path = Path(out_dir).resolve() / f"{result['run_id']}.json"
        mc.write_json_exclusive(path, result)
        result["output_path"] = str(path)
    return result


def evaluation_phase(out_dir: Path) -> Dict:
    """The one-time research robustness evaluation (review M12-R7)."""
    if EVAL_DONE.exists():
        raise MemoryLabError("robustness evaluation already completed (no second research attempt)")
    if EVAL_CLAIM.exists() or EVAL_FAILURE.exists():
        raise MemoryLabError("robustness evaluation already started or failed: claim/failure record exists (no silent retry)")
    if out_dir is None or is_drive_c(out_dir):
        raise MemoryLabError("an output directory on D: is required")
    mref.require_references("research")                     # frozen protocol + references
    mm.require_models("research")                           # model freeze, manifest, provenance
    npz = mm.npz_git_identity_problems()
    if npz:
        raise MemoryLabError(f"model NPZ files are not committed byte-identically: {npz}")
    mc.write_json_exclusive(EVAL_CLAIM, {"started_unix": time.time(), "git_head": mref.git_head(), "protocol_sha256": mc.sha(mc.PROTOCOL),
                                         "out_dir": str(out_dir)})
    try:
        res = run("research", out_dir, _claimed=True)
    except Exception as e:
        mc.write_json_exclusive(EVAL_FAILURE, {"failed_unix": time.time(), "error": f"{type(e).__name__}: {e}"})
        raise
    if res["status"] != "complete":
        mc.write_json_exclusive(EVAL_FAILURE, {"failed_unix": time.time(), "status": res["status"], "failures": res["failures"],
                                               "run_id": res["run_id"], "output_path": res.get("output_path")})
    else:
        mc.write_json_exclusive(EVAL_DONE, {"done_unix": time.time(), "run_id": res["run_id"], "output_path": res["output_path"],
                                            "result_sha256": mc.sha(Path(res["output_path"]))})
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("dev", "smoke", "research"), required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--models", type=Path)
    ap.add_argument("--refs", type=Path)
    ap.add_argument("--seeds", type=int, nargs="+")
    ap.add_argument("--test-pairs", type=int)
    a = ap.parse_args(argv)
    try:
        if a.mode == "research":
            if any(v is not None for v in (a.models, a.refs, a.seeds, a.test_pairs)):
                raise SystemExit("research: no --models/--refs/--seeds/--test-pairs")
            res = evaluation_phase(a.out_dir)
        else:
            res = run(a.mode, a.out_dir, models_dir=a.models, refs_path=a.refs, seeds=a.seeds, test_pairs=a.test_pairs)
    except MemoryLabError as e:
        raise SystemExit(str(e))
    print(json.dumps({"run_id": res["run_id"], "status": res["status"], "failures": res["failures"], "timing_s": res["timing_s"],
                      "peak_rss_mib": res["peak_rss_bytes"] / 2 ** 20, "output": res.get("output_path")}, indent=1))
    return 0 if res["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
