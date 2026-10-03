"""Scratch folders for tests: unchanged on the Windows lab (D:/mandala/.tmp, the
assignment keeps all data on D:), the system temp folder elsewhere. Never a
relative "D:/..." path, which on POSIX would silently create a folder named
"D:" in the working directory."""
import os
import sys
import tempfile
from pathlib import Path


def lab_layout_present() -> bool:
    return sys.platform == "win32" and os.path.isdir("D:/mandala")


def scratch(*parts: str) -> Path:
    base = (Path(r"D:/mandala/.tmp/mandala-memory/test-results") if lab_layout_present()
            else Path(tempfile.gettempdir()) / "mandala-memory-test-results")
    return base.joinpath(*parts)
