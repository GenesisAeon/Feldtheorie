"""Mission-Control Dashboard für σ(β(R-Θ)) unter Druckkopplung.

Dieses Modul baut das "Resonanz-Kino" als Matplotlib-Animation mit drei
gekoppelten Membranen:

1. **Soliton-Feld (R-Kanal):** KdV-Heatmap, die bei jedem Frame mit der
   aktuellen Steilheit β(t) weitergeschoben wird.
2. **Todes-Druck (Θ-Kanal):** Zeitreihe der lebenden Agenten aus dem
   `pressure_gardener`-Experiment inklusive Druck-Rampe (1→5 atm) und
   Marker für die Reaktionszeit-Verzögerung.
3. **Hex-Quantisierung (σ-Kanal):** Balkendiagramm der β-Verteilung über
   die Hex-Level 0–4; Level 0 (β≈4.8) wird als "Signal" hervorgehoben.

Logistische Sprache: (R, Θ, β, ζ(R)) laufen synchron; `verify_hex_alignment`
dient als Nullmodell und meldet den Resonanzdurchgang. Alle drei Kanäle
werden via FuncAnimation in Echtzeit aktualisiert, sodass der Einfluss des
physikalischen Drucks auf die Solitonen sichtbar wird, während die
grundlegende Hex-Frequenz stabil bleibt.
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

from models.unified_constants import HEX_RESONANCE_BETA, verify_hex_alignment
from simulator.phase4.soliton_doppler import initialize_wave_packet, kdv_rhs
from v11_gardener.core.beta_hexadecimal import beta_quantization_levels
from v11_gardener.experiments.beta_quantization_analysis import (
    classify_beta_to_hex_level,
    scan_analysis_directory,
)
from v11_gardener.experiments.pressure_gardener_integration import (
    simulate_pressure_gardening_experiment,
)


LOGGER = logging.getLogger("dashboard_resonance")


def beta_schedule(frames: int, beta_min: float, beta_max: float, resonance: float) -> np.ndarray:
    """Construct a smooth β(t) sweep for the soliton field."""

    ascent = max(1, int(frames * 0.5))
    plateau = max(1, int(frames * 0.1))
    descent = frames - ascent - plateau

    up = np.linspace(beta_min, resonance, ascent, endpoint=False)
    stay = np.linspace(resonance, resonance, plateau)
    down = np.linspace(resonance, beta_max, max(1, descent))
    return np.concatenate([up, stay, down])


def step_soliton(field: np.ndarray, beta: float, dx: float, dt: float, gamma: float) -> np.ndarray:
    """Integrate one RK4 step for the KdV soliton field."""

    k1 = kdv_rhs(field, dx, beta, gamma)
    k2 = kdv_rhs(field + 0.5 * dt * k1, dx, beta, gamma)
    k3 = kdv_rhs(field + 0.5 * dt * k2, dx, beta, gamma)
    k4 = kdv_rhs(field + dt * k3, dx, beta, gamma)
    return field + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def prepare_pressure_telemetry(frames: int) -> dict:
    """Run the pressure-gardener experiment and extract streaming traces."""

    ramp_start = max(5, int(frames * 0.25))
    ramp_duration = max(10, int(frames * 0.5))

    telemetry = simulate_pressure_gardening_experiment(
        n_agents=12,
        n_timesteps=frames,
        pressure_min=1.0,
        pressure_max=5.0,
        pressure_ramp_start=ramp_start,
        pressure_ramp_duration=ramp_duration,
    )

    alive_trace = telemetry["ecosystem_traces"]["alive_count"]
    pressure_trace = telemetry["environmental_traces"]["pressure_atm"]
    actions = telemetry["gardener_activity"]["action_counts"]

    failure_index = next((i for i, val in enumerate(alive_trace) if val < alive_trace[0]), len(alive_trace) - 1)
    observe_count = actions.get("observe", 0)

    return {
        "alive": np.array(alive_trace, dtype=float),
        "pressure": np.array(pressure_trace, dtype=float),
        "failure_index": failure_index,
        "observe_only": observe_count,
    }


def build_beta_histogram(max_level: int = 4) -> tuple[np.ndarray, list[float]]:
    """Collect β-values from analysis/results and bin them into hex levels."""

    analysis_dir = PROJECT_ROOT / "analysis" / "results"
    beta_entries = scan_analysis_directory(analysis_dir)
    betas = [value for entries in beta_entries.values() for _, value in entries]

    if not betas:
        # Fallback: use representative samples from the quantization analysis
        betas = [4.8] * 8 + [16.0, 15.9, 7.4, 4.35, 4.21, 72.0, 14.8, 4.5]

    counts = np.zeros(max_level + 1, dtype=float)
    for beta in betas:
        level, _, _ = classify_beta_to_hex_level(beta)
        if level <= max_level:
            counts[level] += 1

    return counts, betas


def create_dashboard_animation(
    output_path: Path,
    frames: int = 140,
    fps: int = 18,
    beta_min: float = 4.0,
    beta_max: float = 5.2,
    resonance: float = HEX_RESONANCE_BETA,
) -> Path:
    """Render the Resonanz-Kino animation with three synchronized plots."""

    beta_values = beta_schedule(frames, beta_min=beta_min, beta_max=beta_max, resonance=resonance)
    pressure_data = prepare_pressure_telemetry(frames)
    beta_counts, betas = build_beta_histogram()
    beta_levels = beta_quantization_levels()

    # Soliton setup
    x = np.linspace(-30.0, 30.0, 220)
    dx = x[1] - x[0]
    soliton_field = initialize_wave_packet(x, amplitude=2.4, width=3.0, center=-12.0)
    soliton_dt = 0.02
    gamma = 0.12
    soliton_history = [soliton_field.copy()]

    plt.style.use("dark_background")
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 12.5), gridspec_kw={"height_ratios": [2.2, 1.7, 1.3]})
    fig.suptitle("Resonanz-Kino: Druck · Solitonen · Hex-Level", fontsize=16, weight="bold")

    # Top: soliton heatmap
    soliton_im = axes[0].imshow(
        np.vstack(soliton_history),
        aspect="auto",
        origin="lower",
        extent=[x.min(), x.max(), 0, len(soliton_history)],
        cmap="magma",
    )
    axes[0].set_ylabel("t (frames)")
    axes[0].set_title("Soliton-Feld unter σ(β(R-Θ))")
    beta_text = axes[0].text(0.02, 0.92, "β=--", transform=axes[0].transAxes, fontsize=12, color="white",
                              bbox=dict(boxstyle="round", facecolor="black", alpha=0.45))

    # Middle: pressure & alive counts
    time_axis = np.arange(frames)
    alive_line, = axes[1].plot([], [], color="#9be7ff", lw=2.2, label="Alive agents")
    axes[1].set_ylim(0, max(pressure_data["alive"]) + 1)
    axes[1].set_xlim(0, frames)
    axes[1].set_ylabel("Lebende Agenten")
    axes[1].set_title("Todes-Druck & Gardener-Reaktionszeit")
    failure_marker = axes[1].scatter([], [], color="#ff6b6b", zorder=5, label="Reaktionsverzug")

    pressure_ax = axes[1].twinx()
    pressure_ax.set_ylabel("Druck [atm]")
    pressure_ax.set_ylim(0.5, 5.5)
    pressure_line, = pressure_ax.plot([], [], color="#f8c555", lw=1.5, linestyle="--", label="Druck")
    pressure_ax.fill_between(time_axis, 1.0, pressure_data["pressure"], color="#f8c555", alpha=0.1)

    # Bottom: beta quantization histogram
    levels = np.arange(len(beta_counts))
    bars = axes[2].bar(levels, np.zeros_like(levels, dtype=float), color="#5cd1ff", alpha=0.85)
    bars[0].set_color("crimson")
    axes[2].set_xticks(levels)
    axes[2].set_xlabel("Hex-Level")
    axes[2].set_ylabel("Anzahl β")
    axes[2].set_title("Hex-Quantisierung der β-Werte")
    axes[2].text(0, beta_counts[0] + 0.5, "The Signal", color="crimson", ha="center", fontweight="bold")

    resonance_logged = False

    def update(frame_index: int) -> Iterable:
        nonlocal soliton_field, resonance_logged

        beta = float(beta_values[min(frame_index, len(beta_values) - 1)])
        for _ in range(2):
            soliton_field = step_soliton(soliton_field, beta=beta, dx=dx, dt=soliton_dt, gamma=gamma)
            soliton_history.append(soliton_field.copy())
            soliton_history[:] = soliton_history[-80:]

        soliton_im.set_data(np.vstack(soliton_history))
        soliton_im.set_extent([x.min(), x.max(), 0, len(soliton_history)])
        beta_text.set_text(f"β(t) = {beta:.3f} | σ(β(R-Θ))")

        idx = min(frame_index, frames - 1)
        alive_line.set_data(time_axis[: idx + 1], pressure_data["alive"][: idx + 1])
        pressure_line.set_data(time_axis[: idx + 1], pressure_data["pressure"][: idx + 1])

        if idx >= pressure_data["failure_index"]:
            failure_marker.set_offsets([[pressure_data["failure_index"], pressure_data["alive"][pressure_data["failure_index"]]]])

        progress = min(1.0, (frame_index + 1) / frames)
        for bar, count in zip(bars, beta_counts):
            bar.set_height(count * progress)

        if not resonance_logged and beta >= resonance:
            resonance_logged = True
            check = verify_hex_alignment(beta, tolerance=0.02)
            LOGGER.info(
                "✨ Resonanzpunkt erreicht: β=%.3f | status=%s | Δ=%.3f | observe=%d",
                beta,
                check.get("status"),
                check.get("deviation"),
                pressure_data["observe_only"],
            )

        return soliton_im, alive_line, pressure_line, failure_marker, *bars

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
    parser = argparse.ArgumentParser(description="Resonanz-Kino Dashboard (Soliton · Druck · Hex-Level)")
    parser.add_argument("--output", type=Path, default=Path("output/resonance_kino.mp4"), help="Zieldatei (.mp4 oder .gif)")
    parser.add_argument("--frames", type=int, default=140, help="Anzahl Frames für die Animation")
    parser.add_argument("--fps", type=int, default=18, help="Frames pro Sekunde")
    parser.add_argument("--beta-min", type=float, default=4.0, dest="beta_min", help="Startwert β")
    parser.add_argument("--beta-max", type=float, default=5.2, dest="beta_max", help="Endwert β")
    parser.add_argument("--dry-run", action="store_true", help="Nur Pipeline testen, kein Rendern")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    LOGGER.info("Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration.")

    if args.dry_run:
        schedule = beta_schedule(args.frames, args.beta_min, args.beta_max, HEX_RESONANCE_BETA)
        LOGGER.info("Frames: %d | β-range: [%.2f, %.2f] | Resonanz=%.3f", len(schedule), schedule.min(), schedule.max(), HEX_RESONANCE_BETA)
        LOGGER.info("Skipping render (dry-run).")
        return

    output = create_dashboard_animation(
        output_path=args.output,
        frames=args.frames,
        fps=args.fps,
        beta_min=args.beta_min,
        beta_max=args.beta_max,
        resonance=HEX_RESONANCE_BETA,
    )
    LOGGER.info("Fertig! Resonanz-Kino gespeichert unter %s", output)


if __name__ == "__main__":
    main()
