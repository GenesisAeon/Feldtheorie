"""Tests for the sigillin_sync telemetry harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
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


def _create_trilayer(base: Path, sigil: str, version: str, updated: str) -> None:
    """Create a complete trilayer with given metadata."""
    yaml_path = base.with_suffix(".yaml")
    json_path = base.with_suffix(".json")
    md_path = base.with_suffix(".md")

    yaml_data = {
        "meta": {
            "sigil": sigil,
            "version": version,
            "updated": updated,
        },
        "content": "test content",
    }
    json_data = {
        "meta": {
            "version": version,
            "updated": updated,
        },
        "content": "test content",
    }

    yaml_path.write_text(yaml.dump(yaml_data, allow_unicode=True), encoding="utf-8")
    json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(f"# {sigil}\n\nTest content\n", encoding="utf-8")


# ============================================================================
# Test: discover_trilayers()
# ============================================================================


def test_discover_trilayers_finds_complete_sets(tmp_path):
    """Test that discover_trilayers finds complete YAML+JSON+MD sets."""
    root = tmp_path / "seed"
    root.mkdir()

    # Create complete trilayer
    _create_trilayer(root / "test_doc", "test-sigil", "1.0", "2025-01-01T00:00:00Z")

    # Create incomplete set (only YAML+JSON, missing MD)
    (root / "incomplete.yaml").write_text("meta: {sigil: inc}", encoding="utf-8")
    (root / "incomplete.json").write_text('{"meta": {"sigil": "inc"}}', encoding="utf-8")

    trilayers = sigillin_sync.discover_trilayers([root])

    assert len(trilayers) == 1
    assert trilayers[0].name == "test_doc"


def test_discover_trilayers_returns_sorted_unique(tmp_path):
    """Test that discover_trilayers returns sorted unique paths."""
    root = tmp_path / "seed"
    root.mkdir()

    _create_trilayer(root / "zebra", "zebra", "1.0", "2025-01-01T00:00:00Z")
    _create_trilayer(root / "alpha", "alpha", "1.0", "2025-01-01T00:00:00Z")

    trilayers = sigillin_sync.discover_trilayers([root])

    assert len(trilayers) == 2
    assert trilayers[0].name == "alpha"
    assert trilayers[1].name == "zebra"


def test_discover_trilayers_handles_nonexistent_root(tmp_path):
    """Test that discover_trilayers gracefully handles nonexistent roots."""
    nonexistent = tmp_path / "does_not_exist"
    trilayers = sigillin_sync.discover_trilayers([nonexistent])
    assert trilayers == []


def test_discover_trilayers_recurses_subdirectories(tmp_path):
    """Test that discover_trilayers finds trilayers in subdirectories."""
    root = tmp_path / "seed"
    subdir = root / "metaquest" / "system"
    subdir.mkdir(parents=True)

    _create_trilayer(subdir / "compass", "compass", "1.0", "2025-01-01T00:00:00Z")

    trilayers = sigillin_sync.discover_trilayers([root])

    assert len(trilayers) == 1
    assert trilayers[0].name == "compass"


# ============================================================================
# Test: load_yaml() and load_json()
# ============================================================================


def test_load_yaml_parses_valid_file(tmp_path):
    """Test that load_yaml correctly parses valid YAML."""
    yaml_path = tmp_path / "test.yaml"
    yaml_path.write_text("meta:\n  sigil: test\n  version: '1.0'\n", encoding="utf-8")

    data = sigillin_sync.load_yaml(yaml_path)

    assert data["meta"]["sigil"] == "test"
    assert data["meta"]["version"] == "1.0"


def test_load_json_parses_valid_file(tmp_path):
    """Test that load_json correctly parses valid JSON."""
    json_path = tmp_path / "test.json"
    json_path.write_text('{"meta": {"sigil": "test", "version": "1.0"}}', encoding="utf-8")

    data = sigillin_sync.load_json(json_path)

    assert data["meta"]["sigil"] == "test"
    assert data["meta"]["version"] == "1.0"


# ============================================================================
# Test: inspect_trilayer()
# ============================================================================


def test_inspect_trilayer_detects_no_gaps_when_aligned(tmp_path):
    """Test that inspect_trilayer reports no gaps for perfectly aligned trilayer."""
    base = tmp_path / "test_doc"
    _create_trilayer(base, "test-sigil", "1.0", "2025-01-01T00:00:00Z")

    # Temporarily change BASE_DIR for this test
    original_base = sigillin_sync.BASE_DIR
    try:
        sigillin_sync.BASE_DIR = tmp_path
        status = sigillin_sync.inspect_trilayer(base)
    finally:
        sigillin_sync.BASE_DIR = original_base

    assert status.sigil == "test-sigil"
    assert status.version == "1.0"
    assert status.updated == "2025-01-01T00:00:00Z"
    assert status.json_version == "1.0"
    assert status.json_updated == "2025-01-01T00:00:00Z"
    assert status.md_present is True
    assert status.gaps == []


def test_inspect_trilayer_detects_missing_sigil(tmp_path):
    """Test that inspect_trilayer detects missing sigil in YAML."""
    base = tmp_path / "test_doc"

    yaml_path = base.with_suffix(".yaml")
    json_path = base.with_suffix(".json")
    md_path = base.with_suffix(".md")

    # YAML without sigil
    yaml_path.write_text("meta:\n  version: '1.0'\n", encoding="utf-8")
    json_path.write_text('{"meta": {"version": "1.0"}}', encoding="utf-8")
    md_path.write_text("# Test\n", encoding="utf-8")

    original_base = sigillin_sync.BASE_DIR
    try:
        sigillin_sync.BASE_DIR = tmp_path
        status = sigillin_sync.inspect_trilayer(base)
    finally:
        sigillin_sync.BASE_DIR = original_base

    assert "yaml-missing-sigil" in status.gaps


def test_inspect_trilayer_detects_version_mismatch(tmp_path):
    """Test that inspect_trilayer detects version mismatch between YAML and JSON."""
    base = tmp_path / "test_doc"

    yaml_path = base.with_suffix(".yaml")
    json_path = base.with_suffix(".json")
    md_path = base.with_suffix(".md")

    yaml_data = {"meta": {"sigil": "test", "version": "1.0", "updated": "2025-01-01T00:00:00Z"}}
    json_data = {"meta": {"version": "2.0", "updated": "2025-01-01T00:00:00Z"}}  # Different version!

    yaml_path.write_text(yaml.dump(yaml_data), encoding="utf-8")
    json_path.write_text(json.dumps(json_data), encoding="utf-8")
    md_path.write_text("# Test\n", encoding="utf-8")

    original_base = sigillin_sync.BASE_DIR
    try:
        sigillin_sync.BASE_DIR = tmp_path
        status = sigillin_sync.inspect_trilayer(base)
    finally:
        sigillin_sync.BASE_DIR = original_base

    assert "version-mismatch" in status.gaps


def test_inspect_trilayer_detects_updated_mismatch(tmp_path):
    """Test that inspect_trilayer detects updated timestamp mismatch."""
    base = tmp_path / "test_doc"

    yaml_path = base.with_suffix(".yaml")
    json_path = base.with_suffix(".json")
    md_path = base.with_suffix(".md")

    yaml_data = {"meta": {"sigil": "test", "version": "1.0", "updated": "2025-01-01T00:00:00Z"}}
    json_data = {"meta": {"version": "1.0", "updated": "2025-01-02T00:00:00Z"}}  # Different timestamp!

    yaml_path.write_text(yaml.dump(yaml_data), encoding="utf-8")
    json_path.write_text(json.dumps(json_data), encoding="utf-8")
    md_path.write_text("# Test\n", encoding="utf-8")

    original_base = sigillin_sync.BASE_DIR
    try:
        sigillin_sync.BASE_DIR = tmp_path
        status = sigillin_sync.inspect_trilayer(base)
    finally:
        sigillin_sync.BASE_DIR = original_base

    assert "updated-mismatch" in status.gaps


def test_inspect_trilayer_detects_missing_markdown(tmp_path):
    """Test that inspect_trilayer detects missing Markdown file."""
    base = tmp_path / "test_doc"

    yaml_path = base.with_suffix(".yaml")
    json_path = base.with_suffix(".json")

    yaml_path.write_text("meta:\n  sigil: test\n  version: '1.0'\n", encoding="utf-8")
    json_path.write_text('{"meta": {"version": "1.0"}}', encoding="utf-8")
    # No MD file created!

    original_base = sigillin_sync.BASE_DIR
    try:
        sigillin_sync.BASE_DIR = tmp_path
        status = sigillin_sync.inspect_trilayer(base)
    finally:
        sigillin_sync.BASE_DIR = original_base

    assert status.md_present is False
    assert "missing-markdown" in status.gaps


# ============================================================================
# Test: generate_report()
# ============================================================================


def test_generate_report_creates_envelope_structure(tmp_path, monkeypatch):
    """Test that generate_report creates correct envelope structure."""
    root = tmp_path / "seed"
    root.mkdir()

    _create_trilayer(root / "doc1", "doc1", "1.0", "2025-01-01T00:00:00Z")
    _create_trilayer(root / "doc2", "doc2", "1.0", "2025-01-01T00:00:00Z")

    monkeypatch.setattr(sigillin_sync, "BASE_DIR", tmp_path)

    trilayers = sigillin_sync.discover_trilayers([root])
    envelope = sigillin_sync.generate_report(trilayers)

    assert "meta" in envelope
    assert "trilayers" in envelope
    assert envelope["meta"]["counts"]["total"] == 2
    assert envelope["meta"]["counts"]["with_gaps"] == 0
    assert len(envelope["trilayers"]) == 2


def test_generate_report_counts_gaps_correctly(tmp_path):
    """Test that generate_report counts trilayers with gaps."""
    root = tmp_path / "seed"
    root.mkdir()

    # Create one perfect trilayer
    _create_trilayer(root / "doc1", "doc1", "1.0", "2025-01-01T00:00:00Z")

    # Create one with version mismatch
    yaml_path = (root / "doc2").with_suffix(".yaml")
    json_path = (root / "doc2").with_suffix(".json")
    md_path = (root / "doc2").with_suffix(".md")
    yaml_path.write_text("meta:\n  sigil: doc2\n  version: '1.0'\n", encoding="utf-8")
    json_path.write_text('{"meta": {"version": "2.0"}}', encoding="utf-8")
    md_path.write_text("# Doc2\n", encoding="utf-8")

    trilayers = sigillin_sync.discover_trilayers([root])

    original_base = sigillin_sync.BASE_DIR
    try:
        sigillin_sync.BASE_DIR = tmp_path
        envelope = sigillin_sync.generate_report(trilayers)
    finally:
        sigillin_sync.BASE_DIR = original_base

    assert envelope["meta"]["counts"]["total"] == 2
    assert envelope["meta"]["counts"]["with_gaps"] == 1


# ============================================================================
# Test: write_output()
# ============================================================================


def test_write_output_creates_file(tmp_path):
    """Test that write_output creates JSON file with correct content."""
    output_path = tmp_path / "subdir" / "report.json"
    envelope = {
        "meta": {"test": "data"},
        "trilayers": [],
    }

    sigillin_sync.write_output(envelope, output_path)

    assert output_path.exists()
    written_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert written_data["meta"]["test"] == "data"


# ============================================================================
# Test: resolve_roots()
# ============================================================================


def test_resolve_roots_uses_defaults_when_empty(monkeypatch):
    """Test that resolve_roots uses default metaquest paths when no roots given."""
    mock_base = Path("/mock/base")
    monkeypatch.setattr(sigillin_sync, "BASE_DIR", mock_base)

    roots = sigillin_sync.resolve_roots([])

    assert len(roots) == 2
    assert roots[0] == mock_base / "seed" / "bedeutungssigillin" / "metaquest"
    assert roots[1] == mock_base / "seed" / "shadow_sigillin" / "metaquest"


def test_resolve_roots_converts_relative_paths(monkeypatch):
    """Test that resolve_roots converts relative paths to absolute."""
    mock_base = Path("/mock/base")
    monkeypatch.setattr(sigillin_sync, "BASE_DIR", mock_base)

    roots = sigillin_sync.resolve_roots(["seed/custom"])

    assert len(roots) == 1
    assert roots[0] == mock_base / "seed" / "custom"


def test_resolve_roots_preserves_absolute_paths(monkeypatch):
    """Test that resolve_roots preserves absolute paths."""
    mock_base = Path("/mock/base")
    monkeypatch.setattr(sigillin_sync, "BASE_DIR", mock_base)

    roots = sigillin_sync.resolve_roots(["/absolute/path"])

    assert len(roots) == 1
    assert roots[0] == Path("/absolute/path")


# ============================================================================
# Test: parse_args()
# ============================================================================


def test_parse_args_report_command():
    """Test that parse_args handles report command."""
    args = sigillin_sync.parse_args(["report", "--roots", "seed/"])

    assert args.command == "report"
    assert args.roots == ["seed/"]


def test_parse_args_stamp_command():
    """Test that parse_args handles stamp command."""
    args = sigillin_sync.parse_args(["stamp", "--codex-id", "test-001", "--note", "Test note"])

    assert args.command == "stamp"
    assert args.codex_id == "test-001"
    assert args.note == "Test note"


def test_parse_args_stamp_dry_run():
    """Test that parse_args handles dry-run flag."""
    args = sigillin_sync.parse_args(["stamp", "--codex-id", "test-001", "--note", "Test", "--dry-run"])

    assert args.dry_run is True


# ============================================================================
# Test: append_codex_entry()
# ============================================================================


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


def test_append_codex_entry_dry_run_does_not_write(tmp_path, monkeypatch, capsys):
    """Test that dry_run=True only prints without writing."""
    codex_base = tmp_path / "codexfeedback"
    _prepare_codex_trilayer(codex_base)

    md_path = codex_base.with_suffix(".md")
    json_path = codex_base.with_suffix(".json")
    yaml_path = codex_base.with_suffix(".yaml")

    monkeypatch.setattr(sigillin_sync, "CODEx_MD_PATH", md_path)
    monkeypatch.setattr(sigillin_sync, "CODEx_JSON_PATH", json_path)
    monkeypatch.setattr(sigillin_sync, "CODEx_YAML_PATH", yaml_path)

    original_json_content = json_path.read_text(encoding="utf-8")

    envelope = {
        "meta": {
            "generated_at": "2025-01-01T00:00:00+00:00",
            "counts": {"total": 3},
        }
    }

    sigillin_sync.append_codex_entry(envelope, "dry-run-test", "Test dry run", dry_run=True)

    # Files should not be modified
    assert json_path.read_text(encoding="utf-8") == original_json_content

    # But output should be printed
    captured = capsys.readouterr()
    assert "dry-run-test" in captured.out


def test_append_codex_entry_raises_on_missing_codex(tmp_path, monkeypatch):
    """Test that append_codex_entry raises FileNotFoundError if codex doesn't exist."""
    nonexistent = tmp_path / "nonexistent"

    monkeypatch.setattr(sigillin_sync, "CODEx_MD_PATH", nonexistent.with_suffix(".md"))
    monkeypatch.setattr(sigillin_sync, "CODEx_JSON_PATH", nonexistent.with_suffix(".json"))
    monkeypatch.setattr(sigillin_sync, "CODEx_YAML_PATH", nonexistent.with_suffix(".yaml"))

    envelope = {"meta": {"generated_at": "2025-01-01T00:00:00+00:00", "counts": {"total": 0}}}

    with pytest.raises(FileNotFoundError, match="Codexfeedback trilayer not found"):
        sigillin_sync.append_codex_entry(envelope, "test", "note")


# ============================================================================
# Test: Integration (main, handle_report, handle_stamp)
# ============================================================================


def test_handle_report_returns_zero(tmp_path, monkeypatch, capsys):
    """Test that handle_report executes successfully."""
    root = tmp_path / "seed"
    root.mkdir()
    _create_trilayer(root / "test", "test", "1.0", "2025-01-01T00:00:00Z")

    monkeypatch.setattr(sigillin_sync, "BASE_DIR", tmp_path)

    args = sigillin_sync.parse_args(["report", "--roots", "seed"])
    result = sigillin_sync.handle_report(args)

    assert result == 0

    # Check output contains JSON
    captured = capsys.readouterr()
    output_data = json.loads(captured.out)
    assert output_data["meta"]["counts"]["total"] == 1


def test_main_with_report_command(tmp_path, monkeypatch, capsys):
    """Test main() with report command."""
    root = tmp_path / "seed"
    root.mkdir()
    _create_trilayer(root / "test", "test", "1.0", "2025-01-01T00:00:00Z")

    monkeypatch.setattr(sigillin_sync, "BASE_DIR", tmp_path)

    result = sigillin_sync.main(["report", "--roots", "seed"])

    assert result == 0


def test_main_with_stamp_dry_run(tmp_path, monkeypatch, capsys):
    """Test main() with stamp --dry-run."""
    root = tmp_path / "seed"
    root.mkdir()
    _create_trilayer(root / "test", "test", "1.0", "2025-01-01T00:00:00Z")

    codex_base = tmp_path / "seed" / "codexfeedback"
    codex_base.parent.mkdir(exist_ok=True)
    _prepare_codex_trilayer(codex_base)

    monkeypatch.setattr(sigillin_sync, "BASE_DIR", tmp_path)
    monkeypatch.setattr(sigillin_sync, "CODEX_BASE", codex_base)
    monkeypatch.setattr(sigillin_sync, "CODEx_MD_PATH", codex_base.with_suffix(".md"))
    monkeypatch.setattr(sigillin_sync, "CODEx_JSON_PATH", codex_base.with_suffix(".json"))
    monkeypatch.setattr(sigillin_sync, "CODEx_YAML_PATH", codex_base.with_suffix(".yaml"))

    result = sigillin_sync.main(["stamp", "--codex-id", "test-001", "--note", "Test", "--dry-run"])

    assert result == 0
    captured = capsys.readouterr()
    assert "test-001" in captured.out
