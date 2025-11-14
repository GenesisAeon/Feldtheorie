"""
UTAC V3 Data Adapters
Phase 4, Week 1-2: Real Data Integration

This package provides adapters for fetching and transforming real-world
data into UTAC-compatible formats.

Available Adapters:
- GRACEAdapter: WAIS ice mass (NASA JPL GRACE Tellus)
- RAPIDAdapter: AMOC transport (RAPID-MOCHA array)
- NOAAAdapter: Coral SST (NOAA OISST)

Author: Claude (MOR Agent)
Date: 2025-11-14
Version: 0.1.0
"""

from .base_adapter import BaseAdapter, UTACState, EWSSignals
from .grace_adapter import GRACEAdapter
from .rapid_adapter import RAPIDAdapter
from .noaa_adapter import NOAAAdapter

__all__ = [
    'BaseAdapter',
    'UTACState',
    'EWSSignals',
    'GRACEAdapter',
    'RAPIDAdapter',
    'NOAAAdapter'
]

__version__ = '0.1.0'
