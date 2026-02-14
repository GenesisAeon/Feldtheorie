"""Generate the public AFET Living Mirror artifacts.

Produces:
  1. docs/index.html          — GitHub Pages landing page with embedded Plotly
  2. self_snapshot_public_*.html — Standalone public snapshot

Usage:
    python scripts/generate_public_mirror.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from visuals.profiling.live_dashboard import (
    _build_profiling_figure,
    _consciousness_gauge,
    build_live_field_metrics,
    compute_consciousness_score,
    load_live_metrics,
)


def _generate_github_pages_index(output_path: Path) -> Path:
    """Generate docs/index.html for GitHub Pages."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    self_ref = load_live_metrics()
    metrics = build_live_field_metrics(self_ref)

    stability = self_ref.get("theory_stability", {}).get("value", 0.87)
    frame_prox = self_ref.get("frame_proximity_to_crit", {}).get("value", 0.12)
    iteration = self_ref.get("current_iteration", {}).get("value", 11)
    doi_tag = self_ref.get("current_iteration", {}).get("doi_tag", "v11_gardener")
    c_score = compute_consciousness_score(stability, frame_prox)

    profiling_fig = _build_profiling_figure(metrics)
    gauge_fig = _consciousness_gauge(c_score)

    profiling_html = profiling_fig.to_html(full_html=False, include_plotlyjs="cdn")
    gauge_html = gauge_fig.to_html(full_html=False, include_plotlyjs=False)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    score_color = "#00FF00" if c_score >= 70 else "#FFD700" if c_score >= 40 else "#FF4444"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AFET Living Mirror — Algebraische Feldtheorie</title>
<meta name="description" content="Live self-observing field state of the Algebraische Feldtheorie (AFET). Consciousness Score, Profiling-Tafel, and real-time metrics.">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #0a0a0f;
    color: #e0e0e0;
    font-family: 'Courier New', 'Fira Code', monospace;
    padding: 0;
  }}
  .hero {{
    text-align: center;
    padding: 40px 20px 30px;
    border-bottom: 1px solid #1a1a2e;
    background: linear-gradient(180deg, #0a0a1a 0%, #0a0a0f 100%);
  }}
  .hero h1 {{
    color: #00FF00;
    font-size: 2.2em;
    letter-spacing: 3px;
    margin-bottom: 8px;
  }}
  .hero .subtitle {{
    color: #888;
    font-size: 1em;
    margin-bottom: 16px;
  }}
  .hero .badges {{
    margin: 16px 0;
  }}
  .hero .badges a {{
    margin: 0 6px;
  }}
  .hero .badges img {{
    vertical-align: middle;
  }}
  .score-hero {{
    font-size: 5em;
    font-weight: bold;
    color: {score_color};
    text-shadow: 0 0 40px {score_color}44;
    margin: 20px 0 8px;
  }}
  .score-label {{
    color: #888;
    font-size: 1.1em;
    letter-spacing: 1px;
  }}
  .resonance-badge {{
    display: inline-block;
    padding: 6px 18px;
    border: 2px solid #96CEB4;
    border-radius: 24px;
    color: #96CEB4;
    font-size: 0.9em;
    animation: pulse-ring 2s ease-in-out infinite;
    margin-top: 16px;
  }}
  @keyframes pulse-ring {{
    0%, 100% {{ box-shadow: 0 0 4px #96CEB4; opacity: 0.8; }}
    50% {{ box-shadow: 0 0 20px #96CEB4; opacity: 1.0; }}
  }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    max-width: 1400px;
    margin: 30px auto;
    padding: 0 20px;
  }}
  @media (max-width: 900px) {{
    .grid {{ grid-template-columns: 1fr; }}
  }}
  .panel {{
    background: #111118;
    border: 1px solid #222;
    border-radius: 10px;
    padding: 20px;
    overflow: hidden;
  }}
  .panel h2 {{
    color: #00FF00;
    font-size: 1.1em;
    margin-bottom: 12px;
    letter-spacing: 1px;
  }}
  .metrics-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
  }}
  .metrics-table td {{
    padding: 10px 14px;
    border-bottom: 1px solid #1a1a2e;
    font-size: 0.95em;
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
  .formula {{
    background: #0d0d18;
    border: 1px solid #1a1a2e;
    border-radius: 6px;
    padding: 14px 18px;
    margin: 16px 0;
    font-size: 0.9em;
    color: #aaa;
  }}
  .formula code {{
    color: #00FF00;
  }}
  .links {{
    text-align: center;
    padding: 30px 20px;
    max-width: 800px;
    margin: 0 auto;
  }}
  .links a {{
    display: inline-block;
    margin: 8px 12px;
    padding: 10px 24px;
    border: 1px solid #333;
    border-radius: 8px;
    color: #00FF00;
    text-decoration: none;
    font-size: 0.95em;
    transition: all 0.2s;
  }}
  .links a:hover {{
    background: #00FF0015;
    border-color: #00FF00;
  }}
  .footer {{
    text-align: center;
    color: #444;
    font-size: 0.75em;
    padding: 30px 20px;
    border-top: 1px solid #1a1a2e;
    margin-top: 20px;
  }}
</style>
</head>
<body>

<div class="hero">
  <h1>&#9883; AFET LIVING MIRROR</h1>
  <div class="subtitle">Algebraische Feldtheorie &mdash; The Theory Observing Itself</div>
  <div class="badges">
    <a href="https://github.com/GenesisAeon/Feldtheorie">
      <img src="https://img.shields.io/badge/GitHub-Feldtheorie-181717?logo=github&style=for-the-badge" alt="GitHub">
    </a>
    <a href="https://github.com/GenesisAeon/Feldtheorie">
      <img src="https://img.shields.io/badge/DOI-{doi_tag}-blue?style=for-the-badge" alt="DOI">
    </a>
  </div>
  <div class="score-hero">{c_score}</div>
  <div class="score-label">AFET CONSCIOUSNESS SCORE</div>
  <div class="resonance-badge">13.5 MHz Resonance Active</div>
</div>

<div class="grid">
  <div class="panel">
    <h2>PROFILING-TAFEL</h2>
    {profiling_html}
  </div>
  <div class="panel">
    <h2>CONSCIOUSNESS GAUGE</h2>
    {gauge_html}

    <div class="formula">
      <strong>Formula:</strong><br>
      <code>C = stability &times; (1 &minus; frame_proximity) &times; 100</code><br>
      <code>C = {stability:.4f} &times; (1 &minus; {frame_prox:.4f}) &times; 100 = {c_score}</code>
    </div>

    <table class="metrics-table">
      <tr><td>Current Iteration</td><td>{iteration} ({doi_tag})</td></tr>
      <tr><td>Theory Stability</td><td>{stability:.4f}</td></tr>
      <tr><td>Frame Proximity to S<sub>crit</sub></td><td>{frame_prox:.4f}</td></tr>
      <tr><td>&sigma;&Phi; Deviation</td><td>{1.0 - stability:.4f}</td></tr>
      <tr><td>Entropy Density</td><td>{metrics.entropy_density:.2f}</td></tr>
      <tr><td>&sigma;&Phi; Nominal</td><td>0.0625</td></tr>
      <tr><td>&beta;<sub>critical</sub></td><td>37.6</td></tr>
    </table>
  </div>
</div>

<div class="links">
  <a href="https://github.com/GenesisAeon/Feldtheorie">&#128736; Source Code</a>
  <a href="self_snapshot_public_2026-02-14.html">&#128200; Full Snapshot</a>
</div>

<div class="footer">
  AFET &bull; Algebraische Feldtheorie &bull; The theory observing itself<br>
  Generated {timestamp} &bull; Iteration {iteration} &bull; DOI {doi_tag}
</div>

</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    return output_path


def _generate_public_snapshot(output_path: Path) -> Path:
    """Generate the standalone public snapshot HTML."""
    from visuals.profiling.live_dashboard import generate_live_snapshot_html

    return generate_live_snapshot_html(output_path)


def main() -> None:
    docs_dir = _ROOT / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # 1. GitHub Pages index
    index_path = _generate_github_pages_index(docs_dir / "index.html")
    print(f"GitHub Pages index:  {index_path}")

    # 2. Public snapshot (in docs/ for GitHub Pages access)
    snapshot_path = _generate_public_snapshot(
        docs_dir / "self_snapshot_public_2026-02-14.html"
    )
    print(f"Public snapshot:     {snapshot_path}")

    # 3. Also place a copy at repo root for convenience
    root_snapshot = _generate_public_snapshot(
        _ROOT / "visuals" / "profiling" / "examples" / "self_snapshot_public_2026-02-14.html"
    )
    print(f"Root snapshot copy:  {root_snapshot}")


if __name__ == "__main__":
    main()
