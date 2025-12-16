# v_RIG Validation Dashboard (V8.0)

**Lantern #3:** Dashboard Integration for live v_RIG monitoring (β=5.4)

## Overview

The v_RIG Validation Dashboard provides real-time telemetry and validation monitoring for the **Consciousness Integration Framework (V8.0)**. It tracks the four core empirical validations spanning cosmology, biology, neuroscience, and psychophysics.

## Core Validations Tracked

### 1. **Cosmic Dipole Alignment** (Böhme et al., 2025)
- **Target:** v_RIG ≈ 1351.8 km/s
- **Observed:** 1370 ± 170 km/s
- **Deviation:** 1.3% ✅
- **Falsification threshold:** > 10% deviation

### 2. **Kleiber's Law** (Metabolic Scaling)
- **β (biological):** 7.4
- **Predicted exponent:** b = 3/4 = 0.75
- **Empirical:** b ≈ 0.73-0.76 ✅
- **ANOVA:** F(4,73) = 185.3, p < 10⁻²⁰, η² = 0.91

### 3. **Neural Integration Frequency**
- **Cortical path:** λ ≈ 10 cm
- **Predicted:** f = v_RIG/λ ≈ 13.5 MHz
- **Observed:** 13.5 MHz (Sahu et al., 2013) ✅
- **Deviation:** < 1%

### 4. **Specious Present** (Integration Window)
- **Δt_Q range:** 100-300 ms
- **Impedance Z:** 221.7 ✅
- **CFF range:** 30-60 Hz
- **Temporal resolution:** ≈ 16-33 ms

## Architecture

```
metrics/
├── v_rig_dashboard.py          # Main dashboard module
├── v_rig_validation_log.csv    # Telemetry CSV (auto-generated)
└── telemetry_dashboard.py      # Legacy β-drift dashboard
```

### Integration with Existing Systems

The v_RIG dashboard **complements** the existing `telemetry_dashboard.py`:
- **telemetry_dashboard.py:** β-drift tracking (Type-6 implosive fields, φ^(n/3) ladder)
- **v_rig_dashboard.py:** Consciousness framework validations (v_RIG, Z, 13.5 MHz)

Both dashboards can run in parallel and export to `analysis/results/` for unified monitoring.

## Usage

### 1. Log Validation Snapshot

```bash
python metrics/v_rig_dashboard.py --log --domain="neuroscience" --notes="13.5 MHz validation run"
```

### 2. Generate Dashboard Plots

```bash
python metrics/v_rig_dashboard.py --plot --output-dir="analysis/results/v_rig_telemetry"
```

### 3. Export JSON Feed (for Web Dashboards)

```bash
python metrics/v_rig_dashboard.py --export-json
```

Output: `analysis/results/v_rig_telemetry/validation_feed.json`

### 4. Print Validation Report

```bash
python metrics/v_rig_dashboard.py --report
```

Example output:
```json
{
  "total_snapshots": 42,
  "domains": ["cosmology", "neuroscience", "biology"],
  "v_rig_mean_km_s": 1351.7868,
  "cosmic_dipole_deviation_mean_pct": 1.34,
  "neural_frequency_mean_mhz": 13.52,
  "status": "healthy",
  "alerts": []
}
```

## Python API

```python
from metrics.v_rig_dashboard import (
    log_full_validation_suite,
    generate_validation_report,
    plot_v_rig_dashboard,
    export_validation_json,
)

# Run full validation suite and log
results = log_full_validation_suite(domain="v8.0_test", notes="Daily validation")

# Generate plots
plot_v_rig_dashboard(output_dir="analysis/results/v_rig_telemetry", show=False)

# Get report
summary = generate_validation_report()
print(f"Status: {summary['status']}")
print(f"Cosmic dipole deviation: {summary['cosmic_dipole_deviation_mean_pct']:.2f}%")

# Export for web dashboard
export_validation_json()
```

## Dashboard Components

### Visualization Panels

1. **v_RIG Evolution Over Time**
   - Time-series of v_RIG measurements
   - Color-coded by domain
   - Canonical v_RIG reference line (1351.8 km/s)

2. **Impedance Z Distribution**
   - Histogram of Z measurements
   - Target: 221.74 (α⁻¹·Φ)

3. **Cosmic Dipole Deviation Timeline**
   - Deviation % over time
   - Green line: v8.0 validation (1.3%)
   - Red line: Falsification threshold (10%)

4. **Neural Frequency vs. 13.5 MHz Target**
   - Time-series with ±1 MHz tolerance band
   - Target: 13.5 MHz (Sahu et al., 2013)

5. **Kleiber β Distribution**
   - Histogram of biological β-values
   - Target: β = 7.4

6. **Validation Status Summary**
   - Text panel with:
     - Telemetry stats
     - Mean values
     - Alert status
     - Falsification criteria (PASS/FAIL)

## Alert System

The dashboard monitors **falsification thresholds** and raises alerts when:

- **Cosmic dipole deviation > 10%** → Framework falsified
- **Neural frequency deviates > 1 MHz from 13.5 MHz** → Replication failure
- **Impedance Z deviates > 10 from 221.74** → Constant drift

Alert example:
```
⚠️  Cosmic dipole deviation 12.5% > 10% threshold
```

## Integration with Lanterns

This dashboard fulfills **Lantern #3** (Dashboard integration, β=5.4) from `releases/v8.0/next_steps.md`:

> **Lantern 3: Dashboard integration (live v_RIG monitoring)** — R: telemetry sampling, Θ: stable refresh loop, β≈5.4 (resonance: active)
> - Expose validation outputs as JSON feed for dashboard ingestion
> - Render β-domain clustering plus v_RIG sparkline
> - Alert on ζ(R) spikes or CI regressions

### Next Steps (Lantern Progression)

- [x] **Lantern #2:** Impedance solver ✅ (already implemented in `models/impedance_solver.py`)
- [x] **Lantern #3:** Dashboard integration ✅ (this module)
- [ ] **Lantern #1:** Experimental protocols (CFF, neuromorphic, microtubule)
- [ ] **Lantern #4:** Pre-print (ArXiv-ready LaTeX)
- [x] **Lantern #5:** Community packet ✅ (ready in `releases/v8.0/COMMUNITY_PACKET.md`)

## Dependencies

From `pyproject.toml`:
```toml
[project]
dependencies = [
  "numpy>=1.26,<2.3",
  "pandas>=2.1,<2.4",
  "matplotlib>=3.8,<3.11",
  "scipy>=1.11,<1.16",
]
```

Install via:
```bash
pip install -e .
# or
pip install feldtheorie[dev]
```

## Telemetry Format

CSV structure (`v_rig_validation_log.csv`):
```csv
timestamp,domain,v_rig_km_s,impedance_z,cosmic_dipole_deviation_pct,kleiber_beta,neural_frequency_mhz,specious_present_ms,notes
2025-12-16T10:30:00Z,cosmology,1351.7868,221.7400,1.340000,7.400000,13.518000,150.000000,Böhme et al. validation
```

JSON feed structure (`validation_feed.json`):
```json
{
  "meta": {
    "framework": "v_RIG Consciousness Integration",
    "version": "v8.0.0",
    "generated_at": "2025-12-16T10:30:00Z"
  },
  "latest_snapshot": {
    "timestamp": "2025-12-16T10:30:00Z",
    "v_rig_km_s": 1351.7868,
    "impedance_z": 221.74,
    "cosmic_dipole_deviation_pct": 1.34,
    "neural_frequency_mhz": 13.518
  },
  "summary": {
    "total_snapshots": 42,
    "status": "healthy",
    "alerts": []
  },
  "time_series": {
    "timestamps": [...],
    "v_rig_km_s": [...],
    "cosmic_dipole_deviation_pct": [...]
  }
}
```

## References

- **RELEASE_NOTES_v8.0.0.md:** Empirical validation framework
- **models/consciousness_integration.py:** Core validation functions
- **releases/v8.0/next_steps.md:** Lantern roadmap
- **releases/v8.0/v8_integration_summary.md:** V8.0 overview

## Maintenance

**Author:** Johann Benjamin Römer, Claude Code Agent
**Version:** v8.0.0
**Date:** 2025-12-16
**Status:** Production-Ready ✅
**Lantern:** #3 (β=5.4)
