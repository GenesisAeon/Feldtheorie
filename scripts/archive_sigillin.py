#!/usr/bin/env python3
"""
Sigillin Maintenance Script - Archive Oversized Sigillin

PROBLEM: Sigillin-Files wachsen mit der Zeit und werden unüberschaubar
SOLUTION: Alte Einträge archivieren (ZIP), aktive Sigillin klein halten

Usage:
    python scripts/archive_sigillin.py --sigillin seed/codexfeedback.yaml --max-entries 50
    python scripts/archive_sigillin.py --scan-all --max-size 100  # 100KB limit
"""

import argparse
import json
import yaml
import zipfile
from pathlib import Path
from datetime import datetime
import sys
import shutil

# Configuration
BASE_PATH = Path('/home/user/Feldtheorie')
ARCHIVE_DIR = BASE_PATH / 'archive'
ARCHIVE_INDEX_YAML = ARCHIVE_DIR / 'archive_index.yaml'
ARCHIVE_INDEX_JSON = ARCHIVE_DIR / 'archive_index.json'
ARCHIVE_INDEX_MD = ARCHIVE_DIR / 'archive_index.md'

# Default thresholds
DEFAULT_MAX_ENTRIES = 100  # Max entries in active Sigillin
DEFAULT_MAX_SIZE_KB = 50   # Max size in KB
DEFAULT_KEEP_RECENT = 50   # Keep most recent N entries


class SigillinArchiver:
    """Archive oversized Sigillin files"""

    def __init__(self, max_entries=DEFAULT_MAX_ENTRIES, max_size_kb=DEFAULT_MAX_SIZE_KB,
                 keep_recent=DEFAULT_KEEP_RECENT, dry_run=False):
        self.max_entries = max_entries
        self.max_size_kb = max_size_kb
        self.keep_recent = keep_recent
        self.dry_run = dry_run
        self.archive_dir = ARCHIVE_DIR
        self.archive_dir.mkdir(exist_ok=True)

        # Load existing archive index
        self.archive_index = self._load_archive_index()

    def _load_archive_index(self):
        """Load existing archive index or create new"""
        if ARCHIVE_INDEX_YAML.exists():
            with open(ARCHIVE_INDEX_YAML, 'r', encoding='utf-8') as f:
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
        with open(ARCHIVE_INDEX_YAML, 'w', encoding='utf-8') as f:
            yaml.dump(self.archive_index, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        # Save JSON
        with open(ARCHIVE_INDEX_JSON, 'w', encoding='utf-8') as f:
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

        with open(ARCHIVE_INDEX_MD, 'w', encoding='utf-8') as f:
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
        self.archive_index['archives'].append({
            'original_file': str(path.relative_to(BASE_PATH)),
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
            sigillin_files.extend(BASE_PATH.glob(pattern))

        # Filter out index files
        sigillin_files = [f for f in sigillin_files if '_index' not in f.name]

        print(f"Found {len(sigillin_files)} Sigillin candidates")

        archived_count = 0
        for sigillin_path in sigillin_files:
            if self.archive_sigillin(sigillin_path):
                archived_count += 1

        print(f"\n✅ Scan complete: {archived_count} files archived")


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

    args = parser.parse_args()

    if not args.sigillin and not args.scan_all:
        parser.print_help()
        sys.exit(1)

    archiver = SigillinArchiver(
        max_entries=args.max_entries,
        max_size_kb=args.max_size,
        keep_recent=args.keep_recent,
        dry_run=args.dry_run
    )

    if args.sigillin:
        archiver.archive_sigillin(args.sigillin)
    elif args.scan_all:
        archiver.scan_all_sigillin()


if __name__ == '__main__':
    main()
