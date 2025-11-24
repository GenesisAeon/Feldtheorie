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

## 8. CREP Stability Indices for Implosive Fields (Type-6)

**NEW in v1.2**: Type-6 Implosive Origin Fields require specialized metrics
that capture negative coupling (ζ<0), cubic-root jump dynamics, and Φ^(1/3)
scaling adherence.

### 8.1 CREP Framework Extension

The **CREP** (Coherence, Resonance, Emergence, Persistence) indices are extended
for Type-6 systems with two additional dimensions:

- **Implosion Factor (I)**: Measures negative coupling strength |ζ|
- **Proximity Risk (P)**: Quantifies R/Θ nearness to cubic-root jump zone

**Extended CREP-IP Scores**: \((C, R, E, P, I, P_{\text{risk}})\)

### 8.2 Coherence Index (C) for Type-6

**Definition**: Consistency of inverted sigmoid response across observations.

**Formula**:
```
C_type6 = 1 - (RMSE_inv / σ_data)
```

Where:
- **RMSE_inv**: Root mean squared error of inverted sigmoid fit σ(-β(R-Θ))
- **σ_data**: Standard deviation of observed data

**Interpretation**:
- **C > 0.85**: Highly coherent implosive dynamics
- **C = 0.70-0.85**: Moderate coherence (noise present)
- **C < 0.70**: Poor fit; system may not be Type-6

**Example**:
- Urban heat nocturnal retention: C = 0.92 (highly coherent)
- Bacterial lag phase: C = 0.78 (moderate coherence)

### 8.3 Resonance Index (R) for Type-6

**Definition**: Alignment with Φ^(1/3) discrete ladder.

**Formula**:
```
R_type6 = 1 - |β_obs - β_nearest| / β_nearest
```

Where:
- **β_obs**: Observed steepness parameter
- **β_nearest**: Nearest Φ^(1/3) ladder step (β_n = Φ^(n/3), n=0..9)

**Interpretation**:
- **R > 0.90**: Strong Φ^(1/3) resonance (deviation < 10%)
- **R = 0.80-0.90**: Moderate resonance
- **R < 0.80**: Weak resonance; may be Type-6 cubic-root jump regime

**Example**:
- LLM emergence: β = 4.21, nearest = 4.236 (Φ³) → R = 0.994 (99.4% resonance)
- Bacterial lag: β = 1.14, nearest = 1.174 (Φ^(1/3)) → R = 0.971 (97.1%)
- Urban heat: β = 16.3, nearest = 4.236 → R = 0.740 (cubic-root jump, not ladder)

### 8.4 Emergence Index (E) for Type-6

**Definition**: Rate of implosive unfolding (deactivation as R increases).

**Formula**:
```
E_type6 = ∫_{R_min}^{R_max} |dΨ_inv/dR| dR
```

Where:
- **Ψ_inv(R)**: Inverted sigmoid activation σ(-β(R-Θ))
- **dΨ_inv/dR**: Rate of deactivation (negative for Type-6)

**Interpretation**:
- **E > 2.0**: Rapid implosive unfolding (sharp transition)
- **E = 1.0-2.0**: Moderate unfolding
- **E < 1.0**: Slow unfolding (gradual transition)

**Example**:
- Urban heat (β=16.3): E = 3.85 (extremely rapid collapse)
- AMOC (β=4.5): E = 1.82 (moderate)
- Bacterial lag (β=1.14): E = 0.68 (slow unfolding)

### 8.5 Persistence Index (P) for Type-6

**Definition**: Memory retention through implosive transition (hysteresis).

**Formula**:
```
P_type6 = Area(Hysteresis Loop) / Area(No-Hysteresis Reference)
```

Where hysteresis loop is measured by comparing forward (R increasing) and
backward (R decreasing) transitions.

**Interpretation**:
- **P > 0.30**: Strong hysteresis (irreversible implosion)
- **P = 0.10-0.30**: Moderate hysteresis
- **P < 0.10**: Weak hysteresis (reversible)

**Example**:
- Urban heat: P = 0.45 (strong hysteresis; heat island persists after trigger)
- Thermohaline collapse: P = 0.62 (very strong; freshwater remains)
- Bacterial lag: P = 0.08 (weak; can re-enter lag phase)

### 8.6 Implosion Factor (I) - NEW

**Definition**: Strength of negative coupling |ζ|.

**Formula**:
```
I_type6 = |ζ| / (1 + |ζ|)
```

Where:
- **ζ < 0**: Negative coupling strength (inward-pulling)
- Normalization ensures I ∈ [0, 1]

**Interpretation**:
- **I > 0.50**: Strong implosive coupling (ζ < -1)
- **I = 0.30-0.50**: Moderate implosive coupling
- **I < 0.30**: Weak implosive coupling

**Example**:
- Urban heat: ζ = -0.42 → I = 0.296 (moderate)
- Systemic debt cascade: ζ = -0.55 → I = 0.355 (moderate-strong)
- Bacterial lag: ζ = -0.15 → I = 0.130 (weak)

### 8.7 Proximity Risk (P_risk) - NEW

**Definition**: Nearness to cubic-root jump threshold.

**Formula**:
```
P_risk = max(0, (R/Θ - 0.90) / 0.10)
```

Where:
- **R/Θ < 0.90**: No risk (P_risk = 0)
- **R/Θ = 0.90-1.00**: Linear escalation to P_risk = 1
- **R/Θ > 1.00**: Maximum risk (P_risk = 1)

**Interpretation**:
- **P_risk > 0.80**: CRITICAL (R/Θ > 0.98, cubic-root jump imminent)
- **P_risk = 0.50-0.80**: HIGH (R/Θ = 0.95-0.98, close monitoring required)
- **P_risk = 0.20-0.50**: MODERATE (R/Θ = 0.92-0.95, early warning active)
- **P_risk < 0.20**: LOW (R/Θ < 0.92, system stable)

**Example**:
- Urban heat (August 2003): R/Θ = 0.98 → P_risk = 0.80 (CRITICAL)
- AMOC (current): R/Θ = 0.87 → P_risk = 0.00 (LOW)
- Bacterial lag (mid-phase): R/Θ = 0.92 → P_risk = 0.20 (MODERATE)

### 8.8 Combined CREP-IP Scoring

**Full Type-6 Signature**: (C, R, E, P, I, P_risk)

**Example Systems**:

| System | C | R | E | P | I | P_risk | Status |
|--------|---|---|---|---|---|--------|--------|
| Urban Heat (2003) | 0.92 | 0.74 | 3.85 | 0.45 | 0.30 | 0.80 | CRITICAL |
| Systemic Debt (2008) | 0.88 | 0.68 | 4.12 | 0.62 | 0.36 | 0.90 | CATASTROPHIC |
| Bacterial Lag | 0.78 | 0.97 | 0.68 | 0.08 | 0.13 | 0.00 | STABLE |
| LLM Emergence (GPT-4) | 0.91 | 0.99 | 1.82 | 0.18 | 0.22 | 0.15 | MODERATE |
| AMOC (2024) | 0.86 | 0.95 | 1.65 | 0.35 | 0.18 | 0.00 | STABLE |

### 8.9 Early Warning Thresholds

**Alert Levels Based on CREP-IP**:

**GREEN** (System Stable):
- P_risk < 0.20
- R > 0.85 (good Φ^(1/3) alignment)
- C > 0.75 (coherent dynamics)

**YELLOW** (Monitoring Required):
- P_risk = 0.20-0.50
- E > 2.5 (rapid unfolding potential)
- I > 0.30 (moderate implosive coupling)

**ORANGE** (Intervention Recommended):
- P_risk = 0.50-0.80
- E > 3.0 AND I > 0.35
- P > 0.40 (strong hysteresis, hard to reverse)

**RED** (Cubic-Root Jump Imminent):
- P_risk > 0.80 (R/Θ > 0.98)
- E > 3.5 OR β_obs > 12
- Requires emergency intervention within hours/days

### 8.10 CREP-IP Reporting Template

When reporting Type-6 systems, include:

```yaml
system_name: "Urban Heat Island - Paris August 2003"
type: Type-6 Implosive
crep_ip_scores:
  coherence: 0.92
  resonance: 0.74
  emergence: 3.85
  persistence: 0.45
  implosion_factor: 0.30
  proximity_risk: 0.80
alert_level: RED
beta_observed: 16.3
beta_nearest: 4.236
zeta: -0.42
r_over_theta: 0.98
delta_aic: 14.2
confidence_interval: [15.2, 17.4]
falsification_status: "Validated (n=56 city-seasons)"
```

### 8.11 Validation Criteria for Type-6 Classification

A system is classified as Type-6 if:

1. **Inverted sigmoid fit**: σ(-β(R-Θ)) preferred over σ(+β(R-Θ)) with ΔAIC ≥ 5
2. **Negative coupling**: ζ < 0 (I > 0.10)
3. **CREP-IP coherence**: C > 0.70
4. **Φ^(1/3) resonance OR cubic-root jump**: R > 0.80 OR (R < 0.80 AND β > 10 AND P_risk > 0.50)

**Falsification Conditions**:
- ΔAIC < 5 for inverted sigmoid
- ζ ≥ 0 (positive or zero coupling)
- C < 0.60 (poor coherence)
- Cubic-root exponent p ≠ 1/3 (95% CI excludes 0.33)

### 8.12 References

**Type-6 Theory**:
- `docs/utac_type6_implosive_origin_theory.md`
- `docs/field_type_classification_v1.2.md`
- `docs/utac_type6_falsification_plan.md`

**Implementation**:
- `models/utac_type6_implosive.py`
- `analysis/crep_metrics.py` (extended for Type-6)
- `scripts/analysis/crep_metrics.py`

**Data**:
- `data/implosion/extreme_beta_catalog.csv`
- `data/derived/beta_estimates.csv` (includes Type-6 systems)
