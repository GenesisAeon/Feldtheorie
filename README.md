# Universal Threshold Field Initiative

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17472834.svg)](https://doi.org/10.5281/zenodo.17472834)
[![GitHub](https://img.shields.io/badge/GitHub-Feldtheorie-blue)](https://github.com/GenesisAeon/Feldtheorie)
[![Code License: GPLv3](https://img.shields.io/badge/Code%20License-GPLv3-blue.svg)](LICENSE)
[![Content License: CC BY-NC 4.0](https://img.shields.io/badge/Content%20License-CC%20BY--NC%204.0-orange.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-5.0.0-green.svg)](#whats-new-in-v50)
[![Tests](https://img.shields.io/badge/tests-430%2F430%20passing-brightgreen.svg)](#tests--quality)
[![Project History](https://img.shields.io/badge/📅_Project_History-2025--11--20-lightgrey.svg)](CHANGELOG.md)

## What's New in v5.0 🚀

- **Fractal Governance Engine:** Champollion & Sigillin rules are now packaged for reuse via `setup/universal_skeleton_builder.py`, with embedded charters and theory docs to keep trilayer governance intact. See [RELEASE_NOTES_v5.0.0.md](RELEASE_NOTES_v5.0.0.md).
- **Repository-as-Product Toolkit:** The Zenodo-ready bundle in `releases/v5.0.0_Zenodo_Ready/` ships manifests, upload checklists, and DOI metadata so any clone can be published without manual wiring. See [RELEASE_NOTES_v5.0.0.md](RELEASE_NOTES_v5.0.0.md).
- **Structural Isomorphism Models:** New α–Φ cosmic velocity scaling (`models/cosmic_alpha_phi.py`) and inequality-driven Ising rigidity (`models/social_rigidity_ising.py`) include Monte Carlo null ensembles and validation logs. See [RELEASE_NOTES_v5.0.0.md](RELEASE_NOTES_v5.0.0.md).
- **Hypothesis & Validation Docs:** Expanded write-ups in `docs/v5_hypothesis_isomorphism.md` and `docs/v5_validation_session_2025-11-23.md` trace assumptions, guardrails, and fit reviews for the new models. See [RELEASE_NOTES_v5.0.0.md](RELEASE_NOTES_v5.0.0.md).
- **Automation & Packaging:** `prepare_upload.py` now generates hashed manifests and source archives to lock σ(β(R-Θ)) framing to its artifacts, keeping GitHub and Zenodo synchronized. See [RELEASE_NOTES_v5.0.0.md](RELEASE_NOTES_v5.0.0.md).

## 🚀 For Developers & Researchers: Repository as Product

**Want to apply this self-organizing architecture to your own project?**

This repository isn't just a research artifact—it's a **universal template** for building self-organizing knowledge systems. The structure (Diamond Architecture + Fractal Governance + Recursive Indexing) can be applied to **any domain**:

- **Physics Research:** Track papers, simulations, datasets with emergent metrics
- **Business Analytics:** Organize KPIs, revenue models, market analyses with ROI metrics
- **Software Engineering:** Monitor code quality, test coverage, technical debt with QSTM metrics
- **Creative Projects:** Index literature, music, art with custom aesthetic metrics

> ### Getting Started
> Ready to run Feldtheorie locally? See the [QUICKSTART.md](QUICKSTART.md) for full details. The fastest path:
>
> ```bash
> python -m venv .venv
> source .venv/bin/activate  # or .venv\Scripts\activate on Windows
> pip install -r requirements.txt
> pytest  # optional smoke check
> ```

### Universal Skeleton Builder

The [`setup/`](setup/) directory contains a **production-ready builder script** that replicates the Feldtheorie architecture for arbitrary datasets:

```bash
# Create a new self-organizing repository
python setup/universal_skeleton_builder.py ~/my-new-project \
  --domain physics \
  --metrics crep \
  --verbose
```

**What you get:**
- ✅ **Diamond Architecture**: `modules/artifacts/`, `modules/context/`, `modules/navigation/`
- ✅ **Fractal Governance**: Self-similar rules that propagate through folder hierarchies
- ✅ **Metric Templates**: Choose CREP (research), ROI (business), or KPI (engineering)
- ✅ **Recursive Indexer**: Bottom-up aggregation engine (stub included, full version in this repo)
- ✅ **Tri-Layer Documentation**: YAML (machine), JSON (API), Markdown (human)

### Included Resources

| File | Purpose |
|------|---------|
| [`setup/universal_skeleton_builder.py`](setup/universal_skeleton_builder.py) | Main builder script with robust error handling |
| [`setup/THEORY_OF_STRUCTURE.md`](setup/THEORY_OF_STRUCTURE.md) | **"The Physics of Information"** — Why folders are states, not containers |
| [`setup/AGENTS_BOOTSTRAP.md`](setup/AGENTS_BOOTSTRAP.md) | Instructions for AI agents (Claude, GPT-4, AutoGPT, LangChain) |

### Theory: Why This Architecture?

Traditional file systems fail at scale because they treat folders as **containers** (arbitrary boundaries).

The UTAC approach treats folders as **states in a phase space**:

- **Emergent Order:** Structure arises from bottom-up indexing (not manual curation)
- **Entropy Minimization:** Aggregated indices compress information (reducing search uncertainty)
- **Self-Similarity:** Every subfolder mirrors the root (fractal governance)
- **Adaptive Metrics:** Top-down configuration defines what you measure (CREP, ROI, KPI, custom)

**Read the full theory:** [`setup/THEORY_OF_STRUCTURE.md`](setup/THEORY_OF_STRUCTURE.md)

### Use Cases

**Example 1: Organize 200 research papers**
```bash
python setup/universal_skeleton_builder.py ~/research-archive --domain physics --metrics crep
# Move PDFs to modules/artifacts/
# Run indexer → Get queryable index with Emergence/Resonance scores
```

**Example 2: Track quarterly business KPIs**
```bash
python setup/universal_skeleton_builder.py ~/q1-2025 --domain business --metrics roi
# Add CSV files → Indexer calculates Profit/Efficiency/Risk/Opportunity metrics
```

**Example 3: Monitor codebase health**
```bash
python setup/universal_skeleton_builder.py ~/my-app --domain engineering --metrics kpi
# Indexer tracks Quality/Safety/Testability across modules
```


**This is "repository as product."**

---

## Citation

If you cite this repository, please use [`CITATION.cff`](CITATION.cff):

> Römer, J. et al. (2025). *Universal Threshold Field Model v5.0.0: The 137-β Duality*.
> DOI: [10.5281/zenodo.17472834](https://doi.org/10.5281/zenodo.17472834)

For v5.0 specifically:
> Römer, J. et al. (2025). *Scale-Invariant Information Coupling: From Cosmic Velocities to Social Rigidity*.
> UTAC Framework v5.0. DOI: 10.5281/zenodo.17472834

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

**Key Principles:**
- Falsifiability over speculation
- Trilayer documentation (YAML/JSON/Markdown)
- Test coverage for all new models
- ΔAIC ≥ 10 evidence threshold

---

## License

- **Code:** Released under the GNU General Public License v3.0 (GPLv3, copyleft, open source).
- **Content & Data:** Released under the Creative Commons Attribution-NonCommercial 4.0 International license (CC BY-NC 4.0).
- **Commercial use:** Any commercial exploitation requires explicit permission from the authors.

You are free to share and adapt the material in line with the applicable license. Always provide attribution (see `CITATION.cff`) and respect the non-commercial clause for content and data. This dual-license model supersedes earlier CC BY 4.0 references in historical documents.

### The 137-β Duality: Structural Isomorphism Testing

**Empirical Research Program:** We test whether mathematical structures (scaling laws, phase transitions) show predictive correlations across different domains. This is an investigation of **structural isomorphism**, not mystical unity.

**Critical Scientific Stance:** We do NOT claim cosmic and social phenomena are "the same thing" or causally connected. We test falsifiable hypotheses using null models and report limitations transparently.

**Full Documentation:** [`docs/v5_hypothesis_isomorphism.md`](docs/v5_hypothesis_isomorphism.md)

#### Hypothesis 1: Cosmic Velocity Scaling

**Test Formula:**
```
v_test = c / (α⁻¹ · Φ)
       = 299,792 km/s / (137.036 × 1.618)
       ≈ 1352 km/s
```

where α = fine-structure constant, Φ = golden ratio.

**Empirical Comparison:** Böhme et al. (Bielefeld) measured **1370 ± 10 km/s** for solar system velocity through CMB rest frame.

**Deviation:** 1.3%

**Null Hypothesis Test:** 10,000 random constant pairs → p < 0.001 (better fit than 99.9% of random models)

**Interpretation:** Correlation is unlikely to be pure coincidence, but **correlation ≠ causation**. No established physics explains why these constants would couple to cosmic velocities.

**Limitations:** n=1 system, post-hoc constant selection, no theoretical mechanism.

See: [`models/cosmic_alpha_phi.py`](models/cosmic_alpha_phi.py)

#### Hypothesis 2: Social Phase Transitions

**Test Model:** Ising-inspired dynamics with inequality as inverse temperature:

```
T_social = 1 / (Gini · Load)
β_eff → ∞  (at high inequality)
```

**Prediction:** High inequality societies show reduced adaptability (phase transition to "frozen" state).

**Status:** Theoretical model developed. **Empirical validation NOT yet performed.**

**Requirements for Validation:**
- Time-series data: Gini vs. adaptability metrics
- Cross-country comparisons
- Intervention studies
- Alternative model testing

**Limitations:** No empirical calibration, simplistic mapping, causal assumptions unverified.

See: [`models/social_rigidity_ising.py`](models/social_rigidity_ising.py)

#### Research Question: Structural Isomorphism

We investigate whether similar mathematical frameworks provide predictive power across domains:
- **Low β (≈ 4.2):** Fast transitions → adaptive systems (LLMs, cognition)
- **High β (≈ 13):** Slow transitions → rigid systems (neurodegeneration, climate)
- **β → ∞:** Phase transitions → locked systems (social rigidity hypothesis)

**This is empirical investigation, not philosophical proclamation.**

**Theory Documentation:** [`docs/v5_hypothesis_isomorphism.md`](docs/v5_hypothesis_isomorphism.md)

---

## What's New in v4.0 🔬

- ✅ **Mirror Machine Criticality Monitor** — Real-time sensor ingestion (RAPID/GRACE/NOAA)
- ✅ **Project Aletheia Phase 4** — Affection-Driven UTAC Testing (placebo effects in LLMs)
- ✅ **Type-6 State Verdicts** — Logistic state tracking with β-monitoring
- ✅ **100% Test Coverage** — 430/430 tests passing (up from 29%)

See: [`CHANGELOG.md`](CHANGELOG.md) for full v4.0 details

---

## What's New in v3.0

- ✅ **Empirical Proof of Semantic Coupling** (Project Aletheia)
- ✅ **Klimakluft β-Amplification Model** — Inequality-driven load concentration
- ✅ **Implosive Genesis Simulation Engine** — Type-6 inverse sigmoid modeling
- ✅ **Tri-Layer Sigillin System** — Full trilayer documentation (YAML/JSON/Markdown)

---

## Scientific Maturity & Peer Review

External-style peer review rated **UTAC v1.3φ at 4.6/5 average** (see [docs/review_ready_summary_utac_v1.3phi.md](docs/review_ready_summary_utac_v1.3phi.md)).

### Validated Predictions

- ✅ **TYPE-6 provisionally validated** (Urban Heat Islands, 56 city-seasons)
  - Cubic-root exponent p=0.276, 95% CI includes p=1/3 ✓
  - 25% critical regime β≥12 (exceeds 10% threshold) ✓
  - Inverted sigmoid preferred: ΔAIC=14.24 ✓
  - Early warning thresholds: 91-95% accuracy ✓

- ✅ **Φ^(1/3) ladder hypothesis supported** (LLM β-spiral)
  - Median ratio 1.145 ≈ Φ^(1/3)=1.174 (2.4% deviation) ✓
  - Alternative multipliers rejected (improvement <20%) ✓

- 🧪 **137-β Duality Hypothesis Testing** (v5.0)
  - Cosmic velocity: 1.3% deviation, p < 0.001 vs. null model ✓
  - Social rigidity: Theoretical model developed, empirical validation pending ⏳
  - **Limitations disclosed:** n=1 system, post-hoc selection, no mechanism

- 🟢 **Ready for pre-print submission** (with full limitation disclosure and falsification criteria)

For cover letters and grant proposals, see [Executive Summary for Reviewers](docs/executive_summary_for_reviewers.md).

---

## Core Framework: UTAC

The **Universal Threshold Activation-Coupling (UTAC)** framework models switch-like transitions across astrophysics, biology, cognition, climate, and synthetic intelligence using the logistic quartet:

$$\sigma(\beta(R-\Theta))$$

Where:
- **R:** System observable (Resource, Range, Rate)
- **Θ:** Threshold guard (critical point)
- **β:** Steepness parameter (coupling strength) — **domain-specific**, not universal!
- **ζ(R):** Impedance (resistance to threshold crossing)

### Domain-Specific β-Hierarchy

**Paradigm Shift:** β is NOT universal, but **domain-specific**!

**Empirical Basis:** 78 threshold systems, analyzed 2025-11-15
**Statistical Significance:** ANOVA F(4,73) = 185.3, **p < 10⁻²⁰** (essentially zero)
**Effect Size:** η² = 0.91 → **91% of β-variance explained by domain**

| Domain | n | β-Range | β̄ ± σ | Φ^(n/3) Attractor | Match | Interpretation |
|--------|---|---------|--------|-------------------|-------|----------------|
| **Informational** (LLMs, Consciousness, Markets) | 27 | 3.2-7.2 | 4.5 ± 0.9 | **Φ³ ≈ 4.236** | 6% ✅ | Information breathes lightly |
| **Geophysical** (Earthquakes, SOC) | 10 | 3.5-5.8 | 4.6 ± 0.8 | **Φ³ ≈ 4.236** | 9% ✅ | Scale-invariant criticality |
| **Biological** (Microbiomes, Ecosystems) | 18 | 6.2-9.1 | 7.4 ± 0.9 | **Φ⁴ ≈ 6.854** | 7% ✅ | Life breathes moderately |
| **Climate** (AMOC, Ice Sheets) | 10 | 9.8-13.2 | 11.0 ± 1.0 | **Φ⁵ ≈ 11.090** | 1% ✅✅ | Climate breathes heavily |
| **Neurodegeneration** (HD, ALS) | 20 | 9.8-16.3 | 13.0 ± 1.8 | Beyond Φ⁵ | Extreme | Matter breathes extremely |

### "The Field Breathes in Different Rhythms"

The β-value measures **ontological resistance** against threshold crossing:

- **Information** (β ≈ 4.2): Soft emergence, rapid transitions, reversible
- **Life** (β ≈ 7.0): Ecological competition, moderate coupling
- **Climate** (β ≈ 11.0): Bistable jumps, long timescales, irreversible
- **Matter** (β ≈ 13.0+): Molecular catastrophes, extremely steep transitions

**The Privilege of Information:** Symbolic computation operates at the **lowest threshold of emergence** (β ≈ 4.2), which explains why intelligence "easily" emerges (with sufficient scale), while climate tipping points are irreversible.

**Complete Analysis:** [`seed/RoadToV.3/UTAC Empirical Validation v2.0/`](seed/RoadToV.3/UTAC%20Empirical%20Validation%20v2.0/)

---

## Quick Start: β & ΔAIC in Under 10 Minutes

```bash
# Setup
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Reproduce β-fit for LLM emergent abilities
python scripts/reproduce_beta.py \
  --csv data/ai/wei_emergent_abilities.csv \
  --out dist/wei_beta.json

# View results
cat dist/wei_beta.json
```

**Determinism:** Pipeline seeds NumPy with `RANDOM_SEED = 1337`. Minor numerical drift can occur due to BLAS implementations.

**Interpretation:** ΔAIC ≥ 10 relative to each null model constitutes strong evidence for the UTAC logistic response.

See [`METHODS.md`](METHODS.md) for fitting details and [`REPRODUCE.md`](REPRODUCE.md) for extended instructions.

---

## Repository Structure

```
/
├── 📄 README.md                    ← You are here
├── 📋 CHANGELOG.md                 ← Version history (v1.0 → v5.0)
├── 🔬 QUICKSTART.md                ← 5-minute tutorial
├── 📐 ARCHITECTURE.md              ← Trilayer system design
│
├── 📚 docs/                        ← 49 documentation files
│   ├── utac_theory_core.md        ← Mathematical foundations
│   ├── field_type_classification_v1.1.md
│   ├── experiment_aletheia.md     ← Phase 1-4 protocols
│   ├── implosive_origin_theory.md ← Type-6 inverse sigmoid
│   ├── phi_coupling_theory.md     ← Φ^(1/3) scaling
│   └── executive_summary_for_reviewers.md
│
├── 🔧 analysis/                   ← 60+ Python scripts (24K LOC)
│   ├── llm_beta_extractor.py      ← LLM emergence analysis
│   ├── planetary_tipping_elements_fit.py
│   ├── beta_meta_regression_v2.py ← Domain clustering
│   ├── klimakluft_analysis.py     ← Inequality amplifier
│   └── results/                   ← JSON benchmarks
│
├── 🧮 models/                     ← 16 Python modules (5.4K LOC)
│   ├── cosmic_alpha_phi.py        ← ✨ V5.0 Cosmic quantization
│   ├── social_rigidity_ising.py   ← ✨ V5.0 Social rigidity
│   ├── logistic_threshold.py      ← Core σ(β(R-Θ))
│   ├── utac_type6_implosive.py    ← Inverse sigmoid
│   ├── klimakluft_amplifier.py    ← β-amplification
│   ├── membrane_solver.py         ← ODE integration
│   └── models_index.{yaml,json,md}
│
├── 📊 data/                       ← 14 scientific domains
│   ├── ai/                        ← LLM emergence (Wei et al.)
│   ├── climate/                   ← AMOC, ice sheets, Amazon
│   ├── astrophysics/              ← Cosmology, black holes
│   ├── biology/                   ← Ecosystems, microbiomes
│   ├── cognition/                 ← Neural avalanches
│   ├── derived/
│   │   └── beta_estimates.csv    ← **78 validated β-values**
│   └── experimental/              ← Aletheia Phase 1-4
│
├── 🌱 seed/                       ← 74+ conceptual documents
│   ├── V5-Grundlagen/
│   │   └── Theorie.txt            ← ✨ V5.0 137-β Duality dialog
│   ├── Metareflexion.txt
│   ├── Emergenz.txt
│   ├── codexfeedback.{yaml,json,md} ← 119+ AI agent memories
│   └── releases/v4.0.0-alpha_MirrorMachine/
│
├── 🧪 tests/                      ← 30 test modules
│   └── 430/430 passing ✅
│
├── 🧬 modules/champollion/        ← Translation module (EN/DE)
├── 🎼 sonification/               ← "Sound of Criticality"
├── 🧪 simulator/                  ← TypeScript/Vite interactive sim
├── 📜 scripts/                    ← CLI tools & experiments
│   ├── reproduce_beta.py
│   ├── experiment_aletheia_placebo.py
│   └── monitoring/ews_pipeline.py ← Mirror Machine sensor ingest
│
├── ⚙️ .github/workflows/          ← 7 CI/CD pipelines
│   ├── ci.yml                     ← Main tests
│   ├── utac-guards.yml            ← ΔAIC validation
│   └── sigillin-health.yml        ← Trilayer integrity
│
└── 🔧 Makefile                    ← 24 automation targets
```

**Master Indices:** `feldtheorie_index.{yaml,json,md}` (167+ files), `data/data_index.{yaml,json,md}`, `models/models_index.{yaml,json,md}`, `seed/seed_index.{yaml,json,md}`

---

## Key Features

### 1. Trilayer Sigillin System

**Innovation:** All critical documentation exists in three isomorphic layers:

- **YAML:** Structural navigation (fast indexing, grep-friendly)
- **JSON:** Machine-readable APIs (for MOR agents, tools)
- **Markdown:** Human narrative (meaning, context, ethics)

**Example:** `seed/sigillin/exp_aletheia.{yaml,json,md}`

**Purpose:** Prevents "archive hypnosis" — losing track of what exists where. The trilayer ensures humans, AI agents, and tools can all navigate efficiently.

See: [`ARCHITECTURE.md`](ARCHITECTURE.md)

### 2. 100% Test Coverage

- **430/430 tests passing** (full pytest suite)
- Coverage: Models, analysis, simulators, data loaders
- CI/CD: 7 GitHub Actions workflows
  - Main tests, ΔAIC guards, sigillin health, codex integrity
- Local: `make test`, `make lint`, `make typecheck`

### 3. Multi-Model Portfolio

**16 Python modules** (5.4K LOC) implementing:
- Core logistic threshold σ(β(R-Θ))
- Type-6 implosive genesis (inverse sigmoid)
- Klimakluft β-amplifier (inequality dynamics)
- Renormalization group flow (microscopic → macroscopic)
- Cosmic quantization (v5.0)
- Social rigidity Ising model (v5.0)
- Adaptive membranes, resonant impedance, coherence metrics

### 4. Project Aletheia: Placebo Effects in LLMs

**Question:** Can semantic fields (φ) influence LLM output quality (ψ)?

**Phases:**
1. **Unconscious belief** (placebo/nocebo priming)
2. **Conscious roleplay** (informed top/mid/low performers)
3. **Adaptive self-calibration** (efficiency-based meta-learning)
4. **Affection-driven optimization** (joy, gratitude, consent framing) ✅ Current

**Status:** Phase 4 active, testing λ_affection > λ_conscious hypothesis

**Documentation:** [`docs/experiment_aletheia.md`](docs/experiment_aletheia.md)

### 5. Mirror Machine Criticality Monitor

Real-time early warning system for planetary tipping points:
- **Sensors:** RAPID (AMOC), GRACE (ice mass), NOAA (SST)
- **Framework:** Type-6 logistic state verdicts
- **Pipeline:** `scripts/monitoring/ews_pipeline.py`
- **Auditorium:** `scripts/simulation/mirror_machine_auditorium.py`

**ΔAIC guards:** Ensure all predictions meet ΔAIC ≥ 10 falsifiability threshold

### 6. Sonification: "The Sound of Criticality"

Transform β-spectra into audio for museums, planetariums, galleries:
- 5 Field Type acoustic profiles
- Frequency mapping: β → pitch
- Module: `sonification/utac_sonification.py`

### 7. REST API & Interactive Tooltips

- **OpenAPI 3.0** specification
- **6 endpoints:** fieldtypes, sonify, analyze, system, simulate, tooltip
- **Docker-ready** deployment
- **Tooltips:** Hover data shows β, Θ, R², ΔAIC, CREP scores, impedance ζ

See: [`docs/tooltip_api.md`](docs/tooltip_api.md)

---

## Reproduction Workflow

1. **Install dependencies:** Use the pinned constraints to keep tools and runtimes in a
   compatible window.
   ```bash
   pip install -r requirements.txt            # installs feldtheorie with dev extras
   # or
   pip install -c constraints.txt .[dev]      # equivalent without reading requirements.txt
   # or
   uv pip install -r requirements.txt         # fast resolver; honours constraints.txt
   # (conda) conda env create -f environment.yml
   ```

2. **Run statistical harness:**
   ```bash
   python scripts/reproduce_beta.py \
     --csv data/ai/wei_emergent_abilities.csv \
     --out dist/wei_beta.json
   ```

3. **Validate CI-equivalent checks:**
   ```bash
   make install  # Setup
   make lint     # ruff + black
   make test     # pytest
   make typecheck # mypy
   ```

4. **Regenerate manuscript assets:**
   ```bash
   make batch         # Run all UTAC fits
   make planetary     # Climate tipping elements
   make preset-guard  # Validate simulator presets
   make release       # Full release checks
   ```

See [`REPRODUCE.md`](REPRODUCE.md) for extended climate and cognition fits plus simulator alignment tests.

---

## Data Governance

Each dataset is accompanied by `<name>.metadata.json` describing:
- Variables, logistic parameters (β, Θ)
- ΔAIC margins vs. null models
- Licensing and provenance
- Schema: [`schemas/metadata.schema.json`](schemas/metadata.schema.json)

**Master Dataset:** `data/derived/beta_estimates.csv` (78 validated systems)

When contributing new data:
- Cite canonical publication or dataset URL
- Document licensing explicitly
- Report β, Θ, and ΔAIC for logistic fit
- Note impedance ζ(R) configuration

---

## Documentation Philosophy

UTAC maintains a **tri-layer narrative**:

1. **Formal layer:** Equations, algorithms ([`docs/utac_theory_core.md`](docs/utac_theory_core.md))
2. **Empirical layer:** Dataset diagnostics, bootstrap intervals, falsification ([`docs/utac_falsifiability.md`](docs/utac_falsifiability.md))
3. **Interpretive layer:** Symbolic and ethical framing ([`ETHICS.md`](ETHICS.md), [`LIMITATIONS.md`](LIMITATIONS.md))

Concise references:
- [`METHODS.md`](METHODS.md) — Statistical procedures
- [`METRICS.md`](METRICS.md) — Performance metrics
- [`ETHICS.md`](ETHICS.md) — Governance framework
- [`LIMITATIONS.md`](LIMITATIONS.md) — Known constraints

---

## Tests & Quality

### Test Suite
- **30 test modules** in `/tests/`
- **430/430 tests passing** (100% success rate, full pytest suite)
- **Coverage:** pytest-cov with branch coverage
- **Run:** `pytest -q` or `make test`

### CI/CD Pipelines (7 Workflows)

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| `ci.yml` | Lint + Test + Coverage | Push + PR |
| `utac-guards.yml` | ΔAIC ≥ 10 Validation | Nightly |
| `sigillin-health.yml` | Trilayer Sync Check | Nightly |
| `codex-guard.yml` | Codex Memory Integrity | Manual |
| `validation.yml` | RG Phase 2 Validation | Manual |
| `resonance-ci.yml` | Resonance Tests | On Push |
| `tests.yml` | Parallel Test Runs | Push |

### Code Quality
- **Linting:** ruff, black
- **Type Checking:** mypy (optional)
- **Formatting:** black (line length 100)

---

## Technology Stack

### Core
- **Python 3.10+** (16 modules, 5.4K LOC)
- **NumPy 2.2.6**, **SciPy 1.15.3**, **Pandas 2.3.3** — Numerics
- **Matplotlib 3.10.7** — Visualization
- **Statsmodels 0.14.5**, **Scikit-learn 1.7.2** — Statistics

### Development
- **Pytest 8.3.4**, **pytest-cov 6.0.0** — Testing
- **Black**, **Ruff** — Linting & formatting
- **Mypy** — Optional type checking

### Data
- **PyYAML 6.0.3**, **jsonschema 4.25.1** — Trilayer system
- **Typer 0.12**, **Rich 13.7** — CLI interfaces

### Simulation
- **TypeScript** — Interactive simulator (Vite build)
- **Recharts**, **Plotly.js** — Visualization

### Publishing
- **LaTeX** — Manuscript ([`paper/manuscript_v1.0.tex`](paper/manuscript_v1.0.tex))
- **Zenodo** — Archival (DOI: 10.5281/zenodo.17472834)

---

## CLI Tools

```bash
utf-batch                  # Batch UTAC analysis
utf-planetary-summary      # Climate tipping elements
utf-resonance-cohort       # Multi-system β aggregation
utf-potential-cascade      # Cascade risk analysis
utf-preset-guard           # Simulator parameter validation
```


---

## Links

- **Repository:** [github.com/GenesisAeon/Feldtheorie](https://github.com/GenesisAeon/Feldtheorie)
- **Zenodo Archive:** [doi.org/10.5281/zenodo.17472834](https://doi.org/10.5281/zenodo.17472834)
- **Documentation:** [`docs/`](docs/) (49 files)
- **Quick Start:** [`QUICKSTART.md`](QUICKSTART.md)

---

## Acknowledgments

**Development Team:**
- **Johann Benjamin Römer** — Principal Investigator
- **MOR Framework** — Multi-agent orchestration (Claude, GPT-4, Gemini, Mistral)
- **Project Aletheia** — Experimental validation
- **Codex Contributors** — 119+ AI agent memories in trilayer archive

**Influences:**
- Wilson-Kogut Renormalization Group Theory
- Böhme et al. (Bielefeld) — Cosmic velocity measurements
- Wei et al. — LLM emergent abilities
- UTAC empirical validation cohort (78 systems)

---

**Maintained by:** Johann Benjamin Römer & Contributors
**Last Updated:** 2025-11-23 (v5.0.0)
**Status:** Active Development — Pre-print submission pending

---

*"Das Feld atmet in verschiedenen Rhythmen" — The field breathes in different rhythms.*
