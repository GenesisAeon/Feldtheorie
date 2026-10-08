"""LR3: tasks A/B, observation access, streams, writing controls and reference networks.
Plan acceptance: reference-node leak tested negatively, reset / zero impulse, surrogate invariants;
plus the hard gates of plan section 10. Run explicitly with the other Lantern tests."""
from __future__ import annotations

import json
import math
from dataclasses import replace

import numpy as np
import pytest

from experiments.lantern_reconstruction import contexts, episodes, streams, surrogates
from experiments.lantern_reconstruction import observation as ob
from experiments.lantern_reconstruction import registry_adapter as ra
from experiments.lantern_reconstruction.encoding import initial_state

D = streams.defaults()
SID = D["development_study_id"]


@pytest.fixture(scope="module")
def lab():
    s = ra.load_verified_snapshot()
    ctx = contexts.make_context(SID, 0)
    return {"C": np.array(s.C), "g": float(s.structure["g"]), "ctx": ctx, "Cs": episodes.coupling_matrices(np.array(s.C), ctx, proposals=2000)}


# --- defaults and streams --------------------------------------------------------------------------
def test_study_defaults_trilayer_and_planned_values():
    import yaml
    p = ra.HERE / "protocol" / "study_defaults"
    assert yaml.safe_load(p.with_suffix(".yaml").read_text(encoding="utf-8")) == json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))
    assert D["time_grid"] == [0, 0.5, 1, 2, 3, 5, 10] and D["integration"] == {"method": "rk4", "dt": 0.02, "plan_change": "AE-01"}
    assert D["content"]["impulse_rad"] == 0.35 and D["measurement"]["sigma_rad"] == 0.03 and D["measurement"]["process_noise"] == 0.0
    assert D["data_per_context"] == {"train": 1000, "val": 250, "test": 1000} and D["contexts"]["n"] == 20
    assert D["streams"]["roles"] == {"locations": 10, "frequencies": 20, "targets": 30, "global_phase": 40, "measurement": 50,
                                     "surrogate": 60, "decoder": 70}
    assert (D["tasks"]["A"]["features"], D["tasks"]["B"]["features"]) == (66, 16)


def test_streams_are_deterministic_disjoint_and_exclude_aeon_seeds():
    a = streams.generator(SID, 3, "train", "targets", 7).uniform(size=5)
    assert np.array_equal(a, streams.generator(SID, 3, "train", "targets", 7).uniform(size=5))
    others = [streams.generator(SID, 3, sp, "targets", 7).uniform(size=5) for sp in ("val", "test")] + \
             [streams.generator(SID, 3, "train", "measurement", 7).uniform(size=5), streams.generator(SID, 4, "train", "targets", 7).uniform(size=5),
              streams.generator(SID, 3, "train", "targets", 8).uniform(size=5)]
    assert all(not np.array_equal(a, o) for o in others)
    for bad in (900000, 900104):
        with pytest.raises(streams.StreamError, match="excluded"):
            streams.generator(bad, 0, "train", "targets")
    with pytest.raises(streams.StreamError):
        streams.generator(SID, 0, "train", "nonsense")
    with pytest.raises(streams.StreamError):
        streams.generator(True, 0, "train", "targets")


# --- contexts and writing ----------------------------------------------------------------------------
def test_context_locations_are_disjoint_and_reference_unwritten(lab):
    for cid in range(5):
        c = contexts.make_context(SID, cid)
        assert len(set(c.write_nodes) | set(c.read_nodes)) == 17 and not set(c.write_nodes) & set(c.read_nodes)
        assert c.reference == c.read_nodes[-1] and c.reference not in c.write_nodes and abs(sum(c.omega)) < 1e-12
    assert contexts.make_context(SID, 0) == lab["ctx"] and contexts.make_context(SID, 1).permutation != lab["ctx"].permutation
    bad = replace(lab["ctx"], reference=lab["ctx"].write_nodes[0])
    with pytest.raises(ValueError, match="reference is an unwritten"):
        contexts.check_context(bad)


def test_writing_is_exact_and_controls_remove_the_content(lab):
    ctx = lab["ctx"]
    b = episodes.make_batch(ctx, "train", range(6))
    th = initial_state(ctx, b.u, b.phi, 0.35)
    for j, (p, q) in enumerate(ctx.write_pairs):                            # immediate inverse
        d = np.arctan2(np.sin(th[:, p] - th[:, q]), np.cos(th[:, p] - th[:, q]))
        assert np.allclose(d / (math.sqrt(2) * 0.35), b.u[:, j], atol=1e-13)
    others = [i for i in range(34) if i not in ctx.write_nodes]
    assert np.allclose(np.cos(th[:, others] - b.phi[:, None]), 1.0)          # unwritten nodes = phi
    u2 = -b.u
    for control in ("zero_impulse", "reset"):
        assert np.array_equal(initial_state(ctx, b.u, b.phi, 0.35, control), initial_state(ctx, u2, b.phi, 0.35, control))


@pytest.mark.parametrize("control", ["zero_impulse", "reset"])
def test_controls_give_identical_states_for_different_u_at_all_times(lab, control):
    ctx = lab["ctx"]
    b = episodes.make_batch(ctx, "train", range(5))
    b2 = replace(b, u=np.ascontiguousarray(-b.u[::-1]))
    s1 = episodes.simulate(ctx, b, lab["Cs"]["lantern"], lab["g"], control)
    s2 = episodes.simulate(ctx, b2, lab["Cs"]["lantern"], lab["g"], control)
    assert np.array_equal(s1, s2)


# --- observation and leak gates ----------------------------------------------------------------------
def test_task_views(lab):
    ctx = lab["ctx"]
    A, B = ob.observation_spec(ctx, "A"), ob.observation_spec(ctx, "B")
    assert (A.n_features, B.n_features) == (66, 16) and A.reference == B.reference == ctx.reference
    assert not set(B.nodes) & set(ctx.write_nodes) and set(B.nodes) | {B.reference} == set(ctx.read_nodes)
    for bad, match in ((replace(B, nodes=B.nodes[:-1] + (ctx.write_nodes[0],)), "write node|read nodes"),
                       (replace(A, nodes=A.nodes[:-1]), "all nodes")):
        with pytest.raises(ValueError, match=match):
            ob.check_observation(ctx, bad)
    with pytest.raises(ValueError, match="unwritten"):
        ob.check_observation(ctx, replace(B, reference=ctx.write_nodes[1]))


def test_reference_leak_negative_B_features_at_t0_carry_no_target(lab):
    """At t = 0 only write nodes carry u; with an unwritten reference, B's features are IDENTICAL for
    different u (same phi and eps). With a written reference they would differ (mutant)."""
    ctx = lab["ctx"]
    b = episodes.make_batch(ctx, "train", range(8))
    th1 = initial_state(ctx, b.u, b.phi, 0.35)
    th2 = initial_state(ctx, -b.u, b.phi, 0.35)
    B = ob.observation_spec(ctx, "B")
    assert np.array_equal(ob.features(th1, b.eps[:, 0], B), ob.features(th2, b.eps[:, 0], B))
    A = ob.observation_spec(ctx, "A")
    assert not np.array_equal(ob.features(th1, b.eps[:, 0], A), ob.features(th2, b.eps[:, 0], A))
    leaky = ob.ObservationSpec("B", B.nodes, ctx.write_nodes[0])             # a written reference, bypassing the check
    assert not np.array_equal(ob.features(th1, b.eps[:, 0], leaky), ob.features(th2, b.eps[:, 0], leaky))


def test_uncoupled_B_features_independent_of_u_at_all_times(lab):
    """No coupling -> nothing reaches the read nodes: catches re-writing during the pause, target-dependent
    frequencies and source-node features (plan mutants 7, 8, 10)."""
    ctx = lab["ctx"]
    b = episodes.make_batch(ctx, "test", range(6))
    b2 = replace(b, u=np.ascontiguousarray(np.roll(b.u, 1, axis=0) * -0.5))
    s1 = episodes.simulate(ctx, b, lab["Cs"]["uncoupled"], lab["g"])
    s2 = episodes.simulate(ctx, b2, lab["Cs"]["uncoupled"], lab["g"])
    B = ob.observation_spec(ctx, "B")
    for t in range(7):
        assert np.array_equal(ob.features(s1[:, t], b.eps[:, t], B), ob.features(s2[:, t], b.eps[:, t], B))


def test_measurement_errors_shared_between_tasks_and_addressed_per_episode(lab):
    ctx = lab["ctx"]
    b = episodes.make_batch(ctx, "val", range(10))
    sub = episodes.make_batch(ctx, "val", [7, 3])
    assert np.array_equal(sub.eps, b.eps[[7, 3]]) and np.array_equal(sub.u, b.u[[7, 3]]) and np.array_equal(sub.phi, b.phi[[7, 3]])
    st = np.zeros((10, 34))
    A, B = ob.observation_spec(ctx, "A"), ob.observation_spec(ctx, "B")
    fa, fb = ob.features(st, b.eps[:, 2], A), ob.features(st, b.eps[:, 2], B)
    for k, node in enumerate(B.nodes):                                       # same eps on common nodes
        assert np.array_equal(fb[:, k], fa[:, A.nodes.index(node)])
    assert not np.array_equal(episodes.make_batch(ctx, "train", [0]).u, episodes.make_batch(ctx, "test", [0]).u)


def test_batch_size_and_order_independence_of_the_simulation(lab):
    ctx = lab["ctx"]
    b = episodes.make_batch(ctx, "train", range(7))
    full = episodes.simulate(ctx, b, lab["Cs"]["lantern"], lab["g"], chunk=256)
    for chunk in (1, 3):
        assert np.max(np.abs(full - episodes.simulate(ctx, b, lab["Cs"]["lantern"], lab["g"], chunk=chunk))) <= 1e-13
    rb = episodes.make_batch(ctx, "train", range(6, -1, -1))
    assert np.max(np.abs(full[::-1] - episodes.simulate(ctx, rb, lab["Cs"]["lantern"], lab["g"]))) <= 1e-13


def test_matrices_and_frequencies_unchanged_and_no_global_rng(lab):
    ctx = lab["ctx"]
    C0 = {k: v.copy() for k, v in lab["Cs"].items()}
    om0 = ctx.omega_array().copy()
    np.random.seed(3)
    st = np.random.get_state()[1].copy()
    b = episodes.make_batch(ctx, "train", range(3))
    for k in episodes.CONDITIONS:
        episodes.simulate(ctx, b, lab["Cs"][k], lab["g"])
    assert all(np.array_equal(C0[k], lab["Cs"][k]) for k in C0) and np.array_equal(om0, ctx.omega_array())
    assert np.array_equal(st, np.random.get_state()[1])
    assert not ctx.omega_array().flags.writeable and not b.u.flags.writeable and not b.eps.flags.writeable


def test_joint_permutation_of_all_node_objects_keeps_the_features(lab):
    """Plan 10: permuting ALL IDs, matrices, inputs and outputs together changes no prediction
    (plan mutant 2 permutes only C)."""
    ctx = lab["ctx"]
    perm = np.random.default_rng(5).permutation(34)                         # new index k holds old node perm[k]
    inv = np.argsort(perm)
    pctx = contexts.ContextSpec(ctx.study_id, ctx.context_id, tuple(int(inv[i]) for i in ctx.permutation),
                                tuple((int(inv[a]), int(inv[b])) for a, b in ctx.write_pairs), tuple(int(inv[i]) for i in ctx.read_nodes),
                                int(inv[ctx.reference]), tuple(ctx.omega[i] for i in perm))
    b = episodes.make_batch(ctx, "train", range(5))
    pb = replace(b, eps=np.ascontiguousarray(b.eps[:, :, perm]))
    C = lab["Cs"]["lantern"]
    s = episodes.simulate(ctx, b, C, lab["g"])
    ps = episodes.simulate(pctx, pb, C[np.ix_(perm, perm)], lab["g"])
    for task in ("B",):                                                      # B's feature order follows the read list
        f = ob.features(s[:, 5], b.eps[:, 5], ob.observation_spec(ctx, task))
        pf = ob.features(ps[:, 5], pb.eps[:, 5], ob.observation_spec(pctx, task))
        assert np.max(np.abs(f - pf)) < 1e-12
    wrong = episodes.simulate(ctx, b, C[np.ix_(perm, perm)], lab["g"])      # mutant 2: only C permuted
    assert np.max(np.abs(ob.features(wrong[:, 5], b.eps[:, 5], ob.observation_spec(ctx, "B"))
                         - ob.features(s[:, 5], b.eps[:, 5], ob.observation_spec(ctx, "B")))) > 1e-6


# --- reference networks --------------------------------------------------------------------------------
def test_reference_networks_and_strength_surrogate_invariants(lab):
    C, Cs = lab["C"], lab["Cs"]
    assert set(Cs) == set(episodes.CONDITIONS) and np.array_equal(Cs["lantern"], C)
    assert np.all(Cs["uncoupled"] == 0)
    U = Cs["uniform_total"]
    assert U.sum() == pytest.approx(C.sum(), rel=1e-14) and np.all(np.diag(U) == 0) and np.ptp(U[np.triu_indices(34, 1)]) == 0
    assert np.max(np.abs(U.sum(1) - C.sum(1))) > 1.0                       # same total, not the same strengths
    S = Cs["strength_surrogate"]
    rep = surrogates.invariant_report(C, S)
    assert rep["ok"] and rep["max_strength_deviation"] <= 1e-12 and rep["frobenius_distance"] > 1.0
    S2, rep2 = surrogates.strength_surrogate(C, streams.generator(SID, 0, "context", "surrogate"), 2000)
    assert np.array_equal(S, S2) and rep2["degenerate"] >= 0 and rep2["proposals"] == 2000
    S3, _ = surrogates.strength_surrogate(C, streams.generator(SID, 1, "context", "surrogate"), 2000)
    assert not np.array_equal(S, S3)                                         # own draw per context


def test_each_draw_comes_from_its_own_role_stream(lab):
    """u, phi and eps of an episode come from the targets, global_phase and measurement streams of THAT
    episode -- noise never from the target stream (mutation check found this gap)."""
    ctx = lab["ctx"]
    b = episodes.make_batch(ctx, "test", [4])
    assert np.array_equal(b.u[0], streams.generator(SID, 0, "test", "targets", 4).uniform(-1.0, 1.0, 4))
    assert b.phi[0] == streams.generator(SID, 0, "test", "global_phase", 4).uniform(-np.pi, np.pi)
    assert np.array_equal(b.eps[0], streams.generator(SID, 0, "test", "measurement", 4).normal(0.0, 0.03, (7, 34)))


def test_every_context_gets_its_own_surrogate_draw():
    """Through the production path coupling_matrices (mutation check found that only direct draws were tested)."""
    s = ra.load_verified_snapshot()
    C = np.array(s.C)
    S0 = episodes.coupling_matrices(C, contexts.make_context(SID, 0), proposals=500)["strength_surrogate"]
    S1 = episodes.coupling_matrices(C, contexts.make_context(SID, 1), proposals=500)["strength_surrogate"]
    assert not np.array_equal(S0, S1)
    assert np.array_equal(S0, surrogates.strength_surrogate(C, streams.generator(SID, 0, "context", "surrogate"), 500)[0])


def test_strength_surrogate_rejects_invalid_input():
    with pytest.raises(ValueError):
        surrogates.strength_surrogate(np.array([[0.0, 2.0], [2.0, 0.0]]), np.random.default_rng(0), 10)
    with pytest.raises(ValueError):
        surrogates.strength_surrogate(np.array([[0.0, -0.1], [-0.1, 0.0]]), np.random.default_rng(0), 10)


def test_information_free_B_baseline_is_one_third():
    """Target variance of Uniform([-1, 1]) is 1/3: the population-optimal MSE of an information-free predictor."""
    ctx = contexts.make_context(SID, 2)
    u = episodes.make_batch(ctx, "train", range(3000)).u
    assert np.mean(u ** 2) == pytest.approx(1 / 3, abs=0.01) and abs(float(np.mean(u))) < 0.02
