# 🌀 UTAC DATA HARVEST - Sprint Package

**Universal Threshold Activation Criticality - Empirical Data Collection**

---

## 🎯 Mission

Collect, validate, and integrate **75-100 high-quality datasets** across multiple scientific domains to empirically validate the UTAC theory's universality and build a robust foundation for meta-analysis.

## 📊 Current Status

**Progress:** 5/75 datasets (6.7%)  
**Deadline:** 12 days total sprint  
**Next Milestone:** 30 datasets in 3 days

Run `python3 scripts/dashboard.py` for live progress tracking.

---

## 🗂️ Repository Structure

```
utac-data-harvest/
├── data/
│   ├── raw/                    # Original CSV datasets
│   │   ├── AMOC_RAPID_26N_2004-2024.csv
│   │   ├── LLM_Emergent_Abilities_2020-2024.csv
│   │   ├── Paleoclimate_DO_Events.csv
│   │   ├── Neuro_Consciousness_Transitions.csv
│   │   └── Financial_Contagion_2008.csv
│   └── derived/                # Processed data (future)
├── sigillin/
│   └── datasets/               # Metadata trilayer (YAML+JSON+MD)
│       ├── AMOC_RAPID_26N_2004-2024/
│       ├── LLM_Emergent_Abilities_2020-2024/
│       ├── Paleoclimate_DO_Events/
│       ├── Neuro_Consciousness_Transitions/
│       └── Financial_Contagion_2008/
├── scripts/
│   ├── generate_sigillin.py   # Auto-generate Sigillin metadata
│   └── dashboard.py            # Progress tracking dashboard
├── tests/
│   └── test_data_integrity.py # Data validation suite
└── README.md                   # This file
```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd utac-data-harvest
pip install pyyaml  # Only dependency
```

### 2. Validate Existing Data

```bash
python3 tests/test_data_integrity.py --all
```

**Expected Output:**
```
✅ Passed: 5/5
❌ Failed: 0/5
```

### 3. Generate Sigillin Metadata

```bash
python3 scripts/generate_sigillin.py --all
```

**Generates:**
- `sigillin/datasets/{name}/sigillin.yaml`
- `sigillin/datasets/{name}/sigillin.json`
- `sigillin/datasets/{name}/README.md`

### 4. View Progress Dashboard

```bash
python3 scripts/dashboard.py
```

---

## 📝 CSV Data Format

All datasets must follow this schema:

### Required Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `system` | string | System name | "AMOC_RAPID_26N" |
| `domain` | string | Scientific domain | "Climate", "AI", "Neuroscience" |
| `R` | float | State parameter (distance from threshold) | 14.2 |
| `Theta` | float | Threshold value | 15.0 |
| `beta` | float | UTAC steepness parameter | 10.2 |
| `source` | string | Data source citation | "RAPID-MOCHA DOI:10.5285/..." |
| `date_collected` | date | Collection date | "2025-11-14" |

### Recommended Columns

| Column | Type | Description |
|--------|------|-------------|
| `zeta_R` | float | Memory field parameter |
| `license` | string | Data license |
| `notes` | text | Additional context |

---

## 🎯 Domain Targets

| Domain | Current | Target | Priority |
|--------|---------|--------|----------|
| **Climate / Ecosystem** | 2 | 15-20 | 🔴 HIGH |
| **AI / LLM** | 1 | 10-15 | 🔴 HIGH |
| **Neuroscience** | 1 | 10-15 | 🟡 MEDIUM |
| **Biology / Micro** | 0 | 10-15 | 🟡 MEDIUM |
| **Economics / Social** | 1 | 10-15 | 🟢 LOW |
| **Astrophysics / Cosmos** | 0 | 5-10 | 🟢 LOW |

---

## 🔬 Current Datasets

### 1. **AMOC Collapse** (Climate)
- **Source:** RAPID-MOCHA-WBTS Array
- **β:** 10.2 (High-β thermodynamic)
- **Rows:** 8 (2004-2024)
- **Status:** ✅ Validated

### 2. **LLM Emergent Abilities** (AI)
- **Source:** Wei et al. (2022), OpenAI/DeepMind papers
- **β:** 4.18 (Informational)
- **Rows:** 10 (GPT-2 → PaLM 540B)
- **Status:** ✅ Validated

### 3. **Paleoclimate D-O Events** (Climate)
- **Source:** NGRIP Ice Core, Rasmussen et al. (2014)
- **β:** 12.8 (Extreme high-β)
- **Rows:** 7 (Last 80ka)
- **Status:** ✅ Validated

### 4. **Consciousness Transitions** (Neuroscience)
- **Source:** Massimini et al. (2005), Casali et al. (2013)
- **β:** 6.5 (Electrochemical)
- **Rows:** 8 (Wake/Sleep/Anesthesia)
- **Status:** ✅ Validated

### 5. **Financial Contagion 2008** (Economics)
- **Source:** Haldane & May (2011), Billio et al. (2012)
- **β:** 4.9 (Network contagion)
- **Rows:** 7 (Bear Stearns → Trough)
- **Status:** ✅ Validated

---

## 🛠️ Tools & Scripts

### Data Integrity Validator

**Tests:**
- ✅ Required columns present
- ✅ No missing values
- ✅ Correct data types
- ✅ UTAC parameter consistency
- ⚠️ β-range warnings

**Usage:**
```bash
# Validate single file
python3 tests/test_data_integrity.py data/raw/AMOC_RAPID_26N_2004-2024.csv

# Validate all files
python3 tests/test_data_integrity.py --all
```

### Sigillin Generator

**Generates:**
- YAML (machine-readable metadata)
- JSON (API-friendly format)
- Markdown (human-readable docs)

**Features:**
- Auto-detect UTAC type from β-value
- Calculate CREP metrics
- Generate domain-appropriate symbols

**Usage:**
```bash
# Generate for single file
python3 scripts/generate_sigillin.py --file data/raw/AMOC_RAPID_26N_2004-2024.csv

# Generate for all files
python3 scripts/generate_sigillin.py --all
```

### Progress Dashboard

**Shows:**
- Overall progress (5/75)
- Domain breakdown
- UTAC type distribution
- β-parameter statistics
- Next milestones

**Usage:**
```bash
python3 scripts/dashboard.py
```

---

## 📅 Sprint Timeline

### **Week 1: Foundation** (Days 1-7)

| Day | Milestone | Datasets | Responsible |
|-----|-----------|----------|-------------|
| 1-3 | First 30 datasets | +25 | Johann + Agent |
| 4-7 | Next 30 datasets | +30 | Agent |

### **Week 2: Completion** (Days 8-12)

| Day | Milestone | Datasets | Responsible |
|-----|-----------|----------|-------------|
| 8-10 | Final 15-40 datasets | +15-40 | Johann |
| 11 | Quality validation | All | Johann |
| 12 | Meta-analysis ready | All | Johann + AI |

---

## 🔗 Key Data Sources

### Climate & Ecosystem
- [PREDICT (ESA CCI)](https://predict-h2020.eu/) - Climate resilience datasets
- [TiPES](https://www.tipes.dk/) - Tipping points in Earth system
- [RAPID Array](https://rapid.ac.uk/) - AMOC measurements
- [NOAA Coral Reef Watch](https://coralreefwatch.noaa.gov/) - Bleaching data

### AI & LLM
- [Wei et al. (2022)](https://arxiv.org/abs/2206.07682) - Emergent abilities
- [OpenAI Scaling Laws](https://arxiv.org/abs/2001.08361) - GPT-3 paper
- [Chinchilla Paper](https://arxiv.org/abs/2203.15556) - Optimal scaling

### Neuroscience
- [OpenNeuro](https://openneuro.org/) - Public EEG/fMRI datasets
- Consciousness studies (Massimini, Tononi, Koch)

### Economics
- Open finance APIs, historical crisis data
- Network contagion models (Haldane, May, Billio)

### Astrophysics
- NASA/ESA public datasets
- QPO databases, space weather events

---

## ✅ Quality Checklist

For each new dataset:

- [ ] CSV follows required schema
- [ ] All required columns present
- [ ] β-parameter calculated/validated
- [ ] Source properly cited
- [ ] License information included
- [ ] Passed integrity validation
- [ ] Sigillin metadata generated
- [ ] Added to dashboard tracking

---

## 🤝 Contribution Guidelines

1. **Add New Dataset:**
   ```bash
   # 1. Place CSV in data/raw/
   # 2. Validate
   python3 tests/test_data_integrity.py data/raw/your_dataset.csv
   # 3. Generate Sigillin
   python3 scripts/generate_sigillin.py --file data/raw/your_dataset.csv
   # 4. Update dashboard
   python3 scripts/dashboard.py
   ```

2. **Commit Message Format:**
   ```
   feat: Add {dataset_name} ({domain}, β={value}, n={rows})
   ```

3. **Branch Strategy:**
   - `main` - Stable, validated datasets
   - `data-harvest` - Active collection
   - Feature branches for major additions

---

## 📊 Success Criteria

**Minimum Goal (75 datasets):**
- ✅ 15+ Climate datasets
- ✅ 10+ AI/LLM datasets
- ✅ 10+ Neuroscience datasets
- ✅ 10+ Biology datasets
- ✅ 10+ Economics datasets
- ✅ 5+ Astrophysics datasets
- ✅ All validated
- ✅ Full Sigillin metadata
- ✅ β-range coverage: 2.5 → 16.3

**Stretch Goal (100 datasets):**
- Same distribution + 25 more across all domains

---

## 🎉 What's Next?

After reaching 75-100 datasets:

1. **Meta-Analysis** - Aggregate β-distribution analysis
2. **UTAC v2.0 Publication** - Empirical validation paper
3. **Predictive Modeling** - Train ML models on UTAC parameters
4. **Real-Time Monitoring** - Deploy systems for high-β climate tipping points
5. **Scientific Outreach** - Nature/Science submission

---

## 📞 Contact

**Project Lead:** Johann Römer  
**Repository:** [GitHub - TBD]  
**Related:** [UTAC v1.0](https://doi.org/10.5281/zenodo.17472834)

---

*Last Updated: 2025-11-14*  
*Status: 🟢 Active Sprint*  
*Progress: 5/75 (6.7%)*
