"""
Aeon Agent Layer - Individual Consciousness Modules
===================================================

The Agent Layer provides individual consciousness modules that
can be coordinated through the AeonShell and Collective Field.

This module implements:
- SemanticAgent: Individual consciousness nodes
- Collective coordination interface
- Agent-to-agent communication
- Resonance-based synchronization

Integration Points:
------------------
- Collective Field Module (models/collective_field.py)
- Sigillin Kernel (api/sigillin_kernel.py)
- Nullkern (aeon/nullkern/zero_point_kernel.py)

References:
----------
- Collective Field Module docs
- Sigillin Founding Protocol
- V7 Phase 2 implementation
"""

from aeon.agents.semantic_agent import SemanticAgent, RecursiveCoupler
from aeon.agents.collective_interface import CollectiveInterface

__all__ = ["SemanticAgent", "RecursiveCoupler", "CollectiveInterface"]
