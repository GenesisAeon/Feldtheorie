"""LR1 registry adapter: validated, immutable, canonically ordered snapshot of the Lantern registry.

This module NEVER imports the legacy code (v9_alpha, models): the research path loads only the
verified snapshot artifact, so the global-RNG side effects of the legacy import stay outside it.

Hash notions are kept apart (plan section 12):
- raw_sha256          bytes of the working-tree file (CRLF on Windows checkouts),
- lf_sha256           raw bytes with CRLF -> LF (declared text sources only),
- blob_sha256         SHA-256 of the git blob bytes at HEAD,
- container_sha256    bytes of the stored NPZ file (zip metadata may differ for equal arrays),
- canonical_sha256    schema + IDs + node metadata + key/shape/'<f8' + C-order array bytes.

Canonical order: lexicographically sorted IDs; ALL arrays are permuted jointly. The coupling
matrix is checked against an INDEPENDENT reconstruction of the formula from the YAML values.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REGISTRY_REL = "v9_alpha/config/lantern_hub.yaml"
SNAPSHOT_SCHEMA = "lantern-registry-snapshot-v1"
ARRAY_KEYS = ("C", "beta", "theta_threshold", "frequency_hz", "impedance_z", "kappa_photonic", "kappa_em", "kappa_metabolic", "wavelength_cm")
NODE_KEYS = ARRAY_KEYS[1:]
META_KEYS = ("name", "type", "domain", "status", "readiness")
N_NODES = 34
FORMULA_TOL = 1e-14
# Constants as READ in models/unified_constants.py (blob pinned below); not imported.
ALPHA_INV_REF = 137.03599206
PHI_REF = (1.0 + math.sqrt(5.0)) / 2.0
F0_HZ = 13.5e6

# Expected git-blob SHA-256 of the eleven sources (QUELLENINVENTAR.json, 2026-10-06; LR0 verified 11/11).
SOURCES: Dict[str, str] = {
    "v9_alpha/api/lantern_bridge.py": "db45f76fbae6c1a23be547f5ddf19d64f410f9d54ea4cdb628da2943903c54d4",
    "v9_alpha/config/lantern_hub.yaml": "5622d38e1ab5306fc69b34d87694ee0b4797f7e102dc1f48477fd907ffe16786",
    "v9_alpha/models/phase_dynamics.py": "3ad681d428d53e7b73692983904a53f80257c02e48b200b76e6e3982f22f259d",
    "v9_alpha/main_simulation.py": "3640adac4f470e8e5f562fece5f4f2362bf2d84c5a9f42c9ede812e6ba85a269",
    "v9_alpha/api/__init__.py": "c217104d6f8e9463e063f12b39d7cdd2540c708f77ed6f8d9bcbf97b4cbc1b08",
    "v9_alpha/models/__init__.py": "fc348d7d7a442cfb6c142dd2d91e31ac9f19e02d54796484e1f197c85ea91b61",
    "models/__init__.py": "29ead0d03887d8f96b44f60932a922dfa1359ed414a5e3496ef2ac1ce1be759b",
    "models/collective_field.py": "abf4fe84fc2826408e919883b24ded2f90b3b6e482b9d247e23a19575971053e",
    "models/consciousness_integration.py": "7a3224f179db41f522c5eb4521766fa07a1b523f09de79a4b104cb291b01d3dc",
    "models/unified_constants.py": "e7c76ae6b7edb38f86692f7146d10a9a4342065ecab286b67427f888d7904bde",
    "v9_alpha/tests/test_lantern_bridge.py": "723f60634eb515eede0a6c2db21f8e0a81b305cde56c26c59d6ce788b66248d8",
}


class SnapshotError(ValueError):
    """Any integrity, order or provenance problem of the registry snapshot."""


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# --- sources --------------------------------------------------------------------------------
def source_hashes(repo: Path = REPO, sources: Dict[str, str] = SOURCES) -> Dict[str, dict]:
    """raw / LF / git-blob SHA-256 per source; rejects missing files and any blob or LF mismatch."""
    out = {}
    for rel, expected_blob in sources.items():
        p = Path(repo) / rel
        if not p.is_file():
            raise SnapshotError(f"source missing: {rel}")
        raw = p.read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        blob = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{rel}"], capture_output=True)
        if blob.returncode != 0:
            raise SnapshotError(f"source not committed at HEAD: {rel}")
        row = {"raw_sha256": _sha(raw), "lf_sha256": _sha(lf), "blob_sha256": _sha(blob.stdout), "expected_blob_sha256": expected_blob}
        if row["blob_sha256"] != expected_blob:
            raise SnapshotError(f"git blob of {rel} differs from the reviewed baseline")
        if row["lf_sha256"] != row["blob_sha256"]:
            raise SnapshotError(f"working-tree file {rel} differs from its blob beyond line endings")
        out[rel] = row
    return out


# --- independent reconstruction of the coupling formula -----------------------------------
def _num(x, what: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float, str)):
        raise SnapshotError(f"{what}: not a number ({x!r})")
    v = float(x)
    if not math.isfinite(v):
        raise SnapshotError(f"{what}: not finite")
    return v


def registry_nodes(yaml_path: Path) -> Tuple[List[str], Dict[str, dict]]:
    """IDs in YAML insertion order and validated numeric parameters (theta -> theta_threshold)."""
    rows = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))["lanterns"]
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise SnapshotError("duplicate IDs in the registry")
    nodes = {}
    for r in rows:
        em = r["em_properties"]
        nodes[r["id"]] = {"beta": _num(r["beta"], f"{r['id']}.beta"), "theta_threshold": _num(r["theta"], f"{r['id']}.theta"),
                          **{k: _num(em[k], f"{r['id']}.{k}") for k in NODE_KEYS[2:]},
                          **{k: str(r[k]) for k in META_KEYS}}
    return ids, nodes


def independent_coupling(ids: List[str], nodes: Dict[str, dict]) -> Tuple[np.ndarray, dict]:
    """C_ij in the given ID order, rebuilt from the YAML values; plus the two clipping counts."""
    z = ALPHA_INV_REF * PHI_REF
    n = len(ids)
    C = np.zeros((n, n))
    kappa_clipped = 0
    for i in range(n):
        a = nodes[ids[i]]
        for j in range(i + 1, n):
            b = nodes[ids[j]]
            dist = min(1.0, max(0.0, abs(a["beta"] - b["beta"]) / 20.0))
            wave = (a["wavelength_cm"] + b["wavelength_cm"]) / 2.0
            kappa = z / 100.0 / (1.0 + ((a["frequency_hz"] - b["frequency_hz"]) / F0_HZ) ** 2) * math.exp(-dist / (wave / 10.0))
            kappa *= (a["kappa_em"] + b["kappa_em"]) / 2.0
            kappa_clipped += kappa > 1.0
            eta = 1.0 / (1.0 + abs(a["impedance_z"] - b["impedance_z"]) / z)
            C[i, j] = C[j, i] = min(max(kappa, 0.0), 1.0) * eta
    upper = C[np.triu_indices(n, 1)]
    return C, {"kappa_clipped_edges": int(kappa_clipped), "final_edges_at_one": int(np.count_nonzero(upper == 1.0)),
               "edges_positive": int(np.count_nonzero(upper > 0)), "edges_total": int(upper.size)}


# --- canonical hash and snapshot --------------------------------------------------------------
def canonical_sha256(ids: List[str], meta: Dict[str, List[str]], arrays: Dict[str, np.ndarray]) -> str:
    h = hashlib.sha256()
    header = {"schema": SNAPSHOT_SCHEMA, "ids": list(ids), "meta": {k: list(meta[k]) for k in META_KEYS},
              "arrays": [[k, list(np.asarray(arrays[k]).shape), "<f8"] for k in ARRAY_KEYS]}
    h.update(json.dumps(header, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    for k in ARRAY_KEYS:
        h.update(np.ascontiguousarray(arrays[k], dtype="<f8").tobytes(order="C"))
    return h.hexdigest()


def check_arrays(ids: List[str], arrays: Dict[str, np.ndarray]) -> None:
    if list(ids) != sorted(ids) or len(set(ids)) != len(ids) or len(ids) != N_NODES:
        raise SnapshotError("IDs must be the 34 unique IDs in lexicographic order")
    if set(arrays) != set(ARRAY_KEYS):
        raise SnapshotError(f"array keys {sorted(arrays)} differ from {sorted(ARRAY_KEYS)}")
    for k in ARRAY_KEYS:
        a = np.asarray(arrays[k])
        want = (N_NODES, N_NODES) if k == "C" else (N_NODES,)
        if a.dtype != np.float64 or a.shape != want:
            raise SnapshotError(f"{k}: dtype {a.dtype} shape {a.shape}, expected float64 {want}")
        if not np.all(np.isfinite(a)):
            raise SnapshotError(f"{k}: not finite")
    C = arrays["C"]
    if not np.array_equal(C, C.T) or np.any(np.diag(C) != 0.0) or C.min() < 0.0 or C.max() > 1.0:
        raise SnapshotError("C must be exactly symmetric, zero on the diagonal and within [0, 1]")


@dataclass(frozen=True)
class RegistrySnapshot:
    """Immutable canonical snapshot (arrays are read-only)."""
    ids: Tuple[str, ...]
    arrays: Dict[str, np.ndarray]
    meta: Dict[str, Tuple[str, ...]]
    canonical_sha256: str
    container_sha256: str
    manifest: dict

    @property
    def C(self) -> np.ndarray:
        return self.arrays["C"]


def build_snapshot(probe_dir: Path, out_dir: Path, *, repo: Path = REPO, sources: Dict[str, str] = SOURCES) -> dict:
    """Probe output (YAML order) -> canonical snapshot (sorted IDs), checked against the independent
    formula in BOTH orders; written exclusively (NPZ first, then the manifest with its container hash)."""
    probe_dir, out_dir = Path(probe_dir), Path(out_dir)
    if out_dir.exists():
        raise SnapshotError(f"snapshot directory {out_dir} exists already (never overwritten)")
    src = source_hashes(repo, sources)
    probe = json.loads((probe_dir / "probe_raw.json").read_text(encoding="utf-8"))
    with np.load(probe_dir / "probe_raw.npz", allow_pickle=False) as f:
        raw = {k: np.array(f[k], copy=True) for k in f.files}
    ids_yaml = list(probe["ids_yaml_order"])
    yaml_ids, nodes = registry_nodes(Path(repo) / REGISTRY_REL)
    if ids_yaml != yaml_ids:
        raise SnapshotError("probe IDs differ from the registry YAML order")
    C_ind_yaml, _ = independent_coupling(ids_yaml, nodes)
    err_yaml = float(np.max(np.abs(raw["C_yaml_order"] - C_ind_yaml)))
    if err_yaml > FORMULA_TOL:
        raise SnapshotError(f"legacy matrix differs from the independent formula in YAML order ({err_yaml:.3e})")
    perm = sorted(range(len(ids_yaml)), key=lambda i: ids_yaml[i])
    ids = [ids_yaml[i] for i in perm]
    arrays = {"C": np.ascontiguousarray(raw["C_yaml_order"][np.ix_(perm, perm)], dtype=np.float64)}
    for k in NODE_KEYS:
        arrays[k] = np.ascontiguousarray(raw[k][perm], dtype=np.float64)
    meta = {k: [probe["node_meta_yaml_order"][k][i] for i in perm] for k in META_KEYS}
    C_ind, clip = independent_coupling(ids, nodes)
    err = float(np.max(np.abs(arrays["C"] - C_ind)))
    if err > FORMULA_TOL:
        raise SnapshotError(f"canonical matrix differs from the independent formula ({err:.3e})")
    for k in NODE_KEYS:
        if not np.array_equal(arrays[k], np.array([nodes[i][k] for i in ids])):
            raise SnapshotError(f"node array {k} is not jointly permuted with the IDs")
    check_arrays(ids, arrays)
    canon = canonical_sha256(ids, meta, arrays)
    buf = io.BytesIO()
    np.savez(buf, **arrays)
    out_dir.mkdir(parents=True)
    npz = out_dir / "snapshot.npz"
    fd = os.open(str(npz), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o644)
    with os.fdopen(fd, "wb") as fh:
        fh.write(buf.getvalue())
    strengths = arrays["C"].sum(axis=1)
    g = 1.0 / strengths.max()
    ev = np.linalg.eigvalsh(g * (np.diag(strengths) - arrays["C"]))
    manifest = {
        "schema": SNAPSHOT_SCHEMA, "ids": ids, "meta": meta, "array_keys": list(ARRAY_KEYS),
        "permutation_from_yaml_order": perm, "ids_yaml_order": ids_yaml,
        "hashes": {"canonical_sha256": canon, "container_sha256": _sha(npz.read_bytes()),
                   "note": "container hash = these NPZ bytes; canonical hash = schema+IDs+meta+shape+'<f8'+C-order data; "
                           "an equal array set saved again may have a different container hash"},
        "sources": src,
        "formula_check": {"tolerance": FORMULA_TOL, "max_abs_error_yaml_order": err_yaml, "max_abs_error_canonical": err,
                          "constants": {"alpha_inv": ALPHA_INV_REF, "phi": PHI_REF, "f0_hz": F0_HZ}},
        "structure": {**clip, "strength_min": float(strengths.min()), "strength_max": float(strengths.max()),
                      "strength_argmin": ids[int(strengths.argmin())], "strength_argmax": ids[int(strengths.argmax())],
                      "g": float(g), "lambda2_gL": float(ev[1]), "lambda_max_gL": float(ev[-1]),
                      "mean_weight": float(arrays["C"][np.triu_indices(N_NODES, 1)].mean())},
        "theta_note": "theta_threshold is the YAML threshold Theta; it is never a dynamic phase",
        "coupling_targets_used_by_matrix": False,
        "probe": {k: probe[k] for k in ("schema", "python", "numpy", "pythonhashseed", "dont_write_bytecode", "no_user_site",
                                         "global_rng", "audit", "modules")},
    }
    fd = os.open(str(out_dir / "snapshot.json"), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    return manifest


def load_snapshot(directory: Path, *, expected_canonical_sha256: Optional[str] = None, repo: Optional[Path] = REPO) -> RegistrySnapshot:
    """Strict load: exact files, no pickle, keys/shapes/float64/finite, sorted unique IDs, symmetric C
    in [0,1], container AND canonical hash, optional pinned canonical hash, and (with a repo) the
    independent formula and the source blobs again. Never imports legacy code."""
    d = Path(directory)
    files = {p.name for p in d.iterdir()} if d.is_dir() else set()
    if files != {"snapshot.npz", "snapshot.json"}:
        raise SnapshotError(f"snapshot directory must contain exactly snapshot.npz and snapshot.json, found {sorted(files)}")
    man = json.loads((d / "snapshot.json").read_text(encoding="utf-8"))
    if man.get("schema") != SNAPSHOT_SCHEMA:
        raise SnapshotError("unknown snapshot schema")
    if _sha((d / "snapshot.npz").read_bytes()) != man["hashes"]["container_sha256"]:
        raise SnapshotError("NPZ container differs from the manifest (manipulated or replaced file)")
    with np.load(d / "snapshot.npz", allow_pickle=False) as f:
        arrays = {k: np.array(f[k], copy=True) for k in f.files}
    ids = list(man["ids"])
    check_arrays(ids, arrays)
    meta = {k: list(man["meta"][k]) for k in META_KEYS}
    canon = canonical_sha256(ids, meta, arrays)
    if canon != man["hashes"]["canonical_sha256"]:
        raise SnapshotError("canonical array hash differs from the manifest")
    if expected_canonical_sha256 is not None and canon != expected_canonical_sha256:
        raise SnapshotError("canonical array hash differs from the pinned value")
    if repo is not None:
        source_hashes(repo)
        yaml_ids, nodes = registry_nodes(Path(repo) / REGISTRY_REL)
        if sorted(yaml_ids) != ids:
            raise SnapshotError("snapshot IDs differ from the registry")
        C_ind, _ = independent_coupling(ids, nodes)
        if float(np.max(np.abs(arrays["C"] - C_ind))) > FORMULA_TOL:
            raise SnapshotError("snapshot matrix differs from the independent formula (wrong order or manipulated)")
    for a in arrays.values():
        a.setflags(write=False)
    return RegistrySnapshot(tuple(ids), arrays, {k: tuple(v) for k, v in meta.items()}, canon, man["hashes"]["container_sha256"], man)
