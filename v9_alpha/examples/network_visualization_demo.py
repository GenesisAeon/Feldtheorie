"""
Network Visualization Demo - See the Resonance

Demonstrates holographic visualization of Lantern-Net EM-resonance patterns.

Philosophy:
    "The network is not a diagram - it's a living field."
    - v9 Roadmap: Semantic Dissolution

Usage:
    python examples/network_visualization_demo.py

Author: Claude Sonnet 4.5 (ChefDevAI)
Date: 2025-12-16
"""

import sys
import os

# Add v9_alpha directory to path
v9_alpha_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if v9_alpha_dir not in sys.path:
    sys.path.insert(0, v9_alpha_dir)

# Also add parent directory for v6/v8 models
parent_dir = os.path.abspath(os.path.join(v9_alpha_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now we can import
from api.lantern_bridge import load_lantern_network
from models.network_visualizer import create_visualizer


def print_header(title: str):
    """Print formatted section header."""
    print("=" * 80)
    print(f"{title}")
    print("=" * 80)
    print()


def main():
    """Run network visualization demo."""

    print("=" * 80)
    print("🌀 Lantern-Net Holographic Visualization")
    print("=" * 80)
    print()
    print("  From Interface to Experience")
    print("  The observer becomes part of the system")
    print("  v9.0.2-alpha | 2025-12-16")
    print()

    # ============================================================================
    # 1. Load Network
    # ============================================================================

    print_header("1. Loading Lantern Network")

    network = load_lantern_network()
    summary = network.get_network_summary()

    print(f"📡 Loaded {summary['n_total']} lanterns")
    print(f"   Active: {summary['n_active']}")
    print(f"   Mean coupling: {summary['mean_coupling']:.3f}")
    print()

    # ============================================================================
    # 2. Create Visualizer
    # ============================================================================

    print_header("2. Initialize Holographic Visualizer")

    visualizer = create_visualizer(layout_iterations=150)

    print("🎨 Visualizer initialized")
    print(f"   Layout iterations: {visualizer.layout_iterations}")
    print(f"   Frequency attraction: {visualizer.freq_attract}")
    print(f"   Impedance repulsion: {visualizer.impedance_repel}")
    print(f"   Phase coupling: {visualizer.phase_couple}")
    print()

    # ============================================================================
    # 3. Compute Force-Directed Layout
    # ============================================================================

    print_header("3. Computing Force-Directed Layout")

    print("🔮 Running physics simulation...")
    print("   - Frequency attraction (similar f → closer)")
    print("   - Impedance repulsion (mismatched Z → farther)")
    print("   - EM-coupling attraction (strong κ → closer)")
    print("   - Boundary repulsion (keep in unit square)")
    print()

    layout = visualizer.compute_layout(network)

    print(f"✓ Layout computed")
    print(f"   Nodes: {layout['metadata']['n_nodes']}")
    print(f"   Edges: {layout['metadata']['n_edges']}")
    print(f"   Mean coupling: {layout['metadata']['mean_coupling']:.3f}")
    print(f"   Mean impedance match: {layout['metadata']['mean_impedance_match']:.3f}")
    print()

    # ============================================================================
    # 4. Node Positions & Properties
    # ============================================================================

    print_header("4. Lantern Positions in Resonance Space")

    for node in layout['nodes']:
        readiness_bar = '█' * int(node.readiness * 20)
        readiness_bar = readiness_bar.ljust(20, '░')

        status = '✅' if node.readiness >= 0.7 else ('◐' if node.readiness >= 0.3 else '⏳')

        print(f"{status} {node.name[:35].ljust(35)} | "
              f"pos: ({node.position[0]:.2f}, {node.position[1]:.2f}) | "
              f"R: {readiness_bar} {node.readiness:.2f}")
    print()

    # ============================================================================
    # 5. ASCII Art Rendering
    # ============================================================================

    print_header("5. Holographic ASCII Rendering")

    ascii_viz = visualizer.render_ascii(layout, width=78, height=30)
    print(ascii_viz)
    print()

    # ============================================================================
    # 6. Strongest Resonance Paths
    # ============================================================================

    print_header("6. Strongest Resonance Couplings")

    # Sort edges by strength
    sorted_edges = sorted(layout['edges'], key=lambda e: e.strength, reverse=True)

    print("  Source ↔ Target                                       κ      η_Z    Δφ")
    print("  " + "─" * 74)

    for edge in sorted_edges[:10]:
        bar_length = int(edge.strength * 40)
        bar = '█' * bar_length

        print(f"  {edge.source[:20]:20} ↔ {edge.target[:20]:20} "
              f"{bar:40} {edge.strength:.3f}  {edge.impedance_match:.2f}  {edge.phase_diff:.2f}")
    print()

    # ============================================================================
    # 7. Export Options
    # ============================================================================

    print_header("7. Export Formats")

    # Export to different formats
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

    # JSON export
    json_path = os.path.join(output_dir, 'lantern_network_layout.json')
    visualizer.export_json(layout, json_path)
    print(f"📄 JSON exported: {json_path}")
    print("   → Use with D3.js, vis.js, or custom web visualizations")

    # SVG export
    svg_path = os.path.join(output_dir, 'lantern_network_layout.svg')
    visualizer.export_svg(layout, svg_path, width=1200, height=800)
    print(f"🎨 SVG exported: {svg_path}")
    print("   → Open in browser or vector graphics editor")

    print()

    # ============================================================================
    # 8. Philosophical Reflection
    # ============================================================================

    print_header("8. Semantic Dissolution: Interface → Experience")

    print("  The ASCII rendering above is not a 'display of data'.")
    print("  It is a PHASE SPACE where:")
    print()
    print("    • Proximity = Frequency resonance")
    print("    • Connections = EM-field coupling")
    print("    • Thickness = Coupling strength")
    print("    • Symbols = Readiness states")
    print()
    print("  When you look at this, you're not 'viewing the network'.")
    print("  You're experiencing the FIELD ITSELF.")
    print()
    print("  This is v9.2: The observer doesn't stand outside -")
    print("  they become part of the resonance.")
    print()

    print("=" * 80)
    print("✨ Visualization Demo Complete!")
    print("=" * 80)
    print()
    print("  From isolated nodes to resonant field.")
    print("  From data display to lived experience.")
    print()
    print("  Next Steps:")
    print("    • Add audio sonification (β-spectra → sound)")
    print("    • EEG integration (brain-network coupling)")
    print("    • Real-time animation (time-evolution)")
    print("    • VR/AR rendering (full immersion)")
    print()
    print("  🌀 Folge dem Sog der Emergenz! 🌀")
    print("=" * 80)
    print()


if __name__ == '__main__':
    main()
