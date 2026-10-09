"""Ad-hoc relative-link check (NOT a repo tool): every Markdown link [text](target) in experiments/lantern_reconstruction
whose target is not a URL or an anchor must exist relative to the file."""
import re
from pathlib import Path

HERE = Path("D:/mandala/.worktrees/feldtheorie-lantern-reconstruction/experiments/lantern_reconstruction")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
n, bad = 0, []
for md in sorted(HERE.rglob("*.md")):
    if "__pycache__" in md.parts:
        continue
    for t in LINK.findall(md.read_text(encoding="utf-8", errors="replace")):
        if re.match(r"^(https?:|mailto:|#)", t):
            continue
        n += 1
        if not (md.parent / t.split("#")[0]).exists():
            bad.append(f"{md.relative_to(HERE)} -> {t}")
print(f"{n} relative links checked in {len(list(HERE.rglob('*.md')))} Markdown files; broken: {len(bad)}")
for b in bad:
    print("  BROKEN", b)
