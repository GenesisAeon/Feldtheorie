"""LR0 -- local inventory (read-only). Plan: LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md, section 14 (LR0).

Checks, without importing any project module and without changing any file:
- the eleven sources of QUELLENINVENTAR.json in the main checkout AND in this worktree:
  raw bytes, LF-normalised bytes and the git blob of HEAD, kept as SEPARATE hashes; anchor lines;
- the registry ID list (YAML parse only, no matrix);
- SHA-256 of all planning inputs (six original files + review package), referenced unchanged;
- untracked files of the main checkout and the state of all other worktrees (inventory only).

    python experiments/lantern_reconstruction/tools/lr0_inventory.py --out experiments/lantern_reconstruction/lr0/lr0_inventory.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import yaml

PLAN_DIR = Path("D:/mandala/mandala-memory-results/lantern-reconstruction-plan")
MAIN = Path("D:/mandala/Feldtheorie")
HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[3]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(repo: Path, *args: str, binary: bool = False):
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if out.returncode != 0:
        return None
    return out.stdout if binary else out.stdout.decode("utf-8", "replace").strip()


def source_rows(inv: dict) -> list:
    rows = []
    for s in inv["sources"]:
        rel = s["relative_path"]
        row = {"relative_path": rel, "expected": {"raw_sha256_main": s["raw_sha256"], "git_blob_sha256": s["git_blob_sha256"]}}
        for name, repo in (("main", MAIN), ("worktree", WORKTREE)):
            raw = (repo / rel).read_bytes()
            blob = git(repo, "show", f"HEAD:{rel}", binary=True)
            lf = raw.replace(b"\r\n", b"\n")
            row[name] = {"raw_sha256": sha(raw), "lf_sha256": sha(lf), "blob_sha256": sha(blob) if blob is not None else None,
                         "bytes": len(raw), "raw_equals_blob": blob == raw, "lf_equals_blob": blob == lf}
        row["blob_matches_inventory"] = row["main"]["blob_sha256"] == s["git_blob_sha256"] == row["worktree"]["blob_sha256"]
        row["main_raw_matches_inventory"] = row["main"]["raw_sha256"] == s["raw_sha256"]
        text = (MAIN / rel).read_text(encoding="utf-8").splitlines()
        row["anchors"] = [{"line": a["line"], "expected": a["text"],
                           "found": a["text"] in (text[a["line"] - 1] if a["line"] <= len(text) else "")} for a in s["anchors"]]
        rows.append(row)
    return rows


def registry(inv: dict) -> dict:
    rows = yaml.safe_load((WORKTREE / "v9_alpha/config/lantern_hub.yaml").read_text(encoding="utf-8"))["lanterns"]
    ids = [r["id"] for r in rows]
    return {"count": len(ids), "unique": len(set(ids)) == len(ids), "sorted_equals_inventory": sorted(ids) == inv["registry"]["ids_sorted"],
            "yaml_order_differs_from_sorted": ids != sorted(ids), "matrix_calculated": False}


def planning_inputs() -> dict:
    files = {p.name: {"sha256": sha(p.read_bytes()), "bytes": p.stat().st_size} for p in sorted(PLAN_DIR.iterdir()) if p.is_file()}
    sums = {}
    return {"folder": str(PLAN_DIR), "files": files,
            "authoritative": ["LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md", "LANTERN_FACHREVIEW.md"],
            "historical_inputs": ["PLAN_LANTERN_REKONSTRUKTION.md", "CLAUDE_REVIEW.md", "AEON_REVIEW.md", "PLAN_STRUKTUR.json",
                                  "PLAN_STRUKTUR.yaml", "QUELLENINVENTAR.json"], "package_sha256sums_checked": sums}


def untracked_main() -> list:
    lines = git(MAIN, "status", "--porcelain", "--untracked-files=all") or ""
    out = []
    for ln in lines.splitlines():
        if not ln.startswith("?? "):
            continue
        rel = ln[3:]
        p = MAIN / rel
        out.append({"path": rel, "bytes": p.stat().st_size if p.is_file() else None,
                    "is_nested_worktree": rel.startswith(".claude/worktrees/"),
                    "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(p.stat().st_mtime)) if p.exists() else None})
    return out


def worktrees() -> list:
    out, cur = [], {}
    for ln in (git(MAIN, "worktree", "list", "--porcelain") or "").splitlines() + [""]:
        if not ln:
            if cur:
                path = Path(cur["worktree"])
                dirty = git(path, "status", "--porcelain")
                cur["dirty_entries"] = None if dirty is None else len([x for x in dirty.splitlines() if x])
                out.append(cur)
            cur = {}
            continue
        k, _, v = ln.partition(" ")
        cur[k] = v if v else True
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    inv = json.loads((PLAN_DIR / "QUELLENINVENTAR.json").read_text(encoding="utf-8"))
    rows = source_rows(inv)
    result = {
        "schema": "lantern-lr0-inventory-v1", "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": "read-only: file bytes, git blobs, YAML parse; no project import, no matrix, no simulation",
        "main": {"path": str(MAIN), "head": git(MAIN, "rev-parse", "HEAD"), "branch": git(MAIN, "branch", "--show-current"),
                 "tracked_changes": len([x for x in (git(MAIN, "status", "--porcelain", "--untracked-files=no") or "").splitlines() if x])},
        "worktree": {"path": str(WORKTREE), "head": git(WORKTREE, "rev-parse", "HEAD"), "branch": git(WORKTREE, "branch", "--show-current"),
                     "core_autocrlf": git(WORKTREE, "config", "--get", "core.autocrlf")},
        "inventory_repo_head": inv["repo_head"],
        "sources": rows,
        "sources_summary": {"n": len(rows), "blob_matches_inventory": sum(r["blob_matches_inventory"] for r in rows),
                            "main_raw_matches_inventory": sum(r["main_raw_matches_inventory"] for r in rows),
                            "lf_equals_blob_main": sum(r["main"]["lf_equals_blob"] for r in rows),
                            "lf_equals_blob_worktree": sum(r["worktree"]["lf_equals_blob"] for r in rows),
                            "raw_equals_blob_main": sum(r["main"]["raw_equals_blob"] for r in rows),
                            "anchors_found": sum(x["found"] for r in rows for x in r["anchors"]),
                            "anchors_total": sum(len(r["anchors"]) for r in rows)},
        "registry": registry(inv),
        "planning_inputs": planning_inputs(),
        "untracked_main": untracked_main(),
        "worktrees": worktrees(),
        "python": os.sys.version.split()[0],
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(a.out), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: result[k] for k in ("main", "worktree", "sources_summary", "registry")}, indent=1))
    print("untracked in main:", len(result["untracked_main"]), "| worktrees:", len(result["worktrees"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
