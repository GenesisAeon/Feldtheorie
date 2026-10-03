"""M7: build the reproducible review package (plan §11, CLAUDE_START "Fertiges Ergebnis").

Collects into D:/mandala/mandala-memory-results/review/:
  patches (Feldtheorie and unified-mandala vs the plan commits), commit ids,
  SHA-256 of every experiment/view file and every result file, the frozen
  configuration (JSON + YAML twin), raw results (smoke, research +
  evaluation, membrane pilot, explore protocol), resource figures, the
  pytest report (JUnit XML + summary), the mutation report and screenshots.

    python experiments/mandala_memory/tools/make_review_package.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
FT = EXP.parents[1]
UM = Path(r"D:/mandala/.worktrees/unified-mandala-memory-lab")
RES = Path(r"D:/mandala/mandala-memory-results")
OUT = RES / "review"
SHOTS = Path(r"D:/mandala/.tmp/mandala-memory/shots")
PLAN = {"Feldtheorie": "0e46ec88181b430c41330016279a8bd1ea2c0d9b", "unified-mandala": "a76052842cbb9e6cb5ba70b36b1350feb35ad70a"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(repo: Path, *args) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8").stdout


def yaml_dump(obj, indent=0) -> str:
    pad = "  " * indent
    if isinstance(obj, dict):
        lines = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{k}:\n{yaml_dump(v, indent + 1)}")
            else:
                lines.append(f"{pad}{k}: {json.dumps(v, ensure_ascii=False)}")
        return "\n".join(lines)
    if isinstance(obj, list):
        if all(not isinstance(v, (dict, list)) for v in obj):
            return "\n".join(f"{pad}- {json.dumps(v, ensure_ascii=False)}" for v in obj)
        return "\n".join(f"{pad}-\n{yaml_dump(v, indent + 1)}" for v in obj)
    return f"{pad}{json.dumps(obj, ensure_ascii=False)}"


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "patches").mkdir(parents=True)
    (OUT / "results").mkdir()
    env = {**os.environ, "PYTHONPATH": str(FT), "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "2",
           "TMP": r"D:/mandala/.tmp/mandala-memory", "TEMP": r"D:/mandala/.tmp/mandala-memory"}

    # 1) frozen configuration, JSON + YAML twin (Feldtheorie trilayer rule)
    cfg_path = EXP / "protocol" / "startkonfiguration.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    shutil.copy2(cfg_path, OUT / "startkonfiguration.json")
    (OUT / "startkonfiguration.yaml").write_text("# YAML twin of startkonfiguration.json (generated)\n" + yaml_dump(cfg) + "\n", encoding="utf-8")

    # 2) patches and commits
    for name, repo in (("Feldtheorie", FT), ("unified-mandala", UM)):
        (OUT / "patches" / f"{name}.patch").write_text(git(repo, "diff", "--binary", PLAN[name], "HEAD"), encoding="utf-8")
    commits = {name: {"plan_commit": PLAN[name], "head": git(repo, "rev-parse", "HEAD").strip(),
                      "branch": git(repo, "branch", "--show-current").strip(),
                      "log": git(repo, "log", "--oneline", f"{PLAN[name]}..HEAD").strip().splitlines()}
               for name, repo in (("Feldtheorie", FT), ("unified-mandala", UM))}

    # 3) tests (JUnit) and mutation report
    junit = OUT / "pytest_report.xml"
    t = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={junit}",
                        str(EXP / "tests")], cwd=FT, env=env, capture_output=True, text=True)
    (OUT / "pytest_summary.txt").write_text(t.stdout[-4000:], encoding="utf-8")
    m = subprocess.run([sys.executable, str(EXP / "tools" / "mutation_check.py"), "--out", str(OUT / "mutation_report.json")],
                       cwd=FT, env=env, capture_output=True, text=True)
    (OUT / "mutation_summary.txt").write_text(m.stdout[-4000:], encoding="utf-8")

    # 4) results and screenshots (copies; originals untouched)
    for sub in ("smoke", "research", "membrane_pilot"):
        if (RES / sub).exists():
            shutil.copytree(RES / sub, OUT / "results" / sub)
    if (RES / "explore" / "protocol.jsonl").exists():
        (OUT / "results" / "explore").mkdir()
        shutil.copy2(RES / "explore" / "protocol.jsonl", OUT / "results" / "explore" / "protocol.jsonl")
    if SHOTS.exists():
        shutil.copytree(SHOTS, OUT / "screenshots")

    # 5) resources from the result files
    resources = {}
    for sub in ("smoke", "research"):
        for f in (RES / sub).glob(f"{sub}-*.json"):
            if ".evaluation" in f.name:        # evaluation files (incl. versioned ones) are not runs
                continue
            r = json.loads(f.read_text(encoding="utf-8"))
            resources[r["run_id"]] = {"status": r["status"], "seeds": len(r["seeds"]), "failed": r["failed_seeds"], **r["resources"],
                                      "size_bytes": f.stat().st_size}

    # 6) file hashes
    hashes = {}
    for base, root in (("Feldtheorie/experiments/mandala_memory", EXP), ("unified-mandala/experiments/memory_lab", UM / "experiments" / "memory_lab")):
        for p in sorted(root.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                hashes[f"{base}/{p.relative_to(root).as_posix()}"] = sha(p)
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            hashes[f"review/{p.relative_to(OUT).as_posix()}"] = sha(p)

    manifest = {"schema": "mandala-memory-review-v1", "commits": commits, "resources": resources,
                "tests_exit_code": t.returncode, "mutation_exit_code": m.returncode,
                "python": sys.version.split()[0], "sha256": hashes}
    (OUT / "REVIEW_MANIFEST.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.copy2(EXP / "README.md", OUT / "README.md")
    print(json.dumps({"review_dir": str(OUT), "tests_exit": t.returncode, "mutation_exit": m.returncode,
                      "files": len(hashes), "heads": {k: v["head"][:10] for k, v in commits.items()}}, indent=1))
    return 0 if t.returncode == 0 and m.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
