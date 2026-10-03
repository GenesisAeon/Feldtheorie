"""M1 tests: episode operator, reference kernels, K1/K3/K7/K8/K9, SCF parity.

Expected values come from the hand/independent derivations in
controls/independent_controls_m0.py and the plan, not from this code.
K2/K4/K5/K6 concern observation and decoding and are tested in M2.
"""
from fractions import Fraction as F

import numpy as np
import pytest

from experiments.mandala_memory.core import (
    EpisodeOperator,
    LinearScalarKernel,
    MemoryLabError,
    NetworkSpec,
    build_network,
    one_hot,
    pulse_delay_inputs,
    recall_state,
)


# --- K1 / K9: linear reference kernel (exact) ---------------------------------

@pytest.mark.parametrize("d", [0, 1, 2, 4, 8])
@pytest.mark.parametrize("sign", [1, -1])
def test_k1_linear_memory(d, sign):
    k = LinearScalarKernel(F(1, 2))
    assert k.run([F(sign)] + [F(0)] * d)[-1] == F(sign, 2 ** d)


def test_k9_continuation_linear_exact():
    stim = [F(1), F(0), F(0), F(0), F(0)]
    whole = LinearScalarKernel().run(stim)
    k = LinearScalarKernel()
    head = k.run(stim[:2])
    cont = head + k.run(stim[2:])                       # state carried over
    reset = head + LinearScalarKernel().run(stim[2:])   # reset at the seam
    assert whole == cont and whole != reset
    assert [str(v) for v in whole] == ["1", "1/2", "1/4", "1/8", "1/16"]


def test_k9_continuation_network_snapshot_restore():
    spec = build_network()
    inputs = pulse_delay_inputs(0, 8)
    whole = EpisodeOperator(spec)
    whole.reset()
    t_whole = whole.run(inputs)
    a = EpisodeOperator(spec)
    a.reset()
    t_head = a.run(inputs[:3])
    snap = a.snapshot()
    b = EpisodeOperator(spec)
    b.restore(snap)
    t_tail = b.run(inputs[3:])
    assert np.array_equal(t_whole, np.vstack([t_head, t_tail[1:]])), "continuation must reproduce the whole run bit-exactly"
    c = EpisodeOperator(spec)
    c.reset()                                           # reset at the seam instead
    t_reset = c.run(inputs[3:])
    assert not np.array_equal(t_whole[-1], t_reset[-1]), "a reset at the seam must change the result"


# --- SCF parity (constant input, x0 = 0) -------------------------------------

@pytest.mark.parametrize("s", [0, 1])
def test_scf_simulate_trial_parity(s):
    from scoped_correspondence.validation.modular_networks.adaptive_model import simulate_trial

    spec = build_network()
    u = one_hot(s)
    op = EpisodeOperator(spec)
    op.reset()
    mine = op.run([u] * 12)
    ref = simulate_trial(spec.A, spec.B, u, spec.ell, 12)
    assert np.array_equal(mine, ref), "same step as SCF simulate_trial for constant u and x0 = 0"


# --- readout convention -----------------------------------------------------------

@pytest.mark.parametrize("d", [0, 1, 2, 4, 8, 16, 32])
def test_readout_is_state_after_d_plus_one_steps(d):
    spec = build_network()
    op = EpisodeOperator(spec)
    op.reset()
    traj = op.run(pulse_delay_inputs(1, d))
    assert traj.shape == (d + 2, 12)
    assert np.array_equal(recall_state(spec, 1, d), traj[d + 1])
    assert op.k == d + 1


def test_pulse_applied_exactly_once():
    spec = build_network(nonlinearity="identity")
    x1 = recall_state(spec, 0, 0)
    expected = np.zeros(12)
    expected[0] = 0.5 * 0.6            # ell * amplitude, amplitude applied once
    assert np.array_equal(x1, expected)


# --- K3: reset control --------------------------------------------------------------

@pytest.mark.parametrize("d", [0, 1, 8, 32])
def test_k3_reset_after_pulse(d):
    spec = build_network()
    x0 = recall_state(spec, 0, d, reset_after_pulse=True)
    x1 = recall_state(spec, 1, d, reset_after_pulse=True)
    assert np.array_equal(x0, x1) and not np.any(x0), "both classes identical (zero): Bayes accuracy 1/2"


# --- K7: identical operator under different module names --------------------------

def test_k7_exact_matrix_and_identical_trajectories():
    from scoped_correspondence.validation.modular_networks.adaptive_model import budget_adjacency

    g = F(4, 5)
    U, _ = budget_adjacency(12, 1, g)
    Mx, _ = budget_adjacency(12, 3, g, F(8, 11))
    assert U == Mx and U[0][1] == F(4, 55) and all(sum(r) == g for r in U)
    uni = build_network(M=1)
    mod = build_network(M=3, c=F(8, 11))
    assert np.array_equal(uni.A, mod.A), "exact construction -> bit-identical floats"
    for s in (0, 1):
        for d in (0, 4, 32):
            assert np.array_equal(recall_state(uni, s, d), recall_state(mod, s, d))
    assert not np.array_equal(build_network(M=3, c=0.25).A, uni.A), "the experiment's c = 1/4 differs"


# --- K8: contraction bound for frozen weights ------------------------------------

def test_k8_contraction_bound_production_step():
    from scoped_correspondence.validation.modular_networks.adaptive_model import contraction_bound

    q = contraction_bound(F(1, 2), F(4, 5))
    assert q == F(9, 10)
    spec = build_network()
    rng = np.random.default_rng(20261003)
    zero = np.zeros(2)
    worst = 0.0
    for _ in range(200):
        x, z = rng.uniform(0, 1, 12), rng.uniform(0, 1, 12)
        a, b = EpisodeOperator(spec), EpisodeOperator(spec)
        a.reset(x)
        b.reset(z)
        d0 = np.max(np.abs(x - z))
        for k in range(1, 21):
            a.step(zero)
            b.step(zero)
            worst = max(worst, np.max(np.abs(a.x - b.x)) / (float(q) ** k * d0))
    assert worst <= 1 + 1e-12, f"sup-norm distance exceeded q^k bound (ratio {worst})"


# --- ablation kernels -----------------------------------------------------------------

def test_uncoupled_leak_decays_geometrically():
    spec = build_network(coupling=False)
    assert not np.any(spec.A)
    x1 = recall_state(spec, 0, 0)
    for d in (1, 4, 8):
        assert np.allclose(recall_state(spec, 0, d), (0.5 ** d) * x1, rtol=0, atol=1e-15)


# --- snapshot / scope -----------------------------------------------------------------

def test_snapshot_restore_roundtrip_and_mismatch():
    spec = build_network()
    op = EpisodeOperator(spec)
    op.reset()
    op.run(pulse_delay_inputs(0, 3))
    snap = op.snapshot()
    snap_x = snap["x"].copy()
    op.step(np.zeros(2))                       # mutate after snapshot
    assert np.array_equal(snap["x"], snap_x), "snapshot is a copy, not a view"
    op.restore(snap)
    assert np.array_equal(op.x, snap_x) and op.k == 4
    other = EpisodeOperator(build_network(coupling=False))
    with pytest.raises(MemoryLabError):
        other.restore(snap)


def test_scope_errors():
    spec = build_network()
    op = EpisodeOperator(spec)
    with pytest.raises(MemoryLabError):
        op.step([1.0, 0.0, 0.0])
    with pytest.raises(MemoryLabError):
        op.step([np.nan, 0.0])
    with pytest.raises(MemoryLabError):
        op.reset([0.0] * 11)
    with pytest.raises(MemoryLabError):
        NetworkSpec(spec.A, spec.B, ell=1.5)
    with pytest.raises(MemoryLabError):
        NetworkSpec(spec.A, spec.B, ell=0.5, nonlinearity="relu")
    with pytest.raises(MemoryLabError):
        pulse_delay_inputs(0, -1)


def test_weights_untouched_by_episodes():
    spec = build_network()
    A0, B0 = spec.A.copy(), spec.B.copy()
    for s in (0, 1):
        recall_state(spec, s, 32)
    assert np.array_equal(spec.A, A0) and np.array_equal(spec.B, B0)
