#!/usr/bin/env python3
"""
UTAC Data Harvest - Data Integrity Validator
Tests CSV data for completeness, type correctness, and UTAC consistency
"""

import csv
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Required columns
REQUIRED_COLUMNS = ['system', 'domain', 'R', 'Theta', 'beta', 'source', 'date_collected']

# Optional but recommended
RECOMMENDED_COLUMNS = ['zeta_R', 'license', 'notes']

# Data type validations
NUMERIC_COLUMNS = ['R', 'Theta', 'beta', 'zeta_R']

# UTAC parameter ranges (soft warnings)
BETA_RANGE = (1.0, 20.0)  # Expected β range across all domains
R_THETA_RATIO_RANGE = (0.5, 2.0)  # R should be close to Θ at threshold

class DataValidator:
    def __init__(self, csv_file: Path):
        self.csv_file = csv_file
        self.errors = []
        self.warnings = []
        self.row_count = 0
        
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks."""
        
        print(f"\n🔍 Validating {self.csv_file.name}")
        print("-" * 50)
        
        # Read CSV
        try:
            with open(self.csv_file, 'r') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                rows = list(reader)
        except Exception as e:
            self.errors.append(f"Failed to read CSV: {e}")
            return False, self.errors, self.warnings
        
        self.row_count = len(rows)
        
        # Validation checks
        self._check_required_columns(headers)
        self._check_recommended_columns(headers)
        self._check_row_integrity(rows, headers)
        self._check_utac_consistency(rows)
        
        # Report
        is_valid = len(self.errors) == 0
        
        if is_valid:
            print(f"✅ PASSED - {self.row_count} rows validated")
        else:
            print(f"❌ FAILED - {len(self.errors)} errors found")
        
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warnings")
        
        return is_valid, self.errors, self.warnings
    
    def _check_required_columns(self, headers: List[str]):
        """Ensure all required columns are present."""
        missing = [col for col in REQUIRED_COLUMNS if col not in headers]
        if missing:
            self.errors.append(f"Missing required columns: {', '.join(missing)}")
        else:
            print(f"  ✓ All required columns present")
    
    def _check_recommended_columns(self, headers: List[str]):
        """Check for recommended columns."""
        missing = [col for col in RECOMMENDED_COLUMNS if col not in headers]
        if missing:
            self.warnings.append(f"Missing recommended columns: {', '.join(missing)}")
    
    def _check_row_integrity(self, rows: List[Dict], headers: List[str]):
        """Check each row for data integrity."""
        
        for i, row in enumerate(rows, start=2):  # Start at 2 (1 is header)
            
            # Check for empty required fields
            for col in REQUIRED_COLUMNS:
                if col in headers and (not row.get(col) or row[col].strip() == ''):
                    self.errors.append(f"Row {i}: Empty value in required column '{col}'")
            
            # Check numeric columns
            for col in NUMERIC_COLUMNS:
                if col in headers and row.get(col):
                    try:
                        float(row[col])
                    except ValueError:
                        self.errors.append(f"Row {i}: Invalid numeric value in '{col}': {row[col]}")
        
        if not self.errors:
            print(f"  ✓ All {self.row_count} rows have complete data")
    
    def _check_utac_consistency(self, rows: List[Dict]):
        """Check UTAC parameter consistency."""
        
        beta_values = []
        r_values = []
        theta_values = []
        
        for i, row in enumerate(rows, start=2):
            try:
                if 'beta' in row and row['beta']:
                    beta = float(row['beta'])
                    beta_values.append((i, beta))
                    
                    # Check β range
                    if beta < BETA_RANGE[0] or beta > BETA_RANGE[1]:
                        self.warnings.append(f"Row {i}: β={beta:.2f} outside typical range {BETA_RANGE}")
                
                if 'R' in row and row['R']:
                    r = float(row['R'])
                    r_values.append((i, r))
                
                if 'Theta' in row and row['Theta']:
                    theta = float(row['Theta'])
                    theta_values.append((i, theta))
            
            except ValueError:
                pass  # Already caught in row integrity check
        
        # Check R vs Θ consistency
        if r_values and theta_values:
            for (r_idx, r), (t_idx, theta) in zip(r_values, theta_values):
                if theta != 0:
                    ratio = abs(r / theta)
                    if ratio < R_THETA_RATIO_RANGE[0] or ratio > R_THETA_RATIO_RANGE[1]:
                        if abs(r - theta) / theta > 0.5:  # More than 50% deviation
                            self.warnings.append(f"Row {r_idx}: R/Θ ratio={ratio:.2f} may indicate pre/post-tipping state")
        
        # Summary statistics
        if beta_values:
            betas = [b for _, b in beta_values]
            print(f"  ✓ β-range: [{min(betas):.2f}, {max(betas):.2f}], mean: {sum(betas)/len(betas):.2f}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate UTAC dataset integrity')
    parser.add_argument('file', type=str, nargs='?', help='CSV file to validate')
    parser.add_argument('--all', action='store_true', help='Validate all files in data/raw/')
    
    args = parser.parse_args()
    
    print("🌀 UTAC Data Harvest - Integrity Validator")
    print("=" * 50)
    
    data_dir = Path("data/raw")
    
    if args.all:
        csv_files = list(data_dir.glob("*.csv"))
        print(f"\n📂 Found {len(csv_files)} datasets to validate\n")
        
        results = []
        for csv_file in csv_files:
            validator = DataValidator(csv_file)
            is_valid, errors, warnings = validator.validate()
            results.append((csv_file.name, is_valid, errors, warnings))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for _, valid, _, _ in results if valid)
        print(f"\n✅ Passed: {passed}/{len(results)}")
        print(f"❌ Failed: {len(results) - passed}/{len(results)}")
        
        # Show errors
        for name, valid, errors, warnings in results:
            if not valid:
                print(f"\n❌ {name}:")
                for error in errors:
                    print(f"   - {error}")
        
        return 0 if passed == len(results) else 1
    
    elif args.file:
        csv_file = Path(args.file)
        if not csv_file.exists():
            print(f"\n❌ File not found: {csv_file}")
            return 1
        
        validator = DataValidator(csv_file)
        is_valid, errors, warnings = validator.validate()
        
        if errors:
            print("\n❌ ERRORS:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
        
        return 0 if is_valid else 1
    
    else:
        print("\n❌ Please specify a file or use --all")
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
