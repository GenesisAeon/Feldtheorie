"""Run test_lr6.py in the Lantern worktree. --sim312: SIMULATE Python 3.12.14 (platform.python_version only).
Extra args are passed to pytest."""
import os
import platform
import sys

ROOT = "D:/mandala/.worktrees/feldtheorie-lantern-reconstruction"
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.dont_write_bytecode = True
args = sys.argv[1:]
if "--sim312" in args:
    args.remove("--sim312")
    platform.python_version = lambda: "3.12.14"
    print("SIMULATED platform.python_version() = 3.12.14 (real interpreter:", sys.version.split()[0] + ")")
import pytest  # noqa: E402

raise SystemExit(pytest.main(["experiments/lantern_reconstruction/tests/test_lr6.py", "-q", "-p", "no:cacheprovider", "--color=no", *args]))
