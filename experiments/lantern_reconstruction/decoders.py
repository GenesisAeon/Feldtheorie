"""LR4 decoder artifact, prediction and numeric round trip (plan sections 8, 11, 12).

predict() sees ONLY the artifact and the feature matrix: no target, seed, episode counter, model index or
content label (plan 10). This module contains no fit function; fitting lives in training.py, so the
evaluator (evaluate.py) can import prediction without importing any training code (plan 11).

Storage: an NPZ with purely numeric arrays (loaded with allow_pickle=False) plus strict JSON (no
NaN/Infinity, no duplicate keys) holding the metadata and a canonical identity hash per array
(name, dtype incl. byte order, shape, C-order bytes). The NPZ container bytes are NOT the identity:
ZIP time stamps may differ for equal arrays (plan 12)."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

SCHEMA = "lantern-ridge-decoder-v1"
OBJECTIVE = "(1/N) ||X_s W + 1 b^T - U||_F^2 + lambda ||W||_F^2  (X_s standardised features; intercept b unpenalised)"
STANDARDISATION = "mean and population SD (ddof 0) of the TRAINING features only; a column with SD exactly 0 gets scale 1"
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
    a = np.array(a, dtype=np.float64, copy=True)
    a.setflags(write=False)
    return a


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
        check_decoder(self)

    @property
    def n_features(self) -> int:
        return int(self.mean.shape[0])


def check_decoder(m: RidgeDecoder) -> None:
    d = m.mean.shape[0] if m.mean.ndim == 1 else -1
    if m.schema != SCHEMA or m.task not in ("A", "B"):
        raise ValueError("unknown decoder schema or task")
    shapes = {"mean": (d,), "scale": (d,), "W": (d, 4), "b": (4,), "val_mse": m.lambda_grid.shape}
    if d < 1 or m.lambda_grid.ndim != 1 or m.lambda_grid.size < 1 or any(getattr(m, k).shape != s for k, s in shapes.items()):
        raise ValueError("decoder arrays have inconsistent shapes")
    if not all(np.all(np.isfinite(getattr(m, k))) for k in ARRAYS) or np.any(m.scale <= 0):
        raise ValueError("decoder arrays must be finite with positive scales")
    if not isinstance(m.lam, float) or m.lam != select_lambda(m.lambda_grid, m.val_mse):
        raise ValueError("the stored lambda must be the selection rule's choice from the stored validation MSEs")
    if 2 * len(m.feature_definition.get("nodes", ())) != d:
        raise ValueError("feature definition does not match the number of features")


def predict(model: RidgeDecoder, X) -> np.ndarray:
    """RAW predictions (n, 4) = ((X - mean) / scale) W + b. Projection is a separate, fixed step (metrics.project)."""
    x = np.asarray(X)
    if x.dtype.kind not in "iuf" or x.ndim != 2 or x.shape[0] < 1 or x.shape[1] != model.n_features or not np.all(np.isfinite(x)):
        raise ValueError(f"features must be a finite real (n, {model.n_features}) array (got {x.dtype}, {x.shape})")
    return ((x - model.mean) / model.scale) @ model.W + model.b


# --- round trip -------------------------------------------------------------------------------------
def _json_meta(m: RidgeDecoder) -> Dict:
    return {"schema": m.schema, "task": m.task, "feature_definition": m.feature_definition, "lambda": m.lam,
            "n_train": m.n_train, "n_val": m.n_val, "provenance": m.provenance, "software": m.software,
            "objective": OBJECTIVE, "standardisation": STANDARDISATION, "selection": SELECTION, "projection": PROJECTION,
            "arrays": {k: array_identity(k, getattr(m, k)) for k in ARRAYS}}


def save(m: RidgeDecoder, stem: Path) -> Tuple[Path, Path]:
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
    m = RidgeDecoder(meta["task"], meta["feature_definition"], arrays["mean"], arrays["scale"], arrays["W"], arrays["b"],
                     float(meta["lambda"]), arrays["lambda_grid"], arrays["val_mse"], meta["n_train"], meta["n_val"],
                     meta["provenance"], meta["software"])
    if _json_meta(m) != meta:
        raise ValueError("decoder metadata does not round-trip exactly")
    return m
