# Statistical Metrics and Methodology

This reference summarises the metrics reported across UTF analyses.  Every
result documents the logistic quartet \((R, \Theta, \beta, \zeta(R))\), compares
against null models, and quantifies uncertainty.

## 1. Logistic steepness (β)
- **Definition:** slope of the logistic response \(\sigma(\beta(R-\Theta))\).
- **Interpretation:** larger \(\beta\) implies sharper transitions.
- **Estimation:** `scipy.optimize.curve_fit` with bounded parameters (see
  `METHODS.md`).  Bootstrap resampling (1,000 iterations, seed 1337) supplies the
  95% confidence interval.

## 2. Threshold (Θ)
- **Definition:** control parameter value where \(P(R)=0.5\).
- **Reporting:** scripts store \(\Theta\) in dataset units and, when relevant,
  in normalised coordinates.
- **Interpretation:** identifies the resource or stress level at which the
  system switches regimes.

## 3. Goodness-of-fit metrics
| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **AIC** | \(n \log(\mathrm{RSS}/n) + 2k\) | Penalised likelihood; lower is better. |
| **ΔAIC** | \(\mathrm{AIC}_{\text{null}} - \mathrm{AIC}_{\text{logistic}}\) | ≥10 indicates strong support for the logistic response. |
| **BIC** | \(n \log(\mathrm{RSS}/n) + k\log n\) | Conservative penalty for model size. |
| **RMSE** | \(\sqrt{\mathrm{RSS}/n}\) | Absolute prediction error. |
| **R²** | \(1 - \mathrm{RSS}/\mathrm{TSS}\) | Fraction of variance explained. |

## 4. Null models
Analyses benchmark the logistic fit against:
- **Linear regression:** \(y = aR + b\)
- **Power law:** \(y = aR^{b}\) (log–log fit)
- **Exponential:** \(y = a\exp(bR)\)

ΔAIC and ΔBIC values are reported for each null.  Logistic fits failing the
ΔAIC ≥ 10 guard are flagged in the corresponding documentation.

## 5. Sample sizes and provenance
Metadata files enumerate observation counts, domains, and licenses.  Key
examples:

| Domain | Dataset | Observations |
|--------|---------|--------------|
| AI | `wei_emergent_abilities.csv` | 30 per task |
| Climate | `planetary_tipping_elements.csv` | 120 coupled states |
| Cognition | `working_memory_gate.csv` | 48 experimental runs |
| Ecology | `honeybee_waggle_activation.csv` | 60 colony probes |

See `data/*/*.metadata.json` for domain-specific notes.

## 6. Bootstrap procedure
1. Resample paired \((R, \text{response})\) observations with replacement.
2. Refit the logistic curve.
3. Record \(\beta\) and \(\Theta\).
4. Repeat 1,000 times; report 2.5th/97.5th percentiles.

## 7. Falsification tracking
`docs/utac_falsifiability.md` logs any dataset where \(\beta\) leaves the
\([3.6, 4.8]\) universality band or where ΔAIC falls below 10.  Contributors
must extend the table when new evidence challenges the canonical band.

## 8. Type-VI Implosive Dynamics Classification

**Type-VI** systems exhibit **implosive resonance** where \(\zeta(R) < 0\) drives
negative feedback cascades. Unlike expansive transitions (Type I-V), Type-VI
dynamics show:

- **Cubic-root jumps:** \(\Delta R \propto (R - \Theta)^{1/3}\)
- **Negative damping:** \(\zeta(R) = \zeta_0 \cdot (R - R_{\text{critical}}) < 0\)
- **Self-reinforcing collapse:** Field contracts toward singularity

### 8.1 Type-VI Detection Criteria

A system is classified as **Type-VI** if:

1. **Inverted sigmoid:** \(S(R) = 1 - \sigma(\beta(R - \Theta))\) fits better than forward sigmoid (ΔAIC ≥ 10)
2. **Negative velocity gradient:** \(\frac{dv}{dR} < 0\) where \(v = -\zeta_0 R + S(R)\)
3. **Cubic-root scaling:** Residuals fit \(|R_{\text{obs}} - R_{\text{pred}}| \propto (R - \Theta)^{1/3}\) better than linear/quadratic

### 8.2 CREP Index (Collapse-Resonance-Expansion Potential)

The **CREP index** quantifies implosive risk across three phases:

\[
\text{CREP} = \alpha_C \cdot C + \alpha_R \cdot R_{\text{resonance}} + \alpha_E \cdot E_{\text{rebound}}
\]

**Components:**

- **C (Collapse potential):** \(C = \max(0, -\zeta(R)) \cdot \beta\)
  - Measures negative damping strength
  - Higher C → stronger implosive drive

- **R_resonance (Resonance window):** \(R = \exp(-|\beta(R - \Theta)|)\)
  - Peaks at threshold \(\Theta\)
  - Measures proximity to critical transition

- **E_rebound (Expansion recovery):** \(E = \int_{\Theta}^{R_{\max}} \sigma(\beta(R - \Theta)) \, dR\)
  - Quantifies post-implosive expansion capacity
  - Higher E → system can recover from collapse

**Standard weights:** \(\alpha_C = 0.5, \alpha_R = 0.3, \alpha_E = 0.2\)

**CREP interpretation:**

| CREP Range | Classification | Risk Level | Governance |
|------------|----------------|------------|------------|
| 0.0 - 0.3 | Stable expansion | Low | Standard review |
| 0.3 - 0.6 | Transition zone | Medium | Enhanced monitoring |
| 0.6 - 0.8 | High implosive risk | High | **⚠️ Mandatory reviewer** |
| 0.8 - 1.0 | Critical collapse | Extreme | **🔴 Level 3 escalation** |

**⚠️ CREP ≥ 0.7 Safety Protocol:**
- **Mandatory Review**: See `releases/V6-Plans_etc/type6_crep_tau_star_checklist.md`
- **τ* Buffer**: τ* = 0.1·|Θ−R| minimum
- **RK4+ Integrator**: NO Euler methods
- **Provenance**: Full audit trail in `releases/V6-Plans_etc/ETHICS.md`
- **CI Gate**: Automated check via `.github/workflows/v6-governance.yml`

### 8.3 Empirical Examples

**Climate:** Arctic permafrost methane release shows Type-VI characteristics:
- \(\beta = 4.2\), \(\Theta = 2.1°\text{C}\), \(\zeta(R) < 0\) for \(R > 2.5°\text{C}\)
- CREP = 0.72 (high implosive risk)

**Finance:** Flash-crash dynamics (2010):
- Cubic-root jumps in order-book depth
- CREP = 0.85 during cascade window

**Neuroscience:** Seizure onset cascades:
- Inverted sigmoid in neuronal synchrony
- CREP = 0.78 at pre-ictal threshold

### 8.4 Simulation Requirements

Type-VI models require:
- **Safety-delay buffer** \(\tau^*\) to prevent numerical divergence (see `pipelines/fit_tau_star/`)
- **RK4 integration** (Euler methods fail for \(\zeta < 0\))
- **Meta-regression tracking** to detect \(\beta\)-drift across domains

**τ* Implementation (V6 Sprint Δ):**

The τ* safety delay is implemented in `pipelines/fit_tau_star/` with RK4-compatible functions:

```python
from pipelines.fit_tau_star import compute_tau_star, apply_safety_delay

# Compute delay for CREP>0.7 scenarios
tau_star = compute_tau_star(R=0.3, Theta=0.5, beta=4.8)  # τ* = 0.02

# Apply in RK4 loop
R_delayed = apply_safety_delay(R_next, R_prev, tau_star, dt, mode="exponential")
```

**CREP-τ* Coupling:**

Systems with CREP > 0.7 **must** use τ* delay:

```python
from pipelines.fit_tau_star import compute_zeta_risk

zeta = compute_zeta_risk(R, Theta, beta)
if zeta < 0:  # Implosive regime
    tau_star = compute_tau_star(R, Theta, beta)
    # Apply delay in integration
```

See `simulation/implosive_genesis_sim.py` and `analysis/notes/tau_star_safety_delay_integration.md` for reference implementations.

### 8.5 4D Tesseract Integration (V6.0)

**New in V6:** Type-VI dynamics are now integrated with the **4D tesseract time-slicing** framework, which models implosive spacetime genesis and photon propagation through temporal layers.

**Key features:**
- **Block Universe Structure:** 4D hypercube \([-1,1]^4\) with temporal slicing
- **Dual-Flow Geometry:**
  - Implosive spatial flow: \(\frac{dr}{d\tau} = -\alpha^{-1} \cdot r \cdot \sigma(\beta(R - \Theta))\)
  - Explosive temporal flow: Light propagates forward through timeslices
- **Entropic Wavefunction:** \(\Psi(r,\theta,\phi,t)\) couples geometric frustration to gravitation
- **Consciousness Integral:** \(I_C = \int F \cdot u \, d\tau\) tracks observer experience

**Modules:**
- `simulation/tesseract_timeslices.py`: 4D tesseract with photon propagation
- `simulation/genesis_cube.py`: Entropic wavefunction \(\Psi(r,\theta,\phi,t)\) with RK4 evolution
- `scripts/visualize_tesseract.py`: Visualization toolkit (animation, dual-view, photon paths)

**CREP Integration:**
The CREP index now includes tesseract field coupling:
\[
\text{CREP}_{\text{4D}} = \text{CREP}_{\text{base}} + \gamma \cdot \|\nabla S\|
\]
where \(\nabla S\) is the entropy gradient from the wavefunction, and \(\gamma = 0.1\) is the geometric coupling weight.

**Visualization:**
```bash
# Dual-view: 4D projection + 3D slice
python scripts/visualize_tesseract.py --mode dual-view --slice 50

# Photon paths through timeslices
python scripts/visualize_tesseract.py --mode photon-paths
```

**References:**
- `simulation/README_TESSERACT.md`: Complete documentation
- `releases/V6-Plans_etc/Zusatz_bitte_integrieren!.txt`: Theoretical foundation
- `releases/V6-Plans_etc/V6_ToDoListe.md`: Implementation roadmap
