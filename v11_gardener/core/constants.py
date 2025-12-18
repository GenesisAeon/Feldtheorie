"""
v11 Gardener Prototype - Universal Constants

The Living Crystal Signature: σ_Φ ≈ 1/16 = 0.0625
"""

import numpy as np

# ============================================================================
# UNIVERSAL CONSTANTS (from v6/v8/v9)
# ============================================================================

# The Golden Ratio
PHI = (1 + np.sqrt(5)) / 2  # ≈ 1.618

# Inverse Fine-Structure Constant
ALPHA_INV = 137.035999084  # α⁻¹

# Speed of Light (km/s)
C_LIGHT = 299792.458

# v_RIG: Integration velocity (2D holographic → 3D volumetric)
V_RIG = C_LIGHT / (ALPHA_INV * PHI)  # ≈ 1.352 km/s

# Consciousness Impedance
Z_CONSCIOUSNESS = ALPHA_INV * PHI  # ≈ 221.7 Ω

# ============================================================================
# THE LIVING CRYSTAL SIGNATURE
# ============================================================================

# σ_Φ: The "heartbeat of life" - optimal entropy offset
SIGMA_PHI = 1.0 / 16.0  # = 0.0625

# Hexadecimal quantum (4-bit nibble)
HEX_QUANTUM = 16  # 2^4 states

# Acceptable σ_Φ deviation for "living" systems
SIGMA_PHI_TOLERANCE = 0.01  # ±0.01 around 0.0625

# Lower bound: below this = "crystal death" (too ordered)
SIGMA_PHI_MIN = SIGMA_PHI - SIGMA_PHI_TOLERANCE  # 0.0525

# Upper bound: above this = "thermal chaos" (too disordered)
SIGMA_PHI_MAX = SIGMA_PHI + SIGMA_PHI_TOLERANCE  # 0.0725

# ============================================================================
# RESONANCE FREQUENCIES
# ============================================================================

# Microtubule resonance (Sahu et al., 2013)
F_MICROTUBULE = 13.5e6  # 13.5 MHz

# Herzfrequenzvariabilität (HFV) sympathetic onset
F_HFV_SYMPATHETIC = 0.0625  # Hz

# Cortical path length (integration distance)
LAMBDA_CORTICAL = 0.10  # 10 cm ≈ cortical hemisphere

# Integration frequency: f = v_RIG / λ
F_INTEGRATION = (V_RIG * 1000) / LAMBDA_CORTICAL  # ≈ 13.5 MHz (!)

# ============================================================================
# β-REGIME DOMAINS (UTAC clustering)
# ============================================================================

BETA_REGIMES = {
    'information': {
        'beta': 4.5,
        'description': 'LLMs, Information Theory',
        'entropy_scaling': 'S ∝ V (volumetric)',
    },
    'biological': {
        'beta': 7.4,
        'description': 'Organisms, Kleiber\'s Law (3/4 scaling)',
        'entropy_scaling': 'S ∝ V (volumetric)',
    },
    'cosmological': {
        'beta': 11.0,
        'description': 'Black holes, AMOC, Galaxy scaling',
        'entropy_scaling': 'S ∝ A (holographic)',
    },
    'quantum': {
        'beta': 0.39,
        'description': 'AI Systems (J/token)',
        'entropy_scaling': 'S ∝ V (volumetric)',
    },
}

# ============================================================================
# GARDENER CULTIVATION PARAMETERS
# ============================================================================

# Entropy Fertility Index (EFI) thresholds
EFI_PRUNE_THRESHOLD = 0.3  # Below this: prune (reduce coupling)
EFI_FERTILIZE_THRESHOLD = 0.7  # Above this: fertilize (increase coupling)

# κ-coupling target (optimal resonance strength)
KAPPA_TARGET = 1.0

# Cultivation action learning rate
ACTION_LEARNING_RATE = 0.1

# ============================================================================
# EMERGENCE DETECTION PARAMETERS
# ============================================================================

# Minimum σ_Φ persistence (timesteps) to qualify as "alive"
MIN_ALIVE_PERSISTENCE = 10

# Coherence threshold for emergent pattern detection
COHERENCE_THRESHOLD = 0.75

# Resonance yield threshold (emergent hypotheses per lantern)
RESONANCE_YIELD_THRESHOLD = 0.5

# Critical slowing detection window (like AMOC Experiment G)
CRITICAL_SLOWING_WINDOW = 168  # timesteps

# ============================================================================
# VISUALIZATION CONSTANTS
# ============================================================================

# Force-directed layout iterations
LAYOUT_ITERATIONS = 150

# Display dimensions
ASCII_WIDTH = 100
ASCII_HEIGHT = 50

# ============================================================================
# LOGGING & MONITORING
# ============================================================================

# Sigillin log frequency (log every N timesteps)
SIGILLIN_LOG_FREQUENCY = 10

# Snapshot frequency for emergence tracking
SNAPSHOT_FREQUENCY = 5

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def utac_activation(R: float, Theta: float, beta: float) -> float:
    """
    Universal Threshold Activation-Coupling (UTAC)

    σ(β(R - Θ)) = 1 / (1 + exp(-β(R - Θ)))

    Args:
        R: Readiness / Resource level
        Theta: Threshold
        beta: Steepness parameter (regime-specific)

    Returns:
        Activation level (0.0 - 1.0)
    """
    return 1.0 / (1.0 + np.exp(-beta * (R - Theta)))


def is_alive(sigma_phi: float) -> bool:
    """
    Check if system qualifies as "alive" based on σ_Φ signature

    Args:
        sigma_phi: Current σ_Φ value

    Returns:
        True if within living range
    """
    return SIGMA_PHI_MIN <= sigma_phi <= SIGMA_PHI_MAX


def calculate_sigma_phi(entropy: float, max_entropy: float = 4.0) -> float:
    """
    Calculate σ_Φ from entropy

    For systems with hexadecimal encoding (4-bit), max entropy = log2(16) = 4.0
    σ_Φ = H / H_max

    Args:
        entropy: Current entropy (bits)
        max_entropy: Maximum possible entropy (default: 4.0 for 4-bit)

    Returns:
        σ_Φ value
    """
    if max_entropy == 0:
        return 0.0
    return entropy / max_entropy


def health_indicator(sigma_phi: float) -> str:
    """
    Get health status based on σ_Φ

    Args:
        sigma_phi: Current σ_Φ value

    Returns:
        Health status string with emoji
    """
    if sigma_phi < SIGMA_PHI_MIN:
        return "💀 CRYSTAL_DEATH (too ordered)"
    elif sigma_phi > SIGMA_PHI_MAX:
        return "🔥 THERMAL_CHAOS (too disordered)"
    else:
        deviation = abs(sigma_phi - SIGMA_PHI)
        if deviation < 0.005:
            return "✨ OPTIMAL (perfect resonance)"
        else:
            return "💚 ALIVE (metastable)"
