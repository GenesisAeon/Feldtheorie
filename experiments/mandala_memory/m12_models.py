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
import math
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


# --- provenance and loading for the evaluation (review M12-R8) ------------------------------
BINDING_KEYS = ("protocol_sha256", "references_sha256", "code_sha256", "m10_binding", "m11_binding", "hyper_source", "n_pairs", "condition")


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _is_finite_nonneg(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x >= 0


def expected_binding(mode: str, proto: Dict, references_sha256: Optional[str], n_pairs: Optional[int] = None) -> Dict:
    """Expected provenance derived INDEPENDENTLY of the manifest: protocol, references, current
    (= frozen, for research/smoke) code, frozen predecessors, protocol hyper source, protocol n,
    and the c0 base condition of the mode."""
    case_set = "dev" if mode == "dev" else ("research" if mode == "research" else "smoke")
    base = mc.base_of(proto, case_set)
    pred = mc.require_predecessors_frozen()
    n = proto["training"]["n_pairs"] if mode != "dev" else n_pairs
    return {"protocol_sha256": mc.sha(mc.PROTOCOL), "references_sha256": references_sha256, "code_sha256": mc.code_sha256(),
            "m10_binding": pred["m10"], "m11_binding": pred["m11"], "hyper_source": proto["training"]["hyper_source"],
            "n_pairs": n, "condition": {"name": "c0", **{k: base[k] for k in ("X", "Y", "amplitude", "sigma")}}}


def fit_schema_problems(fit, n: int, hyper: Dict, exp_init_streams: List) -> List[str]:
    """Complete fit schema: finite valid losses, admissible epochs, init streams/indices,
    selection incl. tie-break, consistent selected metadata, exact fit/validation counts."""
    if not isinstance(fit, dict):
        return ["fit_metadata_missing"]
    bad = []
    if fit.get("hyper") != hyper:
        bad.append("fit_hyper_differs")
    inits = fit.get("inits")
    if not isinstance(inits, list) or len(inits) != hyper["inits"]:
        return bad + ["inits_incomplete"]
    for k, i in enumerate(inits):
        if not isinstance(i, dict) or i.get("index") != k or not _is_int(i.get("index")):
            bad.append(f"init_{k}_index")
            continue
        if i.get("stream") != exp_init_streams[k]:
            bad.append(f"init_{k}_stream")
        if not _is_finite_nonneg(i.get("best_val_loss")):
            bad.append(f"init_{k}_val_loss_not_finite")
        ep = i.get("epochs")
        if not _is_int(ep) or not 1 <= ep <= hyper["max_epochs"]:
            bad.append(f"init_{k}_epochs_invalid")
    if bad:
        return bad
    sel = min(range(len(inits)), key=lambda k: (inits[k]["best_val_loss"], k))
    chosen = fit.get("selected")
    if not isinstance(chosen, dict) or chosen.get("init") != sel or not _is_int(chosen.get("init")):
        bad.append("selection_rule_violated")
    elif chosen.get("best_val_loss") != inits[sel]["best_val_loss"] or chosen.get("epochs") != inits[sel]["epochs"]:
        bad.append("selected_metadata_inconsistent")
    n_val = int(mr.validation_split(n).sum())
    want = {"split_rule": "every 5th pair -> validation", "n_fit_pairs": n - n_val, "n_val_pairs": n_val,
            "n_fit_episodes": 2 * (n - n_val), "n_val_episodes": 2 * n_val, "n_val_class_B": n_val}
    for k, v in want.items():
        if fit.get(k) != v or (k != "split_rule" and not _is_int(fit.get(k))):
            bad.append(f"{k}_differs")
    return bad


def provenance_problems(meta: Dict, proto: Dict, mode: str, seed: int, expected: Dict) -> List[str]:
    """`expected` comes from expected_binding() -- never from the manifest itself."""
    smode = proto["modes"][mode]
    hyper = mc.mlp_hyper(proto)
    bad = [f"{k}_differs" for k in BINDING_KEYS if meta.get(k) != expected.get(k)]
    n = expected.get("n_pairs")
    if not _is_int(n) or n < 5:
        return bad + ["n_pairs_invalid"]
    if meta.get("mode") != mode or meta.get("seed") != seed or meta.get("schema") != SCHEMA_META:
        bad.append("identity_differs")
    if meta.get("hyper") != hyper:
        bad.append("hyper_differs")
    exp = expected_keys(smode, seed, n, hyper["inits"])
    if meta.get("train_streams") != exp["train"]:
        bad.append("train_streams_differ")
    return bad + fit_schema_problems(meta.get("fit"), n, hyper, exp["inits"])


def _checked(mode: str, directory: Path, seeds: List[int], references_sha256: Optional[str]) -> Dict:
    """Full check of a model directory against the independently derived provenance."""
    proto = mc.load_protocol()
    loaded = mc.load_models(directory, mode, seeds)
    man = loaded["manifest"]
    n_dev = man.get("n_pairs") if mode == "dev" else None
    expected = expected_binding(mode, proto, references_sha256, n_dev)
    man_bad = [f"manifest_{k}_differs" for k in BINDING_KEYS if man.get(k) != expected[k]]
    if man_bad:
        raise MemoryLabError(f"manifest provenance problems: {man_bad}")
    problems = {s: provenance_problems(meta, proto, mode, s, expected) for s, (_, meta) in loaded["models"].items()}
    problems = {s: p for s, p in problems.items() if p}
    if problems:
        raise MemoryLabError(f"provenance problems: {problems}")
    return {**loaded, "directory": str(directory), "binding": expected, "file_hashes": mc.directory_hashes(directory)}


def require_models(mode: str, directory: Optional[Path] = None, *, seeds: Optional[List[int]] = None,
                   references_sha256: Optional[str] = None) -> Dict:
    """Load and check the models of a mode. Research: through the model freeze record."""
    proto = mc.load_protocol()
    if mode == "research":
        prec = mref.require_protocol_frozen("research models")
        if not MODEL_FREEZE.is_file():
            raise MemoryLabError("research models blocked: model freeze record missing")
        frz = json.loads(MODEL_FREEZE.read_text(encoding="utf-8"))
        refs = mref.require_references("research")
        if (frz.get("protocol_sha256") != prec["protocol_sha256"] or frz.get("references_sha256") != refs["sha256"]
                or frz.get("code_sha256") != mc.code_sha256()):
            raise MemoryLabError("model freeze record does not match protocol/references/code")
        out = _checked("research", RESEARCH_MODELS, proto["seeds"]["research"], refs["sha256"])
        if frz.get("manifest_sha256") != out["manifest_sha256"] or frz.get("file_hashes") != out["file_hashes"]:
            raise MemoryLabError("manifest or model files differ from the model freeze record")
        return out
    if mode == "smoke":
        mref.require_protocol_frozen("smoke models")
        return _checked("smoke", Path(proto["artifacts"]["smoke_dir"]), proto["seeds"]["smoke"], mref.require_references("smoke")["sha256"])
    if mode == "dev":
        if directory is None or seeds is None:
            raise MemoryLabError("dev models need a directory and the seeds")
        return _checked("dev", Path(directory), seeds, references_sha256 if references_sha256 is not None
                        else json.loads((Path(directory) / "manifest.json").read_text(encoding="utf-8")).get("references_sha256"))
    raise MemoryLabError("mode must be dev, smoke or research")


def npz_git_identity_problems(directory: Path = None) -> List[str]:
    """Every NPZ must be committed and its git blob byte-identical to the file (no line-ending
    conversion; .gitattributes marks the research NPZ as binary)."""
    import hashlib
    import subprocess

    directory = Path(directory or RESEARCH_MODELS)
    top = subprocess.run(["git", "-C", str(directory), "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    bad = []
    for f in sorted(directory.glob("*.npz")):
        rel = f.resolve().relative_to(Path(top).resolve()).as_posix()
        attr = subprocess.run(["git", "-C", top, "check-attr", "binary", "--", rel], capture_output=True, text=True).stdout
        if not attr.strip().endswith("binary: set"):
            bad.append(f"{f.name}: not marked binary")
        blob = subprocess.run(["git", "-C", top, "show", f"HEAD:{rel}"], capture_output=True)
        if blob.returncode != 0:
            bad.append(f"{f.name}: not committed")
        elif hashlib.sha256(blob.stdout).hexdigest() != mc.raw_sha(f):
            bad.append(f"{f.name}: git blob differs from the file")
    return bad


def write_model_freeze(note: str) -> Dict:
    """After the training phase: FULL validation first (review M12-R8), then the exclusive
    record binding protocol, references, manifest, model file hashes and code."""
    prec = mref.require_protocol_frozen("model freeze")
    refs = mref.require_references("research")
    proto = mc.load_protocol()
    checked = _checked("research", RESEARCH_MODELS, proto["seeds"]["research"], refs["sha256"])
    rec = {"schema": "mandala-memory-m12-model-freeze-v1", "frozen_unix": time.time(), "note": note,
           "protocol_sha256": prec["protocol_sha256"], "references_sha256": refs["sha256"],
           "manifest_sha256": checked["manifest_sha256"], "file_hashes": checked["file_hashes"], "code_sha256": mc.code_sha256(),
           "reviewed_code_commit": prec["reviewed_code_commit"], "seeds": proto["seeds"]["research"]}
    mc.write_json_exclusive(MODEL_FREEZE, rec)
    require_models("research")
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
