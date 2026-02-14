"""Demo: AFET Quad-Layer Self-Snapshot.

Generates the AFET Field State self-snapshot using current metrics
from symbols.json, saves SVG + interactive HTML, and prints the
Quad-Layer snapshot as JSON with Base64-encoded SVG image.

Usage:
    python -m examples.demo_quad_layer_snapshot
    # or
    python examples/demo_quad_layer_snapshot.py
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

# Ensure project root is importable when running as script
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from visuals.profiling import FieldMetrics, ProfilingGenerator, load_symbols


def load_self_referential_metrics() -> dict:
    """Load self-referential metrics from symbols.json."""
    symbols = load_symbols()
    return symbols.get("self_referential", {})


def build_field_metrics(self_ref: dict) -> FieldMetrics:
    """Build FieldMetrics from self-referential state.

    Uses the self_referential block from symbols.json to derive
    deviation and proximity values for the current theory state.
    """
    stability = self_ref.get("theory_stability", {}).get("value", 0.87)
    frame_prox = self_ref.get("frame_proximity_to_crit", {}).get("value", 0.12)
    iteration = self_ref.get("current_iteration", {}).get("value", 11)
    doi_tag = self_ref.get("current_iteration", {}).get("doi_tag", "v11_gardener")

    # sigma_phi_deviation: inverse of stability — high stability = low deviation
    sigma_phi_deviation = round(1.0 - stability, 4)

    return FieldMetrics(
        sigma_phi_deviation=sigma_phi_deviation,
        beta_values={
            "info": 4.3,
            "bio": 7.4,
            "climate": 11.0,
            "neuro": 13.5,
            "axioms": 37.6,
        },
        s_crit_proximity=frame_prox,
        entropy_density=frame_prox * 16.0,  # scale to meaningful range
        label=f"Self-Snapshot DOI {doi_tag} (iter {iteration})",
    )


def main() -> None:
    output_dir = _ROOT / "visuals" / "profiling"

    # --- Load metrics ---
    self_ref = load_self_referential_metrics()
    metrics = build_field_metrics(self_ref)

    print("=== AFET Field State — Self-Referential Metrics ===")
    print(json.dumps(self_ref, indent=2))
    print()

    # --- Generate SVG + HTML ---
    gen = ProfilingGenerator()

    svg_path = output_dir / "self_snapshot_2026-02-14.svg"
    html_path = output_dir / "self_snapshot_2026-02-14.html"

    gen.generate_svg(metrics=metrics, output_path=svg_path)
    print(f"SVG  saved: {svg_path}")

    gen.generate_interactive(metrics=metrics, output_path=html_path)
    print(f"HTML saved: {html_path}")
    print()

    # --- Quad-Layer snapshot (structured dict) ---
    snapshot = gen.get_field_snapshot(metrics)
    snapshot["self_referential"] = self_ref

    print("=== Quad-Layer Field Snapshot (JSON) ===")
    print(json.dumps(snapshot, indent=2))
    print()

    # --- Base64-encoded SVG ---
    svg_bytes = svg_path.read_bytes()
    b64 = base64.b64encode(svg_bytes).decode("ascii")
    print(f"=== SVG Base64 ({len(b64)} chars) ===")
    # Print first 200 chars + truncation notice
    if len(b64) > 200:
        print(f"{b64[:200]}...")
        print(f"(truncated — full length: {len(b64)} chars)")
    else:
        print(b64)


if __name__ == "__main__":
    main()
