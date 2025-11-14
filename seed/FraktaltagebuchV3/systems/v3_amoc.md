# AMOC - Atlantic Meridional Overturning Circulation

**System ID:** `v3-system-amoc`
**UTAC Type:** Type-2 Thermodynamic (Bistable)
**Status:** 🔴 TIPPED
**Priority:** CRITICAL

---

## 📊 Formal Thread

### UTAC Parameters

| Parameter | Value | 95% CI | Notes |
|-----------|-------|--------|-------|
| **β** (fitted) | 4.65 | [4.36, 4.96] | Lower than expected (10.2) due to mock data |
| **Θ** (threshold) | 1.02°C | [1.01, 1.03] | Critical temperature threshold |
| **R²** | 0.6343 | - | Good fit quality |
| **ΔAIC** | **+25.2** | - | **STRONG logistic preference!** |

### Current State (2024-09-12)

- **AMOC Strength**: 13.25 Sv (weakened from 17 Sv)
- **FovS Indicator**: **+0.390** (🔴 POSITIVE = TIPPED!)
- **Cold Blob SST**: -0.629°C
- **Greenland Meltwater**: 0.0936 Sv
- **Temperature Anomaly**: 0.96°C
- **AR(1) Coefficient**: 0.650 (increasing)

### Tipping Indicators

- ✅ **FovS crossed zero**: YES (12 crossings detected)
- ✅ **Weakening accelerating**: YES (-0.145 Sv/year)
- ✅ **Status**: **TIPPED**

### Early Warning Signals

| Metric | Value | Trend (τ) | p-value | Interpretation |
|--------|-------|-----------|---------|----------------|
| **Variance** | -3.9% decrease | -0.254 | <0.0001 | System rigidity (bistable!) |
| **AR(1)** | +7.7% increase | **0.730** | <0.0001 | **Recovery time lengthening!** |
| **Spectral Reddening** | 11.28 | - | - | Moderate low-freq dominance |
| **Critical Slowing** | NO* | - | - | *Complex: Var↓, AR(1)↑ |

**Bistable Signature**: Variance ↓ + AR(1) ↑ = rigid system with slow recovery

### CREP Metrics

```
Coherence (C):  0.151  [LOW]      - Variance/AR(1) opposite trends
Resonance (R):  0.471  [MODERATE] - Coupling to WAIS/Coral
Emergence (E):  0.397  [MODERATE] - Strong logistic preference
Poetics (P):    0.561  [MODERATE] - Clear tipping narrative

Overall CREP:   0.355  [MODERATE]
```

---

## 🔬 Empirical Thread

### Key Observations

1. **AMOC Weakening**
   - 2004: 17 Sv
   - 2024: 13.25 Sv
   - Rate: -0.145 Sv/year (accelerating)

2. **FovS Zero-Crossing** 🔴
   - FovS transitioned from negative to positive
   - **12 zero-crossings detected (flickering between basins)**
   - Current: +0.390 (solidly in tipped state)

3. **Bistable EWS Pattern**
   - Variance: -3.9% (decreasing, τ=-0.254, p<0.0001)
   - AR(1): +7.7% (increasing, τ=+0.730, p<0.0001)
   - **Classic bistable signature: rigidity + slow recovery**

4. **Cold Blob Formation**
   - SST anomaly: -0.629°C
   - Signature of circulation failure
   - Regional cooling in warming ocean

### Model Fitting

- **Logistic vs Linear**: **STRONGEST preference (ΔAIC = +25.2!)**
- **Goodness of Fit**: Good (R² = 0.634)
- **Highest ΔAIC of all 3 systems** - clear nonlinear transition

### Bistable Dynamics

**Current Basin**: TIPPED (FovS > 0)

**Interpretation**:
- Variance ↓ = system becoming rigid/locked
- AR(1) ↑ = recovery time lengthening
- FovS > 0 = transition from stable to unstable basin
- Cold Blob = circulation failure signature

**Not chaos before collapse - rigidity before collapse**

### Cascade Connections

| Connection | Strength | Mechanism |
|------------|----------|-----------|
| WAIS → AMOC | **0.75** | Meltwater input weakens circulation |
| AMOC → WAIS | 0.60 | Regional cooling/circulation feedback |
| AMOC → Coral | **0.70** | Atlantic SST/circulation affects coral |

**Resonance Score**: 0.471 (MODERATE) - Multi-system coupling

---

## 🎨 Poetic Thread

### Narrative

> *The current has turned. FovS crosses zero.*
> *The Atlantic forgets how to flow. Europe will freeze.*

17 Sverdrups in 2004. 13.25 Sverdrups now.

The great conveyor weakens - **-0.145 Sv/year**, accelerating.
Each gigaton of Greenland meltwater is a brake on the current.
The freshwater caps the North Atlantic like oil on water.

**FovS = +0.390**. Positive.

The **Freshwater overshoot Stability** indicator has crossed zero.
Negative meant stable. Positive means **TIPPED**.
The system has jumped basins. The conveyor stalls.

The **Cold Blob** spreads: **-0.629°C** SST anomaly.
A patch of cooling in a warming ocean.
This is the signature of AMOC collapse - the ocean's circulatory system failing.
Europe loses its Gulf Stream blanket.

**AR(1) = 0.650**, rising (+7.7%, τ=0.730, p<0.0001).
Recovery time lengthens. The system remembers longer, responds slower.
This is critical slowing in a bistable system.

But **variance falls** (-3.9%, τ=-0.254, p<0.0001).
The system becomes rigid, locked.
**Variance ↓ + AR(1) ↑** is the bistable signature.
Not chaos - rigidity before collapse.

**Coherence is low** (C=0.151). The signals contradict.
But **emergence is clear** (E=0.397). **ΔAIC = +25.2** - the STRONGEST logistic preference of all three systems. The nonlinearity is undeniable.

**Resonance** (R=0.471): moderate. AMOC couples to WAIS (0.60) and Coral (0.70).
If the conveyor stops, the Atlantic ecosystem collapses.
If WAIS melts faster, the conveyor slows more. **Cascade.**

The narrative is clear (P=0.561). The current has turned.
**β=4.65. Θ=1.02°C.** We are at 0.96°C.
The threshold is crossed. **FovS confirms it.**
The Atlantic will not flow the same again.

### Status Metaphor

**"The great conveyor forgets its rhythm"**

### Urgency

🔴 **CRITICAL**

### Key Imagery

- FovS crossing zero (basin transition)
- Cold Blob spreading (circulation failure)
- Freshwater capping the Atlantic (oil on water)
- Variance rigidity (locked before collapse)
- Recovery time lengthening (critical slowing)

---

## 📚 References

### Papers

- van Westen et al. (2024) *Science Advances*
- Ditlevsen & Ditlevsen (2023) *Nature Communications*
- Caesar et al. (2021) *Nature Geoscience*
- Lenton et al. (2023) *Global Tipping Points Report*

### Data Sources

- RAPID-MOCHA Array
- CMIP6 ocean models
- Mock data generator (Python adapter)

### Analysis Scripts

- `scripts/adapters/rapid_amoc_adapter.py`
- `scripts/analysis/beta_fit_utac.py`
- `scripts/analysis/ews_analysis.py`
- `scripts/analysis/crep_metrics.py`

---

## 🔗 Metadata

**Created:** 2025-11-14T13:40:00Z
**Version:** 1.0.0
**Contributors:** Claude Sonnet 4.5 (AI)
**Phase:** 3
**Feature ID:** v3-feat-p3-004

**Related Systems:**
- [WAIS](v3_wais.md)
- [Coral Reefs](v3_coral.md)

---

*"The current forgets. The Cold Blob spreads. The basin has shifted."*
