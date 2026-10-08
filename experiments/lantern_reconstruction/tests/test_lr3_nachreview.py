"""Follow-up review LANTERN_LR3_NACHREVIEW_2026-10-08 (Astra, reviewed stand d43427d): one regression
test per reproduced counterexample (F1a, F1b, F2, E1, E2) with the review's exact inputs, plus positive
controls that valid A/B features, contexts and streams stay unchanged. Run with the other Lantern tests."""
from __future__ import annotations

import hashlib
from dataclasses import replace

import numpy as np
import pytest

from experiments.lantern_reconstruction import contexts, episodes, streams
from experiments.lantern_reconstruction import observation as ob
from experiments.lantern_reconstruction.encoding import initial_state

SID = 2026100803          # the review's study id (= development_study_id)


@pytest.fixture(scope="module")
def lab():
    ctx = contexts.make_context(SID, 0)
    b = episodes.make_batch(ctx, "test", [0, 1, 2, 3])
    return {"ctx": ctx, "b": b, "th": initial_state(ctx, b.u, b.phi, .35), "th_alt": initial_state(ctx, -b.u, b.phi, .35),
            "A": ob.observation_spec(ctx, "A"), "B": ob.observation_spec(ctx, "B")}


def _old_kernel(states, eps, spec):
    """features() of d43427d verbatim, as the bit-identity reference for VALID inputs."""
    y = np.asarray(states) + np.asarray(eps)
    d = y[:, list(spec.nodes)] - y[:, [spec.reference]]
    return np.concatenate([np.sin(d), np.cos(d)], axis=1)


# --- F1: observation specification ---------------------------------------------------------------------
def test_f1a_unknown_task_with_write_nodes_rejected(lab):
    """Review F1a: ObservationSpec('b', write_nodes, reference) was accepted; its t=0 features then
    differed by 0.4353948827558046 between targets u and -u (a target leak)."""
    ctx = lab["ctx"]
    bad = ob.ObservationSpec("b", ctx.write_nodes, ctx.reference)
    assert np.max(np.abs(_old_kernel(lab["th"], lab["b"].eps[:, 0], bad) - _old_kernel(lab["th_alt"], lab["b"].eps[:, 0], bad))) \
        == 0.4353948827558046                                              # the review's value: the leak is real
    for call in (lambda: ob.check_observation(ctx, bad), lambda: ob.observe(ctx, bad, lab["th"], lab["b"].eps[:, 0]),
                 lambda: ob.features(lab["th"], lab["b"].eps[:, 0], bad)):
        with pytest.raises(ValueError, match="exactly 'A' or 'B'"):
            call()
    for task in ("a", "B ", "", None, 1, ("B",)):
        with pytest.raises(ValueError, match="exactly 'A' or 'B'"):
            ob.check_observation(ctx, replace(lab["B"], task=task))


def test_f1b_negative_index_alias_of_the_reference_rejected(lab):
    """Review F1b: node -26 aliases reference 8 under NumPy; the spec kept 33 'distinct' entries and
    produced a constant (sin 0, cos 1) pair instead of a coordinate."""
    ctx, A = lab["ctx"], lab["A"]
    assert ctx.reference == 8
    neg = replace(A, nodes=(ctx.reference - 34,) + A.nodes[1:])
    assert neg.nodes[0] == -26 and len(set(neg.nodes)) == 33
    f = _old_kernel(lab["th"], lab["b"].eps[:, 0], neg)
    assert f.shape == (4, 66) and np.all(f[:, 0] == 0) and np.all(f[:, 33] == 1)   # the silent alias
    for call in (lambda: ob.check_observation(ctx, neg), lambda: ob.features(lab["th"], lab["b"].eps[:, 0], neg),
                 lambda: ob.observe(ctx, neg, lab["th"], lab["b"].eps[:, 0])):
        with pytest.raises(ValueError, match=r"\[0, 34\)"):
            call()


@pytest.mark.parametrize("node", [-1, 34, 8.0, True, np.bool_(True), "3", None])
def test_f1_feature_and_reference_indices_are_true_in_range_integers(lab, node):
    ctx, B = lab["ctx"], lab["B"]
    with pytest.raises(ValueError, match=r"\[0, 34\)"):
        ob.check_observation(ctx, replace(B, nodes=(node,) + B.nodes[1:]))
    with pytest.raises(ValueError, match=r"\[0, 34\)"):
        ob.check_observation(ctx, replace(B, reference=node))


def test_f1_reference_and_node_order_must_be_the_factorys(lab):
    ctx, A, B = lab["ctx"], lab["A"], lab["B"]
    # another unwritten read node as reference, with the B node set otherwise consistent
    other = ob.ObservationSpec("B", B.nodes[1:] + (B.reference,), B.nodes[0])
    with pytest.raises(ValueError):
        ob.check_observation(ctx, other)
    other_A = ob.ObservationSpec("A", tuple(i for i in range(34) if i != B.nodes[0]), B.nodes[0])   # unwritten, valid indices
    with pytest.raises(ValueError, match="context's reference"):
        ob.check_observation(ctx, other_A)
    with pytest.raises(ValueError, match="all nodes"):
        ob.check_observation(ctx, replace(A, nodes=tuple(reversed(A.nodes))))
    with pytest.raises(ValueError, match="all nodes"):
        ob.check_observation(ctx, replace(A, nodes=A.nodes[1:] + A.nodes[:1]))
    with pytest.raises(ValueError, match="feature nodes"):
        ob.check_observation(ctx, replace(A, nodes=list(A.nodes)))                            # a list is not the fixed tuple


def test_f1_observation_entry_validates_the_context(lab):
    ctx, B = lab["ctx"], lab["B"]
    broken = replace(ctx, omega=(0.1,) * 34)
    with pytest.raises(ValueError, match="omega"):
        ob.check_observation(broken, B)
    with pytest.raises(ValueError, match="omega"):
        ob.observe(broken, B, lab["th"], lab["b"].eps[:, 0])


# --- F2: array contract of the feature kernel ------------------------------------------------------------
def test_f2_per_episode_noise_broadcast_rejected(lab):
    """Review F2: eps (4, 1) was broadcast to all nodes and cancelled exactly in the reference
    differences: the result equalled the noiseless one (difference 0)."""
    B = lab["B"]
    states = np.zeros((4, 34))
    eps = np.array([[0.1], [0.2], [0.3], [0.4]])
    assert np.max(np.abs(_old_kernel(states, eps, B) - _old_kernel(states, np.zeros_like(states), B))) == 0.0
    with pytest.raises(ValueError, match="shape"):
        ob.features(states, eps, B)
    with pytest.raises(ValueError, match="shape"):
        ob.observe(lab["ctx"], B, states, eps)


@pytest.mark.parametrize("states, eps", [
    (np.zeros((4, 34)), np.zeros(34)),                          # (34,)
    (np.zeros((4, 34)), np.zeros((1, 34))),                     # one row for several episodes
    (np.zeros((4, 34)), 0.0),                                   # scalar
    (np.zeros((4, 34)), np.zeros((4, 35))),
    (np.zeros((4, 34)), np.zeros((3, 34))),                     # same width, other n
    (np.zeros((4, 34, 1)), np.zeros((4, 34, 1))),
    (np.zeros(34), np.zeros(34)),
    (np.zeros((0, 34)), np.zeros((0, 34))),                     # no episode
    (np.zeros((4, 1)), np.zeros((4, 34))),                      # broadcasting on the states side
    (np.zeros((4, 35)), np.zeros((4, 35))),                     # SAME wrong width on both sides (mutation check:
    (np.zeros((4, 33)), np.zeros((4, 33))),                     # the equal-shape test alone does not catch these)
])
def test_f2_wrong_shapes_rejected(lab, states, eps):
    with pytest.raises(ValueError, match="shape"):
        ob.features(states, eps, lab["B"])


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
@pytest.mark.parametrize("side", ["states", "eps"])
def test_f2_nonfinite_rejected(lab, bad, side):
    a, e = np.zeros((4, 34)), np.zeros((4, 34))
    (a if side == "states" else e)[2, 8] = bad                  # the reference column of the review's context
    with pytest.raises(ValueError, match="finite"):
        ob.features(a, e, lab["B"])


@pytest.mark.parametrize("dtype", [bool, complex, object])
def test_f2_non_real_dtypes_rejected(lab, dtype):
    with pytest.raises(ValueError, match="real numeric"):
        ob.features(np.zeros((4, 34)), np.zeros((4, 34), dtype=dtype), lab["B"])
    with pytest.raises(ValueError, match="real numeric"):
        ob.features(np.zeros((4, 34), dtype=dtype), np.zeros((4, 34)), lab["B"])


def test_f2_rejection_happens_before_any_arithmetic(lab, monkeypatch):
    calls = []
    monkeypatch.setattr(ob.np, "concatenate", lambda *a, **k: calls.append(1))
    with pytest.raises(ValueError):
        ob.features(np.zeros((4, 34)), np.zeros((4, 1)), lab["B"])
    assert calls == []


# --- positive controls: valid inputs unchanged ------------------------------------------------------------
def test_valid_A_B_features_bit_identical_to_the_reviewed_kernel(lab):
    ctx = lab["ctx"]
    b = episodes.make_batch(ctx, "val", range(6))
    for th in (initial_state(ctx, b.u, b.phi, .35), initial_state(ctx, b.u, b.phi, .35, "reset")):
        for spec in (lab["A"], lab["B"]):
            for t in range(b.eps.shape[1]):
                new = ob.observe(ctx, spec, th, b.eps[:, t])
                assert np.array_equal(new, _old_kernel(th, b.eps[:, t], spec)) and new.dtype == np.float64
                assert np.array_equal(new, ob.features(th, b.eps[:, t], spec))
    ints, f32 = np.arange(68).reshape(2, 34), np.linspace(0, 3, 68, dtype=np.float32).reshape(2, 34)
    assert np.array_equal(ob.features(ints, np.zeros((2, 34), dtype=np.int64), lab["B"]), _old_kernel(ints, np.zeros((2, 34), dtype=np.int64), lab["B"]))
    assert np.array_equal(ob.features(f32, f32 / 7, lab["A"]), _old_kernel(f32, f32 / 7, lab["A"]))


def test_review_controls_B_leak_free_A_carries_signal(lab):
    """The review's paired control under the validated entry point: B exactly target-free, A not."""
    ctx, b = lab["ctx"], lab["b"]
    assert np.array_equal(ob.observe(ctx, lab["B"], lab["th"], b.eps[:, 0]), ob.observe(ctx, lab["B"], lab["th_alt"], b.eps[:, 0]))
    assert not np.array_equal(ob.observe(ctx, lab["A"], lab["th"], b.eps[:, 0]), ob.observe(ctx, lab["A"], lab["th_alt"], b.eps[:, 0]))


# --- E1: context validator -----------------------------------------------------------------------------
def test_e1_float_read_nodes_rejected(lab):
    ctx = lab["ctx"]
    assert tuple(float(i) for i in ctx.read_nodes) == ctx.read_nodes          # why the old tuple comparison passed
    for bad in ({"read_nodes": tuple(float(i) for i in ctx.read_nodes)},
                {"read_nodes": ctx.read_nodes[:-1] + (float(ctx.reference),)},
                {"read_nodes": ctx.read_nodes[:-1] + (np.float64(ctx.reference),), "reference": np.float64(ctx.reference)},
                {"reference": float(ctx.reference)},
                {"reference": ctx.reference - 34}):
        with pytest.raises(ValueError, match=r"\[0, 34\)"):
            contexts.check_context(replace(ctx, **bad))


def test_e1_valid_contexts_unchanged():
    for c in range(20):
        ctx = contexts.make_context(SID, c)
        contexts.check_context(ctx)
        np_ctx = replace(ctx, read_nodes=tuple(np.int64(i) for i in ctx.read_nodes), reference=np.int64(ctx.reference))
        contexts.check_context(np_ctx)                                         # true NumPy integers stay valid


# --- E2: stream key encoding ----------------------------------------------------------------------------
def test_e2_multiword_alias_keys_rejected():
    """Review E2: (6321068099, 1, 0, 30, 0) and (2026100803, 4294967297, 0, 30, 0) gave the SAME stream."""
    a = np.random.SeedSequence([6321068099, 1, 0, 30, 0]).generate_state(16)
    b = np.random.SeedSequence([2026100803, 4294967297, 0, 30, 0]).generate_state(16)
    assert np.array_equal(a, b)                                                # the alias exists in NumPy itself
    with pytest.raises(streams.StreamError, match="2\\*\\*32"):
        streams.key(SID + 2**32, 1, "train", "targets")
    with pytest.raises(streams.StreamError, match="2\\*\\*32"):
        streams.key(SID, 1 + 2**32, "train", "targets")


@pytest.mark.parametrize("pos", ["study", "context", "episode", "extra"])
@pytest.mark.parametrize("value", [2**32, np.uint64(2**32), 2**64 + 5])
def test_e2_every_key_component_bounded(pos, value):
    args = {"study": SID, "context": 0, "episode": 0, "extra": 0, pos: value}
    with pytest.raises(streams.StreamError, match="non-negative integer below 2\\*\\*32"):
        streams.key(args["study"], args["context"], "test", "targets", args["episode"], args["extra"])
    with pytest.raises(ValueError):
        episodes.make_batch(contexts.make_context(SID, 0), "test", [value]) if pos == "episode" else streams.generator(
            args["study"], args["context"], "test", "targets", args["episode"], args["extra"])


def _digest(*arrays):
    m = hashlib.sha256()
    for a in arrays:
        a = np.ascontiguousarray(a)
        m.update(str(a.dtype).encode() + str(a.shape).encode() + a.tobytes())
    return m.hexdigest()


def test_e2_streams_inside_the_bound_unchanged():
    """Digests computed with the reviewed code d43427d (old-vs-new comparison of 173 outputs, see the
    LR3 report): the bound changes no valid stream, including the largest allowed component."""
    assert streams.key(SID, 0, "test", "decoder", 7, 3, 2**32 - 1) == (SID, 0, 2, 70, 7, 3, 4294967295)
    assert _digest(streams.generator(SID, 0, "train", "decoder", 2**32 - 1).random(8)) \
        == "f43b47eef53c9dd2704e4598a7dbcaf8a8858bcb5d6cf508fc84e21e86f2db82"
    b = episodes.make_batch(contexts.make_context(SID, 0), "test", range(25))
    assert _digest(b.u, b.phi, b.eps) == "44502d5c0ebb147e325988e45146ac1c2fac6a739ddee6b56ab4c125e58c29cb"
    assert contexts.fingerprint(contexts.make_context(SID, 0)) == "aec3f505fea90aae7f8976da0cd513e726117ef0d4365e508bb0c22619c30fdc"
