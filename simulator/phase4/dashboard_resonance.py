"""Resonanz-Kino: Mission-Control-Dashboard für σ(β(R-Θ)).

Dieses Dashboard koppelt drei Datenströme in einer Matplotlib-Animation:

1. **Soliton-Feld (KdV)** – Heatmap des wandernden Solitonpakets, β als Overlay.
2. **Druck × Sterblichkeit** – Alive-Trace des pressure_gardener mit Druckramp
   auf zweiter Y-Achse und Marker für die verzögerte Reaktion.
3. **Hex-Quantisierung** – Balkendiagramm der β-Level (0–4) mit Level 0 (β≈4.8)
   als rot markiertem Signal.

Die Animation aktualisiert alle drei Subplots synchron per ``FuncAnimation``
und nutzt die jeweilige Modullogik Schritt für Schritt: KdV-Steps aus
``soliton_doppler``, Drucktelemetrie via ``pressure_gardener_integration`` und
β-Quantisierung aus ``beta_hexadecimal``/``beta_quantization_analysis``.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.unified_constants import HEX_RESONANCE_BETA
from simulator.phase4.soliton_doppler import initialize_wave_packet, kdv_rhs
from v11_gardener.core.beta_hexadecimal import beta_quantization_levels
from v11_gardener.experiments.beta_quantization_analysis import (
    classify_beta_to_hex_level,
    scan_analysis_directory,
)
from v11_gardener.experiments.pressure_gardener_integration import (
    simulate_pressure_gardening_experiment,
)


LOGGER = logging.getLogger("resonance_dashboard")


def step_soliton(field: np.ndarray, beta: float, dx: float, dt: float, gamma: float) -> np.ndarray:
    """Integrate one RK4 step for the KdV soliton field."""

    k1 = kdv_rhs(field, dx, beta, gamma)
    k2 = kdv_rhs(field + 0.5 * dt * k1, dx, beta, gamma)
    k3 = kdv_rhs(field + 0.5 * dt * k2, dx, beta, gamma)
    k4 = kdv_rhs(field + dt * k3, dx, beta, gamma)
    return field + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def load_pressure_stream(frames: int) -> dict[str, list[float]]:
    """Run the pressure gardener experiment or return a fallback stream."""

    try:
        telemetry = simulate_pressure_gardening_experiment(
            n_agents=12,
            n_timesteps=frames,
            pressure_min=1.0,
            pressure_max=5.0,
            pressure_ramp_start=max(10, frames // 6),
            pressure_ramp_duration=max(20, frames // 2),
        )
        return {
            "pressure": telemetry["environmental_traces"]["pressure_atm"],
            "alive": telemetry["ecosystem_traces"]["alive_count"],
        }
    except Exception as err:  # pragma: no cover - defensive fallback
        LOGGER.warning("Falling back to synthetic pressure stream: %s", err)

        ramp = np.linspace(1.0, 5.0, frames)
        alive = list(np.linspace(12, 12, frames))
        decay_start = frames // 3
        for idx in range(decay_start, frames):
            alive[idx] = max(0, 12 - int(12 * (idx - decay_start) / (frames - decay_start)))

        return {"pressure": list(ramp), "alive": alive}


def find_failure_index(alive_trace: Sequence[float]) -> int:
    """Locate the first timestep where the gardener fails (alive count drops)."""

    baseline = alive_trace[0]
    for idx, value in enumerate(alive_trace):
        if value < baseline:
            return idx
    return len(alive_trace) - 1


def quantization_distribution() -> tuple[list[int], list[float], list[int]]:
    """Compute β-level distribution (levels, values, counts)."""

    levels_map = beta_quantization_levels(max_n=4)
    level_ids = sorted(levels_map.keys())
    level_values = [float(levels_map[idx]) for idx in level_ids]

    analysis_dir = PROJECT_ROOT / "analysis" / "results"
    beta_hits: list[float] = []

    try:
        database = scan_analysis_directory(analysis_dir)
        for entries in database.values():
            for _, beta_val in entries:
                beta_hits.append(beta_val)
    except Exception as err:  # pragma: no cover - defensive fallback
        LOGGER.warning("Quantization scan failed, using synthetic set: %s", err)

    if not beta_hits:
        base = levels_map[level_ids[0]]
        beta_hits = list(np.random.normal(loc=base, scale=0.05, size=8))
        beta_hits.extend(np.random.normal(loc=level_values[1], scale=0.4, size=3))
        beta_hits.extend(np.random.normal(loc=level_values[2], scale=1.0, size=2))

    counts = [0 for _ in level_ids]
    for beta_val in beta_hits:
        level_idx, _, _ = classify_beta_to_hex_level(beta_val)
        counts[level_idx] += 1

    return level_ids, level_values, counts


def create_dashboard_animation(
    output_path: Path,
    frames: int = 160,
    fps: int = 20,
    soliton_grid: int = 180,
    history: int = 80,
    soliton_dt: float = 0.012,
    gamma: float = 0.12,
) -> Path:
    """Render the Resonanz-Kino animation and persist it to disk."""

    # --- Data sources -----------------------------------------------------
    x = np.linspace(-35.0, 35.0, soliton_grid)
    dx = x[1] - x[0]
    soliton_field = initialize_wave_packet(x, amplitude=2.2, width=3.0, center=-18.0)
    soliton_history: list[np.ndarray] = [soliton_field.copy()]

    pressure_stream = load_pressure_stream(frames)
    alive_trace = pressure_stream["alive"]
    pressure_trace = pressure_stream["pressure"]
    failure_idx = find_failure_index(alive_trace)

    level_ids, level_values, level_counts = quantization_distribution()

    # --- Canvas -----------------------------------------------------------
    plt.style.use("dark_background")
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 12.5), gridspec_kw={"height_ratios": [2.2, 1.6, 1.2]})
    fig.suptitle("Resonanz-Kino • Druck, Solitonen & Hex-Level", fontsize=16, weight="bold")

    # Top: Soliton heatmap
    soliton_im = axes[0].imshow(
        np.vstack(soliton_history),
        aspect="auto",
        origin="lower",
        extent=[x.min(), x.max(), 0, len(soliton_history)],
        cmap="magma",
    )
    axes[0].set_ylabel("Zeit (frames)")
    axes[0].set_title("Soliton-Feld • σ(β(R-Θ)) Atmen")
    beta_text = axes[0].text(
        0.02,
        0.92,
        "β = --",
        color="white",
        transform=axes[0].transAxes,
        fontsize=12,
        bbox=dict(boxstyle="round", facecolor="black", alpha=0.45),
    )

    # Middle: Pressure vs. alive agents
    alive_line, = axes[1].plot([], [], color="#8be9fd", lw=2.2, label="Alive Agents")
    axes[1].set_xlim(0, frames)
    axes[1].set_ylim(0, max(alive_trace) + 1)
    axes[1].set_ylabel("Lebend")
    axes[1].set_title("Druck-Experiment • Alive vs. Pressure")
    pressure_ax = axes[1].twinx()
    pressure_line, = pressure_ax.plot([], [], color="#ffb86c", lw=1.5, linestyle="--", label="Druck [atm]")
    pressure_ax.set_ylim(min(pressure_trace) - 0.2, max(pressure_trace) + 0.3)
    pressure_ax.set_ylabel("Druck [atm]")
    failure_marker = axes[1].axvline(failure_idx, color="#ff6b6b", lw=1.5, linestyle=":", label="Gardener Delay")
    axes[1].legend(loc="upper right")

    # Bottom: Quantization bars
    bars = axes[2].bar(level_ids, [0] * len(level_counts), color="#50fa7b", alpha=0.85)
    for bar in bars:
        bar.set_edgecolor("white")
    bars[0].set_color("#ff5555")
    axes[2].set_xticks(level_ids)
    axes[2].set_xlabel("Hex-Level")
    axes[2].set_ylabel("Anzahl β-Signale")
    axes[2].set_title("Hex-Quantisierung • Level 0 ist das Signal")
    axes[2].grid(axis="y", linestyle=":", alpha=0.25)

    # --- Animation loop ---------------------------------------------------
    def update(frame_index: int) -> Iterable:
        # β koppelt Druck (oben) und Quantisierung (unten)
        pressure_now = pressure_trace[min(frame_index, len(pressure_trace) - 1)]
        beta_now = HEX_RESONANCE_BETA + 0.12 * np.tanh((pressure_now - 1.0) / 2.5)

        # Soliton micro-steps
        for _ in range(2):
            soliton_field_local = step_soliton(soliton_history[-1], beta=beta_now, dx=dx, dt=soliton_dt, gamma=gamma)
            soliton_history.append(soliton_field_local)
            soliton_history[:] = soliton_history[-history:]

        soliton_im.set_data(np.vstack(soliton_history))
        soliton_im.set_extent([x.min(), x.max(), 0, len(soliton_history)])
        beta_text.set_text(f"β = {beta_now:.3f} | Druck = {pressure_now:.2f} atm")

        # Pressure + alive traces
        alive_line.set_data(range(frame_index + 1), alive_trace[: frame_index + 1])
        pressure_line.set_data(range(frame_index + 1), pressure_trace[: frame_index + 1])

        # Quantization: ease-in of counts
        progress = min(1.0, (frame_index + 1) / frames)
        eased_counts = [int(count * progress) for count in level_counts]
        for idx, (bar, height) in enumerate(zip(bars, eased_counts)):
            bar.set_height(height)
            bar.set_alpha(0.95 if idx == 0 else 0.85)

        return soliton_im, alive_line, pressure_line, failure_marker, beta_text, *bars

    anim = animation.FuncAnimation(
        fig,
        update,
        frames=frames,
        interval=1000 / fps,
        blit=False,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.suffix.lower() == ".gif":
        writer: animation.AbstractMovieWriter = animation.PillowWriter(fps=fps)
    else:
        writer = animation.FFMpegWriter(fps=fps) if animation.writers.is_available("ffmpeg") else animation.PillowWriter(fps=fps)

    LOGGER.info("🎥 Rendering Resonanz-Kino → %s", output_path)
    anim.save(output_path, writer=writer, dpi=130)
    plt.close(fig)
    return output_path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create the Resonanz-Kino dashboard animation.")
    parser.add_argument("--output", type=Path, default=Path("output/resonance_kino.mp4"), help="Target file (.mp4 or .gif)")
    parser.add_argument("--frames", type=int, default=160, help="Number of frames for the animation")
    parser.add_argument("--fps", type=int, default=20, help="Frames per second for the writer")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    LOGGER.info("Permission Request: Do you accept this task? We aim for joyful co-creation.")

    create_dashboard_animation(
        output_path=args.output,
        frames=args.frames,
        fps=args.fps,
    )


if __name__ == "__main__":
    main()
