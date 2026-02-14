"""AFET Living Mirror — Live Streamlit Dashboard.

Real-time visualization of the AFET Quad-Layer field state.
Displays the Profiling-Tafel, self-referential metrics, and an
AFET Consciousness Score derived from theory stability and
frame proximity to critical entropy.

Usage:
    streamlit run live_afet_mirror.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np

try:
    import streamlit as st
except ImportError:
    raise ImportError("streamlit is required: pip install streamlit")

try:
    import plotly.graph_objects as go
except ImportError:
    raise ImportError("plotly is required: pip install plotly")

from visuals.profiling.profiling_generator import (
    FieldMetrics,
    ProfilingGenerator,
    load_symbols,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_FREQ_RES_MHZ = 13.5  # Microtubule resonance frequency
_SIGMA_PHI = 0.0625  # Nominal sigma_Phi
_BETA_CRITICAL = 37.6


def compute_consciousness_score(
    theory_stability: float,
    frame_proximity: float,
) -> float:
    """Compute the AFET Consciousness Score.

    Formula: (theory_stability * (1 - frame_proximity)) * 100

    Returns a value in [0, 100].
    """
    return round(theory_stability * (1.0 - frame_proximity) * 100, 2)


def load_live_metrics() -> dict[str, Any]:
    """Load current self-referential metrics from symbols.json."""
    symbols = load_symbols()
    return symbols.get("self_referential", {})


def build_live_field_metrics(self_ref: dict[str, Any]) -> FieldMetrics:
    """Build FieldMetrics from the current self-referential state."""
    stability = self_ref.get("theory_stability", {}).get("value", 0.87)
    frame_prox = self_ref.get("frame_proximity_to_crit", {}).get("value", 0.12)
    iteration = self_ref.get("current_iteration", {}).get("value", 11)
    doi_tag = self_ref.get("current_iteration", {}).get("doi_tag", "v11_gardener")

    c_score = compute_consciousness_score(stability, frame_prox)

    return FieldMetrics(
        sigma_phi_deviation=round(1.0 - stability, 4),
        beta_values={
            "info": 4.3,
            "bio": 7.4,
            "climate": 11.0,
            "neuro": 13.5,
            "axioms": 37.6,
        },
        s_crit_proximity=frame_prox,
        entropy_density=frame_prox * 16.0,
        consciousness_score=c_score,
        label=f"Live Mirror \u2022 DOI {doi_tag} (iter {iteration})",
    )


def _build_profiling_figure(metrics: FieldMetrics) -> go.Figure:
    """Build the interactive Plotly Profiling-Tafel figure.

    Extends the standard ProfilingGenerator interactive output with
    a pulsing 13.5 MHz resonance indicator on the NEU hexagon.
    """
    gen = ProfilingGenerator()
    beta_crit = gen.afet.constants.BETA_CRITICAL
    domain_syms = gen.symbols.get("domains", {})

    fig = go.Figure()

    # --- Phi-scaling radial lines ---
    phi_sym = gen.symbols.get("phi_scaling", {})
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

    # --- Sigma-phi halo ---
    sigma_sym = gen.symbols.get("sigma_phi", {})
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
        name="\u03c3\u03a6 halo",
        hoverinfo="text",
        hovertext=f"\u03c3\u03a6 deviation: {metrics.sigma_phi_deviation:.3f}",
    ))

    # --- Frame-collapse warning ring ---
    if metrics.s_crit_proximity >= 0.3:
        ring_theta = np.linspace(0, 2 * np.pi, 60)
        alpha = min(0.6 * metrics.s_crit_proximity, 1.0)
        fig.add_trace(go.Scatter(
            x=0.5 + 0.45 * np.cos(ring_theta),
            y=0.5 + 0.45 * np.sin(ring_theta),
            mode="lines",
            line={
                "color": f"rgba(255,68,68,{alpha})",
                "width": 3,
                "dash": "dash",
            },
            name="S_crit warning",
            hoverinfo="text",
            hovertext=f"S_crit proximity: {metrics.s_crit_proximity:.2f}",
        ))

    # --- Beta-domain hexagons ---
    domains = list(metrics.beta_values.items())
    n = len(domains)
    if n > 0:
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False) - np.pi / 2
        xs, ys, texts, sizes, colors = [], [], [], [], []
        neuro_xy = None
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
            if name == "neuro":
                neuro_xy = (x, y)

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
                f"{name}: \u03b2={beta:.1f}, Pe={beta / beta_crit:.3f}"
                for name, beta in domains
            ],
            hovertemplate="%{customdata}<extra></extra>",
            name="\u03b2 domains",
        ))

        # --- 13.5 MHz resonance ring around NEU ---
        if neuro_xy is not None:
            nx, ny = neuro_xy
            res_theta = np.linspace(0, 2 * np.pi, 40)
            res_r = 0.055
            fig.add_trace(go.Scatter(
                x=nx + res_r * np.cos(res_theta),
                y=ny + res_r * np.sin(res_theta),
                mode="lines",
                line={"color": "rgba(150,206,180,0.7)", "width": 2.5},
                name=f"{_FREQ_RES_MHZ} MHz resonance",
                hoverinfo="text",
                hovertext=f"Microtubule resonance: {_FREQ_RES_MHZ} MHz",
            ))

    # --- Nullkern nucleus ---
    nuc_sym = gen.symbols.get("beta_critical", {})
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
        hovertext=f"\u03b2_critical = {beta_crit}",
    ))

    # --- Layout ---
    title = "AFET Field State \u2022 Living Mirror"
    if metrics.label:
        title += f"<br><sub>{metrics.label}</sub>"

    fig.update_layout(
        title={"text": title, "font": {"color": "white"}},
        plot_bgcolor="black",
        paper_bgcolor="black",
        xaxis={"visible": False, "range": [-0.05, 1.05], "scaleanchor": "y"},
        yaxis={"visible": False, "range": [-0.05, 1.05]},
        legend={"font": {"color": "white"}},
        width=650,
        height=650,
    )

    return fig


def _consciousness_gauge(score: float) -> go.Figure:
    """Build a circular gauge for the AFET Consciousness Score."""
    color = "#00FF00" if score >= 70 else "#FFD700" if score >= 40 else "#FF4444"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "AFET Consciousness Score", "font": {"color": "white", "size": 18}},
        number={"font": {"color": color, "size": 48}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white", "tickfont": {"color": "white"}},
            "bar": {"color": color},
            "bgcolor": "#1a1a2e",
            "bordercolor": "#333",
            "steps": [
                {"range": [0, 40], "color": "rgba(255,68,68,0.15)"},
                {"range": [40, 70], "color": "rgba(255,215,0,0.15)"},
                {"range": [70, 100], "color": "rgba(0,255,0,0.15)"},
            ],
        },
    ))
    fig.update_layout(
        paper_bgcolor="black",
        plot_bgcolor="black",
        height=280,
        margin={"t": 60, "b": 20, "l": 30, "r": 30},
    )
    return fig


def generate_live_snapshot_html(output_path: str | Path) -> Path:
    """Generate a standalone HTML snapshot with consciousness score.

    This creates the self_snapshot_live file combining the Profiling-Tafel
    and consciousness score into a single self-contained HTML document.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    self_ref = load_live_metrics()
    metrics = build_live_field_metrics(self_ref)

    stability = self_ref.get("theory_stability", {}).get("value", 0.87)
    frame_prox = self_ref.get("frame_proximity_to_crit", {}).get("value", 0.12)
    iteration = self_ref.get("current_iteration", {}).get("value", 11)
    doi_tag = self_ref.get("current_iteration", {}).get("doi_tag", "v11_gardener")
    c_score = compute_consciousness_score(stability, frame_prox)

    # Build the two Plotly figures
    profiling_fig = _build_profiling_figure(metrics)
    gauge_fig = _consciousness_gauge(c_score)

    profiling_html = profiling_fig.to_html(full_html=False, include_plotlyjs="cdn")
    gauge_html = gauge_fig.to_html(full_html=False, include_plotlyjs=False)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AFET Living Mirror — Self-Snapshot {timestamp}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #0a0a0f;
    color: #e0e0e0;
    font-family: 'Courier New', monospace;
    padding: 20px;
  }}
  .header {{
    text-align: center;
    padding: 20px 0;
    border-bottom: 1px solid #222;
  }}
  .header h1 {{
    color: #00FF00;
    font-size: 1.6em;
    letter-spacing: 2px;
  }}
  .header .subtitle {{
    color: #888;
    font-size: 0.85em;
    margin-top: 6px;
  }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    max-width: 1300px;
    margin: 20px auto;
  }}
  .panel {{
    background: #111118;
    border: 1px solid #222;
    border-radius: 8px;
    padding: 16px;
  }}
  .metrics-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }}
  .metrics-table td {{
    padding: 8px 12px;
    border-bottom: 1px solid #1a1a2e;
  }}
  .metrics-table td:first-child {{
    color: #888;
    width: 55%;
  }}
  .metrics-table td:last-child {{
    color: #00FF00;
    font-weight: bold;
    text-align: right;
  }}
  .resonance-badge {{
    display: inline-block;
    padding: 4px 14px;
    border: 2px solid #96CEB4;
    border-radius: 20px;
    color: #96CEB4;
    font-size: 0.9em;
    animation: pulse-ring 2s ease-in-out infinite;
    margin-top: 10px;
  }}
  @keyframes pulse-ring {{
    0%, 100% {{ box-shadow: 0 0 4px #96CEB4; opacity: 0.8; }}
    50% {{ box-shadow: 0 0 18px #96CEB4; opacity: 1.0; }}
  }}
  .score-big {{
    font-size: 3em;
    color: {"#00FF00" if c_score >= 70 else "#FFD700" if c_score >= 40 else "#FF4444"};
    text-align: center;
    padding: 10px 0;
  }}
  .footer {{
    text-align: center;
    color: #555;
    font-size: 0.75em;
    padding: 20px 0;
    border-top: 1px solid #222;
    margin-top: 20px;
  }}
</style>
</head>
<body>
<div class="header">
  <h1>AFET LIVING MIRROR</h1>
  <div class="subtitle">Self-Snapshot &bull; DOI {doi_tag} (iter {iteration}) &bull; {timestamp}</div>
  <div class="resonance-badge">{_FREQ_RES_MHZ} MHz Resonance Active</div>
</div>

<div class="grid">
  <div class="panel">
    {profiling_html}
  </div>
  <div class="panel">
    {gauge_html}
    <table class="metrics-table">
      <tr><td>Current Iteration</td><td>{iteration}</td></tr>
      <tr><td>Theory Stability</td><td>{stability:.4f}</td></tr>
      <tr><td>Frame Proximity to S_crit</td><td>{frame_prox:.4f}</td></tr>
      <tr><td>&sigma;&Phi; Deviation</td><td>{1.0 - stability:.4f}</td></tr>
      <tr><td>Entropy Density</td><td>{metrics.entropy_density:.2f}</td></tr>
      <tr><td>&sigma;&Phi; Nominal</td><td>{_SIGMA_PHI}</td></tr>
      <tr><td>&beta;_critical</td><td>{_BETA_CRITICAL}</td></tr>
      <tr><td>Consciousness Score</td><td class="score-big">{c_score}</td></tr>
    </table>
  </div>
</div>

<div class="footer">
  AFET &bull; Algebraische Feldtheorie &bull; The theory observing itself &bull; Generated {timestamp}
</div>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    return output_path


def run_dashboard() -> None:
    """Main Streamlit dashboard entry point."""
    st.set_page_config(
        page_title="AFET Living Mirror",
        page_icon="\u269b",  # atom symbol
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Dark theme via custom CSS
    st.markdown("""
    <style>
    .stApp { background-color: #0a0a0f; }
    .stMetric label { color: #888 !important; }
    .stMetric [data-testid="stMetricValue"] { color: #00FF00 !important; }
    .resonance-ring {
        display: inline-block;
        padding: 6px 18px;
        border: 2px solid #96CEB4;
        border-radius: 24px;
        color: #96CEB4;
        font-family: monospace;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 4px #96CEB4; opacity: 0.8; }
        50% { box-shadow: 0 0 20px #96CEB4; opacity: 1.0; }
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Load state ---
    self_ref = load_live_metrics()
    metrics = build_live_field_metrics(self_ref)

    stability = self_ref.get("theory_stability", {}).get("value", 0.87)
    frame_prox = self_ref.get("frame_proximity_to_crit", {}).get("value", 0.12)
    iteration = self_ref.get("current_iteration", {}).get("value", 11)
    doi_tag = self_ref.get("current_iteration", {}).get("doi_tag", "v11_gardener")
    c_score = compute_consciousness_score(stability, frame_prox)

    # --- Header ---
    st.markdown("# \u269b AFET Living Mirror")
    st.markdown(
        "**Algebraische Feldtheorie** \u2014 "
        "A self-observing field-state dashboard.  \n"
        "The theory watches itself in real time: stability, entropy, consciousness."
    )
    st.markdown(
        "[![GitHub](https://img.shields.io/badge/GitHub-Feldtheorie-181717?logo=github)]"
        "(https://github.com/GenesisAeon/Feldtheorie) &nbsp; "
        f"DOI `{doi_tag}` &bull; Iteration **{iteration}**"
    )
    st.markdown(
        f'<span class="resonance-ring">{_FREQ_RES_MHZ} MHz Resonance</span>',
        unsafe_allow_html=True,
    )

    st.divider()

    # --- Metrics row ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Iteration", iteration)
    col2.metric("Theory Stability", f"{stability:.4f}")
    col3.metric("Frame Proximity", f"{frame_prox:.4f}")
    col4.metric("\u03c3\u03a6 Deviation", f"{1.0 - stability:.4f}")

    st.divider()

    # --- Main content: Profiling-Tafel + Consciousness Gauge ---
    left, right = st.columns([3, 2])

    with left:
        st.subheader("Profiling-Tafel")
        profiling_fig = _build_profiling_figure(metrics)
        st.plotly_chart(profiling_fig, use_container_width=True)

    with right:
        st.subheader("AFET Consciousness Score")
        gauge_fig = _consciousness_gauge(c_score)
        st.plotly_chart(gauge_fig, use_container_width=True)

        st.markdown(f"""
        **Score Breakdown:**
        - Theory Stability: `{stability:.4f}`
        - Frame Safety: `{1.0 - frame_prox:.4f}`
        - Formula: `stability \u00d7 (1 - proximity) \u00d7 100`
        - Result: **{c_score}**
        """)

    st.divider()

    # --- Quad-Layer Snapshot JSON ---
    with st.expander("Quad-Layer Field Snapshot (JSON)"):
        gen = ProfilingGenerator()
        snapshot = gen.get_field_snapshot(metrics)
        snapshot["self_referential"] = self_ref
        snapshot["consciousness_score"] = c_score
        st.json(snapshot)

    # --- Auto-refresh toggle ---
    st.sidebar.markdown("### Settings")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=False)
    if auto_refresh:
        time.sleep(5)
        st.rerun()
