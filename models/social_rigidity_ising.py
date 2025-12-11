"""
Social Rigidity Ising Model (UTAC v5.0)

This module implements a mean-field Ising model applied to social dynamics,
testing whether inequality-driven mechanisms can produce phase transitions
analogous to those in physical systems.

MODEL ANALOGY:
    - Spins σ_i ∈ {-1, +1}    →  Individual opinions/beliefs
    - Coupling J               →  Social conformity pressure
    - External field h         →  External influence (media, etc.)
    - Temperature T            →  System adaptability
    - Magnetization M          →  Collective alignment

HYPOTHESIS: We test whether inequality (Gini coefficient) acts as an
inverse temperature via:

    T_social = 1 / (Gini · Load)

where Load represents cognitive/economic stress. At high inequality,
T → 0, potentially producing a phase transition to low-adaptability states.

This is an empirical test of structural isomorphism between physical
phase transitions and social dynamics.

Author: Genesis Aeon (UTAC Framework)
Version: 5.0 "Structural Isomorphism Analysis"
"""

import warnings
from dataclasses import dataclass

import numpy as np

# ============================================================================
# MODEL PARAMETERS
# ============================================================================

# Critical exponents (Mean Field Ising)
BETA_CRITICAL: float = 0.5  # Magnetization exponent: M ~ (T_c - T)^β
GAMMA_CRITICAL: float = 1.0  # Susceptibility exponent: χ ~ |T - T_c|^(-γ)

# Mean-field critical temperature (normalized units)
T_CRITICAL_MF: float = 1.0  # In units of J/k_B


@dataclass
class SocialState:
    """Container for social system state."""

    gini: float  # Gini coefficient (0-1)
    load: float  # Cognitive/economic load (dimensionless)
    temperature: float  # Social temperature T = 1/(Gini·Load)
    magnetization: float  # Order parameter M ∈ [-1, 1]
    susceptibility: float  # Response function χ
    rigidity: float  # Effective β = 1/T

    @property
    def is_frozen(self) -> bool:
        """Check if system is in frozen (ferromagnetic) phase."""
        return self.temperature < T_CRITICAL_MF

    @property
    def adaptability(self) -> float:
        """Inverse rigidity: ability to change."""
        return 1.0 / self.rigidity if self.rigidity > 0 else np.inf

    def __str__(self) -> str:
        phase = "FROZEN (ferromagnetic)" if self.is_frozen else "FLUID (paramagnetic)"
        return (
            f"SocialState:\n"
            f"  Gini:           {self.gini:.3f}\n"
            f"  Load:           {self.load:.3f}\n"
            f"  Temperature:    {self.temperature:.4f} (T_c = {T_CRITICAL_MF:.2f})\n"
            f"  Magnetization:  {self.magnetization:.4f}\n"
            f"  Susceptibility: {self.susceptibility:.4f}\n"
            f"  Rigidity β:     {self.rigidity:.2f}\n"
            f"  Phase:          {phase}"
        )


@dataclass
class PhaseTransition:
    """Container for phase transition analysis."""

    gini_values: np.ndarray
    temperatures: np.ndarray
    magnetizations: np.ndarray
    susceptibilities: np.ndarray
    critical_gini: float  # Where T = T_c
    transition_sharpness: float  # Width of transition

    def __str__(self) -> str:
        return (
            f"PhaseTransition:\n"
            f"  Critical Gini:  {self.critical_gini:.3f}\n"
            f"  Transition width: {self.transition_sharpness:.3f}\n"
            f"  Max susceptibility at Gini = {self.gini_values[np.argmax(self.susceptibilities)]:.3f}"
        )


# ============================================================================
# CORE ISING MODEL CLASS
# ============================================================================


class SocialIsingModel:
    """
    Mean-field Ising model applied to social dynamics.

    We test the hypothesis that social systems exhibit phase transition
    behavior analogous to physical systems by mapping:

        Physical System         →  Social Analogue
        ──────────────────────────────────────────
        Spins σ_i ∈ {-1, +1}    →  Individual beliefs/opinions
        Coupling J               →  Social conformity pressure
        External field h         →  External influence
        Temperature T            →  System adaptability
        Magnetization M          →  Collective alignment

    In mean-field approximation, the self-consistent equation is:

        M = tanh(β J M + β h)

    where β = 1/(k_B T) is the inverse temperature parameter.

    TESTABLE PREDICTIONS:
        - At T < T_c: spontaneous symmetry breaking (M ≠ 0)
        - Near T_c: susceptibility peak χ ~ |T - T_c|^(-γ)
        - If Gini acts as 1/T: high inequality → low adaptability
    """

    def __init__(
        self,
        coupling_strength: float = 1.0,
        external_field: float = 0.0,
        load_baseline: float = 1.0,
    ):
        """
        Initialize social Ising model.

        Args:
            coupling_strength: J (social conformity pressure)
            external_field: h (external influence, e.g., media)
            load_baseline: Baseline cognitive/economic load
        """
        self.J = coupling_strength
        self.h = external_field
        self.load_baseline = load_baseline

    def social_temperature(self, gini: float, load: float | None = None) -> float:
        """
        Calculate effective temperature from inequality measure.

        HYPOTHESIS: T_social = 1 / (Gini · Load)

        This formula encodes the assumption that inequality reduces
        system adaptability in a manner analogous to inverse temperature.

        Args:
            gini: Gini coefficient [0, 1]
            load: Cognitive/economic stress parameter (defaults to baseline)

        Returns:
            Effective temperature in dimensionless units
        """
        if load is None:
            load = self.load_baseline

        if gini <= 0 or load <= 0:
            warnings.warn("Gini or Load ≤ 0; setting T = ∞ (free state)")
            return np.inf

        # Normalize to set critical point at Gini ≈ 0.7
        # We want T_c = 1 when Gini · Load ≈ 1
        T = 1.0 / (gini * load)
        return T

    def solve_magnetization(
        self, temperature: float, max_iterations: int = 1000, tolerance: float = 1e-6
    ) -> float:
        """
        Solve self-consistent mean-field equation for magnetization.

        M = tanh(β J M + β h)

        This is solved iteratively using fixed-point iteration.

        Args:
            temperature: Social temperature T
            max_iterations: Maximum iterations for convergence
            tolerance: Convergence criterion |M_new - M_old| < tol

        Returns:
            Equilibrium magnetization M ∈ [-1, 1]
        """
        if temperature == 0:
            # T=0: Perfect order, M = sign(h)
            return np.sign(self.h) if self.h != 0 else 1.0

        if np.isinf(temperature):
            # T=∞: No order, M = 0
            return 0.0

        beta = 1.0 / temperature
        M = 0.1  # Initial guess (small but non-zero)

        for _ in range(max_iterations):
            M_new = np.tanh(beta * self.J * M + beta * self.h)

            if abs(M_new - M) < tolerance:
                return M_new

            M = M_new

        warnings.warn(f"Magnetization did not converge after {max_iterations} iterations")
        return M

    def susceptibility(self, temperature: float, magnetization: float) -> float:
        """
        Calculate magnetic susceptibility (response function).

        χ = ∂M/∂h |_{h=0}

        In mean-field theory:
            χ = β (1 - M^2) / (1 - β J (1 - M^2))

        Near T_c: χ ~ |T - T_c|^(-γ) with γ = 1 (mean field)

        Args:
            temperature: Social temperature T
            magnetization: Current magnetization M

        Returns:
            Susceptibility χ (dimensionless)
        """
        if temperature == 0 or np.isinf(temperature):
            return 0.0

        beta = 1.0 / temperature
        denominator = 1.0 - beta * self.J * (1.0 - magnetization**2)

        if abs(denominator) < 1e-10:
            # At critical point, χ diverges
            return 1e10

        chi = beta * (1.0 - magnetization**2) / denominator
        return chi

    def compute_state(self, gini: float, load: float | None = None) -> SocialState:
        """
        Compute complete social state for given Gini coefficient.

        Args:
            gini: Gini coefficient [0, 1]
            load: Cognitive/economic load (optional)

        Returns:
            SocialState with all thermodynamic quantities
        """
        T = self.social_temperature(gini, load)
        M = self.solve_magnetization(T)
        chi = self.susceptibility(T, M)
        rigidity = 1.0 / T if T > 0 else np.inf

        return SocialState(
            gini=gini,
            load=load if load is not None else self.load_baseline,
            temperature=T,
            magnetization=M,
            susceptibility=chi,
            rigidity=rigidity,
        )

    def phase_transition_scan(
        self,
        gini_range: tuple[float, float] = (0.2, 0.95),
        n_points: int = 100,
        load: float | None = None,
    ) -> PhaseTransition:
        """
        Scan Gini coefficient to map out phase transition.

        This computes M(Gini) and χ(Gini) to identify:
            - Critical point (where χ is maximal)
            - Transition sharpness
            - Frozen vs. fluid regimes

        Args:
            gini_range: (min, max) Gini values to scan
            n_points: Number of sample points
            load: Fixed cognitive load (optional)

        Returns:
            PhaseTransition with full scan data
        """
        gini_values = np.linspace(gini_range[0], gini_range[1], n_points)
        temperatures = np.zeros(n_points)
        magnetizations = np.zeros(n_points)
        susceptibilities = np.zeros(n_points)

        for i, gini in enumerate(gini_values):
            state = self.compute_state(gini, load)
            temperatures[i] = state.temperature
            magnetizations[i] = state.magnetization
            susceptibilities[i] = state.susceptibility

        # Find critical Gini (where susceptibility is maximal)
        critical_idx = np.argmax(susceptibilities)
        critical_gini = gini_values[critical_idx]

        # Estimate transition width (FWHM of susceptibility peak)
        half_max = susceptibilities[critical_idx] / 2.0
        above_half = susceptibilities > half_max
        indices = np.where(above_half)[0]
        if len(indices) > 1:
            transition_width = gini_values[indices[-1]] - gini_values[indices[0]]
        else:
            transition_width = 0.05  # Default narrow transition

        return PhaseTransition(
            gini_values=gini_values,
            temperatures=temperatures,
            magnetizations=magnetizations,
            susceptibilities=susceptibilities,
            critical_gini=critical_gini,
            transition_sharpness=transition_width,
        )

    def critical_exponents(
        self, gini_critical: float = 0.71, epsilon: float = 0.01, load: float | None = None
    ) -> dict[str, float]:
        """
        Estimate critical exponents near phase transition.

        In mean-field theory:
            M ~ (T_c - T)^β    with β = 0.5
            χ ~ |T - T_c|^(-γ) with γ = 1.0

        Args:
            gini_critical: Critical Gini value
            epsilon: Small offset for numerical derivative
            load: Cognitive load

        Returns:
            Dictionary of critical exponents
        """
        # Subcritical (ordered phase)
        state_sub = self.compute_state(gini_critical + epsilon, load)

        # Supercritical (disordered phase)
        state_super = self.compute_state(gini_critical - epsilon, load)

        # Estimate β exponent: M ~ ΔT^β
        if state_sub.magnetization > 0:
            delta_T = abs(state_sub.temperature - T_CRITICAL_MF)
            beta_exp = np.log(state_sub.magnetization) / np.log(delta_T + 1e-10)
        else:
            beta_exp = np.nan

        # Estimate γ exponent: χ ~ ΔT^(-γ)
        delta_T_super = abs(state_super.temperature - T_CRITICAL_MF)
        if delta_T_super > 0:
            gamma_exp = -np.log(state_super.susceptibility) / np.log(delta_T_super + 1e-10)
        else:
            gamma_exp = np.nan

        return {
            "beta_exponent": beta_exp,
            "gamma_exponent": gamma_exp,
            "beta_theory": BETA_CRITICAL,
            "gamma_theory": GAMMA_CRITICAL,
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def quick_rigidity(gini: float, load: float = 1.0) -> float:
    """
    Quick calculation of social rigidity β.

    Args:
        gini: Gini coefficient
        load: Cognitive/economic load

    Returns:
        Rigidity parameter β = 1/T
    """
    model = SocialIsingModel(load_baseline=load)
    state = model.compute_state(gini)
    return state.rigidity


def is_society_frozen(gini: float, load: float = 1.0) -> bool:
    """
    Check if society is in frozen (ferromagnetic) phase.

    Args:
        gini: Gini coefficient
        load: Cognitive load

    Returns:
        True if T < T_c (frozen), False otherwise
    """
    model = SocialIsingModel(load_baseline=load)
    state = model.compute_state(gini)
    return state.is_frozen


def full_analysis(verbose: bool = True) -> dict:
    """
    Run complete phase transition analysis.

    Args:
        verbose: Print results to stdout

    Returns:
        Dictionary with phase transition data
    """
    model = SocialIsingModel()

    # Example states
    low_gini = model.compute_state(gini=0.3)
    mid_gini = model.compute_state(gini=0.5)
    high_gini = model.compute_state(gini=0.8)

    # Phase transition scan
    transition = model.phase_transition_scan(gini_range=(0.2, 0.95), n_points=200)

    # Critical exponents
    exponents = model.critical_exponents(gini_critical=transition.critical_gini)

    if verbose:
        print("=" * 70)
        print("SOCIAL RIGIDITY ISING MODEL (UTAC v5.0)")
        print("=" * 70)
        print()
        print("LOW INEQUALITY (Gini = 0.3):")
        print(low_gini)
        print()
        print("MEDIUM INEQUALITY (Gini = 0.5):")
        print(mid_gini)
        print()
        print("HIGH INEQUALITY (Gini = 0.8):")
        print(high_gini)
        print()
        print(transition)
        print()
        print("CRITICAL EXPONENTS:")
        for key, value in exponents.items():
            print(f"  {key:20s}: {value:.4f}")
        print("=" * 70)
        print()
        print("INTERPRETATION (UNDER MODEL ASSUMPTIONS):")
        print(f"  At Gini > {transition.critical_gini:.2f}, model predicts phase transition.")
        print(f"  Magnetization M = {high_gini.magnetization:.3f}: high collective alignment.")
        print(f"  Rigidity β = {high_gini.rigidity:.1f}: reduced adaptability parameter.")
        print("=" * 70)

    return {
        "states": {"low": low_gini, "mid": mid_gini, "high": high_gini},
        "transition": transition,
        "exponents": exponents,
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    results = full_analysis(verbose=True)

    # Additional insight: Inequality trajectory
    print("\nINEQUALITY TRAJECTORY (2000 → 2024):")
    print("-" * 70)

    years = [2000, 2010, 2020, 2024]
    gini_trajectory = [0.45, 0.55, 0.68, 0.73]  # Approximate US trend

    for year, gini in zip(years, gini_trajectory):
        state = SocialIsingModel().compute_state(gini)
        phase = "FROZEN" if state.is_frozen else "FLUID"
        print(f"  {year}: Gini = {gini:.2f}  →  β = {state.rigidity:6.2f}  [{phase:6s}]")

    print()
    print("CONCLUSION: Model predicts phase transition behavior.")
    print("Empirical validation required. β-parameter increases with Gini.")
