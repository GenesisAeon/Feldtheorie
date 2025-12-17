#!/usr/bin/env python3
"""Living Crystal main entry point for v9.0.

The CLI bundles the metastability stack (SolarDriver + StochasticResonator +
TopologicalReaper) with the Sensorium interference loader so that Zenodo users
can reproduce Experiments C–E in one run. Outputs are serialized as
Trilayer (YAML+JSON) when an output prefix is provided.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from v9_alpha.api.lantern_bridge import load_lantern_network
from v9_alpha.models.emergence_metrics import EmergenceTracker
from v9_alpha.models.frequency_tuner import (
    create_stochastic_resonator,
    create_topological_reaper,
)
from v9_alpha.models.phase_dynamics import PhaseEvolver, create_natural_frequencies
from v9_alpha.models.sensorium import MultiStreamLoader, load_stream_configs
from v9_alpha.models.solar_driver import SolarDriver, phase_coherence
from v9_alpha.demos.experiment_f_oracle import ExperimentFConfig, run_oracle


def default_streams() -> list[Dict[str, Any]]:
    """Synthetic stressors approximating the Climate–Economy coupling."""
    return [
        {
            "name": "amoc_proxy",
            "synthetic_base": "seasonal",
            "trend_strength": 0.18,
            "seasonal_freq": 0.035,
            "noise_level": 0.06,
        },
        {
            "name": "amazon_evap",
            "synthetic_base": "pulse",
            "trend_strength": 0.22,
            "seasonal_freq": 0.08,
            "noise_level": 0.05,
            "invert": True,
        },
        {
            "name": "market_flux",
            "synthetic_base": "seasonal",
            "trend_strength": 0.12,
            "seasonal_freq": 0.06,
            "noise_level": 0.09,
        },
    ]


def build_sensorium(path: Optional[str], steps: int, coupling: float, seed: int) -> MultiStreamLoader:
    if path:
        configs = load_stream_configs(Path(path))
    else:
        configs = default_streams()
    return MultiStreamLoader(
        stream_configs=configs,
        default_length=steps,
        coupling_factor=coupling,
        seed=seed,
    )


def record(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".json":
        path.write_text(json.dumps(payload, indent=2))
    else:
        path.write_text(yaml.safe_dump(payload, sort_keys=False))


def run_simulation(args: argparse.Namespace) -> Dict[str, Any]:
    network = load_lantern_network(args.config)
    coupling_matrix = network.get_coupling_matrix()

    lanterns = list(network.lanterns.values())
    beta_values = np.array([lantern.beta for lantern in lanterns])
    impedance_values = np.array([lantern.em_properties.impedance_z for lantern in lanterns])
    baseline_impedance = float(np.mean(impedance_values))

    phase_evolver = PhaseEvolver(
        dt=args.dt,
        noise_level=args.noise_level,
        coupling_strength_scale=args.coupling_scale,
    )
    phases = np.random.uniform(-np.pi, np.pi, size=len(lanterns))
    natural_frequencies = create_natural_frequencies(
        len(lanterns),
        mean_frequency=args.mean_frequency,
        frequency_spread=args.frequency_spread,
    )

    tracker = EmergenceTracker()
    snapshots = []

    solar_driver = SolarDriver(
        coherence_threshold=args.coherence_threshold,
        kick_amplitude=args.kick_amplitude,
        kick_strategy=args.kick_strategy,
    ) if args.enable_solar_driver else None

    resonator = create_stochastic_resonator(
        sigma=args.resonator_sigma,
        beta=args.resonator_beta,
        phi_threshold=args.resonator_phi_threshold,
        noise_color=args.resonator_noise_color,
    ) if args.enable_resonator else None

    reaper = create_topological_reaper(
        pruning_threshold=args.pruning_threshold,
        redundancy_threshold=args.redundancy_threshold,
        growth_resonance_threshold=args.growth_resonance_threshold,
        strategy=args.reaper_strategy,
    ) if args.enable_reaper else None

    sensorium = build_sensorium(
        path=args.sensor_config,
        steps=args.steps,
        coupling=args.sensor_coupling,
        seed=args.seed,
    ) if args.enable_sensorium else None

    z_eff = baseline_impedance
    previous_coupling = None
    sensor_trace = []
    solar_trace = []
    resonator_trace = []
    reaper_trace = []

    for step_idx in range(args.steps):
        phases = phase_evolver.evolve_phases(phases, coupling_matrix, natural_frequencies)

        if sensorium:
            stress_state = sensorium.step()
            stress_push = args.sensor_gain * stress_state["combined_stress"]
            phases = np.arctan2(np.sin(phases + stress_push), np.cos(phases + stress_push))
            natural_frequencies = natural_frequencies + args.frequency_gain * stress_push
            sensor_trace.append({"step": step_idx, **stress_state})

        if solar_driver:
            phases, solar_info = solar_driver.step(phases, coupling_matrix)
            solar_trace.append({"step": step_idx, **solar_info})

        coherence = phase_coherence(phases)
        phi_value = tracker.calculate_phi_network(coupling_matrix)

        if resonator:
            z_eff, res_info = resonator.step(z_eff, phi_value, coherence, z_target=baseline_impedance)
            coupling_matrix = coupling_matrix * (z_eff / baseline_impedance)
            res_info.update({"step": step_idx, "z_eff": z_eff})
            resonator_trace.append(res_info)

        if reaper and step_idx > 0 and step_idx % args.reaper_interval == 0:
            coupling_matrix, reaper_info = reaper.full_cycle(
                coupling_matrix=coupling_matrix,
                beta_values=beta_values,
                phases=phases,
                frequencies=natural_frequencies,
            )
            reaper_info["step"] = step_idx
            reaper_trace.append(reaper_info)

        snapshot = tracker.create_snapshot(
            coupling_matrix=coupling_matrix,
            beta_values=beta_values,
            impedance_values=impedance_values,
            n_active_lanterns=len(network.get_active_lanterns()),
            n_emergent_hypotheses=tracker.count_hypotheses(),
            previous_coupling_matrix=previous_coupling,
            dt=args.dt,
        )
        snapshots.append(snapshot)
        previous_coupling = coupling_matrix.copy()

    summary = {
        "R": "Living Crystal v9.0",
        "Theta": args.coherence_threshold,
        "beta": float(np.mean(beta_values)),
        "zeta_R": float(np.std(impedance_values)),
        "sigma_beta": coherence,
        "final_phi": snapshots[-1].phi_network if snapshots else 0.0,
        "final_coherence": coherence,
        "steps": args.steps,
        "n_active": len(network.get_active_lanterns()),
        "sensorium_streams": sensorium.summary() if sensorium else None,
        "solar_kicks": solar_driver.get_statistics() if solar_driver else None,
        "resonator_state": resonator_trace[-1] if resonator_trace else None,
        "reaper_actions": reaper_trace[-1] if reaper_trace else None,
    }

    payload = {
        "summary": summary,
        "snapshots": [asdict(s) for s in snapshots],
        "sensor_trace": sensor_trace,
        "solar_trace": solar_trace,
        "resonator_trace": resonator_trace,
        "reaper_trace": reaper_trace,
    }

    if args.output_prefix:
        prefix = Path(args.output_prefix)
        record(prefix.with_suffix(".json"), payload)
        record(prefix.with_suffix(".yaml"), payload)

    return payload


def run_oracle_experiment(args: argparse.Namespace) -> Dict[str, Any]:
    output_prefix = Path(args.output_prefix) if args.output_prefix else Path("experiment_f_results")
    config = ExperimentFConfig(
        steps=args.oracle_steps,
        dt=args.dt,
        mu_start=args.oracle_mu_start,
        mu_end=args.oracle_mu_end,
        noise_std=args.oracle_noise_level,
        crash_threshold=args.oracle_crash_threshold,
        phi_window=args.oracle_phi_window,
        alert_threshold=args.oracle_alert_threshold,
        frequency_gain=args.oracle_frequency_gain,
        base_frequency=args.oracle_base_frequency,
        coherence_threshold=args.coherence_threshold,
        kick_amplitude=args.kick_amplitude,
        output_path=str(output_prefix.with_suffix(".json")),
        seed=args.seed,
    )

    summary, traces = run_oracle(config)
    payload = {"summary": summary, "traces": traces}

    if args.output_prefix:
        record(output_prefix.with_suffix(".json"), payload)
        record(output_prefix.with_suffix(".yaml"), payload)

    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the v9.0 Living Crystal end-to-end simulation")
    parser.add_argument(
        "--experiment",
        default="living-crystal",
        choices=["living-crystal", "oracle"],
        help="Choose core run: Living Crystal loop or the Pre-Cognition Oracle",
    )
    parser.add_argument("--config", default="v9_alpha/config/lantern_hub.yaml", help="Lantern hub configuration path")
    parser.add_argument("--steps", type=int, default=128, help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=0.05, help="Timestep for PhaseEvolver")
    parser.add_argument("--noise-level", type=float, default=0.02, help="Noise level for PhaseEvolver")
    parser.add_argument("--coupling-scale", type=float, default=5.0, help="Coupling scale for PhaseEvolver")
    parser.add_argument("--mean-frequency", type=float, default=0.0, help="Mean natural frequency")
    parser.add_argument("--frequency-spread", type=float, default=0.1, help="Std dev for natural frequencies")

    parser.add_argument("--enable-solar-driver", action="store_true", help="Activate SolarDriver metastability kicks")
    parser.add_argument("--coherence-threshold", type=float, default=0.93, help="Coherence threshold for SolarDriver kicks")
    parser.add_argument("--kick-amplitude", type=float, default=0.45, help="Phase kick amplitude")
    parser.add_argument("--kick-strategy", type=str, default="aggressive", choices=["aggressive", "gentle"], help="SolarDriver kick style")

    parser.add_argument("--enable-resonator", action="store_true", help="Enable StochasticResonator feedback")
    parser.add_argument("--resonator-sigma", type=float, default=0.15, help="Base sigma for resonator")
    parser.add_argument("--resonator-beta", type=float, default=4.2, help="β steepness for resonator drift")
    parser.add_argument("--resonator-phi-threshold", type=float, default=0.72, help="Φ threshold for resonator criticality")
    parser.add_argument("--resonator-noise-color", type=str, default="pink", choices=["white", "pink", "brown"], help="Noise color for resonator")

    parser.add_argument("--enable-reaper", action="store_true", help="Enable TopologicalReaper cycles")
    parser.add_argument("--pruning-threshold", type=float, default=0.1, help="Weak edge pruning threshold")
    parser.add_argument("--redundancy-threshold", type=float, default=0.95, help="Redundancy β threshold")
    parser.add_argument("--growth-resonance-threshold", type=float, default=0.8, help="Resonance threshold for new edges")
    parser.add_argument("--reaper-strategy", type=str, default="uniform", choices=["uniform", "hub_attack"], help="Reaper pruning strategy")
    parser.add_argument("--reaper-interval", type=int, default=16, help="Steps between reaper cycles")

    parser.add_argument("--enable-sensorium", action="store_true", help="Enable MultiStreamLoader interference")
    parser.add_argument("--sensor-config", type=str, help="Path to YAML/JSON sensor stream config")
    parser.add_argument("--sensor-coupling", type=float, default=0.3, help="Interference coupling factor")
    parser.add_argument("--sensor-gain", type=float, default=0.12, help="Phase push from combined stress")
    parser.add_argument("--frequency-gain", type=float, default=0.04, help="Frequency drift from stress")

    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output-prefix", type=str, help="If set, write JSON+YAML results to this path prefix")

    parser.add_argument("--oracle-steps", type=int, default=200, help="Steps for Pre-Cognition Engine run")
    parser.add_argument("--oracle-mu-start", type=float, default=0.6, help="Initial μ for bifurcation drift")
    parser.add_argument("--oracle-mu-end", type=float, default=-0.6, help="Terminal μ triggering collapse")
    parser.add_argument("--oracle-noise-level", type=float, default=0.03, help="Noise level on the doom stream")
    parser.add_argument("--oracle-crash-threshold", type=float, default=-0.9, help="Crash detection threshold for doom state")
    parser.add_argument("--oracle-phi-window", type=int, default=50, help="Rolling Φ window for autocorrelation")
    parser.add_argument("--oracle-alert-threshold", type=float, default=0.8, help="Alert threshold on lag-1 autocorrelation")
    parser.add_argument("--oracle-frequency-gain", type=float, default=0.9, help="Frequency modulation strength from doom signal")
    parser.add_argument("--oracle-base-frequency", type=float, default=0.05, help="Base natural frequency during oracle run")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if len(sys.argv) == 1:
        args.enable_solar_driver = True
        args.enable_resonator = True
        args.enable_reaper = True
        args.enable_sensorium = True
        args.steps = 50

    np.random.seed(args.seed)

    if args.experiment == "oracle":
        payload = run_oracle_experiment(args)
        print(json.dumps({"R": payload["summary"], "Theta": "oracle"}, indent=2))
    else:
        results = run_simulation(args)
        print(json.dumps({"R": results["summary"], "Theta": "cli"}, indent=2))
