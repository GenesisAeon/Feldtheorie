"""Core utilities for the UATC Chronicle system."""

from .chronicle import AgentLog, ResourceOrigin, TheChronicle

# Import agent_kernel only if numpy is available (for backwards compatibility)
try:
    from .agent_kernel import ExistenceScale, UATCAgent  # noqa: F401
    _HAS_AGENT_KERNEL = True
except ImportError:
    _HAS_AGENT_KERNEL = False

# Import ouroboros_engine (doesn't require numpy)
from .ouroboros_engine import OuroborosEngine, get_engine

__all__ = [
    "AgentLog",
    "ResourceOrigin",
    "TheChronicle",
    "OuroborosEngine",
    "get_engine",
]

if _HAS_AGENT_KERNEL:
    __all__.extend(["ExistenceScale", "UATCAgent"])
