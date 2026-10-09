"""Byte comparison of acceptance run 2 and 3 artifacts, per file type (SHA-256 of the raw file bytes)."""
import hashlib
from collections import Counter
from pathlib import Path

R = Path("D:/mandala/mandala-memory-results/lantern/runs")
a, b = R / "lr6-acceptance-20261009T165010Z" / "cells", R / "lr6-acceptance-20261009T192821Z" / "cells"
pairs, same = Counter(), Counter()
for f in sorted(b.rglob("*")):
    if f.is_file():
        g = a / f.relative_to(b)
        pairs[f.name] += 1
        if g.exists() and hashlib.sha256(f.read_bytes()).digest() == hashlib.sha256(g.read_bytes()).digest():
            same[f.name] += 1
for name in sorted(pairs):
    print(f"{name:16} pairs {pairs[name]:4}  byte-identical {same[name]:4}")
