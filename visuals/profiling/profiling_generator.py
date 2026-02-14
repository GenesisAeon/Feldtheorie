"""AFET Visual Profiling Hub — Quad-Layer Component 4.

Generates spatial/topological snapshots of the AFET field state.
Each snapshot is a micro-cosmic image of the entire AFET field:

- Central halo  -> sigma_Phi metastability buffer
- Hexagon grid  -> beta-hierarchy (domains as hexagons)
- Radial lines  -> Phi-scaling / frame principle
- Nucleus point -> beta_critical (rigid axiom anchor)
- Warning ring  -> S_crit proximity (frame-collapse warning)

This is the visual counterpart to the sonification layer (Layer 3),
completing the Quad-Layer architecture:
  1. Code/Logic   -> UTAC implementation + aeon modules
  2. Documentation -> human narrative + trilayer docs
  3. Sonification  -> auditive resonance checks (time/dynamics)
  4. VisualProfilingHub -> symbolic snapshot (space/topology)

Usage:
    >>> from visuals.profiling import ProfilingGenerator
    >>> gen = ProfilingGenerator()
    >>> gen.generate_snapshot(output_path="field_state.png")

    # With custom metrics:
    >>> metrics = FieldMetrics(
    ...     sigma_phi_deviation=0.01,
    ...     beta_values={"neuro": 13.5, "climate": 11.0},
    ...     s_crit_proximity=0.3,
    ... )
    >>> gen.generate_snapshot(metrics=metrics)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, RegularPolygon

from theory.afet import AFETConstants, AFETFramework

try:
    import plotly.graph_objects as go

    _PLOTLY_AVAILABLE = True
except ImportError:  # pragma: no cover
    go = None
    _PLOTLY_AVAILABLE = False

logger = logging.getLogger(__name__)

_SYMBOLS_PATH = Path(__file__).parent / "symbols.json"

# Default domain beta values from AFET framework
_DEFAULT_DOMAINS: dict[str, float] = {
    "info": 4.3,
    "bio": 7.4,
    "climate": 11.0,
    "neuro": 13.5,
    "axioms": 37.6,
}


@dataclass
class FieldMetrics:
    """Current state of the AFET field for visualization.

    Attributes
    ----------
    sigma_phi_deviation : float
        Deviation of sigma_Phi from its nominal value (0.0625).
        0.0 = nominal, approaching 1.0 = near collapse.
    beta_values : dict[str, float]
        Domain name -> observed beta value.
    s_crit_proximity : float
        How close the system is to critical entropy (0.0 = safe, 1.0 = at S_crit).
    entropy_density : float
        Current entropy density of the field.
    label : str
        Optional label for the snapshot (e.g. DOI iteration, timestamp).
    """

    sigma_phi_deviation: float = 0.0
    beta_values: dict[str, float] = field(default_factory=lambda: dict(_DEFAULT_DOMAINS))
    s_crit_proximity: float = 0.0
    entropy_density: float = 0.0
    label: str = ""


def load_symbols(path: Path | None = None) -> dict[str, Any]:
    """Load the symbol mapping from symbols.json."""
    p = path or _SYMBOLS_PATH
    with open(p) as f:
        return json.load(f)


class ProfilingGenerator:
    """Generates AFET field-state profiling snapshots (Profiling-Tafel).

    The generator reads the symbol mapping from ``symbols.json`` and
    uses ``AFETFramework`` for all constant lookups and computations.
    """

    def __init__(
        self,
        symbols_path: Path | None = None,
        figsize: tuple[float, float] = (9.0, 9.0),
        dpi: int = 300,
    ) -> None:
        self.symbols = load_symbols(symbols_path)
        self.figsize = figsize
        self.dpi = dpi
        self.afet = AFETFramework()

    def generate_snapshot(
        self,
        metrics: FieldMetrics | None = None,
        output_path: str | Path | None = None,
    ) -> Path:
        """Render a profiling snapshot of the current AFET field state.

        Parameters
        ----------
        metrics : FieldMetrics, optional
            Field state to visualize. Uses nominal defaults if not provided.
        output_path : str | Path, optional
            Where to save the image. Defaults to ``profiling_snapshot.png``
            in the examples/ directory.

        Returns
        -------
        Path
            Path to the saved snapshot image.
        """
        if metrics is None:
            metrics = FieldMetrics()

        if output_path is None:
            output_path = Path(__file__).parent / "examples" / "profiling_snapshot.png"
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        bg = self.symbols.get("background", "#000000")
        fig, ax = plt.subplots(figsize=self.figsize, facecolor=bg)
        ax.set_facecolor(bg)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")

        self._draw_phi_radials(ax)
        self._draw_sigma_halo(ax, metrics)
        self._draw_frame_collapse_ring(ax, metrics)
        self._draw_beta_domains(ax, metrics)
        self._draw_nucleus(ax)
        self._draw_title(ax, metrics)

        fig.savefig(
            str(output_path),
            dpi=self.dpi,
            bbox_inches="tight",
            facecolor=bg,
            edgecolor="none",
        )
        plt.close(fig)
        logger.info("Profiling snapshot saved to %s", output_path)
        return output_path

    def get_field_snapshot(
        self,
        metrics: FieldMetrics | None = None,
    ) -> dict[str, Any]:
        """Return a structured snapshot dict (for integration with aeon/lantern).

        Combines the visual profiling data with AFET metastability checks,
        suitable for feeding into both the profiling generator and the
        sonification layer.
        """
        if metrics is None:
            metrics = FieldMetrics()

        metastability = self.afet.check_metastability(metrics.entropy_density)
        beta_analysis = {}
        for domain, beta in metrics.beta_values.items():
            beta_analysis[domain] = {
                "beta": beta,
                "peclet": self.afet.beta_to_peclet(beta),
                "predicted": self.afet.predict_beta(
                    self.afet._estimate_dimension_from_beta(beta)
                ),
            }

        return {
            "layer": "visual_profiling_hub",
            "quad_layer_index": 4,
            "metrics": {
                "sigma_phi_deviation": metrics.sigma_phi_deviation,
                "s_crit_proximity": metrics.s_crit_proximity,
                "entropy_density": metrics.entropy_density,
            },
            "metastability": metastability,
            "beta_analysis": beta_analysis,
            "label": metrics.label,
        }

    def generate_svg(
        self,
        metrics: FieldMetrics | None = None,
        output_path: str | Path | None = None,
    ) -> Path:
        """Render the profiling snapshot as vector SVG.

        Uses the same matplotlib pipeline as ``generate_snapshot`` but
        outputs SVG for vector-sharp rendering in documents and LLM contexts.

        Parameters
        ----------
        metrics : FieldMetrics, optional
            Field state to visualize.
        output_path : str | Path, optional
            Defaults to ``examples/profiling_snapshot.svg``.

        Returns
        -------
        Path
            Path to the saved SVG file.
        """
        if metrics is None:
            metrics = FieldMetrics()

        if output_path is None:
            output_path = Path(__file__).parent / "examples" / "profiling_snapshot.svg"
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        bg = self.symbols.get("background", "#000000")
        fig, ax = plt.subplots(figsize=self.figsize, facecolor=bg)
        ax.set_facecolor(bg)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")

        self._draw_phi_radials(ax)
        self._draw_sigma_halo(ax, metrics)
        self._draw_frame_collapse_ring(ax, metrics)
        self._draw_beta_domains(ax, metrics)
        self._draw_nucleus(ax)
        self._draw_title(ax, metrics)

        fig.savefig(
            str(output_path),
            format="svg",
            bbox_inches="tight",
            facecolor=bg,
            edgecolor="none",
        )
        plt.close(fig)
        logger.info("SVG snapshot saved to %s", output_path)
        return output_path

    def generate_interactive(
        self,
        metrics: FieldMetrics | None = None,
        output_path: str | Path | None = None,
    ) -> Path:
        """Render an interactive Plotly HTML snapshot of the AFET field state.

        Requires ``plotly`` to be installed.  Raises ``ImportError`` if missing.

        Parameters
        ----------
        metrics : FieldMetrics, optional
            Field state to visualize.
        output_path : str | Path, optional
            Defaults to ``examples/profiling_interactive.html``.

        Returns
        -------
        Path
            Path to the saved HTML file.
        """
        if not _PLOTLY_AVAILABLE:
            raise ImportError(
                "plotly is required for interactive snapshots: pip install plotly"
            )

        if metrics is None:
            metrics = FieldMetrics()

        if output_path is None:
            output_path = Path(__file__).parent / "examples" / "profiling_interactive.html"
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        beta_crit = self.afet.constants.BETA_CRITICAL
        domain_syms = self.symbols.get("domains", {})

        fig = go.Figure()

        # Phi-scaling radial lines
        phi_sym = self.symbols.get("phi_scaling", {})
        n_lines = phi_sym.get("n_lines", 8)
        for i in range(n_lines):
            angle = i * (2 * np.pi / n_lines)
            fig.add_trace(go.Scatter(
                x=[0.5, 0.5 + 0.48 * np.cos(angle)],
                y=[0.5, 0.5 + 0.48 * np.sin(angle)],
                mode="lines",
                line={"color": "rgba(255,255,255,0.15)", "width": 1.5},
                hoverinfo="skip",
                showlegend=False,
            ))

        # Sigma-phi halo (approximated as scatter circle)
        sigma_sym = self.symbols.get("sigma_phi", {})
        halo_r = sigma_sym.get("radius_factor", 0.32) * (
            1.0 - min(metrics.sigma_phi_deviation, 0.95)
        )
        halo_theta = np.linspace(0, 2 * np.pi, 60)
        fig.add_trace(go.Scatter(
            x=0.5 + halo_r * np.cos(halo_theta),
            y=0.5 + halo_r * np.sin(halo_theta),
            mode="lines",
            fill="toself",
            fillcolor="rgba(0,255,0,0.12)",
            line={"color": "rgba(0,255,0,0.35)", "width": 2},
            name="sigma_Phi halo",
            hoverinfo="text",
            hovertext=f"sigma_Phi deviation: {metrics.sigma_phi_deviation:.3f}",
        ))

        # Frame-collapse warning ring
        if metrics.s_crit_proximity >= 0.3:
            ring_theta = np.linspace(0, 2 * np.pi, 60)
            alpha = min(0.6 * metrics.s_crit_proximity, 1.0)
            fig.add_trace(go.Scatter(
                x=0.5 + 0.45 * np.cos(ring_theta),
                y=0.5 + 0.45 * np.sin(ring_theta),
                mode="lines",
                line={"color": f"rgba(255,68,68,{alpha})", "width": 3, "dash": "dash"},
                name="S_crit warning",
                hoverinfo="text",
                hovertext=f"S_crit proximity: {metrics.s_crit_proximity:.2f}",
            ))

        # Beta-domain hexagons
        domains = list(metrics.beta_values.items())
        n = len(domains)
        if n > 0:
            angles = np.linspace(0, 2 * np.pi, n, endpoint=False) - np.pi / 2
            xs, ys, texts, sizes, colors = [], [], [], [], []
            for i, (name, beta) in enumerate(domains):
                r = 0.15 + (beta / beta_crit) * 0.25
                x = 0.5 + r * np.cos(angles[i])
                y = 0.5 + r * np.sin(angles[i])
                xs.append(x)
                ys.append(y)
                texts.append(name[:3].upper())
                sizes.append(12 + (beta / beta_crit) * 30)
                sym = domain_syms.get(name, {})
                colors.append(sym.get("color", "#FFFFFF"))

            fig.add_trace(go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                marker={
                    "size": sizes,
                    "color": colors,
                    "symbol": "hexagon",
                    "line": {"color": "white", "width": 1.2},
                },
                text=texts,
                textfont={"color": "white", "size": 10},
                textposition="middle center",
                customdata=[
                    f"{name}: beta={beta:.1f}, Pe={beta/beta_crit:.3f}"
                    for name, beta in domains
                ],
                hovertemplate="%{customdata}<extra></extra>",
                name="beta domains",
            ))

        # Nullkern nucleus
        nuc_sym = self.symbols.get("beta_critical", {})
        fig.add_trace(go.Scatter(
            x=[0.5],
            y=[0.5],
            mode="markers",
            marker={
                "size": 14,
                "color": nuc_sym.get("color", "#FFFFFF"),
                "line": {"color": "white", "width": 2},
            },
            name="Nullkern",
            hoverinfo="text",
            hovertext=f"beta_critical = {beta_crit}",
        ))

        # Layout
        sigma = self.afet.constants.SIGMA_PHI
        title = "AFET Field State \u2022 Profiling Tafel"
        if metrics.label:
            title += f" \u2022 {metrics.label}"

        fig.update_layout(
            title={
                "text": (
                    f"{title}<br>"
                    f"<sub>\u03c3\u03a6={sigma:.4f}  "
                    f"\u0394\u03c3={metrics.sigma_phi_deviation:.3f}  "
                    f"S_crit prox={metrics.s_crit_proximity:.2f}</sub>"
                ),
                "font": {"color": "white"},
            },
            plot_bgcolor="black",
            paper_bgcolor="black",
            xaxis={
                "visible": False,
                "range": [-0.05, 1.05],
                "scaleanchor": "y",
            },
            yaxis={
                "visible": False,
                "range": [-0.05, 1.05],
            },
            legend={"font": {"color": "white"}},
            width=700,
            height=700,
        )

        fig.write_html(str(output_path))
        logger.info("Interactive snapshot saved to %s", output_path)
        return output_path

    # ------------------------------------------------------------------
    # Internal drawing methods
    # ------------------------------------------------------------------

    def _draw_sigma_halo(self, ax: plt.Axes, metrics: FieldMetrics) -> None:
        """Draw the sigma_Phi metastability halo (central green ring)."""
        sym = self.symbols.get("sigma_phi", {})
        base_radius = sym.get("radius_factor", 0.32)
        # Radius shrinks as deviation increases
        radius = base_radius * (1.0 - min(metrics.sigma_phi_deviation, 0.95))
        color = sym.get("color", "#00FF00")
        alpha = sym.get("alpha", 0.25)

        halo = Circle(
            (0.5, 0.5),
            radius,
            facecolor=color,
            edgecolor=color,
            alpha=alpha,
            linewidth=2,
        )
        ax.add_patch(halo)

    def _draw_frame_collapse_ring(self, ax: plt.Axes, metrics: FieldMetrics) -> None:
        """Draw warning ring when approaching S_crit."""
        if metrics.s_crit_proximity < 0.3:
            return  # No warning needed

        sym = self.symbols.get("frame_collapse", {})
        color = sym.get("color", "#FF4444")
        # Alpha intensifies as proximity increases
        alpha = sym.get("alpha", 0.6) * metrics.s_crit_proximity

        ring = Circle(
            (0.5, 0.5),
            0.45,
            facecolor="none",
            edgecolor=color,
            alpha=min(alpha, 1.0),
            linewidth=3,
            linestyle="--",
        )
        ax.add_patch(ring)

    def _draw_beta_domains(self, ax: plt.Axes, metrics: FieldMetrics) -> None:
        """Draw beta-hierarchy hexagons for each domain."""
        domain_syms = self.symbols.get("domains", {})
        cmap = plt.get_cmap(self.symbols.get("colormap", "plasma"))
        beta_crit = self.afet.constants.BETA_CRITICAL

        domains = list(metrics.beta_values.items())
        n = len(domains)
        if n == 0:
            return

        angles = np.linspace(0, 2 * np.pi, n, endpoint=False) - np.pi / 2

        for i, (name, beta) in enumerate(domains):
            # Radial position scales with beta / beta_crit
            r = 0.15 + (beta / beta_crit) * 0.25
            x = 0.5 + r * np.cos(angles[i])
            y = 0.5 + r * np.sin(angles[i])

            # Size proportional to beta
            hex_radius = 0.02 + (beta / beta_crit) * 0.04

            # Color from symbol map or colormap
            sym = domain_syms.get(name, {})
            color = sym.get("color", cmap(beta / beta_crit))

            hexagon = RegularPolygon(
                (x, y),
                numVertices=6,
                radius=hex_radius,
                facecolor=color,
                edgecolor="white",
                linewidth=1.2,
                alpha=0.85,
            )
            ax.add_patch(hexagon)

            # Domain label
            label = name[:3].upper()
            ax.text(
                x,
                y,
                label,
                color="white",
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
            )

    def _draw_nucleus(self, ax: plt.Axes) -> None:
        """Draw the central Nullkern point (beta_critical anchor)."""
        sym = self.symbols.get("beta_critical", {})
        ax.scatter(
            0.5,
            0.5,
            s=sym.get("size", 120),
            color=sym.get("color", "#FFFFFF"),
            marker=sym.get("marker", "o"),
            edgecolors="white",
            linewidth=1.5,
            zorder=10,
        )

    def _draw_phi_radials(self, ax: plt.Axes) -> None:
        """Draw fractal radial lines (Phi-scaling / frame principle)."""
        sym = self.symbols.get("phi_scaling", {})
        n_lines = sym.get("n_lines", 8)
        color = sym.get("color", "#FFFFFF")
        alpha = sym.get("alpha", 0.15)
        lw = sym.get("linewidth", 1.5)

        for i in range(n_lines):
            angle = i * (2 * np.pi / n_lines)
            ax.plot(
                [0.5, 0.5 + 0.48 * np.cos(angle)],
                [0.5, 0.5 + 0.48 * np.sin(angle)],
                color=color,
                alpha=alpha,
                linewidth=lw,
            )

    def _draw_title(self, ax: plt.Axes, metrics: FieldMetrics) -> None:
        """Draw snapshot title with optional label."""
        title = "AFET Field State \u2022 Profiling Tafel"
        if metrics.label:
            title += f" \u2022 {metrics.label}"
        ax.set_title(title, color="white", pad=20, fontsize=13)

        # Subtitle with key metrics
        sigma = self.afet.constants.SIGMA_PHI
        subtitle = (
            f"\u03c3\u03a6={sigma:.4f}  "
            f"\u0394\u03c3={metrics.sigma_phi_deviation:.3f}  "
            f"S_crit prox={metrics.s_crit_proximity:.2f}"
        )
        ax.text(
            0.5,
            -0.02,
            subtitle,
            color="gray",
            ha="center",
            fontsize=9,
            transform=ax.transAxes,
        )
