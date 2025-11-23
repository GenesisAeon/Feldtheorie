#!/usr/bin/env python3
"""
Champollion Recursive Diamond Indexer
======================================

A bottom-up fractal documentation system that automatically generates:
- Machine-readable indices (YAML)
- Human-readable summaries (Markdown)
- Context metadata (JSON)

The system propagates information from leaf nodes to root, creating
self-maintaining documentation at every level of the hierarchy.

Author: Feldtheorie Project
License: MIT
Version: 1.0.0
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import re
import sys

# Add parent directory to path for engine import
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from engines.dynamic_crep import DynamicMetricEngine, format_metrics_for_display
    SIGILLIN_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Dynamic Sigillin Engine not available: {e}")
    SIGILLIN_ENGINE_AVAILABLE = False

# =============================================================================
# CONFIGURATION
# =============================================================================

IGNORED_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv',
    'archive', '.pytest_cache', '.mypy_cache', 'dist', 'build',
    '.idea', '.vscode', 'logs'
}

IGNORED_FILES = {
    '.DS_Store', 'Thumbs.db', '.gitkeep',
    'folder_index.yaml', 'folder_context.json'  # Don't index our own outputs
}

METADATA_FILENAMES = {'meta.json', 'metadata.json', 'info.json'}

CONFIDENCE_THRESHOLD_WARNING = 0.5

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def is_ignored(path: Path) -> bool:
    """Check if a path should be ignored."""
    return path.name in IGNORED_DIRS or path.name in IGNORED_FILES


def safe_load_json(filepath: Path) -> Optional[Dict[str, Any]]:
    """Safely load JSON file, return None on error."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️  Warning: Could not load {filepath}: {e}")
        return None


def safe_load_yaml(filepath: Path) -> Optional[Dict[str, Any]]:
    """Safely load YAML file, return None on error."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, IOError) as e:
        print(f"⚠️  Warning: Could not load {filepath}: {e}")
        return None


def extract_confidence(metadata: Dict[str, Any]) -> float:
    """Extract confidence score from metadata (default: 1.0)."""
    return float(metadata.get('confidence', metadata.get('confidence_level', 1.0)))


def extract_origin(metadata: Dict[str, Any]) -> str:
    """Extract data origin label."""
    return metadata.get('origin', metadata.get('data_origin', 'unknown'))


def check_governance_violation(metadata: Dict[str, Any]) -> List[str]:
    """Check for potential governance policy violations."""
    violations = []

    # Check for PII indicators
    text = json.dumps(metadata).lower()
    pii_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\bpassword\b', r'\bsecret\b', r'\bapi[_-]?key\b'
    ]

    for pattern in pii_patterns:
        if re.search(pattern, text):
            violations.append(f"Potential PII/Secret detected: {pattern}")

    # Check origin label
    origin = extract_origin(metadata)
    if origin not in ['empirical', 'synthetic', 'theoretical', 'hybrid', 'unknown']:
        violations.append(f"Invalid origin label: {origin}")

    return violations


# =============================================================================
# AGGREGATION FUNCTIONS
# =============================================================================

def aggregate_folder_metadata(folder_path: Path) -> Dict[str, Any]:
    """
    Collect and aggregate all metadata from files and subfolders.

    Returns:
        Dictionary with aggregated statistics and references
    """
    aggregated = {
        'folder_name': folder_path.name,
        'folder_path': str(folder_path.relative_to(Path.cwd())),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'total_files': 0,
        'total_subfolders': 0,
        'metadata_files': [],
        'subfolder_contexts': [],
        'origins': defaultdict(int),
        'confidence_scores': [],
        'governance_violations': [],
        'keywords': set(),
        'file_types': defaultdict(int)
    }

    # Scan immediate children only (not recursive)
    try:
        for item in folder_path.iterdir():
            if is_ignored(item):
                continue

            if item.is_file():
                aggregated['total_files'] += 1
                aggregated['file_types'][item.suffix] += 1

                # Check for metadata files
                if item.name in METADATA_FILENAMES:
                    metadata = safe_load_json(item)
                    if metadata:
                        aggregated['metadata_files'].append({
                            'file': item.name,
                            'origin': extract_origin(metadata),
                            'confidence': extract_confidence(metadata)
                        })

                        # Aggregate statistics
                        origin = extract_origin(metadata)
                        aggregated['origins'][origin] += 1

                        confidence = extract_confidence(metadata)
                        aggregated['confidence_scores'].append(confidence)

                        # Check governance
                        violations = check_governance_violation(metadata)
                        if violations:
                            aggregated['governance_violations'].extend([
                                {'file': item.name, 'violation': v} for v in violations
                            ])

                        # Extract keywords
                        if 'keywords' in metadata:
                            aggregated['keywords'].update(metadata['keywords'])
                        if 'tags' in metadata:
                            aggregated['keywords'].update(metadata['tags'])

            elif item.is_dir():
                aggregated['total_subfolders'] += 1

                # Check for child folder context
                child_context = item / 'folder_context.json'
                if child_context.exists():
                    context = safe_load_json(child_context)
                    if context:
                        aggregated['subfolder_contexts'].append({
                            'folder': item.name,
                            'summary': context.get('summary', ''),
                            'confidence': context.get('aggregate_confidence', 1.0),
                            'total_items': context.get('total_files', 0)
                        })

                        # Propagate confidence scores up
                        if 'aggregate_confidence' in context:
                            aggregated['confidence_scores'].append(context['aggregate_confidence'])

                        # Propagate keywords up
                        if 'keywords' in context:
                            aggregated['keywords'].update(context['keywords'])

    except PermissionError as e:
        print(f"⚠️  Permission denied: {folder_path}: {e}")

    # Convert sets to lists for JSON serialization
    aggregated['keywords'] = sorted(list(aggregated['keywords']))
    aggregated['origins'] = dict(aggregated['origins'])
    aggregated['file_types'] = dict(aggregated['file_types'])

    # Calculate aggregate confidence
    if aggregated['confidence_scores']:
        aggregated['aggregate_confidence'] = sum(aggregated['confidence_scores']) / len(aggregated['confidence_scores'])
        aggregated['min_confidence'] = min(aggregated['confidence_scores'])
        aggregated['max_confidence'] = max(aggregated['confidence_scores'])
    else:
        aggregated['aggregate_confidence'] = 1.0
        aggregated['min_confidence'] = 1.0
        aggregated['max_confidence'] = 1.0

    return aggregated


# =============================================================================
# OUTPUT GENERATION
# =============================================================================

def generate_yaml_index(aggregated: Dict[str, Any], output_path: Path, sigillin_metrics: Optional[Dict[str, Any]] = None):
    """Generate machine-readable YAML index."""
    index = {
        'folder': aggregated['folder_name'],
        'indexed_at': aggregated['timestamp'],
        'statistics': {
            'files': aggregated['total_files'],
            'subfolders': aggregated['total_subfolders'],
            'metadata_sources': len(aggregated['metadata_files'])
        },
        'confidence': {
            'aggregate': round(aggregated['aggregate_confidence'], 3),
            'min': round(aggregated['min_confidence'], 3),
            'max': round(aggregated['max_confidence'], 3)
        },
        'origins': aggregated['origins'],
        'file_types': aggregated['file_types'],
        'keywords': aggregated['keywords'],
        'subfolders': [sf['folder'] for sf in aggregated['subfolder_contexts']],
        'governance': {
            'violations_count': len(aggregated['governance_violations']),
            'has_violations': len(aggregated['governance_violations']) > 0
        }
    }

    # Add Sigillin metrics if available
    if sigillin_metrics:
        index['sigillin_metrics'] = {
            'aggregate_score': sigillin_metrics['aggregate_score'],
            'components': {
                key: {
                    'value': metric['value'],
                    'label': metric['label'],
                    'status': metric.get('threshold_status', 'unknown')
                }
                for key, metric in sigillin_metrics.get('metrics', {}).items()
            }
        }

    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✅ Generated: {output_path}")


def generate_markdown_readme(aggregated: Dict[str, Any], output_path: Path, sigillin_metrics: Optional[Dict[str, Any]] = None):
    """Generate human-readable Markdown README."""
    confidence = aggregated['aggregate_confidence']

    # Determine confidence indicator
    if confidence >= 0.9:
        confidence_indicator = "🟢 High"
    elif confidence >= 0.7:
        confidence_indicator = "🟡 Medium"
    elif confidence >= 0.5:
        confidence_indicator = "🟠 Low"
    else:
        confidence_indicator = "🔴 Critical"

    # Build README content
    lines = [
        f"# {aggregated['folder_name']}",
        "",
        f"**Auto-generated:** {aggregated['timestamp']}",
        f"**Confidence:** {confidence_indicator} ({confidence:.2%})",
        ""
    ]

    # Add Sigillin metrics section if available
    if sigillin_metrics:
        lines.extend([
            "## 📊 System Metrics (Dynamic Sigillin)",
            "",
            format_metrics_for_display(sigillin_metrics),
            ""
        ])

    # Warning for governance violations
    if aggregated['governance_violations']:
        lines.extend([
            "## ⚠️ Governance Violations Detected",
            "",
            "**CRITICAL:** This folder contains data that may violate DATA_GOVERNANCE policies.",
            ""
        ])
        for violation in aggregated['governance_violations'][:5]:  # Show first 5
            lines.append(f"- `{violation['file']}`: {violation['violation']}")
        lines.append("")

    # Overview
    lines.extend([
        "## Overview",
        "",
        f"This folder contains:",
        f"- **{aggregated['total_files']}** files",
        f"- **{aggregated['total_subfolders']}** subfolders",
        f"- **{len(aggregated['metadata_files'])}** metadata sources",
        ""
    ])

    # Data origins
    if aggregated['origins']:
        lines.extend(["## Data Origins", ""])
        for origin, count in aggregated['origins'].items():
            emoji = {
                'empirical': '🔬',
                'synthetic': '🤖',
                'theoretical': '📐',
                'hybrid': '🔀'
            }.get(origin, '❓')
            lines.append(f"- {emoji} **{origin.capitalize()}**: {count} item(s)")
        lines.append("")

    # Subfolders
    if aggregated['subfolder_contexts']:
        lines.extend(["## Subfolders", ""])
        for sf in aggregated['subfolder_contexts']:
            conf_emoji = "🟢" if sf['confidence'] >= 0.9 else "🟡" if sf['confidence'] >= 0.7 else "🔴"
            lines.append(f"### {conf_emoji} `{sf['folder']}/`")
            if sf['summary']:
                lines.append(f"{sf['summary']}")
            lines.append(f"*{sf['total_items']} items, confidence: {sf['confidence']:.2%}*")
            lines.append("")

    # Keywords
    if aggregated['keywords']:
        lines.extend([
            "## Keywords",
            "",
            ", ".join(f"`{kw}`" for kw in aggregated['keywords'][:20]),  # Limit to 20
            ""
        ])

    # File types
    if aggregated['file_types']:
        lines.extend(["## File Types", ""])
        for ext, count in sorted(aggregated['file_types'].items(), key=lambda x: -x[1]):
            lines.append(f"- `{ext or '(no extension)'}`: {count}")
        lines.append("")

    # Footer
    lines.extend([
        "---",
        "",
        "*This README was automatically generated by the Champollion Diamond Indexer.*",
        "*See `DATA_GOVERNANCE.md` for data policies.*"
    ])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✅ Generated: {output_path}")


def generate_context_json(aggregated: Dict[str, Any], output_path: Path, sigillin_metrics: Optional[Dict[str, Any]] = None):
    """Generate context metadata for parent folder consumption."""
    # Create a lighter version for upward propagation
    context = {
        'folder': aggregated['folder_name'],
        'indexed_at': aggregated['timestamp'],
        'summary': f"{aggregated['total_files']} files, {aggregated['total_subfolders']} subfolders",
        'total_files': aggregated['total_files'],
        'total_subfolders': aggregated['total_subfolders'],
        'aggregate_confidence': aggregated['aggregate_confidence'],
        'min_confidence': aggregated['min_confidence'],
        'origins': aggregated['origins'],
        'keywords': aggregated['keywords'][:10],  # Top 10 keywords only
        'has_violations': len(aggregated['governance_violations']) > 0,
        'file_types': aggregated['file_types']
    }

    # Add Sigillin metrics (lightweight version for propagation)
    if sigillin_metrics:
        context['sigillin'] = {
            'aggregate_score': sigillin_metrics['aggregate_score'],
            'components': {
                key: metric['value']
                for key, metric in sigillin_metrics.get('metrics', {}).items()
            }
        }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(context, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated: {output_path}")


# =============================================================================
# MAIN INDEXING LOGIC
# =============================================================================

def index_folder(folder_path: Path, dry_run: bool = False):
    """
    Index a single folder: aggregate data and generate outputs.

    Args:
        folder_path: Path to the folder to index
        dry_run: If True, only print what would be done
    """
    print(f"\n📂 Indexing: {folder_path.relative_to(Path.cwd())}")

    # Aggregate data
    aggregated = aggregate_folder_metadata(folder_path)

    # Calculate Dynamic Sigillin Metrics
    sigillin_metrics = None
    if SIGILLIN_ENGINE_AVAILABLE:
        try:
            engine = DynamicMetricEngine()
            sigillin_metrics = engine.calculate_all_metrics(aggregated)
            print(f"   📊 Sigillin Score: {sigillin_metrics['aggregate_score']:.3f}")
        except Exception as e:
            print(f"   ⚠️  Failed to calculate Sigillin metrics: {e}")

    # Show warnings
    if aggregated['aggregate_confidence'] < CONFIDENCE_THRESHOLD_WARNING:
        print(f"   ⚠️  Low confidence: {aggregated['aggregate_confidence']:.2%}")

    if aggregated['governance_violations']:
        print(f"   🚨 Governance violations: {len(aggregated['governance_violations'])}")

    if dry_run:
        print("   (Dry run - no files written)")
        return

    # Generate outputs (pass sigillin_metrics to each)
    generate_yaml_index(aggregated, folder_path / 'folder_index.yaml', sigillin_metrics)
    generate_markdown_readme(aggregated, folder_path / 'README.md', sigillin_metrics)
    generate_context_json(aggregated, folder_path / 'folder_context.json', sigillin_metrics)


def recursive_index(root_path: Path, dry_run: bool = False):
    """
    Recursively index all folders from bottom to top.

    Args:
        root_path: Root directory to start indexing
        dry_run: If True, only show what would be done
    """
    print(f"🚀 Starting recursive indexing from: {root_path}")
    print(f"   Dry run: {dry_run}")
    print("=" * 80)

    # Use os.walk with topdown=False for bottom-up traversal
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        folder_path = Path(dirpath)

        # Skip ignored directories
        if is_ignored(folder_path):
            continue

        # Remove ignored subdirs from traversal
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

        # Index this folder
        try:
            index_folder(folder_path, dry_run=dry_run)
        except Exception as e:
            print(f"   ❌ Error indexing {folder_path}: {e}")

    print("\n" + "=" * 80)
    print("✅ Indexing complete!")


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Champollion Recursive Diamond Indexer - Self-documenting filesystem',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Index current directory
  %(prog)s modules/champollion      # Index specific path
  %(prog)s --dry-run                # Preview without writing
  %(prog)s --root /path/to/data     # Index from specific root
        """
    )

    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to index (default: current directory)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview indexing without writing files'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Resolve path
    target_path = Path(args.path).resolve()

    if not target_path.exists():
        print(f"❌ Error: Path does not exist: {target_path}")
        return 1

    if not target_path.is_dir():
        print(f"❌ Error: Path is not a directory: {target_path}")
        return 1

    # Run indexing
    try:
        recursive_index(target_path, dry_run=args.dry_run)
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Indexing interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
