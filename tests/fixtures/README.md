# Test Fixtures

This directory contains minimal test datasets for fast unit testing.

## Purpose

- **Fast test execution**: Smaller datasets than production data
- **Deterministic**: Fixed seeds and known values for reproducibility
- **Comprehensive**: Cover edge cases (empty, NaN, outliers, single-point)

## Files

- `minimal_sigmoid.csv`: 20-point logistic curve (θ=0.5, β=4.2)
- `edge_cases.json`: Test cases for boundary conditions
- `test_metadata.json`: Minimal metadata matching schema

## Usage

```python
import json
from pathlib import Path

fixtures_dir = Path(__file__).parent / "fixtures"
with open(fixtures_dir / "edge_cases.json") as f:
    test_data = json.load(f)
```
