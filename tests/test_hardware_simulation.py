"""Tests for experiments.week3.hardware_simulation."""

from __future__ import annotations

from pathlib import Path

from experiments.week3.hardware_simulation import (
    HardwareSimulationConfig,
    generate_spice_netlist,
    run_hardware_simulation,
    simulate_switching_cycles,
)


def test_spice_netlist_contains_core_components() -> None:
    netlist = generate_spice_netlist()
    assert ".title HfO2 RRAM AFET Coupled Cell" in netlist
    assert "Rrram" in netlist
    assert ".tran" in netlist


def test_switching_cycles_respect_endurance_limit() -> None:
    cfg = HardwareSimulationConfig(n_cycles=20_000, endurance_cycles=10_000, seed=11)
    payload = simulate_switching_cycles(cfg)
    assert payload["n_cycles"] == 20_000
    assert payload["failed_cycles"] > 0
    assert payload["survival_rate"] < 1.0


def test_run_hardware_simulation_writes_report(tmp_path: Path) -> None:
    payload = run_hardware_simulation(output_dir=tmp_path)
    assert "summary" in payload
    assert "spice" in payload
    assert (tmp_path / "hardware_simulation_report.json").exists()
