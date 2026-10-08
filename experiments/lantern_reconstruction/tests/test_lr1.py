"""LR1: legacy loader in a separate process, canonical export, trust contract of the snapshot
(review REVIEW_LR1 R1-R3). Run explicitly: python -m pytest experiments/lantern_reconstruction/tests"""
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

ARTIFACT = ra.HERE / ra.SNAPSHOT_PIN["directory"]
CPIN, MPIN = ra.SNAPSHOT_PIN["canonical_sha256"], ra.SNAPSHOT_PIN["manifest_sha256"]


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
    return out


def _probe(d):
    meta = json.loads((Path(d) / "probe_raw.json").read_text(encoding="utf-8"))
    with np.load(Path(d) / "probe_raw.npz", allow_pickle=False) as f:
        return meta, {k: np.array(f[k]) for k in f.files}


def _copy(tmp_path, name="snap") -> Path:
    d = tmp_path / name
    shutil.copytree(ARTIFACT, d)
    return d


def _man(d):
    return json.loads((d / "snapshot.json").read_text(encoding="utf-8"))


def _write_man(d, m) -> str:
    """Write a (manipulated) manifest and return the pin an attacker would compute for it."""
    b = json.dumps(m).encode("utf-8")
    (d / "snapshot.json").write_bytes(b)
    return ra._sha(b)


def _arrays():
    with np.load(ARTIFACT / "snapshot.npz", allow_pickle=False) as f:
        return {k: np.array(f[k]) for k in f.files}


def _replace_arrays(d, a, m):
    buf = io.BytesIO()
    np.savez(buf, **a)
    (d / "snapshot.npz").write_bytes(buf.getvalue())
    m["hashes"]["container_sha256"] = ra._sha(buf.getvalue())
    m["hashes"]["canonical_sha256"] = ra.canonical_sha256(m["ids"], m["meta"], a)
    return m["hashes"]["canonical_sha256"]


# --- the pinned research snapshot ----------------------------------------------------------
def test_verified_snapshot_loads_and_recomputes_the_plan_values():
    s = ra.load_verified_snapshot()
    st = s.structure
    assert s.ids == tuple(sorted(s.ids)) and len(s.ids) == 34 and s.canonical_sha256 == CPIN and s.manifest_sha256 == MPIN
    assert (st["edges_positive"], st["kappa_clipped_edges"], st["final_edges_at_one"]) == (561, 187, 9)
    assert st["strength_min"] == pytest.approx(0.8286366711648625, abs=1e-15) and st["strength_max"] == pytest.approx(25.086797192035903, abs=1e-13)
    assert (st["strength_argmin"], st["strength_argmax"]) == ("seed-morph-compute-001", "seed-wolfmessing-001")
    assert st["g"] == pytest.approx(0.03986160498469138, abs=1e-16)
    assert st["lambda2_gL"] == pytest.approx(0.03403007351083512, abs=1e-13) and st["lambda_max_gL"] == pytest.approx(1.038685843274879, abs=1e-13)


def test_pins_are_mandatory_and_external():
    with pytest.raises(TypeError):
        ra.load_snapshot(ARTIFACT)                                         # no default pins
    with pytest.raises(ra.SnapshotError, match="mandatory"):
        ra.load_snapshot(ARTIFACT, canonical_pin="", manifest_pin=MPIN)
    assert ra.read_snapshot_unverified(ARTIFACT)["status"].startswith("UNVERIFIED")


def test_hash_notions_are_separate_and_canonical_is_container_independent():
    s = ra.load_verified_snapshot()
    for rel, h in s.sources.items():
        assert set(h) == {"raw_sha256", "lf_sha256", "blob_sha256", "expected_blob_sha256"}
        assert h["lf_sha256"] == h["blob_sha256"] == ra.SOURCES[rel]
    buf = io.BytesIO()
    np.savez(buf, **s.working_copy())                                      # same arrays, new container
    with np.load(io.BytesIO(buf.getvalue()), allow_pickle=False) as f:
        again = {k: np.array(f[k]) for k in f.files}
    assert ra.canonical_sha256(list(s.ids), s.meta, again) == s.canonical_sha256


def test_import_manifest_is_complete_with_files_and_versions():
    im = ra.load_verified_snapshot().recorded_probe["import_manifest"]
    mods = im["modules"]
    assert im["count"] == len(mods) > 500
    assert all(m["file"] is None or m.get("raw_sha256") for m in mods)
    repo_mods = [m for m in mods if m["inside_repo"]]
    assert all(m["blob_sha256"] for m in repo_mods if m["file"] != "experiments/lantern_reconstruction/legacy_probe.py" or m["blob_sha256"])
    assert {"numpy", "scipy", "PyYAML"} <= set(im["distribution_versions"])


# --- review R1: manifest values are verified, not trusted ------------------------------------
def test_r1_astra_manifest_edits_rejected_even_with_the_original_array_pin(tmp_path):
    d = _copy(tmp_path)
    m = _man(d)
    m["structure"]["g"] = 100.0
    m["sources"] = {}
    m["permutation_from_yaml_order"] = list(range(34))
    attacker_pin = _write_man(d, m)
    with pytest.raises(ra.SnapshotError, match="pinned manifest"):
        ra.load_snapshot(d, canonical_pin=CPIN, manifest_pin=MPIN)         # Astra's case: original pins
    with pytest.raises(ra.SnapshotError, match="permutation"):
        ra.load_snapshot(d, canonical_pin=CPIN, manifest_pin=attacker_pin)  # even a re-pinned manifest


@pytest.mark.parametrize("field, value, match", [
    ("g", 100.0, "structure value g"),
    ("lambda2_gL", 0.5, "structure value lambda2_gL"),
    ("strength_argmax", "seed-morfit-001", "strength_argmax"),
    ("final_edges_at_one", 8, "final_edges_at_one"),
    ("kappa_clipped_edges", 186, "kappa clipping"),
])
def test_r1_each_structure_value_is_recomputed(tmp_path, field, value, match):
    d = _copy(tmp_path)
    m = _man(d)
    m["structure"][field] = value
    pin = _write_man(d, m)
    with pytest.raises(ra.SnapshotError, match=match):
        ra.load_snapshot(d, canonical_pin=CPIN, manifest_pin=pin)


def test_r1_sources_and_order_checked_against_independent_expectations(tmp_path):
    d = _copy(tmp_path)
    m = _man(d)
    m["sources"] = {}
    pin = _write_man(d, m)
    for repo in (ra.REPO, None):
        with pytest.raises(ra.SnapshotError, match="eleven pinned files"):
            ra.load_snapshot(d, canonical_pin=CPIN, manifest_pin=pin, repo=repo)
    d2 = _copy(tmp_path, "s2")
    m = _man(d2)
    rel = "models/unified_constants.py"
    m["sources"][rel]["blob_sha256"] = m["sources"][rel]["lf_sha256"] = m["sources"][rel]["expected_blob_sha256"] = "0" * 64
    pin = _write_man(d2, m)
    with pytest.raises(ra.SnapshotError, match="pinned baseline"):
        ra.load_snapshot(d2, canonical_pin=CPIN, manifest_pin=pin, repo=None)
    d3 = _copy(tmp_path, "s3")
    m = _man(d3)
    m["sources"][rel]["raw_sha256"] = "f" * 64                              # raw is checkout dependent: informational only
    pin = _write_man(d3, m)
    assert ra.load_snapshot(d3, canonical_pin=CPIN, manifest_pin=pin).canonical_sha256 == CPIN
    d4 = _copy(tmp_path, "s4")
    m = _man(d4)
    p = m["permutation_from_yaml_order"]
    p[0], p[1] = p[1], p[0]
    pin = _write_man(d4, m)
    with pytest.raises(ra.SnapshotError, match="permutation"):
        ra.load_snapshot(d4, canonical_pin=CPIN, manifest_pin=pin, repo=None)


@pytest.mark.parametrize("text, match", [
    ('{"a": 1, "a": 2}', "duplicate JSON key"),
    ('{"a": NaN}', "non-finite"),
    ('{"a": Infinity}', "non-finite"),
])
def test_r1_strict_json(text, match):
    with pytest.raises(ra.SnapshotError, match=match):
        ra.strict_json(text)


# --- review R2: every node array and the metadata are authenticated ---------------------------
@pytest.mark.parametrize("key", ["beta", "theta_threshold", "frequency_hz", "impedance_z", "kappa_photonic", "kappa_em",
                                 "kappa_metabolic", "wavelength_cm"])
def test_r2_changed_node_array_rejected_even_with_consistent_hashes_and_attacker_pins(tmp_path, key):
    d = _copy(tmp_path)
    m = _man(d)
    a = _arrays()
    a[key] = a[key].copy()
    a[key][0] = 999.0                                                       # Astra: beta[0]=999
    cpin = _replace_arrays(d, a, m)
    mpin = _write_man(d, m)
    with pytest.raises(ra.SnapshotError, match="pinned"):
        ra.load_snapshot(d, canonical_pin=CPIN, manifest_pin=MPIN)          # original pins
    with pytest.raises(ra.SnapshotError, match=f"node array {key} differs from the registry"):
        ra.load_snapshot(d, canonical_pin=cpin, manifest_pin=mpin)          # attacker pins, repository check


@pytest.mark.parametrize("key", ["name", "type", "domain", "status", "readiness"])
def test_r2_changed_metadata_rejected(tmp_path, key):
    d = _copy(tmp_path)
    m = _man(d)
    m["meta"][key][3] = "manipulated"
    m["hashes"]["canonical_sha256"] = ra.canonical_sha256(m["ids"], m["meta"], _arrays())
    mpin = _write_man(d, m)
    with pytest.raises(ra.SnapshotError, match=f"metadata {key} differs from the registry"):
        ra.load_snapshot(d, canonical_pin=m["hashes"]["canonical_sha256"], manifest_pin=mpin)


def test_r2_without_repository_the_external_pins_are_the_trust_basis(tmp_path):
    d = _copy(tmp_path)
    m = _man(d)
    a = _arrays()
    a["beta"] = a["beta"].copy()
    a["beta"][0] = 999.0
    _replace_arrays(d, a, m)
    _write_man(d, m)
    with pytest.raises(ra.SnapshotError, match="pinned"):
        ra.load_snapshot(d, canonical_pin=CPIN, manifest_pin=MPIN, repo=None)


# --- review R3: the verified snapshot cannot be changed unnoticed ------------------------------
def test_r3_arrays_cannot_be_reenabled_for_writing():
    s = ra.load_verified_snapshot()
    with pytest.raises(ValueError):
        s.C.setflags(write=True)                                           # Astra's case
    with pytest.raises(ValueError):
        s.C[0, 1] = 123.0
    with pytest.raises(ValueError):
        s.arrays["beta"][0] = 1.0


def test_r3_mappings_and_fields_are_read_only():
    s = ra.load_verified_snapshot()
    with pytest.raises(TypeError):
        s.arrays["C"] = np.zeros((34, 34))
    with pytest.raises(TypeError):
        s.meta["name"] = ("x",) * 34
    with pytest.raises(TypeError):
        s.structure["g"] = 100.0
    with pytest.raises(TypeError):
        s.sources["models/__init__.py"] = {}
    with pytest.raises(TypeError):
        s.recorded_probe["import_manifest"]["count"] = 0
    with pytest.raises(AttributeError):
        s.canonical_sha256 = "x"


def test_r3_working_copies_are_independent_and_verify_detects_circumvention():
    s = ra.load_verified_snapshot()
    w = s.working_copy()
    w["C"][0, 1] = 123.0
    assert s.C[0, 1] != 123.0
    s.verify()
    object.__setattr__(s, "arrays", {**s.arrays, "C": np.zeros((34, 34))})  # deliberate circumvention
    with pytest.raises(ra.SnapshotError, match="changed after loading"):
        s.verify()


# --- the probe: full loader, observation, RNG ------------------------------------------------
def test_fresh_probe_rebuilds_exactly_the_pinned_snapshot(probes, tmp_path):
    for key in ("h0", "h1"):                                               # also independent of PYTHONHASHSEED
        man = ra.build_snapshot(probes[key], tmp_path / f"snap-{key}")
        assert man["hashes"]["canonical_sha256"] == CPIN
        assert man["formula_check"]["max_abs_error_canonical"] <= 1e-14 and man["permutation_from_yaml_order"] != list(range(34))


def test_probe_runs_the_full_loader_and_matches_the_snapshot(probes):
    meta, raw = _probe(probes["h0"])
    s = ra.load_verified_snapshot()
    ids = meta["ids_yaml_order"]
    assert ids != sorted(ids) and sorted(ids) == list(s.ids)
    perm = [ids.index(i) for i in s.ids]
    assert np.array_equal(raw["C_yaml_order"][np.ix_(perm, perm)], s.C)
    files = {m["file"] for m in meta["modules"]["inside_repo"]}
    assert {"v9_alpha/api/lantern_bridge.py", "models/collective_field.py", "models/__init__.py", "models/unified_constants.py"} <= files
    assert meta["pythonhashseed"] == "0" and meta["dont_write_bytecode"] and meta["no_user_site"]


def test_audit_is_an_observation_and_records_what_happened(probes):
    meta, _ = _probe(probes["h0"])
    audit = meta["audit"]
    assert "observation" in audit["kind"] and "no isolation" in audit["kind"]
    for ph in ("construct", "extract"):
        assert audit["phases"].get(ph, {}).get("writes", []) == [] and audit["phases"].get(ph, {}).get("network_or_process", []) == []
    net = [e for d in audit["phases"].values() for e in d["network_or_process"]]
    assert not [e for e in net if not e["event"].startswith("subprocess")]
    for e in net:
        assert e["caller_frames"]


def test_global_rng_side_effect_is_observed_and_separated(probes):
    m0, r0 = _probe(probes["h0"])
    m1, r1 = _probe(probes["h1"])
    assert m0["global_rng"]["consumed_by_construct"] is True
    assert m0["global_rng"]["after_construct"] != m1["global_rng"]["after_construct"]
    assert np.array_equal(r0["C_yaml_order"], r1["C_yaml_order"])
    code = ("import sys, hashlib, numpy as np; sys.path.insert(0, sys.argv[1]);"
            "d=lambda: hashlib.sha256(np.random.get_state()[1].tobytes()).hexdigest(); a=d();"
            "from experiments.lantern_reconstruction import registry_adapter as ra; ra.load_verified_snapshot();"
            "bad=[m for m in sys.modules if m.split('.')[0] in ('v9_alpha','models')]; print(bad, a==d())")
    out = subprocess.run([sys.executable, "-s", "-c", code, str(ra.REPO)], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0 and out.stdout.strip() == "[] True"


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


def test_wrong_order_is_rejected(tmp_path, probes):
    m_probe, raw = _probe(probes["h0"])
    d = _copy(tmp_path)
    m = _man(d)
    a = dict(_arrays(), C=np.ascontiguousarray(raw["C_yaml_order"]))       # mutant 1: sorted IDs, matrix in YAML order
    cpin = _replace_arrays(d, a, m)
    m["structure"] = {**ra.structure_from_arrays(m["ids"], a["C"]), "kappa_clipped_edges": 187}
    mpin = _write_man(d, m)
    with pytest.raises(ra.SnapshotError, match="independent formula"):
        ra.load_snapshot(d, canonical_pin=cpin, manifest_pin=mpin)
    d2 = _copy(tmp_path, "unsorted")
    m = _man(d2)
    m["ids"] = list(reversed(m["ids"]))
    mpin = _write_man(d2, m)
    with pytest.raises(ra.SnapshotError, match="lexicographic order"):
        ra.load_snapshot(d2, canonical_pin=CPIN, manifest_pin=mpin)
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


def test_replaced_container_with_identical_arrays_is_rejected(tmp_path):
    """The container hash is part of the contract: a re-packed NPZ with the SAME arrays (different
    bytes) must be rejected, although its canonical hash would still match (mutation check found this gap)."""
    d = _copy(tmp_path)
    buf = io.BytesIO()
    np.savez_compressed(buf, **_arrays())
    assert buf.getvalue() != (ARTIFACT / "snapshot.npz").read_bytes()
    (d / "snapshot.npz").write_bytes(buf.getvalue())
    with pytest.raises(ra.SnapshotError, match="NPZ container differs"):
        ra.load_snapshot(d, canonical_pin=CPIN, manifest_pin=MPIN)


def test_manipulated_artifacts_are_rejected(tmp_path):
    d = _copy(tmp_path)
    b = bytearray((d / "snapshot.npz").read_bytes())
    b[-40] ^= 0xFF
    (d / "snapshot.npz").write_bytes(bytes(b))
    with pytest.raises(Exception):
        ra.load_snapshot(d, canonical_pin=CPIN, manifest_pin=MPIN)
    d2 = _copy(tmp_path, "c2")
    m = _man(d2)
    a = _arrays()
    a["C"] = a["C"].copy()
    a["C"][0, 1] = a["C"][1, 0] = a["C"][0, 1] * 0.5
    cpin = _replace_arrays(d2, a, m)
    m["structure"] = {**ra.structure_from_arrays(m["ids"], a["C"]), "kappa_clipped_edges": 187}
    mpin = _write_man(d2, m)
    with pytest.raises(ra.SnapshotError, match="pinned"):
        ra.load_snapshot(d2, canonical_pin=CPIN, manifest_pin=mpin)          # original canonical pin
    with pytest.raises(ra.SnapshotError, match="independent formula"):
        ra.load_snapshot(d2, canonical_pin=cpin, manifest_pin=mpin)          # everything re-pinned
    d4 = _copy(tmp_path, "x")
    (d4 / "extra.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ra.SnapshotError, match="exactly"):
        ra.load_snapshot(d4, canonical_pin=CPIN, manifest_pin=MPIN)


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
    m = _man(d)
    buf = io.BytesIO()
    np.savez(buf, **a)
    (d / "snapshot.npz").write_bytes(buf.getvalue())
    m["hashes"]["container_sha256"] = ra._sha(buf.getvalue())
    mpin = _write_man(d, m)
    with pytest.raises(ra.SnapshotError, match=match):
        ra.load_snapshot(d, canonical_pin=CPIN, manifest_pin=mpin, repo=None)


def test_pickle_and_bool_parameters_are_refused(tmp_path):
    d = _copy(tmp_path)
    buf = io.BytesIO()
    np.savez(buf, **{**_arrays(), "beta": np.array([{"x": 1}] * 34, dtype=object)})
    (d / "snapshot.npz").write_bytes(buf.getvalue())
    with pytest.raises(ValueError, match="allow_pickle"):
        ra.read_snapshot_unverified(d)
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
