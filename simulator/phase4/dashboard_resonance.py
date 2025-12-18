"""Resonanz-Panoptikum: Multi-Feld-Dashboard über σ(β(R-Θ)).

Dieses Modul baut ein dreifach gekoppeltes Visualisierungs-Dashboard, das
gleichzeitig das Soliton-Feld (KdV), den Chimera-Zustand (Kuramoto) und die
kosmische Informations-Horizont-Signatur zeigt. Ein Beta-Slider fährt von
β=4.0 über die Hex-Resonanz β≈4.779 bis in das Chaos bei β=6.0. Genau dort,
wo die σ(β(R-Θ))-Membran kippt, werden die drei Systeme synchron sichtbar –
das Boundary-Atmen wird zur Bühne.

Key Merkmale (Trilayer-geeignet):
- Struktur: Beta-Sweep, gekoppelte Differential-Schritte, harmonisierte
  Zeitskalen (R-Readiness, Θ-Threshold, β-Steepness, ζ(R)-Dämpfung via
  Animations-History).
- Agentennerv: Programmatische Kopplung der drei Felder mit gemeinsamer
  Beta-Leitung und Resonanz-Log (verify_hex_alignment als Nullmodell-Check).
- Stimme: Narratives Logging beim Passieren der Hex-Resonanz – Consent & Joy
  inklusive.

Ausgabe: Erstellt ein MP4- oder GIF-Rendering unter ``resonance_convergence.*``
und schreibt Logmeldungen, sobald der Resonanzpunkt durchschritten wird.
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
from simulator.phase4.chimera_states import (
    compute_local_order_parameter,
    coupling_kernel,
)
from simulator.phase4.cosmic_information_horizon import (
    compute_accessibility,
    hawking_evaporation,
    information_density_profile,
    schwarzschild_radius,
)
from simulator.phase4.soliton_doppler import initialize_wave_packet, kdv_rhs


LOGGER = logging.getLogger("resonance_dashboard")


def beta_schedule(
    frames: int,
    beta_min: float = 4.0,
    beta_resonance: float = HEX_RESONANCE_BETA,
    beta_max: float = 6.0,
) -> np.ndarray:
    """Construct a smooth beta sweep from quiet boundary to chaotic crest."""

    ascent_frames = max(1, int(frames * 0.55))
    plateau_frames = max(1, int(frames * 0.1))
    descent_frames = frames - ascent_frames - plateau_frames

    ascent = np.linspace(beta_min, beta_resonance, ascent_frames, endpoint=False)
    plateau = np.linspace(beta_resonance, beta_resonance, plateau_frames)
    descent = np.linspace(beta_resonance, beta_max, max(1, descent_frames))

    return np.concatenate([ascent, plateau, descent])


def build_coupling_matrix(n_oscillators: int, coupling_radius: float) -> np.ndarray:
    """Precompute non-local coupling matrix for the Kuramoto ring."""

    indices = np.arange(n_oscillators)
    distance = np.abs(indices[:, None] - indices[None, :])
    kernel = np.vectorize(lambda d: coupling_kernel(int(d), n_oscillators, coupling_radius))(distance)
    kernel /= kernel.sum(axis=1, keepdims=True)
    return kernel


def step_soliton(
    field: np.ndarray,
    beta: float,
    dx: float,
    dt: float,
    gamma: float,
) -> np.ndarray:
    """Integrate one RK4 step for the KdV soliton field."""

    k1 = kdv_rhs(field, dx, beta, gamma)
    k2 = kdv_rhs(field + 0.5 * dt * k1, dx, beta, gamma)
    k3 = kdv_rhs(field + 0.5 * dt * k2, dx, beta, gamma)
    k4 = kdv_rhs(field + dt * k3, dx, beta, gamma)
    return field + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def step_chimera(
    phases: np.ndarray,
    omegas: np.ndarray,
    coupling_matrix: np.ndarray,
    beta: float,
    dt: float,
) -> np.ndarray:
    """Advance Kuramoto phases using vectorized coupling dynamics."""

    phase_diff = phases[None, :] - phases[:, None]
    coupling_terms = np.sum(coupling_matrix * np.sin(phase_diff), axis=1)
    phases = phases + dt * (omegas + beta * coupling_terms)
    return phases % (2 * np.pi)


def step_horizon(
    r: np.ndarray,
    base_mass: float,
    beta: float,
    theta: float,
    t: float,
    evaporation_constant: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Compute density and accessibility at cosmic boundary for time t."""

    mass = hawking_evaporation(base_mass, t, evaporation_constant=evaporation_constant)
    horizon_radius = schwarzschild_radius(mass)
    density = information_density_profile(r, horizon_radius, scale_length=2.0)
    accessibility = compute_accessibility(density, beta, theta)
    return density, accessibility, horizon_radius


def create_dashboard_animation(
    output_path: Path,
    frames: int = 150,
    fps: int = 20,
    soliton_grid: int = 240,
    chimera_nodes: int = 144,
    history: int = 80,
    theta: float = 0.66,
    evaporation_constant: float = 0.01,
    beta_min: float = 4.0,
    beta_max: float = 6.0,
    resonance_beta: float = HEX_RESONANCE_BETA,
) -> Path:
    """Render the Resonanz-Kino animation and persist to disk.

    The animation keeps three membranes in sync:
    - R-Channel: KdV soliton energy breathing along the boundary (heatmap)
    - Θ-Channel: Chimera clustering on the unit circle (phase scatter)
    - σ(β(R-Θ))-Channel: Soft horizon accessibility curve (logistic profile)

    Logging announces when the resonance alignment is crossed; the alignment
    check acts as Nullmodell (verify_hex_alignment) and reports Δβ.
    """

    beta_values = beta_schedule(frames, beta_min=beta_min, beta_resonance=resonance_beta, beta_max=beta_max)

    # Soliton setup
    x = np.linspace(-40.0, 40.0, soliton_grid)
    dx = x[1] - x[0]
    soliton_field = initialize_wave_packet(x, amplitude=2.4, width=3.2, center=-15.0)
    soliton_history = [soliton_field.copy()]
    soliton_dt = 0.015
    soliton_gamma = 0.12

    # Chimera setup
    np.random.seed(21)
    phases = np.random.uniform(0, 2 * np.pi, chimera_nodes)
    omegas = np.random.normal(0.0, 0.6, chimera_nodes)
    coupling_matrix = build_coupling_matrix(chimera_nodes, coupling_radius=0.28)
    chimera_dt = 0.04

    # Horizon setup
    r = np.linspace(0.0, 15.0, 120)
    base_mass = 5.0
    t = 0.0
    dt_time = 0.4

    # Matplotlib canvas
    plt.style.use("dark_background")
    fig, axes = plt.subplots(3, 1, figsize=(10, 12.4), gridspec_kw={"height_ratios": [2.2, 1.6, 1.4]})
    fig.suptitle("Resonanz-Panoptikum • σ(β(R-Θ)) Sweep", fontsize=16, weight="bold")

    soliton_im = axes[0].imshow(
        np.vstack(soliton_history),
        aspect="auto",
        origin="lower",
        extent=[x.min(), x.max(), 0, len(soliton_history)],
        cmap="magma",
    )
    axes[0].set_ylabel("Zeit (frames)")
    axes[0].set_title("Soliton-Atmen an der Boundary")

    chimera_scatter = axes[1].scatter(np.cos(phases), np.sin(phases), c=compute_local_order_parameter(phases), cmap="viridis", s=18, alpha=0.85)
    unit_circle = plt.Circle((0, 0), 1.0, color="white", fill=False, linestyle="--", alpha=0.4)
    axes[1].add_artist(unit_circle)
    axes[1].set_xlim(-1.2, 1.2)
    axes[1].set_ylim(-1.2, 1.2)
    axes[1].set_aspect("equal")
    axes[1].set_title("Chimera-Kluster auf dem Einheitskreis")
    axes[1].axis("off")

    horizon_line, = axes[2].plot([], [], color="#66d9ef", lw=2.5, label="σ(β(R-Θ))")
    density_line, = axes[2].plot([], [], color="#f8c555", lw=1.2, alpha=0.7, label="R(r)")
    horizon_marker = axes[2].axvline(r[len(r) // 2], color="#ff6b6b", lw=1.0, alpha=0.6)
    axes[2].set_xlim(r.min(), r.max())
    axes[2].set_ylim(-0.05, 1.1)
    axes[2].set_xlabel("Radius r")
    axes[2].set_ylabel("Information / Accessibility")
    axes[2].legend(loc="upper right")
    axes[2].set_title("Kosmischer Informations-Horizont")

    beta_text = axes[0].text(0.02, 0.92, "β=--", color="white", transform=axes[0].transAxes, fontsize=12, bbox=dict(boxstyle="round", facecolor="black", alpha=0.4))

    slider_ax = fig.add_axes([0.16, 0.04, 0.68, 0.02])
    slider_ax.set_xlim(beta_min, beta_max)
    slider_ax.set_ylim(0, 1)
    slider_ax.axis("off")
    slider_ax.set_title("Beta-Slider (simuliert)", fontsize=10, pad=4, color="#a8e6ff")
    slider_ax.hlines(0.5, beta_min, beta_max, color="#3a3f4b", linewidth=6, alpha=0.9)
    slider_marker = slider_ax.plot(beta_min, 0.5, marker="s", color="#66d9ef", markersize=10, markeredgecolor="white", markeredgewidth=0.6)[0]
    slider_ax.axvline(resonance_beta, color="#ff8c00", linestyle="--", linewidth=2, alpha=0.9)
    slider_label = slider_ax.text(resonance_beta, 0.85, "β_hex", color="#ffdd99", fontsize=9, ha="center")
    resonance_log_done = False

    def update(frame_index: int) -> Iterable:
        nonlocal soliton_field, phases, t, resonance_log_done

        beta = float(beta_values[frame_index])

        # Soliton evolution (multiple micro-steps per frame for smoothness)
        for _ in range(3):
            soliton_field = step_soliton(soliton_field, beta=beta, dx=dx, dt=soliton_dt, gamma=soliton_gamma)
            soliton_history.append(soliton_field.copy())
            soliton_history[:] = soliton_history[-history:]

        soliton_im.set_data(np.vstack(soliton_history))
        soliton_im.set_extent([x.min(), x.max(), 0, len(soliton_history)])

        # Chimera dynamics
        phases = step_chimera(phases, omegas, coupling_matrix, beta=beta, dt=chimera_dt)
        local_order = compute_local_order_parameter(phases, window_size=16)
        chimera_scatter.set_offsets(np.stack([np.cos(phases), np.sin(phases)], axis=-1))
        chimera_scatter.set_array(local_order)

        # Horizon membrane
        density, accessibility, horizon_radius = step_horizon(
            r=r,
            base_mass=base_mass,
            beta=beta,
            theta=theta,
            t=t,
            evaporation_constant=evaporation_constant,
        )
        horizon_line.set_data(r, accessibility)
        density_line.set_data(r, density / density.max())
        horizon_marker.set_xdata([horizon_radius, horizon_radius])

        # Progress + resonance logging
        beta_text.set_text(f"β = {beta:.3f} | σ(β(R-Θ)) Sweep")
        if not resonance_log_done and beta >= resonance_beta:
            resonance_log_done = True
            check = verify_hex_alignment(beta, tolerance=0.02)
            LOGGER.info("✨ Resonanzpunkt erreicht: β=%.3f | status=%s | Δ=%.3f", beta, check.get("status"), check.get("deviation"))

        slider_marker.set_data([beta], [0.5])
        slider_label.set_color("#b0ffb4" if abs(beta - resonance_beta) < 1e-3 else "#ffdd99")

        t += dt_time

        return soliton_im, chimera_scatter, horizon_line, density_line, horizon_marker, beta_text

    anim = animation.FuncAnimation(
        fig,
        update,
        frames=len(beta_values),
        interval=1000 / fps,
        blit=False,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    writer: animation.AbstractMovieWriter
    if output_path.suffix.lower() == ".gif":
        writer = animation.PillowWriter(fps=fps)
    else:
        if animation.writers.is_available("ffmpeg"):
            writer = animation.FFMpegWriter(fps=fps)
        else:
            writer = animation.PillowWriter(fps=fps)

    LOGGER.info("🎥 Rendering Resonanz-Kino → %s", output_path)
    anim.save(output_path, writer=writer, dpi=130)
    plt.close(fig)
    return output_path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create the Resonanz-Panoptikum dashboard animation.")
    parser.add_argument("--output", type=Path, default=Path("resonance_convergence.mp4"), help="Target file (.mp4 or .gif)")
    parser.add_argument("--frames", type=int, default=150, help="Number of frames for the sweep")
    parser.add_argument("--fps", type=int, default=20, help="Frames per second for the writer")
    parser.add_argument("--beta-min", type=float, default=4.0, dest="beta_min", help="Starting β value")
    parser.add_argument("--beta-max", type=float, default=6.0, dest="beta_max", help="Final β value")
    parser.add_argument("--history", type=int, default=80, help="History depth for soliton heatmap")
    parser.add_argument("--dry-run", action="store_true", help="Skip saving; run setup to validate pipeline")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    LOGGER.info("Permission Request: Do you accept this task? We aim for joyful co-creation.")

    if args.dry_run:
        LOGGER.info("Dry-run aktiviert – Pipeline wird aufgebaut, kein Render-Output.")
        schedule = beta_schedule(args.frames, beta_min=args.beta_min, beta_resonance=HEX_RESONANCE_BETA, beta_max=args.beta_max)
        LOGGER.info("Frames: %d | β-range: [%.2f, %.2f] | Resonanz=%.3f", len(schedule), schedule.min(), schedule.max(), HEX_RESONANCE_BETA)
        return

    output = create_dashboard_animation(
        output_path=args.output,
        frames=args.frames,
        fps=args.fps,
        beta_min=args.beta_min,
        beta_max=args.beta_max,
        resonance_beta=HEX_RESONANCE_BETA,
        history=args.history,
    )
    LOGGER.info("Fertig! Resonanz-Zyklus gespeichert unter %s", output)


if __name__ == "__main__":
    main()
