"""Package V1 (cosmic inheritance plan): physics kernel and run contracts.

Covers findings F2, F3, F4 and observations N1, N2, N4 of the roadmap section
"Kosmische Vererbung" (experiments/research_roadmap_2026/ROADMAP.md). The
review's failure reproductions are replaced by tests of the corrected
invariants: momentum conservation, order independence, repeatability,
parameter positive/negative controls, import and shutdown.

Run: python -m pytest -q -p no:cacheprovider tests/test_stellar_forge_v1.py
"""
from __future__ import annotations

import copy
import dataclasses
import importlib
import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pytest

from simulation.v4_stellar_forge import big_bang_renderer, multiverse_manager, physics_engine
from simulation.v4_stellar_forge.multiverse_manager import MultiverseManager, child_id, lineage_path
from simulation.v4_stellar_forge.physics_engine import AtomAgent, ElementTypes, PhysicsEngine
from simulation.v4_stellar_forge.universe_dna import UniverseDNA

REPO = Path(__file__).resolve().parents[1]
H = ElementTypes.HYDROGEN


def test_modules_under_test_come_from_this_checkout():
    # An editable install of another worktree can shadow this checkout.
    for module in (physics_engine, multiverse_manager, big_bang_renderer):
        assert Path(module.__file__).resolve().is_relative_to(REPO), module.__file__


# --- F3: gravity ---------------------------------------------------------

def _pair():
    return [AtomAgent(-1, 0, 0, 0, H), AtomAgent(1, 0, 0, 0, H)]


def _state(agents):
    return [(a.x, a.y, a.vx, a.vy, a.mass) for a in agents]


def _momentum(agents):
    return (sum(a.mass * a.vx for a in agents), sum(a.mass * a.vy for a in agents))


def _cloud(seed, n=12):
    rng = random.Random(seed)
    return [AtomAgent(rng.gauss(0, 2), rng.gauss(0, 2), rng.gauss(0, 0.1), rng.gauss(0, 0.1), H,
                      rng.uniform(0.5, 3.0)) for _ in range(n)]


def test_two_body_step_matches_hand_oracle():
    # Hand derivation (independent of the engine): m=1, G=0.05, softening
    # s=0.1, distance 2 -> acceleration a = G*2/(4+s^2)^(3/2) towards each
    # other; semi-implicit Euler with unit step: v=±a, x=∓1±a.
    a = 0.05 * 2 / (4 + 0.1 ** 2) ** 1.5
    agents = _pair()
    PhysicsEngine(UniverseDNA(), "t", 0).gravity_step(agents)
    assert agents[0].vx == pytest.approx(a, rel=1e-15)
    assert agents[1].vx == pytest.approx(-a, rel=1e-15)
    assert agents[0].x == pytest.approx(-1 + a, rel=1e-15)
    assert agents[1].x == pytest.approx(1 - a, rel=1e-15)


def test_review_counterexample_now_conserves_momentum_in_both_orders():
    # Review F3: one step gave p = -1.5595164086283989e-4, reversed +1.5595e-4.
    normal = _pair()
    reverse = list(reversed(copy.deepcopy(normal)))
    PhysicsEngine(UniverseDNA(), "a", 0).gravity_step(normal)
    PhysicsEngine(UniverseDNA(), "b", 0).gravity_step(reverse)
    reverse.reverse()
    assert _momentum(normal) == (0.0, 0.0)
    assert _state(normal) == _state(reverse)


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_momentum_is_conserved_over_many_steps(seed):
    agents = _cloud(seed)
    p0 = np.array(_momentum(agents))
    scale = sum(a.mass * math.hypot(a.vx, a.vy) for a in agents) + 1.0
    engine = PhysicsEngine(UniverseDNA(), "m", 0)
    for _ in range(50):
        engine.gravity_step(agents)
        assert np.all(np.abs(np.array(_momentum(agents)) - p0) <= 1e-12 * scale)


@pytest.mark.parametrize("seed", [4, 5])
@pytest.mark.parametrize("steps, atol", [(1, 1e-13), (10, 1e-9)])
def test_result_does_not_depend_on_list_order(seed, steps, atol):
    # Only the summation order of the forces changes, so differences are pure
    # rounding: ~1e-15 after one step, amplified by close encounters to ~1e-12
    # after ten. The order-dependent bug produced ~1e-4 after a single step.
    base = _cloud(seed)
    reference = copy.deepcopy(base)
    engine = PhysicsEngine(UniverseDNA(), "p", 0)
    for _ in range(steps):
        engine.gravity_step(reference)
    for perm_seed in range(3):
        order = list(range(len(base)))
        random.Random(perm_seed).shuffle(order)
        permuted = [copy.deepcopy(base[i]) for i in order]
        for _ in range(steps):
            engine.gravity_step(permuted)
        restored = [None] * len(base)
        for pos, i in enumerate(order):
            restored[i] = permuted[pos]
        np.testing.assert_allclose(_state(restored), _state(reference), rtol=0, atol=atol)


# --- F2 / N2: parameter contract ----------------------------------------------

def _evolve(dna, agents_factory=_pair, steps=5):
    agents = agents_factory()
    engine = PhysicsEngine(dna, "c", 0)
    for _ in range(steps):
        engine.gravity_step(agents)
        engine.fusion_step(agents)
    return _state(agents)


def test_contract_names_every_dna_field():
    fields = {f.name for f in dataclasses.fields(UniverseDNA)}
    assert set(physics_engine.PARAMETER_CONTRACT) == fields


@pytest.mark.parametrize("factory", [_pair, lambda: _cloud(9)])
def test_contract_matches_behaviour(factory):
    base = _evolve(UniverseDNA(), factory)
    contract = physics_engine.PARAMETER_CONTRACT
    # inactive fields: large changes leave the state bit-identical
    for name, value in (("fusion_threshold", 20.0), ("entropy_rate", 0.7), ("mutation_scale", 0.4)):
        assert contract[name] in ("inactive", "mutation_only")
        assert _evolve(dataclasses.replace(UniverseDNA(), **{name: value}), factory) == base, name
    # positive controls
    assert contract["gravity_const"] == "active"
    assert _evolve(UniverseDNA(gravity_const=0.10), factory) != base
    assert contract["clumping_factor"] == "active_from_0.5"
    assert _evolve(UniverseDNA(clumping_factor=2.0), factory) != base
    # N2: below 0.5 the softening is clamped, so the factor has no effect
    assert _evolve(UniverseDNA(clumping_factor=0.1), factory) == _evolve(UniverseDNA(clumping_factor=0.4), factory)
    assert _evolve(UniverseDNA(clumping_factor=0.5), factory) != _evolve(UniverseDNA(clumping_factor=0.6), factory)


def test_mutation_scale_acts_in_mutation_only():
    a = UniverseDNA(mutation_scale=0.05).mutate(np.random.default_rng(3))
    b = UniverseDNA(mutation_scale=0.30).mutate(np.random.default_rng(3))
    assert a.gravity_const != b.gravity_const


# --- F2: seed hierarchy -----------------------------------------------------

def test_initial_state_is_repeatable_and_backward_compatible():
    s1 = _state(big_bang_renderer.initialize_bang(UniverseDNA(), random.Random(11)))
    s2 = _state(big_bang_renderer.initialize_bang(UniverseDNA(), random.Random(11)))
    s3 = _state(big_bang_renderer.initialize_bang(UniverseDNA(), random.Random(12)))
    random.seed(11)
    legacy = _state(big_bang_renderer.initialize_bang(UniverseDNA()))
    assert s1 == s2 == legacy and s1 != s3


def test_lineage_ids():
    assert lineage_path("u") == ()
    assert lineage_path(child_id(child_id("u", 0), 3)) == (0, 3)
    for bad in ("x", "u.a", "u.-1", "VOID", ""):
        with pytest.raises(ValueError):
            lineage_path(bad)


def test_seed_hierarchy_is_deterministic_and_separated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    m1, m2, m3 = MultiverseManager(root_seed=5), MultiverseManager(root_seed=5), MultiverseManager(root_seed=6)
    assert m1.initial_state_seed("u.0") == m2.initial_state_seed("u.0")
    assert m1.initial_state_seed("u.0") != m1.initial_state_seed("u.1")
    assert m1.initial_state_seed("u.0") != m3.initial_state_seed("u.0")
    assert m1.mutation_rng("u.0").random() == m2.mutation_rng("u.0").random()
    assert m1.mutation_rng("u.0").random() != m1.mutation_rng("u.1").random()
    # streams below one universe are independent
    assert m1.mutation_rng("u.0").integers(2**32) != m1.initial_state_seed("u.0")


def test_root_seed_is_drawn_and_reported_when_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    m = MultiverseManager(root_seed=None)
    assert isinstance(m.root_seed, int) and m.root_seed >= 0
    for bad in (-1, 1.5, True):
        with pytest.raises(ValueError):
            MultiverseManager(root_seed=bad)
    with pytest.raises(ValueError):
        MultiverseManager(root_seed=1, max_universes=0)


# --- signals, child ids, budget (N1) ------------------------------------------

class FakeProcess:
    """Stand-in for subprocess.Popen; never touches the OS."""

    instances: list = []

    def __init__(self, cmd, **kwargs):
        self.cmd, self.kwargs = cmd, kwargs
        self.returncode = None
        self.terminated = self.killed = False
        self.ignore_terminate = False
        FakeProcess.instances.append(self)

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        if not self.ignore_terminate:
            self.returncode = -15

    def wait(self, timeout=None):
        if self.returncode is None:
            raise subprocess.TimeoutExpired(self.cmd, timeout)
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -9


@pytest.fixture
def fake_popen(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    FakeProcess.instances = []
    monkeypatch.setattr(multiverse_manager.subprocess, "Popen", FakeProcess)
    return FakeProcess


def _emit(universe_id, count, dna=UniverseDNA()):
    engine = PhysicsEngine(dna, universe_id, 0)
    for _ in range(count):
        engine._trigger_genesis(AtomAgent(0, 0, 0, 0, ElementTypes.BLACK_HOLE, 25))


def _log():
    return json.loads(Path(multiverse_manager.LOG_FILE).read_text(encoding="utf-8"))


def test_signal_files_are_named_deterministically(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _emit("u", 2)
    names = sorted(p.name for p in Path("output/signals").iterdir())
    assert names == ["genesis_u_0000.json", "genesis_u_0001.json"]


def test_children_get_unique_ids_and_numbers(fake_popen):
    m = MultiverseManager(root_seed=1, max_universes=None)
    m.start_root_universe()
    _emit("u", 2)  # review N1: both used to be logged as child_number 1
    m._scan_for_signals()
    log = _log()
    assert [e["child_id"] for e in log] == ["u.0", "u.1"]
    assert [e["child_number"] for e in log] == [1, 2]
    assert [q["universe_id"] for q in m.genesis_queue] == ["u.0", "u.1"]
    assert not list(Path("output/signals").glob("*.json"))


def test_child_dna_and_spawn_seed_depend_only_on_root_seed(fake_popen, tmp_path, monkeypatch):
    results = []
    for run in range(2):
        d = tmp_path / f"r{run}"
        d.mkdir()
        monkeypatch.chdir(d)
        FakeProcess.instances = []
        m = MultiverseManager(root_seed=42, max_universes=None)
        m.start_root_universe()
        _emit("u", 1)
        m.update()
        child_cmd = FakeProcess.instances[-1].cmd
        assert child_cmd[child_cmd.index("--seed") + 1] == str(m.initial_state_seed("u.0"))
        assert child_cmd[child_cmd.index("--id") + 1] == "u.0"
        results.append(_log()[0]["child_dna"])
    assert results[0] == results[1]
    assert results[0] != dataclasses.asdict(UniverseDNA())


def test_unknown_or_malformed_signals_are_rejected(fake_popen):
    m = MultiverseManager(root_seed=1)
    m.start_root_universe()
    _emit("u.7", 1)  # never started
    Path("output/signals/genesis_bad.json").write_text("{", encoding="utf-8")
    m._scan_for_signals()
    assert sorted(m.rejected_signals) == ["genesis_bad.json", "genesis_u.7_0000.json"]
    assert m.genesis_queue == []
    assert len(list(Path("output/signals/rejected").iterdir())) == 2


def test_budget_bounds_total_universes(fake_popen):
    m = MultiverseManager(root_seed=1, max_universes=2)
    m.start_root_universe()
    _emit("u", 3)
    m._scan_for_signals()
    statuses = [e["status"] for e in _log()]
    assert statuses == ["queued", "not_spawned_budget", "not_spawned_budget"]
    assert m.not_spawned_budget == 2
    m.update()
    assert m.universe_counter == 2


# --- F4 / N4: shutdown and entry points ---------------------------------------

def test_terminate_all_kills_unresponsive_children(fake_popen):
    m = MultiverseManager(root_seed=1)
    m.start_root_universe()
    stubborn = FakeProcess(["x"])
    stubborn.ignore_terminate = True
    m.active_processes.append(stubborn)
    assert m.terminate_all(timeout=0.01) == 2
    assert stubborn.terminated and stubborn.killed
    assert all(p.poll() is not None for p in FakeProcess.instances)
    assert m.active_processes == []


def test_terminate_all_on_real_processes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    m = MultiverseManager(root_seed=1)
    procs = [subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"]) for _ in range(2)]
    m.active_processes.extend(procs)
    start = time.monotonic()
    assert m.terminate_all(timeout=5) == 2
    assert all(p.poll() is not None for p in procs)
    assert time.monotonic() - start < 10


def test_run_stops_at_time_limit_and_cleans_up(fake_popen):
    m = MultiverseManager(root_seed=1)
    summary = m.run(max_seconds=0.2, poll_interval=0.02)
    assert summary["stopped_by"] == "time_limit"
    assert summary["terminated_processes"] == 1
    assert all(p.poll() is not None for p in FakeProcess.instances)


def test_run_cleans_up_on_interrupt(fake_popen, monkeypatch):
    m = MultiverseManager(root_seed=1)

    def interrupt():
        raise KeyboardInterrupt

    m.start_root_universe()
    monkeypatch.setattr(m, "update", interrupt)
    summary = m.run(max_seconds=5)
    assert summary["stopped_by"] == "interrupt"
    assert summary["terminated_processes"] == 1


@pytest.mark.parametrize("module", ["run_multiverse", "run_recursive_cosmos"])
def test_entry_points_are_bounded_and_use_the_shutdown_contract(module, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    mod = importlib.import_module(f"simulation.v4_stellar_forge.{module}")
    calls = {}

    def fake_run(self, max_seconds=None, poll_interval=1.0):
        calls.update(seed=self.root_seed, max_universes=self.max_universes, max_seconds=max_seconds)
        return {"root_seed": self.root_seed, "stopped_by": "finished", "universes_started": 0}

    monkeypatch.setattr(MultiverseManager, "run", fake_run)
    mod.main(["--seed", "3"])
    assert calls == {"seed": 3, "max_universes": 16, "max_seconds": 600.0}
    assert hasattr(MultiverseManager, "terminate_all")


def test_cosmic_cycle_demo_is_retired_with_a_clear_reason():
    name = "simulation.v4_stellar_forge.cosmic_cycle_demo"
    sys.modules.pop(name, None)
    with pytest.raises(RuntimeError, match="stillgelegt") as info:
        importlib.import_module(name)
    assert "F4" in str(info.value) and type(info.value).__name__ == "RetiredDemoError"
    sys.modules.pop(name, None)
    source = (REPO / "simulation/v4_stellar_forge/cosmic_cycle_demo.py").read_text(encoding="utf-8")
    assert "def _initialize_ancient_star" in source  # original kept for the record


# --- integration: real child processes ----------------------------------------

def _real_run(directory, monkeypatch):
    monkeypatch.chdir(directory)
    m = MultiverseManager(root_seed=7, max_universes=3, frames=1, max_concurrent=2)
    summary = m.run(max_seconds=180, poll_interval=0.1)
    return summary, _log()


def test_bounded_real_run_is_repeatable(tmp_path, monkeypatch):
    runs = []
    for i in range(2):
        d = tmp_path / f"run{i}"
        d.mkdir()
        runs.append(_real_run(d, monkeypatch))
    for summary, log in runs:
        assert summary["stopped_by"] == "finished"
        assert summary["universes_started"] == 3
        assert summary["not_spawned_budget"] == 1
        assert summary["rejected_signals"] == []
        assert [(e["child_id"], e["status"]) for e in log] == [
            ("u.0", "queued"), ("u.0.0", "queued"), ("u.0.0.0", "not_spawned_budget")]
    strip = lambda log: [{k: v for k, v in e.items() if k not in ("timestamp", "child_number")} for e in log]
    assert strip(runs[0][1]) == strip(runs[1][1])
