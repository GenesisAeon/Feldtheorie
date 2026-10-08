"""LR1: legacy loader in a separate process, canonical export, rejection of missing sources, wrong
order and manipulated artifacts. Run explicitly: python -m pytest experiments/lantern_reconstruction/tests"""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

from experiments.lantern_reconstruction import legacy_probe as lp
from experiments.lantern_reconstruction import registry_adapter as ra

ARTIFACT = ra.HERE / "artifacts" / "registry_snapshot_v1"
PINNED_CANONICAL = "7237a78427f352e3622dfc9183ecee9878ce895cf9e69522b6dd19b0638dab94"


@pytest.fixture(scope="module")
def probes(tmp_path_factory):
    """Three real probe runs of the UNCHANGED original loader in separate processes."""
    root = tmp_path_factory.mktemp("lr1")
    out = {"h0": lp.run_probe(ra.REPO, root / "h0"), "h1": lp.run_probe(ra.REPO, root / "h1", hashseed="1")}
    data = yaml.safe_load((ra.REPO / ra.REGISTRY_REL).read_text(encoding="utf-8"))
    for row in data["lanterns"]:
        row["coupling_targets"] = []
    stripped = root / "lantern_hub_no_targets.yaml"
    stripped.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    out["no_targets"] = lp.run_probe(ra.REPO, root / "no_targets", config=stripped)
    out["root"] = root
    return out


def _probe(d):
    meta = json.loads((Path(d) / "probe_raw.json").read_text(encoding="utf-8"))
    with np.load(Path(d) / "probe_raw.npz", allow_pickle=False) as f:
        return meta, {k: np.array(f[k]) for k in f.files}


# --- the committed snapshot ------------------------------------------------------------------
def test_committed_snapshot_loads_with_pinned_hash_and_plan_values():
    s = ra.load_snapshot(ARTIFACT, expected_canonical_sha256=PINNED_CANONICAL)
    st = s.manifest["structure"]
    assert s.ids == tuple(sorted(s.ids)) and len(s.ids) == 34
    assert (st["edges_positive"], st["kappa_clipped_edges"], st["final_edges_at_one"]) == (561, 187, 9)
    assert st["strength_min"] == pytest.approx(0.8286366711648625, abs=1e-15) and st["strength_max"] == pytest.approx(25.086797192035903, abs=1e-13)
    assert (st["strength_argmin"], st["strength_argmax"]) == ("seed-morph-compute-001", "seed-wolfmessing-001")
    assert st["g"] == pytest.approx(0.03986160498469138, abs=1e-16)
    assert st["lambda2_gL"] == pytest.approx(0.03403007351083512, abs=1e-13) and st["lambda_max_gL"] == pytest.approx(1.038685843274879, abs=1e-13)
    assert not s.C.flags.writeable                                   # immutable


def test_snapshot_records_the_hash_notions_separately():
    man = json.loads((ARTIFACT / "snapshot.json").read_text(encoding="utf-8"))
    for rel, h in man["sources"].items():
        assert set(h) == {"raw_sha256", "lf_sha256", "blob_sha256", "expected_blob_sha256"}
        assert h["lf_sha256"] == h["blob_sha256"] == h["expected_blob_sha256"], rel
    assert set(man["hashes"]) >= {"canonical_sha256", "container_sha256"}
    s = ra.load_snapshot(ARTIFACT, repo=None)
    buf = io.BytesIO()
    np.savez(buf, **{k: np.array(v) for k, v in s.arrays.items()})          # same arrays, new container
    with np.load(io.BytesIO(buf.getvalue()), allow_pickle=False) as f:
        again = {k: np.array(f[k]) for k in f.files}
    assert ra.canonical_sha256(list(s.ids), {k: list(v) for k, v in s.meta.items()}, again) == s.canonical_sha256


# --- the probe: full loader, observation, RNG ------------------------------------------------
def test_probe_runs_the_full_loader_and_matches_the_snapshot(probes):
    meta, raw = _probe(probes["h0"])
    s = ra.load_snapshot(ARTIFACT, repo=None)
    ids = meta["ids_yaml_order"]
    assert ids != sorted(ids) and sorted(ids) == list(s.ids)                # YAML order is NOT sorted
    perm = [ids.index(i) for i in s.ids]
    assert np.array_equal(raw["C_yaml_order"][np.ix_(perm, perm)], s.C)
    files = {m["file"] for m in meta["modules"]["inside_repo"]}
    assert {"v9_alpha/api/lantern_bridge.py", "models/collective_field.py", "models/__init__.py", "models/unified_constants.py"} <= files
    assert meta["pythonhashseed"] == "0" and meta["dont_write_bytecode"] and meta["no_user_site"]


def test_fresh_probe_rebuilds_exactly_the_pinned_snapshot(probes, tmp_path):
    for key in ("h0", "h1"):                                               # also independent of PYTHONHASHSEED
        man = ra.build_snapshot(probes[key], tmp_path / f"snap-{key}")
        assert man["hashes"]["canonical_sha256"] == PINNED_CANONICAL
        assert man["formula_check"]["max_abs_error_canonical"] <= 1e-14 and man["permutation_from_yaml_order"] != list(range(34))
        assert ra.load_snapshot(tmp_path / f"snap-{key}", expected_canonical_sha256=PINNED_CANONICAL).ids == tuple(sorted(man["ids_yaml_order"]))


def test_audit_is_an_observation_and_records_what_happened(probes):
    meta, _ = _probe(probes["h0"])
    audit = meta["audit"]
    assert "observation" in audit["kind"] and "no isolation" in audit["kind"]
    for ph in ("construct", "extract"):
        assert audit["phases"].get(ph, {}).get("writes", []) == [] and audit["phases"].get(ph, {}).get("network_or_process", []) == []
    net = [e for d in audit["phases"].values() for e in d["network_or_process"]]
    assert not [e for e in net if not e["event"].startswith("subprocess")]   # no socket/url events observed
    for e in net:                                                             # observed third-party side effect, recorded with callers
        assert e["caller_frames"]


def test_global_rng_side_effect_is_observed_and_separated(probes):
    m0, r0 = _probe(probes["h0"])
    m1, r1 = _probe(probes["h1"])
    assert m0["global_rng"]["consumed_by_construct"] is True                 # the original reseeds via hash()
    assert m0["global_rng"]["after_construct"] != m1["global_rng"]["after_construct"]   # depends on PYTHONHASHSEED
    assert np.array_equal(r0["C_yaml_order"], r1["C_yaml_order"])            # ... the matrix does not
    code = ("import sys, hashlib, numpy as np; sys.path.insert(0, sys.argv[1]);"
            "d=lambda: hashlib.sha256(np.random.get_state()[1].tobytes()).hexdigest(); a=d();"
            "from experiments.lantern_reconstruction import registry_adapter as ra; ra.load_snapshot(ra.HERE/'artifacts'/'registry_snapshot_v1');"
            "bad=[m for m in sys.modules if m.split('.')[0] in ('v9_alpha','models')]; print(bad, a==d())")
    out = subprocess.run([sys.executable, "-s", "-c", code, str(ra.REPO)], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0 and out.stdout.strip() == "[] True"            # research path: no legacy import, RNG untouched


def test_coupling_targets_are_loaded_but_not_used_by_the_matrix(probes):
    m0, r0 = _probe(probes["h0"])
    mt, rt = _probe(probes["no_targets"])
    assert sum(m0["node_meta_yaml_order"]["coupling_targets_loaded"]) > 0 == sum(mt["node_meta_yaml_order"]["coupling_targets_loaded"])
    assert np.array_equal(r0["C_yaml_order"], rt["C_yaml_order"])


# --- rejections: missing sources, wrong order, manipulated artifacts -------------------------
def test_missing_source_or_registry_is_rejected(tmp_path):
    with pytest.raises(ra.SnapshotError, match="source missing"):
        ra.source_hashes(ra.REPO, {**ra.SOURCES, "v9_alpha/api/does_not_exist.py": "0" * 64})
    with pytest.raises(ra.SnapshotError, match="differs from the reviewed baseline"):
        ra.source_hashes(ra.REPO, {"v9_alpha/api/lantern_bridge.py": "0" * 64})
    with pytest.raises(FileNotFoundError, match="registry source missing"):
        lp.run_probe(ra.REPO, tmp_path / "p", config=tmp_path / "missing.yaml")


def _copy(tmp_path) -> Path:
    d = tmp_path / "snap"
    shutil.copytree(ARTIFACT, d)
    return d


def _rewrite(d: Path, arrays=None, ids=None, fix_canonical=True, fix_container=True):
    man = json.loads((d / "snapshot.json").read_text(encoding="utf-8"))
    if arrays is not None:
        buf = io.BytesIO()
        np.savez(buf, **arrays)
        (d / "snapshot.npz").write_bytes(buf.getvalue())
    if ids is not None:
        man["ids"] = ids
    if fix_canonical:
        with np.load(d / "snapshot.npz", allow_pickle=False) as f:
            arr = {k: np.array(f[k]) for k in f.files}
        man["hashes"]["canonical_sha256"] = ra.canonical_sha256(man["ids"], man["meta"], arr)
    if fix_container:
        man["hashes"]["container_sha256"] = ra._sha((d / "snapshot.npz").read_bytes())
    (d / "snapshot.json").write_text(json.dumps(man), encoding="utf-8")


def _arrays():
    with np.load(ARTIFACT / "snapshot.npz", allow_pickle=False) as f:
        return {k: np.array(f[k]) for k in f.files}


def test_wrong_order_is_rejected(tmp_path, probes):
    m, raw = _probe(probes["h0"])
    a = _arrays()
    ids = list(json.loads((ARTIFACT / "snapshot.json").read_text(encoding="utf-8"))["ids"])
    perm = [m["ids_yaml_order"].index(i) for i in ids]
    yaml_order = dict(a, C=np.ascontiguousarray(raw["C_yaml_order"]))       # mutant 1: sorted IDs, matrix left in YAML order
    d = _copy(tmp_path)
    _rewrite(d, arrays=yaml_order)                                            # hashes made consistent on purpose
    with pytest.raises(ra.SnapshotError, match="independent formula"):
        ra.load_snapshot(d)
    d2 = tmp_path / "unsorted"
    shutil.copytree(ARTIFACT, d2)
    _rewrite(d2, ids=list(reversed(ids)))
    with pytest.raises(ra.SnapshotError, match="lexicographic order"):
        ra.load_snapshot(d2)
    # probe whose ID order no longer matches the YAML, and a node array not permuted with the IDs
    bad = tmp_path / "badprobe"
    shutil.copytree(probes["h0"], bad)
    pm = json.loads((bad / "probe_raw.json").read_text(encoding="utf-8"))
    pm["ids_yaml_order"][0], pm["ids_yaml_order"][1] = pm["ids_yaml_order"][1], pm["ids_yaml_order"][0]
    (bad / "probe_raw.json").write_text(json.dumps(pm), encoding="utf-8")
    with pytest.raises(ra.SnapshotError, match="YAML order"):
        ra.build_snapshot(bad, tmp_path / "s1")
    bad2 = tmp_path / "badprobe2"
    shutil.copytree(probes["h0"], bad2)
    rr = dict(raw)
    rr["beta"] = rr["beta"].copy()
    rr["beta"][[0, 1]] = rr["beta"][[1, 0]]
    buf = io.BytesIO()
    np.savez(buf, **rr)
    (bad2 / "probe_raw.npz").write_bytes(buf.getvalue())
    with pytest.raises(ra.SnapshotError, match="jointly permuted"):
        ra.build_snapshot(bad2, tmp_path / "s2")
    assert perm  # (silence unused)


def test_manipulated_artifacts_are_rejected(tmp_path):
    d = _copy(tmp_path)
    b = bytearray((d / "snapshot.npz").read_bytes())
    b[-40] ^= 0xFF
    (d / "snapshot.npz").write_bytes(bytes(b))
    with pytest.raises(ra.SnapshotError, match="container"):
        ra.load_snapshot(d)
    a = _arrays()
    a["C"] = a["C"].copy()
    a["C"][0, 1] = a["C"][1, 0] = a["C"][0, 1] * 0.5
    d2 = tmp_path / "c2"
    shutil.copytree(ARTIFACT, d2)
    _rewrite(d2, arrays=a, fix_canonical=False)                              # container fixed, canonical not
    with pytest.raises(ra.SnapshotError, match="canonical"):
        ra.load_snapshot(d2)
    d3 = tmp_path / "c3"
    shutil.copytree(ARTIFACT, d3)
    _rewrite(d3, arrays=a)                                                    # both hashes made consistent
    with pytest.raises(ra.SnapshotError, match="independent formula"):
        ra.load_snapshot(d3)
    with pytest.raises(ra.SnapshotError, match="pinned"):
        ra.load_snapshot(d3, expected_canonical_sha256=PINNED_CANONICAL, repo=None)
    d4 = _copy(tmp_path / "x")
    (d4 / "extra.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ra.SnapshotError, match="exactly"):
        ra.load_snapshot(d4)


@pytest.mark.parametrize("change, match", [
    (lambda a: a.update(C=a["C"].astype(np.float32)), "float64"),
    (lambda a: a["C"].__setitem__((0, 1), np.nan), "not finite"),
    (lambda a: a["C"].__setitem__((0, 1), 0.3), "symmetric"),
    (lambda a: a["C"].__setitem__((2, 2), 0.1), "diagonal"),
    (lambda a: a.update(beta=a["beta"][:-1]), "shape"),
])
def test_invalid_arrays_are_rejected(tmp_path, change, match):
    a = {k: v.copy() for k, v in _arrays().items()}
    change(a)
    d = _copy(tmp_path)
    _rewrite(d, arrays=a)
    with pytest.raises(ra.SnapshotError, match=match):
        ra.load_snapshot(d, repo=None)


def test_pickle_and_bool_parameters_are_refused(tmp_path):
    d = _copy(tmp_path)
    a = _arrays()
    buf = io.BytesIO()
    np.savez(buf, **{**a, "beta": np.array([{"x": 1}] * 34, dtype=object)})
    (d / "snapshot.npz").write_bytes(buf.getvalue())
    _rewrite(d, fix_canonical=False)
    with pytest.raises(ValueError, match="allow_pickle"):
        ra.load_snapshot(d, repo=None)
    data = yaml.safe_load((ra.REPO / ra.REGISTRY_REL).read_text(encoding="utf-8"))
    data["lanterns"][0]["beta"] = True
    p = tmp_path / "bool.yaml"
    p.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(ra.SnapshotError, match="not a number"):
        ra.registry_nodes(p)
    data["lanterns"][0]["beta"] = 1.0
    data["lanterns"][1]["id"] = data["lanterns"][0]["id"]
    p.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(ra.SnapshotError, match="duplicate"):
        ra.registry_nodes(p)


def test_existing_outputs_are_never_overwritten(tmp_path, probes):
    with pytest.raises(FileExistsError):
        lp.run_probe(ra.REPO, probes["h0"])
    with pytest.raises(ra.SnapshotError, match="exists already"):
        ra.build_snapshot(probes["h0"], ARTIFACT)


def test_lr1_status_yaml_twin_equals_json():
    p = ra.HERE / "lr1" / "lr1_status"
    assert yaml.safe_load(p.with_suffix(".yaml").read_text(encoding="utf-8")) == json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))
