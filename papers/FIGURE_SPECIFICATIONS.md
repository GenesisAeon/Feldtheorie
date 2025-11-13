# 📊 Figure Specifications for "Emergent Steepness"

Complete specifications for all figures in the paper. These should be generated programmatically via `scripts/generate_all_figures.py`.

---

## Figure 1: UTAC Overview (4 Panels)

**File:** `figures/figure1_utac_overview.pdf`
**Size:** 180mm × 180mm (2×2 grid)
**Format:** PDF, 300 DPI

### Panel A: Sigmoid Response Curve
- **X-axis:** $R$ (Resource/Activation) [0, 20]
- **Y-axis:** $\sigma(R)$ [0, 1]
- **Curves:** 3 sigmoids with $\beta \in \{2, 4.2, 8\}$, $\Theta = 10$
- **Colors:** Blue (#1f77b4), Orange (#ff7f0e), Green (#2ca02c)
- **Annotations:** Threshold line at $R=10$ (dashed gray)
- **Legend:** Top left, $\beta$ values labeled

### Panel B: $\beta$ Distribution Across Systems
- **Type:** Histogram + KDE
- **X-axis:** $\beta$ [0, 20]
- **Y-axis:** Count
- **Data:** $n=36$ systems
- **Bins:** 15 bins
- **Overlay:** Gaussian KDE (smoothed), peak at $\beta \approx 4.2$
- **Annotations:** Mean $\pm$ SD, median line

### Panel C: Field Type Classification
- **Type:** Scatter plot
- **X-axis:** $\log(J/T)$ [-1, 2]
- **Y-axis:** $\beta$ [0, 20]
- **Points:** $n=36$ systems, colored by field type:
  - Weakly Coupled: Blue
  - Strongly Coupled: Orange
  - High-Dimensional: Green
  - Physically Triggered: Red
  - Meta-Adaptive: Purple
- **Fit line:** $\beta = 2(J/T)$ (dashed black)
- **CI band:** 95% confidence (light gray)

### Panel D: Domain Distribution (Pie Chart)
- **Type:** Pie chart
- **Categories:** 11 domains (AI/ML, Climate, Neuro, Astro, Bio, etc.)
- **Labels:** Percentages + counts
- **Colors:** Categorical palette (tab10)

---

## Figure 2: [Reserved for later]

---

## Figure 3: ABM Results (3 Panels)

**File:** `figures/figure3_abm_results.pdf`
**Size:** 180mm × 120mm (1×3 grid)
**Format:** PDF, 300 DPI

### Panel A: $\beta$ vs $J/T$
- **Type:** Scatter with error bars
- **X-axis:** $J/T$ [0, 2.5]
- **Y-axis:** $\beta_{\text{ABM}}$ [0, 6]
- **Points:** 4 conditions ($J/T \in \{0.5, 1.0, 1.5, 2.0\}$)
- **Error bars:** 95% CI from bootstrap
- **Theory line:** $\beta = 2(J/T)$ (solid black)
- **Lattice sizes:** Different markers (circle, square, triangle for $N=64, 128, 256$)

### Panel B: Time Series (Example)
- **Type:** Line plot
- **X-axis:** Time [0, 5000]
- **Y-axis (left):** $R(t)$ [0, 15]
- **Y-axis (right):** response $(t)$ [0, 1]
- **Curves:** $R(t)$ (blue), response$(t)$ (orange)
- **Annotations:** Threshold $\Theta$ (horizontal dashed)

### Panel C: Finite-Size Scaling (Data Collapse)
- **Type:** Scatter plot
- **X-axis:** $(R - R_c) N^{1/\nu}$ [-5, 5]
- **Y-axis:** response $\times N^\beta$ [0, 1]
- **Points:** All lattice sizes ($N=64, 128, 256$), colored differently
- **Collapse:** All points should lie on universal curve

---

## Figure 4: Meta-Regression (2 Panels)

**File:** `figures/figure4_meta_regression.pdf`
**Size:** 180mm × 90mm (1×2 grid)
**Format:** PDF, 300 DPI

### Panel A: $\beta$ vs $\log(J/T)$ with Regression
- **Type:** Scatter + regression line
- **X-axis:** $\log(J/T)$ [-1, 2]
- **Y-axis:** $\beta$ [0, 20]
- **Points:** $n=36$ systems, colored by domain
- **Regression:** OLS fit (solid red), equation in legend
- **CI band:** 95% confidence (light red)
- **Annotations:** $R^2 = 0.665$, $p = 0.0005$

### Panel B: Residuals Diagnostic
- **Type:** QQ plot (quantile-quantile)
- **X-axis:** Theoretical quantiles
- **Y-axis:** Sample quantiles (residuals)
- **Points:** Residuals from regression
- **Reference line:** $y = x$ (dashed)
- **Purpose:** Check normality assumption

---

## Figure 5: $\Phi^{1/3}$ Scaling (2 Panels)

**File:** `figures/figure5_phi_scaling.pdf`
**Size:** 180mm × 90mm (1×2 grid)
**Format:** PDF, 300 DPI

### Panel A: Iterative Convergence to $\Phi^3$
- **Type:** Line plot with markers
- **X-axis:** Step $n$ [0, 10]
- **Y-axis:** $\beta_n$ [0, 5]
- **Curve:** $\beta_n = n \times \Phi^{1/3}$
- **Horizontal line:** $\beta_\infty = \Phi^3 = 4.2361$ (dashed)
- **Annotations:** Final value, convergence rate

### Panel B: Empirical vs Theoretical Comparison
- **Type:** Bar chart
- **X-axis:** Categories (Empirical Mean, $\Phi^3$, RG Theory)
- **Y-axis:** $\beta$ value [3.5, 4.5]
- **Bars:** 3 bars with error bars for empirical
- **Colors:** Blue (Empirical), Gold (Φ³), Green (RG)
- **Annotations:** Deviation percentages

---

## Supplementary Figures

### Figure S1: Noise Model Robustness
- **Type:** Box plots
- **X-axis:** Noise type (Gaussian, Laplace, Poisson)
- **Y-axis:** $\beta$ [0, 6]
- **Boxes:** Distribution for each noise model at $J/T = 1.0$
- **Overlay:** Individual points (jittered)

### Figure S2: Lattice Geometry Independence
- **Type:** Bar chart with error bars
- **X-axis:** Geometry (Square, Hexagonal, Random)
- **Y-axis:** $\beta$ [0, 6]
- **Purpose:** Show $<5\%$ variation

### Figure S3: Bootstrap Distributions
- **Type:** Histogram array (4 subplots)
- **Subplots:** One per $J/T$ value
- **X-axis:** $\beta$ (bootstrapped)
- **Y-axis:** Frequency
- **Purpose:** Show CI estimation quality

### Figure S4: Cross-Domain Comparison Matrix
- **Type:** Heatmap
- **Rows:** 11 domains
- **Columns:** Statistics (mean $\beta$, std, $n$, $R^2$)
- **Colors:** Viridis colormap
- **Purpose:** Domain-wise breakdown

---

## Generation Instructions

All figures should be generated by:
```bash
python scripts/generate_all_figures.py --output papers/figures/ --format pdf --dpi 300
```

**Requirements:**
- matplotlib >= 3.7
- seaborn >= 0.12
- numpy >= 1.24
- pandas >= 2.0
- scipy >= 1.10

**Style:**
- Font: Arial or Helvetica, 10pt for labels, 8pt for annotations
- Line widths: 1.5pt for data, 1pt for guides
- Color palette: Seaborn colorblind-safe
- Grid: Light gray (#cccccc), alpha=0.3

**File naming convention:**
- `figure{N}_{short_description}.pdf`
- `figureS{N}_{short_description}.pdf` (supplementary)

---

**Last Updated:** 2025-11-13
**Maintainer:** Johann Benjamin Römer
**Status:** Specifications complete, ready for implementation
