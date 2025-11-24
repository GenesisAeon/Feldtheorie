"""
Visualize 4D Tesseract Time-Slicing

Provides visualization tools for rendering 4D hypercube timeslices as:
1. Individual 3D cubes (normal orientation, not pyramids)
2. Animated evolution through temporal layers
3. Dual-view: 4D projection + extracted 3D slice
4. Photon paths through timeslices

Usage:
    python scripts/visualize_tesseract.py --mode animation
    python scripts/visualize_tesseract.py --mode dual-view --slice 50
    python scripts/visualize_tesseract.py --mode photon-paths
"""
import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

from simulation.tesseract_timeslices import (
    TesseractConfig,
    TesseractTimeSlices,
    PhotonPropagator,
)


def render_cube_wireframe(ax, edges, color='black', alpha=0.3, linewidth=1):
    """Render cube wireframe edges."""
    for start, end in edges:
        points = np.array([start, end])
        ax.plot3D(points[:, 0], points[:, 1], points[:, 2],
                  color=color, linewidth=linewidth, alpha=alpha)


def render_normal_cube(
    ax,
    cube_3d: np.ndarray,
    tesseract: TesseractTimeSlices,
    time_label: str = "",
    show_wireframe: bool = True,
    show_isosurface: bool = True,
):
    """
    Render 3D cube in NORMAL orientation (standing on base, not inverted).

    Args:
        ax: Matplotlib 3D axis
        cube_3d: 3D array to render
        tesseract: TesseractTimeSlices instance
        time_label: Label for plot title
        show_wireframe: Whether to show cube edges
        show_isosurface: Whether to show field isosurface
    """
    ax.clear()

    # Isosurface rendering
    if show_isosurface and np.max(cube_3d) > 0:
        try:
            verts, faces = tesseract.compute_isosurface(cube_3d)

            # Plot triangulated surface
            ax.plot_trisurf(
                verts[:, 0], verts[:, 1], faces, verts[:, 2],
                cmap='viridis', alpha=0.7, linewidth=0, shade=True
            )
        except (ValueError, RuntimeError):
            # If isosurface extraction fails, skip
            pass

    # Wireframe rendering
    if show_wireframe:
        edges = tesseract.get_cube_wireframe_edges()
        render_cube_wireframe(ax, edges, color='black', alpha=0.5, linewidth=1.5)

    # Styling
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'Zeitscheibe: {time_label}')
    ax.set_box_aspect([1, 1, 1])  # Equal aspect ratio

    # Set limits to show full cube
    n = tesseract.config.resolution
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_zlim(0, n)


def visualize_4d_projection(
    ax,
    tesseract: TesseractTimeSlices,
    current_t_index: int,
    sample_every: int = 10,
):
    """
    Visualize 4D hypercube as stacked 3D slices (projection).

    Shows multiple timeslices overlaid with vertical offset to represent t-axis.
    Current slice is highlighted.

    Args:
        ax: Matplotlib 3D axis
        tesseract: TesseractTimeSlices instance
        current_t_index: Index of current timeslice to highlight
        sample_every: Sample every N slices for visualization
    """
    ax.clear()

    n = tesseract.config.resolution
    z_scale = 0.5  # Vertical spacing between slices

    for t_idx in range(0, tesseract.config.num_slices, sample_every):
        # Highlight current slice
        is_current = (t_idx == current_t_index)
        alpha = 0.8 if is_current else 0.1
        color = 'red' if is_current else 'gray'
        linewidth = 2.0 if is_current else 0.5

        # Vertical offset for this timeslice
        z_offset = t_idx * z_scale

        # Draw cube wireframe at this height
        s = n - 1
        corners = np.array([
            [0, 0, z_offset], [s, 0, z_offset],
            [s, s, z_offset], [0, s, z_offset],
            [0, 0, z_offset + s*z_scale], [s, 0, z_offset + s*z_scale],
            [s, s, z_offset + s*z_scale], [0, s, z_offset + s*z_scale],
        ])

        edge_indices = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom
            (4, 5), (5, 6), (6, 7), (7, 4),  # Top
            (0, 4), (1, 5), (2, 6), (3, 7),  # Vertical
        ]

        for i, j in edge_indices:
            points = corners[[i, j]]
            ax.plot3D(points[:, 0], points[:, 1], points[:, 2],
                      color=color, linewidth=linewidth, alpha=alpha)

    ax.set_title('4D-Hyperkubus (gestapelte Zeitscheiben)')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Zeit (Z + t)')
    ax.set_box_aspect([1, 1, 2])


def create_animation(
    tesseract: TesseractTimeSlices,
    output_path: str = "outputs/tesseract_animation.mp4",
    fps: int = 20,
):
    """
    Create animation cycling through all timeslices.

    Args:
        tesseract: TesseractTimeSlices instance
        output_path: Path to save animation
        fps: Frames per second
    """
    print(f"🎬 Creating animation with {tesseract.config.num_slices} frames...")

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    def update(frame):
        """Animation update function."""
        cube_3d = tesseract.extract_timeslice(frame)
        t = tesseract.t_1d[frame]
        render_normal_cube(ax, cube_3d, tesseract, f"t = {t:.3f}")
        return ax,

    anim = FuncAnimation(
        fig, update,
        frames=tesseract.config.num_slices,
        interval=1000//fps,
        blit=False
    )

    # Save animation
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"💾 Saving to {output_path}...")
    anim.save(str(output_file), writer='ffmpeg', fps=fps)
    print(f"✅ Animation saved!")

    plt.close()


def create_dual_view(
    tesseract: TesseractTimeSlices,
    t_index: int,
    output_path: str | None = None,
):
    """
    Create dual-view figure: 4D projection + extracted 3D slice.

    Args:
        tesseract: TesseractTimeSlices instance
        t_index: Timeslice index to display
        output_path: Optional path to save figure
    """
    print(f"📸 Creating dual-view for slice t={t_index}...")

    fig = plt.figure(figsize=(16, 7))

    # Left: 4D projection
    ax1 = fig.add_subplot(121, projection='3d')
    visualize_4d_projection(ax1, tesseract, t_index, sample_every=5)

    # Right: Extracted 3D cube
    ax2 = fig.add_subplot(122, projection='3d')
    cube_3d = tesseract.extract_timeslice(t_index)
    t = tesseract.t_1d[t_index]
    render_normal_cube(ax2, cube_3d, tesseract, f"t = {t:.3f}")

    plt.tight_layout()

    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✅ Figure saved to {output_path}")

    plt.show()


def visualize_photon_paths(
    tesseract: TesseractTimeSlices,
    num_photons: int = 5,
    output_path: str | None = None,
):
    """
    Visualize multiple photon paths through 4D tesseract.

    Args:
        tesseract: TesseractTimeSlices instance
        num_photons: Number of photon trajectories to show
        output_path: Optional path to save figure
    """
    print(f"🌊 Computing {num_photons} photon paths...")

    propagator = PhotonPropagator(tesseract)
    n = tesseract.config.resolution

    # Generate photon paths with different starting positions
    paths = []
    start_positions = [
        (n//2, n//2, n//2),  # Center
        (n//4, n//4, n//4),  # Off-center 1
        (3*n//4, n//2, n//2),  # Off-center 2
        (n//2, 3*n//4, n//4),  # Off-center 3
        (n//4, 3*n//4, 3*n//4),  # Off-center 4
    ]

    for i in range(num_photons):
        start_pos = start_positions[i % len(start_positions)]
        path = propagator.propagate_photon(start_pos, start_t_index=0)
        paths.append(path)

    # Compute consciousness integral
    I_C = propagator.compute_consciousness_integral(paths)
    print(f"   Consciousness integral I_C = {I_C:.6f}")

    # Visualize
    fig = plt.figure(figsize=(14, 10))

    # 3D plot: x, y, t (z mapped to color)
    ax = fig.add_subplot(111, projection='3d')

    for i, path in enumerate(paths):
        if len(path) > 0:
            # Color by z-coordinate
            colors = plt.cm.viridis(path[:, 2] / n)

            ax.plot3D(
                path[:, 0], path[:, 1], path[:, 3],  # x, y, t
                linewidth=2, label=f'Photon {i+1}',
                alpha=0.8
            )

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Zeit (Scheiben-Index)')
    ax.set_title(f'Photonenbahnen durch 4D-Tesseract\nBewusstseins-Integral I_C = {I_C:.3f}')
    ax.legend(loc='upper left')

    plt.tight_layout()

    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✅ Figure saved to {output_path}")

    plt.show()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Visualize 4D Tesseract Time-Slicing"
    )
    parser.add_argument(
        "--mode",
        choices=["animation", "dual-view", "photon-paths"],
        default="dual-view",
        help="Visualization mode"
    )
    parser.add_argument(
        "--slice",
        type=int,
        default=None,
        help="Timeslice index for dual-view (default: middle slice)"
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=32,
        help="Grid resolution (default: 32)"
    )
    parser.add_argument(
        "--num-slices",
        type=int,
        default=50,
        help="Number of temporal slices (default: 50)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path"
    )

    args = parser.parse_args()

    # Initialize tesseract
    print("🎲 Initializing 4D Tesseract...")
    config = TesseractConfig(
        resolution=args.resolution,
        num_slices=args.num_slices,
    )
    tesseract = TesseractTimeSlices(config)
    print(f"✅ 4D block shape: {tesseract.block_4d.shape}")

    # Select mode
    if args.mode == "animation":
        output = args.output or "outputs/tesseract_animation.mp4"
        create_animation(tesseract, output)

    elif args.mode == "dual-view":
        t_index = args.slice if args.slice is not None else (tesseract.config.num_slices // 2)
        output = args.output or f"outputs/tesseract_dual_view_t{t_index}.png"
        create_dual_view(tesseract, t_index, output)

    elif args.mode == "photon-paths":
        output = args.output or "outputs/tesseract_photon_paths.png"
        visualize_photon_paths(tesseract, num_photons=5, output_path=output)

    print("✨ Done!")


if __name__ == "__main__":
    main()
