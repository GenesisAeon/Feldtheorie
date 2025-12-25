# Feldtheorie V6 - Tutorial Series

**Welcome to the Universal Threshold Field Programme tutorials!**

This series provides hands-on introduction to the UTAC framework, V6 wavefunction, and Genesis Cube visualization tools.

---

## 📚 Tutorial Overview

### Tutorial 1: Introduction to UTAC
**File:** `01_Introduction_UTAC.ipynb`

**Topics:**
- UTAC sigmoid function σ(R; β, Θ)
- Fitting β and Θ to empirical data
- Physical interpretation of parameters
- β ≈ 2J/T relationship

**Duration:** ~30 minutes
**Prerequisites:** Basic Python, NumPy, Matplotlib
**Datasets:** Synthetic + real beta estimates

**Learning Outcomes:**
- ✓ Understand threshold activation framework
- ✓ Fit UTAC model to data
- ✓ Interpret β (steepness) and Θ (threshold)
- ✓ Classify systems by coupling strength

---

### Tutorial 2: V6 Wavefunction and Ψ-Field Integration
**File:** `02_Wavefunction_V6.ipynb`

**Topics:**
- Entropic wavefunction Ψ(r,θ,φ,t)
- Probability density |Ψ|² computation
- Tetrahedral harmonics decomposition
- CREP index classification
- Effective β modulation

**Duration:** ~45 minutes
**Prerequisites:** Tutorial 1, basic quantum mechanics concepts
**Tools:** GenesisCube, EntropicWavefunction

**Learning Outcomes:**
- ✓ Compute wavefunction from threshold field
- ✓ Visualize |Ψ|² and phase evolution
- ✓ Extract tetrahedral harmonics
- ✓ Classify field type using CREP index
- ✓ Integrate Ψ-field with threshold dynamics

---

### Tutorial 3: Genesis Cube - 4D Visualization
**File:** `03_Genesis_Cube.ipynb`

**Topics:**
- 4D block universe representation
- Empirical β/Θ presets (36 systems)
- 3D isosurface visualization
- Comparing weak/strong coupling
- Early warning signals

**Duration:** ~40 minutes
**Prerequisites:** Tutorial 1
**Tools:** Genesis Cube, visualization scripts

**Learning Outcomes:**
- ✓ Configure Genesis Cube for different systems
- ✓ Apply empirical presets (climate, AI, bio)
- ✓ Create 3D visualizations
- ✓ Identify early warning signals
- ✓ Compare activation patterns across domains

---

## 🚀 Getting Started

### 1. Installation

```bash
# Clone repository
git clone https://github.com/GenesisAeon/Feldtheorie.git
cd Feldtheorie

# Install dependencies
pip install -e ".[dev]"
pip install -r scripts/requirements_visualization.txt

# Verify installation
python -c "from models.sigmoid_fit import sigmoid; print('✓ Installation successful')"
```

### 2. Launch Jupyter

```bash
# Start Jupyter Lab
jupyter lab docs/tutorials/

# Or Jupyter Notebook
jupyter notebook docs/tutorials/
```

### 3. Run Tutorials in Order

Start with **Tutorial 1** and proceed sequentially. Each tutorial builds on previous concepts.

---

## 📊 Required Data Files

Tutorials use the following data files:

- `data/derived/beta_estimates.csv` - 36 empirical β/Θ estimates
- `analysis/results/*.json` - Validation results (optional)

If files are missing, tutorials will use synthetic data.

---

## 🎯 Learning Path

### Beginner Track
1. **Tutorial 1** (UTAC basics)
2. **Tutorial 3** (Genesis Cube)
3. Practice with your own data

### Advanced Track
1. **Tutorial 1** (review)
2. **Tutorial 2** (Wavefunction)
3. **Tutorial 3** (Visualization)
4. Explore source code in `models/` and `simulation/`

### Researcher Track
All tutorials + dive into:
- `tests/` - Unit tests with examples
- `analysis/` - Advanced analysis scripts
- `papers/` - Theoretical background

---

## 🔬 Example Applications

### Climate Science
```python
# Tutorial 1: Fit β to AMOC data
beta, theta = fit_sigmoid(temperature, circulation_strength)

# Tutorial 3: Visualize tipping point
python scripts/visualize_genesis.py --preset climate_amoc
```

### AI/ML
```python
# Tutorial 1: Analyze LLM emergence
beta_llm = extract_beta(model_size, capability_score)

# Tutorial 3: Genesis animation
python scripts/visualize_genesis.py --preset llm_emergent
```

### Neuroscience
```python
# Tutorial 1: Synaptic plasticity
beta_syn = fit_sigmoid(calcium_concentration, synapse_strength)

# Tutorial 2: Wavefunction in neural field
crep = compute_crep_index(wavefunction, t=0)
```

---

## 📖 Additional Resources

### Documentation
- **Main README:** `../README.md`
- **Visualization Index:** `../VISUALIZATION_INDEX.md`
- **Test Report:** `../../TEST_REPORT.md`
- **API Documentation:** Run `python -m pydoc -b` and navigate to modules

### Example Notebooks
- `notebooks/utac_demo.ipynb` - Quick UTAC demo
- `notebooks/01_beta_fit_minimal.ipynb` - Minimal beta fitting
- `analysis/dynamic_threshold_lab.ipynb` - Advanced analysis

### Scripts
- `scripts/generate_all_figures.py` - Generate paper figures
- `scripts/visualize_wavefunction.py` - Wavefunction plots
- `scripts/visualize_genesis.py` - Genesis Cube animations
- `scripts/visualize_beta_distribution.py` - Beta statistics

### Papers & Theory
- `releases/V6-Plans_etc/papers/` - Theoretical papers
- `papers/FIGURE_SPECIFICATIONS.md` - Figure details
- `Docs/` - Legacy documentation

---

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure feldtheorie is installed
pip install -e .

# Add to PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Missing Data
```bash
# Tutorials use synthetic data if files missing
# To get full data, run:
python scripts/prepare_beta_estimates.py  # If available
```

### Visualization Issues
```bash
# Install visualization dependencies
pip install -r scripts/requirements_visualization.txt

# For 3D plots, ensure backend supports it
# Try: %matplotlib widget (in Jupyter)
```

### Genesis Cube Slow
```python
# Reduce resolution for faster computation
config = GenesisCubeConfig(
    wavefunction_resolution=16,  # Lower from 64
    slice_count=10,              # Lower from 40
    time_steps=25                # Lower from 100
)
```

---

## 🤝 Contributing

Found an issue or want to improve tutorials?

1. **Report bugs:** Open issue on GitHub
2. **Suggest improvements:** Pull requests welcome
3. **Share examples:** Add your use case to discussions

**Tutorial Guidelines:**
- Keep cells runnable without external data
- Use synthetic data as fallback
- Include clear explanations
- Add references to source code

---

## 📜 Citation

If you use these tutorials in your research:

```bibtex
@software{feldtheorie_v6_tutorials,
  title={Feldtheorie V6: Universal Threshold Field Programme - Tutorials},
  author={Universal Threshold Field Collective},
  year={2025},
  url={https://github.com/GenesisAeon/Feldtheorie},
  note={Interactive Jupyter tutorials for UTAC framework}
}
```

---

## 🌟 Next Steps

After completing tutorials:

1. **Explore Test Suite:** `tests/` has many working examples
2. **Run Full Analysis:** Use `analysis/` scripts on your data
3. **Generate Visualizations:** Create publication-quality figures
4. **Read Papers:** Dive into theoretical foundations
5. **Contribute:** Help expand the framework!

---

**Questions?** Open an issue on GitHub or check documentation.

**Happy Learning! 🚀**

---

**Last Updated:** 2025-11-27
**Version:** V6
**Branch:** claude/testing-docs-review-01KcWVr6QpZq8FDzgNzwev2n
