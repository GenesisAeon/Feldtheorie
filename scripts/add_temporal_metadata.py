#!/usr/bin/env python3
"""
Add Temporal Metadata to Seed Index
Extracts Git timestamps (created, modified, version, change_count) for all seed/ documents
"""

import subprocess
import yaml
from pathlib import Path
from datetime import datetime

def get_git_timestamps(file_path):
    """Extract git timestamps for a file"""
    try:
        # Get first commit (created)
        created_result = subprocess.run(
            ['git', 'log', '--reverse', '--format=%aI', '--follow', str(file_path)],
            capture_output=True, text=True, cwd='/home/user/Feldtheorie'
        )
        created_dates = created_result.stdout.strip().split('\n')
        created = created_dates[0] if created_dates and created_dates[0] else None

        # Get last commit (modified)
        modified_result = subprocess.run(
            ['git', 'log', '-1', '--format=%aI', str(file_path)],
            capture_output=True, text=True, cwd='/home/user/Feldtheorie'
        )
        modified = modified_result.stdout.strip() or None

        # Get commit count (version)
        version_result = subprocess.run(
            ['git', 'log', '--oneline', '--follow', str(file_path)],
            capture_output=True, text=True, cwd='/home/user/Feldtheorie'
        )
        change_count = len([l for l in version_result.stdout.strip().split('\n') if l])

        return {
            'created': created,
            'modified': modified,
            'version': f"1.{change_count - 1}" if change_count > 0 else "1.0",
            'change_count': change_count
        }
    except Exception as e:
        print(f"Warning: Could not get timestamps for {file_path}: {e}")
        return None

def add_temporal_to_index(index_path):
    """Add temporal metadata to seed index"""

    # Load existing index
    with open(index_path, 'r', encoding='utf-8') as f:
        index = yaml.safe_load(f)

    print(f"Processing {len(index['documents'])} documents...")

    # Process each document
    updated_count = 0
    for doc in index['documents']:
        file_path = Path('/home/user/Feldtheorie/seed') / doc['path']

        if file_path.exists():
            temporal = get_git_timestamps(file_path)
            if temporal:
                doc['temporal'] = temporal
                updated_count += 1
                print(f"✓ {doc['title']}: {temporal['change_count']} changes, v{temporal['version']}")

    # Save updated index
    with open(index_path, 'w', encoding='utf-8') as f:
        yaml.dump(index, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    print(f"\n✅ Updated {updated_count} documents with temporal metadata!")
    return updated_count

if __name__ == '__main__':
    index_path = Path('/home/user/Feldtheorie/seed/seed_index.yaml')
    add_temporal_to_index(index_path)
