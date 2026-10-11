"""V0: integrity of the cosmic-inheritance register in the SF-001 roadmap.

Run explicitly (root pytest only collects tests/):

    python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests

Every source reference names a pinned commit, a path, a line and a snippet.
The snippet is checked against ``git show <commit>:<path>`` at that line, so
the references stay valid after later packages edit the files. References into
the neighbouring repositories are checked when a checkout is found next to this
repository or below KV_EXTERNAL_REPOS (otherwise skipped with a reason).
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
ROADMAP_DIR = REPO / "experiments" / "research_roadmap_2026"
FINDINGS = [f"F{i}" for i in range(1, 9)]
PACKAGES = [f"V{i}" for i in range(8)] + ["T6"]
FINDING_STATUS = {"reproduced_locally", "confirmed_by_code_reading", "open", "fixed"}


def _load_json():
    return json.loads((ROADMAP_DIR / "roadmap.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def register():
    return _load_json()["cosmic_inheritance"]


def _all_refs(register):
    for group in ("findings", "observations"):
        for item in register[group]:
            for ref in item["sources"]:
                yield item["id"], ref
    for group in ("parameters", "units"):
        for item in register[group]:
            if item["source"] is not None:
                yield item.get("name", item.get("scope")), item["source"]


def _external_root(repo_name):
    candidates = []
    if os.environ.get("KV_EXTERNAL_REPOS"):
        candidates.append(Path(os.environ["KV_EXTERNAL_REPOS"]) / repo_name)
    # main checkout D:/mandala/Feldtheorie or worktree D:/mandala/.worktrees/<name>
    candidates += [REPO.parent / repo_name, REPO.parent.parent / repo_name]
    for path in candidates:
        if (path / ".git").exists():
            return path
    return None


def _git_show(repo_dir, commit, path):
    out = subprocess.run(
        ["git", "-C", str(repo_dir), "show", f"{commit}:{path}"],
        capture_output=True, check=False,
    )
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8").splitlines()


def test_json_and_yaml_layers_are_identical():
    from_yaml = yaml.safe_load((ROADMAP_DIR / "roadmap.yaml").read_text(encoding="utf-8"))
    assert from_yaml == _load_json()


def test_every_plan_finding_is_registered_once(register):
    ids = [f["id"] for f in register["findings"]]
    assert ids == FINDINGS


@pytest.mark.parametrize("group", ["findings", "observations"])
def test_every_entry_has_source_status_and_next_step(register, group):
    package_ids = {p["id"] for p in register["packages"]}
    for item in register[group]:
        assert item["sources"], item["id"]
        assert item["status"] in FINDING_STATUS, item["id"]
        assert item["next_step"].strip(), item["id"]
        assert item["evidence"].strip(), item["id"]
        assert item["fix_package"] in package_ids | {"open_decision", "none_by_decision"}, item["id"]
        if item["status"] == "fixed":
            assert item["resolution"].strip(), item["id"]


def test_packages_cover_plan_and_map_to_existing_tasks(register):
    data = _load_json()
    task_ids = [t["id"] for t in data["tasks"]]
    assert [p["id"] for p in register["packages"]] == PACKAGES
    for pid in PACKAGES:
        assert task_ids.count(pid) == 1, pid
    # SF-001: V2 realises the existing S00/S01, no competing task ids.
    for task in data["tasks"]:
        if task["id"] in ("S00", "S01"):
            assert task["realized_by"] == "V2"
    v2 = next(p for p in register["packages"] if p["id"] == "V2")
    assert v2["realizes"] == ["S00", "S01"]


def test_delivery_claims_follow_package_order(register):
    # Packages are delivered in order; nothing after the first undelivered one.
    statuses = [p["status"] for p in register["packages"] if p["id"].startswith("V")]
    delivered = ["delivered" in s for s in statuses]
    assert delivered[0]
    assert delivered == sorted(delivered, reverse=True)


def test_decisions_are_recorded(register):
    by_id = {i["id"]: i for i in register["findings"] + register["observations"]}
    assert by_id["F6"]["fix_package"] == by_id["N3"]["fix_package"] == "none_by_decision"
    assert next(p for p in register["packages"] if p["id"] == "T6")["status"] == "deferred_other_session"
    assert len(register["decisions"]) >= 4


def test_each_finding_is_assigned_to_its_fix_package(register):
    packages = {p["id"]: p for p in register["packages"]}
    for item in register["findings"] + register["observations"]:
        target = item["fix_package"]
        if target in packages and target != "V0":
            assert item["id"] in packages[target]["findings"], (item["id"], target)


def test_feldtheorie_source_lines_match_pinned_commit(register):
    checked = 0
    for owner, ref in _all_refs(register):
        if ref["repo"] != "Feldtheorie":
            continue
        lines = _git_show(REPO, ref["commit"], ref["path"])
        if lines is None:
            pytest.skip(f"commit {ref['commit'][:10]} not available in this clone")
        assert ref["contains"] in lines[ref["line"] - 1], (owner, ref["path"], ref["line"])
        checked += 1
    assert checked >= 30


@pytest.mark.parametrize("repo_name", ["implosive-origin-utac", "unified-mandala"])
def test_external_source_lines_match_pinned_commit(register, repo_name):
    refs = [(o, r) for o, r in _all_refs(register) if r["repo"] == repo_name]
    assert refs
    repo_dir = _external_root(repo_name)
    if repo_dir is None:
        pytest.skip(f"{repo_name} checkout not found (set KV_EXTERNAL_REPOS)")
    for owner, ref in refs:
        lines = _git_show(repo_dir, ref["commit"], ref["path"])
        assert lines is not None, (owner, ref["commit"], ref["path"])
        assert ref["contains"] in lines[ref["line"] - 1], (owner, ref["path"], ref["line"])


def test_markdown_layer_names_every_finding_and_package(register):
    text = (ROADMAP_DIR / "ROADMAP.md").read_text(encoding="utf-8")
    section = text.split("## Kosmische Vererbung", 1)
    assert len(section) == 2, "V0 section missing in ROADMAP.md"
    body = section[1]
    for item in register["findings"] + register["observations"] + register["packages"]:
        assert f"| {item['id']} |" in body, item["id"]
    for gate in ("V4", "V6"):
        assert gate in body
    assert "explorativ" in body and "retrospektiv" in body
