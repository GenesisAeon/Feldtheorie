"""
FIT τ* (tau-star) Safety-Delay Pipeline

Provides RK4-compatible safety delay mechanisms for Type-VI implosive
field simulations (ζ<0 scenarios).

Formal:
    τ* = 0.1 · |Θ - R| acts as temporal buffer before activation threshold,
    preventing instantaneous collapse in implosive dynamics.

Empirical:
    Integrates with RK4 solvers in simulation/ and analysis/ modules to
    introduce controlled delay in field evolution.

Poetic:
    Die Zeit zögert, wenn das Feld implodiert – τ* ist der Atem vor dem Sturz.

References:
    - V6_ToDoListe.md v6-activation-gaps (Priority 2)
    - activation_gaps_tau_star.md
    - FinalyzeVorschlägeChatGPT5.1Agent.txt L53-L64
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = [
    "compute_tau_star",
    "apply_safety_delay",
    "compute_zeta_risk",
    "rk4_step_with_tau_star",
]

from .tau_star_delay import (
    apply_safety_delay,
    compute_tau_star,
    compute_zeta_risk,
    rk4_step_with_tau_star,
)
