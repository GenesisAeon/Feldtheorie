#!/usr/bin/env python3
"""Regenerate all Trilayer YAML files from their JSON counterparts."""
import json
import yaml
from pathlib import Path

def regenerate_all():
    seed_dir = Path('/home/user/Feldtheorie/seed')

    # Find all JSON files
    json_files = list(seed_dir.rglob('*.json'))

    regenerated = []
    errors = []

    for json_file in json_files:
        yaml_file = json_file.with_suffix('.yaml')

        # Skip if no corresponding YAML exists
        if not yaml_file.exists():
            continue

        try:
            # Load JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Write as YAML
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False,
                         default_flow_style=False, width=120)

            regenerated.append(str(yaml_file.relative_to(seed_dir)))

        except Exception as e:
            errors.append(f"{json_file.relative_to(seed_dir)}: {str(e)}")

    print(f"✓ Regenerated {len(regenerated)} YAML files from JSON")
    if errors:
        print(f"\n✗ {len(errors)} errors:")
        for err in errors[:10]:  # Show first 10 errors
            print(f"  - {err}")

    if regenerated:
        print(f"\nSample regenerated files:")
        for f in regenerated[:5]:
            print(f"  - {f}")

if __name__ == '__main__':
    regenerate_all()
