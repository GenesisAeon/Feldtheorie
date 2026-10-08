"""LR4 decoder artifact, prediction and numeric round trip (plan sections 8, 11, 12).

predict() sees ONLY the artifact and the feature matrix: no target, seed, episode counter, model index or
content label (plan 10). This module contains no fit function; fitting lives in training.py, so the
evaluator (evaluate.py) can import prediction without importing any training code (plan 11).

Storage: an NPZ with purely numeric arrays (loaded with allow_pickle=False) plus strict JSON (no
NaN/Infinity, no duplicate keys) holding the metadata and a canonical identity hash per array
(name, dtype incl. byte order, shape, C-order bytes). The NPZ container bytes are NOT the identity:
ZIP time stamps may differ for equal arrays (plan 12).

What this does NOT do (review REVIEW_LR4 R2): the array identities stored NEXT TO the arrays do not
authenticate the metadata file -- a syntactically valid but different context id cannot be recognised from
the JSON alone. check_decoder() validates schema and values; check_decoder_for() binds a model to the
expected context and cell. External model/manifest identity, exclusive writes and provenance binding
belong to the LR5 artifact chain; this module is not yet a complete protection against manipulation."""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Dict, Mapping, Tuple

import numpy as np

SCHEMA = "lantern-ridge-decoder-v1"
OBJECTIVE = "(1/N) ||X_s W + 1 b^T - U||_F^2 + lambda ||W||_F^2  (X_s standardised features; intercept b unpenalised)"
STANDARDISATION = ("mean and population SD (ddof 0) of the TRAINING features only; an exactly constant column "
                   "(all values identical) gets mean = its value and scale 1")
FEATURE_ORDER = "[sin(d_1..d_m), cos(d_1..d_m)], d_k = y_node_k - y_reference (observation.observe)"
N_NODES = 34
N_TASK_NODES = {"A": 33, "B": 8}
MAX_PROJECTED_MSE = 4.0          # projected predictions and targets lie in [-1, 1]
SELECTION = "smallest validation MSE of the PROJECTED predictions; on an exactly equal value the larger lambda"
PROJECTION = "main loss on predictions clipped to [-1, 1]; raw predictions are kept"
ARRAYS = ("mean", "scale", "W", "b", "lambda_grid", "val_mse")


def array_identity(name: str, a: np.ndarray) -> str:
    a = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(json.dumps({"name": name, "dtype": a.dtype.str, "shape": list(a.shape)}, sort_keys=True).encode("utf-8"))
    h.update(a.tobytes(order="C"))
    return h.hexdigest()


def select_lambda(lambda_grid, val_mse) -> float:
    """The fixed selection rule: smallest validation MSE; on an EXACTLY equal value the larger lambda."""
    grid, mse = [float(x) for x in lambda_grid], [float(x) for x in val_mse]
    if not grid or len(grid) != len(mse):
        raise ValueError("one validation MSE per lambda is required")
    return grid[min(range(len(grid)), key=lambda k: (mse[k], -grid[k]))]


def _ro(a) -> np.ndarray:
    """Read-only float64 copy on an IMMUTABLE bytes buffer: setflags(write=True) is refused by NumPy
    (review REVIEW_LR4: a plain write flag could be switched back on and W changed)."""
    src = np.array(a, dtype=np.float64, copy=True)
    return np.frombuffer(np.ascontiguousarray(src).tobytes(), dtype=np.float64).reshape(src.shape)


def _true_int(x) -> bool:
    return isinstance(x, (int, np.integer)) and not isinstance(x, (bool, np.bool_))


def _json_scalar(x) -> bool:
    if isinstance(x, float):
        return math.isfinite(x)
    return x is None or isinstance(x, (str, bool, int))


def _freeze_feature_definition(fd) -> Mapping:
    if not isinstance(fd, Mapping) or set(fd) != {"task", "nodes", "reference", "order"}:
        raise ValueError("feature_definition must have exactly the keys task, nodes, reference, order")
    nodes = fd["nodes"]
    if not isinstance(nodes, (list, tuple)):
        raise ValueError("feature_definition.nodes must be a list of node indices")
    return MappingProxyType({"task": fd["task"], "nodes": tuple(nodes), "reference": fd["reference"], "order": fd["order"]})


def _freeze_flat(d, what: str) -> Mapping:
    if not isinstance(d, Mapping) or not all(isinstance(k, str) and _json_scalar(v) for k, v in d.items()):
        raise ValueError(f"{what} must map strings to finite JSON scalars")
    return MappingProxyType(dict(d))


@dataclass(frozen=True)
class RidgeDecoder:
    task: str
    feature_definition: Dict          # observation spec (task, nodes, reference) and feature order
    mean: np.ndarray                  # (d,)
    scale: np.ndarray                 # (d,)
    W: np.ndarray                     # (d, 4), standardised feature space
    b: np.ndarray                     # (4,)
    lam: float
    lambda_grid: np.ndarray           # (k,)
    val_mse: np.ndarray               # (k,) one value per lambda of the grid
    n_train: int
    n_val: int
    provenance: Dict = field(default_factory=dict)   # study/context/condition/time/hashes; never a generator
    software: Dict = field(default_factory=dict)
    schema: str = SCHEMA

    def __post_init__(self):
        for name in ARRAYS:
            object.__setattr__(self, name, _ro(getattr(self, name)))
        object.__setattr__(self, "feature_definition", _freeze_feature_definition(self.feature_definition))
        object.__setattr__(self, "provenance", _freeze_flat(self.provenance, "provenance"))
        object.__setattr__(self, "software", _freeze_flat(self.software, "software"))
        check_decoder(self)

    @property
    def n_features(self) -> int:
        return int(self.mean.shape[0])


def check_decoder(m: RidgeDecoder) -> None:
    """Context-free schema and value check (review REVIEW_LR4 R2); runs on construction AND on load."""
    if m.schema != SCHEMA or not isinstance(m.task, str) or m.task not in N_TASK_NODES:
        raise ValueError("unknown decoder schema or task")
    for name in ("n_train", "n_val"):
        v = getattr(m, name)
        if not _true_int(v) or v < 1:
            raise ValueError(f"{name} must be a positive integer (got {v!r})")
    fd = m.feature_definition
    nodes, ref = fd["nodes"], fd["reference"]
    if fd["task"] != m.task or fd["order"] != FEATURE_ORDER:
        raise ValueError("feature_definition task/order do not match the decoder")
    if (not all(_true_int(i) and 0 <= i < N_NODES for i in nodes) or len(set(nodes)) != len(nodes)
            or len(nodes) != N_TASK_NODES[m.task]):
        raise ValueError(f"feature nodes must be {N_TASK_NODES[m.task]} distinct integer node indices in [0, 34)")
    if not (_true_int(ref) and 0 <= ref < N_NODES) or ref in nodes:
        raise ValueError("the reference must be an integer node index in [0, 34) outside the feature nodes")
    if m.task == "A" and tuple(nodes) != tuple(i for i in range(N_NODES) if i != ref):
        raise ValueError("task A observes all non-reference nodes in ascending order")
    d = m.mean.shape[0] if m.mean.ndim == 1 else -1
    shapes = {"mean": (d,), "scale": (d,), "W": (d, 4), "b": (4,), "val_mse": m.lambda_grid.shape}
    if d != 2 * len(nodes) or m.lambda_grid.ndim != 1 or m.lambda_grid.size < 1 or any(getattr(m, k).shape != s for k, s in shapes.items()):
        raise ValueError("decoder arrays have inconsistent shapes or do not match the feature definition")
    if not all(np.all(np.isfinite(getattr(m, k))) for k in ARRAYS) or np.any(m.scale <= 0):
        raise ValueError("decoder arrays must be finite with positive scales")
    grid = m.lambda_grid.tolist()
    if any(v <= 0 for v in grid) or len(set(grid)) != len(grid):
        raise ValueError("the lambda grid must hold distinct positive values")
    if np.any(m.val_mse < 0) or np.any(m.val_mse > MAX_PROJECTED_MSE):
        raise ValueError("validation MSEs of projected predictions must lie in [0, 4]")
    if not isinstance(m.lam, float) or m.lam != select_lambda(m.lambda_grid, m.val_mse):
        raise ValueError("the stored lambda must be the selection rule's choice from the stored validation MSEs")


def check_decoder_for(m: RidgeDecoder, ctx, task: str, **cell) -> None:
    """Context-bound semantics at the validated entry: the model must belong to THIS context's observation
    spec (exact node order and reference) and carry its study/context/fingerprint/configuration; extra
    keyword arguments (condition=, time=, ...) must equal the provenance entries. This binds against an
    EXPECTED cell; it cannot detect a consistent forgery -- that is the LR5 external manifest."""
    from experiments.lantern_reconstruction import observation, streams
    from experiments.lantern_reconstruction.contexts import fingerprint

    spec = observation.observation_spec(ctx, task)
    check_decoder(m)
    if m.task != task or tuple(m.feature_definition["nodes"]) != spec.nodes or m.feature_definition["reference"] != spec.reference:
        raise ValueError("decoder does not belong to this context's observation spec")
    expected = {"study_id": ctx.study_id, "context_id": ctx.context_id, "context_fingerprint": fingerprint(ctx),
                "config_sha256": streams.config_sha256(), "task": task, **cell}
    wrong = {k: m.provenance.get(k, "<missing>") for k, v in expected.items() if m.provenance.get(k, "<missing>") != v}
    if wrong:
        raise ValueError(f"decoder provenance does not match the expected cell: {wrong}")


def predict(model: RidgeDecoder, X) -> np.ndarray:
    """RAW predictions (n, 4) = ((X - mean) / scale) W + b. Projection is a separate, fixed step (metrics.project)."""
    x = np.asarray(X)
    if x.dtype.kind not in "iuf" or x.ndim != 2 or x.shape[0] < 1 or x.shape[1] != model.n_features or not np.all(np.isfinite(x)):
        raise ValueError(f"features must be a finite real (n, {model.n_features}) array (got {x.dtype}, {x.shape})")
    return ((x - model.mean) / model.scale) @ model.W + model.b


# --- round trip -------------------------------------------------------------------------------------
def _json_meta(m: RidgeDecoder) -> Dict:
    fd = m.feature_definition
    return {"schema": m.schema, "task": m.task,
            "feature_definition": {"task": fd["task"], "nodes": list(fd["nodes"]), "reference": fd["reference"], "order": fd["order"]},
            "lambda": m.lam, "n_train": m.n_train, "n_val": m.n_val, "provenance": dict(m.provenance), "software": dict(m.software),
            "objective": OBJECTIVE, "standardisation": STANDARDISATION, "selection": SELECTION, "projection": PROJECTION,
            "arrays": {k: array_identity(k, getattr(m, k)) for k in ARRAYS}}


def save(m: RidgeDecoder, stem: Path) -> Tuple[Path, Path]:
    """Development helper. It OVERWRITES existing files and writes no manifest: freeze artifacts must use the
    LR5 persistence path (exclusive/atomic writes, full manifest, external identity), never this helper."""
    stem = Path(stem)
    npz, js = stem.with_suffix(".npz"), stem.with_suffix(".json")
    np.savez(npz, **{k: np.ascontiguousarray(getattr(m, k)) for k in ARRAYS})
    js.write_text(json.dumps(_json_meta(m), indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return npz, js


def load(stem: Path) -> RidgeDecoder:
    """Strict: no pickle, exactly the expected arrays, float64, identities equal to the JSON, schema checked."""
    from experiments.lantern_reconstruction.registry_adapter import strict_json

    stem = Path(stem)
    meta = strict_json(stem.with_suffix(".json").read_text(encoding="utf-8"))
    if meta.get("schema") != SCHEMA:
        raise ValueError("unknown decoder schema")
    with np.load(stem.with_suffix(".npz"), allow_pickle=False) as z:
        if sorted(z.files) != sorted(ARRAYS):
            raise ValueError(f"decoder NPZ must contain exactly {sorted(ARRAYS)}")
        arrays = {k: z[k] for k in ARRAYS}
    for k, a in arrays.items():
        if a.dtype != np.float64 or array_identity(k, a) != meta["arrays"][k]:
            raise ValueError(f"decoder array {k!r} does not match its recorded identity")
    lam = meta.get("lambda")
    if isinstance(lam, bool) or not isinstance(lam, (int, float)):
        raise ValueError("lambda must be a JSON number")
    m = RidgeDecoder(meta["task"], meta["feature_definition"], arrays["mean"], arrays["scale"], arrays["W"], arrays["b"],
                     float(lam), arrays["lambda_grid"], arrays["val_mse"], meta["n_train"], meta["n_val"],
                     meta["provenance"], meta["software"])
    if _json_meta(m) != meta:
        raise ValueError("decoder metadata does not round-trip exactly")
    return m
