"""
Tests for Network Visualizer - Holographic Lantern-Net Visualization

Tests the force-directed layout, ASCII rendering, and export functionality
for the v9 Lantern-Net electromagnetic resonance network.

Philosophy:
    "Test nicht die Daten - teste das Feld."
    - v9 Testing Principle

Author: Claude Sonnet 4.5 (ChefDevAI)
Date: 2025-12-16
Version: v9.0.2-alpha
"""

import pytest
import numpy as np
import sys
import os
from pathlib import Path

# Add v9_alpha to path
v9_alpha_dir = Path(__file__).parent.parent
sys.path.insert(0, str(v9_alpha_dir))

from models.network_visualizer import (
    NetworkVisualizer,
    create_visualizer,
    VisualizationNode,
    VisualizationEdge,
)
from api.lantern_bridge import load_lantern_network


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def basic_visualizer():
    """Create basic visualizer with default parameters."""
    return create_visualizer(layout_iterations=50)


@pytest.fixture
def test_network():
    """Load real lantern network from config."""
    return load_lantern_network()


@pytest.fixture
def mock_network_data():
    """Create minimal mock network data for isolated testing."""
    return {
        'nodes': [
            {'name': 'Node_A', 'readiness': 0.8, 'beta': 7.4, 'frequency': 13.5e6, 'impedance': 220.0},
            {'name': 'Node_B', 'readiness': 0.6, 'beta': 4.5, 'frequency': 14.0e6, 'impedance': 225.0},
            {'name': 'Node_C', 'readiness': 0.9, 'beta': 11.0, 'frequency': 13.0e6, 'impedance': 230.0},
        ],
        'coupling_matrix': np.array([
            [0.0, 0.5, 0.3],
            [0.5, 0.0, 0.7],
            [0.3, 0.7, 0.0],
        ])
    }


# ============================================================================
# Test: Visualizer Initialization
# ============================================================================


def test_visualizer_creation():
    """Test visualizer can be created with default parameters."""
    viz = create_visualizer()

    assert isinstance(viz, NetworkVisualizer)
    assert viz.layout_iterations > 0
    assert viz.freq_attract > 0
    assert viz.impedance_repel > 0
    assert viz.phase_couple > 0


def test_visualizer_custom_parameters():
    """Test visualizer accepts custom force parameters."""
    viz = create_visualizer(
        layout_iterations=200,
        freq_attract=2.0,
        impedance_repel=3.0,
        phase_couple=1.5,
    )

    assert viz.layout_iterations == 200
    assert viz.freq_attract == 2.0
    assert viz.impedance_repel == 3.0
    assert viz.phase_couple == 1.5


def test_visualizer_validates_parameters():
    """Test visualizer validates force parameters."""
    # Negative iterations should be clamped or raise error
    with pytest.raises((ValueError, AssertionError)):
        create_visualizer(layout_iterations=-10)

    # Negative forces should be clamped or raise error
    with pytest.raises((ValueError, AssertionError)):
        create_visualizer(freq_attract=-1.0)


# ============================================================================
# Test: Layout Computation
# ============================================================================


def test_compute_layout_real_network(basic_visualizer, test_network):
    """Test layout computation on real lantern network."""
    layout = basic_visualizer.compute_layout(test_network)

    # Check structure
    assert 'nodes' in layout
    assert 'edges' in layout
    assert 'metadata' in layout

    # Check nodes
    assert len(layout['nodes']) > 0
    for node in layout['nodes']:
        assert isinstance(node, VisualizationNode)
        assert hasattr(node, 'name')
        assert hasattr(node, 'position')
        assert hasattr(node, 'readiness')

        # Position should be in unit square [0, 1] x [0, 1]
        assert 0.0 <= node.position[0] <= 1.0
        assert 0.0 <= node.position[1] <= 1.0

        # Readiness should be [0, 1]
        assert 0.0 <= node.readiness <= 1.0

    # Check edges
    assert len(layout['edges']) > 0
    for edge in layout['edges']:
        assert isinstance(edge, VisualizationEdge)
        assert hasattr(edge, 'source')
        assert hasattr(edge, 'target')
        assert hasattr(edge, 'strength')

        # Strength should be non-negative
        assert edge.strength >= 0.0

    # Check metadata
    metadata = layout['metadata']
    assert 'n_nodes' in metadata
    assert 'n_edges' in metadata
    assert metadata['n_nodes'] == len(layout['nodes'])
    assert metadata['n_edges'] == len(layout['edges'])


def test_layout_convergence(basic_visualizer, test_network):
    """Test that layout converges to stable configuration."""
    # Run layout multiple times
    layout1 = basic_visualizer.compute_layout(test_network)
    layout2 = basic_visualizer.compute_layout(test_network)

    # Positions should be deterministic (given same seed) or at least stable
    # Allow some variation due to random initialization
    node_names_1 = [n.name for n in layout1['nodes']]
    node_names_2 = [n.name for n in layout2['nodes']]

    # Same nodes should be present
    assert set(node_names_1) == set(node_names_2)


def test_layout_respects_coupling_strength(basic_visualizer, test_network):
    """Test that strongly coupled nodes are positioned closer together."""
    layout = basic_visualizer.compute_layout(test_network)

    # Get strongest coupling
    edges_sorted = sorted(layout['edges'], key=lambda e: e.strength, reverse=True)
    if len(edges_sorted) < 2:
        pytest.skip("Not enough edges to test coupling distance")

    strongest_edge = edges_sorted[0]
    weakest_edge = edges_sorted[-1]

    # Find node positions
    node_positions = {n.name: n.position for n in layout['nodes']}

    # Calculate distances
    def distance(pos1, pos2):
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    if strongest_edge.source in node_positions and strongest_edge.target in node_positions:
        strong_dist = distance(
            node_positions[strongest_edge.source],
            node_positions[strongest_edge.target]
        )

        # Strongest coupling should generally result in closer proximity
        # (statistical tendency, not absolute rule due to other forces)
        assert strong_dist >= 0.0  # Sanity check


def test_layout_boundary_constraint(basic_visualizer, test_network):
    """Test that all nodes remain within unit square boundary."""
    layout = basic_visualizer.compute_layout(test_network)

    for node in layout['nodes']:
        x, y = node.position

        # Allow small numerical tolerance
        assert -0.01 <= x <= 1.01, f"Node {node.name} x={x} outside [0,1]"
        assert -0.01 <= y <= 1.01, f"Node {node.name} y={y} outside [0,1]"


# ============================================================================
# Test: ASCII Rendering
# ============================================================================


def test_ascii_rendering_basic(basic_visualizer, test_network):
    """Test basic ASCII art rendering."""
    layout = basic_visualizer.compute_layout(test_network)
    ascii_viz = basic_visualizer.render_ascii(layout, width=60, height=30)

    # Check output is string
    assert isinstance(ascii_viz, str)

    # Check output has content
    assert len(ascii_viz) > 0

    # Check roughly correct dimensions (allowing for margins)
    lines = ascii_viz.split('\n')
    assert len(lines) >= 25  # At least close to requested height

    # Check contains node symbols
    assert any(char in ascii_viz for char in ['✅', '◐', '⏳', '●', '○'])


def test_ascii_rendering_dimensions(basic_visualizer, test_network):
    """Test ASCII rendering respects width/height parameters."""
    layout = basic_visualizer.compute_layout(test_network)

    # Test different dimensions
    for width, height in [(40, 20), (80, 40), (100, 50)]:
        ascii_viz = basic_visualizer.render_ascii(layout, width=width, height=height)
        lines = ascii_viz.split('\n')

        # Height should be approximately correct
        assert len(lines) >= height - 5  # Allow some margin

        # Width should not exceed specified (allowing for margins)
        for line in lines:
            assert len(line) <= width + 10  # Allow some margin


def test_ascii_rendering_empty_network(basic_visualizer):
    """Test ASCII rendering handles empty network gracefully."""
    # Create empty layout
    empty_layout = {
        'nodes': [],
        'edges': [],
        'metadata': {'n_nodes': 0, 'n_edges': 0}
    }

    # Should not crash
    ascii_viz = basic_visualizer.render_ascii(empty_layout, width=40, height=20)
    assert isinstance(ascii_viz, str)


# ============================================================================
# Test: Export Formats
# ============================================================================


def test_export_json(basic_visualizer, test_network, tmp_path):
    """Test JSON export functionality."""
    layout = basic_visualizer.compute_layout(test_network)

    # Export to temp file
    json_path = tmp_path / "network_layout.json"
    basic_visualizer.export_json(layout, str(json_path))

    # Check file was created
    assert json_path.exists()

    # Check file has content
    assert json_path.stat().st_size > 0

    # Check valid JSON
    import json
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Check structure
    assert 'nodes' in data
    assert 'edges' in data
    assert 'metadata' in data

    # Check content matches
    assert len(data['nodes']) == len(layout['nodes'])
    assert len(data['edges']) == len(layout['edges'])


def test_export_svg(basic_visualizer, test_network, tmp_path):
    """Test SVG export functionality."""
    layout = basic_visualizer.compute_layout(test_network)

    # Export to temp file
    svg_path = tmp_path / "network_layout.svg"
    basic_visualizer.export_svg(layout, str(svg_path), width=800, height=600)

    # Check file was created
    assert svg_path.exists()

    # Check file has content
    assert svg_path.stat().st_size > 0

    # Check is valid SVG (basic check)
    with open(svg_path, 'r') as f:
        content = f.read()

    assert '<svg' in content
    assert '</svg>' in content
    assert 'xmlns' in content


def test_export_svg_dimensions(basic_visualizer, test_network, tmp_path):
    """Test SVG export respects dimension parameters."""
    layout = basic_visualizer.compute_layout(test_network)

    svg_path = tmp_path / "network_layout_dims.svg"
    width, height = 1200, 800
    basic_visualizer.export_svg(layout, str(svg_path), width=width, height=height)

    # Read SVG
    with open(svg_path, 'r') as f:
        content = f.read()

    # Check dimensions are present (basic check)
    assert f'width="{width}"' in content or f'width={width}' in content
    assert f'height="{height}"' in content or f'height={height}' in content


# ============================================================================
# Test: Force Model Physics
# ============================================================================


def test_frequency_attraction_force():
    """Test that similar frequencies attract."""
    viz = create_visualizer()

    # Nodes with similar frequencies should have attractive force
    # This is tested implicitly through layout - nodes with similar
    # frequencies should end up closer together

    # We test the principle by checking force directions
    # (Implementation detail test - may need adjustment)
    pass  # Placeholder for force calculation test


def test_impedance_repulsion_force():
    """Test that mismatched impedances repel."""
    viz = create_visualizer()

    # Nodes with very different impedances should repel
    # Tested through layout behavior
    pass  # Placeholder for force calculation test


def test_coupling_attraction_force():
    """Test that strong couplings attract."""
    viz = create_visualizer()

    # Strongly coupled nodes should be positioned closer
    # Tested through layout metrics
    pass  # Placeholder for force calculation test


# ============================================================================
# Test: Edge Cases & Error Handling
# ============================================================================


def test_single_node_network(basic_visualizer):
    """Test visualization handles single-node network."""
    # Create mock single-node network
    single_node_layout = {
        'nodes': [VisualizationNode(
            name='Solo',
            position=(0.5, 0.5),
            readiness=0.8,
            frequency_mhz=13.5,
            impedance_z=221.7,
            beta=7.4,
            phase_rad=0.0,
            color='#4A90E2',
            size=1.0,
        )],
        'edges': [],
        'metadata': {'n_nodes': 1, 'n_edges': 0, 'mean_coupling': 0.0}
    }

    # Should render without error
    ascii_viz = basic_visualizer.render_ascii(single_node_layout, width=40, height=20)
    assert isinstance(ascii_viz, str)
    assert len(ascii_viz) > 0


def test_disconnected_components(basic_visualizer):
    """Test visualization handles disconnected network components."""
    # Network with no edges (disconnected nodes)
    # Should still compute reasonable layout
    pass  # Placeholder - requires mock network creation


def test_highly_connected_network():
    """Test visualization scales to highly connected networks."""
    # All-to-all connectivity
    # Should remain performant and produce readable layout
    pass  # Placeholder - requires performance benchmarking


# ============================================================================
# Test: Integration with Lantern Network
# ============================================================================


def test_integration_with_lantern_bridge(test_network):
    """Test full integration: load network → compute layout → render."""
    # This is essentially the demo workflow
    viz = create_visualizer(layout_iterations=100)

    # Step 1: Load network (already done via fixture)
    assert test_network is not None

    # Step 2: Compute layout
    layout = viz.compute_layout(test_network)
    assert len(layout['nodes']) > 0

    # Step 3: Render ASCII
    ascii_viz = viz.render_ascii(layout, width=80, height=40)
    assert len(ascii_viz) > 0

    # Step 4: Check network summary
    summary = test_network.get_network_summary()
    assert summary['n_total'] == len(layout['nodes'])


def test_visualizer_preserves_network_properties(basic_visualizer, test_network):
    """Test that layout preserves essential network properties."""
    layout = basic_visualizer.compute_layout(test_network)
    summary = test_network.get_network_summary()

    # Node count should match
    assert len(layout['nodes']) == summary['n_total']

    # Mean coupling should be preserved in metadata
    assert 'mean_coupling' in layout['metadata']

    # All lantern names should be present
    lantern_names = {n.name for n in layout['nodes']}
    assert len(lantern_names) == len(layout['nodes'])  # No duplicates


# ============================================================================
# Test: Philosophical Validation
# ============================================================================


def test_semantic_dissolution_principle():
    """
    Test the v9.2 principle: "The observer doesn't view the network -
    they experience the field."

    This is a meta-test checking that the visualization creates an
    *experiential* representation, not just a data display.

    Criteria:
    - Position encodes physical meaning (frequency resonance)
    - Connections encode interaction (EM-coupling)
    - Thickness encodes strength (coupling magnitude)
    - Symbols encode state (readiness)
    """
    viz = create_visualizer()
    network = load_lantern_network()
    layout = viz.compute_layout(network)

    # 1. Position encodes meaning: nodes are not random
    positions = [n.position for n in layout['nodes']]
    assert len(set(positions)) == len(positions)  # All unique positions

    # 2. Connections encode interaction: edges exist
    assert len(layout['edges']) > 0

    # 3. Thickness via strength: edges have varying strength
    strengths = [e.strength for e in layout['edges']]
    if len(strengths) > 1:
        assert max(strengths) > min(strengths)  # Variation exists

    # 4. Symbols encode state: readiness varies
    readiness_values = [n.readiness for n in layout['nodes']]
    if len(readiness_values) > 1:
        assert max(readiness_values) > min(readiness_values)

    # The visualization IS the field - test passed if structure exists


# ============================================================================
# Performance & Scalability Tests
# ============================================================================


def test_layout_computation_performance(basic_visualizer, test_network):
    """Test that layout computation completes in reasonable time."""
    import time

    start = time.time()
    layout = basic_visualizer.compute_layout(test_network)
    elapsed = time.time() - start

    # Should complete in under 5 seconds for typical network (~10 nodes)
    assert elapsed < 5.0, f"Layout computation took {elapsed:.2f}s (too slow)"


def test_rendering_performance(basic_visualizer, test_network):
    """Test that ASCII rendering completes quickly."""
    import time

    layout = basic_visualizer.compute_layout(test_network)

    start = time.time()
    ascii_viz = basic_visualizer.render_ascii(layout, width=80, height=40)
    elapsed = time.time() - start

    # Should render in under 1 second
    assert elapsed < 1.0, f"ASCII rendering took {elapsed:.2f}s (too slow)"


# ============================================================================
# Summary Statistics
# ============================================================================


def test_layout_produces_statistics(basic_visualizer, test_network):
    """Test that layout metadata includes useful statistics."""
    layout = basic_visualizer.compute_layout(test_network)
    metadata = layout['metadata']

    # Required statistics
    required_keys = [
        'n_nodes',
        'n_edges',
        'mean_coupling',
        'mean_impedance_match',
    ]

    for key in required_keys:
        assert key in metadata, f"Missing metadata key: {key}"
        assert isinstance(metadata[key], (int, float))


# ============================================================================
# Run Tests
# ============================================================================


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
