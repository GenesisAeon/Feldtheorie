# UTAC v2.0 Visualization Scripts

## 📊 Overview

This directory contains visualization scripts for UTAC v2.0 Multi-Attractor Framework analysis.

## Scripts

### `visualize_beta_distribution.py`

Creates publication-ready visualizations of β-parameter distribution:

1. **β-distribution histogram** with Φ^(n/3) attractor markers
2. **Domain clustering heatmap** showing β_mean by cluster
3. **β vs Domain plot** with 95% confidence intervals
4. **Φ-ladder log-scale visualization** with domain coloring

**Features:**
- SVG/PNG/PDF export for papers and presentations
- Automatic domain clustering (Informational, Biological, Climate, etc.)
- Φ^(n/3) attractor annotations (Φ³≈4.24, Φ⁴≈6.85, Φ⁵≈11.09)
- Individual plot exports for flexible use
- Summary statistics report

## Installation

### Option 1: Install visualization dependencies only

```bash
pip install -r scripts/requirements_visualization.txt
```

### Option 2: Install all project dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic usage (default: SVG output):

```bash
python scripts/visualize_beta_distribution.py
```

**Output:**
- `figures/utac_v2/utac_v2_beta_distribution.svg` (full suite)
- `figures/utac_v2/individual/*.svg` (4 individual plots)

### Custom output format:

```bash
# PNG for presentations
python scripts/visualize_beta_distribution.py --format png

# PDF for LaTeX documents
python scripts/visualize_beta_distribution.py --format pdf
```

### Custom input/output paths:

```bash
python scripts/visualize_beta_distribution.py \
    --input data/derived/beta_estimates.csv \
    --output-dir figures/custom/ \
    --format svg
```

## Output Files

### Main composite figure:
- `utac_v2_beta_distribution.{svg,png,pdf}` - 2x2 grid with all 4 plots

### Individual plots:
- `individual/utac_v2_histogram_phi_ladder.{svg,png,pdf}` - Histogram with Φ-attractors
- `individual/utac_v2_domain_heatmap.{svg,png,pdf}` - Cluster heatmap
- `individual/utac_v2_beta_with_ci.{svg,png,pdf}` - β-values with CI sorted
- `individual/utac_v2_phi_ladder_logscale.{svg,png,pdf}` - Log-scale scatter with ladder

## Input Data

The script reads from `data/derived/beta_estimates.csv` which contains:
- 36 β-estimates across 12 domains
- 95% confidence intervals
- R² and ΔAIC validation metrics

See `data/derived/beta_estimates.metadata.json` for full dataset documentation.

## Domain Clustering

Systems are automatically classified into 5 clusters:

| Cluster | β_mean±SD | Φ^(n/3) Attractor | Color |
|---------|-----------|-------------------|-------|
| Informational | 4.5±0.9 | Φ³ ≈ 4.24 | Blue |
| Geophysical | 4.6±0.8 | Φ³ ≈ 4.24 | Orange |
| Biological | 7.4±0.9 | Φ⁴ ≈ 6.85 | Green |
| Climate | 11.0±1.0 | Φ⁵ ≈ 11.09 | Red |
| Extreme | 13.0±1.8 | Beyond Φ⁵ | Purple |

Classification is heuristic (keyword-based). For refined clustering, edit `DOMAIN_MAP` dict in the script.

## Customization

### Modify Φ-attractor labels:

Edit `PHI_ATTRACTORS` dict:
```python
PHI_ATTRACTORS = {
    "Φ³ (Informational)": PHI**3,
    "Φ⁴ (Biological)": PHI**4,
    "Φ⁵ (Climate)": PHI**5,
    "Φ⁶ (Custom)": PHI**6,  # Add custom attractors
}
```

### Modify domain clustering:

Edit `DOMAIN_MAP` and `DOMAIN_CLUSTERS` dicts to adjust:
- Keyword-based classification
- Cluster colors
- Expected β-values

### Adjust plot styling:

Matplotlib rcParams can be configured at the top of the script.

## Integration with UTAC v2.0 Workflow

This script is part of the UTAC v2.0 validation pipeline:

```
data/derived/beta_estimates.csv
    ↓
scripts/visualize_beta_distribution.py
    ↓
figures/utac_v2/*.svg
    ↓
paper/figures/ (for manuscript)
docs/utac_v2_synthesis.md (inline references)
```

## Citation

If you use these visualizations in publications, please cite:

```bibtex
@software{utac_v2_2025,
  author = {Römer, Johann B. and Multi-AI-Team},
  title = {UTAC v2.0 Multi-Attractor Framework},
  year = {2025},
  doi = {10.5281/zenodo.14201969},
  url = {https://github.com/GenesisAeon/Feldtheorie}
}
```

## Related Documentation

- [UTAC v2.0 Synthesis](../docs/utac_v2_synthesis.md) - Theoretical framework
- [Data Index](../data/data_index.md) - Dataset catalog
- [Beta Estimates Metadata](../data/derived/beta_estimates.metadata.json) - Full data documentation

## Troubleshooting

### "ModuleNotFoundError: No module named 'matplotlib'"

Install dependencies:
```bash
pip install -r scripts/requirements_visualization.txt
```

### "FileNotFoundError: data/derived/beta_estimates.csv"

Ensure you're running from the repository root:
```bash
cd /path/to/Feldtheorie
python scripts/visualize_beta_distribution.py
```

Or specify full path:
```bash
python scripts/visualize_beta_distribution.py --input /full/path/to/beta_estimates.csv
```

### Empty or incorrect plots

- Check that `beta_estimates.csv` has valid data
- Verify domain names match `DOMAIN_MAP` keywords
- Inspect script output for warnings

## Future Enhancements

- [ ] Interactive plots with plotly
- [ ] Animation of β-clustering convergence
- [ ] 3D visualization (β, R², ΔAIC space)
- [ ] Integration with Sigillin mandala visualization

---

**Status:** ✅ Production-ready
**Tested with:** Python 3.11, matplotlib 3.7, seaborn 0.12
**Last updated:** 2025-11-18
