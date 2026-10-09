"""Baseline repro R1 (software not enforced at research-run creation) and R4 (candidate test vs. Python 3.12).
Synthetic freeze fixture in a temp folder only; execute() is never called."""
import json, sys, tempfile
from pathlib import Path
from unittest.mock import patch
ROOT = Path("D:/mandala/.worktrees/feldtheorie-lantern-reconstruction")
sys.path.insert(0, str(ROOT))
from experiments.lantern_reconstruction import runs, artifacts
tmp = Path(tempfile.mkdtemp(prefix="r1_", dir="C:/Users/Privat/.claude/jobs/bc57132d/tmp"))
cand = json.loads(runs.CANDIDATE_FILE.read_text(encoding="utf-8"))
cp = tmp / "cand.json"; cp.write_bytes(runs.CANDIDATE_FILE.read_bytes())
fp = tmp / "freeze.json"
fp.write_text(json.dumps({"schema": runs.FREEZE_SCHEMA, "status": "frozen", "approved_by": ["SYNTHETIC TEST FIXTURE -- NO APPROVAL"],
                          "candidate_sha256": artifacts.sha256(cp.read_bytes().replace(b"\r\n", b"\n")), "code_identity": cand["code_identity"]}))
wrong = {"python": "3.12.14", "numpy": "2.2.6", "scipy": "1.15.3"}
out = {"code_identity": runs.code_identity()["identity"], "candidate_software": cand["software"], "actual": runs.software()}
with patch.object(runs, "CANDIDATE_FILE", cp), patch.object(runs, "FREEZE_FILE", fp), patch.object(runs, "software", lambda: dict(wrong)):
    try:
        rd = runs.create_research_run(tmp / "runs", run_id="synthetic-not-executed")
        m = runs.load_run(rd); runs.check_resumable(m)
        out["R1"] = {"created": True, "manifest_software": m["software"], "check_resumable": "accepted", "status": runs.status(rd)}
    except Exception as e:
        out["R1"] = {"created": False, "error": f"{type(e).__name__}: {e}"}
with patch.object(runs, "software", lambda: dict(wrong)):
    out["R4"] = {"candidate_software_equals_runtime_under_3.12": cand["software"] == runs.software()}
print(json.dumps(out, indent=1))
