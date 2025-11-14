#!/usr/bin/env python3
"""
UTAC Data Harvest - Progress Dashboard
Shows current status of data collection toward 75-100 dataset goal
"""

import json
from pathlib import Path
from collections import defaultdict

RAW_DATA_DIR = Path("data/raw")
SIGILLIN_DIR = Path("sigillin/datasets")

def load_dataset_stats():
    """Load statistics from all datasets."""
    
    datasets = []
    
    for sigillin_dir in SIGILLIN_DIR.iterdir():
        if sigillin_dir.is_dir():
            json_file = sigillin_dir / "sigillin.json"
            if json_file.exists():
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    datasets.append(data)
    
    return datasets

def print_dashboard():
    """Display progress dashboard."""
    
    datasets = load_dataset_stats()
    
    print("\n🌀 UTAC DATA HARVEST - PROGRESS DASHBOARD")
    print("=" * 70)
    
    # Overall progress
    total = len(datasets)
    goal_min = 75
    goal_max = 100
    
    progress_pct = (total / goal_min) * 100
    progress_bar_length = 50
    filled = int((total / goal_min) * progress_bar_length)
    bar = "█" * filled + "░" * (progress_bar_length - filled)
    
    print(f"\n📊 OVERALL PROGRESS: {total}/{goal_min}-{goal_max} datasets")
    print(f"[{bar}] {progress_pct:.1f}%")
    
    # Domain breakdown
    print(f"\n📂 DOMAINS:")
    domain_counts = defaultdict(int)
    domain_betas = defaultdict(list)
    
    for dataset in datasets:
        domain = dataset['domain']
        beta_mean = dataset['utac_classification']['beta_mean']
        domain_counts[domain] += 1
        if beta_mean:
            domain_betas[domain].append(beta_mean)
    
    for domain in sorted(domain_counts.keys()):
        count = domain_counts[domain]
        betas = domain_betas[domain]
        beta_avg = sum(betas) / len(betas) if betas else 0
        
        # Symbol based on domain
        symbols = {
            'Climate': '🌡️',
            'AI': '🧠',
            'Neuroscience': '🔬',
            'Economics': '💰',
            'Biology': '🦠',
            'Astrophysics': '⚫'
        }
        symbol = symbols.get(domain, '📊')
        
        print(f"  {symbol} {domain:20} {count:3} datasets  (β̄ = {beta_avg:.2f})")
    
    # UTAC Type distribution
    print(f"\n🎯 UTAC TYPES:")
    type_counts = defaultdict(int)
    
    for dataset in datasets:
        utac_type = dataset['utac_classification']['type']
        type_counts[utac_type] += 1
    
    for utac_type in sorted(type_counts.keys()):
        count = type_counts[utac_type]
        print(f"  • {utac_type:35} {count:3} datasets")
    
    # β-parameter distribution
    print(f"\n📈 β-DISTRIBUTION:")
    all_betas = []
    for dataset in datasets:
        beta_mean = dataset['utac_classification']['beta_mean']
        if beta_mean:
            all_betas.append(beta_mean)
    
    if all_betas:
        print(f"  Min:  {min(all_betas):.2f}")
        print(f"  Mean: {sum(all_betas)/len(all_betas):.2f}")
        print(f"  Max:  {max(all_betas):.2f}")
        
        # Histogram
        bins = [0, 3, 6, 10, 15, 20]
        bin_labels = ["0-3", "3-6", "6-10", "10-15", "15+"]
        hist = [0] * len(bin_labels)
        
        for beta in all_betas:
            for i, (low, high) in enumerate(zip(bins[:-1], bins[1:])):
                if low <= beta < high:
                    hist[i] += 1
                    break
            else:
                if beta >= bins[-1]:
                    hist[-1] += 1
        
        print(f"\n  β-Range Distribution:")
        for label, count in zip(bin_labels, hist):
            bar = "█" * count
            print(f"    {label:8} {bar} ({count})")
    
    # Next steps
    print(f"\n🎯 NEXT MILESTONES:")
    
    remaining_to_30 = max(0, 30 - total)
    remaining_to_75 = max(0, 75 - total)
    
    if total < 30:
        print(f"  • Reach 30 datasets: {remaining_to_30} more needed ⏰ DEADLINE: 3 days")
    elif total < 60:
        remaining_to_60 = 60 - total
        print(f"  ✅ First milestone (30) reached!")
        print(f"  • Reach 60 datasets: {remaining_to_60} more needed ⏰ DEADLINE: 1 week")
    elif total < 75:
        print(f"  ✅ First two milestones reached!")
        print(f"  • Reach minimum goal (75): {remaining_to_75} more needed ⏰ DEADLINE: 10 days")
    else:
        print(f"  ✅ MINIMUM GOAL REACHED! ({total}/75)")
        if total < 100:
            remaining_to_100 = 100 - total
            print(f"  • Optional: Reach 100 datasets ({remaining_to_100} more)")
        else:
            print(f"  🎉 MAXIMUM GOAL ACHIEVED! ({total}/100)")
    
    print("\n" + "=" * 70)
    print("📝 Run 'python3 scripts/generate_sigillin.py --all' to refresh metadata")
    print("🔍 Run 'python3 tests/test_data_integrity.py --all' to validate data\n")

if __name__ == "__main__":
    try:
        print_dashboard()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure you're in the utac-data-harvest directory")
        print("   and have run 'python3 scripts/generate_sigillin.py --all' first\n")
