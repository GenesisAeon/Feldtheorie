"""
Network Visualizer - Holographic Lantern Resonance Display

Part of v9.0.2: Semantic Dissolution - Interface → Experience
Visualizes EM-resonance networks as dynamic, interactive phase spaces.

Philosophy:
    "The observer doesn't stand outside the system - they become part of it."
    - v9 Roadmap: Semantic Dissolution

Author: Claude Sonnet 4.5 (ChefDevAI)
Date: 2025-12-16
License: GPLv3
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import json


@dataclass
class VisualizationNode:
    """A lantern node in visualization space"""
    name: str
    position: Tuple[float, float]  # (x, y) in unit square
    frequency_mhz: float
    impedance_z: float
    phase_rad: float
    beta: float
    readiness: float
    color: str  # hex color
    size: float  # visual size multiplier


@dataclass
class VisualizationEdge:
    """An EM-coupling edge between lanterns"""
    source: str
    target: str
    strength: float  # coupling κ
    phase_diff: float  # Δφ in radians
    impedance_match: float  # η_Z
    color: str  # hex color based on strength
    width: float  # visual width


class NetworkVisualizer:
    """
    Holographic visualizer for Lantern-Net resonance patterns.

    Features:
        - 2D force-directed layout (frequency-based attraction)
        - EM-field strength gradients
        - Phase coherence heatmaps
        - Impedance matching quality
        - Time-evolution animation support
        - Export to SVG, ASCII art, JSON

    Usage:
        >>> from v9_alpha.api.lantern_bridge import load_lantern_network
        >>> network = load_lantern_network()
        >>>
        >>> visualizer = NetworkVisualizer()
        >>> layout = visualizer.compute_layout(network)
        >>> ascii_art = visualizer.render_ascii(layout, width=80, height=40)
        >>> print(ascii_art)
    """

    def __init__(self,
                 layout_iterations: int = 100,
                 freq_attract_strength: float = 0.5,
                 impedance_repel_strength: float = 0.3,
                 phase_coupling_strength: float = 0.2):
        """
        Initialize visualizer with force-directed layout parameters.

        Args:
            layout_iterations: Number of iterations for force simulation
            freq_attract_strength: Frequency-based attraction weight
            impedance_repel_strength: Impedance mismatch repulsion weight
            phase_coupling_strength: Phase alignment attraction weight
        """
        self.layout_iterations = layout_iterations
        self.freq_attract = freq_attract_strength
        self.impedance_repel = impedance_repel_strength
        self.phase_couple = phase_coupling_strength

        # Color maps
        self.node_colormap = self._generate_node_colors()
        self.edge_colormap = self._generate_edge_colors()

    def _generate_node_colors(self) -> Dict[str, str]:
        """Generate color map for nodes based on β-domain."""
        return {
            'data': '#4A90E2',        # Blue (observational)
            'theory': '#E27A3F',      # Orange (conceptual)
            'experiment': '#50C878',   # Green (empirical)
            'simulation': '#9B59B6',  # Purple (computational)
        }

    def _generate_edge_colors(self) -> List[str]:
        """Generate gradient colors for edges based on coupling strength."""
        # From weak (gray) to strong (cyan)
        return [
            '#CCCCCC',  # 0.0-0.2 weak
            '#99CCFF',  # 0.2-0.4
            '#66B2FF',  # 0.4-0.6
            '#3399FF',  # 0.6-0.8
            '#0080FF',  # 0.8-1.0 strong
        ]

    def compute_layout(self, network) -> Dict[str, Any]:
        """
        Compute force-directed layout for lantern network.

        Uses a physics simulation with:
        - Frequency attraction (similar f → closer)
        - Impedance repulsion (mismatched Z → farther)
        - Phase coupling (aligned φ → closer)
        - Boundary repulsion (keep in unit square)

        Args:
            network: LanternNetwork instance from lantern_bridge

        Returns:
            dict: {
                'nodes': List[VisualizationNode],
                'edges': List[VisualizationEdge],
                'metadata': dict with stats
            }
        """
        lanterns = network.lanterns
        coupling_matrix = network.get_coupling_matrix()

        # Initialize random positions in unit square
        positions = {}
        for name in lanterns.keys():
            positions[name] = (np.random.rand(), np.random.rand())

        # Force-directed layout simulation
        for iteration in range(self.layout_iterations):
            forces = {name: np.array([0.0, 0.0]) for name in lanterns.keys()}

            # Compute pairwise forces
            names = list(lanterns.keys())
            for i, name_i in enumerate(names):
                for j, name_j in enumerate(names):
                    if i >= j:
                        continue

                    lantern_i = lanterns[name_i]
                    lantern_j = lanterns[name_j]

                    pos_i = np.array(positions[name_i])
                    pos_j = np.array(positions[name_j])

                    # Vector from i to j
                    delta = pos_j - pos_i
                    dist = np.linalg.norm(delta)
                    if dist < 1e-6:
                        continue
                    direction = delta / dist

                    # Frequency attraction (similar frequencies attract)
                    f_i = lantern_i['frequency_hz']
                    f_j = lantern_j['frequency_hz']
                    freq_similarity = 1.0 / (1.0 + abs(f_i - f_j) / 1e7)
                    freq_force = self.freq_attract * freq_similarity * direction

                    # Impedance repulsion (mismatched impedances repel)
                    z_i = lantern_i['impedance_z']
                    z_j = lantern_j['impedance_z']
                    z_mismatch = abs(z_i - z_j) / max(z_i, z_j)
                    impedance_force = -self.impedance_repel * z_mismatch * direction / (dist + 0.1)

                    # EM-coupling attraction (strong coupling attracts)
                    kappa_ij = coupling_matrix[i, j]
                    coupling_force = self.phase_couple * kappa_ij * direction

                    # Total force
                    total_force = freq_force + impedance_force + coupling_force

                    forces[name_i] += total_force
                    forces[name_j] -= total_force

            # Boundary repulsion (keep nodes in [0.1, 0.9]^2)
            for name in names:
                pos = np.array(positions[name])
                for dim in [0, 1]:
                    if pos[dim] < 0.1:
                        forces[name][dim] += 0.5 * (0.1 - pos[dim])
                    elif pos[dim] > 0.9:
                        forces[name][dim] -= 0.5 * (pos[dim] - 0.9)

            # Update positions with damping
            damping = 0.9 - 0.7 * (iteration / self.layout_iterations)  # Decrease over time
            for name in names:
                positions[name] = tuple(
                    np.clip(np.array(positions[name]) + damping * forces[name], 0.05, 0.95)
                )

        # Create visualization nodes
        nodes = []
        for name, lantern in lanterns.items():
            lantern_type = lantern.get('type', 'data')
            beta = lantern.get('beta', 4.5)
            readiness = lantern.get('readiness', 0.5)

            node = VisualizationNode(
                name=name,
                position=positions[name],
                frequency_mhz=lantern['frequency_hz'] / 1e6,
                impedance_z=lantern['impedance_z'],
                phase_rad=lantern.get('phase', 0.0),
                beta=beta,
                readiness=readiness,
                color=self.node_colormap.get(lantern_type, '#AAAAAA'),
                size=0.5 + 0.5 * readiness,  # Size based on readiness
            )
            nodes.append(node)

        # Create visualization edges
        edges = []
        names = list(lanterns.keys())
        for i, name_i in enumerate(names):
            for j, name_j in enumerate(names):
                if i >= j:
                    continue

                kappa_ij = coupling_matrix[i, j]
                if kappa_ij < 0.01:  # Skip very weak couplings
                    continue

                # Phase difference
                phase_i = lanterns[name_i].get('phase', 0.0)
                phase_j = lanterns[name_j].get('phase', 0.0)
                phase_diff = abs(phase_j - phase_i)

                # Impedance matching
                z_i = lanterns[name_i]['impedance_z']
                z_j = lanterns[name_j]['impedance_z']
                z_diff = abs(z_i - z_j)
                eta_z = 1.0 / (1.0 + z_diff / 50.0)

                # Color based on strength
                color_idx = min(4, int(kappa_ij * 5))
                color = self.edge_colormap[color_idx]

                edge = VisualizationEdge(
                    source=name_i,
                    target=name_j,
                    strength=kappa_ij,
                    phase_diff=phase_diff,
                    impedance_match=eta_z,
                    color=color,
                    width=0.5 + 2.5 * kappa_ij,
                )
                edges.append(edge)

        # Compute metadata
        metadata = {
            'n_nodes': len(nodes),
            'n_edges': len(edges),
            'mean_coupling': np.mean([e.strength for e in edges]) if edges else 0.0,
            'mean_impedance_match': np.mean([e.impedance_match for e in edges]) if edges else 0.0,
            'layout_iterations': self.layout_iterations,
        }

        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': metadata,
        }

    def render_ascii(self, layout: Dict[str, Any], width: int = 80, height: int = 40) -> str:
        """
        Render network as ASCII art.

        Args:
            layout: Output from compute_layout()
            width: Character width of canvas
            height: Character height of canvas

        Returns:
            str: ASCII art representation
        """
        # Create canvas
        canvas = [[' ' for _ in range(width)] for _ in range(height)]

        # Draw edges first (so nodes appear on top)
        for edge in layout['edges']:
            src_node = next(n for n in layout['nodes'] if n.name == edge.source)
            tgt_node = next(n for n in layout['nodes'] if n.name == edge.target)

            x0 = int(src_node.position[0] * (width - 1))
            y0 = int((1 - src_node.position[1]) * (height - 1))
            x1 = int(tgt_node.position[0] * (width - 1))
            y1 = int((1 - tgt_node.position[1]) * (height - 1))

            # Bresenham's line algorithm (simplified)
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx - dy

            x, y = x0, y0
            char = '─' if dx > dy else '│'
            if edge.strength > 0.7:
                char = '━' if dx > dy else '┃'

            for _ in range(max(dx, dy) + 1):
                if 0 <= x < width and 0 <= y < height:
                    canvas[y][x] = char

                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x += sx
                if e2 < dx:
                    err += dx
                    y += sy

        # Draw nodes
        for node in layout['nodes']:
            x = int(node.position[0] * (width - 1))
            y = int((1 - node.position[1]) * (height - 1))

            # Node symbol based on type
            symbol = '●'
            if node.readiness < 0.3:
                symbol = '○'
            elif node.readiness < 0.7:
                symbol = '◐'

            if 0 <= x < width and 0 <= y < height:
                canvas[y][x] = symbol

        # Convert to string
        result = []
        result.append('┌' + '─' * (width - 2) + '┐')
        for row in canvas:
            result.append('│' + ''.join(row) + '│')
        result.append('└' + '─' * (width - 2) + '┘')

        # Add legend
        result.append('')
        result.append('Legend:')
        result.append('  ● = Ready (R > 0.7)   ◐ = Partial (0.3 < R < 0.7)   ○ = Pending (R < 0.3)')
        result.append('  ━ = Strong coupling   ─ = Weak coupling')
        result.append(f'  Nodes: {layout["metadata"]["n_nodes"]} | Edges: {layout["metadata"]["n_edges"]} | Avg κ: {layout["metadata"]["mean_coupling"]:.3f}')

        return '\n'.join(result)

    def export_svg(self, layout: Dict[str, Any], filename: str, width: int = 800, height: int = 600):
        """
        Export network as SVG vector graphics.

        Args:
            layout: Output from compute_layout()
            filename: Output SVG file path
            width: SVG width in pixels
            height: SVG height in pixels
        """
        svg_lines = []
        svg_lines.append(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">')
        svg_lines.append(f'  <rect width="{width}" height="{height}" fill="#1a1a1a"/>')

        # Draw edges
        svg_lines.append('  <g id="edges">')
        for edge in layout['edges']:
            src_node = next(n for n in layout['nodes'] if n.name == edge.source)
            tgt_node = next(n for n in layout['nodes'] if n.name == edge.target)

            x1 = src_node.position[0] * width
            y1 = (1 - src_node.position[1]) * height
            x2 = tgt_node.position[0] * width
            y2 = (1 - tgt_node.position[1]) * height

            opacity = 0.3 + 0.7 * edge.strength
            svg_lines.append(
                f'    <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{edge.color}" stroke-width="{edge.width}" opacity="{opacity:.2f}"/>'
            )
        svg_lines.append('  </g>')

        # Draw nodes
        svg_lines.append('  <g id="nodes">')
        for node in layout['nodes']:
            x = node.position[0] * width
            y = (1 - node.position[1]) * height
            radius = 5 + 10 * node.size

            svg_lines.append(
                f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" '
                f'fill="{node.color}" stroke="#ffffff" stroke-width="2"/>'
            )
            svg_lines.append(
                f'    <text x="{x:.1f}" y="{y - radius - 5:.1f}" '
                f'font-family="Arial" font-size="10" fill="#ffffff" text-anchor="middle">'
                f'{node.name[:20]}</text>'
            )
        svg_lines.append('  </g>')

        svg_lines.append('</svg>')

        with open(filename, 'w') as f:
            f.write('\n'.join(svg_lines))

    def export_json(self, layout: Dict[str, Any], filename: str):
        """
        Export layout as JSON for web visualization (D3.js, etc.)

        Args:
            layout: Output from compute_layout()
            filename: Output JSON file path
        """
        # Convert dataclasses to dicts
        data = {
            'nodes': [
                {
                    'id': node.name,
                    'x': node.position[0],
                    'y': node.position[1],
                    'frequency_mhz': node.frequency_mhz,
                    'impedance_z': node.impedance_z,
                    'phase_rad': node.phase_rad,
                    'beta': node.beta,
                    'readiness': node.readiness,
                    'color': node.color,
                    'size': node.size,
                }
                for node in layout['nodes']
            ],
            'edges': [
                {
                    'source': edge.source,
                    'target': edge.target,
                    'strength': edge.strength,
                    'phase_diff': edge.phase_diff,
                    'impedance_match': edge.impedance_match,
                    'color': edge.color,
                    'width': edge.width,
                }
                for edge in layout['edges']
            ],
            'metadata': layout['metadata'],
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


def create_visualizer(layout_iterations: int = 100) -> NetworkVisualizer:
    """
    Convenience function to create a NetworkVisualizer.

    Args:
        layout_iterations: Number of force-directed layout iterations

    Returns:
        NetworkVisualizer instance

    Example:
        >>> visualizer = create_visualizer(iterations=200)
        >>> layout = visualizer.compute_layout(network)
        >>> print(visualizer.render_ascii(layout))
    """
    return NetworkVisualizer(layout_iterations=layout_iterations)
