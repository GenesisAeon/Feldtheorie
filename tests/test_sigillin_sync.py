"""Regression tests for :mod:`scripts.sigillin_sync`."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from scripts import sigillin_sync


@pytest.fixture
def codex_trilayer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary Codex trilayer and re-point the module globals."""

    codex_base = tmp_path / "codexfeedback"
    md_path = codex_base.with_suffix(".md")
    json_path = codex_base.with_suffix(".json")
    yaml_path = codex_base.with_suffix(".yaml")

    md_path.write_text("# Codex Test\n", encoding="utf-8")
    json_path.write_text(json.dumps({"meta": {}, "entries": []}, indent=2), encoding="utf-8")
    yaml_path.write_text("meta: {}\nentries: []\n", encoding="utf-8")

    monkeypatch.setattr(sigillin_sync, "CODEX_BASE", codex_base)
    monkeypatch.setattr(sigillin_sync, "CODEx_MD_PATH", md_path)
    monkeypatch.setattr(sigillin_sync, "CODEx_JSON_PATH", json_path)
    monkeypatch.setattr(sigillin_sync, "CODEx_YAML_PATH", yaml_path)

    return codex_base


def test_append_codex_entry_respects_entries_list(codex_trilayer: Path) -> None:
    """The Codex append helper should extend the ``entries`` list only."""

    envelope = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "counts": {"total": 3},
        }
    }

    sigillin_sync.append_codex_entry(envelope, "test-run-001", "Regression coverage for entries list")

    md_contents = sigillin_sync.CODEx_MD_PATH.read_text(encoding="utf-8")
    assert "test-run-001" in md_contents

    json_payload = json.loads(sigillin_sync.CODEx_JSON_PATH.read_text(encoding="utf-8"))
    assert isinstance(json_payload["entries"], list)
    assert json_payload["entries"][-1]["id"] == "test-run-001"

    yaml_payload = yaml.safe_load(sigillin_sync.CODEx_YAML_PATH.read_text(encoding="utf-8"))
    assert isinstance(yaml_payload["entries"], list)
    assert yaml_payload["entries"][-1]["id"] == "test-run-001"

