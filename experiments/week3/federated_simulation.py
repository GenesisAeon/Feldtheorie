"""Week 3 — Federated learning simulation with heterogeneous β_c.

Simulates a 5-client federation where each client has a domain-specific
β_c value.  Implements a weighted-median consensus algorithm for
aggregating β_c across rounds, with drift tracking and outlier detection.

Client profiles:
  - Medical images:  β_c ≈ 42 (high precision)
  - Social media:    β_c ≈ 28 (noisy)
  - Scientific data: β_c ≈ 38 (structured)
  - IoT sensors:     β_c ≈ 25 (sparse)
  - Financial:       β_c ≈ 35 (temporal)

Usage:
    python -m experiments.week3.federated_simulation
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from theory.afet import AFETConstants, AFETFramework

# ---------------------------------------------------------------------------
# Client profiles
# ---------------------------------------------------------------------------

CLIENT_PROFILES = [
    {"name": "medical", "beta_c": 42.0, "noise_std": 0.8, "weight": 1.2},
    {"name": "social_media", "beta_c": 28.0, "noise_std": 2.5, "weight": 0.8},
    {"name": "scientific", "beta_c": 38.0, "noise_std": 1.0, "weight": 1.0},
    {"name": "iot_sensors", "beta_c": 25.0, "noise_std": 3.0, "weight": 0.7},
    {"name": "financial", "beta_c": 35.0, "noise_std": 1.5, "weight": 1.0},
]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ClientState:
    """Snapshot of a client's state at a given round."""

    name: str
    round_num: int
    beta_c_local: float
    is_outlier: bool


@dataclass(frozen=True)
class FederatedRound:
    """Result of a single federated aggregation round."""

    round_num: int
    beta_consensus: float
    client_states: list[ClientState]
    outlier_count: int
    sigma_phi_system: float


@dataclass(frozen=True)
class FederatedReport:
    """Summary of the full federated simulation."""

    n_clients: int
    n_rounds: int
    final_consensus_beta: float
    convergence_round: int
    total_outliers_detected: int
    sigma_phi_mean: float
    sigma_phi_std: float
    per_client_drift: dict[str, float]


# ---------------------------------------------------------------------------
# Consensus algorithm
# ---------------------------------------------------------------------------


def weighted_median(values: list[float], weights: list[float]) -> float:
    """Compute weighted median of values."""
    sorted_pairs = sorted(zip(values, weights))
    cumulative = 0.0
    total_weight = sum(weights)
    for val, w in sorted_pairs:
        cumulative += w
        if cumulative >= total_weight / 2.0:
            return val
    return sorted_pairs[-1][0]


def detect_outliers(
    betas: list[float],
    consensus: float,
    threshold_sigma: float = 2.0,
) -> list[bool]:
    """Detect outlier clients: |β_i - β_consensus| > threshold * σ."""
    arr = np.array(betas)
    sigma = float(np.std(arr))
    if sigma < 1e-12:
        return [False] * len(betas)
    return [abs(b - consensus) > threshold_sigma * sigma for b in betas]


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------


def simulate_federation(
    *,
    n_rounds: int = 10,
    seed: int = 42,
    convergence_threshold: float = 0.5,
) -> tuple[list[FederatedRound], FederatedReport]:
    """Run the federated β_c consensus simulation."""
    rng = np.random.default_rng(seed)
    afet = AFETFramework()

    rounds: list[FederatedRound] = []
    # Track per-client beta history
    client_histories: dict[str, list[float]] = {p["name"]: [] for p in CLIENT_PROFILES}

    convergence_round = n_rounds  # default: never converged
    total_outliers = 0
    sigma_phis: list[float] = []

    for r in range(n_rounds):
        # Each client computes local β_c with noise
        local_betas: list[float] = []
        weights: list[float] = []
        client_states: list[ClientState] = []

        for profile in CLIENT_PROFILES:
            noise = rng.normal(0.0, profile["noise_std"])
            local_beta = profile["beta_c"] + noise
            local_betas.append(local_beta)
            weights.append(profile["weight"])
            client_histories[profile["name"]].append(local_beta)

        # Weighted median consensus
        consensus = weighted_median(local_betas, weights)

        # Outlier detection
        outlier_flags = detect_outliers(local_betas, consensus)
        outlier_count = sum(outlier_flags)
        total_outliers += outlier_count

        for i, profile in enumerate(CLIENT_PROFILES):
            client_states.append(
                ClientState(
                    name=profile["name"],
                    round_num=r,
                    beta_c_local=round(local_betas[i], 4),
                    is_outlier=outlier_flags[i],
                )
            )

        # System-level σ_Φ: CV of local betas (stability measure)
        beta_arr = np.array(local_betas)
        sigma_phi_sys = float(np.std(beta_arr) / max(abs(float(np.mean(beta_arr))), 1e-12))
        sigma_phis.append(sigma_phi_sys)

        # Check convergence
        if r > 0 and convergence_round == n_rounds:
            prev_consensus = rounds[-1].beta_consensus
            if abs(consensus - prev_consensus) < convergence_threshold:
                convergence_round = r

        rounds.append(
            FederatedRound(
                round_num=r,
                beta_consensus=round(consensus, 4),
                client_states=client_states,
                outlier_count=outlier_count,
                sigma_phi_system=round(sigma_phi_sys, 6),
            )
        )

    # Per-client drift: range of beta values over rounds
    per_client_drift = {}
    for name, history in client_histories.items():
        arr = np.array(history)
        per_client_drift[name] = round(float(np.max(arr) - np.min(arr)), 4)

    sigma_arr = np.array(sigma_phis)
    report = FederatedReport(
        n_clients=len(CLIENT_PROFILES),
        n_rounds=n_rounds,
        final_consensus_beta=rounds[-1].beta_consensus,
        convergence_round=convergence_round,
        total_outliers_detected=total_outliers,
        sigma_phi_mean=round(float(np.mean(sigma_arr)), 6),
        sigma_phi_std=round(float(np.std(sigma_arr)), 6),
        per_client_drift=per_client_drift,
    )

    return rounds, report


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_federated_experiment(
    output_dir: Path | None = None,
    *,
    n_rounds: int = 10,
) -> dict:
    """Full experiment: simulate, persist, report."""
    print("=" * 60)
    print("Week 3 — Federated β_c Consensus Simulation")
    print("=" * 60)

    t0 = time.time()
    rounds, report = simulate_federation(n_rounds=n_rounds)
    elapsed = time.time() - t0

    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"  Clients: {report.n_clients}")
    print(f"  Rounds: {report.n_rounds}")
    print(f"  Final consensus β_c: {report.final_consensus_beta:.4f}")
    print(f"  Convergence at round: {report.convergence_round}")
    print(f"  Total outliers: {report.total_outliers_detected}")

    payload = {
        "report": asdict(report),
        "elapsed_seconds": round(elapsed, 2),
        "rounds": [
            {
                "round_num": r.round_num,
                "beta_consensus": r.beta_consensus,
                "outlier_count": r.outlier_count,
                "sigma_phi_system": r.sigma_phi_system,
            }
            for r in rounds
        ],
    }

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / "federated.json"
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Results -> {json_path}")

    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Week 3 federated simulation")
    parser.add_argument("--rounds", type=int, default=10, help="number of rounds")
    args = parser.parse_args()
    run_federated_experiment(
        output_dir=Path("experiments/week3/results"),
        n_rounds=args.rounds,
    )
