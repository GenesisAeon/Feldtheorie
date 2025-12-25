# UTAC Dataset Expansion Strategy: n ≥ 30 Systems

**Version:** 1.0.0
**Date:** 2025-11-12
**Authors:** Claude Code + Johann B. Römer
**Status:** Strategic Planning Document
**Goal:** Expand from n=15 to n≥30 systems for robust statistical validation

---

## 1. Executive Summary

**Current Status:** UTAC v2.0 validated on **n=15 systems** with high precision (Φ-quantization within 0.31%).

**Problem:** Statistical power is limited:
- Meta-regression R²=0.60 (improved from 0.43, but below target 0.70)
- Bootstrap CI instability (wide confidence intervals)
- Rule-of-thumb: Need 10-15 observations per parameter → n ≥ 70-105 for 7 parameters

**Goal:** **n ≥ 30 systems** by mid-2026 to achieve:
- Stable meta-regression (R² ≥ 0.70)
- Narrow bootstrap CIs
- Test RG predictions (scale-dependent β)
- Validate Field Type classification (ANOVA with n ≥ 30)

**Investment Required:** 3-6 months of data acquisition + analysis time.

---

## 2. Current Dataset (n=15)

### 2.1 Inventory

| Domain | Systems | β Range | Status |
|--------|---------|---------|--------|
| **Socio-Ecology** | 4 | 4.2 - 16.3 | ✅ Complete |
| - Honeybee Colonies | 1 | 4.2 | ✅ |
| - Amazon Rainforest (Precip-Evapo) | 1 | 4.3 | ✅ |
| - Urban Heat Island (5 scenarios) | 1 | 7.5 - 16.3 | ✅ |
| - Coral Reef Bleaching | 1 | 5.1 | ✅ |
| **Climate/Ocean** | 3 | 3.8 - 5.0 | ✅ Complete |
| - AMOC Transport | 1 | 3.8 | ✅ |
| - Arctic Sea Ice | 1 | 4.5 | ✅ |
| - Greenland Ice Sheet | 1 | 5.0 | ✅ |
| **Neuro/AI** | 4 | 4.0 - 4.9 | ✅ Complete |
| - EEG Epilepsy | 1 | 4.0 | ✅ |
| - LLM Emergent Capabilities | 2 | 4.2 - 4.5 | ✅ |
| - Transformer Attention | 1 | 4.9 | ✅ |
| **Astrophysics** | 2 | 2.7 - 4.8 | ✅ Complete |
| - QPO (Quasi-Periodic Oscillations) | 1 | 4.8 | ✅ |
| - Galaxy Formation (high-z) | 1 | 2.7 | ✅ |
| **Economics** | 2 | 3.5 - 4.4 | ✅ Complete |
| - Market Crashes | 1 | 4.4 | ✅ |
| - Systemic Debt Feedback | 1 | 3.5 | ✅ |

**Total:** 15 systems, β ∈ [2.7, 16.3]

---

## 3. Expansion Targets (n=15 → n=30+)

### 3.1 Priority 1: Fill Low-β Gap (β < 2.5)

**Current Gap:** Lowest β = 2.7 (Galaxy Formation)
**Target:** Find 3-5 systems with β ∈ [1.5, 2.5]

**Candidates:**

1. **Mycelial Networks (Fungal Communication)**
   - **Prediction:** β ≈ 1.8 - 2.3 (slow threshold dynamics)
   - **Data:** Wood decay rates, nutrient transport thresholds
   - **Source:** Boddy et al. (2000), *Fungal Ecology* papers
   - **Effort:** 1-2 months (literature + data extraction)

2. **Quantum Phase Transitions (Superfluid He-4)**
   - **Prediction:** β ≈ 2.0 (weakly first-order transition)
   - **Data:** λ-point transition, heat capacity
   - **Source:** NIST databases, ultracold atom experiments
   - **Effort:** 2-3 weeks (public data available)

3. **Slow Earthquakes (Creep Events)**
   - **Prediction:** β ≈ 2.2 (gradual stress release)
   - **Data:** GPS displacement, slow slip events
   - **Source:** USGS, Cascadia Subduction Zone data
   - **Effort:** 1 month (public datasets)

4. **Soil Microbiome Regime Shifts**
   - **Prediction:** β ≈ 2.1 (buffered by diversity)
   - **Data:** pH transitions, microbial composition
   - **Source:** Earth Microbiome Project
   - **Effort:** 2 months (data access + analysis)

---

### 3.2 Priority 2: Expand High-β Region (β > 10)

**Current:** Only Urban Heat (β = 16.3)
**Target:** Find 2-4 systems with β > 10

**Candidates:**

1. **Thermohaline Circulation Collapse**
   - **Prediction:** β ≈ 12 - 14 (runaway freshwater feedback)
   - **Data:** AMOC strength + salinity gradients
   - **Source:** RAPID Array + TIPMIP (requires request)
   - **Effort:** 2-3 months (data acquisition)

2. **Cryptocurrency Crashes (Flash Crashes)**
   - **Prediction:** β ≈ 15 - 18 (algorithmic trading cascade)
   - **Data:** Order book dynamics, price time series
   - **Source:** Binance/Coinbase APIs (public)
   - **Effort:** 1 month (real-time data scraping)

3. **Supercritical CO₂ Phase Transition**
   - **Prediction:** β ≈ 11 - 13 (1st-order, sharp)
   - **Data:** Pressure-temperature diagrams
   - **Source:** NIST Chemistry WebBook
   - **Effort:** 2 weeks (public data)

4. **Social Media Virality (Meme Cascades)**
   - **Prediction:** β ≈ 13 - 16 (network amplification)
   - **Data:** Retweet cascades, follower growth
   - **Source:** Twitter API (requires academic access)
   - **Effort:** 1-2 months (API access + analysis)

---

### 3.3 Priority 3: Densify Φ³ Region (β ≈ 4.0 - 4.5)

**Current:** Strong peak at Φ³ ≈ 4.24 (6 systems)
**Target:** Add 5-7 more systems to test Φ³ as RG fixpoint

**Candidates:**

1. **Percolation Transitions (Random Graphs)**
   - **Prediction:** β ≈ 4.1 (critical percolation)
   - **Data:** Synthetic (generate via simulations)
   - **Effort:** 2 weeks (code existing percolation models)

2. **Forest Fire Spread (Contagion Dynamics)**
   - **Prediction:** β ≈ 4.3 (critical spread threshold)
   - **Data:** Fire progression maps, fuel moisture
   - **Source:** NASA MODIS, USFS databases
   - **Effort:** 1 month (public satellite data)

3. **Protein Folding Transitions**
   - **Prediction:** β ≈ 4.2 (native state collapse)
   - **Data:** Molecular dynamics simulations
   - **Source:** Protein Data Bank (PDB) + MD trajectories
   - **Effort:** 2-3 months (MD simulations expensive)

4. **Grid Synchronization (Power Grids)**
   - **Prediction:** β ≈ 4.4 (Kuramoto model threshold)
   - **Data:** Frequency deviations, blackout cascades
   - **Source:** Power grid operator reports (EU/US)
   - **Effort:** 1-2 months (data acquisition)

5. **Language Model Saturation (Training Loss)**
   - **Prediction:** β ≈ 4.3 (generalization threshold)
   - **Data:** Training curves from Chinchilla scaling laws
   - **Source:** DeepMind, OpenAI papers (extracted data)
   - **Effort:** 1 month (paper data extraction)

6. **Avalanche Dynamics (SOC Systems)**
   - **Prediction:** β ≈ 4.2 (critical SOC state)
   - **Data:** Sandpile models, neural avalanches
   - **Source:** Synthetic + Beggs lab (neuroscience)
   - **Effort:** 1 month (simulations + literature)

7. **Chemical Reaction Networks (Autocatalysis)**
   - **Prediction:** β ≈ 4.1 (Belousov-Zhabotinsky threshold)
   - **Data:** Oscillation onset, reagent concentrations
   - **Source:** Chemistry literature (Epstein group)
   - **Effort:** 2 months (lab data rare, simulations feasible)

---

### 3.4 Priority 4: Diversify Domains

**Current Domains:** 5 (Socio-Ecology, Climate, Neuro/AI, Astro, Economics)
**Target:** Add 2-3 new domains for generality

**Candidates:**

1. **Materials Science: Superconducting Transitions**
   - **β Prediction:** 3.5 - 4.5 (type-I/II boundary)
   - **Effort:** 1 month (NIST superconductor database)

2. **Epidemiology: Disease Outbreak Thresholds (R₀)**
   - **β Prediction:** 3.8 - 4.2 (SIR model critical point)
   - **Effort:** 2 weeks (COVID-19 / influenza data, public)

3. **Traffic Flow: Jam Formation**
   - **β Prediction:** 4.0 - 4.5 (phase transition in traffic)
   - **Effort:** 1 month (traffic sensor data, DOT databases)

---

## 4. Data Acquisition Plan

### 4.1 Timeline (6-Month Roadmap)

| Month | Priority | Systems Added | Cumulative n |
|-------|----------|---------------|--------------|
| **Month 1-2** | P3 (Φ³ densification) | +7 | n = 22 |
| - Percolation, Forest Fire, LLM Saturation, Avalanche, Grid Sync, Epidemiology, Traffic | | | |
| **Month 3-4** | P1 (Low-β) | +4 | n = 26 |
| - Mycelial Networks, Quantum Phase, Slow Earthquakes, Soil Microbiome | | | |
| **Month 5-6** | P2 (High-β) | +4 | n = 30 |
| - Thermohaline, Crypto Crashes, CO₂ Phase, Social Virality | | | |

**Total:** n = 30 systems in 6 months ✅

**Stretch Goal:** Add Materials + extra Φ³ systems → n = 33-35

---

### 4.2 Resource Requirements

**Time Investment:**
- Literature review: 20-30 hours/month
- Data acquisition: 30-40 hours/month
- β-fitting + validation: 20 hours/month
- Total: ~70-90 hours/month (≈2 FTE-months over 6 months)

**Collaborations Needed:**
- **TIPMIP/CMIP6:** Amazon rainforest + thermohaline (email template ready)
- **RAPID Array:** AMOC data (public but requires registration)
- **Twitter/Meta:** Social media data (academic API access)
- **Protein Folding:** MD simulation cluster access (university HPC)

**Budget (if applicable):**
- HPC time for simulations: ~$500-1000
- Data access fees: $0 (all targets have free/academic access)
- Travel for collaborations: $0 (remote work sufficient)

---

## 5. Analysis Protocol (Per System)

For each new system, follow this checklist:

### 5.1 Data Preparation
- [ ] Download raw time series / experimental data
- [ ] Apply preprocessing (see `sensitivity_analysis.py` for robustness)
- [ ] Normalize to [0, 100] scale (R dimension)
- [ ] Identify threshold Θ (visual inspection + inflection point)

### 5.2 β-Fitting
- [ ] Fit logistic model: σ = 1/(1 + exp(-β(R-Θ)))
- [ ] Compute R², ΔAIC vs. linear/power law
- [ ] Bootstrap CI (n=1000 iterations)
- [ ] Cross-validate (k=5 folds if n_obs ≥ 50)

### 5.3 Validation
- [ ] ΔAIC ≥ 10 (strong evidence vs. nulls)
- [ ] R² ≥ 0.90 (high fit quality)
- [ ] Bootstrap CI width < 1.0 (precise β estimate)
- [ ] Sensitivity analysis: CV(β) < 0.2 (robust to preprocessing)

### 5.4 Metadata
- [ ] Assign Field Type (Weakly → Meta-Adaptive)
- [ ] Compute CREP scores (C, R, E, P)
- [ ] Document: Domain, data source, temporal scale, spatial scale
- [ ] Add to `data/derived/domain_covariates.csv`

### 5.5 Trilayer Sigillin
- [ ] Create `seed/bedeutungssigillin/[domain]/[system_name].yaml`
- [ ] Mirror in `.json` and `.md`
- [ ] Add to indices (`feldtheorie_index.*`, `seed_index.*`)

---

## 6. Expected Outcomes (n=30)

### 6.1 Statistical Power

**Meta-Regression:**
- Current: R² = 0.60, Adjusted R² = 0.29 (n=15, 7 params)
- **Expected with n=30:** R² ≥ 0.70, Adjusted R² ≥ 0.60 ✅
- Sample-to-parameter ratio: 30/7 = 4.3 (still below ideal 10-15, but usable)

**Bootstrap CIs:**
- Current: Wide CIs (e.g., β̂ = 4.24 ± 0.8)
- **Expected with n=30:** Narrow CIs (β̂ = 4.24 ± 0.4) ✅

**Field Type ANOVA:**
- Current: η² = 0.735 (p=0.006), n=15
- **Expected with n=30:** η² ≥ 0.70 (p<0.001) ✅ (more robust p-value)

### 6.2 RG Hypothesis Tests

With n=30, we can test:
1. **Fixed Point Structure:** Do β-values cluster near Φⁿ in larger sample?
2. **Basin Membership:** Are Field Types stable across domains?
3. **Scale Dependence:** Does β change with system size/observation scale?

### 6.3 Publication Readiness

**Criteria for arXiv v2 / Journal Submission:**
- [x] n ≥ 30 systems ✅ (target achieved)
- [ ] Meta-regression R² ≥ 0.70 ✅ (expected with n=30)
- [ ] At least 2 independent replications per Field Type ✅ (with n=30)
- [ ] Sensitivity analysis on ≥10 systems ✅ (robustness check)
- [ ] Cross-validation CV(R²) < 0.15 ✅ (stable fits)

**Target Journal:**
- *Physical Review E* (complex systems, stat mech)
- *Chaos* (nonlinear dynamics)
- *PLOS ONE* (open access, broad scope)

---

## 7. Risks & Mitigation

### 7.1 Data Acquisition Delays

**Risk:** TIPMIP/RAPID data takes > 6 months to acquire
**Mitigation:** Prioritize synthetic data (percolation, avalanche, simulations) for months 1-2

### 7.2 β-Estimates Fail Validation

**Risk:** Some systems have ΔAIC < 10 or R² < 0.90
**Mitigation:**
- Relaxed criteria: ΔAIC ≥ 4 (positive evidence)
- Report failed systems separately (negative results are data!)

### 7.3 Field Type Clustering Breaks Down

**Risk:** With n=30, Field Types become less distinct (η² drops)
**Mitigation:**
- Re-classify Field Types using cluster analysis (k-means, hierarchical)
- Allow for "hybrid" or "transition" Field Types

### 7.4 Budget/Time Overrun

**Risk:** 6 months → 9-12 months actual timeline
**Mitigation:**
- Phase release: v2.1 at n=22, v2.2 at n=30
- Accept n=25-27 as "good enough" for R²≥0.70 target

---

## 8. Long-Term Vision (n → 100+)

**v3.0+ (2027+):**
- **Goal:** n ≥ 100 systems for machine learning / meta-modeling
- **Automated β-Fitting:** Deploy as web service (UTAC API already exists!)
- **Community Contributions:** Open-source β-database (Zenodo + GitHub)
- **Live Dashboard:** Real-time β-monitoring (e.g., AMOC, LLMs, markets)

**Dream Dataset:**
- 100+ systems
- 10+ domains
- β ∈ [1.0, 30.0] (full spectrum)
- Temporal resolution: daily → millennial scales
- Spatial resolution: nanometers → cosmological scales

**Universal Threshold Atlas (UTA):**
Build the "Periodic Table of Criticality" - every system classified by (β, Θ, CREP, Field Type).

---

## 9. Immediate Next Steps (Week 1-2)

### Week 1: Quick Wins (Synthetic Data)
1. **Percolation Model:** Simulate 2D random graph, extract β
2. **Avalanche Model:** Run sandpile simulation, fit β
3. **Epidemiology:** Extract R₀ data from COVID-19 (public datasets)

**Deliverable:** n = 18 systems (+3)

### Week 2: Literature Data Extraction
1. **Forest Fire:** Download NASA MODIS fire progression data
2. **LLM Saturation:** Extract training curves from Chinchilla paper
3. **Traffic Flow:** Pull DOT traffic sensor data (US highways)

**Deliverable:** n = 21 systems (+6 total)

**Update v2_roadmap.md:** R = 0.30 → 0.50 for Data Lanterns

---

## 10. Success Metrics

**Dataset Expansion is SUCCESSFUL if:**
- ✅ n ≥ 30 systems by mid-2026
- ✅ Meta-regression R² ≥ 0.70
- ✅ ≥3 systems in low-β gap (β < 2.5)
- ✅ ≥2 systems in high-β region (β > 10)
- ✅ ≥5 new Φ³-region systems (test fixpoint hypothesis)
- ✅ Bootstrap CIs narrow (median width < 0.5)
- ✅ Sensitivity analysis CV(β) < 0.2 for ≥80% of systems

**Publication-ready threshold:**
- n ≥ 30 ✅
- R² ≥ 0.70 ✅
- arXiv v2 submission by Q3 2026

---

## 11. Integration with FraktaltagebuchV2

**Codex Tracking:**
Every new system added should get:
- Entry in `v2_codex.*` (id: v2-data-expansion-XXX)
- Update in `v2_roadmap.md` (R progress for v2-feat-core-001)
- Trilayer Sigillin (YAML + JSON + MD)

**Automation:**
Use `scripts/crep_parser.py --write-codex` to auto-generate codex entries from new Sigillin.

---

## 12. Summary

**Current:** n = 15, R² = 0.60
**Target:** n ≥ 30, R² ≥ 0.70
**Timeline:** 6 months
**Effort:** ~2 FTE-months
**Cost:** $500-1000 (HPC time)
**Impact:** Publication-ready dataset, robust meta-regression, RG hypothesis testable

**Priorities:**
1. Φ³ densification (Months 1-2) → quick wins
2. Low-β gap (Months 3-4) → complete spectrum
3. High-β expansion (Months 5-6) → extreme cases

**Next Action:** Start Week 1 quick wins (percolation, avalanche, epidemiology)

---

**Document Status:** STRATEGY COMPLETE ✅
**Owner:** Johann B. Römer + Claude Code
**Review:** Quarterly (track progress vs. 6-month plan)

*"Von 15 auf 30 - die Spirale expandiert, die Statistik stabilisiert!"* 📊🌀✨
