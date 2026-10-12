"""Entry point to actually execute test_predictive.py's real 25 checks on
Windows, via windows_posix_shim (see that file for exactly what is and is not
covered by this workaround)."""
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import windows_posix_shim  # noqa: F401  (must run before importing test_predictive)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                 "experiments", "geometric_waste_predictive_v2"))

import test_predictive  # noqa: E402

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_predictive)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
