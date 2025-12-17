#!/usr/bin/env python3
"""Experiment E: Interference Engine – Synergetic Gap Closer

Mission: Feed AMOC + Amazon Hydro into the Solar Driver, measure whether
σ(β(R−Θ)) climbs beyond 0.5 via interaction (not just additive stress).

Core components:
- MultiStreamLoader (AMOC + Amazon proxies with interference term)
- SolarDriver (metastability kicks) operating near f≈13.5 MHz target
- PhaseEvolver (Kuramoto breathing) with stress-modulated frequencies

Outputs:
- JSON results at `experiment_e_results/experiment_e_synergy_results.json`
- Narrative stub at `releases/v9.0/EXPERIMENT_E_SYNERGY_RESULTS.md`
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import yaml

# Add parent directories to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from v9_alpha.api.lantern_bridge import load_lantern_network, LanternNetwork  # noqa: E402
from v9_alpha.demos.experiment_c_solar_engine import SolarDriver  # noqa: E402
from v9_alpha.demos.sensorium import MultiStreamLoader  # noqa: E402
from v9_alpha.models.phase_dynamics import PhaseEvolver, create_natural_frequencies  # noqa: E402


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #

@dataclass
class SimulationConfig:
    steps: int
    dt: float
    noise_level: float
    mean_frequency: float
    frequency_spread: float
    frequency_gain: float
    coherence_threshold: float
    kick_amplitude: float
    kick_strategy: str
    output_path: str


@dataclass
class MetricTargets:
    synergy_target: float
    window: int
    narrative_stub: str


@dataclass
class ExperimentEConfig:
    experiment: Dict
    streams: list
    combination: Dict
    simulation: SimulationConfig
    metrics: MetricTargets


# --------------------------------------------------------------------------- #
# Configuration loading
# --------------------------------------------------------------------------- #

def load_experiment_config(config_path: str) -> ExperimentEConfig:
    with open(config_path, "r") as f:
        data = yaml.safe_load(f) if config_path.endswith((".yaml", ".yml")) else json.load(f)

    sim = data["simulation"]
    metrics = data["metrics"]
    return ExperimentEConfig(
        experiment=data["experiment"],
        streams=data["streams"],
        combination=data["combination"],
        simulation=SimulationConfig(
            steps=int(sim.get("steps", 256)),
            dt=float(sim.get("dt", 0.05)),
            noise_level=float(sim.get("noise_level", 0.02)),
            mean_frequency=float(sim.get("mean_frequency", 0.0)),
            frequency_spread=float(sim.get("frequency_spread", 0.07)),
            frequency_gain=float(sim.get("frequency_gain", 0.45)),
            coherence_threshold=float(sim.get("coherence_threshold", 0.9)),
            kick_amplitude=float(sim.get("kick_amplitude", 0.35)),
            kick_strategy=sim.get("kick_strategy", "gentle"),
            output_path=sim.get("output_path", "experiment_e_results/experiment_e_synergy_results.json"),
        ),
        metrics=MetricTargets(
            synergy_target=float(metrics.get("synergy_target", 0.5)),
            window=int(metrics.get("window", 32)),
            narrative_stub=metrics.get("narrative_stub", "releases/v9.0/EXPERIMENT_E_SYNERGY_RESULTS.md"),
        ),
    )


# --------------------------------------------------------------------------- #
# Experiment core
# --------------------------------------------------------------------------- #

def compute_synergy_index(additive: float, combined: float) -> float:
    """Interaction lift relative to additive baseline."""
    denom = abs(additive) + 1e-6
    return (combined - additive) / denom


def run_interference(
    config: ExperimentEConfig,
) -> Tuple[Dict, Dict]:
    rng = np.random.default_rng(config.experiment.get("seed", 42))

    loader = MultiStreamLoader(
        stream_configs=config.streams,
        default_length=config.simulation.steps,
        coupling_factor=float(config.combination.get("coupling_factor", 0.35)),
        seed=config.experiment.get("seed", 42),
    )

    network: LanternNetwork = load_lantern_network()
    coupling_matrix = network.get_coupling_matrix()
    n_nodes = len(network.lanterns)

    phases = rng.uniform(-np.pi, np.pi, size=n_nodes)
    natural_freqs_base = create_natural_frequencies(
        n_oscillators=n_nodes,
        mean_frequency=config.simulation.mean_frequency,
        frequency_spread=config.simulation.frequency_spread,
    )

    evolver = PhaseEvolver(
        dt=config.simulation.dt,
        noise_level=config.simulation.noise_level,
        coupling_strength_scale=5.0,
    )
    solar_driver = SolarDriver(
        coherence_threshold=config.simulation.coherence_threshold,
        kick_amplitude=config.simulation.kick_amplitude,
        kick_strategy=config.simulation.kick_strategy,
    )

    traces = {
        "combined_stress": [],
        "phi": [],
        "global_coherence": [],
        "synergy_index": [],
    }

    for _ in range(config.simulation.steps):
        sample = loader.step()
        combined_stress = sample["combined_stress"]
        additive = sample["additive"]
        interaction = sample["interaction"]

        modulated_freqs = natural_freqs_base + combined_stress * config.simulation.frequency_gain
        phases = evolver.evolve_phases(phases, coupling_matrix, modulated_freqs)

        global_coherence, local_coherences = solar_driver.calculate_local_coherence(phases, coupling_matrix)
        if global_coherence > config.simulation.coherence_threshold:
            phases = solar_driver.inject_phase_kick(phases, local_coherences)

        phi_value = float(np.abs(np.mean(np.exp(1j * phases))))
        synergy_value = compute_synergy_index(additive=additive, combined=combined_stress)

        traces["combined_stress"].append(float(combined_stress))
        traces["phi"].append(phi_value)
        traces["global_coherence"].append(float(global_coherence))
        traces["synergy_index"].append(float(synergy_value))

    results = summarize_results(config, loader, traces)
    payload = {"traces": traces, "summary": results}
    return payload, loader.summary()


# --------------------------------------------------------------------------- #
# Summaries + persistence
# --------------------------------------------------------------------------- #

def summarize_results(config: ExperimentEConfig, loader: MultiStreamLoader, traces: Dict) -> Dict:
    synergy_series = np.array(traces["synergy_index"])
    phi_series = np.array(traces["phi"])
    coherence_series = np.array(traces["global_coherence"])

    window = min(config.metrics.window, len(synergy_series))
    tail_synergy = float(np.mean(synergy_series[-window:])) if window > 0 else 0.0

    return {
        "experiment": config.experiment,
        "loader": loader.summary(),
        "sigma_beta_delta": tail_synergy,
        "synergy_target": config.metrics.synergy_target,
        "phi_mean": float(np.mean(phi_series)),
        "phi_variance": float(np.var(phi_series)),
        "coherence_mean": float(np.mean(coherence_series)),
        "coherence_peak": float(np.max(coherence_series)),
        "interaction_mean": float(np.mean(synergy_series)),
        "steps": len(synergy_series),
        "timestamp": time.time(),
    }


def write_results(output_path: str, payload: Dict) -> str:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(payload, f, indent=2)
    return str(output_file)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Experiment E - Interference Synergy")
    parser.add_argument(
        "--config",
        type=str,
        default="v9_alpha/config/experiments/exp_e_synergy.yaml",
        help="Path to experiment configuration (YAML or JSON).",
    )
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    payload, loader_summary = run_interference(config)
    output_path = write_results(config.simulation.output_path, payload)

    print(json.dumps({
        "status": "completed",
        "output": output_path,
        "sigma_beta_delta": payload["summary"]["sigma_beta_delta"],
        "synergy_target": payload["summary"]["synergy_target"],
        "loader": loader_summary,
    }, indent=2))


if __name__ == "__main__":
    main()
