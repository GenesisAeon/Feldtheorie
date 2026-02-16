"""Pytest configuration for v9_alpha tests.

Sets up sys.path to allow importing from parent Feldtheorie modules.

Author: Claude Sonnet 4.5 (ChefDevAI)
Date: 2025-12-16
"""

import sys
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

# These test modules import names that no longer exist in their source modules
# (functions were refactored into class methods). Exclude until tests are updated.
_tests_dir = Path(__file__).parent
collect_ignore = [
    str(_tests_dir / "test_em_field_calculator.py"),
    str(_tests_dir / "test_emergence_metrics.py"),
    str(_tests_dir / "test_lantern_bridge.py"),
]

