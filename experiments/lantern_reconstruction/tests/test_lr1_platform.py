"""Platform-independent parts of the two Windows-bound LR1 probe checks (2026-10-13, CI_PLATTFORMBINDUNG.md).

``test_lr1.py::test_fresh_probe_rebuilds_exactly_the_pinned_snapshot`` and
``test_lr1.py::test_probe_runs_the_full_loader_and_matches_the_snapshot`` bind the pinned snapshot BIT-EXACTLY.
They pass in the freeze environment (Windows) and fail on Linux CI; the cause there is not established (an
unconfirmed guess is last-bit rounding of the legacy formula). Those two tests stay unchanged and run in the
Windows CI job. This file keeps every tolerant/structural part of them running on EVERY platform, so Linux still
checks the formula, the ordering and the loader coverage. It does not replace or weaken the bit-exact checks.
"""
from __future__ import annotations

import numpy as np

from experiments.lantern_reconstruction import registry_adapter as ra
from experiments.lantern_reconstruction.tests.test_lr1 import _probe, probes  # noqa: F401  (fixture re-use)

# Same bound the freeze uses for the formula check of the canonical matrix (test_lr1.py:268).
FORMULA_ATOL = 1e-14


def test_fresh_probe_formula_and_permutation_hold_on_every_platform(probes, tmp_path):
    for key in ("h0", "h1"):                                               # also independent of PYTHONHASHSEED
        man = ra.build_snapshot(probes[key], tmp_path / f"snap-{key}")
        assert man["formula_check"]["max_abs_error_canonical"] <= FORMULA_ATOL
        assert man["permutation_from_yaml_order"] != list(range(34))


def test_probe_matrix_matches_snapshot_within_formula_tolerance(probes):
    meta, raw = _probe(probes["h0"])
    s = ra.load_verified_snapshot()
    ids = meta["ids_yaml_order"]
    assert ids != sorted(ids) and sorted(ids) == list(s.ids)                # ordering: exact
    perm = [ids.index(i) for i in s.ids]
    C = raw["C_yaml_order"][np.ix_(perm, perm)]
    assert C.shape == s.C.shape and np.all(np.isfinite(C))
    assert np.max(np.abs(C - s.C)) <= FORMULA_ATOL                          # values: within the formula tolerance
    files = {m["file"] for m in meta["modules"]["inside_repo"]}
    assert {"v9_alpha/api/lantern_bridge.py", "models/collective_field.py", "models/__init__.py", "models/unified_constants.py"} <= files
    assert meta["pythonhashseed"] == "0" and meta["dont_write_bytecode"] and meta["no_user_site"]


def test_tolerance_rejects_a_real_deviation(probes):
    """Negative control: a change above the tolerance in one entry must be detected."""
    meta, raw = _probe(probes["h0"])
    s = ra.load_verified_snapshot()
    ids = meta["ids_yaml_order"]
    perm = [ids.index(i) for i in s.ids]
    C = raw["C_yaml_order"][np.ix_(perm, perm)].copy()
    C[0, 1] += 10 * FORMULA_ATOL
    assert np.max(np.abs(C - s.C)) > FORMULA_ATOL
