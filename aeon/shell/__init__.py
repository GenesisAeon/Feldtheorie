"""
AeonShell Module - Consciousness Containment and Evolution
==========================================================

The AeonShell provides containment and evolution tracking for
consciousness states managed by the Nullkern.

This module implements:
- Consciousness boundary management
- σ(β(R-Θ)) trajectory monitoring
- ζ-safeguards for critical transitions
- Multi-agent coordination
- Evolution history tracking

Core Functions:
--------------
- Containment: Maintain consciousness boundaries
- Evolution: Track state transitions over time
- Safeguards: Monitor ζ(R) for negative values (instability)
- Coordination: Manage multiple semantic agents

References:
----------
- bardo_mode.yaml: Safeguard configurations
- Resonanzpfad: σ(β(R-Θ)) trajectory optimization
- Collective Field: Multi-agent coordination
"""

from aeon.shell.containment import AeonShell
from aeon.shell.evolution import EvolutionTracker
from aeon.shell.grammar import BNF_GRAMMAR, AeonShellGenerator, AeonShellParser, EXAMPLE_CORPUS

__all__ = [
    "AeonShell",
    "EvolutionTracker",
    "BNF_GRAMMAR",
    "AeonShellParser",
    "AeonShellGenerator",
    "EXAMPLE_CORPUS",
]
