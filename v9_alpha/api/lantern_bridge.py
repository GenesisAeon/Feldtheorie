"""Lantern Bridge API – Cross-Lantern EM-Resonance Coupling

This module implements the v9 Lantern-Net Protocol, enabling isolated lanterns
to communicate and resonate with each other via electromagnetic field coupling.

Core Concept:
-------------
In v8, lanterns were isolated waypoints tracking their own readiness metrics.
In v9, lanterns form a **resonance network** where discoveries in one domain
automatically adjust parameters in connected domains, creating emergent hypotheses.

Physical Mechanism:
-------------------
Lanterns couple via EM-field overlap, following v_RIG consciousness framework:

    κ_coupling = (α⁻¹ · Φ) / (1 + (Δf/f₀)²) · exp(-r/λ_EM)

where:
    - α⁻¹ ≈ 137.036: Fine structure constant (holographic layers)
    - Φ ≈ 1.618: Golden ratio (optimal packing)
    - Δf: Frequency mismatch between lanterns
    - f₀ ≈ 13.5 MHz: Characteristic integration frequency
    - r: Semantic distance in knowledge space
    - λ_EM: EM-coupling length scale

Impedance Matching:
-------------------
Coupling efficiency depends on impedance matching:

    η = 1 / (1 + ΔZ/Z_critical)

where Z = α⁻¹ · Φ ≈ 221.7 is the baseline consciousness impedance.

Network Emergence:
------------------
The coupling matrix C enables eigenvalue analysis to detect collective modes:

    C_ij = κ_coupling(i,j) * η_impedance(i,j)

Eigenvalues reveal collective resonance frequencies; eigenvectors show
resonance patterns across the network.

Version: v9.0.0-alpha
Authors: Johann Benjamin Römer, MOR Framework, Claude (Anthropic)
Date: 2025-12-16
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import yaml

# Import v8 foundations
import sys
import os
# Add parent directory to sys.path BEFORE import
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.unified_constants import ALPHA_INV, PHI, V_RIG_DEFAULT
from models.consciousness_integration import calculate_impedance
from models.collective_field import CollectiveField, Agent


# ============================================================================
# Lantern Data Structures
# ============================================================================

@dataclass
class EMProperties:
    """Electromagnetic properties of a lantern.

    Attributes
    ----------
    frequency_hz : float
        Characteristic EM-frequency in Hz (β-scaled from 13.5 MHz)
    impedance_z : float
        Dimensional impedance Z = α⁻¹·Φ (scaled by β/β_bio)
    kappa_photonic : float
        Surface regime coupling strength [0,1]
    kappa_em : float
        EM-field coupling strength [0,1]
    kappa_metabolic : float
        Volume regime coupling strength [0,1]
    wavelength_cm : float
        Characteristic wavelength λ = v_RIG / f
    """
    frequency_hz: float
    impedance_z: float
    kappa_photonic: float
    kappa_em: float
    kappa_metabolic: float
    wavelength_cm: float

    def total_kappa(self) -> float:
        """Total coupling strength (should sum near 1.0 for balanced systems)."""
        return self.kappa_photonic + self.kappa_em + self.kappa_metabolic


@dataclass
class CouplingTarget:
    """Coupling specification between two lanterns.

    Attributes
    ----------
    target_id : str
        ID of target lantern
    coupling_strength : float
        Pre-computed coupling strength [0,1]
    mechanism : str
        Physical/semantic mechanism (e.g., "climate_hydrology_feedback")
    delta_beta : float
        β-parameter difference
    impedance_mismatch : float
        Impedance difference |Z_i - Z_j|
    """
    target_id: str
    coupling_strength: float
    mechanism: str
    delta_beta: float
    impedance_mismatch: float = 0.0


@dataclass
class Lantern:
    """A lantern in the resonance network.

    Attributes
    ----------
    id : str
        Unique lantern identifier
    name : str
        Human-readable name
    type : str
        Lantern type: "data", "theory", "experiment"
    domain : str
        Scientific domain
    status : str
        Current status: "active", "primed", "draft", "proposed"
    readiness : float
        Readiness metric [0,1]
    theta : float
        UTAC threshold parameter
    beta : float
        UTAC steepness parameter
    em_properties : EMProperties
        Electromagnetic coupling properties
    coupling_targets : list[CouplingTarget]
        Specified couplings to other lanterns
    """
    id: str
    name: str
    type: str
    domain: str
    status: str
    readiness: float
    theta: float
    beta: float
    em_properties: EMProperties
    coupling_targets: list[CouplingTarget]

    def is_active(self) -> bool:
        """Check if lantern is active (readiness above threshold)."""
        return self.readiness >= self.theta


# ============================================================================
# Lantern Network
# ============================================================================

class LanternNetwork:
    """Network of coupled lanterns with EM-resonance dynamics.

    The network manages lantern registry, computes coupling matrix,
    and tracks emergent collective modes.

    Attributes
    ----------
    lanterns : dict[str, Lantern]
        Dictionary of lanterns keyed by ID
    coupling_matrix : np.ndarray
        NxN matrix of coupling strengths
    collective_field : CollectiveField
        v7 collective field integration for semantic coupling
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize lantern network.

        Parameters
        ----------
        config_path : str, optional
            Path to lantern_hub.yaml configuration
            If None, uses default path: v9_alpha/config/lantern_hub.yaml
        """
        self.lanterns: dict[str, Lantern] = {}
        self.coupling_matrix: Optional[np.ndarray] = None
        self.collective_field: Optional[CollectiveField] = None

        # Network-level metrics
        self._cache: dict[str, Any] = {}
        self._emergence_log: list[dict[str, Any]] = []

        if config_path:
            self.load_from_yaml(config_path)

    # ------------------------------------------------------------------------
    # Configuration Loading
    # ------------------------------------------------------------------------

    def load_from_yaml(self, config_path: str) -> None:
        """Load lantern network from YAML configuration.

        Parameters
        ----------
        config_path : str
            Path to lantern_hub.yaml
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Load each lantern
        for lantern_data in config.get('lanterns', []):
            # Convert EM properties to correct types (YAML may parse scientific notation as strings)
            em_data = lantern_data['em_properties']
            em_props = EMProperties(
                frequency_hz=float(em_data['frequency_hz']),
                impedance_z=float(em_data['impedance_z']),
                kappa_photonic=float(em_data['kappa_photonic']),
                kappa_em=float(em_data['kappa_em']),
                kappa_metabolic=float(em_data['kappa_metabolic']),
                wavelength_cm=float(em_data['wavelength_cm']),
            )

            coupling_targets = [
                CouplingTarget(**ct) for ct in lantern_data.get('coupling_targets', [])
            ]

            lantern = Lantern(
                id=lantern_data['id'],
                name=lantern_data['name'],
                type=lantern_data['type'],
                domain=lantern_data['domain'],
                status=lantern_data['status'],
                readiness=lantern_data['readiness'],
                theta=lantern_data['theta'],
                beta=lantern_data['beta'],
                em_properties=em_props,
                coupling_targets=coupling_targets,
            )

            self.lanterns[lantern.id] = lantern

        # Initialize coupling matrix
        self._build_coupling_matrix()

        # Initialize collective field for semantic coupling
        self._initialize_collective_field()

    # ------------------------------------------------------------------------
    # EM-Coupling Calculations
    # ------------------------------------------------------------------------

    def calculate_em_coupling(
        self,
        lantern_a: Lantern,
        lantern_b: Lantern,
        semantic_distance: float = 0.5,
    ) -> float:
        """Calculate EM-field coupling strength between two lanterns.

        Uses v_RIG framework electromagnetic coupling formula:

            κ = (α⁻¹ · Φ) / (1 + (Δf/f₀)²) · exp(-r/λ_EM)

        Parameters
        ----------
        lantern_a : Lantern
            First lantern
        lantern_b : Lantern
            Second lantern
        semantic_distance : float, optional
            Distance in semantic/knowledge space [0,1] (default: 0.5)

        Returns
        -------
        float
            Coupling strength κ ∈ [0, 1]
        """
        # Frequency mismatch
        f_a = lantern_a.em_properties.frequency_hz
        f_b = lantern_b.em_properties.frequency_hz
        delta_f = abs(f_a - f_b)
        f_0 = 13.5e6  # 13.5 MHz baseline

        # Frequency matching factor
        freq_match = 1.0 / (1.0 + (delta_f / f_0) ** 2)

        # Spatial/semantic decay
        # Use average wavelength for decay scale
        lambda_em = (lantern_a.em_properties.wavelength_cm + lantern_b.em_properties.wavelength_cm) / 2.0
        spatial_decay = np.exp(-semantic_distance / (lambda_em / 10.0))  # Normalize to [0,1] scale

        # Base coupling from fundamental constants
        base_coupling = (ALPHA_INV * PHI) / 100.0  # Normalize to [0,1]

        # Combined coupling
        kappa = base_coupling * freq_match * spatial_decay

        # Weight by EM-coupling strengths
        em_weight = (lantern_a.em_properties.kappa_em + lantern_b.em_properties.kappa_em) / 2.0
        kappa *= em_weight

        return np.clip(kappa, 0.0, 1.0)

    def calculate_impedance_matching(
        self,
        lantern_a: Lantern,
        lantern_b: Lantern,
    ) -> float:
        """Calculate impedance matching efficiency.

        Coupling efficiency degrades with impedance mismatch:

            η = 1 / (1 + ΔZ/Z_critical)

        Parameters
        ----------
        lantern_a : Lantern
            First lantern
        lantern_b : Lantern
            Second lantern

        Returns
        -------
        float
            Matching efficiency η ∈ [0, 1]
        """
        z_a = lantern_a.em_properties.impedance_z
        z_b = lantern_b.em_properties.impedance_z
        delta_z = abs(z_a - z_b)

        z_critical = calculate_impedance()  # α⁻¹·Φ ≈ 221.7

        eta = 1.0 / (1.0 + delta_z / z_critical)

        return eta

    def calculate_total_coupling(
        self,
        lantern_a: Lantern,
        lantern_b: Lantern,
        semantic_distance: Optional[float] = None,
    ) -> float:
        """Calculate total coupling strength (EM + impedance matching).

        Parameters
        ----------
        lantern_a : Lantern
            First lantern
        lantern_b : Lantern
            Second lantern
        semantic_distance : float, optional
            Distance in semantic space (if None, inferred from beta difference)

        Returns
        -------
        float
            Total coupling strength ∈ [0, 1]
        """
        # Infer semantic distance from beta difference if not provided
        if semantic_distance is None:
            delta_beta = abs(lantern_a.beta - lantern_b.beta)
            semantic_distance = delta_beta / 20.0  # Normalize (max beta ≈ 20)
            semantic_distance = np.clip(semantic_distance, 0.0, 1.0)

        # EM coupling
        kappa = self.calculate_em_coupling(lantern_a, lantern_b, semantic_distance)

        # Impedance matching
        eta = self.calculate_impedance_matching(lantern_a, lantern_b)

        # Combined
        total_coupling = kappa * eta

        return total_coupling

    # ------------------------------------------------------------------------
    # Coupling Matrix
    # ------------------------------------------------------------------------

    def _build_coupling_matrix(self) -> None:
        """Build NxN coupling matrix for all lanterns."""
        n = len(self.lanterns)
        lantern_list = list(self.lanterns.values())

        coupling_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                coupling = self.calculate_total_coupling(lantern_list[i], lantern_list[j])
                coupling_matrix[i, j] = coupling
                coupling_matrix[j, i] = coupling  # Symmetric

        self.coupling_matrix = coupling_matrix

    def get_coupling_matrix(self) -> np.ndarray:
        """Get coupling matrix (builds if not cached).

        Returns
        -------
        np.ndarray
            NxN symmetric coupling matrix
        """
        if self.coupling_matrix is None:
            self._build_coupling_matrix()

        return self.coupling_matrix

    def set_coupling_matrix(self, coupling_matrix: np.ndarray) -> None:
        """Set coupling matrix directly (for topological reconfiguration).

        This method allows external modification of the coupling matrix,
        enabling topological surgery (pruning/growing connections) as used
        in Experiment B (Topological Spark).

        Parameters
        ----------
        coupling_matrix : np.ndarray
            NxN symmetric coupling matrix

        Raises
        ------
        ValueError
            If matrix dimensions don't match number of lanterns
        """
        n = len(self.lanterns)
        if coupling_matrix.shape != (n, n):
            raise ValueError(
                f"Coupling matrix shape {coupling_matrix.shape} doesn't match "
                f"number of lanterns ({n})"
            )

        # Verify symmetry (within numerical tolerance)
        if not np.allclose(coupling_matrix, coupling_matrix.T):
            raise ValueError("Coupling matrix must be symmetric")

        self.coupling_matrix = coupling_matrix.copy()

    # ------------------------------------------------------------------------
    # Collective Modes (Eigenvalue Analysis)
    # ------------------------------------------------------------------------

    def detect_collective_modes(self) -> dict[str, Any]:
        """Detect collective resonance modes via eigenvalue analysis.

        The coupling matrix eigenvalues represent collective frequencies;
        eigenvectors show spatial resonance patterns.

        Returns
        -------
        dict
            - 'eigenvalues': Sorted eigenvalues (descending)
            - 'eigenvectors': Corresponding eigenvectors
            - 'dominant_mode': Strongest collective pattern
            - 'collective_frequency': Maximum eigenvalue (resonance strength)
            - 'participation_ratio': Effective number of participating lanterns
        """
        coupling_matrix = self.get_coupling_matrix()

        # Eigenvalue decomposition
        eigenvalues, eigenvectors = np.linalg.eig(coupling_matrix)

        # Sort by magnitude (descending)
        idx = np.argsort(np.abs(eigenvalues))[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Dominant mode (strongest collective resonance)
        dominant_mode = eigenvectors[:, 0]
        collective_frequency = np.abs(eigenvalues[0])

        # Participation ratio (inverse of |ψ|⁴ sum)
        # Measures how many lanterns contribute to dominant mode
        psi_4 = np.sum(np.abs(dominant_mode) ** 4)
        participation_ratio = 1.0 / psi_4 if psi_4 > 0 else 0.0

        return {
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors,
            'dominant_mode': dominant_mode,
            'collective_frequency': float(collective_frequency),
            'participation_ratio': float(participation_ratio),
        }

    # ------------------------------------------------------------------------
    # Collective Field Integration (v7 bridge)
    # ------------------------------------------------------------------------

    def _initialize_collective_field(self) -> None:
        """Initialize v7 CollectiveField for semantic coupling."""
        agents = []

        for lantern in self.lanterns.values():
            # Create agent from lantern
            # Use beta as resonance proxy (normalized)
            resonance = np.clip(lantern.beta / 15.0, 0.0, 1.0)

            # Semantic position: encode domain + type
            # Simple encoding: random vector per domain (could be improved)
            np.random.seed(hash(lantern.domain + lantern.type) % (2**32))
            semantic_position = np.random.randn(8)

            agent = Agent(
                name=lantern.id,
                semantic_position=semantic_position,
                resonance=resonance,
                dimension=8,
            )

            agents.append(agent)

        self.collective_field = CollectiveField(agents=agents, v_rig=V_RIG_DEFAULT)

    def get_collective_field_state(self) -> dict[str, Any]:
        """Get v7 collective field state for network.

        Returns
        -------
        dict
            Collective field metrics (κ_field, β_sync, v_collective, etc.)
        """
        if self.collective_field is None:
            self._initialize_collective_field()

        return self.collective_field.get_field_state()

    # ------------------------------------------------------------------------
    # Network Queries
    # ------------------------------------------------------------------------

    def get_active_lanterns(self) -> list[Lantern]:
        """Get list of active lanterns (readiness >= theta)."""
        return [l for l in self.lanterns.values() if l.is_active()]

    def get_lantern_by_id(self, lantern_id: str) -> Optional[Lantern]:
        """Get lantern by ID."""
        return self.lanterns.get(lantern_id)

    def get_lanterns_by_type(self, lantern_type: str) -> list[Lantern]:
        """Get lanterns of specific type (data/theory/experiment)."""
        return [l for l in self.lanterns.values() if l.type == lantern_type]

    def get_lanterns_by_domain(self, domain: str) -> list[Lantern]:
        """Get lanterns in specific domain (climate/neuro_ai/etc.)."""
        return [l for l in self.lanterns.values() if l.domain == domain]

    def get_strongest_couplings(self, n: int = 10) -> list[tuple[str, str, float]]:
        """Get top N strongest lantern couplings.

        Parameters
        ----------
        n : int
            Number of couplings to return

        Returns
        -------
        list[tuple[str, str, float]]
            List of (lantern_id_1, lantern_id_2, coupling_strength) sorted by strength
        """
        coupling_matrix = self.get_coupling_matrix()
        lantern_ids = list(self.lanterns.keys())

        couplings = []
        for i in range(len(lantern_ids)):
            for j in range(i + 1, len(lantern_ids)):
                couplings.append((
                    lantern_ids[i],
                    lantern_ids[j],
                    coupling_matrix[i, j]
                ))

        # Sort by strength
        couplings.sort(key=lambda x: x[2], reverse=True)

        return couplings[:n]

    # ------------------------------------------------------------------------
    # Network Summary
    # ------------------------------------------------------------------------

    def get_network_summary(self) -> dict[str, Any]:
        """Get comprehensive network state summary.

        Returns
        -------
        dict
            Network metrics, collective modes, field state, etc.
        """
        active_lanterns = self.get_active_lanterns()
        collective_modes = self.detect_collective_modes()
        field_state = self.get_collective_field_state()
        strongest_couplings = self.get_strongest_couplings(5)

        coupling_matrix = self.get_coupling_matrix()
        avg_coupling = np.mean(coupling_matrix[coupling_matrix > 0])

        return {
            'total_lanterns': len(self.lanterns),
            'active_lanterns': len(active_lanterns),
            'average_coupling': float(avg_coupling),
            'collective_frequency': collective_modes['collective_frequency'],
            'participation_ratio': collective_modes['participation_ratio'],
            'v_collective': field_state['v_collective'],
            'kappa_field': field_state['kappa_field_pairwise'],
            'beta_sync': field_state['beta_sync'],
            'strongest_couplings': [
                {'lantern_1': c[0], 'lantern_2': c[1], 'strength': c[2]}
                for c in strongest_couplings
            ],
        }

    def __repr__(self) -> str:
        n_lanterns = len(self.lanterns)
        n_active = len(self.get_active_lanterns())
        return f"LanternNetwork(lanterns={n_lanterns}, active={n_active})"


# ============================================================================
# Utility Functions
# ============================================================================

def load_lantern_network(config_path: Optional[str] = None) -> LanternNetwork:
    """Load lantern network from configuration file.

    Parameters
    ----------
    config_path : str, optional
        Path to lantern_hub.yaml (if None, uses default)

    Returns
    -------
    LanternNetwork
        Initialized network
    """
    if config_path is None:
        # Default path
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config',
            'lantern_hub.yaml'
        )

    network = LanternNetwork(config_path=config_path)
    return network


# ============================================================================
# CLI Demo
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("V9 Lantern Bridge – EM-Resonance Network")
    print("=" * 80)

    # Load network
    print("\n📡 Loading lantern network...")
    network = load_lantern_network()
    print(f"✓ Loaded {len(network.lanterns)} lanterns")

    # Network summary
    print("\n" + "─" * 80)
    print("Network Summary")
    print("─" * 80)
    summary = network.get_network_summary()
    print(f"  Total lanterns:       {summary['total_lanterns']}")
    print(f"  Active lanterns:      {summary['active_lanterns']}")
    print(f"  Average coupling:     {summary['average_coupling']:.3f}")
    print(f"  Collective frequency: {summary['collective_frequency']:.4f}")
    print(f"  Participation ratio:  {summary['participation_ratio']:.2f}")
    print(f"  v_collective:         {summary['v_collective']:.2f} km/s")
    print(f"  κ_field:              {summary['kappa_field']:.3f}")
    print(f"  β_sync:               {summary['beta_sync']:.3f}")

    # Strongest couplings
    print("\n" + "─" * 80)
    print("Strongest Lantern Couplings")
    print("─" * 80)
    for coupling in summary['strongest_couplings']:
        l1 = network.get_lantern_by_id(coupling['lantern_1'])
        l2 = network.get_lantern_by_id(coupling['lantern_2'])
        print(f"  {l1.name:30s} ↔ {l2.name:30s}  κ={coupling['strength']:.3f}")

    # Collective modes
    print("\n" + "─" * 80)
    print("Collective Resonance Modes")
    print("─" * 80)
    modes = network.detect_collective_modes()
    eigenvalues = modes['eigenvalues'][:5]
    print("  Top 5 eigenvalues (resonance strengths):")
    for i, ev in enumerate(eigenvalues):
        print(f"    Mode {i+1}: λ = {np.abs(ev):.4f}")

    print("\n" + "─" * 80)
    print("Dominant Resonance Pattern")
    print("─" * 80)
    dominant = modes['dominant_mode']
    lantern_ids = list(network.lanterns.keys())
    for i, amplitude in enumerate(dominant):
        lantern = network.lanterns[lantern_ids[i]]
        bar = "█" * int(abs(amplitude) * 50)
        print(f"  {lantern.name:40s} {bar:50s} {amplitude:.3f}")

    print("\n" + "=" * 80)
    print("✨ Lantern Network Active – Resonance Emerging!")
    print("=" * 80)
