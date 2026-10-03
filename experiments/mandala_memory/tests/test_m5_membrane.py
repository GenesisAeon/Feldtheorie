"""M5 tests: Feldtheorie membrane pilot (plan §7) -- continuation, fresh reset,
probe semantics, frozen control, loader isolation, source unchanged."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from experiments.mandala_memory.membrane_pilot import (
    CLASS_AMPLITUDES,
    PROBE_R,
    episode,
    membrane_class,
    new_membrane,
    run_pilot,
)

REPO = Path(__file__).resolve().parents[3]


def test_long_trace_equals_two_pieces_on_same_instance():
    trace = [0.8] + [0.0] * 8 + [PROBE_R]
    a = new_membrane()
    whole = a.propagate(trace, dt=1.0)
    b = new_membrane()
    p1 = b.propagate(trace[:4], dt=1.0)
    p2 = b.propagate(trace[4:], dt=1.0)
    for key in ("theta", "beta", "sigma"):
        assert np.array_equal(whole[key], np.concatenate([p1[key], p2[key]])), key
    assert a.theta == b.theta and a.beta == b.beta


def test_parameters_are_state_reset_and_fresh_instance():
    m = new_membrane()
    m.propagate([0.8], dt=1.0)
    theta_after = m.theta
    assert theta_after != 0.5, "the stimulus moved theta: the memory lives in the parameters"
    # 'resetting' only the visible output (ignoring the returned arrays) keeps the memory
    reused = episode(0, 4, membrane=m)
    fresh = episode(0, 4)
    assert reused["theta_before_probe"] != fresh["theta_before_probe"]
    m.reset()
    assert (m.theta, m.beta) == (0.5, 6.0)
    after_reset = episode(0, 4, membrane=m)
    assert after_reset == fresh, "reset() restores the baseline: equivalent to a fresh instance"


def test_probe_semantics_pre_vs_post_update():
    adaptive = episode(1, 2)
    assert adaptive["pre_probe_sigma"] != adaptive["post_probe_sigma"], "propagate updates first, then outputs"
    frozen = episode(1, 2, frozen=True)
    assert frozen["pre_probe_sigma"] == frozen["post_probe_sigma"]


def test_frozen_membrane_has_no_class_memory():
    for d in (0, 4, 16):
        f0, f1 = episode(0, d, frozen=True), episode(1, d, frozen=True)
        assert f0 == f1 and f0["theta_before_probe"] == 0.5 and f0["beta_before_probe"] == 6.0


def test_adaptive_membrane_separates_classes_at_short_delay():
    a0, a1 = episode(0, 0), episode(1, 0)
    assert a0["theta_before_probe"] != a1["theta_before_probe"]
    assert abs(a0["post_probe_sigma"] - a1["post_probe_sigma"]) > 0.1


def test_loader_does_not_import_the_models_package():
    code = ("import sys; sys.path.insert(0, r'%s'); "
            "from experiments.mandala_memory.membrane_pilot import membrane_class; membrane_class(); "
            "print('models' in sys.modules)") % str(REPO)
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=REPO)
    assert out.stdout.strip() == "False", out.stderr


def test_feldtheorie_membrane_source_unchanged():
    src = (REPO / "models" / "adaptive_logistic_membrane.py").read_bytes()
    ref = subprocess.run(["git", "-C", str(REPO), "show", "0e46ec88181b430c41330016279a8bd1ea2c0d9b:models/adaptive_logistic_membrane.py"],
                         capture_output=True).stdout
    assert src.replace(b"\r\n", b"\n") == ref.replace(b"\r\n", b"\n")


def test_run_pilot_structure_and_vocabulary():
    r = run_pilot(delays=(0, 8), seeds=(1, 2), n_per_class=5, mode="test")
    assert r["evidence_kind"] == "numerical_sample" and r["empirical_status"] == "synthetic_only"
    assert "not comparable" in r["note"]
    assert set(r["results"]) == {"adaptive", "frozen"}
    assert r["results"]["frozen"]["0"]["probe_output_difference"] == 0.0
