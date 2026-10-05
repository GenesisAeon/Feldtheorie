"""M12 base models (plan Fassung 2, sections 2, 3, 7): training in c0 ONLY, artifacts, model freeze.

The training has no access to the shift grid and computes no test accuracy. Every model is
written exclusively (NPZ + JSON), reloaded strictly and compared bit-exactly with the model
in memory (roundtrip) before the manifest is written. Research models: only through
training_phase() (frozen protocol, committed references, exclusive claim, failure record);
the model freeze record binds protocol, references, manifest and code.

    python -m experiments.mandala_memory.m12_models --mode dev --out-dir D:/mandala/mandala-memory-results/m12/dev/models-<tag> [--seeds 921] [--n-pairs 2000]
    python -m experiments.mandala_memory.m12_models --mode smoke
    python -m experiments.mandala_memory.m12_models --mode research   # training phase -> protocol/m12_models/
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np

from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory import m11_readout as mr
from experiments.mandala_memory import m12_common as mc
from experiments.mandala_memory import m12_references as mref
from experiments.mandala_memory.core import MemoryLabError
from experiments.mandala_memory.runner import peak_rss_bytes

RESEARCH_MODELS = mc.HERE / "protocol" / "m12_models"
TRAINING_CLAIM = mc.HERE / "protocol" / "m12_models.claim.json"
TRAINING_FAILURE = mc.HERE / "protocol" / "m12_models.failed.json"
MODEL_FREEZE = mc.HERE / "protocol" / "m12_models_freeze.json"
SCHEMA_META = "mandala-memory-m12-model-v1"
ROUNDTRIP_EPISODES = 1000
clock: Callable[[], float] = time.monotonic


class RunTimeout(MemoryLabError):
    pass


def record_path(directory: Path) -> Path:
    return Path(directory).with_name(Path(directory).name + ".training.json")


def expected_keys(smode: str, seed: int, n: int, inits: int) -> Dict:
    return {"train": [list(mc.stream(smode, seed, "pattern", "train")[1]), list(mc.stream(smode, seed, "noise", "train")[1])],
            "inits": [list(mc.stream(smode, seed, "mlp-init", mc.CASE_LABEL, n, k)[1]) for k in range(inits)]}


def roundtrip_problems(directory: Path, seed: int, mlp: mr.MLP, lda_w, lda_b, Y: np.ndarray, hyper: Dict) -> List[str]:
    """Saved and freshly loaded models give bit-identical scores on fixed inputs."""
    arr, _ = mc.load_seed(directory, seed)
    m2 = mc.mlp_from_arrays(arr, hyper)
    bad = []
    if not np.array_equal(mc.mlp_logits(mlp, Y), mc.mlp_logits(m2, Y)):
        bad.append("mlp_logits_differ")
    if not np.array_equal(Y @ np.asarray(lda_w) + lda_b, Y @ arr["lda_w"] + arr["lda_b"][0]):
        bad.append("lda_scores_differ")
    return bad


def train(mode: str, out_dir: Optional[Path] = None, *, seeds: Optional[List[int]] = None, n_pairs: Optional[int] = None,
          refs_path: Optional[Path] = None, time_limit_s: Optional[float] = None, _claimed: bool = False) -> Dict:
    proto = mc.load_protocol()
    overrides = {"seeds": seeds, "n_pairs": n_pairs, "time_limit_s": time_limit_s}
    if mode in ("research", "smoke"):
        if any(v is not None for v in overrides.values()) or refs_path is not None:
            raise MemoryLabError(f"no overrides in the {mode} mode")
        if mode == "research" and not _claimed:
            raise MemoryLabError("research models only via training_phase() (frozen protocol, references, claim)")
        mref.require_protocol_frozen(f"{mode} training")
        refs = mref.require_references(mode)
        out_dir = RESEARCH_MODELS if mode == "research" else Path(proto["artifacts"]["smoke_dir"])
        case_set, smode, seeds = "research" if mode == "research" else "smoke", proto["modes"][mode], proto["seeds"][mode]
    elif mode == "dev":
        if out_dir is None:
            raise MemoryLabError("dev training needs --out-dir")
        refs = mref.require_references("dev", refs_path) if refs_path is not None else {"refs": None, "sha256": None}
        case_set, smode, seeds = "dev", proto["modes"]["dev"], seeds or proto["seeds"]["dev"]
    else:
        raise MemoryLabError("mode must be dev, smoke or research")
    out_dir = Path(out_dir)
    if out_dir.exists():
        raise MemoryLabError(f"model directory {out_dir} exists already (never overwritten)")
    binding_pred = mc.require_predecessors_frozen()             # before any state
    hyper = mc.mlp_hyper(proto)
    n = n_pairs or proto["training"]["n_pairs"]
    limit = time_limit_s if time_limit_s is not None else proto["resources"]["time_limits_s"]["training"]
    start = clock()

    def deadline():
        if clock() - start > limit:
            raise RunTimeout(f"time limit of {limit} s exceeded")

    base = mc.base_of(proto, case_set)
    pats = mt.patterns()
    probs = mc.probabilities(pats)
    t0 = time.perf_counter()
    binding = {"protocol_sha256": mc.sha(mc.PROTOCOL), "references_sha256": refs["sha256"], "code_sha256": mc.code_sha256(),
               "m10_binding": binding_pred["m10"], "m11_binding": binding_pred["m11"],
               "hyper_source": proto["training"]["hyper_source"], "n_pairs": n,
               "condition": {"name": "c0", **{k: base[k] for k in ("X", "Y", "amplitude", "sigma")}}}
    record = {"schema": "mandala-memory-m12-training-v1", "mode": mode, "seeds": list(seeds), "overrides": overrides,
              "time_limit_s": limit, "status": "running", "failures": [], "per_seed": [], **binding}
    files: Dict[str, str] = {}
    try:
        z0 = mc.states(proto, case_set, base["amplitude"], pats)     # c0 only: the grid is never read here
        for seed in seeds:
            deadline()
            t1 = time.perf_counter()
            d = mc.draw(smode, seed, "train", n, probs)
            Y, lab, pair = mc.episodes(z0, d, n, base["sigma"])
            lda_w, lda_b = mr.lda_rule(Y, lab)
            mlp, info = mc.fit_mlp(Y, lab, pair, n, hyper, smode, seed, deadline)
            meta = {"schema": SCHEMA_META, "mode": mode, "seed": seed, "n_pairs": n, "condition": binding["condition"],
                    "hyper": hyper, "hyper_source": binding["hyper_source"], "fit": info, "train_streams": d["streams"],
                    "protocol_sha256": binding["protocol_sha256"], "references_sha256": binding["references_sha256"],
                    "code_sha256": binding["code_sha256"], "m10_binding": binding["m10_binding"], "m11_binding": binding["m11_binding"]}
            files.update(mc.save_seed(out_dir, seed, mc.model_arrays(mlp, lda_w, lda_b), meta))
            rt = roundtrip_problems(out_dir, seed, mlp, lda_w, lda_b, Y[:ROUNDTRIP_EPISODES], hyper)
            if rt:
                raise MemoryLabError(f"seed {seed}: roundtrip failed: {rt}")
            record["per_seed"].append({"seed": seed, "seconds": time.perf_counter() - t1, "selected_init": info["selected"]["init"],
                                       "epochs": [i["epochs"] for i in info["inits"]], "roundtrip": "bit-identical"})
        deadline()
        mc.write_manifest(out_dir, mode, seeds, files, binding)
        record["status"] = "complete"
    except RunTimeout as e:
        record["failures"].append(f"{type(e).__name__}: {e}")
        record["status"] = "aborted_timeout"
    except Exception as e:
        record["failures"].append(f"{type(e).__name__}: {e}")
        record["status"] = "failed"
    record["timing_s"] = time.perf_counter() - t0
    record["peak_rss_bytes"] = peak_rss_bytes()
    mc.write_json_exclusive(record_path(out_dir), record)
    record["output_dir"] = str(out_dir)
    return record


def training_phase() -> Dict:
    """One-time research training: preconditions BEFORE any computation, exclusive claim."""
    if RESEARCH_MODELS.exists() or MODEL_FREEZE.exists():
        raise MemoryLabError("training phase already completed: model directory or model freeze exists")
    if TRAINING_CLAIM.exists() or TRAINING_FAILURE.exists():
        raise MemoryLabError("training phase already started or failed: claim/failure record exists (no silent retry)")
    if not mref.git_clean(mref.VERSIONED + ("protocol/m12_references.json", "protocol/m12_freeze.json")):
        raise MemoryLabError("training phase refused: M12 code/protocol/references are not committed")
    mref.require_protocol_frozen("training phase")
    mref.require_references("research")
    mc.write_json_exclusive(TRAINING_CLAIM, {"started_unix": time.time(), "git_head": mref.git_head(), "protocol_sha256": mc.sha(mc.PROTOCOL)})
    try:
        rec = train("research", _claimed=True)
    except Exception as e:
        mc.write_json_exclusive(TRAINING_FAILURE, {"failed_unix": time.time(), "error": f"{type(e).__name__}: {e}"})
        raise
    if rec["status"] != "complete":
        mc.write_json_exclusive(TRAINING_FAILURE, {"failed_unix": time.time(), "status": rec["status"], "failures": rec["failures"]})
    return rec


# --- provenance and loading for the evaluation ---------------------------------------------
def provenance_problems(meta: Dict, proto: Dict, mode: str, seed: int, binding: Dict) -> List[str]:
    smode = proto["modes"][mode]
    hyper = mc.mlp_hyper(proto)
    exp = expected_keys(smode, seed, meta.get("n_pairs", -1), hyper["inits"])
    bad = []
    for k in ("protocol_sha256", "references_sha256", "code_sha256", "m10_binding", "m11_binding", "hyper_source", "n_pairs", "condition"):
        if meta.get(k) != binding.get(k):
            bad.append(f"{k}_differs")
    if mode != "dev" and meta.get("n_pairs") != proto["training"]["n_pairs"]:
        bad.append("n_pairs_not_protocol")
    if meta.get("hyper") != hyper:
        bad.append("hyper_differs")
    if meta.get("train_streams") != exp["train"]:
        bad.append("train_streams_differ")
    fit = meta.get("fit", {})
    inits = fit.get("inits", [])
    if [i.get("stream") for i in inits] != exp["inits"] or [i.get("index") for i in inits] != list(range(hyper["inits"])):
        bad.append("init_streams_differ")
    try:
        sel = min(range(len(inits)), key=lambda k: (inits[k]["best_val_loss"], k))
        if fit.get("selected", {}).get("init") != sel:
            bad.append("selection_rule_violated")
    except (KeyError, ValueError, TypeError):
        bad.append("fit_metadata_incomplete")
    n = meta.get("n_pairs", 0)
    if fit.get("n_val_pairs") != int(mr.validation_split(n).sum()) or fit.get("split_rule") != "every 5th pair -> validation":
        bad.append("validation_split_differs")
    return bad


def require_models(mode: str, directory: Optional[Path] = None, *, seeds: Optional[List[int]] = None,
                   references_sha256: Optional[str] = None) -> Dict:
    """Load and check the models of a mode. Research: through the model freeze record."""
    proto = mc.load_protocol()
    if mode == "research":
        prec = mref.require_protocol_frozen("research models")
        if not MODEL_FREEZE.is_file():
            raise MemoryLabError("research models blocked: model freeze record missing")
        frz = json.loads(MODEL_FREEZE.read_text(encoding="utf-8"))
        directory, seeds = RESEARCH_MODELS, proto["seeds"]["research"]
        refs = mref.require_references("research")
        if (frz.get("protocol_sha256") != prec["protocol_sha256"] or frz.get("references_sha256") != refs["sha256"]
                or frz.get("code_sha256") != mc.code_sha256()):
            raise MemoryLabError("model freeze record does not match protocol/references/code")
        references_sha256 = refs["sha256"]
    elif mode == "smoke":
        mref.require_protocol_frozen("smoke models")
        directory, seeds = Path(proto["artifacts"]["smoke_dir"]), proto["seeds"]["smoke"]
        references_sha256 = mref.require_references("smoke")["sha256"]
        frz = None
    elif mode == "dev":
        if directory is None or seeds is None:
            raise MemoryLabError("dev models need a directory and the seeds")
        frz = None
    else:
        raise MemoryLabError("mode must be dev, smoke or research")
    loaded = mc.load_models(directory, mode, seeds)
    if frz is not None and frz.get("manifest_sha256") != loaded["manifest_sha256"]:
        raise MemoryLabError("manifest differs from the model freeze record")
    man = loaded["manifest"]
    binding = {k: man.get(k) for k in ("protocol_sha256", "references_sha256", "code_sha256", "m10_binding", "m11_binding",
                                       "hyper_source", "n_pairs", "condition")}
    if references_sha256 is not None and binding["references_sha256"] != references_sha256:
        raise MemoryLabError("models were not trained against these references")
    if mode != "dev" and binding["protocol_sha256"] != mc.sha(mc.PROTOCOL):
        raise MemoryLabError("models were not trained under the frozen protocol")
    pred = mc.require_predecessors_frozen()
    if binding["m10_binding"] != pred["m10"] or binding["m11_binding"] != pred["m11"]:
        raise MemoryLabError("models are bound to other M10/M11 states")
    problems = {s: provenance_problems(meta, proto, mode, s, binding) for s, (_, meta) in loaded["models"].items()}
    problems = {s: p for s, p in problems.items() if p}
    if problems:
        raise MemoryLabError(f"provenance problems: {problems}")
    return {**loaded, "directory": str(directory), "binding": binding, "file_hashes": mc.directory_hashes(directory)}


def write_model_freeze(note: str) -> Dict:
    """After the training phase: bind protocol, references, manifest and code (exclusive)."""
    prec = mref.require_protocol_frozen("model freeze")
    refs = mref.require_references("research")
    proto = mc.load_protocol()
    loaded = mc.load_models(RESEARCH_MODELS, "research", proto["seeds"]["research"])
    rec = {"schema": "mandala-memory-m12-model-freeze-v1", "frozen_unix": time.time(), "note": note,
           "protocol_sha256": prec["protocol_sha256"], "references_sha256": refs["sha256"],
           "manifest_sha256": loaded["manifest_sha256"], "code_sha256": mc.code_sha256(),
           "reviewed_code_commit": prec["reviewed_code_commit"], "seeds": proto["seeds"]["research"]}
    mc.write_json_exclusive(MODEL_FREEZE, rec)
    require_models("research")                                  # full check incl. provenance after writing
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("dev", "smoke", "research"), required=True)
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--seeds", type=int, nargs="+")
    ap.add_argument("--n-pairs", type=int)
    ap.add_argument("--refs", type=Path)
    a = ap.parse_args(argv)
    try:
        rec = training_phase() if a.mode == "research" else train(a.mode, a.out_dir, seeds=a.seeds, n_pairs=a.n_pairs, refs_path=a.refs)
    except MemoryLabError as e:
        raise SystemExit(str(e))
    print(json.dumps({k: rec[k] for k in ("mode", "status", "failures", "timing_s", "output_dir")} |
                     {"peak_rss_mib": rec["peak_rss_bytes"] / 2 ** 20, "per_seed_s": [round(p["seconds"], 1) for p in rec["per_seed"]]}, indent=1))
    return 0 if rec["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
