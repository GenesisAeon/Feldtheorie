"""Phase 4 research modules energized by HEX_RESONANCE_BETA.

The package bundles Doppler-style experiments for solitons, chimera networks,
cosmic information gradients, and pressure modulation of v_RIG. Each module
keeps σ(β(R-Θ)) explicit and reports telemetries suitable for ΔAIC
falsifiability checks.

Modules:
- soliton_doppler: Neural field standing waves
- chimera_network: Chaos-synchronization coexistence
- cosmic_doppler: Hex-quantized information density
- pressure_modulation: Medium-dependent v_RIG modulation (HPNS/Narkose)
"""

from simulation.phase4.soliton_doppler import (
    SolitonDopplerConfig,
    simulate_soliton_doppler,
)
from simulation.phase4.pressure_modulation import (
    PressureModulationConfig,
    PressureModulator,
    simulate_pressure_modulation,
)

__all__ = [
    "SolitonDopplerConfig",
    "simulate_soliton_doppler",
    "PressureModulationConfig",
    "PressureModulator",
    "simulate_pressure_modulation",
]
