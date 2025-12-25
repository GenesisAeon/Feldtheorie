# Figure Specifications for "Emergent Steepness" Paper

## Figure 1: UTAC Framework Overview
**Type:** Conceptual diagram
**Layout:** 2x2 panel

**Panel A:** Sigmoid activation function S(R) = 1/(1 + e^(-β(R-Θ)))
- X-axis: System progress R
- Y-axis: Activation S(R)
- Show curves for β = 2, 4, 6, 8 (different colors)
- Highlight β = 4.2 in bold
- Annotate Θ (threshold location)
- Annotate transition width ΔR ∝ 1/β

**Panel B:** Cross-domain β distribution
- Histogram of 36 β values
- Color-coded by domain (11 categories)
- Overlay normal distribution fit (μ = 4.18, σ = 0.21)
- Vertical line at β = 4.2 (theoretical prediction)
- Show mean ± 1σ shaded region

**Panel C:** 3D parameter space (R, Θ, β)
- 3D scatter plot of systems
- Axes: R (progress), Θ (threshold), β (steepness)
- Points colored by domain
- Show Φ^(1/3) spiral trajectory
- Resonance points at Φ, Φ², Φ³ marked

**Panel D:** Universal criticality examples
- 4 mini-plots showing S(R) curves
- Examples: Black hole QPO, LLM emergence, AMOC tipping, bee swarms
- All with β ≈ 4.2 despite vastly different scales
- Shared legend emphasizing universality

---

## Figure 2: Renormalization Group Derivation
**Type:** Theoretical schematic
**Layout:** Single panel with insets

**Main Panel:** RG flow diagram
- Horizontal axis: Coupling g = J/T
- Vertical axis: β_RG(g) (beta function)
- Show flow arrows indicating coarse-graining direction
- Critical point at g_c ≈ 1 (fixed point where β_RG = 0)
- Shade stable/unstable regions

**Inset A:** Lattice coarse-graining
- Show 4x4 lattice → 2x2 under RG transformation
- Indicate block spin averaging
- Label rescaling factor b = 2

**Inset B:** β_UTAC vs. J/T plot
- Scatter: Theoretical predictions
- Line: β = 2 × (J/T) fit
- Highlight J/T = 2.1 → β = 4.2
- Error bars on predictions

**Annotations:**
- Equation: β_UTAC ≈ α(J/T) with α ≈ 2
- Connection to mean-field theory (ν = 1/2)

---

## Figure 3: Agent-Based Modeling Results
**Type:** Simulation data
**Layout:** 2x3 panel grid

**Panel A:** Lattice snapshot at criticality
- 64x64 grid visualization
- Color: Blue (inactive) to red (active)
- Show emergent clustering near threshold
- Time: t = 5000 steps (equilibrated)

**Panel B:** Magnetization vs. threshold curve
- X-axis: Threshold h
- Y-axis: Magnetization M = ⟨Σ s_i⟩/N
- Data points: 50 replicas (light gray)
- Mean curve: Bold blue line
- Sigmoid fit: Dashed red (β_emergent = 3.25)
- Vertical line at critical threshold h_c

**Panel C:** β_emergent vs. J/T phase diagram
- X-axis: J/T ratio
- Y-axis: Emergent β
- Data: Points with error bars (SEM)
- Theory: Dashed line β_theory = 2(J/T)
- Highlight J/T = 2.5 → β = 3.25 (23% deviation)
- Shade ±1 standard deviation band

**Panel D:** Finite-size scaling
- X-axis: System size N (log scale)
- Y-axis: β_emergent
- Data: N = 32², 64², 128²
- Extrapolation to N → ∞ (dashed line)
- Horizontal line: β_theory = 4.21
- Show convergence trend

**Panel E:** Equilibration dynamics
- X-axis: Monte Carlo steps
- Y-axis: Magnetization M(t)
- Multiple curves for different initial conditions
- Show convergence to equilibrium (~2000 steps)
- Highlight equilibration window (shaded)

**Panel F:** Correlation function
- X-axis: Distance r (lattice units)
- Y-axis: G(r) = ⟨s_i s_{i+r}⟩
- Show exponential decay
- Extract correlation length ξ
- Inset: Log plot confirming exponential

---

## Figure 4: Meta-Regression Analysis
**Type:** Statistical summary
**Layout:** 2x2 panel

**Panel A:** β vs. domain scatter plot
- X-axis: 11 domains (categorical)
- Y-axis: β values
- Box plots per domain showing distribution
- Overlay individual data points (jittered)
- Horizontal line: Global mean β = 4.18
- Shade ±1σ confidence band
- Annotate outliers (Climate high-β, Materials low-β)

**Panel B:** Regression diagnostics
- Predicted vs. observed β
- Diagonal line (perfect prediction)
- Data points colored by domain
- Annotate R² = 0.665, p < 0.001
- Show 95% prediction intervals (gray band)
- Label outliers

**Panel C:** Residual analysis
- X-axis: Predicted β
- Y-axis: Residuals (observed - predicted)
- Horizontal line at zero
- Check for systematic patterns (should be random)
- Overlay LOWESS smoother
- Histogram inset showing normal distribution of residuals

**Panel D:** Predictor coefficients
- Forest plot of regression coefficients
- Variables: Dimensionality, Coupling Range, Noise, Size
- Horizontal axis: Coefficient value
- Error bars: 95% CI
- Vertical line at zero (no effect)
- Stars indicating significance (* p<0.05, ** p<0.01)

---

## Figure 5: Φ^(1/3) Scaling Structure
**Type:** Geometric analysis
**Layout:** 2x2 panel

**Panel A:** β spiral trajectory
- Polar plot: θ = n, r = β_n
- Show β_n = β_0 × Φ^(n/3) spiral
- Mark resonance points: Φ, Φ², Φ³, Φ⁴
- Color gradient by complexity index n
- Overlay observed data points from 36 systems

**Panel B:** Log-log validation
- X-axis: Complexity index n
- Y-axis: β (log scale)
- Data: Observed values with error bars
- Theory: Straight line (slope = log(Φ)/3 = 0.333)
- Fitted line: Slope = 0.337 ± 0.012
- Annotate 1.2% deviation

**Panel C:** Resonance histogram
- X-axis: β values
- Y-axis: Count of systems
- Vertical lines: Φ^n harmonics (Φ, Φ², Φ³, Φ⁴, Φ⁵)
- Histogram bars colored by proximity to harmonics
- Show clustering at resonance points
- Inset: Close-up of Φ³ ≈ 4.236 peak

**Panel D:** 3D parameter space evolution
- Isometric view of (R, Θ, β) cube
- Show trajectory: β_0 → β_3 → β_6 → β_9
- After 3 steps: full Φ expansion
- Illustrate volumetric growth (Φ³ per 3 steps)
- Annotate: "Linear dimension scales as Φ^(1/3)"

---

## Figure 6: Domain-Specific Examples
**Type:** Case studies
**Layout:** 3x2 panel grid

Each panel shows one domain with:
- Main plot: S(R) curve with data points
- Fitted β value prominently displayed
- System schematic or photo (small inset)
- Annotation of physical meaning of R, S

**Panel A: Astrophysics** - Black Hole QPO
- R = accretion rate
- S = QPO amplitude
- β = 4.1 ± 0.3
- Inset: Artistic rendering of black hole

**Panel B: AI** - LLM Emergence  
- R = model scale (parameters)
- S = capability score
- β = 3.8 ± 0.4
- Inset: Neural network diagram

**Panel C: Climate** - AMOC Tipping
- R = freshwater forcing
- S = circulation strength
- β = 5.1 ± 0.6
- Inset: Atlantic Ocean currents map

**Panel D: Biology** - Honeybee Swarms
- R = scout bee count
- S = swarm commitment
- β = 4.3 ± 0.2
- Inset: Bee swarm photo

**Panel E: Psychology** - Therapeutic Gains
- R = therapy sessions
- S = symptom improvement
- β = 4.0 ± 0.5
- Inset: Progress chart

**Panel F: Materials** - Superconductivity
- R = temperature (inverted)
- S = resistance
- β = 2.5 ± 0.3
- Inset: Meissner effect diagram

---

## Figure 7: High-β Climate Systems
**Type:** Warning graphic
**Layout:** Single panel with annotations

**Main Plot:** β spectrum across climate subsystems
- X-axis: Climate system type
- Y-axis: β value (log scale)
- Bar chart colored by severity:
  - Green: β < 4 (manageable)
  - Yellow: 4 < β < 8 (concerning)
  - Orange: 8 < β < 12 (dangerous)
  - Red: β > 12 (critical)

**Systems Plotted:**
- AMOC: β = 5.1 (yellow)
- Greenland Ice Sheet: β = 6.8 (yellow)
- Amazon Rainforest: β = 14.0 (red) ⚠
- Urban Heat Islands: β = 15.6 (red) ⚠
- Permafrost Methane: β = 11.2 (orange)
- West Antarctic Ice: β = 7.5 (yellow)

**Annotations:**
- Horizontal line at β = 4.2 (typical threshold)
- Shade "cliff edge zone" β > 12
- Callout boxes explaining implications:
  - β = 15.6 → "Transition width < 5% of threshold"
  - "Minimal warning window"
  - "Cascading potential"

**Inset:** Time evolution
- Show β increasing over time for Amazon (1980-2024)
- Trend: β = 8.5 → 14.0 (worsening)

---

## Figure 8: Future Applications Roadmap
**Type:** Conceptual diagram
**Layout:** Flowchart

**Central Node:** UTAC Framework (β ≈ 4.2)

**Applications (branches):**

1. **Climate Early Warning**
   - Monitor β evolution in real-time
   - Trigger alerts when β > 8
   - Intervention targets: Reduce J or increase T

2. **AI Safety**
   - Track β during training (emergence risk)
   - Design architectures with controlled β
   - Detect unexpected capability jumps

3. **Medicine**
   - Predict therapeutic response rates
   - Personalize treatment intensity
   - Identify high-β patients (sudden improvement likely)

4. **Finance**
   - Crash prediction (β spikes)
   - Market stability indices
   - Portfolio stress testing

5. **Ecology**
   - Ecosystem resilience mapping
   - Invasive species detection
   - Restoration strategy design

6. **Social Systems**
   - Polarization monitoring
   - Conflict prediction
   - Policy intervention timing

**Connecting Arrows:** Show how UTAC theory informs each application

**Bottom Box:** "Universal Principles Enable Domain Transfer"

---

## Supplementary Figures

### Figure S1: Complete System Database
**Type:** Data table visualization
**Layout:** Scrollable table with 36 rows

Columns:
- System name
- Domain
- β value ± error
- Measurement method
- Sample size n
- R² goodness of fit
- Reference

Sortable by β value, domain, or date
Color-coded by domain

### Figure S2: ABM Parameter Sweep
**Type:** Heat map
**Layout:** 2D grid

- X-axis: Coupling J (6 values)
- Y-axis: Temperature T (5 values)  
- Color: β_emergent
- Contour lines: J/T = constant
- Overlay theoretical prediction

### Figure S3: Convergence Analysis
**Type:** Time series
**Layout:** Multi-panel

Show equilibration for 10 different initial conditions
Demonstrate robustness to starting configuration

### Figure S4: Φ Derivation Schematic
**Type:** Geometric proof
**Layout:** Step-by-step diagram

Illustrate why Φ^(1/3) emerges from 3D growth

---

## Figure Generation Notes

**Software:**
- Python: matplotlib 3.7, seaborn 0.12
- Layout: Use matplotlib GridSpec for complex arrangements
- Style: Nature journal format (sans-serif fonts, high DPI)
- Colors: Colorblind-friendly palette (Okabe-Ito)
- Size: 183mm width (full page), 300 DPI minimum

**Data Sources:**
- Figure 3: analysis/results/rg_phase2_microscopic_validation.json
- Figure 4: analysis/results/meta_regression_*.csv
- Figure 5: analysis/results/phi_scaling_validation.json
- Figure 7: data/derived/high_beta_climate_systems.csv

**Reproducibility:**
All figures generated by scripts in `scripts/figures/`
Version controlled with Git
Random seeds fixed for stochastic elements
