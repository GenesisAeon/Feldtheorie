"""Tests for the archive_sigillin maintenance script."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from scripts.archive_sigillin import SigillinArchiver, main


# ============================================================================
# Test: SigillinArchiver.__init__()
# ============================================================================


def test_archiver_init_creates_archive_dir(tmp_path):
    """Test that archiver creates archive directory on init."""
    archiver = SigillinArchiver(base_path=tmp_path)

    assert archiver.archive_dir.exists()
    assert archiver.archive_dir == tmp_path / 'archive'


def test_archiver_init_raises_on_nonexistent_base(tmp_path):
    """Test that archiver raises FileNotFoundError for nonexistent base path."""
    nonexistent = tmp_path / "does_not_exist"

    with pytest.raises(FileNotFoundError, match="Base path does not exist"):
        SigillinArchiver(base_path=nonexistent)


def test_archiver_loads_existing_archive_index(tmp_path):
    """Test that archiver loads existing archive index if present."""
    archive_dir = tmp_path / 'archive'
    archive_dir.mkdir()

    # Create existing index
    existing_index = {
        'meta': {'system': 'Test System'},
        'archives': [{'name': 'test_archive'}]
    }

    index_yaml = archive_dir / 'archive_index.yaml'
    with open(index_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(existing_index, f)

    archiver = SigillinArchiver(base_path=tmp_path)

    assert archiver.archive_index['meta']['system'] == 'Test System'
    assert len(archiver.archive_index['archives']) == 1


# ============================================================================
# Test: check_sigillin_size()
# ============================================================================


def test_check_sigillin_size_detects_size_exceeded(tmp_path):
    """Test that check_sigillin_size detects when size limit is exceeded."""
    archiver = SigillinArchiver(base_path=tmp_path, max_size_kb=1)  # 1KB limit

    # Create a file larger than 1KB
    test_file = tmp_path / "large.yaml"
    test_file.write_text("x" * 2048, encoding='utf-8')  # 2KB

    needs_archiving, info = archiver.check_sigillin_size(test_file)

    assert needs_archiving is True
    assert info['size_exceeded'] is True
    assert info['size_kb'] > 1


def test_check_sigillin_size_detects_entry_count_exceeded_yaml(tmp_path):
    """Test that check_sigillin_size detects when entry count limit is exceeded."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=5)

    # Create YAML with more than 5 entries
    test_file = tmp_path / "many_entries.yaml"
    data = {
        'entries': [{'id': i} for i in range(10)]  # 10 entries
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

    needs_archiving, info = archiver.check_sigillin_size(test_file)

    assert needs_archiving is True
    assert info['entry_exceeded'] is True
    assert info['entry_count'] == 10


def test_check_sigillin_size_detects_entry_count_exceeded_json(tmp_path):
    """Test that check_sigillin_size detects entry count for JSON files."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=5)

    # Create JSON with more than 5 entries
    test_file = tmp_path / "many_entries.json"
    data = {
        'entries': [{'id': i} for i in range(10)]  # 10 entries
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    needs_archiving, info = archiver.check_sigillin_size(test_file)

    assert needs_archiving is True
    assert info['entry_exceeded'] is True
    assert info['entry_count'] == 10


def test_check_sigillin_size_handles_nonexistent_file(tmp_path):
    """Test that check_sigillin_size handles nonexistent files gracefully."""
    archiver = SigillinArchiver(base_path=tmp_path)

    nonexistent = tmp_path / "does_not_exist.yaml"
    needs_archiving, info = archiver.check_sigillin_size(nonexistent)

    assert needs_archiving is False
    assert info is None


def test_check_sigillin_size_within_limits(tmp_path):
    """Test that check_sigillin_size returns False when within limits."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=100, max_size_kb=50)

    # Create small file with few entries
    test_file = tmp_path / "small.yaml"
    data = {
        'entries': [{'id': i} for i in range(5)]  # 5 entries
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

    needs_archiving, info = archiver.check_sigillin_size(test_file)

    assert needs_archiving is False
    assert info['size_exceeded'] is False
    assert info['entry_exceeded'] is False


# ============================================================================
# Test: archive_sigillin()
# ============================================================================


def test_archive_sigillin_creates_backup(tmp_path):
    """Test that archive_sigillin creates a backup file."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=5, keep_recent=2)

    # Create a file that needs archiving
    test_file = tmp_path / "test.yaml"
    data = {
        'entries': [{'id': i} for i in range(10)]  # 10 entries
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

    result = archiver.archive_sigillin(test_file)

    assert result is True
    backup_file = test_file.with_suffix('.yaml.bak')
    assert backup_file.exists()


def test_archive_sigillin_keeps_recent_entries(tmp_path):
    """Test that archive_sigillin keeps only the most recent entries."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=5, keep_recent=3)

    # Create a file with 10 entries
    test_file = tmp_path / "test.yaml"
    data = {
        'entries': [{'id': i} for i in range(10)]
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

    result = archiver.archive_sigillin(test_file)

    assert result is True

    # Check that only 3 recent entries remain
    with open(test_file, 'r', encoding='utf-8') as f:
        updated_data = yaml.safe_load(f)

    assert len(updated_data['entries']) == 3
    # Should keep entries 7, 8, 9 (last 3)
    assert updated_data['entries'][0]['id'] == 7
    assert updated_data['entries'][2]['id'] == 9


def test_archive_sigillin_creates_zip_archive(tmp_path):
    """Test that archive_sigillin creates a ZIP archive."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=5, keep_recent=2)

    test_file = tmp_path / "test.yaml"
    data = {
        'entries': [{'id': i} for i in range(10)]
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

    result = archiver.archive_sigillin(test_file)

    assert result is True

    # Check that ZIP archive was created
    archive_files = list(archiver.archive_dir.glob("test_*_archive.zip"))
    assert len(archive_files) == 1
    assert archive_files[0].exists()


def test_archive_sigillin_updates_archive_index(tmp_path):
    """Test that archive_sigillin updates the archive index."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=5, keep_recent=2)

    test_file = tmp_path / "test.yaml"
    data = {
        'entries': [{'id': i} for i in range(10)]
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

    result = archiver.archive_sigillin(test_file)

    assert result is True
    assert len(archiver.archive_index['archives']) == 1
    assert archiver.archive_index['archives'][0]['entry_count'] == 8  # 10 - 2 kept


def test_archive_sigillin_skips_when_within_limits(tmp_path):
    """Test that archive_sigillin skips files within limits."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=100, max_size_kb=50)

    # Create small file
    test_file = tmp_path / "small.yaml"
    data = {
        'entries': [{'id': i} for i in range(5)]
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

    result = archiver.archive_sigillin(test_file)

    assert result is False
    # No archive should be created
    archive_files = list(archiver.archive_dir.glob("*.zip"))
    assert len(archive_files) == 0


def test_archive_sigillin_dry_run_does_not_modify(tmp_path):
    """Test that dry_run=True does not modify files."""
    archiver = SigillinArchiver(
        base_path=tmp_path,
        max_entries=5,
        keep_recent=2,
        dry_run=True
    )

    test_file = tmp_path / "test.yaml"
    original_data = {
        'entries': [{'id': i} for i in range(10)]
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(original_data, f)

    original_content = test_file.read_text(encoding='utf-8')

    result = archiver.archive_sigillin(test_file)

    assert result is False
    # File should be unchanged
    assert test_file.read_text(encoding='utf-8') == original_content
    # No archive should be created
    archive_files = list(archiver.archive_dir.glob("*.zip"))
    assert len(archive_files) == 0


def test_archive_sigillin_handles_json_files(tmp_path):
    """Test that archive_sigillin works with JSON files."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=5, keep_recent=2)

    test_file = tmp_path / "test.json"
    data = {
        'entries': [{'id': i} for i in range(10)]
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    result = archiver.archive_sigillin(test_file)

    assert result is True

    # Check that only 2 entries remain
    with open(test_file, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)

    assert len(updated_data['entries']) == 2


def test_archive_sigillin_handles_list_root(tmp_path):
    """Test that archive_sigillin handles files where root is a list."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=5, keep_recent=2)

    # Create file where root is a list (no 'entries' key)
    test_file = tmp_path / "test.yaml"
    data = [{'id': i} for i in range(10)]  # List at root
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

    result = archiver.archive_sigillin(test_file)

    assert result is True

    # Check that only 2 entries remain
    with open(test_file, 'r', encoding='utf-8') as f:
        updated_data = yaml.safe_load(f)

    assert len(updated_data) == 2


def test_archive_sigillin_skips_when_not_enough_entries(tmp_path):
    """Test that archive_sigillin skips when there aren't enough entries to archive."""
    archiver = SigillinArchiver(base_path=tmp_path, max_entries=5, keep_recent=10)

    # Create file with only 5 entries, but we want to keep 10
    test_file = tmp_path / "test.yaml"
    data = {
        'entries': [{'id': i} for i in range(5)]
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

    # Force size exceeded to trigger archiving attempt
    archiver.max_size_kb = 0.001  # Very small limit

    result = archiver.archive_sigillin(test_file)

    # Should return False because not enough entries to archive
    assert result is False


# ============================================================================
# Test: _save_archive_index()
# ============================================================================


def test_save_archive_index_creates_trilayer(tmp_path):
    """Test that _save_archive_index creates YAML, JSON, and MD files."""
    archiver = SigillinArchiver(base_path=tmp_path)

    archiver.archive_index['archives'].append({
        'original_file': 'test.yaml',
        'archive_file': 'test_2025-11_archive.zip',
        'archived_date': '2025-11-10T00:00:00',
        'entry_range': 'Entry 1-8',
        'entry_count': 8,
        'kept_recent': 2,
        'original_size_kb': 10.5,
        'compressed_size_kb': 3.2,
        'compression_ratio': 30.5
    })

    archiver._save_archive_index()

    # Check all three files exist
    assert archiver.archive_index_yaml.exists()
    assert archiver.archive_index_json.exists()
    assert archiver.archive_index_md.exists()

    # Verify YAML content
    with open(archiver.archive_index_yaml, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    assert yaml_data['meta']['total_archives'] == 1

    # Verify JSON content
    with open(archiver.archive_index_json, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    assert json_data['meta']['total_archives'] == 1

    # Verify MD content
    md_content = archiver.archive_index_md.read_text(encoding='utf-8')
    assert 'Sigillin Archive Index' in md_content
    assert 'test.yaml' in md_content


# ============================================================================
# Test: Helper methods
# ============================================================================


def test_collect_files_finds_matching_patterns(tmp_path):
    """Test that _collect_files finds files matching patterns."""
    archiver = SigillinArchiver(base_path=tmp_path)

    # Create test files
    (tmp_path / "file1.py").write_text("test", encoding='utf-8')
    (tmp_path / "file2.py").write_text("test", encoding='utf-8')
    (tmp_path / "file3.md").write_text("test", encoding='utf-8')

    files = archiver._collect_files(tmp_path, patterns=['*.py'])

    assert len(files) == 2
    assert 'file1.py' in files
    assert 'file2.py' in files


def test_collect_files_excludes_names(tmp_path):
    """Test that _collect_files excludes specified names."""
    archiver = SigillinArchiver(base_path=tmp_path)

    # Create test files
    (tmp_path / "file1.py").write_text("test", encoding='utf-8')
    (tmp_path / "exclude_me.py").write_text("test", encoding='utf-8')

    files = archiver._collect_files(
        tmp_path,
        patterns=['*.py'],
        exclude_names={'exclude_me.py'}
    )

    assert len(files) == 1
    assert 'file1.py' in files
    assert 'exclude_me.py' not in files


def test_collect_files_filters_by_suffix(tmp_path):
    """Test that _collect_files filters by suffix."""
    archiver = SigillinArchiver(base_path=tmp_path)

    # Create test files
    (tmp_path / "file1.py").write_text("test", encoding='utf-8')
    (tmp_path / "file2.md").write_text("test", encoding='utf-8')
    (tmp_path / "file3.txt").write_text("test", encoding='utf-8')

    files = archiver._collect_files(
        tmp_path,
        patterns=['*'],
        include_suffixes={'.py', '.md'}
    )

    assert len(files) == 2
    assert 'file1.py' in files
    assert 'file2.md' in files
    assert 'file3.txt' not in files


def test_load_yaml_or_empty_returns_empty_on_error(tmp_path):
    """Test that _load_yaml_or_empty returns empty dict on parse error."""
    archiver = SigillinArchiver(base_path=tmp_path)

    # Create invalid YAML
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("not: valid: yaml: syntax", encoding='utf-8')

    result = archiver._load_yaml_or_empty(invalid_yaml)

    assert result == {}


# ============================================================================
# Test: Main CLI
# ============================================================================


def test_main_requires_arguments(capsys):
    """Test that main() prints help when no arguments provided."""
    import sys
    original_argv = sys.argv

    try:
        sys.argv = ['archive_sigillin.py']
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
    finally:
        sys.argv = original_argv


def test_main_with_recount_option(tmp_path, monkeypatch):
    """Test main() with --recount option."""
    import sys
    from scripts import archive_sigillin

    # Create required directories and index files
    for dirname in ['docs', 'analysis', 'models', 'data', 'seed']:
        (tmp_path / dirname).mkdir()

        # Create minimal index files
        index_yaml = tmp_path / dirname / f'{dirname}_index.yaml'
        index_json = tmp_path / dirname / f'{dirname}_index.json'

        index_yaml.write_text('meta:\n  test: data\n', encoding='utf-8')
        index_json.write_text('{"meta": {"test": "data"}}', encoding='utf-8')

    # Monkeypatch DEFAULT_BASE_PATH
    monkeypatch.setattr(archive_sigillin, 'DEFAULT_BASE_PATH', tmp_path)

    original_argv = sys.argv
    try:
        sys.argv = ['archive_sigillin.py', '--recount', '--recount-targets', 'docs']
        main()

        # Check that recount output was created
        results_dir = tmp_path / 'analysis' / 'results'
        assert results_dir.exists()
        json_files = list(results_dir.glob('index_recount_*.json'))
        assert len(json_files) >= 1
    finally:
        sys.argv = original_argv
