"""M6 tests: local service -- validation, traces from the tested kernel,
intervention, new run ids, path whitelist, 127.0.0.1 binding, no benchmark writes."""
import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pytest

import experiments.mandala_memory.serve as serve
from experiments.mandala_memory.core import MemoryLabError, recall_state

UI = Path(r"D:/mandala/.worktrees/unified-mandala-memory-lab/experiments/memory_lab")
TEST_EXPLORE = Path(r"D:/mandala/.tmp/mandala-memory/test-results/explore")


@pytest.mark.parametrize("bad", [
    {}, {"runs": []}, {"runs": [{"network": "frozen", "stimulus": 2, "delay": 3}]},
    {"runs": [{"network": "evil", "stimulus": 0, "delay": 3}]},
    {"runs": [{"network": "frozen", "stimulus": 0, "delay": 65}]},
    {"runs": [{"network": "frozen", "stimulus": 0, "delay": 3, "path": "C:/x"}]},
    {"runs": [{"network": "frozen", "stimulus": True, "delay": 3}]},
    {"runs": [{"network": "frozen", "stimulus": 0, "delay": 1}] * 5},
])
def test_validation_rejects(bad):
    with pytest.raises(MemoryLabError):
        serve.validate_request(bad)


def test_traces_come_from_the_tested_kernel():
    specs, _ = serve.networks()
    p = serve.explore({"runs": [{"network": "frozen", "stimulus": 0, "delay": 8},
                                {"network": "adapted", "stimulus": 1, "delay": 8}]}, write=False)
    for t in p["traces"]:
        ref = recall_state(specs[t["spec"]["network"]], t["spec"]["stimulus"], 8)
        assert np.array_equal(np.array(t["readout"]), ref)
        assert len(t["states"]) == 10 and t["phases"][1] == "stimulus" and t["phases"][-1] == "readout"
    assert p["explorative"] is True and p["comparison"]["observation_noise_sigma"] == 0.02


def test_comparison_reports_bayes_accuracy_over_all_coordinates():
    from statistics import NormalDist

    p = serve.explore({"runs": [{"network": "frozen", "stimulus": 0, "delay": 8},
                                {"network": "frozen", "stimulus": 1, "delay": 8}]}, write=False)
    c = p["comparison"]
    assert c["bayes_accuracy_full_observation"] == NormalDist().cdf(c["readout_separation_l2"] / (2 * 0.02))
    # uses the whole vector: the l2 separation exceeds the largest single coordinate
    assert c["readout_separation_l2"] > c["readout_separation_inf"]
    near = serve.explore({"runs": [{"network": "frozen", "stimulus": 0, "delay": 0},
                                   {"network": "frozen", "stimulus": 1, "delay": 0}]}, write=False)
    assert near["comparison"]["bayes_accuracy_full_observation"] > 0.999


def test_clear_intervention_and_identical_start():
    p = serve.explore({"runs": [{"network": "frozen", "stimulus": 0, "delay": 4, "intervention": "clear_after_pulse"},
                                {"network": "frozen", "stimulus": 1, "delay": 4, "intervention": "clear_after_pulse"}]}, write=False)
    for t in p["traces"]:
        assert t["phases"][2] == "cleared" and not any(t["readout"]) and t["events"]
        assert not any(t["states"][0]), "identical initial condition x0 = 0"
    assert p["comparison"]["readout_separation_l2"] == 0.0


def test_each_request_gets_a_new_run_id_and_protocol_entry(monkeypatch):
    monkeypatch.setattr(serve, "EXPLORE_DIR", TEST_EXPLORE)
    req = {"runs": [{"network": "frozen", "stimulus": 0, "delay": 2}]}
    a, b = serve.explore(req), serve.explore(req)
    assert a["run_id"] != b["run_id"]
    assert (TEST_EXPLORE / f"{a['run_id']}.json").is_file()
    lines = (TEST_EXPLORE / "protocol.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert {json.loads(l)["run_id"] for l in lines[-2:]} == {a["run_id"], b["run_id"]}


@pytest.fixture()
def server(monkeypatch):
    monkeypatch.setattr(serve, "EXPLORE_DIR", TEST_EXPLORE)
    srv = serve.make_server(0, UI)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield srv
    srv.shutdown()


def _get(srv, path):
    return urllib.request.urlopen(f"http://127.0.0.1:{srv.server_address[1]}{path}", timeout=10)


def test_http_routes_whitelist_and_binding(server):
    assert server.server_address[0] == "127.0.0.1"
    html = _get(server, "/").read().decode("utf-8")
    assert "Mandala-Gedächtnislabor" in html
    assert _get(server, "/app.js").headers["Content-Type"].startswith(("text/javascript", "application/javascript"))
    preset = json.loads(_get(server, "/api/preset").read())
    assert preset["read_only"] is True and preset["max_delay"] == 64
    for path in ("/../serve.py", "/FORMAT.md", "/README.md", "/%2e%2e/x", "/etc/passwd"):
        with pytest.raises(urllib.error.HTTPError) as e:
            _get(server, path)
        assert e.value.code == 404


def test_http_run_and_bad_request(server):
    url = f"http://127.0.0.1:{server.server_address[1]}/api/run"
    req = urllib.request.Request(url, data=json.dumps({"runs": [{"network": "frozen", "stimulus": 0, "delay": 3},
                                                               {"network": "frozen", "stimulus": 1, "delay": 3}]}).encode(),
                                 headers={"Content-Type": "application/json"})
    p = json.loads(urllib.request.urlopen(req, timeout=10).read())
    assert p["run_id"].startswith("explore-") and len(p["traces"]) == 2
    bad = urllib.request.Request(url, data=b'{"runs": [{"network": "frozen", "stimulus": 0, "delay": 999}]}',
                                 headers={"Content-Type": "application/json"})
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(bad, timeout=10)
    assert e.value.code == 400


def test_benchmark_results_are_never_written(monkeypatch):
    monkeypatch.setattr(serve, "EXPLORE_DIR", TEST_EXPLORE)
    bench = Path(r"D:/mandala/mandala-memory-results")
    before = {p: p.stat().st_mtime for d in ("smoke", "research") for p in (bench / d).glob("*.json")} if bench.exists() else {}
    serve.explore({"runs": [{"network": "adapted", "stimulus": 1, "delay": 16}]})
    after = {p: p.stat().st_mtime for p in before}
    assert before == after
