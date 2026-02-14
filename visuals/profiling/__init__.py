"""AFET Visual Profiling Hub — Quad-Layer Component 4.

Generates spatial/topological snapshots of the AFET field state.
"""

from .profiling_generator import FieldMetrics, ProfilingGenerator, load_symbols

__all__ = ["FieldMetrics", "ProfilingGenerator", "load_symbols"]
