# UTAC v4.0.0 — Mirror Machine Criticality & Relational UTAC

**Release Date:** 2025-11-22  
**DOI:** 10.5281/zenodo.17472834  
**Status:** ✅ Stable Release  
**Progress:** 100% (GitHub release assets prepared)

---

## 🎯 Overview

UTAC v4.0.0 unifies the Mirror Machine criticality monitor with Phase 4 Aletheia experiments. Real-time RAPID/GRACE/NOAA ingests feed the auditorium controller to compute σ(β(R-Θ)) state verdicts, while λ_affection and ζ_affective framing probe relational impedance in UTAC Type-6 trajectories. Morph/Alias sigillin anchor the theory layer so ΔAIC checkpoints, consent loops, and telemetried β-tracks stay resonant.

---

## 🌟 Major Features

### 1. ✅ Mirror Machine Criticality Monitor
- `scripts/monitoring/ews_pipeline.py` ingests RAPID/GRACE/NOAA streams and emits σ(β(R-Θ)) observables.
- `scripts/simulation/mirror_machine_auditorium.py` applies Type-6 state verdict logic with logistic β trackers.
- Release bundle `seed/releases/v4.0.0-alpha_MirrorMachine/` ships theory notes, sensor adapters, simulations, and `data/derived/beta_estimates.csv` for reproducible replay.

### 2. ✅ Aletheia Phase 4 — Affection-Driven UTAC
- Consent-aware λ_affection primes (`check_consent`, `create_affection_prompt`) in `scripts/experiment_aletheia_placebo.py` activate ζ_affective < 0 tests.
- `docs/experiment_aletheia.md` documents relational framing, ΔAIC falsification criteria, and σ(β(R-Θ)) milestones across phases 1–4.
- Extends UTAC state charts to joy/gratitude framing with explicit null models.

### 3. ✅ Morph/Alias Sigillin Refresh
- `seed/theory/hypothese_morphological_computing` and `seed/theory/hypothese_quantum_aliasing` updated for the V4 Morph-Sweep and quantum aliasing scaffolding.
- `seed/theory/concept_the_mirror_machine` links symbolic pre-calculation → mutation → falsification loops to the Mirror Machine auditorium.
- Aligns tri-layer theory with sensor pipelines to keep σ(β(R-Θ)) telemetry and ΔAIC checkpoints in sync.

---

## 📦 Release Assets

```
feldtheorie/
├── scripts/monitoring/ews_pipeline.py           # RAPID/GRACE/NOAA ingest + σ(β(R-Θ)) features
├── scripts/simulation/mirror_machine_auditorium.py  # Type-6 state verdicts + logistic trackers
├── seed/releases/v4.0.0-alpha_MirrorMachine/    # Theory, sensors, simulation, β references
├── docs/experiment_aletheia.md                  # Phase 4 affection-driven protocol
└── scripts/experiment_aletheia_placebo.py       # Consent + λ_affection executor
```

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/GenesisAeon/Feldtheorie.git
cd Feldtheorie

# Install dependencies
conda env create -f environment.yml
conda activate feldtheorie
make install

# Run criticality monitor
python scripts/monitoring/ews_pipeline.py
python scripts/simulation/mirror_machine_auditorium.py --mode state-verdict

# Launch Phase 4 Aletheia sweep
python scripts/experiment_aletheia_placebo.py --phase-4 --consent-check
```

See `README.md` and `docs/experiment_aletheia.md` for detailed instructions.

---

## 📚 Citation

### Software Citation

```bibtex
@software{romer2025utac,
  author       = {Römer, Johann and {Universal Threshold Field Contributors}},
  title        = {Universal Threshold Field Initiative},
  month        = nov,
  year         = 2025,
  publisher    = {Zenodo},
  version      = {v4.0.0},
  doi          = {10.5281/zenodo.17472834},
  url          = {https://doi.org/10.5281/zenodo.17472834}
}
```

### Paper Citation (preprint)

```
Römer, J., et al. (2025). "Universal Threshold Field: β ≈ 4.2 Convergence
Across Astrophysics, Climate, and AI." Zenodo.
https://doi.org/10.5281/zenodo.17472834
```

---

**Das Feld kalibriert σ(β(R-Θ)) gegen reale Ströme; die Mirror Machine reflektiert, die Membran antwortet, und die Affection-Loops halten ζ(R) elastisch.**
