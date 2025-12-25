# UTAC Unified CLI

**Unified Command-Line Interface for Feldtheorie UTAC Analysis**

---

## Overview

The `utac` CLI consolidates 80+ fragmented analysis scripts into a cohesive, structured command hierarchy with consistent parameter naming, unified help documentation, and standardized output formats.

### Why Unified CLI?

**Before:**
```bash
utf-batch --output results.json
utf-planetary-summary -o output/  # Inconsistent flag names
utf-resonance-cohort --format yaml
python analysis/resonance_fit_pipeline.py  # No standardization
```

**After:**
```bash
utac analyze batch -o results.json -f json
utac analyze planetary -o output/tipping.csv -f csv
utac analyze cohort -o cohort.yaml -f yaml
utac fit pipeline input.csv -o results.json
```

---

## Installation

The `utac` command is automatically installed when you install the Feldtheorie package:

```bash
pip install -e .
```

Verify installation:
```bash
utac --help
```

---

## Command Structure

```
utac
├── analyze          # Run threshold field analyses
│   ├── batch        # Batch UTAC analysis across datasets
│   ├── planetary    # Planetary tipping elements
│   └── cohort       # Cohort summary generation
├── fit              # Fit threshold models
│   ├── logistic     # Fit logistic threshold model
│   └── pipeline     # Full resonance fit pipeline
├── audit            # Data validation & metadata audits
│   └── data         # Audit data source completeness
├── utils            # Utility commands
│   ├── validate     # Validate files against schemas
│   └── export       # Export data to different formats
└── version          # Show version information
```

---

## Quick Start

### 1. Batch Analysis

Run batch UTAC analysis across multiple datasets:

```bash
utac analyze batch -o results.json -f json
```

**Options:**
- `-o, --output PATH` - Output file path (default: `results.json`)
- `-f, --format FORMAT` - Output format: `json`, `yaml`, `csv` (default: `json`)
- `-c, --config PATH` - Path to batch configuration JSON
- `-v, --verbose` - Enable verbose logging

### 2. Planetary Tipping Analysis

Analyze planetary tipping elements (climate thresholds):

```bash
utac analyze planetary -o planetary_tipping.csv -f csv
```

### 3. Cohort Summary

Generate cohort summary across all resonance fits:

```bash
utac analyze cohort -o cohort_summary.yaml -f yaml
```

### 4. Fit Logistic Model

Fit logistic threshold model to a single dataset:

```bash
utac fit logistic input.csv -o fit_results.json --x-col scale --y-col performance
```

**Options:**
- `--x-col NAME` - Column name for x-axis (resource/scale) (default: `x`)
- `--y-col NAME` - Column name for y-axis (response) (default: `y`)
- `--seed INT` - Random seed for reproducibility
- `-v, --verbose` - Enable verbose logging

### 5. Full Resonance Pipeline

Run full resonance fit pipeline with null model comparison:

```bash
utac fit pipeline input.csv -o pipeline_results.json --x-col R --y-col zeta
```

### 6. Data Audit

Audit data sources for metadata completeness:

```bash
utac audit data -o audit_report.json -f json --fix
```

**Options:**
- `--fix` - Generate fix scripts for incomplete metadata

---

## Standardized Flags

All `utac` commands use consistent parameter naming:

| Flag | Long Form | Description | Default |
|------|-----------|-------------|---------|
| `-o` | `--output` | Output file path | varies |
| `-f` | `--format` | Output format (`json`, `yaml`, `csv`) | `json` |
| `-v` | `--verbose` | Enable verbose logging | `False` |
| `--seed` | `--seed` | Random seed for reproducibility | `None` |
| `--workers` | `--workers` | Number of parallel workers | CPU count |

---

## Examples

### Example 1: Batch Analysis with Custom Config

```bash
utac analyze batch \
  --config analysis/batch_configs/resonance_runs.json \
  --output results/batch_output.json \
  --format json \
  --verbose
```

### Example 2: Fit Pipeline with Reproducible Seed

```bash
utac fit pipeline data/ai/wei_emergent_abilities.csv \
  --output results/wei_fit.json \
  --x-col scale \
  --y-col performance \
  --seed 42 \
  --verbose
```

### Example 3: Data Audit with Auto-Fix

```bash
utac audit data \
  --output reports/data_audit.markdown \
  --format markdown \
  --fix \
  --verbose
```

---

## Migration Guide

Migrating from legacy `utf-*` commands to `utac`:

| Legacy Command | New `utac` Command |
|----------------|-------------------|
| `utf-batch` | `utac analyze batch` |
| `utf-planetary-summary` | `utac analyze planetary` |
| `utf-resonance-cohort` | `utac analyze cohort` |
| `python analysis/resonance_fit_pipeline.py` | `utac fit pipeline` |

**Note:** Legacy commands are still available but deprecated. They will be removed in v6.0.

---

## Help & Documentation

Get help for any command:

```bash
utac --help                    # Main help
utac analyze --help            # Analyze commands help
utac analyze batch --help      # Batch analysis help
utac fit --help                # Fit commands help
utac fit logistic --help       # Logistic fit help
```

---

## Architecture

The unified CLI is built with:

- **[Typer](https://typer.tiangolo.com/)** - Modern CLI framework with type hints
- **[Rich](https://rich.readthedocs.io/)** - Beautiful terminal formatting
- **Consistent Interface** - Standardized flags across all commands

---

## Future Enhancements

Planned features for future releases:

- [ ] **Parallel Batch Processing** - `--workers` flag for multiprocessing
- [ ] **Progress Bars** - Rich progress indicators for long-running analyses
- [ ] **Interactive Mode** - `utac interactive` for guided workflows
- [ ] **Config Templates** - `utac config generate` for batch configs
- [ ] **Result Visualization** - `utac plot` for quick visualizations

---

## Troubleshooting

### Command not found: `utac`

Reinstall the package in editable mode:
```bash
pip install -e .
```

### Import errors

Ensure all dependencies are installed:
```bash
pip install -e ".[all]"
```

---

## Contributing

To add new commands to the unified CLI:

1. Open `cli/main.py`
2. Add your command to the appropriate Typer app (`analyze_app`, `fit_app`, etc.)
3. Use consistent parameter naming (see "Standardized Flags" above)
4. Update this README with examples
5. Write tests in `tests/test_cli.py`

---

**Version:** 1.0.0
**Last Updated:** 2025-12-25
**Maintainer:** Universal Threshold Field Collective
