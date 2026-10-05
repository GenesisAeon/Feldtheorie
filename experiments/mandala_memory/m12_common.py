"""M12 shared building blocks (docs/M12_PLAN_ROBUSTHEIT.md, Fassung 2).

The Mandala is unchanged: states come from the FROZEN M10 functions. The decoders reuse the
FROZEN M11 code unchanged (MLP, validation_split, lda_rule, exact_accuracy, population_rules,
episodes); only the M12 streams and the artifact handling are new.

- own stream modes (never coinciding with M10/M11 streams),
- the 9 test conditions (research: explicit protocol list; dev: generated on the dev base),
- states per condition, train/test draws with standard-normal noise (common random numbers),
- the MLP wrapper (same selection rule and metadata as m11_readout.fit_mlp; bit-equal for
  equal streams, tested),
- model artifacts: exclusive NPZ + JSON per seed, manifest with SHA-256, strict loading
  (no pickle, exact keys/shapes/dtype, finite, std > 0, complete metadata, exact seed set).
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import zlib
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory import m11_readout as mr
from experiments.mandala_memory.core import MemoryLabError, is_drive_c

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol" / "m12_protokoll.json"
M11_PROTOCOL = HERE / "protocol" / "m11_protokoll.json"
M12_MODES = {"m12": 13, "m12dev": 14, "m12bayes": 15}       # own codes; M10 data.py / M11 modes are not touched
CASE_LABEL = "modular_N_c0"
NPZ_SHAPES = {"W1": (12, 32), "b1": (32,), "w2": (32,), "b2": (1,), "mean": (12,), "std": (12,), "lda_w": (12,), "lda_b": (1,)}
META_KEYS = ("schema", "mode", "seed", "n_pairs", "condition", "hyper", "hyper_source", "fit", "train_streams",
             "protocol_sha256", "references_sha256", "code_sha256", "m10_binding", "m11_binding")
CODE_FILES = ("m12_common.py", "m12_references.py", "m12_models.py", "m12_robust.py", "m12_evaluate.py",
              "m11_readout.py", "m11_references.py", "m11_evaluate.py", "m10_task.py", "m10_bayes.py",
              "m10_decoders.py", "core.py")


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def raw_sha(path: Path) -> str:
    """Binary files (NPZ) are hashed byte-exactly."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def code_sha256() -> Dict[str, str]:
    return {f: sha(HERE / f) for f in CODE_FILES}


def load_protocol() -> Dict:
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


def stream(mode: str, seed: int, *names):
    """Named generator plus derivation key (same construction as M11, own mode codes)."""
    if mode not in M12_MODES:
        raise MemoryLabError(f"mode must be one of {tuple(M12_MODES)}")
    key = (int(seed), M12_MODES[mode]) + tuple(zlib.crc32(str(n).encode("utf-8")) for n in names)
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(list(key)))), key


# --- bindings to the frozen predecessors ---------------------------------------------
def require_predecessors_frozen() -> Dict:
    """M10 (Mandala) and M11 (MLP procedure) must be the frozen ones -- before any state."""
    from experiments.mandala_memory import m11_references as mref
    from experiments.mandala_memory import m11_run

    m10 = mref.require_m10_frozen()
    rec = m11_run.require_frozen("m12")
    return {"m10": m10, "m11": {"m11_protocol_sha256": rec["protocol_sha256"], "m11_reviewed_code_commit": rec["reviewed_code_commit"],
                                "m11_freeze_record_sha256": sha(m11_run.FREEZE_RECORD)}}


def mlp_hyper(proto: Dict) -> Dict:
    """MLP procedure READ from the frozen M11 protocol (no new search); hash-checked."""
    src = proto["training"]["hyper_source"]
    if sha(M11_PROTOCOL) != src["m11_protocol_sha256"]:
        raise MemoryLabError("M11 protocol differs from the recorded hyperparameter source")
    h = json.loads(M11_PROTOCOL.read_text(encoding="utf-8"))["decoders"]["mlp"]
    return {**h["hyperparameters"], "hidden": h["hidden"], "inits": h["inits"]}


# --- conditions and states -------------------------------------------------------------
def conditions(proto: Dict, case_set: str) -> List[Dict]:
    """The 9 test conditions. Research/smoke: the explicit protocol list (checked against the
    factor rule); dev: generated on the development base with the same factors."""
    base = base_of(proto, case_set)
    gen = [{"name": "c0", "amplitude": base["amplitude"], "sigma": base["sigma"]}]
    for f in proto["grid"]["factors"]:
        if f != 1.0:
            a = round(base["amplitude"] * f, 10)
            gen.append({"name": f"a{a:g}", "amplitude": a, "sigma": base["sigma"]})
    for f in proto["grid"]["factors"]:
        if f != 1.0:
            s = round(base["sigma"] * f, 10)
            gen.append({"name": f"s{s:g}", "amplitude": base["amplitude"], "sigma": s})
    if case_set in ("research", "smoke"):
        listed = proto["grid"]["conditions"]
        key = lambda c: (round(c["amplitude"], 10), round(c["sigma"], 10))
        if sorted(map(key, listed)) != sorted(map(key, gen)) or len({c["name"] for c in listed}) != len(listed):
            raise MemoryLabError("protocol condition list does not follow the factor rule")
        c0 = [c for c in listed if c["name"] == "c0"]
        if len(c0) != 1 or key(c0[0]) != key(base):
            raise MemoryLabError("protocol condition list needs exactly one c0 equal to the base condition")
        return [dict(c) for c in listed]
    return gen


def base_of(proto: Dict, case_set: str) -> Dict:
    return proto["base_condition"] if case_set in ("research", "smoke") else proto["development"]["base_condition"]


def states(proto: Dict, case_set: str, amplitude: float, pats) -> np.ndarray:
    """z(s, pi) = x_(d+1) of the frozen modular tanh network with the distractor amplitude."""
    b = base_of(proto, case_set)
    m10 = mt.load_protocol()
    cond = {"X": b["X"], "Y": b["Y"], "amplitude": float(amplitude)}
    return mt.readout_states(mt.network(m10, proto["mandala"]["network"], proto["mandala"]["nonlinearity"], cond),
                             proto["mandala"]["delay"], pats)


def probabilities(pats) -> np.ndarray:
    return np.array([float(p) for _, p in pats])


# --- draws ---------------------------------------------------------------------------------
def draw(mode: str, seed: int, role: str, n_pairs: int, probs: np.ndarray, N: int = 12) -> Dict:
    """Patterns and STANDARD-normal noise from separate named streams; noise is scaled by
    sigma(c) only when episodes are formed (common random numbers across conditions)."""
    rng_p, key_p = stream(mode, seed, "pattern", role)
    rng_e, key_e = stream(mode, seed, "noise", role)
    pi = rng_p.choice(len(probs), size=n_pairs, p=probs / probs.sum())
    eps = rng_e.standard_normal(size=(n_pairs, 2, N))
    return {"pattern_index": pi, "eps": eps, "streams": [list(key_p), list(key_e)], "role": role}


def episodes(z: np.ndarray, d: Dict, n_pairs: int, sigma: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """y = z(c) + sigma(c) * eps via the frozen m11_readout.episodes."""
    return mr.episodes(z, {"pattern_index": d["pattern_index"], "noise": sigma * d["eps"]}, n_pairs)


def pair_scores(pred: np.ndarray, n_pairs: int) -> np.ndarray:
    """Per-pair contribution r = (1[A correct] + 1[B correct]) / 2 (A/B share the pattern)."""
    return 0.5 * ((pred[:n_pairs] == 0).astype(float) + (pred[n_pairs:] == 1).astype(float))


def acc_and_se(pred: np.ndarray, n_pairs: int) -> Dict:
    r = pair_scores(pred, n_pairs)
    return {"acc": float(r.mean()), "se_pair": float(r.std(ddof=1) / np.sqrt(n_pairs))}


# --- MLP wrapper (same rule as m11_readout.fit_mlp, M12 streams) ----------------------
def fit_mlp(Y, labels, pair, n_pairs: int, hyper: Dict, mode: str, seed: int, deadline=None,
            *, _stream: Callable = None, _case: str = CASE_LABEL) -> Tuple[mr.MLP, Dict]:
    """Identical procedure to m11_readout.fit_mlp; only the stream function differs. The
    private arguments exist ONLY for the bit-equality test against M11 (same streams)."""
    st = _stream or stream
    val_pairs = mr.validation_split(n_pairs)
    is_val = val_pairs[pair]
    models, infos = [], []
    for k in range(hyper["inits"]):
        rng, key = st(mode, seed, "mlp-init", _case, n_pairs, k)
        model = mr.MLP(hyper["hidden"], hyper["lr"], hyper["l2"], hyper["patience"], hyper["max_epochs"])
        info = model.fit(Y[~is_val], labels[~is_val].astype(float), Y[is_val], labels[is_val].astype(float), rng, deadline)
        models.append(model)
        infos.append({"index": k, "stream": list(key), "best_val_loss": float(info["best_val_loss"]), "epochs": int(info["epochs"])})
    sel = min(range(len(infos)), key=lambda k: (infos[k]["best_val_loss"], k))
    return models[sel], {"hyper": dict(hyper), "inits": infos, "selected": {"init": sel, "best_val_loss": infos[sel]["best_val_loss"],
                                                                           "epochs": infos[sel]["epochs"]},
                         "split_rule": "every 5th pair -> validation", "n_fit_pairs": int((~val_pairs).sum()),
                         "n_val_pairs": int(val_pairs.sum()), "n_fit_episodes": int((~is_val).sum()),
                         "n_val_episodes": int(is_val.sum()), "n_val_class_B": int((is_val & (labels == 1)).sum())}


def mlp_from_arrays(arr: Dict[str, np.ndarray], hyper: Dict) -> mr.MLP:
    m = mr.MLP(hyper["hidden"], hyper["lr"], hyper["l2"], hyper["patience"], hyper["max_epochs"])
    m.p = {k: np.array(arr[k], dtype=float, copy=True) for k in ("W1", "b1", "w2", "b2")}
    m.mean, m.std = np.array(arr["mean"], dtype=float, copy=True), np.array(arr["std"], dtype=float, copy=True)
    return m


def mlp_logits(m: mr.MLP, Y: np.ndarray) -> np.ndarray:
    return m._forward((np.asarray(Y, dtype=float) - m.mean) / m.std)[1]


# --- artifacts -------------------------------------------------------------------------
def _write_bytes_exclusive(path: Path, data: bytes) -> None:
    if is_drive_c(path):
        raise MemoryLabError("refusing to write on C:")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o644)
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)


def write_json_exclusive(path: Path, payload: Dict) -> None:
    _write_bytes_exclusive(path, (json.dumps(payload, indent=1, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))


def model_arrays(mlp: mr.MLP, lda_w: np.ndarray, lda_b: float) -> Dict[str, np.ndarray]:
    return {"W1": mlp.p["W1"], "b1": mlp.p["b1"], "w2": mlp.p["w2"], "b2": mlp.p["b2"], "mean": mlp.mean, "std": mlp.std,
            "lda_w": np.asarray(lda_w, dtype=float), "lda_b": np.array([float(lda_b)])}


def save_seed(directory: Path, seed: int, arrays: Dict[str, np.ndarray], meta: Dict) -> Dict[str, str]:
    """Exclusive NPZ + JSON; returns {file name: SHA-256}."""
    check_arrays(arrays, f"seed {seed} before saving")
    missing = [k for k in META_KEYS if k not in meta]
    if missing:
        raise MemoryLabError(f"seed {seed}: metadata incomplete before saving: {missing}")
    buf = io.BytesIO()
    np.savez(buf, **{k: np.asarray(v, dtype=np.float64) for k, v in arrays.items()})
    npz, js = Path(directory) / f"seed-{seed}.npz", Path(directory) / f"seed-{seed}.json"
    _write_bytes_exclusive(npz, buf.getvalue())
    write_json_exclusive(js, meta)
    return {npz.name: raw_sha(npz), js.name: sha(js)}


def check_arrays(arr: Dict[str, np.ndarray], what: str) -> None:
    if set(arr) != set(NPZ_SHAPES):
        raise MemoryLabError(f"{what}: keys {sorted(arr)} differ from {sorted(NPZ_SHAPES)}")
    for k, shp in NPZ_SHAPES.items():
        a = np.asarray(arr[k])
        if a.dtype != np.float64 or a.shape != shp:
            raise MemoryLabError(f"{what}: {k} has dtype {a.dtype} and shape {a.shape}, expected float64 {shp}")
        if not np.all(np.isfinite(a)):
            raise MemoryLabError(f"{what}: {k} is not finite")
    if not np.all(np.asarray(arr["std"]) > 0):
        raise MemoryLabError(f"{what}: std must be > 0")


def load_seed(directory: Path, seed: int) -> Tuple[Dict[str, np.ndarray], Dict]:
    """Strict load: no pickle, exact keys/shapes/float64, finite, std > 0, metadata complete."""
    npz, js = Path(directory) / f"seed-{seed}.npz", Path(directory) / f"seed-{seed}.json"
    with np.load(npz, allow_pickle=False) as f:
        arr = {k: np.array(f[k], copy=True) for k in f.files}
    check_arrays(arr, f"seed {seed}")
    meta = json.loads(js.read_text(encoding="utf-8"))
    missing = [k for k in META_KEYS if k not in meta]
    if missing:
        raise MemoryLabError(f"seed {seed}: metadata incomplete: {missing}")
    if meta["seed"] != seed:
        raise MemoryLabError(f"seed {seed}: metadata belongs to seed {meta['seed']}")
    return arr, meta


def write_manifest(directory: Path, mode: str, seeds: List[int], files: Dict[str, str], binding: Dict) -> Path:
    path = Path(directory) / "manifest.json"
    write_json_exclusive(path, {"schema": "mandala-memory-m12-models-manifest-v1", "mode": mode, "seeds": list(seeds),
                                "files": dict(sorted(files.items())), **binding})
    return path


def load_models(directory: Path, mode: str, expected_seeds: List[int]) -> Dict:
    """Manifest with exactly the expected seeds and files, every file hash-checked and
    strictly loaded. Returns {'manifest', 'manifest_sha256', 'models': {seed: (arrays, meta)}}."""
    directory = Path(directory)
    man_path = directory / "manifest.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    if man.get("mode") != mode:
        raise MemoryLabError(f"manifest mode {man.get('mode')!r} is not {mode!r}")
    if list(man.get("seeds", [])) != list(expected_seeds):
        raise MemoryLabError(f"manifest seeds {man.get('seeds')} differ from the protocol seeds {list(expected_seeds)}")
    expected_files = {f"seed-{s}.{ext}" for s in expected_seeds for ext in ("npz", "json")}
    if set(man.get("files", {})) != expected_files:
        raise MemoryLabError("manifest files differ from exactly one NPZ + JSON per protocol seed")
    on_disk = {p.name for p in directory.iterdir() if p.name != "manifest.json"}
    if on_disk != expected_files:
        raise MemoryLabError(f"model directory content differs from the manifest: {sorted(on_disk ^ expected_files)}")
    for name, h in man["files"].items():
        got = raw_sha(directory / name) if name.endswith(".npz") else sha(directory / name)
        if got != h:
            raise MemoryLabError(f"{name}: SHA-256 differs from the manifest")
    models = {s: load_seed(directory, s) for s in expected_seeds}
    for s, (_, meta) in models.items():
        if meta["mode"] != mode:
            raise MemoryLabError(f"seed {s}: metadata mode {meta['mode']!r} is not {mode!r}")
    return {"manifest": man, "manifest_sha256": sha(man_path), "models": models}


def directory_hashes(directory: Path) -> Dict[str, str]:
    return {p.name: raw_sha(p) for p in sorted(Path(directory).iterdir())}
