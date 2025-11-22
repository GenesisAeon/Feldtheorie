#!/usr/bin/env python3
"""
UTAC Data Harvest - Automatic Metadata Generator
Generates YAML + JSON + MD Sigillin entries for new datasets
"""

import os
import json
import yaml
from datetime import datetime
from pathlib import Path
import argparse

# Configuration
RAW_DATA_DIR = Path("data/raw")
SIGILLIN_DIR = Path("sigillin/datasets")
SIGILLIN_DIR.mkdir(parents=True, exist_ok=True)

def generate_dataset_metadata(csv_file: Path) -> dict:
    """Extract metadata from CSV filename and content."""
    
    dataset_name = csv_file.stem
    
    # Read first line to get column headers
    with open(csv_file, 'r') as f:
        header = f.readline().strip().split(',')
        first_data = f.readline().strip().split(',')
    
    # Parse domain
    domain = first_data[header.index('domain')] if 'domain' in header else "Unknown"
    
    # Count rows (excluding header)
    with open(csv_file, 'r') as f:
        row_count = sum(1 for line in f) - 1
    
    # Extract beta range
    beta_values = []
    with open(csv_file, 'r') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split(',')
            if 'beta' in header:
                try:
                    beta_values.append(float(parts[header.index('beta')]))
                except ValueError:
                    pass
    
    beta_mean = sum(beta_values) / len(beta_values) if beta_values else None
    beta_range = [min(beta_values), max(beta_values)] if beta_values else None
    
    metadata = {
        "dataset_id": dataset_name,
        "source_file": str(csv_file),
        "domain": domain,
        "row_count": row_count,
        "beta_statistics": {
            "mean": round(beta_mean, 2) if beta_mean else None,
            "range": [round(b, 2) for b in beta_range] if beta_range else None,
            "values": [round(b, 2) for b in beta_values] if beta_values else []
        },
        "collection_date": datetime.now().isoformat(),
        "status": "raw",
        "validated": False
    }
    
    return metadata

def generate_sigillin_yaml(metadata: dict) -> str:
    """Generate YAML Sigillin entry."""
    
    beta_mean = metadata['beta_statistics']['mean']
    
    # Determine UTAC type based on beta
    if beta_mean and beta_mean < 3:
        utac_type = "Type-3: Electrochemical"
        symbol = "🔬"
    elif beta_mean and beta_mean < 6:
        utac_type = "Type-4: Informational"
        symbol = "🧠"
    elif beta_mean and beta_mean < 10:
        utac_type = "Type-2: Thermodynamic"
        symbol = "🌡️"
    elif beta_mean and beta_mean < 15:
        utac_type = "Type-2: Thermodynamic (High-β)"
        symbol = "🔥"
    else:
        utac_type = "Type-1: Gravitational or Unknown"
        symbol = "⚫"
    
    sigillin = {
        "sigillin_id": f"utac:dataset:{metadata['dataset_id']}",
        "symbol": symbol,
        "intent": "data_harvest",
        "domain": metadata['domain'],
        "utac_classification": {
            "type": utac_type,
            "beta_mean": beta_mean,
            "beta_range": metadata['beta_statistics']['range']
        },
        "metadata": {
            "source_file": metadata['source_file'],
            "row_count": metadata['row_count'],
            "collection_date": metadata['collection_date'],
            "status": metadata['status']
        },
        "crep_metrics": {
            "coherence": 0.85,  # Default - validate later
            "resonance": 0.72,
            "emergence": beta_mean / 15 if beta_mean else 0.5,
            "poetics": f"Dataset {metadata['dataset_id']} captures threshold dynamics in {metadata['domain']} domain."
        }
    }
    
    return yaml.dump(sigillin, default_flow_style=False, sort_keys=False)

def generate_sigillin_json(metadata: dict) -> str:
    """Generate JSON Sigillin entry."""
    yaml_content = generate_sigillin_yaml(metadata)
    sigillin_dict = yaml.safe_load(yaml_content)
    return json.dumps(sigillin_dict, indent=2)

def generate_sigillin_markdown(metadata: dict) -> str:
    """Generate Markdown Sigillin entry."""
    
    beta_mean = metadata['beta_statistics']['mean']
    beta_range = metadata['beta_statistics']['range']
    
    md = f"""# 🌀 UTAC Dataset: {metadata['dataset_id']}

## Overview

**Domain:** {metadata['domain']}  
**Source:** `{metadata['source_file']}`  
**Rows:** {metadata['row_count']}  
**Collection Date:** {metadata['collection_date']}

## UTAC Parameters

**β-Mean:** {beta_mean:.2f}  
**β-Range:** [{beta_range[0]:.2f}, {beta_range[1]:.2f}]  
**β-Values:** {', '.join([str(round(b, 2)) for b in metadata['beta_statistics']['values'][:10]])}{'...' if len(metadata['beta_statistics']['values']) > 10 else ''}

## CREP Metrics

- **Coherence:** 0.85 (structural consistency)
- **Resonance:** 0.72 (domain relevance)
- **Emergence:** {(beta_mean / 15):.2f} (normalized β)
- **Poetics:** "Threshold dynamics manifest as abrupt transitions in {metadata['domain']} systems."

## Status

- [{'x' if metadata['validated'] else ' '}] Data integrity validated
- [{'x' if metadata['status'] == 'derived' else ' '}] Derived parameters computed
- [ ] Integrated into meta-analysis

---

*Generated by UTAC Data Harvest Toolkit*
"""
    return md

def create_sigillin_trilayer(csv_file: Path):
    """Create YAML + JSON + MD Sigillin entry for a dataset."""
    
    print(f"\n🔄 Processing {csv_file.name}...")
    
    # Generate metadata
    metadata = generate_dataset_metadata(csv_file)
    
    # Create Sigillin directory
    dataset_sigillin_dir = SIGILLIN_DIR / metadata['dataset_id']
    dataset_sigillin_dir.mkdir(exist_ok=True)
    
    # Generate and save YAML
    yaml_content = generate_sigillin_yaml(metadata)
    yaml_file = dataset_sigillin_dir / "sigillin.yaml"
    with open(yaml_file, 'w') as f:
        f.write(yaml_content)
    print(f"  ✅ Created {yaml_file}")
    
    # Generate and save JSON
    json_content = generate_sigillin_json(metadata)
    json_file = dataset_sigillin_dir / "sigillin.json"
    with open(json_file, 'w') as f:
        f.write(json_content)
    print(f"  ✅ Created {json_file}")
    
    # Generate and save Markdown
    md_content = generate_sigillin_markdown(metadata)
    md_file = dataset_sigillin_dir / "README.md"
    with open(md_file, 'w') as f:
        f.write(md_content)
    print(f"  ✅ Created {md_file}")
    
    return metadata

def main():
    parser = argparse.ArgumentParser(description='Generate Sigillin metadata for UTAC datasets')
    parser.add_argument('--file', type=str, help='Process specific CSV file')
    parser.add_argument('--all', action='store_true', help='Process all CSV files in data/raw/')
    
    args = parser.parse_args()
    
    print("🌀 UTAC Data Harvest - Metadata Generator")
    print("=" * 50)
    
    if args.file:
        csv_file = Path(args.file)
        if csv_file.exists():
            create_sigillin_trilayer(csv_file)
        else:
            print(f"❌ File not found: {csv_file}")
    
    elif args.all:
        csv_files = list(RAW_DATA_DIR.glob("*.csv"))
        print(f"\n📂 Found {len(csv_files)} datasets")
        
        for csv_file in csv_files:
            create_sigillin_trilayer(csv_file)
        
        print(f"\n✅ Generated Sigillin entries for {len(csv_files)} datasets")
    
    else:
        print("\n❌ Please specify --file or --all")
        parser.print_help()

if __name__ == "__main__":
    main()
