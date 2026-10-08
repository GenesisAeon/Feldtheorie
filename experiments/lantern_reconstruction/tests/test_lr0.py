"""LR0 checks: trilayer twin, unchanged reference package, reported inventory and oracle results.
Run explicitly (root pytest only collects tests/): python -m pytest experiments/lantern_reconstruction/tests"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
LR0 = HERE / "lr0"
REF = HERE / "reference" / "review_package_2026-10-07"


def test_status_yaml_twin_equals_json():
    yaml = pytest.importorskip("yaml")
    assert yaml.safe_load((LR0 / "lr0_status.yaml").read_text(encoding="utf-8")) == json.loads((LR0 / "lr0_status.json").read_text(encoding="utf-8"))


def test_reference_package_is_byte_identical_to_its_sha256sums():
    lines = [ln.split(None, 1) for ln in (REF / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 10
    for h, name in lines:
        assert hashlib.sha256((REF / name.strip()).read_bytes()).hexdigest() == h, name


def test_inventory_matches_the_report():
    inv = json.loads((LR0 / "lr0_inventory.json").read_text(encoding="utf-8"))
    s = inv["sources_summary"]
    assert s["n"] == s["blob_matches_inventory"] == s["main_raw_matches_inventory"] == s["lf_equals_blob_main"] == s["lf_equals_blob_worktree"] == 11
    assert s["anchors_found"] == s["anchors_total"] == 9
    assert inv["registry"] == {"count": 34, "unique": True, "sorted_equals_inventory": True, "yaml_order_differs_from_sorted": True,
                               "matrix_calculated": False}
    assert inv["worktree"]["head"] == inv["inventory_repo_head"] == "d1c56267ae81e90f9ebd7d5d195fea818b5f3930"


def test_oracle_results_as_reported():
    c = json.loads((LR0 / "local_control_results.json").read_text(encoding="utf-8"))
    assert c["passed"] == c["total"] == 22 and all(r["passed"] for r in c["checks"])
    a = json.loads((LR0 / "local_source_audit.json").read_text(encoding="utf-8"))
    stored = json.loads((REF / "source_audit_results.json").read_text(encoding="utf-8"))
    for k in ("nodes", "edges", "kappa_clipped_edges", "final_edges_at_one", "canonical_ids", "zero_noise_consumes_global_rng"):
        assert a[k] == stored[k], k
    for k in ("strength_min", "strength_max", "g", "lambda2", "lambda_max", "mean_weight"):
        assert a[k] == pytest.approx(stored[k], rel=0, abs=1e-12), k
    assert a["matrix_max_abs_error"] <= 1e-14 and a["phase_200_steps_max_circular_error"] <= 1e-12
    assert all(a["source_hashes"][p]["lf_sha256"] == stored["source_hashes"][p]["lf_sha256"] for p in stored["source_hashes"])
