"""LR5 artifact chain (plan section 12; review REVIEW_LR4 / LANTERN_LR4_NACHREVIEW LR5 duties).

* Canonical identities: canonical JSON (sorted keys, no NaN) -> SHA-256. A MODEL identity covers the decoder's
  complete metadata including the canonical identity of every array (decoders._json_meta), so arrays and
  metadata are bound TOGETHER; a CELL record binds that model identity to its expected cell (study, context,
  condition, control, task, time, dt) and to the run identity. The NPZ container bytes are recorded too, but
  they are not the identity (ZIP time stamps).
* Exclusive, atomic writes: write a temp file in the target folder, flush + fsync, then os.link() it to the
  final name -- link fails if the name exists, so NOTHING is ever overwritten -- and remove the temp file.
  A crash leaves at most a '.tmp-*' file, which is never a valid artifact.
* Model integrity: evaluate_with_integrity() checks the model identity against the expected one before AND
  after scoring.
The external anchor of all expected identities is the run's cell records (runs.py), not the files beside them."""
from __future__ import annotations

import hashlib
import io
import json
import os
import uuid
from pathlib import Path
from typing import Dict, Mapping

import numpy as np

from experiments.lantern_reconstruction import decoders


class IntegrityError(ValueError):
    pass


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(obj) -> str:
    return sha256(canonical_json(obj))


def write_exclusive(path: Path, data: bytes) -> str:
    """Atomic and exclusive: the final name appears complete or not at all, and an existing file is never
    replaced (FileExistsError). Returns the SHA-256 of the bytes."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"{path} exists already (artifacts are never overwritten)")
    tmp = path.with_name(f".{path.name}.tmp-{uuid.uuid4().hex}")
    try:
        with open(tmp, "xb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.link(tmp, path)                     # atomic; raises FileExistsError if the name was taken meanwhile
    finally:
        if tmp.exists():
            tmp.unlink()
    return sha256(data)


def write_json_exclusive(path: Path, obj) -> str:
    return write_exclusive(path, json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n")


def read_verified(path: Path, expected_sha256: str) -> bytes:
    data = Path(path).read_bytes()
    if sha256(data) != expected_sha256:
        raise IntegrityError(f"{path} does not match its recorded SHA-256")
    return data


# --- models ------------------------------------------------------------------------------------------------
def model_identity(model: decoders.RidgeDecoder) -> str:
    """Arrays (canonical identities) and metadata of a decoder, bound together."""
    decoders.check_decoder(model)
    return identity(decoders._json_meta(model))


def array_identity(name: str, a: np.ndarray) -> str:
    return decoders.array_identity(name, np.asarray(a))


def model_npz_bytes(model: decoders.RidgeDecoder) -> bytes:
    buf = io.BytesIO()
    np.savez(buf, **{k: np.ascontiguousarray(getattr(model, k)) for k in decoders.ARRAYS})
    return buf.getvalue()


def save_model_exclusive(model: decoders.RidgeDecoder, folder: Path, stem: str) -> Dict:
    """NPZ (numeric arrays, no pickle) + JSON metadata, each written exclusively; returns the record part."""
    folder = Path(folder)
    npz_sha = write_exclusive(folder / f"{stem}.npz", model_npz_bytes(model))
    meta = decoders._json_meta(model)
    json_sha = write_json_exclusive(folder / f"{stem}.json", meta)
    return {"model_identity": identity(meta), "npz": f"{stem}.npz", "npz_sha256": npz_sha, "json": f"{stem}.json", "json_sha256": json_sha}


def load_model_verified(folder: Path, record: Mapping, ctx=None, task=None, **cell) -> decoders.RidgeDecoder:
    """File bytes against the record, then decoders.load (schema/values/array identities), then the model
    identity against the record, then -- if a context is given -- the binding to the expected cell."""
    folder = Path(folder)
    read_verified(folder / record["npz"], record["npz_sha256"])
    read_verified(folder / record["json"], record["json_sha256"])
    model = decoders.load(folder / Path(record["npz"]).stem)
    if model_identity(model) != record["model_identity"]:
        raise IntegrityError("model identity differs from the recorded one")
    if ctx is not None:
        decoders.check_decoder_for(model, ctx, task, **cell)
    return model


def evaluate_with_integrity(model: decoders.RidgeDecoder, expected_identity: str, X_test, U_test) -> Dict:
    """Score a model only if its identity equals the expected one before AND after the evaluation."""
    from experiments.lantern_reconstruction.evaluate import score_cell

    if model_identity(model) != expected_identity:
        raise IntegrityError("model identity before evaluation differs from the expected one")
    res = score_cell(model, X_test, U_test)
    if model_identity(model) != expected_identity:
        raise IntegrityError("model changed during evaluation")
    return res


def save_arrays_exclusive(path: Path, **arrays) -> Dict:
    """Prediction/target arrays of a cell (numeric NPZ) with canonical array identities."""
    buf = io.BytesIO()
    np.savez(buf, **{k: np.ascontiguousarray(v, dtype=np.float64) for k, v in arrays.items()})
    return {"file": Path(path).name, "sha256": write_exclusive(path, buf.getvalue()),
            "arrays": {k: array_identity(k, np.asarray(v, dtype=np.float64)) for k, v in arrays.items()}}


def load_arrays_verified(folder: Path, record: Mapping) -> Dict[str, np.ndarray]:
    read_verified(Path(folder) / record["file"], record["sha256"])
    with np.load(Path(folder) / record["file"], allow_pickle=False) as z:
        if sorted(z.files) != sorted(record["arrays"]):
            raise IntegrityError("array file does not hold exactly the recorded arrays")
        out = {k: z[k] for k in z.files}
    for k, a in out.items():
        if a.dtype != np.float64 or array_identity(k, a) != record["arrays"][k]:
            raise IntegrityError(f"array {k!r} does not match its recorded identity")
    return out
