"""Wavefunction Pipeline for V6 Framework.

This module provides entropic wavefunction computations for the UTAC framework,
bridging quantum mechanics and entropic governance.

Main Components:
----------------
- PsiField: Core wavefunction ψ_genesis(r,θ,φ,t) computation
- PsiFieldConfig: Configuration for ψ-field parameters
- PsiFieldPipeline: Complete workflow for UTAC integration
- compute_psi_genesis: Convenience function for quick access

Usage:
------
>>> from pipelines.wavefunction import PsiField, compute_psi_genesis
>>>
>>> # Quick computation
>>> psi = compute_psi_genesis(r=1.0, theta=np.pi/2, phi=0)
>>>
>>> # Full pipeline
>>> pipeline = PsiFieldPipeline()
>>> results = pipeline.run()

Version: v6.0.0-alpha
"""

from .psi_field import (
    ALPHA_INV,
    E_PLANCK,  # Legacy alias
    HBAR,
    L_PLANCK,  # Legacy alias
    PHI,
    PLANCK_ENERGY,
    PLANCK_LENGTH,
    PsiField,
    PsiFieldConfig,
    PsiFieldPipeline,
    compute_psi_genesis,
)

__all__ = [
    "PsiField",
    "PsiFieldConfig",
    "PsiFieldPipeline",
    "compute_psi_genesis",
    "ALPHA_INV",
    "PHI",
    "PLANCK_LENGTH",
    "PLANCK_ENERGY",
    "HBAR",
    "L_PLANCK",
    "E_PLANCK",
]

__version__ = "v6.0.0-alpha"
