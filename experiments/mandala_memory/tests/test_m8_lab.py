"""M8 tests: knob lab -- bounded knobs, same kernel as the benchmark, the q
bound is a bound (never exceeded, often loose), ablation and partial clearing
semantics, readout operators, explicit memory-duration definition, logging
(new run id, never overwrite, benchmark untouched), HTTP routes."""
import json
import math
import threading
import urllib.error
import urllib.request
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pytest

import experiments.mandala_memory.serve as serve
from experiments.mandala_memory import lab
from experiments.mandala_memory.core import MemoryLabError, recall_state
from experiments.mandala_memory.model import condition_specs

UI = Path(r"D:/mandala/.worktrees/unified-mandala-memory-lab/experiments/memory_lab")
TEST_EXPLORE = Path(r"D:/mandala/.tmp/mandala-memory/test-results/explore")
B = lab.BENCHMARK_KNOBS


@pytest.mark.parametrize("bad", [
    {"path": "C:/x"}, {"gamma": 1.0}, {"gamma": True}, {"gamma": float("nan")}, {"ell": 0.0}, {"c": -0.1},
    {"sigma": "0.02"}, {"N": 7}, {"N": 12, "M": 5}, {"N": 12, "M": 12}, {"M": 0}, {"inputs": [3, 3]},
    {"inputs": [0, 12]}, {"inputs": [0]}, {"clear": "evil"}, {"clear": "module", "clear_module": 3},
    {"readout": "secret"}, {"readout": "node", "readout_node": 12}, {"ablation": {"edges": [[1, 1]]}},
    {"ablation": {"edges": [[1, 2, 3]]}}, {"ablation": {"edges": [], "mode": "x"}},
    {"ablation": {"edges": [], "file": "a"}}, {"p_star": 0.5}, {"amplitude": 3.5}, {"nonlinearity": "relu"},
])
def test_validation_rejects(bad):
    with pytest.raises(MemoryLabError):
        lab.validate_knobs(bad)


def test_lab_request_shape_rejected():
    for bad in ({}, {"knobs": {}, "extra": 1}, [], {"runs": []}):
        with pytest.raises(MemoryLabError):
            serve.lab(bad, write=False)


def test_benchmark_knobs_reproduce_the_frozen_network_and_kernel():
    frozen = condition_specs(serve.CONFIG["network"])["frozen"]
    net = lab.build_lab_network(lab.validate_knobs({}))
    assert np.array_equal(net["spec"].A, frozen.A) and np.array_equal(net["spec"].B, frozen.B)
    p = lab.compute({})
    for d in (0, 1, 2, 4, 8, 16, 32, 64):
        assert np.array_equal(np.array(p["trajectory"]["A"][d + 1]), recall_state(frozen, 0, d))
        assert np.array_equal(np.array(p["trajectory"]["B"][d + 1]), recall_state(frozen, 1, d))
    ref = serve.explore({"runs": [{"network": "frozen", "stimulus": 0, "delay": 8},
                                  {"network": "frozen", "stimulus": 1, "delay": 8}]}, write=False)
    assert p["curve"]["bayes"][8] == ref["comparison"]["bayes_accuracy_full_observation"]
    assert abs(p["curve"]["bayes"][8] - 0.683) < 5e-4 and abs(p["network"]["q_effective"] - 0.9) < 1e-15


def _random_knobs(rng):
    N = int(rng.choice(lab.N_CHOICES))
    Ms = [m for m in range(1, N // 2 + 1) if N % m == 0]
    M = int(rng.choice(Ms))
    i0, i1 = (int(v) for v in rng.choice(N, 2, replace=False))
    edges = [[int(a), int(b)] for a, b in (rng.choice(N, 2, replace=False) for _ in range(int(rng.integers(0, 8))))]
    return {"N": N, "M": M, "c": float(rng.uniform(0, 1)), "gamma": float(rng.uniform(0.05, 0.99)),
            "ell": float(rng.uniform(0.05, 1)), "amplitude": float(rng.uniform(0.05, 3)),
            "sigma": float(rng.uniform(0.001, 0.5)), "inputs": [i0, i1],
            "nonlinearity": str(rng.choice(["tanh", "identity"])), "clear": str(rng.choice(["none", "module"])),
            "clear_module": int(rng.integers(0, M)), "readout": str(rng.choice(lab.READOUTS)),
            "readout_node": int(rng.integers(0, N)),
            "ablation": {"edges": edges, "mode": str(rng.choice(lab.ABLATION_MODES))}}


def test_q_bound_is_never_exceeded():
    rng = np.random.default_rng(20261003)
    for _ in range(60):
        p = lab.compute(_random_knobs(rng))
        for s, b in zip(p["curve"]["separation_l2"], p["curve"]["q_bound_separation"]):
            assert s <= b * (1 + 1e-12) + 1e-15
        assert all(x <= y + 1e-15 for x, y in zip(p["curve"]["bayes"], p["curve"]["q_bound_bayes"]))


def test_same_q_different_memory_and_bound_is_loose():
    """Johann's point, made checkable: q is only an upper bound. Three networks
    with the SAME q_eff = 0.9 keep the trace for clearly different times."""
    ds = {}
    for c in (0.05, 0.25, 0.5):
        p = lab.compute({"c": c})
        assert abs(p["network"]["q_effective"] - 0.9) < 1e-15
        ds[c] = p["memory_duration"]["last_delay_at_or_above"]
        if c == 0.25:
            assert p["curve"]["separation_l2"][16] < 0.05 * p["curve"]["q_bound_separation"][16]
    assert ds[0.05] > ds[0.25] > ds[0.5]


def test_ablation_budget_loss_and_renormalize():
    edges = [[0, 1], [0, 5]]
    lo = lab.build_lab_network(lab.validate_knobs({"ablation": {"edges": edges, "mode": "budget_loss"}}))
    A = lo["spec"].A
    for i, j in edges:
        assert A[i, j] == 0 and A[j, i] == 0
    rs = A.sum(axis=1)
    assert all(rs[r] < 0.8 - 1e-9 for r in (0, 1, 5)) and all(abs(rs[r] - 0.8) < 1e-12 for r in range(12) if r not in (0, 1, 5))
    assert lo["q_effective"] == pytest.approx(0.9)       # untouched rows still carry the full budget
    rn = lab.build_lab_network(lab.validate_knobs({"ablation": {"edges": edges, "mode": "renormalize"}}))
    assert np.allclose(rn["spec"].A.sum(axis=1), 0.8, atol=1e-12) and rn["rows_emptied"] == []
    assert rn["spec"].A[0, 2] > lo["spec"].A[0, 2]      # the remaining edges of a touched row grow
    # a row without any edge left stays empty and is reported
    em = lab.build_lab_network(lab.validate_knobs({"N": 6, "M": 3, "c": 0.0,
                                                    "ablation": {"edges": [[0, 1]], "mode": "renormalize"}}))
    assert em["rows_emptied"] == [0, 1] and not em["spec"].A[0].any()
    assert em["ablation_already_zero"] == []
    z = lab.build_lab_network(lab.validate_knobs({"c": 0.0, "ablation": {"edges": [[0, 4]]}}))
    assert z["ablation_already_zero"] == [[0, 4]]


def test_ablating_every_edge_is_the_uncoupled_leak_model():
    all_edges = [[i, j] for i in range(12) for j in range(i + 1, 12)]
    p = lab.compute({"ablation": {"edges": all_edges, "mode": "budget_loss"}})
    leak = condition_specs(serve.CONFIG["network"])["uncoupled_leak"]
    for d in (0, 4, 8):
        assert np.array_equal(np.array(p["trajectory"]["A"][d + 1]), recall_state(leak, 0, d))
    assert p["network"]["q_effective"] == pytest.approx(0.5)


def test_clear_all_and_clear_one_module():
    p = lab.compute({"clear": "all"})
    assert all(b == 0.5 for b in p["curve"]["bayes"]) and p["memory_duration"]["last_delay_at_or_above"] is None
    q = lab.compute({"clear": "module", "clear_module": 1})
    x1, raw = np.array(q["trajectory"]["B"][1]), np.array(q["trajectory"]["pulse_raw_B"])
    assert not x1[4:8].any() and np.array_equal(x1[:4], raw[:4]) and np.array_equal(x1[8:], raw[8:])
    assert raw[4] > 0                                     # the pulse did arrive before clearing
    # the pulse lands only on node 4, so clearing its module erases trace B completely:
    # x_B = 0 and the difference is x_A itself -- which now carries the slow common
    # (Perron) mode, so the ideal separation lasts LONGER than without clearing
    assert not np.array(q["trajectory"]["B"]).any()
    full = lab.compute({})
    dA = np.array(q["trajectory"]["A"])
    assert np.array_equal(dA, np.array(full["trajectory"]["A"]))
    assert q["curve"]["bayes"][16] > full["curve"]["bayes"][16] + 0.05


def test_readout_operators():
    p = lab.compute({})
    dx = np.array(p["trajectory"]["A"]) - np.array(p["trajectory"]["B"])
    s = lab.compute({"readout": "sum"})
    assert all(abs(b - 0.5) < 1e-9 for b in s["curve"]["bayes"])   # symmetric inputs: the sum carries nothing
    m = lab.compute({"readout": "module_means"})
    for d in (0, 8):
        mm = np.array([dx[d + 1][4 * k:4 * k + 4].mean() for k in range(3)])
        assert m["curve"]["separation_l2"][d] == pytest.approx(float(np.linalg.norm(mm)), rel=1e-12)
    n = lab.compute({"readout": "node", "readout_node": 4})
    assert n["curve"]["separation_l2"][3] == pytest.approx(abs(dx[4][4]), rel=1e-12)
    assert n["readout"]["kappa"] == 1 and m["readout"]["kappa"] == pytest.approx(math.sqrt(3))


def test_identity_nonlinearity_is_exactly_linear_propagation():
    p = lab.compute({"nonlinearity": "identity"})
    net = lab.build_lab_network(lab.validate_knobs({"nonlinearity": "identity"}))
    J = 0.5 * np.eye(12) + 0.5 * net["spec"].A
    dx = np.array(p["trajectory"]["A"]) - np.array(p["trajectory"]["B"])
    for d in (1, 5, 20):
        pred = np.linalg.matrix_power(J, d) @ dx[1]
        assert np.max(np.abs(dx[d + 1] - pred)) <= 1e-12 * np.max(np.abs(pred))


def test_memory_duration_definition():
    md = lab.memory_duration([0.9, 0.8, 0.74, 0.76, 0.6], 0.75)
    assert md["last_delay_at_or_above"] == 3 and md["first_passage"] == 1 and md["monotone_non_increasing"] is False
    assert lab.memory_duration([0.7, 0.6], 0.75)["last_delay_at_or_above"] is None
    assert lab.memory_duration([0.7, 0.6], 0.75)["first_passage"] is None
    cz = lab.memory_duration([0.99, 0.95], 0.75)
    assert cz["censored_at_d_max"] and cz["first_passage"] == 1 and cz["last_delay_at_or_above"] == 1
    # benchmark: Phi(||dx|| / 2 sigma) crosses 0.75 between d = 6 and d = 7
    b = lab.compute({})["curve"]["bayes"]
    assert b[6] >= 0.75 > b[7] and lab.compute({})["memory_duration"]["last_delay_at_or_above"] == 6
    assert b[8] == NormalDist().cdf(lab.compute({})["curve"]["separation_l2"][8] / 0.04)


def test_lab_logging_new_ids_never_overwrite(monkeypatch):
    monkeypatch.setattr(serve, "EXPLORE_DIR", TEST_EXPLORE)
    a, b = serve.lab({"knobs": {"c": 0.1}}), serve.lab({"knobs": {"c": 0.1}})
    assert a["run_id"] != b["run_id"] and a["run_id"].startswith("lab-") and a["explorative"] is True
    assert (TEST_EXPLORE / f"{a['run_id']}.json").is_file()
    last = [json.loads(l) for l in (TEST_EXPLORE / "protocol.jsonl").read_text(encoding="utf-8").strip().splitlines()[-2:]]
    assert {l["run_id"] for l in last} == {a["run_id"], b["run_id"]}
    assert all(l["kind"] == "lab" and l["knobs"]["c"] == 0.1 and l["explorative"] for l in last)
    with pytest.raises(FileExistsError):
        serve._log(a, "lab", {"knobs": a["knobs"]})
    assert a["reference_curve"]["bayes"][8] == pytest.approx(0.683, abs=5e-4)


def test_lab_never_writes_benchmark(monkeypatch):
    monkeypatch.setattr(serve, "EXPLORE_DIR", TEST_EXPLORE)
    bench = Path(r"D:/mandala/mandala-memory-results")
    files = [p for d in ("smoke", "research") for p in (bench / d).glob("*.json")] if bench.exists() else []
    before = {p: (p.stat().st_mtime, p.stat().st_size) for p in files}
    proto = serve.HERE / "protocol" / "startkonfiguration.json"
    pb = proto.read_bytes()
    serve.lab({"knobs": {"gamma": 0.95, "ablation": {"edges": [[0, 1]], "mode": "renormalize"}}})
    assert {p: (p.stat().st_mtime, p.stat().st_size) for p in files} == before and proto.read_bytes() == pb


def test_explore_dir_can_be_redirected_but_never_to_c(monkeypatch):
    monkeypatch.setattr(serve, "EXPLORE_DIR", serve.EXPLORE_DIR)          # restored after the test
    with pytest.raises(MemoryLabError):
        serve.set_explore_dir("C:/mandala-check")
    target = TEST_EXPLORE.parent / "redirected"
    assert serve.set_explore_dir(target) == target
    p = serve.lab({"knobs": {}})
    assert (target / f"{p['run_id']}.json").is_file()


@pytest.fixture()
def server(monkeypatch):
    monkeypatch.setattr(serve, "EXPLORE_DIR", TEST_EXPLORE)
    srv = serve.make_server(0, UI)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield srv
    srv.shutdown()


def test_http_lab_routes(server):
    base = f"http://127.0.0.1:{server.server_address[1]}"
    assert "Regler" in urllib.request.urlopen(base + "/lab.html", timeout=10).read().decode("utf-8")
    assert urllib.request.urlopen(base + "/lab.js", timeout=10).status == 200
    preset = json.loads(urllib.request.urlopen(base + "/api/preset", timeout=10).read())
    assert preset["lab"]["benchmark_knobs"] == B and preset["lab"]["d_max"] == 64
    ok = urllib.request.Request(base + "/api/lab", data=json.dumps({"knobs": {"ell": 0.25}}).encode(),
                                headers={"Content-Type": "application/json"})
    p = json.loads(urllib.request.urlopen(ok, timeout=10).read())
    assert p["run_id"].startswith("lab-") and len(p["curve"]["bayes"]) == 65
    for body in (b'{"knobs": {"gamma": 2}}', b'{"knobs": {}, "x": 1}', b'{"knobs": {"inputs": ' + b'[0,' * 9000 + b'1]}'):
        bad = urllib.request.Request(base + "/api/lab", data=body, headers={"Content-Type": "application/json"})
        with pytest.raises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(bad, timeout=10)
        assert e.value.code == 400
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(base + "/lab.py", timeout=10)
    assert e.value.code == 404
