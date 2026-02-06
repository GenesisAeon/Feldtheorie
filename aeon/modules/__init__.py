"""Aeon core module prototypes and architecture contracts."""

from aeon.modules.architecture_spec import (
    CORE_MODULE_REGISTRY,
    extract_aeon_layers,
    get_core_module_contracts,
)
from aeon.modules.genesis_orchestrator import GenesisOrchestrator
from aeon.modules.knowledge_system import KnowledgeSystem

__all__ = [
    "CORE_MODULE_REGISTRY",
    "extract_aeon_layers",
    "get_core_module_contracts",
    "GenesisOrchestrator",
    "KnowledgeSystem",
]
