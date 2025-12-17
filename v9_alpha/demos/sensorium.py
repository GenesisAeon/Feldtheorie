#!/usr/bin/env python3
"""Sensorium re-export for legacy demos.

This file routes the legacy demo imports to the modularized implementation in
`v9_alpha.models.sensorium`, keeping Trilayer semantics intact while avoiding
code drift between demos and library.
"""

from v9_alpha.models.sensorium import DataStream, MultiStreamLoader, load_stream_configs

__all__ = ["DataStream", "MultiStreamLoader", "load_stream_configs"]
