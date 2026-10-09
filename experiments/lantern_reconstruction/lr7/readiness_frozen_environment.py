"""Read-only operational readiness facts for the LR7 pre-start review. Creates nothing, starts nothing."""
import ctypes
import json
import platform
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "D:/mandala/.worktrees/feldtheorie-lantern-reconstruction")
from experiments.lantern_reconstruction import registry_adapter as ra, runs  # noqa: E402

out = {"readiness": runs.research_readiness()}
cand = json.loads(runs.CANDIDATE_FILE.read_text(encoding="utf-8"))
du = shutil.disk_usage("D:/")
need = cand["budget"]["extrapolated_research"]["artifact_bytes"]
out["disk_D"] = {"free_bytes": du.free, "extrapolated_artifacts_bytes": need, "ratio_free_to_needed": round(du.free / need, 1)}


class MEMSTAT(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


m = MEMSTAT(); m.dwLength = ctypes.sizeof(MEMSTAT)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
out["ram"] = {"total_bytes": m.ullTotalPhys, "available_bytes": m.ullAvailPhys, "draft_budget_bytes": cand["budget"]["draft"]["ram_bytes"]}


class SPS(ctypes.Structure):
    _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte), ("BatteryLifePercent", ctypes.c_ubyte),
                ("SystemStatusFlag", ctypes.c_ubyte), ("BatteryLifeTime", ctypes.c_ulong), ("BatteryFullLifeTime", ctypes.c_ulong)]


s = SPS()
ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s))
out["power"] = {"ac_line": {0: "offline (battery)", 1: "online", 255: "unknown"}.get(s.ACLineStatus, s.ACLineStatus),
                "battery_percent": s.BatteryLifePercent}
locks = runs.RESULTS / "runs" / "_locks"
out["locks"] = sorted(p.name for p in locks.iterdir()) if locks.exists() else []
runs_dir = runs.RESULTS / "runs"
out["existing_runs"] = sorted(p.name for p in runs_dir.iterdir() if p.is_dir() and p.name != "_locks")
out["research_runs_existing"] = [n for n in out["existing_runs"] if not n.startswith("lr6-acceptance-")]
snap = ra.load_verified_snapshot()                     # FULL check incl. the original Git history
out["registry_snapshot"] = {"canonical_sha256": snap.canonical_sha256, "matches_candidate":
                            snap.canonical_sha256 == cand["sources"]["registry_snapshot"]["canonical_sha256"]
                            and snap.manifest_sha256 == cand["sources"]["registry_snapshot"]["manifest_sha256"],
                            "check": "load_verified_snapshot() with the default repo (Git history check active)"}
out["host"] = {"node": platform.node(), "platform": platform.platform()}
print(json.dumps(out, indent=1, ensure_ascii=False))
