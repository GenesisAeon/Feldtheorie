"""Week 3 — HfO2 hardware simulation scaffold.

Provides a lightweight SPICE-style netlist generator and a stochastic
switching-endurance simulation for the HfO2 RRAM stack.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from hardware.neuromorphic.hfo2_detailed_spec import HfO2ChipSpec


@dataclass(frozen=True)
class HardwareSimulationConfig:
    """Configuration for endurance and switching simulation."""

    n_cycles: int = 50_000
    endurance_cycles: int = 1_000_000
    set_voltage_v: float = 1.5
    reset_voltage_v: float = -1.2
    read_voltage_v: float = 0.2
    seed: int = 42


def generate_spice_netlist(config: HardwareSimulationConfig | None = None) -> str:
    """Return a minimal SPICE netlist for an AFET-coupled HfO2 RRAM cell."""
    cfg = config or HardwareSimulationConfig()
    return "\n".join(
        [
            ".title HfO2 RRAM AFET Coupled Cell",
            f"Vset nset 0 PULSE(0 {cfg.set_voltage_v} 0 1n 1n 10n 20n)",
            f"Vreset nreset 0 PULSE(0 {cfg.reset_voltage_v} 0 1n 1n 10n 20n)",
            f"Vread nread 0 DC {cfg.read_voltage_v}",
            "Rrram nset nread 1k",
            "Cpar nread 0 2p",
            "Rline nread nreset 50",
            ".tran 0.1n 100n",
            ".end",
        ]
    )


def simulate_switching_cycles(config: HardwareSimulationConfig | None = None) -> dict[str, float | int]:
    """Run a simplified endurance model with rising failure risk after endurance limit."""
    cfg = config or HardwareSimulationConfig()
    rng = np.random.default_rng(cfg.seed)

    failed_cycles = 0
    effective_cycles = 0
    for cycle in range(cfg.n_cycles):
        overload_ratio = max(0.0, (cycle - cfg.endurance_cycles) / max(cfg.endurance_cycles, 1))
        p_fail = min(0.95, 5e-6 + overload_ratio * 0.02)
        if rng.random() < p_fail:
            failed_cycles += 1
        else:
            effective_cycles += 1

    survival_rate = effective_cycles / max(cfg.n_cycles, 1)
    return {
        "n_cycles": cfg.n_cycles,
        "failed_cycles": failed_cycles,
        "effective_cycles": effective_cycles,
        "survival_rate": round(float(survival_rate), 6),
    }


def run_hardware_simulation(
    output_dir: Path | None = None,
    config: HardwareSimulationConfig | None = None,
) -> dict[str, object]:
    """Run simulation and optionally write a JSON report."""
    cfg = config or HardwareSimulationConfig()
    spec = HfO2ChipSpec()
    spice = generate_spice_netlist(cfg)
    summary = simulate_switching_cycles(cfg)

    payload: dict[str, object] = {
        "config": asdict(cfg),
        "hfo2_spec": {
            "thickness_nm": spec.physical.hfo2_thickness_nm,
            "dielectric_constant": spec.physical.hfo2_dielectric_constant,
            "set_voltage_v": spec.electrical.set_voltage_V,
            "reset_voltage_v": spec.electrical.reset_voltage_V,
            "resonance_hz": spec.electrical.resonance_freq_hz,
        },
        "spice": spice,
        "summary": summary,
    }

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "hardware_simulation_report.json").write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

    return payload


if __name__ == "__main__":
    run_hardware_simulation(output_dir=Path("analysis/results"))
