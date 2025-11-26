"""Wavefunction Pipeline for V6 Framework.

This module provides entropic wavefunction computations for the UTAC framework,
bridging quantum mechanics and entropic governance.

Main Components:
----------------
- PsiField: Core wavefunction ψ_genesis(r,θ,φ,t) computation
- PsiFieldPipeline: Complete workflow for UTAC integration
- compute_psi_genesis: Convenience function for quick access

Usage:
------
>>> from pipelines.wavefunction import compute_psi_genesis, PsiFieldPipeline
>>>
>>> # Quick computation
>>> r = np.linspace(0, 10, 100)
>>> psi = compute_psi_genesis(r, theta=np.pi/2, phi=0)
>>>
>>> # Full pipeline
>>> pipeline = PsiFieldPipeline()
>>> results = pipeline.run()

Version: v6.0.0-alpha
"""

from .psi_field import (
    PsiField,
    PsiFieldConfig,
    PsiFieldPipeline,
    compute_psi_genesis,
    ALPHA_INV,
    PHI,
    L_PLANCK,
    E_PLANCK,
    HBAR,
)

__all__ = [
    'PsiField',
    'PsiFieldConfig',
    'PsiFieldPipeline',
    'compute_psi_genesis',
    'ALPHA_INV',
    'PHI',
    'L_PLANCK',
    'E_PLANCK',
    'HBAR',
]

__version__ = 'v6.0.0-alpha'
