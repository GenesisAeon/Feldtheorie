"""AFET Visual Profiling Hub — Quad-Layer Component 4.

Generates spatial/topological snapshots of the AFET field state.
"""

from .profiling_generator import FieldMetrics, ProfilingGenerator, load_symbols
from .live_dashboard import compute_consciousness_score, run_dashboard

__all__ = [
    "FieldMetrics",
    "ProfilingGenerator",
    "compute_consciousness_score",
    "load_symbols",
    "run_dashboard",
]
