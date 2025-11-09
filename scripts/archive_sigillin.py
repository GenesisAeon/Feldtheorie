#!/usr/bin/env python3
"""
Sigillin Maintenance Script - Archive Oversized Sigillin

PROBLEM: Sigillin-Files wachsen mit der Zeit und werden unüberschaubar
SOLUTION: Alte Einträge archivieren (ZIP), aktive Sigillin klein halten

Usage:
    python scripts/archive_sigillin.py --sigillin seed/codexfeedback.yaml --max-entries 50
    python scripts/archive_sigillin.py --scan-all --max-size 100  # 100KB limit
    python scripts/archive_sigillin.py --scan-all --base-path /path/to/Feldtheorie
"""

import argparse
import json
import re
import yaml
import zipfile
from pathlib import Path
from datetime import datetime, timezone
import sys
import shutil

# Configuration
DEFAULT_BASE_PATH = Path(__file__).resolve().parents[1]

# Default thresholds
DEFAULT_MAX_ENTRIES = 100  # Max entries in active Sigillin
DEFAULT_MAX_SIZE_KB = 50   # Max size in KB
DEFAULT_KEEP_RECENT = 50   # Keep most recent N entries


class SigillinArchiver:
    """Archive oversized Sigillin files"""

    def __init__(
        self,
        max_entries: int = DEFAULT_MAX_ENTRIES,
        max_size_kb: int = DEFAULT_MAX_SIZE_KB,
        keep_recent: int = DEFAULT_KEEP_RECENT,
        dry_run: bool = False,
        base_path: Path = DEFAULT_BASE_PATH,
    ):
        self.max_entries = max_entries
        self.max_size_kb = max_size_kb
        self.keep_recent = keep_recent
        self.dry_run = dry_run
        self.base_path = base_path.resolve()

        if not self.base_path.exists():
            raise FileNotFoundError(f"Base path does not exist: {self.base_path}")

        self.archive_dir = self.base_path / 'archive'
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self.archive_index_yaml = self.archive_dir / 'archive_index.yaml'
        self.archive_index_json = self.archive_dir / 'archive_index.json'
        self.archive_index_md = self.archive_dir / 'archive_index.md'

        # Load existing archive index
        self.archive_index = self._load_archive_index()

    def _load_archive_index(self):
        """Load existing archive index or create new"""
        if self.archive_index_yaml.exists():
            with open(self.archive_index_yaml, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return {
                'meta': {
                    'system': 'Sigillin Archive System',
                    'purpose': 'Cold storage for archived Sigillin entries',
                    'format': 'ZIP archives with Trilayer Index',
                    'created': datetime.now().isoformat()
                },
                'archives': []
            }

    def _save_archive_index(self):
        """Save archive index in trilayer format"""
        # Update timestamp
        self.archive_index['meta']['updated'] = datetime.now().isoformat()
        self.archive_index['meta']['total_archives'] = len(self.archive_index['archives'])

        # Save YAML
        with open(self.archive_index_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(self.archive_index, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        # Save JSON
        with open(self.archive_index_json, 'w', encoding='utf-8') as f:
            json.dump(self.archive_index, f, ensure_ascii=False, indent=2)

        # Save MD (human-readable)
        self._generate_markdown_index()

        print(f"✅ Archive index updated: {len(self.archive_index['archives'])} archives")

    def _generate_markdown_index(self):
        """Generate human-readable markdown index"""
        md_content = f"""# 📦 Sigillin Archive Index

**System:** {self.archive_index['meta']['system']}
**Purpose:** {self.archive_index['meta']['purpose']}
**Format:** {self.archive_index['meta']['format']}
**Updated:** {self.archive_index['meta']['updated']}
**Total Archives:** {self.archive_index['meta']['total_archives']}

---

## 🗄️ Archives

"""
        for archive in self.archive_index['archives']:
            md_content += f"""### {archive['original_file']}

- **Archive File:** `{archive['archive_file']}`
- **Archived Date:** {archive['archived_date']}
- **Entry Range:** {archive['entry_range']}
- **Entry Count:** {archive['entry_count']}
- **Original Size:** {archive['original_size_kb']:.2f} KB
- **Compressed Size:** {archive['compressed_size_kb']:.2f} KB
- **Compression Ratio:** {archive['compression_ratio']:.1f}%

"""

        md_content += """
---

## 🔍 How to Search Archives

### Extract ZIP Archive
```bash
unzip archive/sigillin_name_YYYY-MM_archive.zip -d temp/
```

### Search in Archive
```bash
# Extract and search
unzip -p archive/codexfeedback_2025-11_archive.zip | grep "keyword"
```

### List Archive Contents
```bash
unzip -l archive/sigillin_name_YYYY-MM_archive.zip
```

---

**Maintained by Sigillin Maintenance System** 🧹✨
"""

        with open(self.archive_index_md, 'w', encoding='utf-8') as f:
            f.write(md_content)

    def check_sigillin_size(self, sigillin_path):
        """Check if Sigillin exceeds thresholds"""
        path = Path(sigillin_path)

        if not path.exists():
            print(f"❌ File not found: {sigillin_path}")
            return False, None

        # Check file size
        size_kb = path.stat().st_size / 1024
        size_exceeded = size_kb > self.max_size_kb

        # Check entry count (for YAML/JSON)
        entry_count = None
        entry_exceeded = False

        if path.suffix in ['.yaml', '.yml']:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                # Count entries (assuming list or dict structure)
                if isinstance(data, list):
                    entry_count = len(data)
                elif isinstance(data, dict):
                    # Look for common list keys
                    for key in ['entries', 'items', 'documents', 'feedbacks']:
                        if key in data and isinstance(data[key], list):
                            entry_count = len(data[key])
                            break

                if entry_count:
                    entry_exceeded = entry_count > self.max_entries

        elif path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    entry_count = len(data)
                elif isinstance(data, dict):
                    for key in ['entries', 'items', 'documents', 'feedbacks']:
                        if key in data and isinstance(data[key], list):
                            entry_count = len(data[key])
                            break

                if entry_count:
                    entry_exceeded = entry_count > self.max_entries

        needs_archiving = size_exceeded or entry_exceeded

        info = {
            'size_kb': size_kb,
            'size_exceeded': size_exceeded,
            'entry_count': entry_count,
            'entry_exceeded': entry_exceeded,
            'needs_archiving': needs_archiving
        }

        return needs_archiving, info

    def archive_sigillin(self, sigillin_path):
        """Archive old entries from Sigillin, keep recent entries active"""
        path = Path(sigillin_path)

        if not path.is_absolute():
            path = (self.base_path / path).resolve()
        else:
            path = path.resolve()

        print(f"\n📦 Archiving: {path.name}")

        # Check if archiving needed
        needs_archiving, info = self.check_sigillin_size(path)

        if not needs_archiving:
            print(f"✅ {path.name} is within limits (Size: {info['size_kb']:.2f}KB, Entries: {info.get('entry_count', 'N/A')})")
            return False

        print(f"⚠️  Exceeds limits: Size={info['size_kb']:.2f}KB (max {self.max_size_kb}), Entries={info.get('entry_count', 'N/A')} (max {self.max_entries})")

        if self.dry_run:
            print(f"🔍 DRY RUN: Would archive old entries from {path.name}")
            return False

        # Load data
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                print(f"❌ Unsupported format: {path.suffix}")
                return False

        # Find list of entries
        entries_key = None
        entries = None

        if isinstance(data, list):
            entries = data
            entries_key = None  # Root is list
        elif isinstance(data, dict):
            for key in ['entries', 'items', 'documents', 'feedbacks']:
                if key in data and isinstance(data[key], list):
                    entries = data[key]
                    entries_key = key
                    break

        if entries is None or len(entries) <= self.keep_recent:
            print(f"⚠️  Not enough entries to archive ({len(entries) if entries else 0} entries)")
            return False

        # Split: old entries (to archive) vs recent entries (to keep)
        old_entries = entries[:-self.keep_recent]
        recent_entries = entries[-self.keep_recent:]

        print(f"📊 Total entries: {len(entries)} | Archiving: {len(old_entries)} | Keeping: {len(recent_entries)}")

        # Create archive filename
        timestamp = datetime.now().strftime('%Y-%m')
        archive_filename = f"{path.stem}_{timestamp}_archive.zip"
        archive_path = self.archive_dir / archive_filename

        # Create ZIP archive with old entries
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Save old entries
            if entries_key:
                archived_data = {entries_key: old_entries}
            else:
                archived_data = old_entries

            # Add to ZIP
            if path.suffix in ['.yaml', '.yml']:
                content = yaml.dump(archived_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
            else:
                content = json.dumps(archived_data, ensure_ascii=False, indent=2)

            zf.writestr(path.name, content)

        compressed_size_kb = archive_path.stat().st_size / 1024
        original_size_kb = info['size_kb']
        compression_ratio = (compressed_size_kb / original_size_kb) * 100

        print(f"✅ Created archive: {archive_filename} ({compressed_size_kb:.2f}KB, {compression_ratio:.1f}% of original)")

        # Update active Sigillin (keep only recent)
        if entries_key:
            data[entries_key] = recent_entries
        else:
            data = recent_entries

        # Backup original
        backup_path = path.with_suffix(path.suffix + '.bak')
        shutil.copy(path, backup_path)
        print(f"💾 Backup created: {backup_path.name}")

        # Save updated Sigillin
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            else:
                json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ Updated active Sigillin: {path.name} (now {len(recent_entries)} entries)")

        # Update archive index
        try:
            original_file = str(path.relative_to(self.base_path))
        except ValueError:
            original_file = str(path)

        self.archive_index['archives'].append({
            'original_file': original_file,
            'archive_file': archive_filename,
            'archived_date': datetime.now().isoformat(),
            'entry_range': f"Entry 1-{len(old_entries)}",
            'entry_count': len(old_entries),
            'kept_recent': len(recent_entries),
            'original_size_kb': original_size_kb,
            'compressed_size_kb': compressed_size_kb,
            'compression_ratio': compression_ratio
        })

        self._save_archive_index()

        return True

    def scan_all_sigillin(self):
        """Scan all Sigillin files and archive if needed"""
        print("\n🔍 Scanning all Sigillin files...")

        # Find all YAML/JSON files in key directories
        patterns = [
            'seed/**/*.yaml',
            'seed/**/*.json',
            'analysis/**/*.yaml',
            'analysis/**/*.json',
            'data/**/*.yaml',
            'data/**/*.json',
            'models/**/*.yaml',
            'models/**/*.json',
        ]

        sigillin_files = []
        for pattern in patterns:
            sigillin_files.extend(self.base_path.glob(pattern))

        # Filter out index files
        sigillin_files = [f for f in sigillin_files if '_index' not in f.name]

        print(f"Found {len(sigillin_files)} Sigillin candidates")

        archived_count = 0
        for sigillin_path in sigillin_files:
            if self.archive_sigillin(sigillin_path):
                archived_count += 1

        print(f"\n✅ Scan complete: {archived_count} files archived")

    # ------------------------------------------------------------------
    # Index recount helpers

    def _update_yaml_fields(self, path: Path, replacements: dict) -> dict:
        """Update specific key-value pairs in a YAML file via regex substitution.

        Returns a dictionary with the previous values for reporting."""

        content = path.read_text(encoding='utf-8')
        previous = {}

        for key, value in replacements.items():
            pattern = re.compile(rf"^(\s*{re.escape(key)}:\s*)(.+)$", re.MULTILINE)
            match = pattern.search(content)
            if not match:
                continue

            old_value = match.group(2).strip()
            previous[key] = old_value

            if isinstance(value, str) and not value.startswith('"') and not value.endswith('"') and not value.startswith("'"):
                replacement_value = f'"{value}"'
            else:
                replacement_value = str(value)

            content = pattern.sub(rf"\g<1>{replacement_value}", content, count=1)

        path.write_text(content, encoding='utf-8')
        return previous

    def _collect_files(
        self,
        directory: Path,
        *,
        patterns=None,
        recursive: bool = False,
        include_suffixes=None,
        exclude_names=None,
        exclude_paths=None,
        use_relative: bool = False,
    ) -> set:
        """Return a set of filenames (or relative paths) that match the spec."""

        patterns = patterns or ['*']
        exclude_names = {name for name in (exclude_names or [])}
        exclude_paths = {path for path in (exclude_paths or [])}
        include_suffixes = {s for s in (include_suffixes or [])}

        collected = set()
        for pattern in patterns:
            iterator = directory.rglob(pattern) if recursive else directory.glob(pattern)
            for path in iterator:
                if not path.is_file():
                    continue

                rel = path.relative_to(directory)
                rel_str = rel.as_posix() if use_relative else rel.name

                if rel.name in exclude_names or rel_str in exclude_paths:
                    continue

                if include_suffixes and rel.suffix not in include_suffixes:
                    continue

                collected.add(rel_str)

        return collected

    def _load_yaml_or_empty(self, path: Path) -> dict:
        """Load YAML content and fall back to an empty mapping on parse errors."""

        try:
            with open(path, 'r', encoding='utf-8') as handle:
                return yaml.safe_load(handle) or {}
        except yaml.YAMLError as exc:
            print(f"⚠️  YAML parse issue for {path}: {exc}. Treating as empty mapping.")
            return {}

    def _prepare_summary(self, timestamp: str) -> dict:
        return {
            'meta': {
                'generated_at': timestamp,
                'base_path': str(self.base_path),
                'order_parameter_R': 'index parity delta',
                'threshold_Theta': 'filesystem counts',
                'beta': 4.8,
                'zeta': 'σ(β(R-Θ)) guard for index parity',
            },
            'indices': [],
        }

    def _log_index_delta(self, target: str, filesystem: int, listed: int, missing, orphans) -> None:
        print("\n🔁 Index recount:")
        print(f"   • Target: {target}")
        print(f"   • Filesystem count: {filesystem}")
        if listed is not None:
            print(f"   • Listed entries: {listed}")
        if missing:
            print(f"   • Missing in index: {', '.join(missing)}")
        if orphans:
            print(f"   • Orphan entries: {', '.join(orphans)}")

    def _recount_docs(self, timestamp: str) -> dict:
        directory = self.base_path / 'docs'
        files = self._collect_files(
            directory,
            patterns=['*.md'],
            recursive=False,
        )

        index_yaml = directory / 'docs_index.yaml'
        index_json = directory / 'docs_index.json'

        yaml_data = self._load_yaml_or_empty(index_yaml)

        with open(index_json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        listed_entries = [
            entry.get('name')
            for entry in (yaml_data.get('markdown_docs') or [])
            if isinstance(entry, dict)
        ]
        listed_set = {name for name in listed_entries if name}

        filesystem_count = len(files)

        yaml_replacements = {
            'markdown_files': filesystem_count,
            'updated': timestamp,
        }
        previous_yaml = self._update_yaml_fields(index_yaml, yaml_replacements)

        previous_json = {
            'markdown_files': json_data.get('meta', {}).get('markdown_files'),
            'updated': json_data.get('meta', {}).get('updated'),
        }
        json_data.setdefault('meta', {})['markdown_files'] = filesystem_count
        json_data['meta']['updated'] = timestamp

        with open(index_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        missing_files = sorted(files - listed_set)
        orphan_entries = sorted(listed_set - files)

        self._log_index_delta('docs', filesystem_count, len(listed_set), missing_files, orphan_entries)

        return {
            'index': 'docs',
            'directory': 'docs/',
            'counts': {
                'filesystem': filesystem_count,
                'listed': len(listed_set),
            },
            'delta': filesystem_count - len(listed_set),
            'missing_files': missing_files,
            'orphan_entries': orphan_entries,
            'meta_updates': {
                'yaml': previous_yaml,
                'json': previous_json,
            },
            'logistic': {
                'beta': 4.8,
                'zeta': 'docs-index parity damping',
            },
        }

    def _recount_analysis(self, timestamp: str) -> dict:
        directory = self.base_path / 'analysis'
        py_files = self._collect_files(
            directory,
            patterns=['*.py'],
            recursive=False,
            exclude_names={
                'analysis_index.py',
            },
        )
        aux_files = self._collect_files(
            directory,
            patterns=['*.md', '*.ipynb'],
            recursive=False,
            exclude_names={
                'analysis_index.md',
            },
        )
        files = py_files | aux_files

        index_yaml = directory / 'analysis_index.yaml'
        index_json = directory / 'analysis_index.json'

        yaml_data = self._load_yaml_or_empty(index_yaml)

        with open(index_json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        listed_entries = [
            entry.get('name')
            for entry in (yaml_data.get('python_scripts') or [])
            if isinstance(entry, dict)
        ]
        listed_set = {name for name in listed_entries if name}

        filesystem_count = len(files)
        python_file_count = len(py_files)
        subdirectories = len([p for p in directory.iterdir() if p.is_dir()])

        yaml_replacements = {
            'python_files': python_file_count,
            'subdirectories': subdirectories,
            'updated': timestamp,
        }
        previous_yaml = self._update_yaml_fields(index_yaml, yaml_replacements)

        previous_json = {
            'python_files': json_data.get('meta', {}).get('python_files'),
            'subdirectories': json_data.get('meta', {}).get('subdirectories'),
            'updated': json_data.get('meta', {}).get('updated'),
        }
        json_data.setdefault('meta', {})['python_files'] = python_file_count
        json_data['meta']['subdirectories'] = subdirectories
        json_data['meta']['updated'] = timestamp

        with open(index_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        missing_files = sorted(files - listed_set)
        orphan_entries = sorted(listed_set - files)

        self._log_index_delta('analysis', filesystem_count, len(listed_set), missing_files, orphan_entries)

        return {
            'index': 'analysis',
            'directory': 'analysis/',
            'counts': {
                'filesystem': filesystem_count,
                'listed': len(listed_set),
            },
            'delta': filesystem_count - len(listed_set),
            'missing_files': missing_files,
            'orphan_entries': orphan_entries,
            'meta_updates': {
                'yaml': previous_yaml,
                'json': previous_json,
            },
            'logistic': {
                'beta': 4.8,
                'zeta': 'analysis-index parity damping',
            },
        }

    def _recount_models(self, timestamp: str) -> dict:
        directory = self.base_path / 'models'
        py_files = self._collect_files(
            directory,
            patterns=['*.py'],
            recursive=False,
            exclude_names={'models_index.py'},
        )
        doc_files = self._collect_files(
            directory,
            patterns=['*.md'],
            recursive=False,
            exclude_names={'models_index.md'},
        )
        files = py_files | doc_files

        index_yaml = directory / 'models_index.yaml'
        index_json = directory / 'models_index.json'

        yaml_data = self._load_yaml_or_empty(index_yaml)

        with open(index_json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        listed_entries = [
            entry.get('name')
            for entry in (yaml_data.get('python_models') or [])
            if isinstance(entry, dict)
        ]
        listed_set = {name for name in listed_entries if name}

        filesystem_count = len(files)
        python_file_count = len(py_files)

        yaml_replacements = {
            'python_files': python_file_count,
            'updated': timestamp,
        }
        previous_yaml = self._update_yaml_fields(index_yaml, yaml_replacements)

        previous_json = {
            'python_files': json_data.get('meta', {}).get('python_files'),
            'updated': json_data.get('meta', {}).get('updated'),
        }
        json_data.setdefault('meta', {})['python_files'] = python_file_count
        json_data['meta']['updated'] = timestamp

        with open(index_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        missing_files = sorted(files - listed_set)
        orphan_entries = sorted(listed_set - files)

        self._log_index_delta('models', filesystem_count, len(listed_set), missing_files, orphan_entries)

        return {
            'index': 'models',
            'directory': 'models/',
            'counts': {
                'filesystem': filesystem_count,
                'listed': len(listed_set),
            },
            'delta': filesystem_count - len(listed_set),
            'missing_files': missing_files,
            'orphan_entries': orphan_entries,
            'meta_updates': {
                'yaml': previous_yaml,
                'json': previous_json,
            },
            'logistic': {
                'beta': 4.8,
                'zeta': 'model-index parity damping',
            },
        }

    def _recount_data(self, timestamp: str) -> dict:
        directory = self.base_path / 'data'
        files = self._collect_files(
            directory,
            patterns=['**/*'],
            recursive=True,
            include_suffixes={'.csv', '.json', '.md', '.yaml'},
            exclude_names={'data_index.yaml', 'data_index.json', 'data_index.md'},
            use_relative=True,
        )

        index_yaml = directory / 'data_index.yaml'
        index_json = directory / 'data_index.json'

        yaml_data = self._load_yaml_or_empty(index_yaml)

        with open(index_json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        filesystem_count = len(files)
        domain_dirs = [p for p in directory.iterdir() if p.is_dir()]

        yaml_replacements = {
            'total_files': filesystem_count,
            'domains': len(domain_dirs),
            'updated': timestamp,
        }
        previous_yaml = self._update_yaml_fields(index_yaml, yaml_replacements)

        previous_json = {
            'total_files': json_data.get('meta', {}).get('total_files'),
            'domains': json_data.get('meta', {}).get('domains'),
            'updated': json_data.get('meta', {}).get('updated'),
        }
        json_data.setdefault('meta', {})['total_files'] = filesystem_count
        json_data['meta']['domains'] = len(domain_dirs)
        json_data['meta']['updated'] = timestamp

        with open(index_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        self._log_index_delta('data', filesystem_count, None, [], [])

        return {
            'index': 'data',
            'directory': 'data/',
            'counts': {
                'filesystem': filesystem_count,
                'listed': None,
            },
            'delta': None,
            'missing_files': [],
            'orphan_entries': [],
            'meta_updates': {
                'yaml': previous_yaml,
                'json': previous_json,
            },
            'logistic': {
                'beta': 4.8,
                'zeta': 'data-index volume damping',
            },
        }

    def _recount_seed(self, timestamp: str) -> dict:
        directory = self.base_path / 'seed'
        files = self._collect_files(
            directory,
            patterns=['**/*'],
            recursive=True,
            include_suffixes={'.md', '.txt', '.pdf', '.json', '.yaml', '.latex'},
            exclude_names={'seed_index.yaml', 'seed_index.json', 'seed_index.md'},
            use_relative=True,
        )

        index_yaml = directory / 'seed_index.yaml'
        index_json = directory / 'seed_index.json'

        yaml_data = self._load_yaml_or_empty(index_yaml)

        with open(index_json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        filesystem_count = len(files)

        yaml_replacements = {
            'documents_total': filesystem_count,
            'updated': timestamp,
        }
        previous_yaml = self._update_yaml_fields(index_yaml, yaml_replacements)

        previous_json = {
            'documents_total': json_data.get('meta', {}).get('documents_total'),
            'updated': json_data.get('meta', {}).get('updated'),
        }
        json_data.setdefault('meta', {})['documents_total'] = filesystem_count
        json_data['meta']['updated'] = timestamp

        with open(index_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        self._log_index_delta('seed', filesystem_count, None, [], [])

        return {
            'index': 'seed',
            'directory': 'seed/',
            'counts': {
                'filesystem': filesystem_count,
                'listed': None,
            },
            'delta': None,
            'missing_files': [],
            'orphan_entries': [],
            'meta_updates': {
                'yaml': previous_yaml,
                'json': previous_json,
            },
            'logistic': {
                'beta': 4.8,
                'zeta': 'seed-index archive damping',
            },
        }

    def recount_indices(self, targets=None, output_dir=None):
        """Refresh index metadata counts and emit a parity summary."""

        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        summary = self._prepare_summary(timestamp)

        available_targets = ['analysis', 'data', 'docs', 'models', 'seed']

        if targets:
            requested = []
            for target in targets:
                if not target:
                    continue
                for segment in target.split(','):
                    segment = segment.strip().lower()
                    if segment:
                        requested.append(segment)
        else:
            requested = available_targets

        unknown = [t for t in requested if t not in available_targets]
        if unknown:
            raise ValueError(f"Unknown indices for recount: {', '.join(unknown)}")

        results_dir = self.base_path / 'analysis' / 'results'
        results_dir.mkdir(parents=True, exist_ok=True)

        for target in requested:
            if target == 'docs':
                info = self._recount_docs(timestamp)
            elif target == 'analysis':
                info = self._recount_analysis(timestamp)
            elif target == 'models':
                info = self._recount_models(timestamp)
            elif target == 'data':
                info = self._recount_data(timestamp)
            elif target == 'seed':
                info = self._recount_seed(timestamp)
            else:
                continue

            summary['indices'].append(info)

        summary_path = results_dir / f"index_recount_{timestamp.replace(':', '').replace('-', '')}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Recount summary written to {summary_path.relative_to(self.base_path)}")


def main():
    parser = argparse.ArgumentParser(
        description='Sigillin Maintenance - Archive oversized Sigillin files'
    )

    parser.add_argument('--sigillin', type=str, help='Path to specific Sigillin file to archive')
    parser.add_argument('--scan-all', action='store_true', help='Scan all Sigillin files')
    parser.add_argument('--max-entries', type=int, default=DEFAULT_MAX_ENTRIES,
                       help=f'Max entries before archiving (default: {DEFAULT_MAX_ENTRIES})')
    parser.add_argument('--max-size', type=int, default=DEFAULT_MAX_SIZE_KB,
                       help=f'Max size in KB before archiving (default: {DEFAULT_MAX_SIZE_KB})')
    parser.add_argument('--keep-recent', type=int, default=DEFAULT_KEEP_RECENT,
                       help=f'Number of recent entries to keep active (default: {DEFAULT_KEEP_RECENT})')
    parser.add_argument('--dry-run', action='store_true', help='Check only, do not archive')
    parser.add_argument('--base-path', type=str, default=None,
                        help='Repository root containing Sigillin assets (default: script directory parent)')
    parser.add_argument('--recount', action='store_true', help='Refresh index metadata counts and emit summary')
    parser.add_argument('--recount-targets', type=str, nargs='*',
                        help='Specific indices to recount (default: all supported)')

    args = parser.parse_args()

    if not args.sigillin and not args.scan_all and not args.recount:
        parser.print_help()
        sys.exit(1)

    base_path = Path(args.base_path).expanduser().resolve() if args.base_path else DEFAULT_BASE_PATH

    archiver = SigillinArchiver(
        max_entries=args.max_entries,
        max_size_kb=args.max_size,
        keep_recent=args.keep_recent,
        dry_run=args.dry_run,
        base_path=base_path,
    )

    if args.recount:
        archiver.recount_indices(targets=args.recount_targets)

    if args.sigillin:
        archiver.archive_sigillin(args.sigillin)

    if args.scan_all:
        archiver.scan_all_sigillin()


if __name__ == '__main__':
    main()
