# UTAC Framework - Unified Track

**Universal Threshold Activation-Coupling (UTAC) Framework**

This directory provides **integration** between the scientific and narrative tracks, offering a unified entry point to the entire UTAC project.

---

## 🎯 Purpose

The UTAC project operates on **two parallel tracks**:

1. **[Scientific Track](../science/)** - Empirical research, mathematical models, statistical validation
2. **[Narrative Track](../narrative/)** - Interpretive frameworks, philosophical context, developmental story

This **Unified Track** bridges the two, providing:
- **Entry Points** - Where to start based on your interests
- **Integration Docs** - How the tracks connect
- **Overview** - Big-picture understanding
- **Navigation** - Finding what you need

---

## 🚀 Start Here

### I'm a Scientist / Researcher
**→ [Scientific Summary](SUMMARY.md)**
- Concise overview without metaphors
- Empirical results, statistical evidence
- Reproducibility instructions

**Then:**
- [User Guide](../science/docs/USER_GUIDE.md) - Practical workflows
- [Methods](../science/docs/METHODS.md) - Statistical methodology
- [Data](../science/data/) - 78 datasets across 5 domains

### I'm Interested in Philosophy / Context
**→ [Main README](README.md)**
- Full project vision
- Philosophical themes
- Integration story

**Then:**
- [Ethics](../narrative/docs/ETHICS.md) - Ethical considerations
- [Agents](../narrative/docs/AGENTS.md) - Development process
- [Seed](../narrative/seed/) - Conceptual origins

### I'm a Developer / Contributor
**→ [Architecture](ARCHITECTURE.md)**
- System design & structure
- Technical decisions
- Module organization

**Then:**
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [CLI](../science/cli/) - Command-line interface
- [Tests](../science/tests/) - Test suite

### I Want to Dive Right In
**→ [Quickstart](QUICKSTART.md)**
- 5-minute tutorial
- First analysis
- Key results

---

## 📂 Directory Structure

```
unified/
├── README.md              → Main project overview (vision + context)
├── ARCHITECTURE.md        → System design & technical structure
├── QUICKSTART.md          → 5-minute getting started guide
├── SUMMARY.md             → Scientific summary (empirical focus)
├── IMPROVEMENT_PLAN.md    → Development roadmap & progress
├── CHANGELOG.md           → Version history
└── CONTRIBUTING.md        → Contribution guidelines
```

All files are **symlinks** to the root directory, providing a single entry point for integration documents.

---

## 🔗 Track Navigation

### Scientific Track (`../science/`)
**Focus:** Falsifiable hypotheses, empirical validation, reproducibility

**Key Directories:**
- `models/` - Mathematical models (logistic threshold, solvers)
- `analysis/` - Analysis pipelines (fits, meta-regression)
- `data/` - 78 datasets with metadata
- `tests/` - 567 passing tests (~30% coverage)
- `docs/` - Scientific documentation hub

**Entry Point:** [science/README.md](../science/README.md)

### Narrative Track (`../narrative/`)
**Focus:** Philosophical context, ethical considerations, developmental story

**Key Directories:**
- `seed/` - Conceptual origins & early explorations
- `releases/` - Version narratives & reflections
- `aeon/` - Long-term visions
- `sigillin/` - Trilayer memory architecture
- `docs/` - Narrative documentation hub

**Entry Point:** [narrative/README.md](../narrative/README.md)

---

## 🧩 How the Tracks Connect

### Science → Narrative
- **Empirical findings** inspire philosophical reflection
- **Statistical evidence** grounds speculative thinking
- **Reproducible results** enable responsible interpretation

### Narrative → Science
- **Poetic thinking** generates research questions
- **Ethical frameworks** inform research design
- **Developmental history** contextualizes current state

### Bidirectional Integration
- **Sigillin System** ensures synchronization (YAML/JSON/MD)
- **Shared Glossary** maintains consistent terminology
- **Cross-references** link related concepts

---

## 📚 Core Documentation

### Integration Documents (in this directory)

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](README.md) | Full project vision | All audiences |
| [SUMMARY.md](SUMMARY.md) | Scientific summary | Scientists, reviewers |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design | Developers |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute tutorial | New users |
| [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) | Development roadmap | Contributors |
| [CHANGELOG.md](CHANGELOG.md) | Version history | All audiences |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guide | Contributors |

### Track-Specific Documentation

**Scientific:**
- [User Guide](../science/docs/USER_GUIDE.md)
- [Methods](../science/docs/METHODS.md)
- [Performance Guide](../science/docs/PERFORMANCE_GUIDE.md)

**Narrative:**
- [Agents Charter](../narrative/docs/AGENTS.md)
- [Ethics](../narrative/docs/ETHICS.md)
- [Governance Report](../narrative/docs/GOVERNANCE_REPORT.md)

---

## 🎯 Key Concepts

### The UTAC Model

**Mathematical Form:**
```
σ(R) = L / (1 + exp(-β(R - Θ)))
```

**Parameters:**
- **R**: Control parameter (resource, scale, stress)
- **Θ**: Critical threshold (inflection point)
- **β**: Steepness parameter (domain-specific!)
- **L**: Asymptotic limit (typically 1)

**Key Finding:** β varies by domain (Information: ~4.5, Biology: ~7.4, Climate: ~11.0)

### Trilayer System (Sigillin)

Every central concept exists in **three synchronized forms**:
1. **YAML** - Agent-readable configuration
2. **JSON** - Machine-parsable data
3. **Markdown** - Human-readable narrative

This ensures both scientific rigor (structured data) and interpretive richness (narrative context).

---

## 🌍 Project Philosophy

### Separation of Concerns
- **Scientific claims** remain falsifiable and empirically grounded
- **Narrative interpretations** are clearly labeled as such
- **No conflation** between evidence and speculation

### Transparency
- **All data** with DOI/metadata
- **All analyses** scripted and reproducible
- **All AI contributions** explicitly attributed

### Responsibility
- **Dual-use awareness** (e.g., climate tipping points)
- **Ethical guidelines** for threshold modeling
- **Community engagement** before high-stakes applications

---

## 📖 Version History

- **v10.2 (Platinum)** - Three-track structure (science/narrative/unified)
- **v10.0** - Comprehensive documentation overhaul
- **v9.0** - Dimensional emergence framework
- **v8.0** - Experimental protocols
- **v7.0** - Performance optimizations
- **v6.0** - MkDocs integration
- **v5.0** - 78 datasets, meta-regression
- Earlier versions: see [CHANGELOG.md](CHANGELOG.md)

---

## 🚀 Next Steps

1. **Choose your track:**
   - Scientific? → [science/README.md](../science/README.md)
   - Narrative? → [narrative/README.md](../narrative/README.md)

2. **Pick a starting point:**
   - Quick analysis? → [QUICKSTART.md](QUICKSTART.md)
   - Deep dive? → [SUMMARY.md](SUMMARY.md) + [README.md](README.md)

3. **Contribute:**
   - Found an issue? → [GitHub Issues](https://github.com/GenesisAeon/Feldtheorie/issues)
   - Want to help? → [CONTRIBUTING.md](CONTRIBUTING.md)

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
**Track:** Unified Integration
