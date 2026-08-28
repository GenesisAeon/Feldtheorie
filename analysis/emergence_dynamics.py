"""Emergence Dynamics: Simulates concept stabilisation and spread using
AFET parameters (β, σ_Φ, v_RIG).

Usage::

    python -m analysis.emergence_dynamics

Outputs:
    analysis/results/emergence_dynamics.json
    analysis/plots/emergence_dynamics.png
    docs/emergence/emergence_dynamics.md
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from theory.afet import AFETConstants

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

@dataclass
class EmergenceParams:
    """Parameters controlling emergence simulation."""

    beta: float = AFETConstants.BETA_CRITICAL
    sigma_phi: float = AFETConstants.SIGMA_PHI
    damping: float = 0.1


# ---------------------------------------------------------------------------
# Stabilisation simulation
# ---------------------------------------------------------------------------

def simulate_stabilization(
    params: EmergenceParams,
    steps: int = 200,
    initial_activation: float = 0.1,
    convergence_threshold: float = 1e-4,
) -> dict[str, Any]:
    """Simulate iterative concept activation with reinforcement and damping.

    The update rule models resonance amplification damped by σ_Φ:

        a_{t+1} = a_t + gain * σ(a_t) - damping * a_t

    where ``gain = β / β_critical`` and ``σ`` is the logistic function.
    Convergence is declared when ``|a_{t} - a_{t-1}| < convergence_threshold``
    for 10 consecutive steps.

    Returns dict with ``converged``, ``final_activation``, ``steps_to_converge``,
    and ``history``.
    """
    beta_c = AFETConstants.BETA_CRITICAL
    gain = params.beta / beta_c
    d = params.damping

    a = initial_activation
    history: list[float] = []
    stable_count = 0
    steps_to_converge: int | None = None

    for step in range(steps):
        # Logistic activation
        sig = 1.0 / (1.0 + math.exp(-a))
        a_new = a + gain * sig * params.sigma_phi - d * a
        history.append(a_new)

        if abs(a_new - a) < convergence_threshold:
            stable_count += 1
            if stable_count >= 10 and steps_to_converge is None:
                steps_to_converge = step + 1
        else:
            stable_count = 0

        a = a_new

        # Safety cap: detect runaway
        if abs(a) > 1e6:
            return {
                "converged": False,
                "final_activation": float(a),
                "steps_to_converge": None,
                "history": history,
            }

    converged = steps_to_converge is not None
    return {
        "converged": converged,
        "final_activation": float(a),
        "steps_to_converge": steps_to_converge,
        "history": history,
    }


# ---------------------------------------------------------------------------
# Concept spread simulation
# ---------------------------------------------------------------------------

# The 0.05 growth-rate normalizer below was tuned by hand against v_RIG's
# old (incorrect) magnitude of 1.352; the corrected physical value
# (AFETConstants.V_RIG ~= 1352 km/s, see theory/afet.py) would make `rate`
# ~1000x larger and saturate this logistic model in a single step. This
# local default preserves the model's existing tested dynamics -- it is a
# deliberate simulation-tuning constant, not the corrected physical v_RIG.
_LEGACY_V_RIG_SCALE = 1.352


def simulate_concept_spread(
    beta: float = AFETConstants.BETA_CRITICAL,
    v_rig: float = _LEGACY_V_RIG_SCALE,
    steps: int = 100,
    population: int = 100,
) -> dict[str, Any]:
    """Simulate how a concept spreads through a population of interacting agents.

    Uses a logistic-growth model where the growth rate is proportional to
    ``β / β_critical`` and the propagation velocity scales with ``v_RIG``.

    Returns dict with ``spread_history`` (fraction of population reached per step),
    ``peak_spread``, and ``half_life`` (step at which 50% is reached, or None).
    """
    beta_c = AFETConstants.BETA_CRITICAL
    rate = (beta / beta_c) * v_rig * 0.05  # normalised growth rate

    spread: list[float] = []
    n = 1.0 / population  # initial fraction (one agent)

    half_life: int | None = None
    for step in range(steps):
        # Logistic growth: dn/dt = rate * n * (1 - n)
        dn = rate * n * (1.0 - n)
        n = min(max(n + dn, 0.0), 1.0)
        spread.append(n)
        if half_life is None and n >= 0.5:
            half_life = step

    return {
        "spread_history": spread,
        "peak_spread": max(spread),
        "half_life": half_life,
    }


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def export_json(results: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


def export_plot(
    stab_results: dict[str, dict[str, Any]],
    spread_results: dict[str, dict[str, Any]],
    output_path: Path,
) -> None:
    """Plot stabilisation curves and spread dynamics side-by-side."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Stabilisation curves
    for label, res in stab_results.items():
        ax1.plot(res["history"], label=label, linewidth=1.5)
    ax1.set_title("Concept Stabilisation (activation over time)")
    ax1.set_xlabel("Step")
    ax1.set_ylabel("Activation")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Spread curves
    for label, res in spread_results.items():
        ax2.plot(res["spread_history"], label=label, linewidth=1.5)
    ax2.set_title("Concept Spread (fraction of population)")
    ax2.set_xlabel("Step")
    ax2.set_ylabel("Spread fraction")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def generate_report(
    stab_results: dict[str, dict[str, Any]],
    spread_results: dict[str, dict[str, Any]],
    output_path: Path,
) -> None:
    """Generate Markdown report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Emergence Dynamics Report",
        "",
        "## Stabilisation Analysis",
        "",
        "| Scenario | Converged | Final Activation | Steps to Converge |",
        "|----------|-----------|------------------|-------------------|",
    ]
    for label, res in stab_results.items():
        conv = "Yes" if res["converged"] else "No"
        fa = f"{res['final_activation']:.4f}"
        stc = str(res["steps_to_converge"]) if res["steps_to_converge"] else "N/A"
        lines.append(f"| {label} | {conv} | {fa} | {stc} |")

    lines += [
        "",
        "## Spread Analysis",
        "",
        "| Scenario | Peak Spread | Half-Life (steps) |",
        "|----------|-------------|-------------------|",
    ]
    for label, res in spread_results.items():
        ps = f"{res['peak_spread']:.4f}"
        hl = str(res["half_life"]) if res["half_life"] is not None else "N/A"
        lines.append(f"| {label} | {ps} | {hl} |")

    lines += [
        "",
        "## Key Findings",
        "",
        "- Concepts stabilise when `β < β_critical` or when sufficient damping"
        " (via σ_Φ buffer) is applied.",
        "- Above `β_critical` without damping, activation diverges (runaway recursion).",
        "- Spread velocity scales with `v_RIG`; higher β accelerates adoption.",
        "- The σ_Φ = 0.0625 boundary acts as a natural limiter on resonance amplification.",
        "",
        "See `analysis/results/emergence_dynamics.json` for raw data and"
        " `analysis/plots/emergence_dynamics.png` for visualisations.",
    ]

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(root: Path | None = None) -> None:
    """Run emergence dynamics scenarios and export results."""
    root = root or Path(__file__).resolve().parent.parent

    # Stabilisation scenarios
    stab_scenarios = {
        "sub-critical (β=20, d=0.1)": EmergenceParams(beta=20.0, damping=0.1),
        "critical (β=37.6, d=0.1)": EmergenceParams(beta=37.6, damping=0.1),
        "super-critical (β=50, d=0)": EmergenceParams(beta=50.0, damping=0.0),
        "super-critical damped (β=50, d=0.3)": EmergenceParams(beta=50.0, damping=0.3),
    }
    stab_results = {
        label: simulate_stabilization(params) for label, params in stab_scenarios.items()
    }

    # Spread scenarios
    spread_scenarios = {
        "low β (10)": {"beta": 10.0},
        "critical β (37.6)": {"beta": 37.6},
        "high β (60)": {"beta": 60.0},
    }
    spread_results = {
        label: simulate_concept_spread(**kw) for label, kw in spread_scenarios.items()
    }

    # Combine for JSON export
    all_results = {
        "stabilization": {
            k: {key: val for key, val in v.items() if key != "history"}
            for k, v in stab_results.items()
        },
        "spread": {
            k: {key: val for key, val in v.items() if key != "spread_history"}
            for k, v in spread_results.items()
        },
    }

    export_json(all_results, root / "analysis" / "results" / "emergence_dynamics.json")
    export_plot(stab_results, spread_results, root / "analysis" / "plots" / "emergence_dynamics.png")
    generate_report(stab_results, spread_results, root / "docs" / "emergence" / "emergence_dynamics.md")

    print("Emergence dynamics analysis complete.")


if __name__ == "__main__":
    main()
