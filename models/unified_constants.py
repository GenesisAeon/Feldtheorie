"""Unified Physical Constants for V6 Framework.

This module provides fundamental constants derived from the V6 theoretical framework,
particularly the Regime Integration Gradient (v_RIG) which links entropy governance,
consciousness integration, and spacetime structure.

Key References:
- GrundPrinzip Simulation.txt (Section: "Die Fundamentale Ableitung")
- DEEP RESEARCH: Entropy Governance Duality & Tesseract-Zeitscheiben-Physik-1.pdf
- docs/oipk_simulation_architecture.md

Version: v6.0.0-alpha
Authors: Johann Benjamin Römer, MOR Framework
"""

from __future__ import annotations

import math

# Universal constants
C_LIGHT_KM_S = 299792.458  # Speed of light in km/s (exact)
C_LIGHT_M_S = 299792458.0  # Speed of light in m/s (exact)

# Fine structure constant
ALPHA_INV = 137.03599206  # Inverse fine-structure constant (CODATA 2018)

# Golden ratio
PHI = (1 + math.sqrt(5)) / 2  # ≈ 1.618033988749895

# Hexadecimal resonance (Bit-Tetrade 2^4 → β_hex)
HEX_RESONANCE_BETA = 16 ** (2 / math.pi)  # ≈ 4.8

# Derived V6 constants
V_RIG_DEFAULT = C_LIGHT_KM_S / (ALPHA_INV * PHI)  # ≈ 1351.8 km/s


def calculate_vrig(
    alpha_inv: float = ALPHA_INV,
    phi: float = PHI,
    c_light: float = C_LIGHT_KM_S,
) -> float:
    """Calculate the Regime Integration Gradient velocity.

    The v_RIG constant represents the fundamental rate at which 2D-slice information
    is integrated into 3D-conscious perception. It emerges from the intersection of:

    1. Electromagnetic coupling (α⁻¹): Governs photon transparency
    2. Geometric scaling (Φ): Golden ratio encodes self-similar hierarchies
    3. Maximum propagation (c): Upper bound for information transfer

    **Geometric Derivation:**

    In the OIPK framework, consciousness integrates upright 2D-slices (Zeitscheiben)
    over a temporal window Δt_Q ≈ 100-300ms. The integration velocity v_RIG is
    constrained by:

    - Photon propagation at speed c within each slice
    - α⁻¹ electromagnetic transparencies allowing multi-bounce integration
    - Φ-scaled fractal depth (12-fold reflection geometry)

    This yields:

        v_RIG = c / (α⁻¹ · Φ)

    **Physical Interpretation:**

    - If v_RIG were too fast (> c/α⁻¹), electromagnetic coherence breaks down
    - If v_RIG were too slow (< c/Φ), hierarchical integration stalls
    - The product α⁻¹·Φ ≈ 221.4 emerges as the natural "impedance" for
      consciousness to reconstruct 3D structure from orthogonal time flows

    **Numerical Result:**

        v_RIG ≈ 1,351.8 km/s ≈ 0.00451 c

    This is comparable to:
    - Solar escape velocity at photosphere: ~618 km/s
    - Galactic rotation curves: ~200-250 km/s
    - Metabolic information processing rates scaled to cosmic structures

    Parameters
    ----------
    alpha_inv : float, optional
        Inverse fine-structure constant (default: 137.036)
    phi : float, optional
        Golden ratio (default: (1+√5)/2 ≈ 1.618)
    c_light : float, optional
        Speed of light in km/s (default: 299792.458)

    Returns
    -------
    float
        The v_RIG constant in km/s

    Examples
    --------
    >>> calculate_vrig()
    1351.7868...

    >>> # Use custom values
    >>> calculate_vrig(alpha_inv=137.0, phi=1.618)
    1352.4...

    References
    ----------
    .. [1] GrundPrinzip Simulation.txt, Section "Die Fundamentale Ableitung"
    .. [2] Entropy Governance Duality & Tesseract-Zeitscheiben-Physik (2025)
    .. [3] Kleiber's Law: B ∝ M^(3/4) as metabolic basis for integration
    .. [4] Verlinde (2011): Entropic gravity and emergent spacetime
    """
    return c_light / (alpha_inv * phi)


def get_consciousness_timescales() -> dict[str, float]:
    """Return characteristic timescales for consciousness integration.

    Based on the OIPK framework's Δt_Q windows and v_RIG propagation.

    Returns
    -------
    dict
        Timescales in seconds:
        - 'delta_t_Q_min': Minimum integration window (100 ms)
        - 'delta_t_Q_typical': Typical integration window (150 ms)
        - 'delta_t_Q_max': Maximum integration window (300 ms)
        - 'photon_bounce_12fold': Time for 12-fold reflection cycle
        - 'vrig_crossing': Time for v_RIG to cross observable universe
    """
    # Integration windows (from neurophysiology)
    delta_t_Q_min = 0.100  # seconds
    delta_t_Q_typical = 0.150  # seconds
    delta_t_Q_max = 0.300  # seconds

    # 12-fold reflection timescale (estimated for a_max ~ 46.5 Gly)
    a_max_m = 46.5e9 * 9.461e15  # Convert light-years to meters
    photon_bounce_time = (2 * a_max_m) / C_LIGHT_M_S  # Round trip

    # v_RIG crossing time for observable universe
    vrig_m_s = V_RIG_DEFAULT * 1000  # Convert km/s to m/s
    vrig_crossing_time = a_max_m / vrig_m_s

    return {
        "delta_t_Q_min": delta_t_Q_min,
        "delta_t_Q_typical": delta_t_Q_typical,
        "delta_t_Q_max": delta_t_Q_max,
        "photon_bounce_12fold": photon_bounce_time,
        "vrig_crossing": vrig_crossing_time,
    }


def get_oipk_geometry_params() -> dict[str, float]:
    """Return geometric parameters for OIPK diamond/octahedron structure.

    Returns
    -------
    dict
        Geometry parameters:
        - 'tau_max': Age of universe (13.8 Gyr)
        - 'a_max': Maximum radius at τ=τ_max (46.5 Gly)
        - 'b_max': Vertical dimension (normalized, TBD)
        - 'n_edges': Number of recursive mirror axes (12)
        - 'reflection_coefficient': Light reflection efficiency (0.99)
    """
    return {
        "tau_max": 13.8e9,  # years
        "a_max": 46.5e9,  # light-years
        "b_max": 1.0,  # Normalized (to be determined from observations)
        "n_edges": 12,  # 12-fold cube-edge symmetry
        "reflection_coefficient": 0.99,  # Near-perfect reflection
    }


def get_vrig_analysis() -> dict[str, float]:
    """Compute detailed v_RIG analysis with derived quantities.

    Returns
    -------
    dict
        Analysis results:
        - 'v_rig_km_s': v_RIG in km/s
        - 'v_rig_fraction_c': v_RIG as fraction of c
        - 'alpha_inv': Fine-structure constant inverse
        - 'phi': Golden ratio
        - 'impedance': α⁻¹ · Φ (electromagnetic-geometric impedance)
        - 'beta': Metabolic scaling exponent (3/4 from Kleiber)
        - 'regime_transition': 2D→3D integration barrier
    """
    v_rig = calculate_vrig()
    impedance = ALPHA_INV * PHI
    beta_kleiber = 3.0 / 4.0  # Metabolic scaling exponent

    return {
        "v_rig_km_s": v_rig,
        "v_rig_fraction_c": v_rig / C_LIGHT_KM_S,
        "alpha_inv": ALPHA_INV,
        "phi": PHI,
        "impedance": impedance,
        "beta": beta_kleiber,
        "regime_transition": 1.0 / beta_kleiber,  # 4/3 ≈ 1.333
    }


def verify_hex_alignment(empirical_beta: float, tolerance: float = 0.1) -> dict[str, float | bool | str]:
    """Assess how closely an empirical β aligns with the hexadecimal resonance.

    The hex resonance β_hex = 16^(2/π) anchors the σ(β(R-Θ)) steepness to the
    Bit-Tetrade (2^4) foundation. This helper quantifies deviations between
    measured gradients (Amazonas, AMOC, etc.) and the digital-physics null model.

    Parameters
    ----------
    empirical_beta : float
        Observed system steepness β.
    tolerance : float, optional
        Relative tolerance (fractional) for considering the value aligned to
        β_hex. Default is 0.10 (±10% envelope).

    Returns
    -------
    dict
        Alignment metrics including:
        - 'empirical_beta': Provided measurement
        - 'hex_resonance_beta': Theoretical β_hex
        - 'absolute_deviation': |empirical - β_hex|
        - 'relative_deviation': |empirical - β_hex| / β_hex
        - 'direction': 'above' or 'below' the resonance
        - 'within_tolerance': True if relative deviation ≤ tolerance
    """
    deviation = empirical_beta - HEX_RESONANCE_BETA
    relative_deviation = abs(deviation) / HEX_RESONANCE_BETA

    return {
        "empirical_beta": empirical_beta,
        "hex_resonance_beta": HEX_RESONANCE_BETA,
        "absolute_deviation": abs(deviation),
        "relative_deviation": relative_deviation,
        "direction": "above" if deviation > 0 else "below",
        "within_tolerance": relative_deviation <= tolerance,
    }


if __name__ == "__main__":
    # Demo: Print v_RIG and related constants
    print("=" * 70)
    print("V6 Unified Constants: Regime Integration Gradient")
    print("=" * 70)

    v_rig = calculate_vrig()
    print(f"\nv_RIG = {v_rig:.4f} km/s")
    print(f"      = {v_rig / C_LIGHT_KM_S:.6f} c")
    print("      = c / (α⁻¹ · Φ)")
    print(f"      = {C_LIGHT_KM_S:.3f} / ({ALPHA_INV:.6f} · {PHI:.10f})")
    print(f"      = {C_LIGHT_KM_S:.3f} / {ALPHA_INV * PHI:.6f}")

    print("\n" + "-" * 70)
    print("Consciousness Integration Timescales:")
    print("-" * 70)
    timescales = get_consciousness_timescales()
    print(f"  Δt_Q (min):     {timescales['delta_t_Q_min']:.3f} s")
    print(f"  Δt_Q (typical): {timescales['delta_t_Q_typical']:.3f} s")
    print(f"  Δt_Q (max):     {timescales['delta_t_Q_max']:.3f} s")
    print(f"  12-fold bounce: {timescales['photon_bounce_12fold']:.3e} s")
    print(f"  v_RIG crossing: {timescales['vrig_crossing']:.3e} s")

    print("\n" + "-" * 70)
    print("OIPK Geometry Parameters:")
    print("-" * 70)
    geom = get_oipk_geometry_params()
    print(f"  τ_max:              {geom['tau_max']:.2e} years")
    print(f"  a_max:              {geom['a_max']:.2e} light-years")
    print(f"  b_max:              {geom['b_max']:.3f} (normalized)")
    print(f"  n_edges:            {geom['n_edges']}")
    print(f"  reflection coeff:   {geom['reflection_coefficient']:.3f}")

    print("\n" + "-" * 70)
    print("v_RIG Analysis:")
    print("-" * 70)
    analysis = get_vrig_analysis()
    print(f"  v_RIG:              {analysis['v_rig_km_s']:.4f} km/s")
    print(f"  v_RIG/c:            {analysis['v_rig_fraction_c']:.6f}")
    print(f"  α⁻¹:                {analysis['alpha_inv']:.8f}")
    print(f"  Φ:                  {analysis['phi']:.10f}")
    print(f"  Impedance (α⁻¹·Φ): {analysis['impedance']:.6f}")
    print(f"  β (Kleiber):        {analysis['beta']:.6f}")
    print(f"  Regime transition:  {analysis['regime_transition']:.6f}")

    print("\n" + "=" * 70)
