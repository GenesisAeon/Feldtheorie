#!/usr/bin/env python3
"""Experiment F – The Pre-Cognition Engine (Critical Slowing Down Oracle)

Mission: Teach the Living Crystal (v9.0) to predict collapse by watching the
change rate of its own stability, not just the raw stress signal. We inject a
synthetic fold-bifurcation "doom stream" into the SolarDriver and watch Φ and
R for Critical Slowing Down (CSD): lag-1 autocorrelation → 1 before impact.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from v9_alpha.api.lantern_bridge import load_lantern_network  # noqa: E402
from v9_alpha.models.early_warning import EarlyWarningSystem  # noqa: E402
from v9_alpha.models.phase_dynamics import PhaseEvolver, create_natural_frequencies  # noqa: E402
from v9_alpha.models.sensorium import BifurcationGenerator  # noqa: E402
from v9_alpha.models.solar_driver import SolarDriver  # noqa: E402


@dataclass
class ExperimentFConfig:
    steps: int = 600
    dt: float = 0.05
    mu_start: float = 0.6
    mu_end: float = -0.6
    noise_std: float = 0.03
    crash_threshold: float = -0.9
    phi_window: int = 50
    alert_threshold: float = 0.8
    frequency_gain: float = 0.9
    base_frequency: float = 0.05
    coherence_threshold: float = 0.9
    kick_amplitude: float = 0.35
    output_path: str = "experiment_f_results/experiment_f_oracle_results.json"
    seed: int = 11


def build_oracle_components(config: ExperimentFConfig):
    """Initialize drivers, evolvers, and the synthetic doom stream."""
    bifurcation = BifurcationGenerator(
        length=config.steps,
        mu_start=config.mu_start,
        mu_end=config.mu_end,
        noise_std=config.noise_std,
        dt=config.dt,
        crash_threshold=config.crash_threshold,
        seed=config.seed,
    )
    doom = bifurcation.generate()
    doom_stream = bifurcation.to_stream()
    normalized_doom = doom_stream.get_full()

    network = load_lantern_network()
    coupling_matrix = network.get_coupling_matrix()
    n_nodes = len(network.lanterns)

    rng = np.random.default_rng(config.seed)
    phases = rng.uniform(-np.pi, np.pi, size=n_nodes)
    natural_freqs = create_natural_frequencies(
        n_oscillators=n_nodes,
        mean_frequency=config.base_frequency,
        frequency_spread=0.05,
    )

    evolver = PhaseEvolver(dt=config.dt, noise_level=config.noise_std, coupling_strength_scale=5.0)
    solar_driver = SolarDriver(
        coherence_threshold=config.coherence_threshold,
        kick_amplitude=config.kick_amplitude,
        kick_strategy="gentle",
    )
    oracle = EarlyWarningSystem(window=config.phi_window, alert_threshold=config.alert_threshold)

    return doom, normalized_doom, bifurcation, phases, natural_freqs, coupling_matrix, evolver, solar_driver, oracle


def run_oracle(config: ExperimentFConfig) -> Tuple[Dict, Dict]:
    doom, doom_stream, bifurcation, phases, natural_freqs, coupling_matrix, evolver, solar_driver, oracle = build_oracle_components(config)

    traces = {
        "phi": [],
        "coherence": [],
        "lag1_autocorr_phi": [],
        "variance_phi": [],
        "doom_signal": [],
        "mu": [],
        "alerts": [],
    }

    for step in range(config.steps):
        doom_value = float(doom_stream[step])
        mu_value = float(doom["mu"][step])
        modulated_freqs = natural_freqs + (doom_value - 0.5) * config.frequency_gain

        phases = evolver.evolve_phases(phases, coupling_matrix, modulated_freqs)
        global_coherence, local_coherences = solar_driver.calculate_local_coherence(phases, coupling_matrix)
        if global_coherence > solar_driver.coherence_threshold:
            phases = solar_driver.inject_phase_kick(phases, local_coherences)

        phi_value = float(np.abs(np.mean(np.exp(1j * phases))))
        metrics = oracle.update(phi=phi_value, coherence=global_coherence)

        traces["phi"].append(phi_value)
        traces["coherence"].append(float(global_coherence))
        traces["lag1_autocorr_phi"].append(metrics["lag1_autocorr_phi"])
        traces["variance_phi"].append(metrics["variance_phi"])
        traces["doom_signal"].append(doom_value)
        traces["mu"].append(mu_value)
        traces["alerts"].append(oracle.alert_step == step)

    crash_step = int(doom["crash_index"])
    alert_step = oracle.alert_step
    time_to_impact = None if alert_step is None else crash_step - alert_step
    lead_time_positive = time_to_impact is not None and time_to_impact > 0

    summary = {
        "experiment": "Phase VI - Experiment F (Pre-Cognition Engine)",
        "csd_hypothesis": "lag-1 autocorrelation of Φ spikes before collapse",
        "config": asdict(config),
        "bifurcation": {**bifurcation.summary(), "crash_step": crash_step},
        "oracle": {
            "alert_step": alert_step,
            "alert_threshold": config.alert_threshold,
            "window": config.phi_window,
            "time_to_impact": time_to_impact,
            "lead_time_positive": lead_time_positive,
        },
        "metrics": {
            "final_phi": traces["phi"][-1] if traces["phi"] else 0.0,
            "final_coherence": traces["coherence"][-1] if traces["coherence"] else 0.0,
            "final_lag1_autocorr_phi": traces["lag1_autocorr_phi"][-1] if traces["lag1_autocorr_phi"] else 0.0,
            "final_variance_phi": traces["variance_phi"][-1] if traces["variance_phi"] else 0.0,
        },
        "hypothesis_result": {
            "alert_before_crash": lead_time_positive,
            "t_prediction": time_to_impact,
        },
    }
    return summary, traces


def save_results(summary: Dict, traces: Dict, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"summary": summary, "traces": traces}
    path.write_text(json.dumps(payload, indent=2))


def parse_args() -> ExperimentFConfig:
    parser = argparse.ArgumentParser(description="Experiment F – Pre-Cognition Engine (Critical Slowing Down Oracle)")
    parser.add_argument("--steps", type=int, default=600, help="Number of simulation steps / doom samples")
    parser.add_argument("--output", type=str, default="experiment_f_results/experiment_f_oracle_results.json", help="Where to store the JSON payload")
    parser.add_argument("--alert-threshold", type=float, default=0.8, help="Lag-1 autocorrelation threshold for alerts")
    parser.add_argument("--phi-window", type=int, default=50, help="Rolling window used for Φ autocorrelation")
    parser.add_argument("--seed", type=int, default=11, help="Random seed for reproducibility")
    args = parser.parse_args()
    return ExperimentFConfig(
        steps=args.steps,
        output_path=args.output,
        alert_threshold=args.alert_threshold,
        phi_window=args.phi_window,
        seed=args.seed,
    )


def main() -> None:
    args = parse_args()
    summary, traces = run_oracle(args)
    save_results(summary, traces, args.output_path)
    T_pred = summary["hypothesis_result"]["t_prediction"]
    print("🔮 Phase VI – Experiment F complete.")
    print(f"   Alert step: {summary['oracle']['alert_step']}")
    print(f"   Crash step: {summary['bifurcation']['crash_step']}")
    print(f"   T_prediction (lead time): {T_pred}")
    if summary["hypothesis_result"]["alert_before_crash"]:
        print("✅ Critical slowing detected before impact (Φ autocorr > threshold).")
    else:
        print("⚠️  No lead time detected — adjust thresholds or noise and retry.")


if __name__ == "__main__":
    main()
