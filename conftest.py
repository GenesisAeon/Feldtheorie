"""Root pytest configuration.

Excludes directories that are not part of the main test suite from collection.
v9_alpha has its own test configuration and should be run separately.
simulation/ contains standalone scripts, not pytest-compatible tests.
"""

collect_ignore_glob = [
    "v9_alpha/*",
    "simulation/*",
    "releases/*",
    "v3/*",
    "v10_oracle/*",
    "v11_gardener/*",
    "vr/*",
    "science/tests/*",
    "analysis/implosion/*",
    "science/analysis/implosion/*",
]
