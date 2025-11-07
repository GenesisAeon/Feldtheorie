"""Tests for the sigillin_sync telemetry harness."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from scripts import sigillin_sync


def _prepare_codex_trilayer(base: Path) -> None:
    """Create a minimal codexfeedback tri-layer for testing."""

    md_path = base.with_suffix(".md")
    json_path = base.with_suffix(".json")
    yaml_path = base.with_suffix(".yaml")

    md_path.write_text("# Codexfeedback Test\n", encoding="utf-8")
    json_path.write_text(json.dumps({"entries": [{"id": "existing"}]}), encoding="utf-8")
    yaml_path.write_text("entries:\n  - id: existing\n", encoding="utf-8")


def test_append_codex_entry_appends_to_entries(tmp_path, monkeypatch):
    codex_base = tmp_path / "codexfeedback"
    _prepare_codex_trilayer(codex_base)

    md_path = codex_base.with_suffix(".md")
    json_path = codex_base.with_suffix(".json")
    yaml_path = codex_base.with_suffix(".yaml")

    monkeypatch.setattr(sigillin_sync, "CODEx_MD_PATH", md_path)
    monkeypatch.setattr(sigillin_sync, "CODEx_JSON_PATH", json_path)
    monkeypatch.setattr(sigillin_sync, "CODEx_YAML_PATH", yaml_path)

    envelope = {
        "meta": {
            "generated_at": "2025-01-01T00:00:00+00:00",
            "counts": {"total": 3},
        }
    }

    sigillin_sync.append_codex_entry(envelope, "sync-test-0001", "Ensuring entries list is used")

    codex_json = json.loads(json_path.read_text(encoding="utf-8"))
    assert [entry["id"] for entry in codex_json["entries"]] == ["existing", "sync-test-0001"]

    codex_yaml = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert [entry["id"] for entry in codex_yaml["entries"]] == ["existing", "sync-test-0001"]

    md_content = md_path.read_text(encoding="utf-8")
    assert "sync-test-0001" in md_content
