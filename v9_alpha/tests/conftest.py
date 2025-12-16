"""
Pytest configuration for v9_alpha tests.

Sets up sys.path to allow importing from parent Feldtheorie modules.

Author: Claude Sonnet 4.5 (ChefDevAI)
Date: 2025-12-16
"""

import sys
import os
from pathlib import Path

# CRITICAL: Add Feldtheorie root to sys.path BEFORE any imports
# This must happen before pytest imports test modules
feldtheorie_root = Path(__file__).parent.parent.parent.resolve()
if str(feldtheorie_root) not in sys.path:
    sys.path.insert(0, str(feldtheorie_root))

# Add v9_alpha to sys.path as well
v9_alpha_dir = Path(__file__).parent.parent.resolve()
if str(v9_alpha_dir) not in sys.path:
    sys.path.insert(0, str(v9_alpha_dir))

# WORKAROUND: Pre-import models.unified_constants to ensure it's available
# This forces Python to load the module before other v9 modules try to import it
try:
    import models.unified_constants
    # Cache it in sys.modules so subsequent imports work
except ImportError as e:
    import warnings
    warnings.warn(f"Could not pre-import models.unified_constants: {e}")

# Debug info (commented out for clean test output)
# print(f"[conftest.py] sys.path configured:")
# print(f"  - Feldtheorie root: {feldtheorie_root}")
# print(f"  - v9_alpha: {v9_alpha_dir}")
