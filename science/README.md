# UTAC Framework - Scientific Track

**Universal Threshold Activation-Coupling (UTAC) Framework**

This directory contains all **scientific** components of the UTAC project: models, data, analyses, tests, and documentation focused on empirical research and mathematical foundations.

---

## 🎯 Quick Navigation

### For Scientists & Researchers

- **[Scientific Summary](docs/SUMMARY.md)** - Concise overview without metaphors (start here!)
- **[User Guide](docs/USER_GUIDE.md)** - Practical workflows for using UTAC
- **[Methods Documentation](docs/METHODS.md)** - Statistical methods & theory
- **[Performance Guide](docs/PERFORMANCE_GUIDE.md)** - Profiling & optimization
- **[Glossary](docs/GLOSSARY.md)** - Technical terminology (DE/EN)

### For Developers

- **[Tests](tests/)** - 567 passing tests, ~30% coverage
- **[CLI Tools](cli/)** - Unified `utac` command-line interface
- **[Scripts](scripts/)** - Reproduction & analysis scripts

---

## 📂 Directory Structure

```
science/
├── models/          → Core mathematical models (logistic threshold, solvers)
├── analysis/        → Analysis pipelines (resonance fit, meta-regression)
├── data/            → 78 datasets across 5 domains (AI, climate, biology, ...)
├── tests/           → Pytest test suite (567 tests)
├── benchmarks/      → Performance benchmarks
├── scripts/         → Reproduction & utility scripts
├── cli/             → Unified CLI (utac)
└── docs/            → Scientific documentation hub
    ├── SUMMARY.md            ← Scientific summary
    ├── USER_GUIDE.md         ← User guide
    ├── METHODS.md            ← Statistical methods
    ├── PERFORMANCE_GUIDE.md  ← Performance & profiling
    └── GLOSSARY.md           ← Technical glossary
```

---

## 🚀 Quick Start

### Installation

```bash
cd /path/to/Feldtheorie
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Your First Analysis

```bash
# Fit logistic threshold to LLM emergence data
python scripts/reproduce_beta.py \
  --csv data/ai/wei_emergent_abilities.csv \
  --out results/wei_beta.json

# View results
cat results/wei_beta.json
```

Expected output: `β ≈ 3.47, Θ ≈ 0.52, R² ≈ 0.92, ΔAIC ≈ 18.3`

### Run Tests

```bash
pytest tests/ -v
```

---

## 📊 Core Concept

UTAC models phase transitions across diverse domains using a **logistic threshold function**:

```
σ(R) = L / (1 + exp(-β(R - Θ)))
```

**Parameters:**
- **R**: Control parameter (resource, scale, stress)
- **Θ**: Critical threshold (inflection point)
- **β**: Steepness parameter (transition sharpness, **domain-specific**)
- **L**: Asymptotic limit (typically 1)

**Key Finding:** β is **NOT universal** but varies by domain:
- **Information Systems:** β ≈ 4.5 ± 0.9
- **Biology:** β ≈ 7.4 ± 0.9
- **Climate:** β ≈ 11.0 ± 1.0
- **Neurodegeneration:** β ≈ 13.0 ± 1.8

---

## 📖 Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [SUMMARY.md](docs/SUMMARY.md) | Scientific overview | Scientists, reviewers |
| [USER_GUIDE.md](docs/USER_GUIDE.md) | Practical workflows | Researchers using UTAC |
| [METHODS.md](docs/METHODS.md) | Statistical methods | Methodologists |
| [PERFORMANCE_GUIDE.md](docs/PERFORMANCE_GUIDE.md) | Optimization | Developers |
| [GLOSSARY.md](docs/GLOSSARY.md) | Terminology | All audiences |

---

## 🔬 Empirical Results

- **78 systems** analyzed across 5 domains
- **ANOVA:** F(4,73) = 185.3, p < 10⁻²⁰, η² = 0.91
- **Model comparison:** Logistic ΔAIC > 10 vs. linear/power-law in 82% of cases
- **Reproducibility:** All analyses scripted, datasets with DOI/metadata

---

## 🛠️ Tools & CLI

### Unified CLI (`utac`)

```bash
# Batch analysis
utac analyze batch -o results.json

# Fit single dataset
utac fit logistic data.csv -o fit.json

# Audit data sources
utac audit data -o audit.json --fix
```

See [CLI README](cli/README.md) for full documentation.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=analysis --cov=models --cov-report=html

# Run specific test suite
pytest tests/test_resonance_fit_pipeline.py -v
```

**Current Status:**
- 567/567 tests passing (100%)
- Coverage: ~30% (goal: >50%)

---

## 📚 Learn More

- **[Main Repository README](../README.md)** - Full project overview
- **[Narrative Track](../narrative/)** - Interpretive & philosophical context
- **[Unified Track](../unified/)** - Integration & architecture

---

## 📄 Citation

```bibtex
@software{feldtheorie_utac_2025,
  author = {GenesisAeon},
  title = {Universal Threshold Activation-Coupling (UTAC) Framework},
  year = {2025},
  version = {10.2},
  doi = {10.5281/zenodo.17974828},
  url = {https://github.com/GenesisAeon/Feldtheorie}
}
```

---

**Last Updated:** 2025-12-25
**Version:** 10.2 (Platinum Release)
**Track:** Scientific
